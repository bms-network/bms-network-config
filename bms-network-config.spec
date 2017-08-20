%if 0%{?suse_version} >= 1000 
# SUSE
%if 0%{?suse_version} < 1200
%define dist suse114
%define nosystemd 1
%else
%define dist suse121
%define nosystemd 0
%endif
%else
# REDHAT/CentOS/Oracle/Euler
%if 0%{?rhel_version} < 700 && 0%{?centos_version} < 700
%define nosystemd 1
%define dist redhat73
%else
%define nosystemd 0
%define dist redhat73
%endif
%endif

Name:		bms-network-config
Version:	1.0
Release:	42.1
Summary:	OTC Bare Metal Network Device Configuration Scripts

Group:		Development/Tools
License:	GPL
Source0:	bms-network-config-%{version}.tar.gz
Patch0:		disable-auth-keys.diff
Patch1:		initscript-tweaks.diff
Patch2:		bms-before-cloudinit.diff
Patch3:		phy-slaves-dhcp-none.diff

Autoreqprov: on

BuildRequires:	python
BuildRequires:	dos2unix
%if 0%{?suse_version} >= 1210
BuildRequires: systemd-rpm-macros
%endif
%if %{nosystemd} != 1
BuildRequires: systemd
%endif
#Requires(post):	cloud-init
#BuildRequires:  udev
#%if 0%{?suse_version} >= 1000
#BuildRequires:  sysconfig
#%fi
%if 0%{?suse_version} >= 1000
PreReq:         %insserv_prereq
%endif
Requires:	python
Requires:	cloud-init
Requires:	python-six
BuildRoot:	%{_tmppath}/%{name}-%{version}-build

BuildArch:	noarch



%description
OTC Bare Metal Network Device Configuration Scripts

bms-network-config is needed on OTC's Bare Metal (Ironic) Service to configure
the network interfaces.  It evaluates the configuration passed via the
meta-data service and configures the Network Interface according to it.
Unfortunately, this can not easily be achieved inside the oldish cloud-init
shipped in current distributions, thus the separate package that gets invoked
on system startup.


%prep
%setup -n bms-network-config-%{version}
#Not yet ...
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%if 0%{?suse_version} == 0
sed -i 's@ExecStart=/usr/bin/bms-network_config@ExecStart=/usr/bin/bms-network_config rhel@' bms-network-config.service
%endif

%build
#sed -i 's/network-config/bms-network-config/g' bms-network-config
#sed -i 's/network_config/bms_network_config/g' bms-network-config
cp -p network_config.py.%dist bms-network_config.py
dos2unix bms-network_config.py

%install
#cd %{name}-%{version}
mkdir -p ${RPM_BUILD_ROOT}/usr/bin
mkdir -p ${RPM_BUILD_ROOT}/opt/huawei/network_config
mkdir -p ${RPM_BUILD_ROOT}/%{_initddir}
mkdir -p ${RPM_BUILD_ROOT}/%{_sbindir}

%if %{nosystemd} == 1
cp -p bms-network-config $RPM_BUILD_ROOT/%{_initddir}/bms-network-config
%if 0%{?suse_version} >= 1000
ln -sf "%{_initddir}/bms-network-config" "${RPM_BUILD_ROOT}/%{_sbindir}/rcbms-network-config"
%endif
%else
# Systemd
mkdir -p %{buildroot}%{_unitdir}
install -m 0644 bms-network-config.service %{buildroot}%{_unitdir}/
%endif

install -m 0750 bms-network_config.py $RPM_BUILD_ROOT/opt/huawei/network_config/bms-network_config.py
ln -sf /opt/huawei/network_config/bms-network_config.py $RPM_BUILD_ROOT/usr/bin/bms-network_config

%clean
rm -rf $RPM_BUILD_ROOT

#%pre
#

%post
%if 0%{?suse_version} >= 1000 && 0%{?suse_version} < 1200
%{fillup_and_insserv -f -y bms-network-config}
%else
if [ $1 -eq 1 ] ; then
%if %{nosystemd} == 1
chkconfig -a bms-network-config
chkconfig bms-network-config on
%else
systemctl enable bms-network-config.service 
%endif
fi
%endif

%preun
%if 0%{?suse_version} >= 1000 && 0%{?suse_version} < 1200
%stop_on_removal bms-network-config
%else
if [ $1 -eq 0 ] ; then
%if %{nosystemd} == 1
    service bms-network-config stop
    chkconfig --del bms-network-config
%else
    systemctl --no-reload disable bms-network-config.service
%endif
fi
%endif

%postun
%if 0%{?suse_version} >= 1000 && 0%{?suse_version} < 1200
%restart_on_update bms-network-config
%insserv_cleanup
%else
%if %{nosystemd} != 1
    systemctl daemon-reload >/dev/null 2>&1 || :
%endif
%endif


%files
%defattr(-,root,root)
/opt/huawei/network_config/*
/usr/bin/bms-network_config
%if %{nosystemd} == 1
%attr(0755, root, root) %{_initddir}/bms-network-config
%if 0%{?suse_version} >= 1000
%{_sbindir}/rcbms-network-config
%endif
%else
%attr(0644, root, root) %{_unitdir}/bms-network-config.service
%endif
%dir /opt/huawei/network_config
%dir /opt/huawei

%changelog
* Thu Jul 13 2017 kurt@garloff.de
- Move bms-network-script b/f network bring-up.
- phy-slaves-dhcp-none.diff: Disable DHCP on phy slaves
* Thu Jul 13 2017 kurt@garloff.de
- Run bms-network-setup before cloud-init.
* Thu Jul 13 2017 kurt@garloff.de
- Use distro specific setup script.
- Use systemd unit file or init script dep on distro.
* Wed Jul 12 2017 kurt@garloff.de
- Use new package from Huawei with config scripts for several
  distributions (not used yet).
* Fri Jun 16 2017 kurt@garloff.de
- Avoid accessing ssh keys.
* Fri Jun 16 2017 kurt@garloff.de
- Rename to bms-network-config
  Mon May 22 12:00:00 CST 2017 - huawei
- Initial release 1.0

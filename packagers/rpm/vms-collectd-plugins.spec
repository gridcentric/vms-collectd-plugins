Name: vms-collectd-plugins
Summary: Collectd plugins for Gridcentric VMS
Version: %{version}
Release: 1
Group: System Environment/Daemons
License: Copyright 2013 Gridcentric Inc.
URL: http://www.gridcentric.com
Packager: Gridcentric Inc. <support@gridcentric.com>
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}.%{version}-buildroot
AutoReq: no
AutoProv: no
Requires: collectd

# To prevent ypm/rpm/zypper/etc from complaining about FileDigests when installing we set the
# algorithm explicitly to MD5SUM. This should be compatible across systems (e.g. RedHat or openSUSE)
# and is backwards compatible.
%global _binary_filedigest_algorithm 1
# Don't strip the binaries.
%define __os_install_post %{nil}

%description
Collectd plugins for Gridcentric VMS.

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT
rsync -rav --delete ../../dist-rpm/* $RPM_BUILD_ROOT

%files
/etc/
/var/

%post
if [ "$1" == "1" ]; then
    # Restart collectd if running.
    if service collectd status | grep 'running'; then
        service collectd restart
    fi
fi

%postun
if [ "$1" == "0" ]; then
    # Restart collectd if running.
    if service collectd status | grep 'running'; then
        service collectd restart
    fi
fi

%changelog
* Thu Mar 28 2013 Rahat Mahmood <rmahmood@gridcentric.ca>
- Initial package creation

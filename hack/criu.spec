#
# spec file for package criu
#
# Copyright (c) 2020 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           criu
Version:        3.15
Release:        0
Summary:        Checkpoint/Restore In Userspace Tools
License:        GPL-2.0-only
Group:          System/Console
URL:            https://criu.org/
Source:		criu.tar.gz
BuildRequires:  libcap-devel
BuildRequires:  gnutls-devel
BuildRequires:  libnet-devel
BuildRequires:  libnl3-devel
BuildRequires:  pkgconfig
BuildRequires:  protobuf-c
BuildRequires:  protobuf-devel
%define _unpackaged_files_terminate_build 0
%description
Checkpoint/Restore In Userspace, or CRIU, is a software tool for Linux
operating system. Using this tool, you can freeze a running application
(or part of it) and checkpoint it to a hard drive as a collection of
files. You can then use the files to restore and run the application from
the point it was frozen at.

%prep
%setup -q
# default off
echo "BINFMT_MISC_VIRTUALIZED" > .config

%build
%global _lto_cflags %{_lto_cflags} -ffat-lto-objects
export CFLAGS="%{optflags}"
%ifarch %arm
export CFLAGS="$CFLAGS -Wno-error=deprecated"
%endif
# WERROR=0 is needed for avoiding warning due to doubly _GNU_SOURCE defines
make V=1 %{?_smp_mflags} %{?make_options} WERROR=0

%install
%make_install V=1 %{?make_options} WERROR=0 \
	PREFIX=%{_prefix} \
	LIBDIR=%{_libdir} \
	LIBEXECDIR=%{_libexecdir}
# remove static libs
rm -f %{buildroot}%{_libdir}/lib*.a \
      %{buildroot}%{_libexecdir}/compel/*.a

# remove stable files
rm -f %{buildroot}%{_includedir}/compel/plugins/std/asm/.gitignore
# for compatiblity
ln -s criu %{buildroot}%{_sbindir}/crtools
ln -s criu.8 %{buildroot}%{_mandir}/man8/crtools.8

%files
%license COPYING
%doc README.md
%{_sbindir}/criu
%{_sbindir}/crtools
%{_bindir}/compel
%{_bindir}/crit
%{_mandir}/man1/compel.1%{?ext_man}
%{_mandir}/man1/crit.1%{?ext_man}
%{_mandir}/man8/criu.8%{?ext_man}
%{_mandir}/man8/crtools.8%{?ext_man}
%{_libexecdir}/criu
%{_libexecdir}/compel
%{_libdir}/libcriu.so.*
%{_libdir}/libcompel.so.*

%changelog

%if 0%{?fedora} >= 27 || 0%{?rhel} > 7
%global py_prefix python3
%global py_binary %{py_prefix}
%else
%global py_prefix python
%global py_binary python2
%endif

# With annobin enabled, CRIU does not work anymore. It seems CRIU's
# parasite code breaks if annobin is enabled.
%undefine _annotated_build

Name: criu
Version: %{version}
Release: %{commit_num}.%{commit}%{?dist}
Provides: crtools = %{version}-%{release}
Obsoletes: crtools <= 1.0-2
Summary: Tool for Checkpoint/Restore in User-space
License: GPLv2
URL: http://criu.org/
Source0: criu.tar.gz

%if 0%{?rhel} && 0%{?rhel} <= 7
BuildRequires: perl
# RHEL has no asciidoc; take man-page from Fedora 26
# zcat /usr/share/man/man8/criu.8.gz > criu.8
#Source1: criu.8
#Source2: crit.1
#Source3: compel.1
# The patch aio-fix.patch is needed as RHEL7
# doesn't do "nr_events *= 2" in ioctx_alloc().
#Patch100: aio-fix.patch
%endif

#Source4: criu-tmpfiles.conf

BuildRequires: gcc
BuildRequires: systemd
BuildRequires: libnet-devel
BuildRequires: protobuf-devel protobuf-c-devel %{py_prefix}-devel libnl3-devel libcap-devel
%if 0%{?fedora} || 0%{?rhel} > 7
BuildRequires: asciidoc xmlto
BuildRequires: perl-interpreter
BuildRequires: libselinux-devel
BuildRequires: gnutls-devel
#BuildRequires: nftables-devel
# Checkpointing containers with a tmpfs requires tar
Recommends: tar
%if 0%{?fedora}
BuildRequires: libbsd-devel
%endif
%endif
BuildRequires: make

# user-space and kernel changes are only available for x86_64, arm,
# ppc64le, aarch64 and s390x
# https://bugzilla.redhat.com/show_bug.cgi?id=902875
ExclusiveArch: x86_64 %{arm} ppc64le aarch64 s390x

%description
criu is the user-space part of Checkpoint/Restore in User-space
(CRIU), a project to implement checkpoint/restore functionality for
Linux in user-space.

%if 0%{?fedora}
%package devel
Summary: Header files and libraries for %{name}
Requires: %{name} = %{version}-%{release}

%description devel
This package contains header files and libraries for %{name}.

%package libs
Summary: Libraries for %{name}
Requires: %{name} = %{version}-%{release}

%description libs
This package contains the libraries for %{name}
%endif

%package -n %{py_prefix}-%{name}
%{?python_provide:%python_provide %{py_prefix}-%{name}}
Summary: Python bindings for %{name}
%if 0%{?rhel} && 0%{?rhel} <= 7
Requires: protobuf-python
Requires: %{name} = %{version}-%{release} %{py_prefix}-ipaddress
%else
Requires: %{py_prefix}-protobuf
Obsoletes: python2-criu < 3.10-1
%endif

%description -n %{py_prefix}-%{name}
%{py_prefix}-%{name} contains Python bindings for %{name}.

%package -n crit
Summary: CRIU image tool
Requires: %{py_prefix}-%{name} = %{version}-%{release}

%description -n crit
crit is a tool designed to decode CRIU binary dump files and show
their content in human-readable form.


%prep
%setup -q

#%if 0%{?rhel} && 0%{?rhel} <= 7
#%patch100 -p1
#%endif

%build
# This package calls LD directly without specifying the LTO plugins.  Until
# that is fixed, disable LTO.
%define _lto_cflags %{nil}

# %{?_smp_mflags} does not work
# -fstack-protector breaks build
CFLAGS+=`echo %{optflags} | sed -e 's,-fstack-protector\S*,,g'` make V=1 WERROR=0 PREFIX=%{_prefix} COMMIT=%{commit} RUNDIR=/run/criu PYTHON=%{py_binary}
%if 0%{?fedora} || 0%{?rhel} > 7
make docs V=1
%endif


%install
make install-criu DESTDIR=$RPM_BUILD_ROOT COMMIT=%{commit} PREFIX=%{_prefix} LIBDIR=%{_libdir}
make install-lib DESTDIR=$RPM_BUILD_ROOT COMMIT=%{commit} PREFIX=%{_prefix} LIBDIR=%{_libdir} PYTHON=%{py_binary}
%if 0%{?fedora} || 0%{?rhel} > 7
# only install documentation on Fedora as it requires asciidoc,
# which is not available on RHEL7
make install-man DESTDIR=$RPM_BUILD_ROOT PREFIX=%{_prefix} LIBDIR=%{_libdir}
%else
install -p -m 644  -D %{SOURCE0} $RPM_BUILD_ROOT%{_mandir}/man8/%{name}.8
install -p -m 644  -D %{SOURCE0} $RPM_BUILD_ROOT%{_mandir}/man1/compel.1
install -p -m 644  -D %{SOURCE0} $RPM_BUILD_ROOT%{_mandir}/man1/crit.1
%endif

mkdir -p %{buildroot}%{_tmpfilesdir}
#nstall -m 0644 %{SOURCE4} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -d -m 0755 %{buildroot}/run/%{name}/

%if 0%{?rhel}
# remove devel and libs packages
rm -rf $RPM_BUILD_ROOT%{_includedir}/criu
rm $RPM_BUILD_ROOT%{_libdir}/*.so*
rm -rf $RPM_BUILD_ROOT%{_libdir}/pkgconfig
rm -rf $RPM_BUILD_ROOT%{_libexecdir}/%{name}
%endif

# remove static lib
rm -f $RPM_BUILD_ROOT%{_libdir}/libcriu.a

%files
%{_sbindir}/%{name}
%if 0%{?fedora} || 0%{?rhel} > 7
%{_sbindir}/%{name}-ns
%doc %{_mandir}/man1/criu-ns.1*
%endif
%doc %{_mandir}/man8/criu.8*
%doc %{_mandir}/man1/compel.1*
%if 0%{?fedora}
%{_libexecdir}/%{name}
%endif
%dir /run/%{name}
#%{_tmpfilesdir}/{name}.conf
%doc README.md COPYING

%if 0%{?fedora}
%files devel
%{_includedir}/criu
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%files libs
%{_libdir}/*.so.*
%endif

%files -n %{py_prefix}-%{name}
%if 0%{?rhel} && 0%{?rhel} <= 7
%{python2_sitelib}/pycriu/*
%{python2_sitelib}/*egg-info
%else
%{python3_sitelib}/pycriu/*
%{python3_sitelib}/*egg-info
%endif

%files -n crit
%{_bindir}/crit
%doc %{_mandir}/man1/crit.1*


%changelog

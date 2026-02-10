Name:           keyspace
Version:        1.0.0
Release:        1%{?dist}
Summary:        Advanced Password Cracking Tool

License:        MIT
URL:            https://github.com/tworjaga/keyspace
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3 >= 3.6
Requires:       python3-qt6
Requires:       python3-flask
Requires:       python3-flask-login
Requires:       python3-cryptography
Requires:       python3-pytest
Requires:       python3-matplotlib

%description
Keyspace is a comprehensive password cracking application featuring:
- Multiple attack types (Dictionary, Brute Force, Rule-based, etc.)
- PyQt6 GUI interface
- Web-based remote interface
- Hashcat and John the Ripper integration
- Cloud wordlist storage
- Advanced security features and audit logging

%prep
%setup -q

%build
# No build step needed for Python application

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_var}/log/%{name}
mkdir -p %{buildroot}%{_var}/lib/%{name}

# Install application files
cp -r * %{buildroot}%{_datadir}/%{name}/
rm -rf %{buildroot}%{_datadir}/%{name}/packaging

# Create executable script
cat > %{buildroot}%{_bindir}/%{name} << EOF
#!/bin/bash
cd %{_datadir}/%{name} && python3 main.py "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

# Create desktop file
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << EOF
[Desktop Entry]
Name=Keyspace
Comment=Advanced Password Cracking Tool
Exec=%{name}
Icon=%{name}
Terminal=false
Type=Application
Categories=Utility;Security;
EOF

# Create default configuration
cat > %{buildroot}%{_sysconfdir}/%{name}/config.yaml << EOF
# Keyspace Configuration
logging:
  level: INFO
  file: %{_var}/log/%{name}/%{name}.log

security:
  session_timeout: 3600
  max_login_attempts: 3

integrations:
  hashcat_enabled: false
  john_enabled: false
  cloud_enabled: false
EOF

%files
%doc README.md USER_GUIDE.md
%license LICENSE
%{_datadir}/%{name}/
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%config(noreplace) %{_sysconfdir}/%{name}/config.yaml
%dir %{_var}/log/%{name}
%dir %{_var}/lib/%{name}

%post
# Create necessary directories if they don't exist
mkdir -p %{_var}/log/%{name}
mkdir -p %{_var}/lib/%{name}

# Set proper permissions
chmod 755 %{_bindir}/%{name}
chmod -R 755 %{_datadir}/%{name}

# Update desktop database
if [ -x %{_bindir}/update-desktop-database ]; then
    %{_bindir}/update-desktop-database
fi

%postun
# Clean up desktop database
if [ -x %{_bindir}/update-desktop-database ]; then
    %{_bindir}/update-desktop-database
fi

%changelog
* Mon Feb 05 2026 Keyspace Team <admin@keyspace.local> - 1.0.0-1
- Initial RPM package release
- Complete password cracking tool with GUI and web interfaces

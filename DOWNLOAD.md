# Download Keyspace

Get the latest version of Keyspace for your platform.

## Latest Release

**Version 1.0.0** (January 15, 2024)

[Download v1.0.0](https://github.com/tworjaga/keyspace/releases/tag/v1.0.0) | [Release Notes](CHANGELOG.md)

## Platform Downloads

### Windows

| Package | Size | Download | Requirements |
|---------|------|----------|--------------|
| Installer (.exe) | 45 MB | [Download](https://github.com/tworjaga/keyspace/releases/download/v1.0.0/keyspace-1.0.0-windows.exe) | Windows 10/11 |
| Portable (.zip) | 43 MB | [Download](https://github.com/tworjaga/keyspace/releases/download/v1.0.0/keyspace-1.0.0-windows.zip) | Windows 10/11 |
| Source Code | - | [Source](https://github.com/tworjaga/keyspace/archive/v1.0.0.zip) | Python 3.8+ |

**Installation:**
1. Download the installer
2. Run the .exe file
3. Follow the setup wizard
4. Launch from Start Menu or Desktop

### Linux

#### Debian/Ubuntu (.deb)
```bash
wget https://github.com/tworjaga/keyspace/releases/download/v1.0.0/keyspace_1.0.0_amd64.deb
sudo dpkg -i keyspace_1.0.0_amd64.deb
sudo apt-get install -f
```

#### Fedora/RHEL/CentOS (.rpm)
```bash
wget https://github.com/tworjaga/keyspace/releases/download/v1.0.0/keyspace-1.0.0-1.x86_64.rpm
sudo rpm -i keyspace-1.0.0-1.x86_64.rpm
```

#### Arch Linux (AUR)
```bash
yay -S keyspace
```

#### AppImage (Universal)
| Package | Size | Download |
|---------|------|----------|
| AppImage | 48 MB | [Download](https://github.com/tworjaga/keyspace/releases/download/v1.0.0/keyspace-1.0.0-x86_64.AppImage) |

```bash
chmod +x keyspace-1.0.0-x86_64.AppImage
./keyspace-1.0.0-x86_64.AppImage
```

### macOS

| Package | Size | Download | Requirements |
|---------|------|----------|--------------|
| DMG (Intel) | 50 MB | [Download](https://github.com/tworjaga/keyspace/releases/download/v1.0.0/keyspace-1.0.0-intel.dmg) | macOS 10.14+ |
| DMG (Apple Silicon) | 48 MB | [Download](https://github.com/tworjaga/keyspace/releases/download/v1.0.0/keyspace-1.0.0-arm64.dmg) | macOS 11+ |
| Homebrew | - | `brew install keyspace` | macOS 10.14+ |

**Installation (DMG):**
1. Download the DMG file
2. Open it
3. Drag to Applications folder
4. Allow in System Settings > Privacy & Security

### Docker

```bash
docker pull tworjaga/keyspace:latest
docker run -it --rm tworjaga/keyspace
```

Or use Docker Compose:
```bash
git clone https://github.com/tworjaga/keyspace.git
cd keyspace
docker-compose up -d
```

## Package Managers

### pip (Coming Soon)
```bash
pip install keyspace
```

### Homebrew (macOS/Linux)
```bash
brew tap tworjaga/keyspace
brew install keyspace
```

### Chocolatey (Windows)
```bash
choco install keyspace
```

### Snap (Linux)
```bash
sudo snap install keyspace
```

## Build from Source

### Requirements
- Python 3.8+
- pip
- Git

### Steps
```bash
# Clone repository
git clone https://github.com/tworjaga/keyspace.git
cd keyspace

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## Beta/Development Versions

### Nightly Builds
[Download latest development build](https://github.com/tworjaga/keyspace/actions)

**Warning**: Development builds may be unstable.

### Previous Releases
[View all releases](https://github.com/tworjaga/keyspace/releases)

## Verification

### Checksums

Verify your download with SHA-256 checksums:

```
keyspace-1.0.0-windows.exe: a1b2c3d4e5f6...
keyspace_1.0.0_amd64.deb: b2c3d4e5f6g7...
keyspace-1.0.0-intel.dmg: c3d4e5f6g7h8...
```

[Download checksums file](https://github.com/tworjaga/keyspace/releases/download/v1.0.0/SHA256SUMS)

### GPG Signatures

All releases are signed with our GPG key:

```bash
# Import our public key
gpg --keyserver keyserver.ubuntu.com --recv-key YOUR_KEY_ID

# Verify signature
gpg --verify keyspace-1.0.0-windows.exe.sig
```

[Download public key](https://keyspace.example.com/public.key)

## System Requirements

### Minimum
- **OS**: Windows 10, Ubuntu 18.04, macOS 10.14
- **RAM**: 4 GB
- **Storage**: 500 MB
- **Display**: 1280x720

### Recommended
- **OS**: Windows 11, Ubuntu 22.04, macOS 13
- **RAM**: 16 GB
- **Storage**: 2 GB
- **Display**: 1920x1080

## Installation Guides

- [Windows Installation](INSTALL.md#windows)
- [Linux Installation](INSTALL.md#linux)
- [macOS Installation](INSTALL.md#macos)
- [Docker Installation](INSTALL.md#docker)

## Troubleshooting

### Download Issues

**Slow download?**
- Try using a download manager
- Use GitHub mirror: [mirror.example.com](https://mirror.example.com)

**Download interrupted?**
- Resume with: `wget -c <url>`
- Or use browser's resume capability

**Corrupted file?**
- Verify checksum
- Re-download the file
- Try alternative mirror

### Installation Issues

See [INSTALL.md](INSTALL.md) for detailed troubleshooting.

## Stay Updated

### Notification Options

- **GitHub**: Watch the repository for releases
- **Email**: [Subscribe to newsletter](https://keyspace.example.com/newsletter)
- **RSS**: [Releases feed](https://github.com/tworjaga/keyspace/releases.atom)
- **Twitter**: [@keyspace](https://twitter.com/keyspace)

### Auto-Update

The application can check for updates automatically:
- **GUI**: Help > Check for Updates
- **CLI**: `keyspace --check-update`

## Archive

### Old Versions

| Version | Date | Download |
|---------|------|----------|
| 0.9.0 | 2023-12-01 | [Download](https://github.com/tworjaga/keyspace/releases/tag/v0.9.0) |
| 0.8.0 | 2023-10-15 | [Download](https://github.com/tworjaga/keyspace/releases/tag/v0.8.0) |

### LTS Releases

Long-term support versions for enterprise users:

| Version | Support Until | Download |
|---------|-------------|----------|
| 1.0.x LTS | 2026-01-15 | [Download](https://github.com/tworjaga/keyspace/releases/tag/v1.0.0) |

## Mirrors

### Official Mirrors

- **GitHub**: [github.com/tworjaga/keyspace](https://github.com/tworjaga/keyspace)
- **SourceForge**: [sourceforge.net/projects/keyspace](https://sourceforge.net/projects/keyspace)

### Community Mirrors

- [Mirror 1](https://mirror1.example.com)
- [Mirror 2](https://mirror2.example.com)

## Support

Need help with installation?

- [Installation Guide](INSTALL.md)
- [FAQ](FAQ.md)
- [GitHub Issues](https://github.com/tworjaga/keyspace/issues)
- [Discord](https://discord.gg/keyspace)
- Email: support@keyspace.example.com

---

**Ready to install?** → [Installation Guide](INSTALL.md)

**New user?** → [Quick Start Guide](QUICKSTART.md)


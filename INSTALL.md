# Installation Guide

Complete installation instructions for Keyspace on all supported platforms.

## System Requirements


### Minimum Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: 3.8 or higher
- **RAM**: 4 GB minimum (8 GB recommended)
- **Storage**: 500 MB free space
- **Display**: 1280x720 resolution

### Recommended Requirements
- **OS**: Windows 11, Ubuntu 22.04, macOS 13+
- **Python**: 3.10 or higher
- **RAM**: 16 GB or more
- **Storage**: 2 GB free space (for wordlists)
- **Display**: 1920x1080 resolution
- **GPU**: Optional, for future GPU acceleration

## Windows Installation


### Method 1: Using Pre-built Package (Recommended)

1. **Download**
   - Download `keyspace-v1.0.0-windows.exe` from [Releases](https://github.com/tworjaga/keyspace/releases)


2. **Install**
   - Run the installer
   - Follow the setup wizard
   - Choose installation directory

3. **Launch**
   - Desktop shortcut: Double-click "Keyspace"
   - Start Menu: Search "Keyspace"
   - Command line: `keyspace`


### Method 2: Using Python (Developers)

1. **Install Python**
   - Download Python 3.8+ from [python.org](https://python.org)
   - **Important**: Check "Add Python to PATH" during installation

2. **Download Source**
   ```bash
   git clone https://github.com/tworjaga/keyspace.git
   cd keyspace
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run**
   ```bash
   python main.py
   ```
   Or use the batch file:
   ```bash
   start.bat
   ```

## Linux Installation


### Ubuntu/Debian

#### Option A: .deb Package

1. **Download**
   ```bash
   wget https://github.com/tworjaga/keyspace/releases/download/v1.0.0/keyspace_1.0.0_amd64.deb

   ```

2. **Install**
   ```bash
   sudo dpkg -i keyspace_1.0.0_amd64.deb

   sudo apt-get install -f  # Fix dependencies if needed
   ```

3. **Launch**
   ```bash
   keyspace
   ```

#### Option B: Build from Source

1. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-venv git
   ```

2. **Download Source**
   ```bash
   git clone https://github.com/tworjaga/keyspace.git
   cd keyspace
   ```

3. **Create Virtual Environment (Recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run**
   ```bash
   python3 main.py
   ```

### Fedora/RHEL/CentOS

#### Option A: .rpm Package

1. **Download**
   ```bash
   wget https://github.com/tworjaga/keyspace/releases/download/v1.0.0/keyspace-1.0.0-1.x86_64.rpm

   ```

2. **Install**
   ```bash
   sudo rpm -i keyspace-1.0.0-1.x86_64.rpm

   ```

3. **Launch**
   ```bash
   keyspace
   ```

## macOS Installation


### Method 1: DMG Installer (Recommended)

1. **Download**
   - Download `keyspace-v1.0.0.dmg` from [Releases](https://github.com/tworjaga/keyspace/releases)


2. **Install**
   - Open the DMG file
   - Drag "Keyspace" to Applications folder


3. **Launch**
   - Open from Applications
   - **Note**: You may need to allow the app in System Settings > Privacy & Security


### Method 2: Build from Source

1. **Install Homebrew** (if not installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Dependencies**
   ```bash
   brew install python@3.10 git
   ```

3. **Download Source**
   ```bash
   git clone https://github.com/tworjaga/keyspace.git
   cd keyspace
   ```

4. **Create Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run**
   ```bash
   python3 main.py
   ```

## Docker Installation


### Quick Start with Docker

1. **Pull Image**
   ```bash
   docker pull tworjaga/keyspace:latest

   ```

2. **Run Container**
   ```bash
   docker run -it --rm \
     -v $(pwd)/wordlists:/app/wordlists \
     -v $(pwd)/results:/app/results \
     tworjaga/keyspace

   ```

### Using Docker Compose

1. **Clone Repository**
   ```bash
   git clone https://github.com/tworjaga/keyspace.git
   cd keyspace

   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Access Application**
   - GUI: `docker-compose exec keyspace python main.py`

   - Web: Open http://localhost:8080

## Troubleshooting


### Common Issues

#### "Python not found"
**Solution**: Install Python 3.8+ and ensure it's in PATH

#### "Permission denied"
**Solution**: 
- Windows: Run as Administrator
- Linux/macOS: Use `sudo` or fix permissions with `chmod +x`

#### "Module not found"
**Solution**: 
```bash
pip install -r requirements.txt
```

### Getting Help

- Check [FAQ.md](FAQ.md) for common questions
- Search [GitHub Issues](https://github.com/tworjaga/keyspace/issues)
- Join [Discord](https://discord.gg/keyspace)


---

**Next Steps**: [Quick Start Guide](QUICKSTART.md) → [User Guide](USER_GUIDE.md)


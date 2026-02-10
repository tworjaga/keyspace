# Keyspace

Advanced password cracking tool with modern GUI built using PyQt6. Features multiple attack types including dictionary attacks, brute force, rule-based attacks, and more.


## Features

- **Multiple Attack Types**:
  - Dictionary Attack (WPA2)
  - Brute Force Attack
  - Rule-based Attack
  - Hybrid Attack
  - Mask Attack
  - Combinator Attack
  - PIN Code Attack

- **Advanced Features**:
  - Real-time progress monitoring
  - Speed and ETA calculations
  - Comprehensive logging
  - Pause/Resume functionality
  - Checkpoint saving for resume capability
  - Modern PyQt6 GUI
  - Multiple mutation rules for rule-based attacks

- **GUI Features**:
  - Dashboard with live statistics
  - Attack log viewer
  - Results panel
  - Configuration panel
  - Progress bars and status indicators

## Installation

### Option 1: Manual Installation

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Platform-Specific Packages

The tool provides native packages for different platforms:

#### Linux (Debian/Ubuntu)
```bash
# Build Debian package
./packaging/linux/deb/build_deb.sh

# Or use the universal build script
./build_packages.sh
```

#### Linux (Red Hat/Fedora/CentOS)
```bash
# Build RPM package
./packaging/linux/rpm/build_rpm.sh

# Or use the universal build script
./build_packages.sh
```

#### macOS
```bash
# Build DMG installer
./packaging/macos/build_dmg.sh

# Or use the universal build script
./build_packages.sh
```

### Option 3: Docker

Run the tool in a container:
```bash
# Build and run with Docker
docker build -t keyspace .

docker run -it --rm keyspace


# Or use Docker Compose for full stack
docker-compose up
```

## Usage

### GUI Mode (Recommended)

Run the tool with the graphical interface:

```bash
python main.py
```

Or use the provided batch file:
```bash
start.bat
```

### Command Line Mode

You can also pre-configure attacks via command line:

```bash
python main.py --target "demo_target" --attack-type "Brute Force Attack" --min-length 8 --max-length 12
```

## Attack Types

### Dictionary Attack (WPA2)
Uses a wordlist file to test passwords against a target. Requires a wordlist file.

### Brute Force Attack
Generates all possible combinations within the specified character set and length range.

### Rule-based Attack
Applies various mutation rules to base passwords from a wordlist, including:
- Case variations
- Leet speak
- Number appending/prepending
- Special character insertion
- Keyboard walk patterns
- And more

### Hybrid Attack
Combines dictionary words with common additions (numbers, special chars, etc.)

### Mask Attack
Uses password masks (like Hashcat) to generate specific patterns.

### Combinator Attack
Combines words from two wordlists.

### PIN Code Attack
Specialized attack for numeric PIN codes of various lengths.

## Configuration

### Basic Settings
- **Target**: The target to attack (SSID, username, etc.)
- **Attack Type**: Select from available attack methods
- **Wordlist**: Path to wordlist file (required for some attacks)
- **Min/Max Length**: Password length range for brute force
- **Charset**: Characters to use in brute force generation

### Advanced Settings
The tool includes various performance optimizations:
- Memory-efficient processing
- Batch processing
- Speed monitoring with moving averages
- Error handling and recovery

## GUI Layout

The main window is divided into several panels:

1. **Attack Configuration**: Set up your attack parameters
2. **Dashboard**: Live statistics and progress
3. **Attack Log**: Detailed logging of attack progress
4. **Statistics**: Performance metrics and analysis
5. **Results**: Found passwords and attack outcomes

## Safety & Ethics

**WARNING**: This tool is for educational and security research purposes only. Unauthorized use against systems you don't own may be illegal. Always obtain proper authorization before performing security testing.


## Requirements

- Python 3.8+
- PyQt6
- Windows/Linux/macOS

## License

This project is for educational purposes. Use responsibly.

## Contributing

Contributions welcome! Please ensure all code follows security best practices and includes proper error handling.

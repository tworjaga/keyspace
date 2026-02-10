# Keyspace - User Guide


## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [GUI Overview](#gui-overview)
5. [Attack Configuration](#attack-configuration)
6. [Attack Types](#attack-types)
7. [Monitoring Progress](#monitoring-progress)
8. [Results and Logging](#results-and-logging)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

## Introduction

Keyspace is a comprehensive password cracking application with a modern graphical interface. It supports multiple attack methodologies and provides real-time monitoring of cracking progress.


### Key Features
- Multiple attack types (Dictionary, Brute Force, Rule-based, etc.)
- Real-time progress monitoring
- Pause/Resume functionality
- Comprehensive logging
- Modern PyQt6 GUI
- Performance statistics
- Export capabilities

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows, Linux, or macOS

### Quick Installation
1. Download or clone the Keyspace repository

2. Navigate to the project directory
3. Run the installation script:

**Windows:**
```bash
start.bat
```

**Manual Installation:**
```bash
pip install -r requirements.txt
```

## Getting Started

### Launching the Application

**Windows:**
Double-click `start.bat` or run:
```bash
python main.py
```

**Command Line:**
```bash
python main.py --target "demo_target" --attack-type "Brute Force Attack"
```

### First Time Setup
1. Launch the application
2. The main window will open with default settings
3. Configure your attack parameters (see [Attack Configuration](#attack-configuration))
4. Click "▶ Start Attack" to begin

## GUI Overview

The main window is divided into several key areas:

### 1. Menu Bar
- **File**: New/Open/Save sessions, Export results
- **Attack**: Start/Stop/Pause/Resume attacks
- **Tools**: Wordlist generator, Charset analyzer
- **Help**: About dialog

### 2. Toolbar
- Quick Start/Stop buttons
- Current target display
- Progress indicator

### 3. Attack Configuration Panel (Left Top)
Main control center for setting up attacks.

### 4. Tabbed Interface (Left Bottom)
- **Dashboard**: Live statistics and progress
- **Attack Log**: Detailed operation logs
- **Statistics**: Performance metrics
- **Results**: Found passwords and outcomes

### 5. Results Panel (Right)
Displays attack results and findings.

### 6. Status Bar
Shows current status, attempt count, and speed.

## Attack Configuration

### Basic Settings

#### Target
- Enter the target to attack (WiFi SSID, username, service name)
- Example: `MyWiFiNetwork`, `admin`, `demo_target`

#### Attack Type
Select from available attack methods:
- Dictionary Attack (WPA2)
- Brute Force Attack
- Rule-based Attack
- Hybrid Attack
- Mask Attack
- Combinator Attack
- PIN Code Attack
- Rainbow Table Attack
- Markov Chain Attack
- Neural Network Attack
- Distributed Attack

#### Wordlist (for applicable attacks)
- Click "Browse..." to select a wordlist file
- Supports .txt files with one password per line
- Recommended: RockYou.txt or custom wordlists

#### Password Length
- **Min Length**: Minimum password length to try
- **Max Length**: Maximum password length to try
- Brute force will generate combinations between these lengths

#### Character Set
- Default: `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*`
- Customize for specific requirements
- Common sets:
  - Lowercase only: `abcdefghijklmnopqrstuvwxyz`
  - Alphanumeric: `abcdefghijklmnopqrstuvwxyz0123456789`
  - All printable: Include spaces and special characters

### Control Buttons
- **▶ Start Attack**: Begin the configured attack
- **⏹ Stop Attack**: Immediately halt the current attack
- **⏸ Pause**: Temporarily suspend the attack (can be resumed)
- **▶ Resume**: Continue a paused attack

## Attack Types

### Dictionary Attack (WPA2)
**Best for:** Known password lists, common passwords

**Requirements:** Wordlist file

**How it works:**
1. Loads passwords from the specified wordlist
2. Tests each password against the target
3. Stops when password is found or list is exhausted

**Configuration:**
- Select "Dictionary Attack (WPA2)" from Attack Type
- Choose wordlist file
- Click Start

### Brute Force Attack
**Best for:** Short passwords, known character sets

**Requirements:** Character set, length range

**How it works:**
1. Generates all possible combinations within length range
2. Tests each combination systematically
3. Continues until password found or manually stopped

**Configuration:**
- Select "Brute Force Attack"
- Set Min/Max Length (keep small for testing)
- Customize charset if needed
- Click Start

**⚠️ Warning:** Can take extremely long for longer passwords!

### Rule-based Attack
**Best for:** Passwords with predictable patterns

**Requirements:** Wordlist file

**How it works:**
1. Takes base passwords from wordlist
2. Applies various mutation rules:
   - Case variations (Password → password, PASSWORD)
   - Leet speak (password → p4ssw0rd)
   - Number appending (password → password123)
   - Special character insertion
   - Keyboard patterns
   - And many more

**Configuration:**
- Select "Rule-based Attack"
- Choose wordlist file
- Click Start

### Hybrid Attack
**Best for:** Common password + addition patterns

**Requirements:** Wordlist file

**How it works:**
1. Takes each word from wordlist
2. Tests original word
3. Tests word + common additions (123, !, 2023, etc.)
4. Tests common additions + word

**Configuration:**
- Select "Hybrid Attack"
- Choose wordlist file
- Click Start

### Mask Attack
**Best for:** Known password patterns

**Requirements:** None (uses predefined masks)

**How it works:**
1. Uses common password masks like:
   - `?u?l?l?l?l?l?l?l` (8 chars: Upper + 7 lower)
   - `?u?l?l?l?l?d?d?d` (8 chars: Upper + 4 lower + 3 digits)
   - `?a?a?a?a?a?a?a?a` (8 any characters)

**Configuration:**
- Select "Mask Attack"
- Click Start

### Combinator Attack
**Best for:** Two-word combinations

**Requirements:** Wordlist file

**How it works:**
1. Combines words from wordlist: word1 + word2
2. Tests all combinations

**Configuration:**
- Select "Combinator Attack"
- Choose wordlist file
- Click Start

### PIN Code Attack
**Best for:** Numeric PINs

**Requirements:** None

**How it works:**
1. Tests all possible PIN combinations
2. Supports 4, 5, 6, and 8-digit PINs

**Configuration:**
- Select "PIN Code Attack"
- Click Start

### Rainbow Table Attack
**Best for:** Precomputed hash attacks

**Requirements:** None (uses simulated rainbow tables)

**How it works:**
1. Uses precomputed hash chains (rainbow tables)
2. Performs fast lookups for known hashes
3. Reduces computation time for repeated attacks

**Configuration:**
- Select "Rainbow Table Attack"
- Click Start

**Note:** Real implementation would require actual rainbow table files

### Markov Chain Attack
**Best for:** Statistical password prediction

**Requirements:** None

**How it works:**
1. Analyzes common password patterns statistically
2. Builds transition probability matrices
3. Generates passwords based on learned patterns
4. Tests statistically likely combinations first

**Configuration:**
- Select "Markov Chain Attack"
- Set Min/Max Length
- Click Start

### Neural Network Attack
**Best for:** AI-powered password prediction

**Requirements:** None (uses simulated neural network)

**How it works:**
1. Uses machine learning to predict common passwords
2. Analyzes patterns in password datasets
3. Generates passwords based on learned patterns
4. Prioritizes high-probability candidates

**Configuration:**
- Select "Neural Network Attack"
- Click Start

**Note:** Real implementation would require trained neural network models

### Distributed Attack
**Best for:** Large-scale cracking operations

**Requirements:** None (simulates distributed computing)

**How it works:**
1. Simulates multiple worker nodes
2. Distributes workload across simulated machines
3. Coordinates attack across multiple processes
4. Aggregates results from all workers

**Configuration:**
- Select "Distributed Attack"
- Click Start

**Note:** Real implementation would require network coordination

## Monitoring Progress

### Dashboard Tab
- **Attack Status**: Current state (Running, Paused, Stopped)
- **Progress Bar**: Visual progress indicator
- **Speed**: Current attempts per second
- **ETA**: Estimated time to completion
- **Attempts**: Total passwords tested
- **Elapsed Time**: Time since attack started

### Real-time Updates
- Progress updates every few seconds
- Speed calculations use moving averages for stability
- ETA recalculates based on current performance

### Performance Metrics
- **Current Speed**: Attempts per second right now
- **Average Speed**: Overall average speed
- **Peak Speed**: Highest speed achieved
- **Total Attempts**: Cumulative count

## Results and Logging

### Results Panel
- Shows successful password discoveries
- Displays attempt numbers and timing
- Includes hash information (if available)

### Attack Log Tab
- Detailed chronological log of operations
- Shows attack initialization
- Records progress milestones
- Logs errors and warnings
- Timestamps all entries

### Exporting Results
1. Go to **File → Export → Export to CSV/HTML**
2. Choose save location
3. Results saved in selected format

## Advanced Features

### Pause/Resume
- Pause attacks for later continuation
- Resume from exact stopping point
- Useful for long-running attacks

### Session Management
- **New Session**: Clear all data, start fresh
- **Save Session**: Save current configuration
- **Open Session**: Load previous configuration

### Command Line Options
```bash
python main.py [options]

Options:
  --target TARGET          Target for attack
  --attack-type TYPE       Attack type
  --wordlist FILE          Wordlist file path
  --min-length N           Minimum password length
  --max-length N           Maximum password length
  --charset CHARS          Character set
```

### Logging
- Automatic log file creation in `logs/bruteforce.log`
- Console output for debugging
- Log rotation for long-term use

## Troubleshooting

### Common Issues

#### "Wordlist file not found"
- Check file path is correct
- Ensure file exists and is readable
- Use absolute paths if relative paths fail

#### "Attack scope too large"
- Reduce Max Length for brute force attacks
- Use smaller character sets
- Consider alternative attack types

#### GUI not responding
- Attacks run in separate threads
- GUI should remain responsive
- If frozen, force close and restart

#### Memory errors
- Reduce batch size in code
- Use smaller wordlists
- Close other applications

#### Slow performance
- Some attack types are computationally intensive
- Consider hardware limitations
- Use optimized wordlists

### Performance Tips
- Use SSD storage for wordlists
- Close unnecessary applications
- Monitor system resources
- Use appropriate attack types for your hardware

## Best Practices

### Security & Ethics
- **⚠️ LEGAL WARNING**: Only use on systems you own or have explicit permission to test
- Obtain written authorization before security testing
- Respect applicable laws and regulations

### Attack Strategy
1. **Start Simple**: Begin with dictionary attacks
2. **Profile Target**: Use known information about the target
3. **Combine Methods**: Use hybrid approaches for better results
4. **Monitor Progress**: Don't let attacks run unsupervised for too long

### Wordlist Selection
- **RockYou.txt**: Classic wordlist with common passwords
- **Custom Lists**: Create based on target knowledge
- **Industry Specific**: Use lists relevant to the target domain
- **Size vs Speed**: Balance coverage with performance

### Hardware Considerations
- **CPU**: More cores = better performance
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: Fast SSD for wordlist access
- **Cooling**: Long attacks generate heat

### Session Management
- Save configurations for reuse
- Export results regularly
- Keep logs for analysis
- Document successful methodologies

### Maintenance
- Keep dependencies updated
- Monitor log files for errors
- Clean temporary files periodically
- Backup important configurations

## Support

For issues or questions:
1. Check this user guide
2. Review the README.md
3. Check log files for error details
4. Ensure all prerequisites are met

## Version History

- **v1.0**: Initial release with core attack types and GUI

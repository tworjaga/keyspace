# Changelog

All notable changes to Keyspace will be documented in this file.


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GPU acceleration support (experimental)
- Distributed attack mode for multiple machines
- Neural network-based password prediction
- Cloud wordlist storage integration (AWS S3, GCS, Azure)
- REST API for remote control
- WebSocket support for real-time updates
- Web-based interface alternative to GUI
- Docker containerization
- CI/CD pipeline with GitHub Actions

### Changed
- Improved memory efficiency for large wordlists
- Enhanced progress tracking with detailed statistics
- Updated PyQt6 to latest version
- Refactored attack engine for better performance

### Fixed
- Memory leak in long-running attacks
- Unicode handling in wordlists
- Progress bar accuracy for certain attack types
- GUI responsiveness during intensive operations

## [1.0.0] - 2024-01-15

### Added
- Initial release of Keyspace

- Modern PyQt6-based GUI with tabbed interface
- Multiple attack types:
  - Dictionary Attack (WPA2)
  - Brute Force Attack
  - Rule-based Attack with 15+ mutation rules
  - Hybrid Attack
  - Mask Attack
  - Combinator Attack
  - PIN Code Attack
  - Rainbow Table Attack
  - Markov Chain Attack
- Real-time progress monitoring with graphs
- Speed and ETA calculations
- Pause/Resume functionality
- Session management (save/load)
- Comprehensive logging system
- Results export (CSV, JSON, TXT)
- Wordlist Generator tool
- Charset Analyzer tool
- Attack Profiler tool
- Integration with Hashcat
- Integration with John the Ripper
- Dark/Light theme switching
- Keyboard shortcuts configuration
- Security features:
  - Encrypted session storage
  - Audit logging
  - Permission management
  - Compliance reporting
- Cross-platform support:
  - Windows 10/11
  - Linux (Ubuntu, Fedora, Debian)
  - macOS 10.14+
- Packaging:
  - Windows installer (.exe)
  - Linux packages (.deb, .rpm)
  - macOS DMG
  - Docker image
- Documentation:
  - User Guide
  - API Documentation
  - FAQ
  - Contributing Guidelines
  - Security Policy

### Security
- Implemented secure session encryption
- Added audit logging for compliance
- Created security policy and vulnerability reporting process

## [0.9.0] - 2023-12-01 (Beta)

### Added
- Beta release for testing
- Core attack engine
- Basic GUI implementation
- Initial test suite
- Documentation draft

### Changed
- Optimized password generation algorithms
- Improved error handling

### Fixed
- Various bugs from alpha testing
- GUI layout issues on different screen sizes

## [0.8.0] - 2023-10-15 (Alpha)

### Added
- Alpha release for internal testing
- Proof of concept for attack types
- Basic GUI prototype

## Roadmap

### Version 1.1.0 (Planned - Q2 2024)
- [ ] GPU acceleration (CUDA/OpenCL)
- [ ] Additional attack types:
  - Fingerprint attack
  - PRINCE attack
  - Association attack
- [ ] Enhanced wordlist management
- [ ] Performance profiling tools
- [ ] Plugin system for custom attacks

### Version 1.2.0 (Planned - Q3 2024)
- [ ] Machine learning password generation
- [ ] Advanced pattern recognition
- [ ] Distributed cracking network
- [ ] Mobile companion app
- [ ] Enhanced reporting and analytics

### Version 2.0.0 (Planned - 2025)
- [ ] Complete architecture redesign
- [ ] Native GPU support
- [ ] Cloud-based cracking service
- [ ] AI-powered attack optimization
- [ ] Enterprise features (SSO, LDAP, etc.)

## Contributing to Changelog

When making changes, add an entry under the `[Unreleased]` section:

```markdown
### Added
- New feature description

### Changed
- Change description

### Deprecated
- Feature being deprecated

### Removed
- Feature being removed

### Fixed
- Bug fix description

### Security
- Security-related change
```

Categories:
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Now removed features
- **Fixed**: Bug fixes
- **Security**: Security-related changes

---

**Full Changelog**: https://github.com/tworjaga/keyspace/compare/v0.9.0...v1.0.0

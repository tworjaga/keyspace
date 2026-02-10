# Frequently Asked Questions (FAQ)

Find answers to common questions about Keyspace.

## General Questions

### What is Keyspace?
Keyspace is an advanced password cracking application with a modern PyQt6 GUI. It supports multiple attack types including dictionary attacks, brute force, rule-based attacks, and more.

### Is it free?
Yes! Keyspace is open-source and free to use under the MIT License.

### What platforms are supported?
- Windows 10/11
- Linux (Ubuntu, Fedora, Debian, etc.)
- macOS 10.14+

### Do I need programming experience?
No! The GUI makes it easy to use without any coding. However, developers can use the API for advanced integrations.

## Getting Started

### How do I install it?
See our [Installation Guide](INSTALL.md) for platform-specific instructions.

Quick start:
```bash
pip install -r requirements.txt
python main.py
```

### What's the minimum system requirement?
- 4 GB RAM (8 GB recommended)
- Python 3.8+
- 500 MB free disk space

### Can I run it without GUI?
Yes! Use the command line mode or API for headless operation.

## Attack Types

### What's the difference between attack types?

| Attack Type | Best For | Speed | Coverage |
|-------------|----------|-------|----------|
| Dictionary | Known passwords | Very Fast | Limited |
| Brute Force | Short passwords | Slow | Complete |
| Rule-based | Common patterns | Fast | Moderate |
| Hybrid | Combined approach | Moderate | Good |
| Mask | Known patterns | Fast | Targeted |

### Which attack should I use?
1. **Start with Dictionary** - Fastest, tests common passwords
2. **Try Rule-based** - If dictionary fails, adds mutations
3. **Use Brute Force** - For short passwords (6-8 chars)
4. **Mask Attack** - When you know the pattern

### How long will an attack take?
It depends on:
- Password length
- Character set size
- Attack type
- Hardware speed

Example: 8-character lowercase password
- Brute force: ~2 hours
- Dictionary: Minutes to hours
- With rules: 10-100x longer than base wordlist

## Configuration

### What wordlist should I use?
Popular options:
- **SecLists** - Comprehensive collection
- **RockYou** - Real leaked passwords
- **Custom** - Build your own with the Wordlist Generator

### How do I create a custom wordlist?
Use the built-in Wordlist Generator:
1. Tools > Wordlist Generator
2. Choose generator type (Pattern, Date, Numbers)
3. Configure options
4. Generate and save

### What's a good charset for brute force?
Start small, expand if needed:
- `?l` (lowercase) - 26 chars
- `?l?d` (lowercase + digits) - 36 chars
- `?l?u?d` (all letters + digits) - 62 chars
- `?l?u?d?s` (all chars) - 95 chars

### How do I use mask attacks?
Mask patterns use placeholders:
- `?l` = lowercase letter
- `?u` = uppercase letter
- `?d` = digit
- `?s` = special character

Example: `?u?l?l?d?d` = "Pass12"

## Troubleshooting

### "No wordlist selected" error
**Solution**: Click "Browse..." and select a wordlist file, or use the Wordlist Generator to create one.

### Attack is very slow
**Solutions**:
- Reduce password length range
- Use smaller charset
- Try dictionary attack instead
- Close other applications
- Check CPU usage

### "Permission denied" error
**Solutions**:
- Windows: Run as Administrator
- Linux/macOS: Check file permissions with `ls -la`

### GUI won't start
**Solutions**:
1. Check Python version: `python --version` (need 3.8+)
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Check for Qt errors: Install Qt platform plugins

### Out of memory error
**Solutions**:
- Use smaller wordlists
- Enable memory-efficient mode
- Increase system RAM
- Use streaming mode for large files

## Security & Legal

### Is this legal to use?
**Yes, if**:
- You own the target system
- You have written authorization
- You're in a controlled lab environment

**No, if**:
- Testing systems without permission
- Attempting to crack others' passwords
- Using for malicious purposes

### Can I use this for WiFi hacking?
Only on networks you own or have explicit permission to test. Unauthorized WiFi access is illegal in most jurisdictions.

### How do I report a security vulnerability?
See [SECURITY.md](SECURITY.md) for responsible disclosure procedures.

### Is my data safe?
- All processing is local
- No data sent to external servers
- Optional encryption for saved sessions
- Audit logging for compliance

## Technical Questions

### Can I integrate with Hashcat/John the Ripper?
Yes! Use the Integrations tab or API:
```python
from keyspace.integrations import HashcatIntegration
```

### Does it support GPU acceleration?
Not yet, but planned for future releases. Currently CPU-only.

### Can I run multiple attacks simultaneously?
Yes! Each attack runs in its own thread. Monitor system resources.

### How do I pause and resume?
Click the Pause button, then Resume when ready. Sessions are automatically saved.

### Where are logs stored?
- Windows: `%APPDATA%\Keyspace\logs\`
- Linux: `~/.local/share/keyspace/logs/`
- macOS: `~/Library/Logs/Keyspace/`

## Performance

### How fast is it?
Typical speeds (CPU):
- Dictionary: 100,000+ passwords/second
- Brute force: 10,000-50,000/second
- Rule-based: 50,000+ mutations/second

### How can I improve performance?
1. Use dictionary over brute force when possible
2. Optimize your wordlist (remove duplicates)
3. Use appropriate charset (don't over-specify)
4. Close unnecessary applications
5. Upgrade hardware (CPU, RAM)

### Why is my speed varying?
Speed depends on:
- Password complexity being tested
- System load
- Attack type
- Target response time (for live systems)

## GUI Features

### Can I customize the interface?
Yes! Use the View menu:
- Switch themes (Light/Dark)
- Show/hide panels
- Configure keyboard shortcuts

### How do I export results?
Click "Export Results" button in the Results panel, or use File > Export.

### Can I filter the attack log?
Yes! Use the filter input above the log to search for specific entries.

### What do the graphs show?
- **Speed Over Time**: Attack performance trend
- **Progress**: Completion percentage over time

## API & Development

### Is there an API?
Yes! REST API and WebSocket for real-time updates. See [API.md](API.md).

### Can I build my own attack module?
Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) for developer guidelines.

### How do I contribute?
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Installation Issues

### pip install fails
**Solutions**:
- Upgrade pip: `pip install --upgrade pip`
- Use virtual environment
- Install build tools: `sudo apt-get install python3-dev` (Linux)

### Docker won't start
**Solutions**:
- Check Docker daemon is running
- Verify port 8080 is available
- Check docker-compose.yml syntax

### macOS "app is damaged" error
**Solution**: 
```bash
xattr -cr /Applications/Keyspace.app
```

## Getting Help

### Where can I get support?
- [GitHub Issues](https://github.com/tworjaga/keyspace/issues)
- [Discord](https://discord.gg/keyspace)
- [Documentation](DOCUMENTATION_INDEX.md)

### How do I report a bug?
Use the bug report template in GitHub Issues. Include:
- Version number
- Operating system
- Steps to reproduce
- Error messages

### Can I request a feature?
Yes! Use GitHub Issues with the feature request template.

## Learning Resources

### Where can I learn more about password security?
- [OWASP Password Security](https://owasp.org/www-project-password-security/)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [SecLists](https://github.com/danielmiessler/SecLists) - Security test resources

### Recommended wordlists?
1. RockYou (common passwords)
2. SecLists (comprehensive)
3. CrackStation (human passwords)
4. Custom (your own)

### How do I create strong passwords?
- 12+ characters
- Mix of letters, numbers, symbols
- No dictionary words
- Use a password manager

---

**Still have questions?** → [Support](SUPPORT.md)

**Found a bug?** → [Report Issue](https://github.com/tworjaga/keyspace/issues)

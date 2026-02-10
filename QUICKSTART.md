# Quick Start Guide

Get started with Keyspace in 5 minutes! This guide will walk you through your first password cracking session.

## 5-Minute Quick Start


### Step 1: Install (1 minute)

**Option A: Using pip**
```bash
pip install -r requirements.txt
```

**Option B: Using Docker**
```bash
docker-compose up
```

**Option C: Windows Quick Start**
```bash
start.bat
```

### Step 2: Launch (30 seconds)

```bash
python main.py
```

The GUI will open with a modern interface.

### Step 3: Configure Your First Attack (2 minutes)

1. **Enter Target**: Type `demo_target` in the Target field
2. **Select Attack Type**: Choose "Dictionary Attack (WPA2)" from the dropdown
3. **Select Wordlist**: Click "Browse..." and select a wordlist file
   - Use the included `test_wordlist.txt` for testing
   - Or download a wordlist from [SecLists](https://github.com/danielmiessler/SecLists)

### Step 4: Start Attack (30 seconds)

1. Click the **"Start Attack"** button

2. Watch the dashboard for real-time progress
3. View results in the Results panel

### Step 5: Monitor Progress (1 minute)

The dashboard shows:
- **Progress Bar**: Attack completion percentage
- **Speed**: Passwords tested per second
- **ETA**: Estimated time remaining
- **Attempts**: Total passwords tested

## Your First Successful Attack


### Demo Attack (No Wordlist Required)

Try the built-in demo:

1. Set Target: `demo`
2. Select Attack: "Brute Force Attack"
3. Set Min Length: `4`
4. Set Max Length: `6`
5. Set Charset: `abc123`
6. Click **Start Attack**


The tool will test combinations like:
- `aaaa`
- `aaab`
- `1234`
- etc.

## Understanding Results

### Success
```
[FOUND] Password Found: demo123

Time: 00:02:15
Attempts: 15,234
Speed: 112.5/sec
```

### No Match
```
[NOT FOUND] Password not found in wordlist

Completed: 100%
Time: 00:05:30
```

## Common Configurations


### Quick Dictionary Attack
```
Target: MyWiFiNetwork
Attack: Dictionary Attack (WPA2)
Wordlist: /path/to/wordlist.txt
```

### Quick Brute Force
```
Target: test_user
Attack: Brute Force Attack
Min Length: 6
Max Length: 8
Charset: abcdefghijklmnopqrstuvwxyz0123456789
```

### PIN Code Attack
```
Target: device_001
Attack: PIN Code Attack
Length: 4-6 digits
```

## GUI Navigation

### Main Panels
1. **Attack Configuration** (Top Left): Set attack parameters
2. **Dashboard** (Bottom Left): Live statistics and graphs
3. **Results** (Right): Found passwords and output

### Tabs
- **Dashboard**: Overview and statistics
- **Attack Log**: Detailed progress log
- **Statistics**: Performance metrics
- **Integrations**: External tool connections


### Keyboard Shortcuts
- `Ctrl+S`: Start Attack
- `Ctrl+T`: Stop Attack
- `Ctrl+P`: Pause Attack
- `Ctrl+R`: Resume Attack

## Safety First

**Important**: Only test systems you own or have written permission to test!


### Legal Checklist
- [ ] You own the target system, OR
- [ ] You have written authorization, OR
- [ ] You're in a controlled lab environment

## Troubleshooting


### Issue: "No wordlist selected"
**Fix**: Click "Browse..." and select a wordlist file

### Issue: "Target is empty"
**Fix**: Enter a target name in the Target field

### Issue: "Attack won't start"
**Fix**: Check that all required fields are filled

### Issue: "Slow performance"
**Fix**: 
- Reduce password length range
- Use a smaller character set
- Close other applications

## Next Steps


### Learn More
- [User Guide](USER_GUIDE.md) - Complete documentation
- [FAQ](FAQ.md) - Common questions
- [API Guide](API.md) - For developers

### Practice
1. Try different attack types
2. Experiment with mutation rules
3. Test with various wordlists
4. Analyze performance metrics

### Advanced Features
- Rule-based attacks with mutations
- Mask attacks for specific patterns
- Hybrid attacks combining methods
- Integration with Hashcat/John the Ripper

## Learning Path


### Beginner
1. [x] Complete this Quick Start

2. Read [User Guide - Basics](USER_GUIDE.md#basics)
3. Try all attack types with demo targets

### Intermediate
1. Learn [mutation rules](USER_GUIDE.md#mutation-rules)
2. Understand [mask attacks](USER_GUIDE.md#mask-attacks)
3. Configure [integrations](USER_GUIDE.md#integrations)

### Advanced
1. Study [API documentation](API.md)
2. Read [contributing guide](CONTRIBUTING.md)
3. Develop custom attack modules

## Pro Tips


1. **Start Small**: Test with short passwords first
2. **Use Wordlists**: More efficient than brute force
3. **Monitor Resources**: Watch CPU and memory usage
4. **Save Sessions**: Use pause/resume for long attacks
5. **Check Logs**: Review attack logs for insights

## Quick Links


- [Full Documentation](DOCUMENTATION_INDEX.md)
- [Installation Guide](INSTALL.md)
- [FAQ](FAQ.md)
- [Support](SUPPORT.md)

---

**Ready to dive deeper?** → [Read the User Guide](USER_GUIDE.md)

**Questions?** → [Check the FAQ](FAQ.md)

**Need help?** → [Get Support](SUPPORT.md)

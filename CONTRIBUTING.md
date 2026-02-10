# Contributing to Keyspace

Thank you for your interest in contributing to Keyspace! This document provides guidelines and instructions for contributing.

## Ways to Contribute

### Code Contributions
- **Bug Fixes**: Fix issues reported by users
- **Features**: Add new attack types or functionality
- **Performance**: Optimize existing code
- **Tests**: Add or improve test coverage

### Documentation
- Fix typos and grammar
- Add examples and tutorials
- Improve clarity and organization
- Translate to other languages

### Community
- Answer questions in discussions
- Report bugs with detailed information
- Suggest new features
- Share the project with others

## Getting Started

### 1. Fork the Repository

Click the "Fork" button on GitHub to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/tworjaga/keyspace.git
cd keyspace
```

### 3. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

## Contribution Guidelines

### Code Style

We follow PEP 8 with some modifications:

```python
# Use 4 spaces for indentation
# Maximum line length: 100 characters
# Use descriptive variable names

# Good
def calculate_attack_speed(attempts, elapsed_time):
    if elapsed_time > 0:
        return attempts / elapsed_time
    return 0.0

# Bad
def calc(a, t):
    return a/t if t>0 else 0
```

### Type Hints

Use type hints for function signatures:

```python
from typing import Optional, List, Dict

def start_attack(
    target: str,
    attack_type: str,
    wordlist_path: Optional[str] = None
) -> Dict[str, str]:
    ...
```

### Documentation

Add docstrings to all functions:

```python
def start_attack(target: str, attack_type: str) -> dict:
    """
    Start a password cracking attack.
    
    Args:
        target: The target to attack (SSID, username, etc.)
        attack_type: Type of attack to perform
    
    Returns:
        Dictionary containing attack_id and status
    
    Raises:
        ValueError: If attack_type is invalid
    """
    ...
```

### Testing

Write tests for new functionality:

```python
# tests/test_new_feature.py
import pytest
from backend.new_feature import new_function

def test_new_function():
    result = new_function("test_input")
    assert result == "expected_output"
```

Run tests before submitting:
```bash
pytest tests/ -v
```

## Specific Contribution Areas

### Adding New Attack Types

1. Create attack module in `backend/attacks/`:

```python
# backend/attacks/my_attack.py
from .base import BaseAttack

class MyAttack(BaseAttack):
    def __init__(self, config):
        super().__init__(config)
        self.name = "My Custom Attack"
    
    def run(self):
        # Implementation
        pass
    
    def stop(self):
        # Cleanup
        pass
```

2. Register in attack factory:

```python
# backend/attack_factory.py
from .attacks.my_attack import MyAttack

ATTACK_TYPES = {
    # ... existing types
    "My Attack": MyAttack,
}
```

3. Add tests:

```python
# tests/attacks/test_my_attack.py
def test_my_attack():
    attack = MyAttack({"target": "test"})
    assert attack.name == "My Custom Attack"
```

4. Update documentation:

```markdown
# USER_GUIDE.md
## My Attack
Description of how to use the new attack type...
```

### Adding GUI Features

1. Create UI component in `frontend/ui/`:

```python
# frontend/ui/my_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class MyPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("My Panel"))
```

2. Integrate into main window:

```python
# frontend/ui/main_window.py
from .my_panel import MyPanel

# In init_ui():
self.my_panel = MyPanel()
self.tab_widget.addTab(self.my_panel, "My Panel")
```

### Documentation Contributions

1. Edit relevant `.md` files
2. Follow Markdown best practices
3. Add code examples where helpful
4. Test all links

## Code Review Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear

### Commit Message Format

```
type: Brief description (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Include motivation for change and contrast with previous behavior.

- Bullet points are okay
- Use present tense: "Add feature" not "Added feature"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat: Add mask attack support

Implement mask attack type similar to Hashcat syntax.
Supports ?l, ?u, ?d, ?s placeholders.

Closes #123
```

```
fix: Correct speed calculation in progress updates

Speed was being calculated incorrectly when attack was paused.
Now properly tracks only active time.

Fixes #456
```

## Reporting Bugs

### Before Reporting

1. Search existing issues
2. Check if it's already fixed in latest version
3. Try to reproduce with minimal steps

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 11]
- Python: [e.g., 3.10.4]
- Version: [e.g., 1.0.0]

**Screenshots**
If applicable

**Additional Context**
Any other relevant information
```

## Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Description of what the problem is

**Describe the solution you'd like**
Clear description of desired feature

**Describe alternatives you've considered**
Other approaches you've thought about

**Additional context**
Any other information
```

## Issue Labels

We use labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `performance`: Performance-related
- `security`: Security-related

## Pull Request Process

1. **Create PR** from your fork to main repository
2. **Fill out PR template** with all required information
3. **Link related issues** using `Fixes #123` or `Closes #456`
4. **Wait for review** - maintainers will review within 1-2 days
5. **Address feedback** - make requested changes
6. **Merge** - once approved, maintainers will merge

### PR Checklist

- [ ] Branch is up to date with main
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts

## Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:
- Email: security@keyspace.example.com
- Or use GitHub Security Advisories

See [SECURITY.md](SECURITY.md) for details.

### Security Best Practices

- Never commit API keys or passwords
- Validate all user inputs
- Use parameterized queries
- Keep dependencies updated
- Follow OWASP guidelines

## Resources

### Learning Resources

- [Python Best Practices](https://docs.python-guide.org/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Git Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows)
- [Markdown Guide](https://www.markdownguide.org/)

### Project Resources

- [API Documentation](API.md)
- [User Guide](USER_GUIDE.md)
- [Architecture Overview](docs/architecture.md)

## First-Time Contributors

### Good First Issues

Look for issues labeled:
- `good first issue`
- `help wanted`
- `documentation`

### Getting Help

- Join our [Discord](https://discord.gg/keyspace)
- Ask in GitHub Discussions
- Email: contributors@keyspace.example.com

## Recognition

Contributors will be:
- Listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Mentioned in release notes
- Credited in the application About dialog

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Questions about contributing?** → [GitHub Discussions](https://github.com/tworjaga/keyspace/discussions)

**Ready to contribute?** → [Fork the Repository](https://github.com/tworjaga/keyspace/fork)

Thank you for helping make Keyspace better!


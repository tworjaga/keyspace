# Keyspace Icon Assets

This folder contains the application icon for Keyspace in multiple formats and sizes.

## Icon Design

- **Style**: Flat, utilitarian, professional security tool aesthetic (Wireshark-like)
- **Background**: Dark blue solid (#003366)
- **Foreground**: Bold white capital "K" centered
- **Design**: Minimal, no gradients, shadows, outlines, or decorations
- **Readability**: Optimized for 16x16 pixels (window title bar)

## Files

| File | Size | Format | Purpose |
|------|------|--------|---------|
| `keyspace.ico` | Multi-size (16,32,48,256) | Windows ICO | Windows application icon |
| `icon_16x16.png` | 16x16 | PNG | Window title bar, taskbar |
| `icon_32x32.png` | 32x32 | PNG | Desktop shortcuts, dialogs |
| `icon_48x48.png` | 48x48 | PNG | Application launcher |
| `icon_256x256.png` | 256x256 | PNG | High-DPI displays, store listings |
| `keyspace_icon.svg` | Vector | SVG | Source file, scalable usage |

## Usage

### In Python/PyQt6:
```python
from PyQt6.QtGui import QIcon
app.setWindowIcon(QIcon("assets/keyspace.ico"))
```

### In Windows (window title bar):
The 16x16 version is automatically used by Windows for the title bar icon.

### In HTML/Web:
```html
<link rel="icon" type="image/svg+xml" href="assets/keyspace_icon.svg">
<link rel="icon" type="image/png" sizes="16x16" href="assets/icon_16x16.png">
```

## Generation

Icons were generated using Python with Pillow library from a single SVG source.

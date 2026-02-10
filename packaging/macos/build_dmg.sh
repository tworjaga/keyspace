#!/bin/bash
# Build macOS DMG installer for Keyspace

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building macOS DMG installer for Keyspace${NC}"

# Check if we're on macOS
if [ "$(uname)" != "Darwin" ]; then
    echo -e "${RED}Error: This script must be run on macOS.${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: main.py not found. Please run this script from the keyspace root directory.${NC}"
    exit 1
fi

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}Error: python3 is required but not installed.${NC}"; exit 1; }
command -v hdiutil >/dev/null 2>&1 || { echo -e "${RED}Error: hdiutil is required but not installed.${NC}"; exit 1; }

# Create build directory
BUILD_DIR="build_dmg"
APP_NAME="Keyspace"
APP_BUNDLE="$APP_NAME.app"
DMG_NAME="keyspace-1.0.0.dmg"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo -e "${YELLOW}Creating app bundle structure...${NC}"
# Create app bundle structure
APP_DIR="$BUILD_DIR/$APP_BUNDLE/Contents"
mkdir -p "$APP_DIR/MacOS"
mkdir -p "$APP_DIR/Resources"
mkdir -p "$APP_DIR/Frameworks"

# Create Info.plist
cat > "$APP_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Keyspace</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.keyspace.app</string>
    <key>CFBundleName</key>
    <string>Keyspace</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
</dict>
</plist>
EOF

# Create executable script
cat > "$APP_DIR/MacOS/Keyspace" << EOF
#!/bin/bash
DIR="\$(dirname "\$0")"
APP_DIR="\$(dirname "\$DIR")"
cd "\$APP_DIR/Resources"
exec python3 main.py "\$@"
EOF
chmod +x "$APP_DIR/MacOS/Keyspace"

echo -e "${YELLOW}Copying application files...${NC}"
# Copy application files
cp -r . "$APP_DIR/Resources/"
cd "$APP_DIR/Resources"

# Clean up unnecessary files
rm -rf packaging/
rm -rf .git/
rm -rf __pycache__/
rm -rf *.pyc
rm -rf .pytest_cache/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create icon (placeholder - you'll need to add actual icon)
# echo "Creating placeholder icon..."
# You would add actual icon creation here

cd "$BUILD_DIR"

echo -e "${YELLOW}Creating DMG installer...${NC}"
# Create DMG
hdiutil create -volname "Keyspace" -srcfolder "$APP_BUNDLE" -ov -format UDZO "$DMG_NAME"

echo -e "${GREEN}macOS DMG installer created successfully!${NC}"
echo -e "${GREEN}DMG file: $DMG_NAME${NC}"

echo -e "${GREEN}Installation instructions:${NC}"
echo "  Double-click the DMG file to mount it"
echo "  Drag Keyspace.app to your Applications folder"
echo "  The app will be available in your Applications folder"

# Clean up
rm -rf "$APP_BUNDLE"

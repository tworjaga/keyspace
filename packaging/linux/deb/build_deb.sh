#!/bin/bash
# Build Debian package for BruteForce Tool

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Debian package for BruteForce Tool${NC}"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: main.py not found. Please run this script from the bruteforce-tool root directory.${NC}"
    exit 1
fi

# Check for required tools
command -v dpkg >/dev/null 2>&1 || { echo -e "${RED}Error: dpkg is required but not installed.${NC}"; exit 1; }
command -v fakeroot >/dev/null 2>&1 || { echo -e "${RED}Error: fakeroot is required but not installed.${NC}"; exit 1; }

# Create build directory
BUILD_DIR="build_deb"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo -e "${YELLOW}Copying source files...${NC}"
# Copy source files
cp -r . "$BUILD_DIR/bruteforce-tool-1.0.0"
cd "$BUILD_DIR/bruteforce-tool-1.0.0"

# Remove unnecessary files
echo -e "${YELLOW}Cleaning up build directory...${NC}"
rm -rf packaging/
rm -rf .git/
rm -rf __pycache__/
rm -rf *.pyc
rm -rf .pytest_cache/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Copy debian packaging files
echo -e "${YELLOW}Setting up Debian packaging...${NC}"
mkdir -p debian
cp -r ../packaging/linux/deb/debian/* debian/

# Make scripts executable
chmod +x debian/rules
chmod +x debian/postinst
chmod +x debian/prerm

# Build the package
echo -e "${YELLOW}Building Debian package...${NC}"
cd ..
fakeroot dpkg-buildpackage -us -uc

echo -e "${GREEN}Debian package built successfully!${NC}"
echo -e "${GREEN}Package files:${NC}"
ls -la *.deb *.dsc *.changes 2>/dev/null || echo "No package files found"

echo -e "${GREEN}Installation instructions:${NC}"
echo "  sudo dpkg -i bruteforce-tool_1.0.0-1_all.deb"
echo "  sudo apt-get install -f  # Install any missing dependencies"

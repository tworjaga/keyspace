#!/bin/bash
# Build RPM package for Keyspace

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building RPM package for Keyspace${NC}"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: main.py not found. Please run this script from the keyspace root directory.${NC}"
    exit 1
fi

# Check for required tools
command -v rpmbuild >/dev/null 2>&1 || { echo -e "${RED}Error: rpmbuild is required but not installed.${NC}"; exit 1; }

# Create build directory structure
BUILD_DIR="build_rpm"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

echo -e "${YELLOW}Creating source tarball...${NC}"
# Create source tarball
tar -czf "$BUILD_DIR/SOURCES/keyspace-1.0.0.tar.gz" \
    --exclude='packaging' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --transform 's,^,keyspace-1.0.0/,' \
    .

# Copy spec file
cp "packaging/linux/rpm/keyspace.spec" "$BUILD_DIR/SPECS/"

echo -e "${YELLOW}Building RPM package...${NC}"
# Build the RPM
cd "$BUILD_DIR"
rpmbuild --define "_topdir $(pwd)" -ba SPECS/keyspace.spec

echo -e "${GREEN}RPM package built successfully!${NC}"
echo -e "${GREEN}Package files:${NC}"
find RPMS -name "*.rpm" -exec ls -la {} \;

echo -e "${GREEN}Installation instructions:${NC}"
echo "  sudo rpm -i RPMS/*/keyspace-1.0.0-1.*.rpm"
echo "  sudo dnf install -y python3-qt6 python3-flask python3-flask-login python3-cryptography python3-pytest python3-matplotlib  # For Fedora/RHEL"

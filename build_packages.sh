#!/bin/bash
# Build packages for all platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  BruteForce Tool - Package Builder${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to detect OS
detect_os() {
    case "$(uname -s)" in
        Linux)
            if command -v apt-get >/dev/null 2>&1; then
                echo "debian"
            elif command -v dnf >/dev/null 2>&1; then
                echo "fedora"
            elif command -v yum >/dev/null 2>&1; then
                echo "centos"
            else
                echo "linux"
            fi
            ;;
        Darwin)
            echo "macos"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

OS=$(detect_os)

echo -e "${YELLOW}Detected OS: $OS${NC}"

# Build packages based on OS
case "$OS" in
    debian)
        echo -e "${GREEN}Building Debian package...${NC}"
        chmod +x packaging/linux/deb/build_deb.sh
        ./packaging/linux/deb/build_deb.sh
        ;;
    fedora|centos)
        echo -e "${GREEN}Building RPM package...${NC}"
        chmod +x packaging/linux/rpm/build_rpm.sh
        ./packaging/linux/rpm/build_rpm.sh
        ;;
    macos)
        echo -e "${GREEN}Building macOS DMG...${NC}"
        chmod +x packaging/macos/build_dmg.sh
        ./packaging/macos/build_dmg.sh
        ;;
    *)
        echo -e "${YELLOW}Unknown OS. Building all available packages...${NC}"

        # Try Debian
        if command -v dpkg >/dev/null 2>&1; then
            echo -e "${GREEN}Building Debian package...${NC}"
            chmod +x packaging/linux/deb/build_deb.sh
            ./packaging/linux/deb/build_deb.sh
        fi

        # Try RPM
        if command -v rpmbuild >/dev/null 2>&1; then
            echo -e "${GREEN}Building RPM package...${NC}"
            chmod +x packaging/linux/rpm/build_rpm.sh
            ./packaging/linux/rpm/build_rpm.sh
        fi

        # Try macOS
        if [ "$(uname)" = "Darwin" ]; then
            echo -e "${GREEN}Building macOS DMG...${NC}"
            chmod +x packaging/macos/build_dmg.sh
            ./packaging/macos/build_dmg.sh
        fi
        ;;
esac

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Package building completed!${NC}"
echo -e "${BLUE}========================================${NC}"

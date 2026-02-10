#!/usr/bin/env python3
"""
Keyspace - GUI Launcher with Auto-Start API
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from frontend.ui.main_window import MainWindow
from backend.integrations.integration_manager import IntegrationManager, IntegrationConfig
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point with auto-start API"""
    print("="*50)
    print("Keyspace GUI with API - Starting...")
    print("="*50)
    
    # Enable high DPI (must be before creating QApplication)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    print("[1/5] High DPI configured")

    # Create app
    app = QApplication(sys.argv)
    app.setApplicationName('Keyspace')
    app.setOrganizationName('Keyspace')
    print("[2/5] QApplication created")

    # Create integration config with API enabled
    config = IntegrationConfig(api_enabled=True, api_port=8080)
    integration_manager = IntegrationManager(config)
    print("[3/5] IntegrationManager created")

    # Create main window
    print("[4/5] Creating MainWindow...")
    window = MainWindow(integration_manager=integration_manager)
    print("[4/5] MainWindow created, showing...")
    window.show()
    print("[4/5] MainWindow shown")

    # Auto-start API server
    print("[5/5] Starting API server...")
    if integration_manager.api_server:
        if integration_manager.api_server.start():
            logger.info('API Server auto-started on http://localhost:8080')
            print('='*50)
            print('API Server started on http://localhost:8080')
            print('='*50)
        else:
            logger.error('Failed to auto-start API Server')
            print('WARNING: Failed to start API Server')
    else:
        print('WARNING: No API server available')

    print("Starting event loop...")
    # Run app
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

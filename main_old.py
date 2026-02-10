#!/usr/bin/env python3
"""
Keyspace - Main Entry Point
Advanced password cracking tool with GUI
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from frontend.ui.main_window import MainWindow
import logging


def setup_logging():
    """Configure logging system"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "bruteforce.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Keyspace - Advanced Password Cracking"
    )

    parser.add_argument(
        '--target',
        type=str,
        help='Target for attack'
    )

    parser.add_argument(
        '--attack-type',
        type=str,
        choices=[
            "Dictionary Attack (WPA2)",
            "Brute Force Attack",
            "Rule-based Attack",
            "Hybrid Attack",
            "Mask Attack",
            "Combinator Attack",
            "Pin Code Attack"
        ],
        help='Type of attack to perform'
    )

    parser.add_argument(
        '--wordlist',
        type=str,
        help='Path to wordlist file'
    )

    parser.add_argument(
        '--min-length',
        type=int,
        default=8,
        help='Minimum password length (default: 8)'
    )

    parser.add_argument(
        '--max-length',
        type=int,
        default=16,
        help='Maximum password length (default: 16)'
    )

    parser.add_argument(
        '--charset',
        type=str,
        default='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*',
        help='Character set for brute force'
    )

    return parser.parse_args()


def run_gui(args, logger):
    """Run tool with GUI"""
    logger.info("Starting Keyspace with GUI")

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Keyspace")
    app.setOrganizationName("Keyspace")

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    window = MainWindow()

    # If arguments provided, pre-fill the configuration
    if args.target:
        window.target_input.setText(args.target)
    if args.attack_type:
        index = window.attack_type_combo.findText(args.attack_type)
        if index >= 0:
            window.attack_type_combo.setCurrentIndex(index)
    if args.wordlist:
        window.wordlist_input.setText(args.wordlist)
    if args.min_length:
        window.min_length_spin.setValue(args.min_length)
    if args.max_length:
        window.max_length_spin.setValue(args.max_length)
    if args.charset:
        window.charset_input.setText(args.charset)

    window.show()

    # Run application
    sys.exit(app.exec())


def main():
    """Main entry point"""
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    logger = setup_logging()

    try:
        # Run GUI
        run_gui(args, logger)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


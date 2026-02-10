#!/usr/bin/env python3
"""
Keyspace - Main Entry Point
Advanced password cracking tool with GUI and integrations
"""


import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from frontend.ui.main_window import MainWindow
from backend.integrations.integration_manager import IntegrationManager, IntegrationConfig
import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Configure logging system"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create rotating file handler (max 10MB per file, keep 5 backup files)
    log_file = log_dir / "bruteforce.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
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
            "Pin Code Attack",
            "Rainbow Table Attack",
            "Markov Chain Attack",
            "Neural Network Attack",
            "Distributed Attack"
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

    # Integration arguments
    parser.add_argument(
        '--enable-hashcat',
        action='store_true',
        help='Enable Hashcat integration'
    )

    parser.add_argument(
        '--hashcat-path',
        type=str,
        help='Path to Hashcat executable'
    )

    parser.add_argument(
        '--enable-john',
        action='store_true',
        help='Enable John the Ripper integration'
    )

    parser.add_argument(
        '--john-path',
        type=str,
        help='Path to John the Ripper executable'
    )

    parser.add_argument(
        '--enable-cloud',
        action='store_true',
        help='Enable cloud storage integration'
    )

    parser.add_argument(
        '--cloud-provider',
        type=str,
        choices=['aws', 'gcp', 'azure'],
        default='aws',
        help='Cloud provider (default: aws)'
    )

    parser.add_argument(
        '--cloud-bucket',
        type=str,
        help='Cloud storage bucket name'
    )

    parser.add_argument(
        '--enable-api',
        action='store_true',
        help='Enable REST API server'
    )

    parser.add_argument(
        '--api-port',
        type=int,
        default=8080,
        help='API server port (default: 8080)'
    )

    return parser.parse_args()


def create_integration_config(args) -> IntegrationConfig:
    """Create integration configuration from arguments"""
    return IntegrationConfig(
        hashcat_enabled=args.enable_hashcat,
        hashcat_path=args.hashcat_path or "",
        john_enabled=args.enable_john,
        john_path=args.john_path or "",
        cloud_enabled=args.enable_cloud,
        cloud_provider=args.cloud_provider,
        cloud_bucket=args.cloud_bucket or "",
        cloud_access_key="",  # Would be set via environment or config file
        cloud_secret_key="",  # Would be set via environment or config file
        api_enabled=args.enable_api,
        api_port=args.api_port
    )


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

    # Create integration configuration
    integration_config = create_integration_config(args)

    # Create integration manager
    integration_manager = IntegrationManager(integration_config)

    # Create and show main window
    window = MainWindow(integration_manager=integration_manager)

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


def print_splash_screen():
    """Print ASCII art splash screen"""
    splash = r"""
    _  __          _                     
   | |/ /___ _   _| | ____ _ _ __ _   _ 
   | ' // _ \ | | | |/ / _` | '__| | | |
   | . \  __/ |_| |   < (_| | |  | |_| |
   |_|\_\___|\__, |_|\_\__,_|_|   \__, |
             |___/                |___/ 
              
         Advanced Password Cracking Tool v1.0
    """
    print(splash)



def main():
    """Main entry point"""
    # Print splash screen
    print_splash_screen()
    
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

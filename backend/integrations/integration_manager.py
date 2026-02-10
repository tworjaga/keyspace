"""
Integration Manager
Coordinates various external tool integrations and cloud services
"""

import os
import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class IntegrationConfig:
    """Configuration for integration features"""
    hashcat_enabled: bool = False
    hashcat_path: str = ""
    john_enabled: bool = False
    john_path: str = ""
    cloud_enabled: bool = False
    cloud_provider: str = "aws"  # aws, gcp, azure
    cloud_bucket: str = ""
    cloud_access_key: str = ""
    cloud_secret_key: str = ""
    api_enabled: bool = False
    api_port: int = 8080
    api_host: str = "localhost"


class IntegrationManager:
    """Manages external tool integrations and cloud services"""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.hashcat_integration = None
        self.john_integration = None
        self.cloud_integration = None
        self.api_server = None

        # Initialize integrations
        self._init_integrations()

    def _init_integrations(self):
        """Initialize all configured integrations"""
        try:
            if self.config.hashcat_enabled:
                from .hashcat_integration import HashcatIntegration
                self.hashcat_integration = HashcatIntegration(self.config.hashcat_path)
                logger.info("Hashcat integration initialized")

            if self.config.john_enabled:
                from .john_integration import JohnIntegration
                self.john_integration = JohnIntegration(self.config.john_path)
                logger.info("John the Ripper integration initialized")

            if self.config.cloud_enabled:
                from .cloud_integration import CloudIntegration
                self.cloud_integration = CloudIntegration(
                    provider=self.config.cloud_provider,
                    bucket=self.config.cloud_bucket,
                    access_key=self.config.cloud_access_key,
                    secret_key=self.config.cloud_secret_key
                )
                logger.info("Cloud integration initialized")

            if self.config.api_enabled:
                from .api_integration import APIIntegration
                self.api_server = APIIntegration(
                    host=self.config.api_host,
                    port=self.config.api_port
                )
                logger.info("API integration initialized")

        except Exception as e:
            logger.error(f"Failed to initialize integrations: {e}")

    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        return {
            "hashcat": {
                "enabled": self.config.hashcat_enabled,
                "available": self.hashcat_integration is not None,
                "path": self.config.hashcat_path
            },
            "john": {
                "enabled": self.config.john_enabled,
                "available": self.john_integration is not None,
                "path": self.config.john_path
            },
            "cloud": {
                "enabled": self.config.cloud_enabled,
                "available": self.cloud_integration is not None,
                "provider": self.config.cloud_provider,
                "bucket": self.config.cloud_bucket
            },
            "api": {
                "enabled": self.config.api_enabled,
                "available": self.api_server is not None,
                "host": self.config.api_host,
                "port": self.config.api_port
            }
        }

    def run_hashcat_attack(self, hash_file: str, wordlist: str, hash_type: str = "0") -> Dict[str, Any]:
        """Run Hashcat attack"""
        if not self.hashcat_integration:
            return {"error": "Hashcat integration not available"}

        try:
            return self.hashcat_integration.run_attack(hash_file, wordlist, hash_type)
        except Exception as e:
            logger.error(f"Hashcat attack failed: {e}")
            return {"error": str(e)}

    def run_john_attack(self, hash_file: str, wordlist: str) -> Dict[str, Any]:
        """Run John the Ripper attack"""
        if not self.john_integration:
            return {"error": "John the Ripper integration not available"}

        try:
            return self.john_integration.run_attack(hash_file, wordlist)
        except Exception as e:
            logger.error(f"John attack failed: {e}")
            return {"error": str(e)}

    def upload_wordlist(self, local_path: str, remote_name: str) -> bool:
        """Upload wordlist to cloud storage"""
        if not self.cloud_integration:
            logger.error("Cloud integration not available")
            return False

        try:
            return self.cloud_integration.upload_file(local_path, remote_name)
        except Exception as e:
            logger.error(f"Cloud upload failed: {e}")
            return False

    def download_wordlist(self, remote_name: str, local_path: str) -> bool:
        """Download wordlist from cloud storage"""
        if not self.cloud_integration:
            logger.error("Cloud integration not available")
            return False

        try:
            return self.cloud_integration.download_file(remote_name, local_path)
        except Exception as e:
            logger.error(f"Cloud download failed: {e}")
            return False

    def list_cloud_wordlists(self) -> List[str]:
        """List available wordlists in cloud storage"""
        if not self.cloud_integration:
            return []

        try:
            return self.cloud_integration.list_files()
        except Exception as e:
            logger.error(f"Cloud list failed: {e}")
            return []

    def start_api_server(self):
        """Start the API server"""
        if not self.api_server:
            logger.error("API integration not available")
            return False

        try:
            self.api_server.start()
            return True
        except Exception as e:
            logger.error(f"API server start failed: {e}")
            return False

    def stop_api_server(self):
        """Stop the API server"""
        if not self.api_server:
            return False

        try:
            self.api_server.stop()
            return True
        except Exception as e:
            logger.error(f"API server stop failed: {e}")
            return False

    def handle_anomaly(self, anomaly_data: Dict[str, Any]):
        """Handle anomaly detection (for future SIEM integration)"""
        # Placeholder for SIEM integration
        logger.info(f"Anomaly detected: {anomaly_data}")

    def export_results(self, results: Dict[str, Any], format_type: str = "json") -> str:
        """Export results in various formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bruteforce_results_{timestamp}.{format_type}"

        try:
            if format_type == "json":
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            elif format_type == "csv":
                # Simple CSV export
                with open(filename, 'w') as f:
                    f.write("timestamp,password,hash,attempts,time\n")
                    for result in results.get("found_passwords", []):
                        f.write(f"{result.get('timestamp', '')},{result.get('password', '')},"
                               f"{result.get('hash', '')},{result.get('attempts', '')},"
                               f"{result.get('time', '')}\n")
            else:
                logger.error(f"Unsupported export format: {format_type}")
                return ""

            logger.info(f"Results exported to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return ""

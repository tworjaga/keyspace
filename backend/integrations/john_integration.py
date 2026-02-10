"""
John the Ripper Integration
Provides integration with John the Ripper password cracking tool
"""

import os
import subprocess
import logging
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class JohnIntegration:
    """Integration with John the Ripper password cracking tool"""

    def __init__(self, john_path: str = ""):
        self.john_path = john_path or self._find_john()
        self.is_available = self._check_availability()
        self.running_processes = {}

        if self.is_available:
            logger.info(f"John the Ripper found at: {self.john_path}")
        else:
            logger.warning("John the Ripper not found. Please install John or set correct path.")

    def _find_john(self) -> str:
        """Try to find John the Ripper in common locations"""
        common_paths = [
            "john.exe",      # Windows
            "john",          # Linux/macOS
            "/usr/bin/john",
            "/usr/local/bin/john",
            "/opt/john/john",
            "C:\\Program Files\\John the Ripper\\run\\john.exe",
            "C:\\john\\run\\john.exe"
        ]

        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path

        # Check PATH
        try:
            result = subprocess.run(["which", "john"],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        return ""

    def _check_availability(self) -> bool:
        """Check if John the Ripper is available and working"""
        if not self.john_path:
            return False

        try:
            result = subprocess.run([self.john_path, "--version"],
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"John availability check failed: {e}")
            return False

    def get_supported_formats(self) -> List[str]:
        """Get supported hash formats"""
        formats = [
            "md5", "sha1", "sha256", "sha512",
            "nt", "lm", "ntlm",
            "mysql", "mysql-sha1",
            "mssql", "mssql05", "mssql12",
            "oracle", "oracle11", "oracle12c",
            "postgres", "mysqlna"
        ]
        return formats

    def run_attack(self, hash_file: str, wordlist: str,
                   format_type: str = "md5", additional_args: List[str] = None) -> Dict[str, Any]:
        """
        Run John the Ripper attack

        Args:
            hash_file: Path to file containing hashes
            wordlist: Path to wordlist file
            format_type: Hash format (md5, sha1, etc.)
            additional_args: Additional John arguments

        Returns:
            Dict with attack results
        """
        if not self.is_available:
            return {"error": "John the Ripper not available"}

        if not os.path.exists(hash_file):
            return {"error": f"Hash file not found: {hash_file}"}

        if not os.path.exists(wordlist):
            return {"error": f"Wordlist not found: {wordlist}"}

        # Prepare command
        cmd = [
            self.john_path,
            "--wordlist=" + wordlist,    # Wordlist mode
            "--format=" + format_type,   # Hash format
            hash_file                     # Hash file
        ]

        # Add additional arguments
        if additional_args:
            cmd.extend(additional_args)

        logger.info(f"Running John command: {' '.join(cmd)}")

        try:
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Store process reference
            process_id = f"john_{int(time.time())}"
            self.running_processes[process_id] = process

            # Monitor process
            results = self._monitor_john_process(process, process_id, hash_file)

            # Cleanup
            if process_id in self.running_processes:
                del self.running_processes[process_id]

            return results

        except Exception as e:
            logger.error(f"John execution failed: {e}")
            return {"error": str(e)}

    def _monitor_john_process(self, process, process_id: str, hash_file: str) -> Dict[str, Any]:
        """Monitor John process and extract results"""
        results = {
            "process_id": process_id,
            "status": "running",
            "cracked_count": 0,
            "total_hashes": 0,
            "progress": 0,
            "cracked_hashes": []
        }

        try:
            while process.poll() is None:
                # Read output
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        results.update(self._parse_john_output(line.strip()))

                time.sleep(0.1)

            # Process finished
            returncode = process.returncode
            results["status"] = "completed" if returncode == 0 else "failed"
            results["return_code"] = returncode

            # Read cracked hashes
            results["cracked_hashes"] = self._read_john_cracked_hashes(hash_file)

        except Exception as e:
            logger.error(f"Process monitoring failed: {e}")
            results["error"] = str(e)

        return results

    def _parse_john_output(self, line: str) -> Dict[str, Any]:
        """Parse John output line"""
        updates = {}

        try:
            # Parse progress information
            if "guesses:" in line and "time:" in line:
                # Extract cracked count and timing
                pass
            elif "Loaded" in line and "hashes" in line:
                # Extract total hash count
                pass

        except Exception as e:
            logger.debug(f"Failed to parse John output: {line} - {e}")

        return updates

    def _read_john_cracked_hashes(self, hash_file: str) -> List[Dict[str, str]]:
        """Read cracked hashes using john --show"""
        hashes = []

        try:
            # Run john --show to get cracked passwords
            cmd = [self.john_path, "--show", hash_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ':' in line and line.count(':') >= 2:
                        parts = line.split(':', 2)
                        if len(parts) >= 2:
                            username = parts[0] if len(parts) > 2 else ""
                            hash_value = parts[-2]
                            password = parts[-1]

                            if password and password != hash_value:
                                hashes.append({
                                    "username": username,
                                    "hash": hash_value,
                                    "password": password
                                })

        except Exception as e:
            logger.error(f"Failed to read John cracked hashes: {e}")

        return hashes

    def stop_attack(self, process_id: str) -> bool:
        """Stop a running John attack"""
        if process_id in self.running_processes:
            try:
                process = self.running_processes[process_id]
                process.terminate()

                # Wait for process to finish
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

                del self.running_processes[process_id]
                logger.info(f"John process {process_id} stopped")
                return True

            except Exception as e:
                logger.error(f"Failed to stop John process: {e}")
                return False

        return False

    def convert_hash_format(self, input_file: str, output_format: str) -> str:
        """Convert hash format for John compatibility"""
        # This is a simplified implementation
        # Real implementation would handle various hash formats

        output_file = f"{input_file}.{output_format}"

        try:
            # For demonstration, just copy the file
            # In real implementation, this would convert hash formats
            with open(input_file, 'r') as src:
                with open(output_file, 'w') as dst:
                    dst.write(src.read())

            return output_file

        except Exception as e:
            logger.error(f"Hash format conversion failed: {e}")
            return ""

    def get_session_info(self, hash_file: str) -> Dict[str, Any]:
        """Get session information for a hash file"""
        if not self.is_available:
            return {"error": "John not available"}

        try:
            cmd = [self.john_path, "--status", hash_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except Exception as e:
            logger.error(f"Session info retrieval failed: {e}")
            return {"error": str(e)}

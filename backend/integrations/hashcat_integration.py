"""
Hashcat Integration
Provides integration with Hashcat password cracking tool
"""

import os
import subprocess
import logging
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class HashcatIntegration:
    """Integration with Hashcat password cracking tool"""

    def __init__(self, hashcat_path: str = ""):
        self.hashcat_path = hashcat_path or self._find_hashcat()
        self.is_available = self._check_availability()
        self.running_processes = {}

        if self.is_available:
            logger.info(f"Hashcat found at: {self.hashcat_path}")
        else:
            logger.warning("Hashcat not found. Please install Hashcat or set correct path.")

    def _find_hashcat(self) -> str:
        """Try to find Hashcat in common locations"""
        common_paths = [
            "hashcat.exe",  # Windows
            "hashcat",      # Linux/macOS
            "/usr/bin/hashcat",
            "/usr/local/bin/hashcat",
            "/opt/hashcat/hashcat",
            "C:\\Program Files\\hashcat\\hashcat.exe",
            "C:\\hashcat\\hashcat.exe"
        ]

        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path

        # Check PATH
        try:
            result = subprocess.run(["which", "hashcat"],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        return ""

    def _check_availability(self) -> bool:
        """Check if Hashcat is available and working"""
        if not self.hashcat_path:
            return False

        try:
            result = subprocess.run([self.hashcat_path, "--version"],
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Hashcat availability check failed: {e}")
            return False

    def get_hash_types(self) -> Dict[str, str]:
        """Get available hash types from Hashcat"""
        hash_types = {
            "0": "MD5",
            "100": "SHA1",
            "1400": "SHA256",
            "1700": "SHA512",
            "2100": "DCC2",
            "2500": "WPA2",
            "5500": "NetNTLMv1",
            "5600": "NetNTLMv2",
            "7500": "Kerberos 5 TGS-REP etype 23",
            "10000": "NTLM",
            "21000": "DCC2 (Half LM Chiffre)"
        }
        return hash_types

    def run_attack(self, hash_file: str, wordlist: str, hash_type: str = "0",
                   attack_mode: str = "0", additional_args: List[str] = None) -> Dict[str, Any]:
        """
        Run Hashcat attack

        Args:
            hash_file: Path to file containing hashes
            wordlist: Path to wordlist file
            hash_type: Hash type number (see get_hash_types())
            attack_mode: Attack mode (0=dictionary, 1=combination, 3=brute-force, etc.)
            additional_args: Additional Hashcat arguments

        Returns:
            Dict with attack results
        """
        if not self.is_available:
            return {"error": "Hashcat not available"}

        if not os.path.exists(hash_file):
            return {"error": f"Hash file not found: {hash_file}"}

        if not os.path.exists(wordlist):
            return {"error": f"Wordlist not found: {wordlist}"}

        # Prepare command
        cmd = [
            self.hashcat_path,
            "-m", hash_type,           # Hash type
            "-a", attack_mode,         # Attack mode
            "-o", f"{hash_file}.cracked",  # Output file
            hash_file,                 # Hash file
            wordlist                   # Wordlist
        ]

        # Add additional arguments
        if additional_args:
            cmd.extend(additional_args)

        # Add common optimization flags
        cmd.extend([
            "--force",                 # Ignore warnings
            "--status",                # Show status
            "--status-timer", "1",     # Status update every second
            "--machine-readable"       # Machine readable output
        ])

        logger.info(f"Running Hashcat command: {' '.join(cmd)}")

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
            process_id = f"hashcat_{int(time.time())}"
            self.running_processes[process_id] = process

            # Monitor process
            results = self._monitor_hashcat_process(process, process_id)

            # Cleanup
            if process_id in self.running_processes:
                del self.running_processes[process_id]

            return results

        except Exception as e:
            logger.error(f"Hashcat execution failed: {e}")
            return {"error": str(e)}

    def _monitor_hashcat_process(self, process, process_id: str) -> Dict[str, Any]:
        """Monitor Hashcat process and extract results"""
        results = {
            "process_id": process_id,
            "status": "running",
            "progress": 0,
            "speed": 0,
            "recovered": 0,
            "total": 0,
            "time_remaining": 0,
            "cracked_hashes": []
        }

        try:
            while process.poll() is None:
                # Read output
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        results.update(self._parse_hashcat_output(line.strip()))

                time.sleep(0.1)

            # Process finished
            returncode = process.returncode
            results["status"] = "completed" if returncode == 0 else "failed"
            results["return_code"] = returncode

            # Read cracked hashes if available
            cracked_file = f"{process_id}.cracked"
            if os.path.exists(cracked_file):
                results["cracked_hashes"] = self._read_cracked_hashes(cracked_file)

        except Exception as e:
            logger.error(f"Process monitoring failed: {e}")
            results["error"] = str(e)

        return results

    def _parse_hashcat_output(self, line: str) -> Dict[str, Any]:
        """Parse Hashcat output line"""
        updates = {}

        try:
            # Parse status line format: STATUS  PROGRESS  SPEED  etc.
            if line.startswith("STATUS"):
                parts = line.split()
                if len(parts) >= 8:
                    updates["progress"] = float(parts[2])
                    updates["speed"] = float(parts[4])
                    updates["recovered"] = int(parts[6])
                    updates["total"] = int(parts[8])

            # Parse time remaining
            elif "TIME" in line and "LEFT" in line:
                # Extract time remaining if available
                pass

        except Exception as e:
            logger.debug(f"Failed to parse Hashcat output: {line} - {e}")

        return updates

    def _read_cracked_hashes(self, cracked_file: str) -> List[Dict[str, str]]:
        """Read cracked hashes from output file"""
        hashes = []

        try:
            with open(cracked_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        hash_value, password = line.split(':', 1)
                        hashes.append({
                            "hash": hash_value,
                            "password": password
                        })

        except Exception as e:
            logger.error(f"Failed to read cracked hashes: {e}")

        return hashes

    def stop_attack(self, process_id: str) -> bool:
        """Stop a running Hashcat attack"""
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
                logger.info(f"Hashcat process {process_id} stopped")
                return True

            except Exception as e:
                logger.error(f"Failed to stop Hashcat process: {e}")
                return False

        return False

    def get_benchmark(self, hash_type: str = "0") -> Dict[str, Any]:
        """Run Hashcat benchmark for specific hash type"""
        if not self.is_available:
            return {"error": "Hashcat not available"}

        try:
            cmd = [self.hashcat_path, "-b", "-m", hash_type]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return {"error": str(e)}

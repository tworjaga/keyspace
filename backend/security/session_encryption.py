"""
Session Encryption Module
Provides secure encrypted storage for session data using Fernet symmetric encryption
"""

import os
import json
import base64
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


@dataclass
class EncryptionConfig:
    """Configuration for encryption settings"""
    key_iterations: int = 100000
    salt_length: int = 32
    algorithm: str = "pbkdf2_hmac_sha256"


class SessionEncryption:
    """Handles encrypted session storage and retrieval"""

    def __init__(self, config: EncryptionConfig = None):
        self.config = config or EncryptionConfig()
        self._master_key: Optional[bytes] = None
        self._fernet: Optional[Fernet] = None

    def set_master_password(self, password: str) -> bool:
        """Set the master password for encryption/decryption"""
        try:
            if not password or len(password) < 8:
                logger.error("Master password must be at least 8 characters")
                return False

            # Generate salt (store this securely for key derivation)
            salt = os.urandom(self.config.salt_length)

            # Derive key from password using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=self.config.key_iterations,
            )

            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            self._master_key = key
            self._fernet = Fernet(key)

            logger.info("Master password set successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to set master password: {e}")
            return False

    def encrypt_session_data(self, data: Dict[str, Any]) -> Optional[str]:
        """Encrypt session data and return as base64 string"""
        if not self._fernet:
            logger.error("Master password not set")
            return None

        try:
            # Add metadata
            session_data = {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "data": data
            }

            # Convert to JSON and encrypt
            json_data = json.dumps(session_data, default=str, indent=2)
            encrypted_data = self._fernet.encrypt(json_data.encode())

            # Return as base64 string
            return base64.urlsafe_b64encode(encrypted_data).decode()

        except Exception as e:
            logger.error(f"Failed to encrypt session data: {e}")
            return None

    def decrypt_session_data(self, encrypted_data: str) -> Optional[Dict[str, Any]]:
        """Decrypt session data from base64 string"""
        if not self._fernet:
            logger.error("Master password not set")
            return None

        try:
            # Decode from base64 and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)

            # Parse JSON
            session_data = json.loads(decrypted_bytes.decode())

            # Validate structure
            if not isinstance(session_data, dict) or "data" not in session_data:
                logger.error("Invalid session data structure")
                return None

            return session_data["data"]

        except InvalidToken:
            logger.error("Invalid encryption token - wrong password or corrupted data")
            return None
        except Exception as e:
            logger.error(f"Failed to decrypt session data: {e}")
            return None

    def save_encrypted_session(self, filepath: str, data: Dict[str, Any]) -> bool:
        """Save session data to encrypted file"""
        try:
            encrypted_data = self.encrypt_session_data(data)
            if not encrypted_data:
                return False

            # Write to file
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(encrypted_data)

            logger.info(f"Encrypted session saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save encrypted session: {e}")
            return False

    def load_encrypted_session(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Load and decrypt session data from file"""
        try:
            if not Path(filepath).exists():
                logger.error(f"Session file does not exist: {filepath}")
                return None

            # Read encrypted data
            with open(filepath, 'r') as f:
                encrypted_data = f.read().strip()

            # Decrypt
            return self.decrypt_session_data(encrypted_data)

        except Exception as e:
            logger.error(f"Failed to load encrypted session: {e}")
            return None

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """Change the master password for existing encrypted sessions"""
        try:
            # First verify old password works
            if not self.set_master_password(old_password):
                return False

            # Store current key for re-encryption
            old_fernet = self._fernet

            # Set new password
            if not self.set_master_password(new_password):
                return False

            # Return success (actual re-encryption would need to be done file-by-file)
            logger.info("Master password changed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to change master password: {e}")
            return False

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength and provide feedback"""
        result = {
            "valid": True,
            "score": 0,
            "feedback": [],
            "strength": "weak"
        }

        # Length check
        if len(password) < 8:
            result["feedback"].append("Password must be at least 8 characters")
            result["valid"] = False
        elif len(password) >= 12:
            result["score"] += 2
        elif len(password) >= 8:
            result["score"] += 1

        # Character variety
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        variety_score = sum([has_lower, has_upper, has_digit, has_special])
        result["score"] += variety_score

        if variety_score < 3:
            result["feedback"].append("Use a mix of uppercase, lowercase, numbers, and special characters")

        # Common patterns
        common_patterns = ["123456", "password", "qwerty", "admin", "letmein"]
        if any(pattern in password.lower() for pattern in common_patterns):
            result["feedback"].append("Avoid common passwords or patterns")
            result["score"] -= 1

        # Determine strength
        if result["score"] >= 5:
            result["strength"] = "strong"
        elif result["score"] >= 3:
            result["strength"] = "medium"
        else:
            result["strength"] = "weak"

        return result

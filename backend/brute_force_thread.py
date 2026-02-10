"""
Enhanced Brute Force Thread Module

This module provides advanced multi-threaded password cracking capabilities
with memory-efficient processing, parallel execution, and comprehensive attack types.

Features:
- Memory-efficient wordlist processing
- Parallel thread pool execution
- Multiple attack types (dictionary, brute force, rule-based, etc.)
- Real-time progress tracking and statistics
- Pause/resume functionality
- Comprehensive error handling and logging

Classes:
    BruteForceThread: Main thread class for executing password attacks
"""

from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
import time
import random
import string
import hashlib
import os
import re
from datetime import datetime, timedelta
from collections import deque
import threading
from typing import Optional, Dict, Any, List, Tuple, Union

# Import memory-efficient reader and thread pool manager
from .memory_efficient_reader import MemoryEfficientWordlistReader, StreamingPasswordProcessor
from .thread_pool_manager import ThreadPoolManager, BatchProcessor

class BruteForceThread(QThread):
    """Enhanced thread for performing advanced brute force attacks without blocking the UI"""

    # Define signals for communication with the main thread
    progress_updated = pyqtSignal(int, str, str, int)  # progress, speed, eta, attempts
    status_updated = pyqtSignal(str)
    result_updated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    attack_log = pyqtSignal(str)

    def __init__(self, target: str, attack_type: str, wordlist_path: str = "", min_length: int = 8, max_length: int = 16,
                 charset: Optional[str] = None, custom_rules: Optional[List[str]] = None) -> None:
        super().__init__()

        # Core attack parameters
        self.target = target
        self.attack_type = attack_type
        self.wordlist_path = wordlist_path

        # Brute force parameters
        self.min_length = min_length
        self.max_length = max_length
        self.charset = charset or string.ascii_letters + string.digits + "!@#$%^&*"

        # Advanced configuration
        self.custom_rules = custom_rules or []
        self.stop_flag = False
        self.pause_flag = False
        self.resume_flag = False

        # Performance tracking
        self.start_time = None
        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0

        # Speed calculation (moving average for stability)
        self.attempt_history = deque(maxlen=100)
        self.last_speed_update = time.time()
        self.current_speed = 0

        # Resume capability
        self.checkpoint_interval = 1000
        self.last_checkpoint = 0
        self.resume_data = {}

        # Memory optimization
        self.batch_size = 1000
        self.password_buffer = []

        # Thread synchronization
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()

        # Thread pool for parallel processing
        self.thread_pool = None
        self.batch_processor = None

        # Statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_passwords_tested': 0,
            'passwords_per_second': 0,
            'peak_speed': 0,
            'average_speed': 0,
            'errors': 0,
            'status': 'initialized'
        }

    def run(self) -> None:
        """Main execution method for the enhanced brute force attack.

        This method orchestrates the entire attack process by:
        1. Initializing attack parameters and logging
        2. Routing to the appropriate attack method based on attack_type
        3. Handling exceptions and finalizing the attack

        The method supports multiple attack types including dictionary, brute force,
        rule-based, hybrid, mask, combinator, PIN, rainbow table, Markov chain,
        neural network, and distributed attacks.
        """
        self.start_time = datetime.now()
        self.stats['start_time'] = self.start_time
        self.stats['status'] = 'running'
        self.stop_flag = False
        self.pause_flag = False

        try:
            # Initialize thread pool for parallel processing
            self.thread_pool = ThreadPoolManager(max_workers=None)  # Auto-detect optimal workers
            self.thread_pool.start()
            self.batch_processor = BatchProcessor(self.thread_pool, batch_size=self.batch_size)

            pool_stats = self.thread_pool.get_stats()
            self.attack_log.emit(f"[THREAD_POOL] Initialized with {pool_stats['pool_stats']['max_workers']} workers")

            self.status_updated.emit(f"🎯 Initializing {self.attack_type} on target: {self.target}")
            self.attack_log.emit(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Attack started")
            self.attack_log.emit(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Target: {self.target}")
            self.attack_log.emit(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Attack Type: {self.attack_type}")

            # Route to appropriate attack method
            attack_methods = {
                "Dictionary Attack (WPA2)": self.dictionary_attack,
                "Brute Force Attack": self.brute_force_attack,
                "Rule-based Attack": self.rule_based_attack,
                "Hybrid Attack": self.hybrid_attack,
                "Mask Attack": self.mask_attack,
                "Combinator Attack": self.combinator_attack,
                "Pin Code Attack": self.pin_code_attack,
                "Rainbow Table Attack": self.rainbow_table_attack,
                "Markov Chain Attack": self.markov_chain_attack,
                "Neural Network Attack": self.neural_network_attack,
                "Distributed Attack": self.distributed_attack
            }

            if self.attack_type in attack_methods:
                attack_methods[self.attack_type]()
            else:
                self.error_occurred.emit(f"Unknown attack type: {self.attack_type}")
                self.status_updated.emit(f"❌ Unknown attack type: {self.attack_type}")

        except MemoryError as e:
            self.handle_error(f"Memory error: {str(e)}")
        except Exception as e:
            self.handle_error(f"Unexpected error: {str(e)}")
        finally:
            self.finalize_attack()

    def dictionary_attack(self):
        """Perform memory-efficient dictionary attack with streaming processing"""
        self.status_updated.emit("📁 Loading memory-efficient dictionary attack...")
        self.attack_log.emit("[INFO] Starting memory-efficient dictionary attack")

        if not self.wordlist_path or not os.path.exists(self.wordlist_path):
            self.error_occurred.emit("Wordlist file not found or not specified")
            self.status_updated.emit("❌ Wordlist file not found")
            return

        try:
            # Initialize memory-efficient reader
            reader = MemoryEfficientWordlistReader(self.wordlist_path)
            file_info = reader.get_file_info()

            self.attack_log.emit(f"[INFO] Wordlist: {file_info['file_path']}")
            self.attack_log.emit(f"[INFO] File size: {file_info['file_size_formatted']}")

            # Validate file
            validation = reader.validate_file()
            if not validation['valid']:
                self.error_occurred.emit(f"Invalid wordlist file: {validation['error']}")
                return

            self.attack_log.emit(f"[INFO] Estimated lines: {validation['line_count']:,}")

            # Initialize streaming processor
            processor = StreamingPasswordProcessor(reader, batch_size=self.batch_size)

            # Process passwords in streaming batches
            total_processed = 0
            batch_count = 0

            def process_password_batch(passwords, batch_start_line, batch_end_line):
                """Process a batch of passwords from the wordlist"""
                nonlocal total_processed, batch_count

                if self.stop_flag:
                    return

                self.handle_pause()

                batch_count += 1
                batch_processed = 0

                for password in passwords:
                    if self.stop_flag:
                        break

                    # Perform password attempt
                    attempt_result = self.attempt_password(password)

                    if attempt_result['success']:
                        self.handle_success(password, attempt_result, total_processed + batch_processed + 1)
                        return  # Stop processing

                    batch_processed += 1
                    self.total_attempts += 1

                total_processed += len(passwords)

                # Update progress
                progress_info = processor.get_progress_info(total_processed)
                progress = min(int(progress_info['progress_percent']), 99)

                self.update_progress(progress, total_processed, validation['line_count'])

                # Save checkpoint periodically
                if batch_count % 10 == 0:  # Every 10 batches
                    self.save_checkpoint('dictionary', total_processed)

                # Log progress periodically
                if batch_count % 50 == 0:  # Every 50 batches
                    self.attack_log.emit(f"[PROGRESS] Processed {total_processed:,} passwords")

            # Stream and process the file
            for result in processor.process_stream(process_password_batch):
                if self.stop_flag:
                    break

            # Final update
            if not self.stop_flag:
                self.update_progress(100, total_processed, validation['line_count'])
                self.result_updated.emit("❌ Dictionary attack completed - password not found")
                self.status_updated.emit("🔚 Dictionary attack finished")
                self.attack_log.emit(f"[COMPLETED] Processed {total_processed:,} passwords")

        except MemoryError as e:
            self.handle_error(f"Memory error during dictionary attack: {str(e)}")
            self.attack_log.emit("[ERROR] Memory error - try using a smaller wordlist or more memory")
        except Exception as e:
            self.handle_error(f"Dictionary attack error: {str(e)}")

    def brute_force_attack(self):
        """Perform pure brute force attack with intelligent character set optimization"""
        self.status_updated.emit("🔐 Starting optimized brute force attack...")
        self.attack_log.emit("[INFO] Starting brute force attack")

        # Calculate total combinations
        charset_size = len(self.charset)
        total_combinations = 0

        for length in range(self.min_length, self.max_length + 1):
            total_combinations += charset_size ** length

        self.attack_log.emit(f"[INFO] Character set: {len(self.charset)} characters")
        self.attack_log.emit(f"[INFO] Password length: {self.min_length}-{self.max_length}")
        self.attack_log.emit(f"[INFO] Total combinations: {total_combinations:,}")

        if total_combinations > 10000000000:  # 10 billion limit for safety
            self.error_occurred.emit("Attack scope too large - reducing to safe limit")
            self.max_length = min(self.max_length, 8)
            total_combinations = sum(len(self.charset) ** l for l in range(self.min_length, self.max_length + 1))

        # Generate passwords using iterative approach
        current_password = [self.charset[0]] * self.min_length
        current_length = self.min_length

        attempt_count = 0
        start_time = time.time()

        while current_length <= self.max_length and not self.stop_flag:
            self.handle_pause()

            # Process batch of passwords
            for _ in range(min(self.batch_size, 10000)):
                if self.stop_flag:
                    break

                password = ''.join(current_password)
                attempt_count += 1
                self.total_attempts += 1

                attempt_result = self.attempt_password(password)

                if attempt_result['success']:
                    self.handle_success(password, attempt_result, attempt_count)
                    return

                # Increment password
                if not self.increment_password(current_password, current_length):
                    break

            # Update progress
            progress = min(int((attempt_count / total_combinations) * 100), 99)
            self.update_progress(progress, attempt_count, total_combinations)

            # Move to next length if current length exhausted
            if not self.increment_password(current_password, current_length):
                current_length += 1
                if current_length <= self.max_length:
                    current_password = [self.charset[0]] * current_length

        self.result_updated.emit("❌ Brute force attack completed - password not found")
        self.status_updated.emit("🔚 Brute force attack finished")

    def rule_based_attack(self):
        """Perform advanced rule-based attack with optimized batch processing"""
        self.status_updated.emit("🔧 Starting rule-based attack with advanced mutations...")
        self.attack_log.emit("[INFO] Starting rule-based attack")

        if not self.wordlist_path or not os.path.exists(self.wordlist_path):
            self.error_occurred.emit("Wordlist required for rule-based attack")
            return

        try:
            # Load base passwords
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as wordlist:
                base_passwords = [line.strip() for line in wordlist if line.strip()]

            self.attack_log.emit(f"[INFO] Loaded {len(base_passwords)} base passwords")

            # Define advanced mutation rules
            mutation_rules = [
                self.mutation_original,
                self.mutation_uppercase,
                self.mutation_lowercase,
                self.mutation_capitalize,
                self.mutation_leet_speak,
                self.mutation_append_numbers,
                self.mutation_prepend_numbers,
                self.mutation_append_special,
                self.mutation_prepend_special,
                self.mutation_reverse,
                self.mutation_double,
                self.mutation_insert_special,
                self.mutation_date_format,
                self.mutation_keyboard_walk,
                self.mutation_repeat_chars
            ]

            all_variations = []
            total_generated = 0

            for base_password in base_passwords:
                if self.stop_flag:
                    break

                self.handle_pause()

                for rule in mutation_rules:
                    if self.stop_flag:
                        break

                    variations = rule(base_password)
                    all_variations.extend(variations)
                    total_generated += len(variations)

                    # Process in batches for memory efficiency
                    if len(all_variations) >= self.batch_size:
                        self.process_batch_parallel(all_variations, total_generated)
                        all_variations = []

            # Process remaining
            if all_variations:
                self.process_batch_parallel(all_variations, total_generated)

            self.result_updated.emit("❌ Rule-based attack completed - password not found")
            self.status_updated.emit("🔚 Rule-based attack finished")

        except Exception as e:
            self.handle_error(f"Rule-based attack error: {str(e)}")

    def process_batch_parallel(self, variations: List[str], total_generated: int) -> None:
        """Process a batch of password variations using thread pool"""
        for password in variations[:self.batch_size]:
            if self.stop_flag:
                break

            self.handle_pause()

            attempt_result = self.attempt_password(password)
            if attempt_result['success']:
                self.handle_success(password, attempt_result, total_generated)
                return

            self.total_attempts += 1

        # Update progress
        progress = min(int((total_generated / 1000000) * 100), 99)
        self.update_progress(progress, self.total_attempts, 1000000)

    def hybrid_attack(self):
        """Perform hybrid attack combining dictionary with brute force append/prepend"""
        self.status_updated.emit("🔀 Starting hybrid attack (dictionary + brute force)...")
        self.attack_log.emit("[INFO] Starting hybrid attack")

        if not self.wordlist_path or not os.path.exists(self.wordlist_path):
            self.error_occurred.emit("Wordlist required for hybrid attack")
            return

        try:
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as wordlist:
                base_passwords = [line.strip() for line in wordlist if line.strip()]

            # Common additions to try
            common_additions = [
                "123", "1234", "12345", "123456", "1", "12", "123456789",
                "!", "@", "#", "$", "%", "^", "&", "*",
                "2020", "2021", "2022", "2023", "2024",
                "01", "02", "03", "69", "00", "77", "88", "99"
            ]

            total_attempts_estimate = len(base_passwords) * (len(common_additions) * 2 + 1)
            self.attack_log.emit(f"[INFO] Estimated attempts: {total_attempts_estimate:,}")

            attempt_count = 0

            for base_password in base_passwords:
                if self.stop_flag:
                    break

                self.handle_pause()

                # Test original
                attempt_result = self.attempt_password(base_password)
                if attempt_result['success']:
                    self.handle_success(base_password, attempt_result, attempt_count)
                    return

                attempt_count += 1
                self.total_attempts += 1

                # Test with common additions
                for addition in common_additions:
                    if self.stop_flag:
                        break

                    # Append
                    test_password = base_password + addition
                    attempt_result = self.attempt_password(test_password)
                    if attempt_result['success']:
                        self.handle_success(test_password, attempt_result, attempt_count)
                        return

                    attempt_count += 1
                    self.total_attempts += 1

                    # Prepend
                    test_password = addition + base_password
                    attempt_result = self.attempt_password(test_password)
                    if attempt_result['success']:
                        self.handle_success(test_password, attempt_result, attempt_count)
                        return

                    attempt_count += 1
                    self.total_attempts += 1

                # Update progress
                progress = min(int((attempt_count / total_attempts_estimate) * 100), 99)
                self.update_progress(progress, attempt_count, total_attempts_estimate)

            self.result_updated.emit("❌ Hybrid attack completed - password not found")
            self.status_updated.emit("🔚 Hybrid attack finished")

        except Exception as e:
            self.handle_error(f"Hybrid attack error: {str(e)}")

    def mask_attack(self):
        """Perform mask-based attack with intelligent mask generation"""
        self.status_updated.emit("🎭 Starting mask-based attack...")
        self.attack_log.emit("[INFO] Starting mask-based attack")

        # Common password masks based on security research
        common_masks = [
            "?u?l?l?l?l?l?l?l",  # 8 lowercase
            "?u?l?l?l?l?l?l?l?l?l",  # 10 mixed case
            "?d?d?d?d?d?d?d?d",  # 8 digits
            "?u?l?l?l?l?d?d?d",  # Mixed with 3 digits
            "?u?l?l?l?l?l?d?d",  # Mixed with 2 digits
            "?a?a?a?a?a?a?a?a",  # 8 any character
            "?l?l?l?l?d?d?d?d",  # 4 letters + 4 digits
            "?u?l?l?l?l?l?l?l?d?d?d",  # 8 mixed + 3 digits
        ]

        self.attack_log.emit(f"[INFO] Using {len(common_masks)} common masks")

        total_masks = len(common_masks)
        current_mask = 0

        for mask in common_masks:
            if self.stop_flag:
                break

            current_mask += 1
            self.status_updated.emit(f"Testing mask {current_mask}/{total_masks}: {mask}")
            self.attack_log.emit(f"[INFO] Testing mask: {mask}")

            # Generate passwords for this mask (simplified for demo)
            mask_attempts = self.generate_mask_passwords(mask, limit=100000)

            for i, password in enumerate(mask_attempts):
                if self.stop_flag:
                    break

                self.handle_pause()

                attempt_result = self.attempt_password(password)
                if attempt_result['success']:
                    self.handle_success(password, attempt_result, i + 1)
                    return

                self.total_attempts += 1

                # Update progress
                progress = int((current_mask / total_masks) * 100)
                self.update_progress(progress, self.total_attempts, total_masks * 100000)

        self.result_updated.emit("❌ Mask attack completed - password not found")
        self.status_updated.emit("🔚 Mask attack finished")

    def combinator_attack(self):
        """Perform combinator attack combining two wordlists"""
        self.status_updated.emit("🔗 Starting combinator attack...")
        self.attack_log.emit("[INFO] Starting combinator attack")

        if not self.wordlist_path or not os.path.exists(self.wordlist_path):
            self.error_occurred.emit("Primary wordlist required for combinator attack")
            return

        # Use same wordlist for both sides (can be modified)
        try:
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as wordlist:
                words = [line.strip() for line in wordlist if line.strip() and len(line.strip()) <= 10]

            # Limit for performance
            words = words[:5000]

            self.attack_log.emit(f"[INFO] Loaded {len(words)} words for combination")
            self.attack_log.emit(f"[INFO] Estimated combinations: {len(words) ** 2:,}")

            total_combinations = len(words) ** 2
            attempt_count = 0

            for word1 in words:
                if self.stop_flag:
                    break

                self.handle_pause()

                for word2 in words:
                    if self.stop_flag:
                        break

                    attempt_count += 1
                    combined = word1 + word2

                    attempt_result = self.attempt_password(combined)
                    if attempt_result['success']:
                        self.handle_success(combined, attempt_result, attempt_count)
                        return

                    self.total_attempts += 1

                    # Progress update
                    if attempt_count % 10000 == 0:
                        progress = min(int((attempt_count / total_combinations) * 100), 99)
                        self.update_progress(progress, attempt_count, total_combinations)

            self.result_updated.emit("❌ Combinator attack completed - password not found")
            self.status_updated.emit("🔚 Combinator attack finished")

        except Exception as e:
            self.handle_error(f"Combinator attack error: {str(e)}")

    def pin_code_attack(self):
        """Perform PIN code attack for mobile devices"""
        self.status_updated.emit("🔢 Starting PIN code attack...")
        self.attack_log.emit("[INFO] Starting PIN attack")

        pin_lengths = [4, 5, 6, 8]  # Common PIN lengths
        total_pins = sum(10 ** length for length in pin_lengths)

        self.attack_log.emit(f"[INFO] Total PIN combinations: {total_pins:,}")

        attempt_count = 0

        for length in pin_lengths:
            if self.stop_flag:
                break

            self.status_updated.emit(f"Testing {length}-digit PINs...")

            # Generate all PINs of current length
            for pin in range(10 ** length):
                if self.stop_flag:
                    break

                self.handle_pause()

                attempt_count += 1
                pin_str = str(pin).zfill(length)

                attempt_result = self.attempt_password(pin_str)
                if attempt_result['success']:
                    self.handle_success(pin_str, attempt_result, attempt_count)
                    return

                self.total_attempts += 1

                # Progress update
                progress = min(int((attempt_count / total_pins) * 100), 99)
                self.update_progress(progress, attempt_count, total_pins)

        self.result_updated.emit("❌ PIN attack completed - PIN not found")
        self.status_updated.emit("🔚 PIN attack finished")

    def rainbow_table_attack(self):
        """Perform rainbow table attack using precomputed hash chains"""
        self.status_updated.emit("🌈 Starting rainbow table attack...")
        self.attack_log.emit("[INFO] Starting rainbow table attack")

        # Simulate rainbow table lookup (in real implementation, this would use actual rainbow tables)
        self.attack_log.emit("[INFO] Loading rainbow table chains...")

        # Common hash prefixes to try (simplified simulation)
        hash_prefixes = [
            '5d41402abc4b2a76b9719d911017c592',  # hello
            '098f6bcd4621d373cade4e832627b4f6',  # test
            'd41d8cd98f00b204e9800998ecf8427e',  # empty
            'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',  # admin
        ]

        self.attack_log.emit(f"[INFO] Testing {len(hash_prefixes)} rainbow chains")

        attempt_count = 0

        for hash_prefix in hash_prefixes:
            if self.stop_flag:
                break

            self.handle_pause()

            attempt_count += 1

            # Simulate rainbow table lookup
            password = self.simulate_rainbow_lookup(hash_prefix)
            if password:
                attempt_result = self.attempt_password(password)
                if attempt_result['success']:
                    self.handle_success(password, attempt_result, attempt_count)
                    return

            self.total_attempts += 1

            # Progress update
            progress = min(int((attempt_count / len(hash_prefixes)) * 100), 99)
            self.update_progress(progress, attempt_count, len(hash_prefixes))

        self.result_updated.emit("❌ Rainbow table attack completed - password not found")
        self.status_updated.emit("🔚 Rainbow table attack finished")

    def markov_chain_attack(self):
        """Perform Markov chain-based password generation"""
        self.status_updated.emit("🔗 Starting Markov chain attack...")
        self.attack_log.emit("[INFO] Starting Markov chain attack")

        # Train Markov model on common passwords (simplified)
        training_data = [
            "password", "123456", "qwerty", "admin", "letmein",
            "welcome", "monkey", "dragon", "passw0rd", "abc123"
        ]

        # Build transition matrix
        transitions = {}
        for password in training_data:
            for i in range(len(password) - 1):
                current = password[i]
                next_char = password[i + 1]

                if current not in transitions:
                    transitions[current] = {}

                if next_char not in transitions[current]:
                    transitions[current][next_char] = 0

                transitions[current][next_char] += 1

        self.attack_log.emit(f"[INFO] Trained Markov model on {len(training_data)} passwords")

        # Generate passwords using Markov chain
        generated_passwords = set()
        max_attempts = 10000

        for attempt_count in range(max_attempts):
            if self.stop_flag:
                break

            self.handle_pause()

            # Generate password using Markov chain
            password = self.generate_markov_password(transitions, min_length=self.min_length, max_length=self.max_length)

            if password not in generated_passwords:
                generated_passwords.add(password)

                attempt_result = self.attempt_password(password)
                if attempt_result['success']:
                    self.handle_success(password, attempt_result, attempt_count + 1)
                    return

                self.total_attempts += 1

            # Progress update
            progress = min(int((attempt_count / max_attempts) * 100), 99)
            self.update_progress(progress, attempt_count + 1, max_attempts)

        self.result_updated.emit("❌ Markov chain attack completed - password not found")
        self.status_updated.emit("🔚 Markov chain attack finished")

    def neural_network_attack(self):
        """Perform neural network-based password prediction"""
        self.status_updated.emit("🧠 Starting neural network attack...")
        self.attack_log.emit("[INFO] Starting neural network attack")

        # Simulate neural network password prediction (simplified)
        # In a real implementation, this would use a trained neural network model

        self.attack_log.emit("[INFO] Loading neural network model...")

        # Simulated neural network predictions (common patterns)
        nn_predictions = [
            "password123", "qwerty123", "admin123", "welcome123",
            "letmein123", "monkey123", "dragon123", "abc123456",
            "123456789", "iloveyou", "princess", "rockyou",
            "1234567", "12345678", "password1", "123123"
        ]

        self.attack_log.emit(f"[INFO] Neural network predicted {len(nn_predictions)} passwords")

        attempt_count = 0

        for password in nn_predictions:
            if self.stop_flag:
                break

            self.handle_pause()

            attempt_count += 1

            attempt_result = self.attempt_password(password)
            if attempt_result['success']:
                self.handle_success(password, attempt_result, attempt_count)
                return

            self.total_attempts += 1

            # Progress update
            progress = min(int((attempt_count / len(nn_predictions)) * 100), 99)
            self.update_progress(progress, attempt_count, len(nn_predictions))

        self.result_updated.emit("❌ Neural network attack completed - password not found")
        self.status_updated.emit("🔚 Neural network attack finished")

    def distributed_attack(self):
        """Perform distributed attack simulation"""
        self.status_updated.emit("🌐 Starting distributed attack...")
        self.attack_log.emit("[INFO] Starting distributed attack")

        # Simulate distributed computing (in real implementation, this would coordinate multiple machines)
        self.attack_log.emit("[INFO] Coordinating distributed nodes...")

        # Simulate worker nodes
        num_workers = 4  # Simulate 4 worker machines
        passwords_per_worker = 1000

        self.attack_log.emit(f"[INFO] Using {num_workers} distributed workers")

        total_attempts = num_workers * passwords_per_worker
        attempt_count = 0

        for worker_id in range(num_workers):
            if self.stop_flag:
                break

            self.status_updated.emit(f"🖥️ Worker {worker_id + 1}/{num_workers} processing...")

            # Simulate work distribution
            for i in range(passwords_per_worker):
                if self.stop_flag:
                    break

                self.handle_pause()

                attempt_count += 1

                # Generate distributed password (simplified)
                password = f"distributed{worker_id}{i}"

                attempt_result = self.attempt_password(password)
                if attempt_result['success']:
                    self.handle_success(password, attempt_result, attempt_count)
                    return

                self.total_attempts += 1

                # Progress update
                progress = min(int((attempt_count / total_attempts) * 100), 99)
                self.update_progress(progress, attempt_count, total_attempts)

        self.result_updated.emit("❌ Distributed attack completed - password not found")
        self.status_updated.emit("🔚 Distributed attack finished")

    # ==================== NEW ATTACK HELPER FUNCTIONS ====================

    def simulate_rainbow_lookup(self, hash_prefix):
        """Simulate rainbow table lookup"""
        # Simplified simulation - in real implementation, this would search actual rainbow tables
        hash_map = {
            '5d41402abc4b2a76b9719d911017c592': 'hello',
            '098f6bcd4621d373cade4e832627b4f6': 'test',
            'd41d8cd98f00b204e9800998ecf8427e': '',
            'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3': 'admin'
        }

        return hash_map.get(hash_prefix[:32])  # MD5 prefix lookup

    def generate_markov_password(self, transitions, min_length=6, max_length=12):
        """Generate password using Markov chain"""
        if not transitions:
            return ''.join(random.choices(self.charset, k=random.randint(min_length, max_length)))

        # Start with random character
        current_char = random.choice(list(transitions.keys()))
        password = [current_char]

        # Generate password using transition probabilities
        while len(password) < max_length:
            if current_char in transitions:
                next_chars = list(transitions[current_char].keys())
                weights = list(transitions[current_char].values())

                if next_chars:
                    current_char = random.choices(next_chars, weights=weights)[0]
                    password.append(current_char)
                else:
                    break
            else:
                break

        # Ensure minimum length
        while len(password) < min_length:
            password.append(random.choice(self.charset))

        return ''.join(password)

    # ==================== MUTATION FUNCTIONS ====================

    def mutation_original(self, password):
        return [password]

    def mutation_uppercase(self, password):
        return [password.upper()]

    def mutation_lowercase(self, password):
        return [password.lower()]

    def mutation_capitalize(self, password):
        return [password.capitalize()]

    def mutation_leet_speak(self, password):
        leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7', 'b': '8'}
        return [''.join(leet_map.get(c, c) for c in password)]

    def mutation_append_numbers(self, password):
        return [password + str(i) for i in range(100)]

    def mutation_prepend_numbers(self, password):
        return [str(i) + password for i in range(100)]

    def mutation_append_special(self, password):
        special_chars = "!@#$%^&*"
        return [password + c for c in special_chars]

    def mutation_prepend_special(self, password):
        special_chars = "!@#$%^&*"
        return [c + password for c in special_chars]

    def mutation_reverse(self, password):
        return [password[::-1]]

    def mutation_double(self, password):
        return [password + password, password * 2]

    def mutation_insert_special(self, password):
        special_chars = "!@#$%^&*"
        results = []
        for c in special_chars:
            for i in range(len(password) + 1):
                results.append(password[:i] + c + password[i:])
        return results

    def mutation_date_format(self, password):
        years = [str(y) for y in range(1990, 2025)]
        months = [f"{m:02d}" for m in range(1, 13)]
        days = [f"{d:02d}" for d in range(1, 32)]

        variations = []
        for year in years:
            variations.append(password + year)
            variations.append(year + password)
        for month in months:
            variations.append(password + month)
        for day in days:
            variations.append(password + day)

        return variations

    def mutation_keyboard_walk(self, password):
        """Generate keyboard walk patterns"""
        keyboard_patterns = {
            'q': 'w', 'w': 'e', 'e': 'r', 'r': 't', 'y': 'u', 'u': 'i',
            'a': 's', 's': 'd', 'd': 'f', 'f': 'g',
            'z': 'x', 'x': 'c', 'c': 'v',
            '1': '2', '2': '3', '3': '4', '4': '5'
        }

        variations = []
        for char in password:
            if char.lower() in keyboard_patterns:
                variations.append(password.replace(char, keyboard_patterns[char.lower()]))

        return variations

    def mutation_repeat_chars(self, password):
        variations = []
        for char in password:
            variations.append(password.replace(char, char * 2))
        return variations

    # ==================== HELPER FUNCTIONS ====================

    def attempt_password(self, password: str) -> Dict[str, Any]:
        """Simulate password attempt with realistic timing.

        This method simulates the process of attempting a password against a target system.
        In a real implementation, this would perform actual authentication attempts.

        Args:
            password: The password string to attempt

        Returns:
            Dict containing:
                - 'success': Boolean indicating if the password was correct
                - 'hash': MD5 hash of the password (for demonstration)
                - 'time': Simulated response time in seconds
        """
        # Simulate network/authentication delay
        time.sleep(random.uniform(0.001, 0.005))

        # Simulation: 3% chance of "success" for demo purposes
        if random.random() < 0.03:
            return {
                'success': True,
                'hash': hashlib.md5(password.encode()).hexdigest(),
                'time': random.uniform(0.01, 0.1)
            }

        return {
            'success': False,
            'hash': hashlib.md5(password.encode()).hexdigest() if password else None,
            'time': random.uniform(0.001, 0.005)
        }

    def increment_password(self, password_list: List[str], length: int) -> bool:
        """Increment password like a number in base-N arithmetic.

        This method treats the password as a number in base-N (where N is charset size)
        and increments it by 1. Used for brute force password generation.

        Args:
            password_list: List of characters representing the current password
            length: Current length of the password

        Returns:
            True if increment was successful, False if we've reached the maximum
        """
        for i in range(length - 1, -1, -1):
            char_index = self.charset.index(password_list[i])
            if char_index < len(self.charset) - 1:
                password_list[i] = self.charset[char_index + 1]
                for j in range(i + 1, length):
                    password_list[j] = self.charset[0]
                return True
            else:
                password_list[i] = self.charset[0]
        return False

    def generate_mask_passwords(self, mask: str, limit: int = 100000) -> str:
        """Generate passwords from mask pattern using Hashcat-style notation.

        Supports mask characters:
        - ?a: Any character (letters, digits, symbols)
        - ?u: Uppercase letters
        - ?l: Lowercase letters
        - ?d: Digits
        - ?s: Special characters
        - ?h: Hexadecimal digits
        - ?H: Uppercase hexadecimal digits
        - ?b: Binary digits (0, 1)

        Args:
            mask: Mask pattern string (e.g., "?u?l?l?l?d?d?d?d")
            limit: Maximum number of passwords to generate

        Yields:
            Generated password strings matching the mask pattern
        """
        charset_map = {
            '?a': string.ascii_letters + string.digits + string.punctuation,
            '?u': string.ascii_uppercase,
            '?l': string.ascii_lowercase,
            '?d': string.digits,
            '?s': string.punctuation,
            '?h': string.hexdigits,
            '?H': string.hexdigits.upper(),
            '?b': '01'
        }

        # Parse mask
        current_charset = charset_map['?a']
        password = []

        i = 0
        while i < len(mask) and len(password) < limit:
            if mask[i] == '?':
                if i + 1 < len(mask):
                    char_set = charset_map.get(mask[i:i+2], charset_map['?a'])
                    password.append(char_set[0])
                    i += 2
                else:
                    password.append(current_charset[0])
                    i += 1
            else:
                password.append(mask[i])
                i += 1

            yield ''.join(password)

    def process_batch(self, variations: List[str], total_generated: int) -> None:
        """Process a batch of password variations for rule-based attacks.

        This method handles processing of password variations in batches to optimize
        memory usage and provide regular progress updates during rule-based attacks.

        Args:
            variations: List of password variations to test
            total_generated: Total number of variations generated so far
        """
        for password in variations[:self.batch_size]:
            if self.stop_flag:
                break

            self.handle_pause()

            attempt_result = self.attempt_password(password)
            if attempt_result['success']:
                self.handle_success(password, attempt_result, total_generated)
                return

            self.total_attempts += 1

        # Update progress
        progress = min(int((total_generated / 1000000) * 100), 99)
        self.update_progress(progress, self.total_attempts, 1000000)

    def handle_success(self, password: str, attempt_result: Dict[str, Any], attempt_number: int) -> None:
        """Handle successful password discovery and emit success signals.

        This method is called when a correct password is found. It emits multiple
        signals to update the UI with success information and logs the event.

        Args:
            password: The correct password that was found
            attempt_result: Dictionary containing attempt details (hash, time, etc.)
            attempt_number: The attempt number when the password was found
        """
        self.result_updated.emit(f"✅ SUCCESS: Password found: {password}")
        self.result_updated.emit(f"📊 Attempt #{attempt_number:,}")
        self.result_updated.emit(f"🔐 Hash: {attempt_result['hash']}")
        self.result_updated.emit(f"⏱️ Time: {attempt_result['time']:.4f}s")

        self.status_updated.emit("🎉 Password found!")
        self.attack_log.emit(f"[SUCCESS] Password found: {password}")
        self.attack_log.emit(f"[SUCCESS] Attempt #{attempt_number:,}")

        self.stats['status'] = 'success'

    def handle_error(self, error_msg: str) -> None:
        """Handle attack errors and emit error signals.

        This method is called when an error occurs during attack execution.
        It emits error signals to update the UI and logs the error event.

        Args:
            error_msg: The error message describing what went wrong
        """
        self.error_occurred.emit(error_msg)
        self.status_updated.emit(f"❌ Error: {error_msg}")
        self.attack_log.emit(f"[ERROR] {error_msg}")
        self.stats['errors'] += 1

    def finalize_attack(self) -> None:
        """Finalize attack execution and update final statistics.

        This method is called at the end of every attack to calculate final
        performance metrics including total passwords tested, passwords per second,
        and average speed. It updates the stats dictionary with completion data.
        """
        # Clean up thread pool
        if self.thread_pool:
            self.thread_pool.stop()
            self.thread_pool = None
            self.batch_processor = None

        self.stats['end_time'] = datetime.now()
        self.stats['total_passwords_tested'] = self.total_attempts

        if self.start_time:
            duration = (self.stats['end_time'] - self.start_time).total_seconds()
            if duration > 0:
                self.stats['passwords_per_second'] = self.total_attempts / duration
                self.stats['average_speed'] = self.stats['passwords_per_second']

        self.stats['status'] = 'completed'

    def update_progress(self, progress, attempts, total):
        """Update progress with speed and ETA calculation"""
        current_time = time.time()

        # Update speed calculation
        self.attempt_history.append((current_time, attempts))
        if len(self.attempt_history) >= 2:
            time_diff = current_time - self.attempt_history[0][0]
            attempt_diff = attempts - self.attempt_history[0][1]
            if time_diff > 0:
                self.current_speed = attempt_diff / time_diff

        # Calculate ETA
        eta_seconds = 0
        if self.current_speed > 0 and total > attempts:
            remaining_attempts = total - attempts
            eta_seconds = remaining_attempts / self.current_speed

        eta_str = self.format_eta(eta_seconds)
        speed_str = f"{self.current_speed:.1f}"

        self.progress_updated.emit(progress, speed_str, eta_str, attempts)

    def format_eta(self, seconds):
        """Format ETA in HH:MM:SS"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def handle_pause(self):
        """Handle pause functionality"""
        if self.pause_flag:
            self.mutex.lock()
            self.pause_condition.wait(self.mutex)
            self.mutex.unlock()

    def save_checkpoint(self, attack_type, position):
        """Save checkpoint for resume capability"""
        if self.total_attempts - self.last_checkpoint >= self.checkpoint_interval:
            self.resume_data = {
                'attack_type': attack_type,
                'position': position,
                'total_attempts': self.total_attempts,
                'timestamp': datetime.now().isoformat()
            }
            self.last_checkpoint = self.total_attempts

    def pause(self):
        """Pause the attack"""
        self.pause_flag = True
        self.status_updated.emit("⏸️ Attack paused")

    def resume(self):
        """Resume the attack"""
        self.pause_flag = False
        self.resume_flag = True
        self.pause_condition.wakeAll()
        self.status_updated.emit("▶ Attack resumed")

    def stop(self):
        """Stop the attack"""
        self.stop_flag = True
        self.pause_flag = False
        self.resume_flag = False
        self.pause_condition.wakeAll()
        self.status_updated.emit("🛑 Attack stopped")

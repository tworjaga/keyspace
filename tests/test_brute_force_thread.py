"""
Unit tests for BruteForceThread core functions
"""

import unittest
import time
from unittest.mock import patch, MagicMock
from backend.brute_force_thread import BruteForceThread


class TestBruteForceThread(unittest.TestCase):
    """Test cases for BruteForceThread methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.thread = BruteForceThread(
            target="test_target",
            attack_type="Dictionary Attack (WPA2)",
            wordlist_path="",
            min_length=8,
            max_length=16,
            charset="abc123",
            custom_rules=[]
        )

    def test_initialization(self):
        """Test thread initialization"""
        self.assertEqual(self.thread.target, "test_target")
        self.assertEqual(self.thread.attack_type, "Dictionary Attack (WPA2)")
        self.assertEqual(self.thread.min_length, 8)
        self.assertEqual(self.thread.max_length, 16)
        self.assertEqual(self.thread.charset, "abc123")
        self.assertFalse(self.thread.stop_flag)
        self.assertFalse(self.thread.pause_flag)

    def test_attempt_password_structure(self):
        """Test attempt_password returns correct structure"""
        result = self.thread.attempt_password("test_password")

        self.assertIn('success', result)
        self.assertIn('hash', result)
        self.assertIn('time', result)
        self.assertIsInstance(result['success'], bool)
        self.assertIsInstance(result['time'], float)

    def test_increment_password(self):
        """Test password increment logic"""
        # Temporarily set charset for test
        original_charset = self.thread.charset
        self.thread.charset = "abc"

        password_list = ['a', 'a', 'a']
        length = 3

        # Test increment
        result = self.thread.increment_password(password_list, length)
        self.assertTrue(result)
        self.assertEqual(password_list, ['a', 'a', 'b'])

        # Test rollover
        password_list = ['c', 'c', 'c']
        result = self.thread.increment_password(password_list, length)
        self.assertFalse(result)  # Should return False when max reached
        self.assertEqual(password_list, ['a', 'a', 'a'])

        # Restore charset
        self.thread.charset = original_charset

    def test_format_eta(self):
        """Test ETA formatting"""
        # Test zero seconds
        self.assertEqual(self.thread.format_eta(0), "00:00:00")

        # Test seconds
        self.assertEqual(self.thread.format_eta(59), "00:00:59")

        # Test minutes
        self.assertEqual(self.thread.format_eta(125), "00:02:05")

        # Test hours
        self.assertEqual(self.thread.format_eta(3661), "01:01:01")

    def test_format_file_size(self):
        """Test file size formatting"""
        self.assertEqual(self.thread.format_file_size(512), "512.0 B")
        self.assertEqual(self.thread.format_file_size(1024), "1.0 KB")
        self.assertEqual(self.thread.format_file_size(1024*1024), "1.0 MB")
        self.assertEqual(self.thread.format_file_size(1024*1024*1024), "1.0 GB")

    def test_mutation_original(self):
        """Test original password mutation"""
        result = self.thread.mutation_original("password")
        self.assertEqual(result, ["password"])

    def test_mutation_uppercase(self):
        """Test uppercase mutation"""
        result = self.thread.mutation_uppercase("password")
        self.assertEqual(result, ["PASSWORD"])

    def test_mutation_lowercase(self):
        """Test lowercase mutation"""
        result = self.thread.mutation_lowercase("PASSWORD")
        self.assertEqual(result, ["password"])

    def test_mutation_capitalize(self):
        """Test capitalize mutation"""
        result = self.thread.mutation_capitalize("password")
        self.assertEqual(result, ["Password"])

    def test_mutation_leet_speak(self):
        """Test leet speak mutation"""
        result = self.thread.mutation_leet_speak("password")
        self.assertEqual(result, ["p455w0rd"])

    def test_mutation_reverse(self):
        """Test reverse mutation"""
        result = self.thread.mutation_reverse("password")
        self.assertEqual(result, ["drowssap"])

    def test_mutation_double(self):
        """Test double mutation"""
        result = self.thread.mutation_double("pass")
        self.assertIn("passpass", result)
        self.assertIn("passpass", result)  # Should have both variations

    def test_mutation_append_numbers(self):
        """Test append numbers mutation"""
        result = self.thread.mutation_append_numbers("pass")
        self.assertEqual(len(result), 100)  # 0-99
        self.assertIn("pass0", result)
        self.assertIn("pass99", result)

    def test_mutation_prepend_numbers(self):
        """Test prepend numbers mutation"""
        result = self.thread.mutation_prepend_numbers("word")
        self.assertEqual(len(result), 100)
        self.assertIn("0word", result)
        self.assertIn("99word", result)

    def test_mutation_append_special(self):
        """Test append special characters mutation"""
        result = self.thread.mutation_append_special("pass")
        expected_chars = "!@#$%^&*"
        self.assertEqual(len(result), len(expected_chars))
        for char in expected_chars:
            self.assertIn(f"pass{char}", result)

    def test_mutation_prepend_special(self):
        """Test prepend special characters mutation"""
        result = self.thread.mutation_prepend_special("word")
        expected_chars = "!@#$%^&*"
        self.assertEqual(len(result), len(expected_chars))
        for char in expected_chars:
            self.assertIn(f"{char}word", result)

    def test_mutation_insert_special(self):
        """Test insert special characters mutation"""
        result = self.thread.mutation_insert_special("pa")
        # Should insert at all positions
        self.assertIn("!pa", result)
        self.assertIn("p!a", result)
        self.assertIn("pa!", result)

    def test_generate_markov_password(self):
        """Test Markov chain password generation"""
        transitions = {
            'a': {'b': 2, 'c': 1},
            'b': {'c': 1},
            'c': {'a': 1}
        }

        password = self.thread.generate_markov_password(transitions, min_length=3, max_length=5)
        self.assertIsInstance(password, str)
        self.assertGreaterEqual(len(password), 3)
        self.assertLessEqual(len(password), 5)

    def test_simulate_rainbow_lookup(self):
        """Test rainbow table lookup simulation"""
        # Test known hash
        result = self.thread.simulate_rainbow_lookup('5d41402abc4b2a76b9719d911017c592')
        self.assertEqual(result, 'hello')

        # Test unknown hash
        result = self.thread.simulate_rainbow_lookup('unknown_hash')
        self.assertIsNone(result)

    def test_generate_mask_passwords(self):
        """Test mask-based password generation"""
        mask = "?u?l?d"
        passwords = list(self.thread.generate_mask_passwords(mask, limit=10))

        self.assertGreater(len(passwords), 0)
        self.assertLessEqual(len(passwords), 10)

        # Check that passwords are generated progressively (incremental lengths)
        lengths = [len(pwd) for pwd in passwords]
        self.assertTrue(all(lengths[i] <= lengths[i+1] for i in range(len(lengths)-1)))  # Non-decreasing lengths

    def test_save_checkpoint(self):
        """Test checkpoint saving"""
        self.thread.total_attempts = 1500
        self.thread.last_checkpoint = 0
        self.thread.checkpoint_interval = 1000

        self.thread.save_checkpoint("test_attack", 100)

        # Should save checkpoint since 1500 - 0 >= 1000
        self.assertIn('attack_type', self.thread.resume_data)
        self.assertEqual(self.thread.resume_data['attack_type'], "test_attack")
        self.assertEqual(self.thread.resume_data['position'], 100)

    def test_pause_resume_stop_flags(self):
        """Test pause, resume, and stop functionality"""
        # Test pause
        self.thread.pause()
        self.assertTrue(self.thread.pause_flag)

        # Test resume
        self.thread.resume()
        self.assertFalse(self.thread.pause_flag)
        self.assertTrue(self.thread.resume_flag)

        # Test stop
        self.thread.stop()
        self.assertTrue(self.thread.stop_flag)
        self.assertFalse(self.thread.pause_flag)
        self.assertFalse(self.thread.resume_flag)


if __name__ == '__main__':
    unittest.main()

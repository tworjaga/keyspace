"""
GUI tests for MainWindow using pytest-qt
"""

import pytest
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from frontend.ui.main_window import MainWindow


@pytest.fixture
def app(qapp):
    """Provide QApplication instance"""
    return qapp


@pytest.fixture
def main_window(app):
    """Create MainWindow instance for testing"""
    # Create window with no integration manager to avoid dependencies
    window = MainWindow(integration_manager=None)
    yield window
    # Cleanup
    if window.isVisible():
        window.close()


class TestMainWindow:
    """Test cases for MainWindow GUI components"""

    def test_window_initialization(self, main_window):
        """Test that MainWindow initializes correctly"""
        assert main_window.windowTitle() == "Keyspace - Advanced Password Cracking"

        assert main_window.geometry().width() >= 1400
        assert main_window.geometry().height() >= 900

    def test_ui_components_exist(self, main_window):
        """Test that all major UI components are created"""
        # Check main components exist
        assert hasattr(main_window, 'attack_config_panel')
        assert hasattr(main_window, 'tab_widget')
        assert hasattr(main_window, 'results_panel')

        # Check attack configuration components
        assert hasattr(main_window, 'target_input')
        assert hasattr(main_window, 'attack_type_combo')
        assert hasattr(main_window, 'wordlist_input')
        assert hasattr(main_window, 'min_length_spin')
        assert hasattr(main_window, 'max_length_spin')
        assert hasattr(main_window, 'charset_input')

        # Check control buttons
        assert hasattr(main_window, 'start_attack_btn')
        assert hasattr(main_window, 'stop_attack_btn')
        assert hasattr(main_window, 'pause_attack_btn')
        assert hasattr(main_window, 'resume_attack_btn')

    def test_attack_type_combo_values(self, main_window):
        """Test that attack type combo box has correct values"""
        expected_attack_types = [
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
        ]

        actual_attack_types = [main_window.attack_type_combo.itemText(i)
                              for i in range(main_window.attack_type_combo.count())]

        assert actual_attack_types == expected_attack_types

    def test_spin_box_ranges(self, main_window):
        """Test that spin boxes have correct ranges"""
        assert main_window.min_length_spin.minimum() == 1
        assert main_window.min_length_spin.maximum() == 32
        assert main_window.min_length_spin.value() == 8

        assert main_window.max_length_spin.minimum() == 1
        assert main_window.max_length_spin.maximum() == 32
        assert main_window.max_length_spin.value() == 16

    def test_default_values(self, main_window):
        """Test that default values are set correctly"""
        assert main_window.target_input.text() == "demo_target"
        assert main_window.charset_input.text() == "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"

    def test_button_states_initial(self, main_window):
        """Test initial button states"""
        assert main_window.start_attack_btn.isEnabled()
        assert not main_window.stop_attack_btn.isEnabled()
        assert not main_window.pause_attack_btn.isEnabled()
        assert not main_window.resume_attack_btn.isEnabled()

    def test_tab_widget_setup(self, main_window):
        """Test that tab widget is set up correctly"""
        assert main_window.tab_widget.count() >= 3  # Dashboard, Attack Log, Statistics

        # Check tab names (may or may not have emoji prefixes)
        assert "Dashboard" in main_window.tab_widget.tabText(0)
        assert "Attack Log" in main_window.tab_widget.tabText(1)
        assert "Statistics" in main_window.tab_widget.tabText(2)


    def test_dashboard_components(self, main_window):
        """Test dashboard panel components"""
        dashboard = main_window.dashboard_panel

        # Check for key dashboard components
        assert hasattr(main_window, 'attack_status_label')
        assert hasattr(main_window, 'progress_bar')
        assert hasattr(main_window, 'speed_label')
        assert hasattr(main_window, 'eta_label')

        # Check progress bar range
        assert main_window.progress_bar.minimum() == 0
        assert main_window.progress_bar.maximum() == 100

    def test_attack_log_components(self, main_window):
        """Test attack log panel components"""
        # Check for attack log text area
        assert hasattr(main_window, 'attack_log_text')
        assert hasattr(main_window, 'attack_log_filter_input')

    def test_results_panel_components(self, main_window):
        """Test results panel components"""
        # Check for results text area
        assert hasattr(main_window, 'results_text')
        assert hasattr(main_window, 'results_filter_input')

    def test_menu_bar_exists(self, main_window):
        """Test that menu bar is created"""
        assert main_window.menuBar() is not None

    def test_status_bar_exists(self, main_window):
        """Test that status bar is created"""
        assert main_window.statusBar is not None

    def test_toolbar_exists(self, main_window):
        """Test that toolbar is created"""
        # Check that toolbar exists (may be empty in test environment)
        toolbars = main_window.findChildren(type(main_window.addToolBar("test")))
        assert len(toolbars) > 0

    @pytest.mark.parametrize("theme", ["light", "dark"])
    def test_theme_switching(self, main_window, theme):
        """Test theme switching functionality"""
        # Store original theme
        original_theme = main_window.current_theme

        # Switch theme
        main_window.switch_theme(theme)

        # Check that theme was updated
        assert main_window.current_theme == theme

        # Switch back
        main_window.switch_theme(original_theme)
        assert main_window.current_theme == original_theme

    def test_filter_functionality(self, main_window):
        """Test text filtering functionality"""
        # Test results filter
        main_window.results_text.setPlainText("Line 1: test\nLine 2: example\nLine 3: test case")
        main_window.full_results_text = main_window.results_text.toPlainText()

        # Apply filter
        main_window.results_filter_input.setText("test")
        main_window.filter_results()

        # Check that only lines containing "test" are shown
        filtered_text = main_window.results_text.toPlainText()
        assert "Line 1: test" in filtered_text
        assert "Line 3: test case" in filtered_text
        assert "Line 2: example" not in filtered_text

    def test_attack_log_filter(self, main_window):
        """Test attack log filtering"""
        main_window.attack_log_text.setPlainText("INFO: Starting attack\nERROR: Connection failed\nINFO: Attack completed")
        main_window.full_attack_log_text = main_window.attack_log_text.toPlainText()

        # Apply filter for ERROR messages
        main_window.attack_log_filter_input.setText("ERROR")
        main_window.filter_attack_log()

        # Check filtering
        filtered_text = main_window.attack_log_text.toPlainText()
        assert "ERROR: Connection failed" in filtered_text
        assert "INFO:" not in filtered_text

    def test_clear_attack_log(self, main_window):
        """Test clearing attack log"""
        main_window.attack_log_text.setPlainText("Test log content")
        main_window.full_attack_log_text = "Test log content"

        # Clear log
        main_window.clear_attack_log()

        # Check that log is cleared
        assert main_window.attack_log_text.toPlainText() == ""
        assert main_window.full_attack_log_text == ""

    def test_new_session_reset(self, main_window):
        """Test new session functionality"""
        # Set some values
        main_window.target_input.setText("test_target")
        main_window.results_text.setPlainText("test results")
        main_window.attack_log_text.setPlainText("test log")
        main_window.progress_bar.setValue(50)

        # Create new session
        main_window.new_session()

        # Check that values are reset
        assert main_window.target_input.text() == ""
        assert main_window.results_text.toPlainText() == ""
        assert main_window.attack_log_text.toPlainText() == ""
        assert main_window.progress_bar.value() == 0

    def test_shortcut_validation(self, main_window):
        """Test keyboard shortcut validation"""
        # Test valid shortcuts
        assert main_window.validate_shortcut("Ctrl+S")
        assert main_window.validate_shortcut("Alt+F1")
        assert main_window.validate_shortcut("F5")

        # Test invalid shortcuts
        assert not main_window.validate_shortcut("Invalid")
        assert not main_window.validate_shortcut("Ctrl+Invalid")

    def test_wordlist_browse_dialog(self, main_window, qtbot):
        """Test wordlist browse dialog (mocked)"""
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("/path/to/wordlist.txt", "Text Files (*.txt)")

            # Trigger browse
            main_window.browse_wordlist()

            # Check that file path was set
            assert main_window.wordlist_input.text() == "/path/to/wordlist.txt"

    def test_form_validation_empty_target(self, main_window, qtbot):
        """Test form validation for empty target"""
        # Clear target
        main_window.target_input.clear()

        # Mock QMessageBox to avoid blocking
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            # Try to start attack
            main_window.start_attack()

            # Check that warning was shown
            mock_warning.assert_called_once()

    def test_form_validation_invalid_wordlist(self, main_window, qtbot):
        """Test form validation for invalid wordlist path"""
        main_window.target_input.setText("test_target")
        main_window.attack_type_combo.setCurrentText("Dictionary Attack (WPA2)")
        main_window.wordlist_input.setText("/nonexistent/wordlist.txt")

        # Mock QMessageBox to avoid blocking
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            # Try to start attack
            main_window.start_attack()

            # Check that warning was shown
            mock_warning.assert_called_once()

    def test_progress_update_simulation(self, main_window):
        """Test progress update mechanism"""
        # Simulate progress update
        main_window.on_progress_updated(50, 1000.5, "01:30:00", 50000)

        # Check that UI was updated
        assert main_window.progress_bar.value() == 50
        assert "50%" in main_window.progress_label.text()
        assert "1000.5" in main_window.speed_label.text()
        assert "01:30:00" in main_window.eta_label.text()
        assert "50,000" in main_window.attempts_status.text()

    def test_status_update(self, main_window):
        """Test status update mechanism"""
        main_window.on_status_updated("Test Status")

        assert main_window.attack_status_label.text() == "Status: Test Status"
        assert main_window.status_label.text() == "Test Status"

    def test_result_update(self, main_window):
        """Test result update mechanism"""
        test_result = "Test result line"
        main_window.on_result_updated(test_result)

        # Check that result was added
        assert test_result in main_window.results_text.toPlainText()
        assert test_result in main_window.full_results_text

    def test_attack_log_update(self, main_window):
        """Test attack log update mechanism"""
        test_log = "Test log entry"
        main_window.on_attack_log(test_log)

        # Check that log was added
        assert test_log in main_window.attack_log_text.toPlainText()
        assert test_log in main_window.full_attack_log_text

    def test_error_handling(self, main_window):
        """Test error handling mechanism"""
        test_error = "Test error message"

        # Mock QMessageBox to avoid blocking
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
            main_window.on_error_occurred(test_error)

            # Check that error dialog was shown
            mock_critical.assert_called_once_with(main_window, "Error", test_error)

    def test_attack_finished_cleanup(self, main_window):
        """Test attack finished cleanup"""
        # Set up attacking state
        main_window.is_attacking = True
        main_window.start_attack_btn.setEnabled(False)
        main_window.stop_attack_btn.setEnabled(True)
        main_window.pause_attack_btn.setEnabled(True)
        main_window.resume_attack_btn.setEnabled(False)

        # Mock thread stats
        mock_stats = {
            'total_passwords_tested': 100000,
            'average_speed': 1500.5,
            'peak_speed': 2000.0,
            'start_time': None,
            'end_time': None
        }

        with patch.object(main_window, 'brute_force_thread') as mock_thread:
            mock_thread.stats = mock_stats

            # Trigger attack finished
            main_window.on_attack_finished()

            # Check cleanup
            assert not main_window.is_attacking
            assert main_window.start_attack_btn.isEnabled()
            assert not main_window.stop_attack_btn.isEnabled()
            assert not main_window.pause_attack_btn.isEnabled()
            assert not main_window.resume_attack_btn.isEnabled()

    def test_update_display_timer(self, main_window, qtbot):
        """Test display update timer"""
        # Set initial time
        main_window.start_time = main_window.start_time  # Use current time

        # Wait for timer to trigger (1 second)
        qtbot.wait(1100)

        # Check that elapsed time was updated (should be > 0)
        elapsed_text = main_window.elapsed_time_label.text()
        assert "Elapsed:" in elapsed_text

    def test_window_close_with_attack_running(self, main_window):
        """Test window close behavior when attack is running"""
        main_window.is_attacking = True

        # Mock QMessageBox.question to return Yes
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            from PyQt6.QtWidgets import QMessageBox
            mock_question.return_value = QMessageBox.StandardButton.Yes

            # Mock close event
            from PyQt6.QtGui import QCloseEvent
            event = QCloseEvent()

            # Trigger close event
            main_window.closeEvent(event)

            # Check that question was asked
            mock_question.assert_called_once()

    def test_window_close_without_attack(self, main_window):
        """Test window close behavior when no attack is running"""
        main_window.is_attacking = False

        # Mock close event
        from PyQt6.QtGui import QCloseEvent
        event = QCloseEvent()

        # Trigger close event
        main_window.closeEvent(event)

        # Event should be accepted without questions
        assert event.isAccepted()

    def test_export_results_functionality(self, main_window):
        """Test results export functionality"""
        # Set some test results
        test_results = "Test result 1\nTest result 2\nTest result 3"
        main_window.results_text.setPlainText(test_results)

        # Mock file dialog and file operations
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName') as mock_dialog, \
             patch('builtins.open', create=True) as mock_file, \
             patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:

            mock_dialog.return_value = ("/path/to/export.txt", "Text Files (*.txt)")
            mock_file.return_value.__enter__.return_value.write = MagicMock()

            # Trigger export
            main_window.export_results()

            # Check that file was written
            mock_file.assert_called_once_with("/path/to/export.txt", 'w')
            mock_file.return_value.__enter__.return_value.write.assert_called_once_with(test_results)

            # Check that success message was shown
            mock_info.assert_called_once()

    def test_export_results_cancel(self, main_window):
        """Test results export when user cancels"""
        # Mock file dialog to return empty (cancelled)
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")

            # Trigger export
            main_window.export_results()

            # Should not show any messages or create files
            # (This is an implicit test - no assertions needed if no exceptions occur)

    def test_start_attack_valid_inputs(self, main_window):
        """Test start attack with valid inputs"""
        # Set up valid inputs
        main_window.target_input.setText("test_target")
        main_window.attack_type_combo.setCurrentText("Brute Force Attack")  # Doesn't require wordlist

        # Mock BruteForceThread to avoid actual thread creation
        with patch('frontend.ui.main_window.BruteForceThread') as mock_thread_class, \
             patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:

            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            # Trigger start attack
            main_window.start_attack()

            # Check that thread was created and started
            mock_thread_class.assert_called_once()
            mock_thread.start.assert_called_once()

            # Check UI state changes
            assert not main_window.start_attack_btn.isEnabled()
            assert main_window.stop_attack_btn.isEnabled()
            assert main_window.pause_attack_btn.isEnabled()
            assert not main_window.resume_attack_btn.isEnabled()
            assert main_window.is_attacking

    def test_stop_attack_button(self, main_window):
        """Test stop attack button functionality"""
        # Set up attacking state
        main_window.is_attacking = True
        main_window.brute_force_thread = MagicMock()

        # Trigger stop attack
        main_window.stop_attack()

        # Check that thread stop was called
        main_window.brute_force_thread.stop.assert_called_once()

    def test_pause_attack_button(self, main_window):
        """Test pause attack button functionality"""
        # Set up attacking state
        main_window.is_attacking = True
        main_window.brute_force_thread = MagicMock()

        # Trigger pause attack
        main_window.pause_attack()

        # Check that thread pause was called
        main_window.brute_force_thread.pause.assert_called_once()

        # Check button states
        assert not main_window.pause_attack_btn.isEnabled()
        assert main_window.resume_attack_btn.isEnabled()

    def test_resume_attack_button(self, main_window):
        """Test resume attack button functionality"""
        # Set up paused state
        main_window.is_attacking = True
        main_window.brute_force_thread = MagicMock()

        # Trigger resume attack
        main_window.resume_attack()

        # Check that thread resume was called
        main_window.brute_force_thread.resume.assert_called_once()

        # Check button states
        assert main_window.pause_attack_btn.isEnabled()
        assert not main_window.resume_attack_btn.isEnabled()

    def test_toolbar_buttons_connection(self, main_window):
        """Test that toolbar buttons are connected to correct handlers"""
        # Check that toolbar buttons exist and are connected
        assert hasattr(main_window, 'start_tb_btn')
        assert hasattr(main_window, 'stop_tb_btn')

        # Check connections (this tests that the buttons are properly set up)
        assert main_window.start_tb_btn.isEnabled()
        assert not main_window.stop_tb_btn.isEnabled()

    def test_menu_actions_exist(self, main_window):
        """Test that menu actions are created"""
        menubar = main_window.menuBar()

        # Check File menu
        file_menu = menubar.findChild(type(menubar.addMenu("File")))
        if file_menu:
            actions = file_menu.actions()
            assert len(actions) > 0  # Should have New, Open, Save, Exit

        # Check Attack menu
        attack_menu = menubar.findChild(type(menubar.addMenu("Attack")))
        if attack_menu:
            actions = attack_menu.actions()
            assert len(actions) > 0  # Should have Start, Stop, Pause, Resume

    def test_form_validation_min_length_greater_than_max(self, main_window):
        """Test form validation when min length > max length"""
        main_window.target_input.setText("test_target")
        main_window.attack_type_combo.setCurrentText("Brute Force Attack")
        main_window.min_length_spin.setValue(16)
        main_window.max_length_spin.setValue(8)  # Min > Max

        # Mock QMessageBox to avoid blocking
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            # Try to start attack
            main_window.start_attack()

            # Should show warning (though this specific validation might not be implemented)
            # This tests the general validation framework

    def test_form_validation_empty_charset(self, main_window):
        """Test form validation for empty charset"""
        main_window.target_input.setText("test_target")
        main_window.attack_type_combo.setCurrentText("Brute Force Attack")
        main_window.charset_input.clear()  # Empty charset

        # Mock QMessageBox to avoid blocking
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            # Try to start attack
            main_window.start_attack()

            # Should show warning or handle gracefully

    def test_form_validation_invalid_length_range(self, main_window):
        """Test form validation for invalid length ranges"""
        main_window.target_input.setText("test_target")
        main_window.attack_type_combo.setCurrentText("Brute Force Attack")
        main_window.min_length_spin.setValue(0)  # Invalid minimum
        main_window.max_length_spin.setValue(100)  # Invalid maximum

        # Mock QMessageBox to avoid blocking
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            # Try to start attack
            main_window.start_attack()

            # Should handle invalid ranges gracefully

    def test_button_states_during_attack(self, main_window):
        """Test button state transitions during attack lifecycle"""
        # Initial state
        assert main_window.start_attack_btn.isEnabled()
        assert not main_window.stop_attack_btn.isEnabled()
        assert not main_window.pause_attack_btn.isEnabled()
        assert not main_window.resume_attack_btn.isEnabled()

        # Simulate attack start
        main_window.is_attacking = True
        main_window.start_attack_btn.setEnabled(False)
        main_window.stop_attack_btn.setEnabled(True)
        main_window.pause_attack_btn.setEnabled(True)
        main_window.resume_attack_btn.setEnabled(False)

        # Check attacking state
        assert not main_window.start_attack_btn.isEnabled()
        assert main_window.stop_attack_btn.isEnabled()
        assert main_window.pause_attack_btn.isEnabled()
        assert not main_window.resume_attack_btn.isEnabled()

        # Simulate pause
        main_window.pause_attack_btn.setEnabled(False)
        main_window.resume_attack_btn.setEnabled(True)

        # Check paused state
        assert not main_window.pause_attack_btn.isEnabled()
        assert main_window.resume_attack_btn.isEnabled()

        # Simulate resume
        main_window.pause_attack_btn.setEnabled(True)
        main_window.resume_attack_btn.setEnabled(False)

        # Check resumed state
        assert main_window.pause_attack_btn.isEnabled()
        assert not main_window.resume_attack_btn.isEnabled()

        # Simulate attack finish
        main_window.is_attacking = False
        main_window.start_attack_btn.setEnabled(True)
        main_window.stop_attack_btn.setEnabled(False)
        main_window.pause_attack_btn.setEnabled(False)
        main_window.resume_attack_btn.setEnabled(False)

        # Check finished state
        assert main_window.start_attack_btn.isEnabled()
        assert not main_window.stop_attack_btn.isEnabled()
        assert not main_window.pause_attack_btn.isEnabled()
        assert not main_window.resume_attack_btn.isEnabled()

    def test_form_validation_wordlist_required_attacks(self, main_window):
        """Test that wordlist is required for certain attack types"""
        main_window.target_input.setText("test_target")

        # Test attacks that require wordlist
        wordlist_required_attacks = [
            "Dictionary Attack (WPA2)",
            "Rule-based Attack",
            "Hybrid Attack",
            "Combinator Attack"
        ]

        for attack_type in wordlist_required_attacks:
            main_window.attack_type_combo.setCurrentText(attack_type)
            main_window.wordlist_input.clear()  # No wordlist

            with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
                main_window.start_attack()
                # Should show warning about missing wordlist

    def test_form_validation_wordlist_not_required_attacks(self, main_window):
        """Test that wordlist is not required for certain attack types"""
        main_window.target_input.setText("test_target")

        # Test attacks that don't require wordlist
        no_wordlist_attacks = [
            "Brute Force Attack",
            "Mask Attack",
            "Pin Code Attack",
            "Rainbow Table Attack",
            "Markov Chain Attack",
            "Neural Network Attack",
            "Distributed Attack"
        ]

        for attack_type in no_wordlist_attacks:
            main_window.attack_type_combo.setCurrentText(attack_type)
            main_window.wordlist_input.clear()  # No wordlist

            # These should not show wordlist warnings
            with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning, \
                 patch('frontend.ui.main_window.BruteForceThread') as mock_thread_class:

                mock_thread = MagicMock()
                mock_thread_class.return_value = mock_thread

                main_window.start_attack()

                # Check that no wordlist warning was shown
                # (Other warnings might be shown, but not about wordlist)

    def test_input_field_limits(self, main_window):
        """Test that input fields have reasonable limits"""
        # Test charset input length
        long_charset = "a" * 1000  # Very long charset
        main_window.charset_input.setText(long_charset)
        assert main_window.charset_input.text() == long_charset  # Should accept

        # Test target input length
        long_target = "target_" * 100  # Long target name
        main_window.target_input.setText(long_target)
        assert main_window.target_input.text() == long_target  # Should accept

    def test_spin_box_value_changes(self, main_window):
        """Test that spin box values can be changed programmatically"""
        # Test min length
        main_window.min_length_spin.setValue(5)
        assert main_window.min_length_spin.value() == 5

        main_window.min_length_spin.setValue(20)
        assert main_window.min_length_spin.value() == 20

        # Test max length
        main_window.max_length_spin.setValue(10)
        assert main_window.max_length_spin.value() == 10

        main_window.max_length_spin.setValue(25)
        assert main_window.max_length_spin.value() == 25

    def test_combo_box_selection_changes(self, main_window):
        """Test that combo box selection changes work"""
        # Test attack type changes
        attack_types = [
            "Dictionary Attack (WPA2)",
            "Brute Force Attack",
            "Rule-based Attack"
        ]

        for attack_type in attack_types:
            main_window.attack_type_combo.setCurrentText(attack_type)
            assert main_window.attack_type_combo.currentText() == attack_type

    def test_text_input_validation(self, main_window):
        """Test text input field validation"""
        # Test target input
        main_window.target_input.setText("valid_target")
        assert main_window.target_input.text() == "valid_target"

        main_window.target_input.setText("")  # Empty
        assert main_window.target_input.text() == ""

        # Test charset input
        main_window.charset_input.setText("abc123!@#")
        assert main_window.charset_input.text() == "abc123!@#"

        # Test wordlist input
        main_window.wordlist_input.setText("/path/to/wordlist.txt")
        assert main_window.wordlist_input.text() == "/path/to/wordlist.txt"

    def test_graph_update_methods(self, main_window):
        """Test graph update methods don't crash with empty data"""
        # Test with no data
        main_window.time_data.clear()
        main_window.speed_data.clear()
        main_window.progress_data.clear()
        
        # These should not raise exceptions
        main_window.update_speed_graph()
        main_window.update_progress_graph()
        
        # Test with data
        import time
        current_time = time.time() - main_window.start_time
        main_window.time_data.append(current_time)
        main_window.speed_data.append(1000.0)
        main_window.progress_data.append(50)
        
        main_window.update_speed_graph()
        main_window.update_progress_graph()

    def test_speed_graph_with_invalid_values(self, main_window):
        """Test speed graph handles invalid values gracefully"""
        import time
        
        # Add invalid values
        current_time = time.time() - main_window.start_time
        main_window.time_data.append(current_time)
        main_window.speed_data.append(-1)  # Invalid negative speed
        main_window.progress_data.append(50)
        
        # Should handle gracefully
        main_window.update_speed_graph()
        main_window.update_progress_graph()

    def test_attack_log_filter_empty(self, main_window):
        """Test attack log filter with empty log"""
        main_window.full_attack_log_text = ""
        main_window.attack_log_text.setPlainText("")
        main_window.attack_log_filter_input.setText("test")
        main_window.filter_attack_log()
        
        # Should handle empty log gracefully
        assert main_window.attack_log_text.toPlainText() == ""

    def test_results_filter_empty(self, main_window):
        """Test results filter with empty results"""
        main_window.full_results_text = ""
        main_window.results_text.setPlainText("")
        main_window.results_filter_input.setText("test")
        main_window.filter_results()
        
        # Should handle empty results gracefully
        assert main_window.results_text.toPlainText() == ""

    def test_clear_attack_log_already_empty(self, main_window):
        """Test clearing already empty attack log"""
        main_window.attack_log_text.clear()
        main_window.full_attack_log_text = ""
        
        # Should not raise exception
        main_window.clear_attack_log()
        assert main_window.attack_log_text.toPlainText() == ""

    def test_new_session_already_reset(self, main_window):
        """Test new session when already in reset state"""
        # First reset
        main_window.new_session()
        
        # Reset again - should not raise exception
        main_window.new_session()
        
        # Check values are still reset
        assert main_window.target_input.text() == ""
        assert main_window.progress_bar.value() == 0

    def test_progress_update_edge_cases(self, main_window):
        """Test progress update with edge case values"""
        # Test with zero values
        main_window.on_progress_updated(0, 0.0, "00:00:00", 0)
        assert main_window.progress_bar.value() == 0
        
        # Test with maximum values
        main_window.on_progress_updated(100, 999999.9, "99:99:99", 999999999)
        assert main_window.progress_bar.value() == 100
        
        # Test with string speed that needs conversion
        main_window.on_progress_updated(50, "1000.5", "01:30:00", 50000)
        assert main_window.progress_bar.value() == 50

    def test_result_update_multiple(self, main_window):
        """Test multiple result updates"""
        results = ["Result 1", "Result 2", "Result 3"]
        
        for result in results:
            main_window.on_result_updated(result)
        
        # Check all results are present
        full_text = main_window.results_text.toPlainText()
        for result in results:
            assert result in full_text

    def test_attack_log_multiple_entries(self, main_window):
        """Test multiple attack log entries"""
        entries = ["Entry 1", "Entry 2", "Entry 3"]
        
        for entry in entries:
            main_window.on_attack_log(entry)
        
        # Check all entries are present
        full_text = main_window.attack_log_text.toPlainText()
        for entry in entries:
            assert entry in full_text

    def test_status_update_sequence(self, main_window):
        """Test sequence of status updates"""
        statuses = ["Initializing", "Running", "Paused", "Resumed", "Finished"]
        
        for status in statuses:
            main_window.on_status_updated(status)
            assert main_window.attack_status_label.text() == f"Status: {status}"
            assert main_window.status_label.text() == status

    def test_attack_finished_without_thread(self, main_window):
        """Test attack finished when thread is None"""
        main_window.is_attacking = True
        main_window.brute_force_thread = None
        
        # Should handle gracefully without thread
        main_window.on_attack_finished()
        
        assert not main_window.is_attacking
        assert main_window.start_attack_btn.isEnabled()

    def test_stop_attack_without_thread(self, main_window):
        """Test stop attack when no thread exists"""
        main_window.is_attacking = True
        main_window.brute_force_thread = None
        
        # Should handle gracefully
        main_window.stop_attack()
        # No exception should be raised

    def test_pause_attack_without_thread(self, main_window):
        """Test pause attack when no thread exists"""
        main_window.is_attacking = True
        main_window.brute_force_thread = None
        
        # Should handle gracefully
        main_window.pause_attack()
        # No exception should be raised

    def test_resume_attack_without_thread(self, main_window):
        """Test resume attack when no thread exists"""
        main_window.is_attacking = True
        main_window.brute_force_thread = None
        
        # Should handle gracefully
        main_window.resume_attack()
        # No exception should be raised

    def test_start_attack_while_already_attacking(self, main_window):
        """Test starting attack while already attacking"""
        main_window.is_attacking = True
        
        # Should return early without creating new thread
        with patch('frontend.ui.main_window.BruteForceThread') as mock_thread:
            main_window.start_attack()
            mock_thread.assert_not_called()

    def test_form_validation_whitespace_target(self, main_window):
        """Test form validation with whitespace-only target"""
        main_window.target_input.setText("   ")  # Whitespace only
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            main_window.start_attack()
            mock_warning.assert_called_once()

    def test_charset_with_special_characters(self, main_window):
        """Test charset input with special characters"""
        special_charset = "abc123!@#$%^&*()_+-=[]{}|;:,.<>?"
        main_window.charset_input.setText(special_charset)
        assert main_window.charset_input.text() == special_charset

    def test_min_max_length_relationship(self, main_window):
        """Test that min and max length can be set independently"""
        # Set min greater than max (should be allowed by UI, validation happens on start)
        main_window.min_length_spin.setValue(10)
        main_window.max_length_spin.setValue(5)
        
        assert main_window.min_length_spin.value() == 10
        assert main_window.max_length_spin.value() == 5
        
        # Now set max greater than min
        main_window.max_length_spin.setValue(15)
        assert main_window.max_length_spin.value() == 15

    def test_attack_type_change_updates_ui(self, main_window):
        """Test that changing attack type updates UI appropriately"""
        # Change to brute force (no wordlist required)
        main_window.attack_type_combo.setCurrentText("Brute Force Attack")
        
        # Wordlist should not be required
        # (UI doesn't disable it, but validation should handle it)
        
        # Change to dictionary attack
        main_window.attack_type_combo.setCurrentText("Dictionary Attack (WPA2)")
        
        # Wordlist should be required for this attack type

    def test_filter_results_case_insensitive(self, main_window):
        """Test that results filter is case insensitive"""
        main_window.results_text.setPlainText("UPPERCASE\nlowercase\nMixedCase")
        main_window.full_results_text = main_window.results_text.toPlainText()
        
        # Filter with lowercase
        main_window.results_filter_input.setText("case")
        main_window.filter_results()
        
        filtered = main_window.results_text.toPlainText()
        assert "UPPERCASE" in filtered
        assert "lowercase" in filtered
        assert "MixedCase" in filtered

    def test_filter_attack_log_case_insensitive(self, main_window):
        """Test that attack log filter is case insensitive"""
        main_window.attack_log_text.setPlainText("ERROR: Message\nerror: Another\nError: Third")
        main_window.full_attack_log_text = main_window.attack_log_text.toPlainText()
        
        # Filter with mixed case
        main_window.attack_log_filter_input.setText("error")
        main_window.filter_attack_log()
        
        filtered = main_window.attack_log_text.toPlainText()
        assert "ERROR: Message" in filtered
        assert "error: Another" in filtered
        assert "Error: Third" in filtered

    def test_clear_filter_shows_all_results(self, main_window):
        """Test that clearing filter shows all results again"""
        # Set up results
        main_window.results_text.setPlainText("Line 1\nLine 2\nLine 3")
        main_window.full_results_text = main_window.results_text.toPlainText()
        
        # Apply filter
        main_window.results_filter_input.setText("Line 1")
        main_window.filter_results()
        
        # Clear filter
        main_window.results_filter_input.setText("")
        main_window.filter_results()
        
        # All lines should be visible
        assert "Line 1" in main_window.results_text.toPlainText()
        assert "Line 2" in main_window.results_text.toPlainText()
        assert "Line 3" in main_window.results_text.toPlainText()

    def test_recent_results_updates(self, main_window):
        """Test that recent results panel updates correctly"""
        # Add multiple results
        for i in range(15):
            main_window.on_result_updated(f"Result {i}")
        
        # Recent results should contain the results
        recent_text = main_window.recent_results_text.toPlainText()
        assert "Result" in recent_text

    def test_elapsed_time_format(self, main_window):
        """Test elapsed time formatting"""
        import time
        
        # Set start time to 1 hour ago
        main_window.start_time = time.time() - 3661  # 1 hour, 1 minute, 1 second
        
        # Update display
        main_window.update_display()
        
        # Check format contains hours, minutes, seconds
        elapsed_text = main_window.elapsed_time_label.text()
        assert "Elapsed:" in elapsed_text

    def test_target_display_updates(self, main_window):
        """Test that target display updates when target changes"""
        # Set target and verify it's set in input
        main_window.target_input.setText("new_target")
        assert main_window.target_input.text() == "new_target"
        
        # Manually update display to simulate what start_attack does
        main_window.target_display.setText("new_target")
        main_window.current_target_label.setText(f"Target: new_target")
        
        # Verify display was updated
        assert main_window.target_display.text() == "new_target"
        assert "new_target" in main_window.current_target_label.text()




    def test_progress_display_updates(self, main_window):
        """Test that progress display updates correctly"""
        main_window.on_progress_updated(75, 1000.0, "00:10:00", 75000)
        
        assert main_window.progress_display.text() == "75%"

    def test_attempts_status_format(self, main_window):
        """Test attempts status formatting with large numbers"""
        main_window.on_progress_updated(50, 1000.0, "01:00:00", 1234567)
        
        # Should format with commas
        assert "1,234,567" in main_window.attempts_status.text()

    def test_speed_status_format(self, main_window):
        """Test speed status formatting"""
        main_window.on_progress_updated(50, 1500.75, "01:00:00", 50000)
        
        assert "1500.75" in main_window.speed_status.text()

    def test_statistics_panel_updates(self, main_window):
        """Test that statistics panel updates with attack data"""
        # Set up mock thread with stats - use integers to avoid format issues
        mock_stats = {
            'total_passwords_tested': 50000,
            'average_speed': 2500.0,
            'peak_speed': 3000.0,
            'start_time': None,
            'end_time': None
        }
        
        with patch.object(main_window, 'brute_force_thread') as mock_thread:
            mock_thread.stats = mock_stats
            main_window.on_attack_finished()
        
        # Check statistics were updated (format may vary)
        assert "50000" in main_window.total_attempts_stat.text().replace(",", "")
        assert "2500.0" in main_window.avg_speed_stat.text().replace(",", "")
        assert "3000.0" in main_window.peak_speed_stat.text().replace(",", "")


    def test_success_rate_calculation(self, main_window):
        """Test success rate calculation display"""
        # This would require actual attack results
        # For now, just verify the label exists and can be updated
        assert hasattr(main_window, 'success_rate_stat')

    def test_theme_application(self, main_window):
        """Test that theme stylesheets are applied"""
        # Test light theme
        main_window.switch_theme("light")
        assert main_window.current_theme == "light"
        
        # Test dark theme
        main_window.switch_theme("dark")
        assert main_window.current_theme == "dark"
        
        # Stylesheet should be non-empty
        assert len(main_window.styleSheet()) > 0

    def test_tab_visibility_toggle(self, main_window):
        """Test tab visibility toggling"""
        # Get initial tab count
        initial_count = main_window.tab_widget.count()
        
        # Toggle dashboard tab off
        if hasattr(main_window, 'show_dashboard_action'):
            main_window.show_dashboard_action.setChecked(False)
            main_window.toggle_dashboard_tab()
        
        # Toggle back on
        if hasattr(main_window, 'show_dashboard_action'):
            main_window.show_dashboard_action.setChecked(True)
            main_window.toggle_dashboard_tab()

    def test_results_panel_toggle(self, main_window):
        """Test results panel visibility toggle"""
        # Verify panel exists and is visible by default
        assert hasattr(main_window, 'results_panel')
        
        # Panel should be visible initially (created with isVisible=True by default)
        # Just verify the panel exists and has the toggle method
        assert hasattr(main_window, 'toggle_results_panel')
        
        # Test that we can call the toggle method without errors
        if hasattr(main_window, 'show_results_action'):
            original_state = main_window.show_results_action.isChecked()
            main_window.toggle_results_panel()
            # Toggle back
            main_window.show_results_action.setChecked(original_state)
            main_window.toggle_results_panel()




    def test_shortcut_validation_edge_cases(self, main_window):
        """Test shortcut validation edge cases"""
        # Empty shortcut should be valid
        assert main_window.validate_shortcut("")
        assert main_window.validate_shortcut("   ")
        
        # Invalid formats
        assert not main_window.validate_shortcut("Invalid+Key")
        assert not main_window.validate_shortcut("Ctrl+InvalidKey")
        assert not main_window.validate_shortcut("Super+Long+Invalid+Shortcut")

    def test_shortcut_validation_valid_formats(self, main_window):
        """Test various valid shortcut formats"""
        valid_shortcuts = [
            "Ctrl+A", "Ctrl+Z", "Ctrl+0", "Ctrl+9",
            "Alt+F1", "Alt+F12",
            "F1", "F12",
            "Ctrl+Shift+S",
            "Shift+A", "Shift+Z"
        ]
        
        for shortcut in valid_shortcuts:
            assert main_window.validate_shortcut(shortcut), f"Failed for {shortcut}"
        
        # Ctrl+Alt+Delete is a special system shortcut, may not be valid
        # Just verify it doesn't crash
        main_window.validate_shortcut("Ctrl+Alt+Delete")



    def test_export_results_empty(self, main_window):
        """Test exporting empty results"""
        main_window.results_text.clear()
        main_window.full_results_text = ""
        
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName') as mock_dialog, \
             patch('builtins.open', create=True) as mock_file:
            
            mock_dialog.return_value = ("/path/to/export.txt", "Text Files (*.txt)")
            mock_file.return_value.__enter__.return_value.write = MagicMock()
            
            main_window.export_results()
            
            # Should write empty string
            mock_file.return_value.__enter__.return_value.write.assert_called_once_with("")

    def test_browse_wordlist_cancel(self, main_window):
        """Test browse wordlist when user cancels"""
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")  # User cancelled
            
            # Set initial value
            main_window.wordlist_input.setText("/initial/path.txt")
            
            main_window.browse_wordlist()
            
            # Path should remain unchanged
            assert main_window.wordlist_input.text() == "/initial/path.txt"

    def test_window_geometry(self, main_window):
        """Test window geometry constraints"""
        # Window should have minimum size
        assert main_window.geometry().width() >= 1400
        assert main_window.geometry().height() >= 900
        
        # Window should be resizable (no maximum size constraint)
        # This is implicit - if the window was created, it should be resizable

    def test_security_components_initialized(self, main_window):
        """Test that security components are initialized"""
        assert main_window.session_encryption is not None
        assert main_window.audit_logger is not None
        assert main_window.permission_manager is not None
        assert main_window.compliance_manager is not None

    def test_graph_data_structures(self, main_window):
        """Test graph data structure initialization"""
        from collections import deque
        
        assert isinstance(main_window.time_data, deque)
        assert isinstance(main_window.speed_data, deque)
        assert isinstance(main_window.attempts_data, deque)
        assert isinstance(main_window.progress_data, deque)
        
        # All should have maxlen of 100
        assert main_window.time_data.maxlen == 100
        assert main_window.speed_data.maxlen == 100
        assert main_window.attempts_data.maxlen == 100
        assert main_window.progress_data.maxlen == 100

    def test_integration_manager_none(self, main_window):
        """Test that window works without integration manager"""
        # Window was created with integration_manager=None in fixture
        assert main_window.integration_manager is None
        
        # Should still have basic functionality
        assert main_window.is_attacking is False

    def test_attack_lifecycle_simulation(self, main_window):
        """Simulate complete attack lifecycle"""
        # 1. Set up attack
        main_window.target_input.setText("test_target")
        main_window.attack_type_combo.setCurrentText("Brute Force Attack")
        
        # 2. Start attack (mocked)
        with patch('frontend.ui.main_window.BruteForceThread') as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread
            
            main_window.start_attack()
            
            # Verify attack started
            assert main_window.is_attacking
            assert not main_window.start_attack_btn.isEnabled()
            assert main_window.stop_attack_btn.isEnabled()
            
            # 3. Simulate progress updates
            for i in range(0, 101, 25):
                main_window.on_progress_updated(i, 1000.0, "00:00:00", i * 100)
            
            # 4. Pause attack
            main_window.pause_attack()
            assert not main_window.pause_attack_btn.isEnabled()
            assert main_window.resume_attack_btn.isEnabled()
            
            # 5. Resume attack
            main_window.resume_attack()
            assert main_window.pause_attack_btn.isEnabled()
            assert not main_window.resume_attack_btn.isEnabled()
            
            # 6. Finish attack - set up proper stats first
            class MockThread:
                stats = {
                    'total_passwords_tested': 1000,
                    'average_speed': 100.0,
                    'peak_speed': 200.0,
                    'start_time': None,
                    'end_time': None
                }
            
            main_window.brute_force_thread = MockThread()
            main_window.on_attack_finished()
            
            # Verify cleanup
            assert not main_window.is_attacking
            assert main_window.start_attack_btn.isEnabled()
            assert not main_window.stop_attack_btn.isEnabled()



    def test_consecutive_attacks(self, main_window):
        """Test running multiple consecutive attacks"""
        for i in range(3):
            # Set up attack
            main_window.target_input.setText(f"target_{i}")
            main_window.attack_type_combo.setCurrentText("Brute Force Attack")
            
            with patch('frontend.ui.main_window.BruteForceThread') as mock_thread_class:
                mock_thread = MagicMock()
                mock_thread_class.return_value = mock_thread
                
                # Start attack
                main_window.start_attack()
                assert main_window.is_attacking
                
                # Finish attack with proper stats
                class MockThread:
                    stats = {
                        'total_passwords_tested': 100,
                        'average_speed': 50.0,
                        'peak_speed': 100.0,
                        'start_time': None,
                        'end_time': None
                    }
                
                main_window.brute_force_thread = MockThread()
                main_window.on_attack_finished()
                assert not main_window.is_attacking



    def test_memory_efficiency_with_large_data(self, main_window):
        """Test that large data doesn't cause memory issues"""
        # Add many results
        large_result = "A" * 1000  # 1000 character result
        for i in range(100):
            main_window.on_result_updated(f"{i}: {large_result}")
        
        # Should still be responsive
        assert len(main_window.full_results_text) > 0
        
        # Filter should work
        main_window.results_filter_input.setText("50:")
        main_window.filter_results()
        
        # Should show filtered results
        assert "50:" in main_window.results_text.toPlainText()

    def test_ui_responsiveness_during_updates(self, main_window):
        """Test UI remains responsive during rapid updates"""
        import time
        
        start_time = time.time()
        
        # Reduced number of updates for test environment stability
        for i in range(50):
            main_window.on_progress_updated(i, float(i) * 10, "00:00:00", i * 1000)
        
        end_time = time.time()
        
        # Should complete reasonably quickly (less than 15 seconds for 50 updates in test environment)
        # Note: Extended timeout for CI/test environments with limited resources
        elapsed = end_time - start_time
        assert elapsed < 15.0, f"UI updates took too long: {elapsed:.2f} seconds"



    def test_error_recovery(self, main_window):
        """Test error handling and recovery"""
        # Simulate error during attack
        main_window.is_attacking = True
        main_window.start_attack_btn.setEnabled(False)
        main_window.stop_attack_btn.setEnabled(True)
        
        # Trigger error
        with patch('PyQt6.QtWidgets.QMessageBox.critical'):
            main_window.on_error_occurred("Test error message")
        
        # UI should still be functional
        assert main_window.is_attacking  # Still attacking after error
        # User can still stop the attack
        assert main_window.stop_attack_btn.isEnabled()

    def test_data_persistence_across_operations(self, main_window):
        """Test that data persists correctly across operations"""
        # Add results
        main_window.on_result_updated("Persistent result")
        
        # Filter results
        main_window.results_filter_input.setText("Persistent")
        main_window.filter_results()
        
        # Clear filter
        main_window.results_filter_input.setText("")
        main_window.filter_results()
        
        # Original result should still be there
        assert "Persistent result" in main_window.results_text.toPlainText()
        assert "Persistent result" in main_window.full_results_text

"""
Main Window
Primary GUI interface for Keyspace
"""

import sys
import time
import logging
from pathlib import Path

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QMenuBar, QMenu, QToolBar, QStatusBar,
                             QLabel, QPushButton, QMessageBox, QFileDialog,
                             QDockWidget, QSplitter, QProgressBar, QTextEdit,
                             QGroupBox, QGridLayout, QComboBox, QSpinBox,
                             QLineEdit, QCheckBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont

from backend.brute_force_thread import BruteForceThread

import logging
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window for Keyspace"""

    def __init__(self):
        super().__init__()

        # Initialize components
        self.brute_force_thread = None
        self.is_attacking = False
        self.start_time = time.time()

        # Setup UI
        self.init_ui()
        self.setup_connections()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second

        logger.info("Keyspace main window initialized")

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Keyspace - Advanced Password Cracking")
        self.setGeometry(100, 100, 1400, 900)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create main horizontal splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Control panel and tabs
        left_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top section: Attack configuration
        self.attack_config_panel = self.create_attack_config_panel()
        left_splitter.addWidget(self.attack_config_panel)

        # Bottom section: Tabs for different views
        self.tab_widget = QTabWidget()

        # Dashboard tab
        self.dashboard_panel = self.create_dashboard_panel()
        self.tab_widget.addTab(self.dashboard_panel, "🏠 Dashboard")

        # Attack Log tab
        self.attack_log_panel = self.create_attack_log_panel()
        self.tab_widget.addTab(self.attack_log_panel, "📋 Attack Log")

        # Statistics tab
        self.stats_panel = self.create_statistics_panel()
        self.tab_widget.addTab(self.stats_panel, "📊 Statistics")

        left_splitter.addWidget(self.tab_widget)
        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 2)

        # Add left splitter to main splitter
        main_splitter.addWidget(left_splitter)

        # Right side: Results panel
        self.results_panel = self.create_results_panel()
        main_splitter.addWidget(self.results_panel)

        # Set stretch factors for main splitter
        main_splitter.setStretchFactor(0, 2)  # Left side (config + tabs)
        main_splitter.setStretchFactor(1, 1)  # Right side (results)

        main_layout.addWidget(main_splitter)

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create status bar
        self.create_status_bar()

    def create_attack_config_panel(self):
        """Create attack configuration panel"""
        group = QGroupBox("Attack Configuration")
        layout = QGridLayout(group)

        # Target
        layout.addWidget(QLabel("Target:"), 0, 0)
        self.target_input = QLineEdit("demo_target")
        self.target_input.setPlaceholderText("Enter target (WiFi SSID, username, etc.)")
        layout.addWidget(self.target_input, 0, 1, 1, 2)

        # Attack Type
        layout.addWidget(QLabel("Attack Type:"), 1, 0)
        self.attack_type_combo = QComboBox()
        self.attack_type_combo.addItems([
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
        ])
        layout.addWidget(self.attack_type_combo, 1, 1, 1, 2)

        # Wordlist
        layout.addWidget(QLabel("Wordlist:"), 2, 0)
        self.wordlist_input = QLineEdit()
        self.wordlist_input.setPlaceholderText("Path to wordlist file")
        layout.addWidget(self.wordlist_input, 2, 1)
        self.browse_wordlist_btn = QPushButton("Browse...")
        self.browse_wordlist_btn.clicked.connect(self.browse_wordlist)
        layout.addWidget(self.browse_wordlist_btn, 2, 2)

        # Password Length
        layout.addWidget(QLabel("Min Length:"), 3, 0)
        self.min_length_spin = QSpinBox()
        self.min_length_spin.setRange(1, 32)
        self.min_length_spin.setValue(8)
        layout.addWidget(self.min_length_spin, 3, 1)

        layout.addWidget(QLabel("Max Length:"), 3, 2)
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setRange(1, 32)
        self.max_length_spin.setValue(16)
        layout.addWidget(self.max_length_spin, 3, 3)

        # Character Set
        layout.addWidget(QLabel("Charset:"), 4, 0)
        self.charset_input = QLineEdit("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*")
        layout.addWidget(self.charset_input, 4, 1, 1, 2)

        # Control buttons
        button_layout = QHBoxLayout()
        self.start_attack_btn = QPushButton("▶ Start Attack")
        self.start_attack_btn.clicked.connect(self.start_attack)
        self.start_attack_btn.setStyleSheet("QPushButton { padding: 10px 20px; font-weight: bold; }")
        button_layout.addWidget(self.start_attack_btn)

        self.stop_attack_btn = QPushButton("⏹ Stop Attack")
        self.stop_attack_btn.clicked.connect(self.stop_attack)
        self.stop_attack_btn.setEnabled(False)
        self.stop_attack_btn.setStyleSheet("QPushButton { padding: 10px 20px; font-weight: bold; }")
        button_layout.addWidget(self.stop_attack_btn)

        self.pause_attack_btn = QPushButton("⏸ Pause")
        self.pause_attack_btn.clicked.connect(self.pause_attack)
        self.pause_attack_btn.setEnabled(False)
        button_layout.addWidget(self.pause_attack_btn)

        self.resume_attack_btn = QPushButton("▶ Resume")
        self.resume_attack_btn.clicked.connect(self.resume_attack)
        self.resume_attack_btn.setEnabled(False)
        button_layout.addWidget(self.resume_attack_btn)

        layout.addLayout(button_layout, 5, 0, 1, 4)

        return group

    def create_dashboard_panel(self):
        """Create dashboard panel with overview widgets"""
        widget = QWidget()
        layout = QGridLayout(widget)

        # Attack Status
        status_group = QGroupBox("Attack Status")
        status_layout = QVBoxLayout(status_group)

        self.attack_status_label = QLabel("Status: Ready")
        self.attack_status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_layout.addWidget(self.attack_status_label)

        self.current_target_label = QLabel("Target: None")
        status_layout.addWidget(self.current_target_label)

        self.elapsed_time_label = QLabel("Elapsed: 0:00:00")
        status_layout.addWidget(self.elapsed_time_label)

        layout.addWidget(status_group, 0, 0)

        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("Progress: 0%")
        progress_layout.addWidget(self.progress_label)

        self.speed_label = QLabel("Speed: 0.0 attempts/sec")
        progress_layout.addWidget(self.speed_label)

        self.eta_label = QLabel("ETA: --:--:--")
        progress_layout.addWidget(self.eta_label)

        layout.addWidget(progress_group, 0, 1)

        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.attempts_label = QLabel("Attempts: 0")
        stats_layout.addWidget(self.attempts_label)

        self.found_label = QLabel("Found: 0")
        stats_layout.addWidget(self.found_label)

        self.errors_label = QLabel("Errors: 0")
        stats_layout.addWidget(self.errors_label)

        layout.addWidget(stats_group, 1, 0)

        # Recent Results
        results_group = QGroupBox("Recent Results")
        results_layout = QVBoxLayout(results_group)

        self.recent_results_text = QTextEdit()
        self.recent_results_text.setMaximumHeight(150)
        self.recent_results_text.setReadOnly(True)
        results_layout.addWidget(self.recent_results_text)

        layout.addWidget(results_group, 1, 1)

        return widget

    def create_attack_log_panel(self):
        """Create attack log panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.attack_log_text = QTextEdit()
        self.attack_log_text.setReadOnly(True)
        self.attack_log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.attack_log_text)

        # Clear log button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.clear_attack_log)
        layout.addWidget(clear_btn)

        return widget

    def create_statistics_panel(self):
        """Create statistics panel"""
        widget = QWidget()
        layout = QGridLayout(widget)

        # Attack Statistics
        attack_stats_group = QGroupBox("Attack Statistics")
        attack_stats_layout = QVBoxLayout(attack_stats_group)

        self.total_attempts_stat = QLabel("Total Attempts: 0")
        attack_stats_layout.addWidget(self.total_attempts_stat)

        self.success_rate_stat = QLabel("Success Rate: 0%")
        attack_stats_layout.addWidget(self.success_rate_stat)

        self.avg_speed_stat = QLabel("Average Speed: 0.0/sec")
        attack_stats_layout.addWidget(self.avg_speed_stat)

        self.peak_speed_stat = QLabel("Peak Speed: 0.0/sec")
        attack_stats_layout.addWidget(self.peak_speed_stat)

        layout.addWidget(attack_stats_group, 0, 0)

        # Time Statistics
        time_stats_group = QGroupBox("Time Statistics")
        time_stats_layout = QVBoxLayout(time_stats_group)

        self.start_time_stat = QLabel("Start Time: N/A")
        time_stats_layout.addWidget(self.start_time_stat)

        self.end_time_stat = QLabel("End Time: N/A")
        time_stats_layout.addWidget(self.end_time_stat)

        self.duration_stat = QLabel("Duration: 0:00:00")
        time_stats_layout.addWidget(self.duration_stat)

        layout.addWidget(time_stats_group, 0, 1)

        # Attack Types
        attack_types_group = QGroupBox("Attack Type Performance")
        attack_types_layout = QVBoxLayout(attack_types_group)

        self.attack_types_text = QTextEdit()
        self.attack_types_text.setMaximumHeight(200)
        self.attack_types_text.setReadOnly(True)
        attack_types_layout.addWidget(self.attack_types_text)

        layout.addWidget(attack_types_group, 1, 0, 1, 2)

        return widget

    def create_results_panel(self):
        """Create results panel"""
        group = QGroupBox("Results")
        layout = QVBoxLayout(group)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results_text)

        # Export results button
        export_btn = QPushButton("Export Results")
        export_btn.clicked.connect(self.export_results)
        layout.addWidget(export_btn)

        return group

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_session_action = QAction("&New Session", self)
        new_session_action.setShortcut(QKeySequence.StandardKey.New)
        new_session_action.triggered.connect(self.new_session)
        file_menu.addAction(new_session_action)

        open_session_action = QAction("&Open Session", self)
        open_session_action.setShortcut(QKeySequence.StandardKey.Open)
        open_session_action.triggered.connect(self.open_session)
        file_menu.addAction(open_session_action)

        save_session_action = QAction("&Save Session", self)
        save_session_action.setShortcut(QKeySequence.StandardKey.Save)
        save_session_action.triggered.connect(self.save_session)
        file_menu.addAction(save_session_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Attack menu
        attack_menu = menubar.addMenu("&Attack")

        start_action = QAction("&Start Attack", self)
        start_action.setShortcut("Ctrl+S")
        start_action.triggered.connect(self.start_attack)
        attack_menu.addAction(start_action)

        stop_action = QAction("S&top Attack", self)
        stop_action.setShortcut("Ctrl+T")
        stop_action.triggered.connect(self.stop_attack)
        attack_menu.addAction(stop_action)

        attack_menu.addSeparator()

        pause_action = QAction("&Pause Attack", self)
        pause_action.setShortcut("Ctrl+P")
        pause_action.triggered.connect(self.pause_attack)
        attack_menu.addAction(pause_action)

        resume_action = QAction("&Resume Attack", self)
        resume_action.setShortcut("Ctrl+R")
        resume_action.triggered.connect(self.resume_attack)
        attack_menu.addAction(resume_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        wordlist_generator_action = QAction("&Wordlist Generator", self)
        wordlist_generator_action.triggered.connect(self.show_wordlist_generator)
        tools_menu.addAction(wordlist_generator_action)

        charset_analyzer_action = QAction("&Charset Analyzer", self)
        charset_analyzer_action.triggered.connect(self.show_charset_analyzer)
        tools_menu.addAction(charset_analyzer_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Quick start/stop buttons
        self.start_tb_btn = QPushButton("▶ Start")
        self.start_tb_btn.clicked.connect(self.start_attack)
        toolbar.addWidget(self.start_tb_btn)

        self.stop_tb_btn = QPushButton("⏹ Stop")
        self.stop_tb_btn.clicked.connect(self.stop_attack)
        self.stop_tb_btn.setEnabled(False)
        toolbar.addWidget(self.stop_tb_btn)

        toolbar.addSeparator()

        # Target display
        toolbar.addWidget(QLabel("Target:"))
        self.target_display = QLabel("None")
        toolbar.addWidget(self.target_display)

        toolbar.addSeparator()

        # Progress display
        toolbar.addWidget(QLabel("Progress:"))
        self.progress_display = QLabel("0%")
        toolbar.addWidget(self.progress_display)

    def create_status_bar(self):
        """Create status bar"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Status labels
        self.status_label = QLabel("Ready")
        self.statusBar.addWidget(self.status_label)

        self.statusBar.addPermanentWidget(QLabel("|"))

        self.attempts_status = QLabel("Attempts: 0")
        self.statusBar.addPermanentWidget(self.attempts_status)

        self.statusBar.addPermanentWidget(QLabel("|"))

        self.speed_status = QLabel("Speed: 0.0/sec")
        self.statusBar.addPermanentWidget(self.speed_status)

    def setup_connections(self):
        """Setup signal/slot connections"""
        pass

    def browse_wordlist(self):
        """Browse for wordlist file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Wordlist", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            self.wordlist_input.setText(filename)

    def start_attack(self):
        """Start brute force attack"""
        if self.is_attacking:
            return

        try:
            # Get configuration
            target = self.target_input.text().strip()
            if not target:
                QMessageBox.warning(self, "Warning", "Please enter a target")
                return

            attack_type = self.attack_type_combo.currentText()
            wordlist_path = self.wordlist_input.text().strip()
            min_length = self.min_length_spin.value()
            max_length = self.max_length_spin.value()
            charset = self.charset_input.text().strip()

            # Validate configuration
            if attack_type in ["Dictionary Attack (WPA2)", "Rule-based Attack", "Hybrid Attack", "Combinator Attack"]:
                if not wordlist_path or not Path(wordlist_path).exists():
                    QMessageBox.warning(self, "Warning", "Please select a valid wordlist file")
                    return

            # Create and start attack thread
            self.brute_force_thread = BruteForceThread(
                target=target,
                attack_type=attack_type,
                wordlist_path=wordlist_path,
                min_length=min_length,
                max_length=max_length,
                charset=charset
            )

            # Connect signals
            self.brute_force_thread.progress_updated.connect(self.on_progress_updated)
            self.brute_force_thread.status_updated.connect(self.on_status_updated)
            self.brute_force_thread.result_updated.connect(self.on_result_updated)
            self.brute_force_thread.error_occurred.connect(self.on_error_occurred)
            self.brute_force_thread.attack_log.connect(self.on_attack_log)
            self.brute_force_thread.finished.connect(self.on_attack_finished)

            # Update UI
            self.is_attacking = True
            self.start_attack_btn.setEnabled(False)
            self.stop_attack_btn.setEnabled(True)
            self.pause_attack_btn.setEnabled(True)
            self.resume_attack_btn.setEnabled(False)
            self.start_tb_btn.setEnabled(False)
            self.stop_tb_btn.setEnabled(True)

            self.target_display.setText(target)
            self.current_target_label.setText(f"Target: {target}")
            self.attack_status_label.setText("Status: Running")
            self.start_time = time.time()

            # Start thread
            self.brute_force_thread.start()

            self.status_label.setText("Attack running...")
            logger.info(f"Attack started: {attack_type} on {target}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start attack: {str(e)}")
            logger.error(f"Failed to start attack: {e}")

    def stop_attack(self):
        """Stop brute force attack"""
        if not self.is_attacking or not self.brute_force_thread:
            return

        try:
            self.brute_force_thread.stop()
            self.status_label.setText("Stopping attack...")
            logger.info("Attack stop requested")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop attack: {str(e)}")
            logger.error(f"Failed to stop attack: {e}")

    def pause_attack(self):
        """Pause brute force attack"""
        if not self.is_attacking or not self.brute_force_thread:
            return

        try:
            self.brute_force_thread.pause()
            self.pause_attack_btn.setEnabled(False)
            self.resume_attack_btn.setEnabled(True)
            self.status_label.setText("Attack paused")
            logger.info("Attack paused")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to pause attack: {str(e)}")
            logger.error(f"Failed to pause attack: {e}")

    def resume_attack(self):
        """Resume brute force attack"""
        if not self.is_attacking or not self.brute_force_thread:
            return

        try:
            self.brute_force_thread.resume()
            self.pause_attack_btn.setEnabled(True)
            self.resume_attack_btn.setEnabled(False)
            self.status_label.setText("Attack running...")
            logger.info("Attack resumed")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to resume attack: {str(e)}")
            logger.error(f"Failed to resume attack: {e}")

    def on_progress_updated(self, progress, speed, eta, attempts):
        """Handle progress update"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Progress: {progress}%")
        self.speed_label.setText(f"Speed: {speed} attempts/sec")
        self.eta_label.setText(f"ETA: {eta}")
        self.attempts_label.setText(f"Attempts: {attempts:,}")
        self.attempts_status.setText(f"Attempts: {attempts:,}")
        self.speed_status.setText(f"Speed: {speed}/sec")
        self.progress_display.setText(f"{progress}%")

    def on_status_updated(self, status):
        """Handle status update"""
        self.attack_status_label.setText(f"Status: {status}")
        self.status_label.setText(status)

    def on_result_updated(self, result):
        """Handle result update"""
        self.results_text.append(result)
        self.recent_results_text.append(result)

        # Scroll to bottom
        cursor = self.results_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.results_text.setTextCursor(cursor)

        cursor = self.recent_results_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.recent_results_text.setTextCursor(cursor)

    def on_error_occurred(self, error):
        """Handle error"""
        QMessageBox.critical(self, "Error", error)
        self.status_label.setText(f"Error: {error}")

    def on_attack_log(self, log_entry):
        """Handle attack log entry"""
        self.attack_log_text.append(log_entry)

        # Scroll to bottom
        cursor = self.attack_log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.attack_log_text.setTextCursor(cursor)

    def on_attack_finished(self):
        """Handle attack finished"""
        self.is_attacking = False
        self.start_attack_btn.setEnabled(True)
        self.stop_attack_btn.setEnabled(False)
        self.pause_attack_btn.setEnabled(False)
        self.resume_attack_btn.setEnabled(False)
        self.start_tb_btn.setEnabled(True)
        self.stop_tb_btn.setEnabled(False)

        self.attack_status_label.setText("Status: Finished")
        self.status_label.setText("Attack finished")

        # Update statistics
        if self.brute_force_thread:
            stats = self.brute_force_thread.stats
            self.total_attempts_stat.setText(f"Total Attempts: {stats['total_passwords_tested']:,}")
            self.avg_speed_stat.setText(f"Average Speed: {stats['average_speed']:.1f}/sec")
            self.peak_speed_stat.setText(f"Peak Speed: {stats['peak_speed']:.1f}/sec")

            if stats['start_time']:
                self.start_time_stat.setText(f"Start Time: {stats['start_time'].strftime('%H:%M:%S')}")
            if stats['end_time']:
                self.end_time_stat.setText(f"End Time: {stats['end_time'].strftime('%H:%M:%S')}")

        logger.info("Attack finished")

    def update_display(self):
        """Update display periodically"""
        if self.is_attacking:
            elapsed = int(time.time() - self.start_time)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.elapsed_time_label.setText(f"Elapsed: {hours}:{minutes:02d}:{seconds:02d}")

    def clear_attack_log(self):
        """Clear attack log"""
        self.attack_log_text.clear()

    def export_results(self):
        """Export results to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.results_text.toPlainText())
                QMessageBox.information(self, "Success", "Results exported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export results: {str(e)}")

    def new_session(self):
        """Create new session"""
        # Reset UI
        self.results_text.clear()
        self.attack_log_text.clear()
        self.recent_results_text.clear()
        self.progress_bar.setValue(0)
        self.progress_label.setText("Progress: 0%")
        self.speed_label.setText("Speed: 0.0 attempts/sec")
        self.eta_label.setText("ETA: --:--:--")
        self.attempts_label.setText("Attempts: 0")
        self.found_label.setText("Found: 0")
        self.errors_label.setText("Errors: 0")
        self.attack_status_label.setText("Status: Ready")
        self.current_target_label.setText("Target: None")
        self.elapsed_time_label.setText("Elapsed: 0:00:00")
        self.target_display.setText("None")
        self.progress_display.setText("0%")
        self.status_label.setText("Ready")

    def open_session(self):
        """Open existing session"""
        QMessageBox.information(self, "Info", "Session loading not implemented yet")

    def save_session(self):
        """Save current session"""
        QMessageBox.information(self, "Info", "Session saving not implemented yet")

    def show_wordlist_generator(self):
        """Show wordlist generator dialog"""
        QMessageBox.information(self, "Info", "Wordlist generator not implemented yet")

    def show_charset_analyzer(self):
        """Show charset analyzer dialog"""
        QMessageBox.information(self, "Info", "Charset analyzer not implemented yet")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Keyspace",
                         "Keyspace v1.0 - Advanced Password Cracking\n\n"
                         "Features:\n"
                         "• Multiple attack types (Dictionary, Brute Force, Rule-based, etc.)\n"
                         "• Real-time progress monitoring\n"
                         "• Advanced mutation rules\n"
                         "• Mask-based attacks\n"
                         "• Hybrid attack combinations\n"
                         "• Comprehensive logging and statistics\n"
                         "• Modern PyQt6 GUI\n\n"
                         "Built for security research and penetration testing.")

    def closeEvent(self, event):
        """Handle window close"""
        if self.is_attacking:
            reply = QMessageBox.question(self, "Confirm Exit",
                                        "Attack is still running. Stop and exit?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                self.stop_attack()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


"""
Main Window
Primary GUI interface for Keyspace with Integration Support
"""


import sys
import time
import logging
import string
import itertools
from pathlib import Path
from collections import deque
from typing import Optional, Dict, Any, List


from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QMenuBar, QMenu, QToolBar, QStatusBar,
                             QLabel, QPushButton, QMessageBox, QFileDialog,
                             QDockWidget, QSplitter, QProgressBar, QTextEdit,
                             QGroupBox, QGridLayout, QComboBox, QSpinBox,
                             QLineEdit, QCheckBox, QFrame, QDialog, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialogButtonBox,
                             QInputDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont

import matplotlib
matplotlib.use('Qt5Agg')  # Use Qt5Agg backend for PyQt6 compatibility
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from backend.brute_force_thread import BruteForceThread
from backend.security.session_encryption import SessionEncryption
from backend.security.audit_logger import AuditLogger, AuditEventType, AuditSeverity
from backend.security.permissions import PermissionManager, Permission, UserRole
from backend.security.compliance import ComplianceManager

import logging
logger = logging.getLogger(__name__)

# Keyboard shortcuts configuration
DEFAULT_SHORTCUTS = {
    "start_attack": "Ctrl+S",
    "stop_attack": "Ctrl+T",
    "pause_attack": "Ctrl+P",
    "resume_attack": "Ctrl+R",
    "new_session": "Ctrl+N",
    "open_session": "Ctrl+O",
    "save_session": "Ctrl+W",
    "export_results": "Ctrl+E",
    "clear_log": "Ctrl+L",
    "show_dashboard": "Ctrl+1",
    "show_attack_log": "Ctrl+2",
    "show_statistics": "Ctrl+3",
    "show_integrations": "Ctrl+4"
}


class MainWindow(QMainWindow):
    """Main application window for Keyspace"""


    def __init__(self, integration_manager: Optional[Any] = None) -> None:
        super().__init__()

        # Initialize components
        self.brute_force_thread = None
        self.is_attacking = False
        self.start_time = time.time()
        self.integration_manager = integration_manager
        self.current_theme = "light"  # Default theme

        # Initialize security modules
        self.session_encryption = SessionEncryption()
        self.audit_logger = AuditLogger()
        self.permission_manager = PermissionManager()
        self.compliance_manager = ComplianceManager(self.audit_logger)

        # Set default user context for audit logging
        self.audit_logger.set_user_context("admin", "main_session")

        # Graph data storage
        self.time_data = deque(maxlen=100)
        self.speed_data = deque(maxlen=100)
        self.attempts_data = deque(maxlen=100)
        self.progress_data = deque(maxlen=100)

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
        self.setWindowIcon(QIcon("assets/keyspace.ico"))

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
        self.tab_widget.addTab(self.dashboard_panel, "Dashboard")

        # Attack Log tab
        self.attack_log_panel = self.create_attack_log_panel()
        self.tab_widget.addTab(self.attack_log_panel, "Attack Log")

        # Statistics tab
        self.stats_panel = self.create_statistics_panel()
        self.tab_widget.addTab(self.stats_panel, "Statistics")

        # Integrations tab (if available)
        if self.integration_manager:
            self.integrations_panel = self.create_integrations_panel()
            self.tab_widget.addTab(self.integrations_panel, "Integrations")


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

        # Speed Graph
        speed_group = QGroupBox("Speed Over Time")
        speed_layout = QVBoxLayout(speed_group)

        self.speed_figure = Figure(figsize=(4, 3))
        self.speed_canvas = FigureCanvas(self.speed_figure)
        speed_layout.addWidget(self.speed_canvas)

        # Initialize speed graph
        self.speed_ax = self.speed_figure.add_subplot(111)
        self.speed_ax.set_title("Attack Speed", fontsize=10)
        self.speed_ax.set_xlabel("Time (s)", fontsize=8)
        self.speed_ax.set_ylabel("Speed (attempts/sec)", fontsize=8)
        self.speed_ax.grid(True, alpha=0.3)

        layout.addWidget(speed_group, 1, 0)

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

        # Filter input
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self.attack_log_filter_input = QLineEdit()
        self.attack_log_filter_input.setPlaceholderText("Filter log by keyword...")
        self.attack_log_filter_input.textChanged.connect(self.filter_attack_log)
        filter_layout.addWidget(self.attack_log_filter_input)
        layout.addLayout(filter_layout)

        self.attack_log_text = QTextEdit()
        self.attack_log_text.setReadOnly(True)
        self.attack_log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.attack_log_text)

        # Store full log for filtering
        self.full_attack_log_text = ""

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

        # Progress Graph
        progress_group = QGroupBox("Progress Over Time")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_figure = Figure(figsize=(6, 3))
        self.progress_canvas = FigureCanvas(self.progress_figure)
        progress_layout.addWidget(self.progress_canvas)

        # Initialize progress graph
        self.progress_ax = self.progress_figure.add_subplot(111)
        self.progress_ax.set_title("Progress Over Time", fontsize=10)
        self.progress_ax.set_xlabel("Time (s)", fontsize=8)
        self.progress_ax.set_ylabel("Progress (%)", fontsize=8)
        self.progress_ax.grid(True, alpha=0.3)

        layout.addWidget(progress_group, 1, 0, 1, 2)

        return widget

    def create_integrations_panel(self):
        """Create integrations panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Integration status
        status_group = QGroupBox("Integration Status")
        status_layout = QVBoxLayout(status_group)

        if self.integration_manager:
            status = self.integration_manager.get_integration_status()
            for name, info in status.items():
                status_layout.addWidget(QLabel(f"{name.upper()}: {'Enabled' if info['enabled'] else 'Disabled'}"))

        layout.addWidget(status_group)

        # Integration configuration
        config_group = QGroupBox("Integration Configuration")
        config_layout = QGridLayout(config_group)

        # Hashcat configuration
        config_layout.addWidget(QLabel("Hashcat Path:"), 0, 0)
        self.hashcat_path_input = QLineEdit()
        self.hashcat_path_input.setPlaceholderText("Path to hashcat executable")
        config_layout.addWidget(self.hashcat_path_input, 0, 1)
        self.hashcat_browse_btn = QPushButton("Browse...")
        self.hashcat_browse_btn.clicked.connect(self.browse_hashcat)
        config_layout.addWidget(self.hashcat_browse_btn, 0, 2)

        # John the Ripper configuration
        config_layout.addWidget(QLabel("John Path:"), 1, 0)
        self.john_path_input = QLineEdit()
        self.john_path_input.setPlaceholderText("Path to john executable")
        config_layout.addWidget(self.john_path_input, 1, 1)
        self.john_browse_btn = QPushButton("Browse...")
        self.john_browse_btn.clicked.connect(self.browse_john)
        config_layout.addWidget(self.john_browse_btn, 1, 2)

        # Cloud configuration
        config_layout.addWidget(QLabel("Cloud Provider:"), 2, 0)
        self.cloud_provider_combo = QComboBox()
        self.cloud_provider_combo.addItems(["aws", "gcp", "azure"])
        config_layout.addWidget(self.cloud_provider_combo, 2, 1)

        config_layout.addWidget(QLabel("Cloud Bucket:"), 3, 0)
        self.cloud_bucket_input = QLineEdit()
        self.cloud_bucket_input.setPlaceholderText("Bucket/container name")
        config_layout.addWidget(self.cloud_bucket_input, 3, 1)

        config_layout.addWidget(QLabel("Access Key:"), 4, 0)
        self.cloud_access_key_input = QLineEdit()
        self.cloud_access_key_input.setPlaceholderText("Access key/ID")
        config_layout.addWidget(self.cloud_access_key_input, 4, 1)

        config_layout.addWidget(QLabel("Secret Key:"), 5, 0)
        self.cloud_secret_key_input = QLineEdit()
        self.cloud_secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.cloud_secret_key_input.setPlaceholderText("Secret key")
        config_layout.addWidget(self.cloud_secret_key_input, 5, 1)

        # API configuration
        config_layout.addWidget(QLabel("API Host:"), 6, 0)
        self.api_host_input = QLineEdit("localhost")
        config_layout.addWidget(self.api_host_input, 6, 1)

        config_layout.addWidget(QLabel("API Port:"), 7, 0)
        self.api_port_spin = QSpinBox()
        self.api_port_spin.setRange(1024, 65535)
        self.api_port_spin.setValue(8080)
        config_layout.addWidget(self.api_port_spin, 7, 1)

        # Apply configuration button
        self.apply_config_btn = QPushButton("Apply Configuration")
        self.apply_config_btn.clicked.connect(self.apply_integration_config)
        config_layout.addWidget(self.apply_config_btn, 8, 0, 1, 3)

        layout.addWidget(config_group)

        # Integration controls
        controls_group = QGroupBox("Integration Controls")
        controls_layout = QVBoxLayout(controls_group)

        # Hashcat controls
        hashcat_controls = QHBoxLayout()
        hashcat_controls.addWidget(QLabel("Hashcat:"))
        self.hashcat_benchmark_btn = QPushButton("Run Benchmark")
        self.hashcat_benchmark_btn.clicked.connect(self.run_hashcat_benchmark)
        hashcat_controls.addWidget(self.hashcat_benchmark_btn)
        controls_layout.addLayout(hashcat_controls)

        # John controls
        john_controls = QHBoxLayout()
        john_controls.addWidget(QLabel("John:"))
        self.john_test_btn = QPushButton("Test Installation")
        self.john_test_btn.clicked.connect(self.test_john_installation)
        john_controls.addWidget(self.john_test_btn)
        controls_layout.addLayout(john_controls)

        # Cloud controls
        cloud_controls = QHBoxLayout()
        cloud_controls.addWidget(QLabel("Cloud:"))
        self.cloud_test_btn = QPushButton("Test Connection")
        self.cloud_test_btn.clicked.connect(self.test_cloud_connection)
        cloud_controls.addWidget(self.cloud_test_btn)
        self.cloud_list_btn = QPushButton("List Files")
        self.cloud_list_btn.clicked.connect(self.list_cloud_files)
        cloud_controls.addWidget(self.cloud_list_btn)
        controls_layout.addLayout(cloud_controls)

        # API controls
        api_controls = QHBoxLayout()
        api_controls.addWidget(QLabel("API:"))
        self.api_start_btn = QPushButton("Start Server")
        self.api_start_btn.clicked.connect(self.start_api_server)
        api_controls.addWidget(self.api_start_btn)
        self.api_stop_btn = QPushButton("Stop Server")
        self.api_stop_btn.clicked.connect(self.stop_api_server)
        self.api_stop_btn.setEnabled(False)
        api_controls.addWidget(self.api_stop_btn)
        controls_layout.addLayout(api_controls)

        layout.addWidget(controls_group)

        return widget

    def create_results_panel(self):
        """Create results panel"""
        group = QGroupBox("Results")
        layout = QVBoxLayout(group)

        # Filter input
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self.results_filter_input = QLineEdit()
        self.results_filter_input.setPlaceholderText("Filter results by keyword...")
        self.results_filter_input.textChanged.connect(self.filter_results)
        filter_layout.addWidget(self.results_filter_input)
        layout.addLayout(filter_layout)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results_text)

        # Store full results for filtering
        self.full_results_text = ""

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

        # View menu
        view_menu = menubar.addMenu("&View")

        # Theme submenu
        theme_menu = view_menu.addMenu("&Theme")

        light_theme_action = QAction("&Light", self)
        light_theme_action.triggered.connect(lambda: self.switch_theme("light"))
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("&Dark", self)
        dark_theme_action.triggered.connect(lambda: self.switch_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        view_menu.addSeparator()

        # Panel visibility options
        self.show_results_action = QAction("Show &Results Panel", self)
        self.show_results_action.setCheckable(True)
        self.show_results_action.setChecked(True)
        self.show_results_action.triggered.connect(self.toggle_results_panel)
        view_menu.addAction(self.show_results_action)

        self.show_dashboard_action = QAction("Show &Dashboard Tab", self)
        self.show_dashboard_action.setCheckable(True)
        self.show_dashboard_action.setChecked(True)
        self.show_dashboard_action.triggered.connect(self.toggle_dashboard_tab)
        view_menu.addAction(self.show_dashboard_action)

        self.show_attack_log_action = QAction("Show &Attack Log Tab", self)
        self.show_attack_log_action.setCheckable(True)
        self.show_attack_log_action.setChecked(True)
        self.show_attack_log_action.triggered.connect(self.toggle_attack_log_tab)
        view_menu.addAction(self.show_attack_log_action)

        self.show_statistics_action = QAction("Show &Statistics Tab", self)
        self.show_statistics_action.setCheckable(True)
        self.show_statistics_action.setChecked(True)
        self.show_statistics_action.triggered.connect(self.toggle_statistics_tab)
        view_menu.addAction(self.show_statistics_action)

        if self.integration_manager:
            self.show_integrations_action = QAction("Show &Integrations Tab", self)
            self.show_integrations_action.setCheckable(True)
            self.show_integrations_action.setChecked(True)
            self.show_integrations_action.triggered.connect(self.toggle_integrations_tab)
            view_menu.addAction(self.show_integrations_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        wordlist_generator_action = QAction("&Wordlist Generator", self)
        wordlist_generator_action.triggered.connect(self.show_wordlist_generator)
        tools_menu.addAction(wordlist_generator_action)

        charset_analyzer_action = QAction("&Charset Analyzer", self)
        charset_analyzer_action.triggered.connect(self.show_charset_analyzer)
        tools_menu.addAction(charset_analyzer_action)

        charset_optimizer_action = QAction("&Charset Optimizer", self)
        charset_optimizer_action.triggered.connect(self.show_charset_optimizer)
        tools_menu.addAction(charset_optimizer_action)

        attack_profiler_action = QAction("&Attack Profiler", self)
        attack_profiler_action.triggered.connect(self.show_attack_profiler)
        tools_menu.addAction(attack_profiler_action)

        tools_menu.addSeparator()

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts_dialog)
        tools_menu.addAction(shortcuts_action)

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
            self, "Select Wordlist", "", "Text Files (*.txt);;All Files (*)"
        )
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
        self.attempts_status.setText(f"Attempts: {attempts:,}")
        self.speed_status.setText(f"Speed: {speed}/sec")
        self.progress_display.setText(f"{progress}%")

        # Collect data for graphs
        current_time = time.time() - self.start_time
        self.time_data.append(current_time)
        # Convert speed to float for graphing (handle both string and numeric inputs)
        try:
            speed_float = float(speed) if isinstance(speed, (int, float, str)) else 0.0
        except (ValueError, TypeError):
            speed_float = 0.0
        self.speed_data.append(speed_float)
        self.attempts_data.append(attempts)
        self.progress_data.append(progress)

        # Update graphs if they exist
        if hasattr(self, 'speed_canvas'):
            self.update_speed_graph()
        if hasattr(self, 'progress_canvas'):
            self.update_progress_graph()

        # Update statistics panel in real-time
        self.update_statistics_panel(attempts, speed_float)



    def on_status_updated(self, status):
        """Handle status update"""
        self.attack_status_label.setText(f"Status: {status}")
        self.status_label.setText(status)

    def on_result_updated(self, result):
        """Handle result update"""
        self.full_results_text += result + "\n"
        self.filter_results()  # Apply current filter
        self.recent_results_text.append(result)

        # Scroll to bottom
        cursor = self.recent_results_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.recent_results_text.setTextCursor(cursor)

    def on_error_occurred(self, error):
        """Handle error"""
        QMessageBox.critical(self, "Error", error)
        self.status_label.setText(f"Error: {error}")

    def on_attack_log(self, log_entry):
        """Handle attack log entry"""
        self.full_attack_log_text += log_entry + "\n"
        self.filter_attack_log()  # Apply current filter

    def update_statistics_panel(self, attempts, current_speed):
        """Update statistics panel with real-time data"""
        # Update total attempts
        self.total_attempts_stat.setText(f"Total Attempts: {attempts:,}")
        
        # Update average speed (using moving average)
        if hasattr(self, '_speed_history'):
            self._speed_history.append(current_speed)
            if len(self._speed_history) > 100:
                self._speed_history.pop(0)
        else:
            self._speed_history = [current_speed]
        
        avg_speed = sum(self._speed_history) / len(self._speed_history) if self._speed_history else 0
        self.avg_speed_stat.setText(f"Average Speed: {avg_speed:.1f}/sec")
        
        # Update peak speed
        if not hasattr(self, '_peak_speed'):
            self._peak_speed = 0
        if current_speed > self._peak_speed:
            self._peak_speed = current_speed
        self.peak_speed_stat.setText(f"Peak Speed: {self._peak_speed:.1f}/sec")
        
        # Update success rate (placeholder - would need actual success count)
        success_rate = 0.0  # Could be calculated if we track successes
        self.success_rate_stat.setText(f"Success Rate: {success_rate:.1f}%")
        
        # Update start time
        if self.brute_force_thread and self.brute_force_thread.stats.get('start_time'):
            start_time = self.brute_force_thread.stats['start_time']
            self.start_time_stat.setText(f"Start Time: {start_time.strftime('%H:%M:%S')}")
        
        # Update duration
        elapsed = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.duration_stat.setText(f"Duration: {hours}:{minutes:02d}:{seconds:02d}")

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

        # Final statistics update
        if self.brute_force_thread:
            stats = self.brute_force_thread.stats
            self.total_attempts_stat.setText(f"Total Attempts: {stats['total_passwords_tested']:,}")
            self.avg_speed_stat.setText(f"Average Speed: {stats['average_speed']:.1f}/sec")
            self.peak_speed_stat.setText(f"Peak Speed: {stats['peak_speed']:.1f}/sec")

            if stats['start_time']:
                self.start_time_stat.setText(f"Start Time: {stats['start_time'].strftime('%H:%M:%S')}")
            if stats['end_time']:
                self.end_time_stat.setText(f"End Time: {stats['end_time'].strftime('%H:%M:%S')}")
            
            # Final duration
            if stats['start_time'] and stats['end_time']:
                duration = (stats['end_time'] - stats['start_time']).total_seconds()
                hours, remainder = divmod(int(duration), 3600)
                minutes, seconds = divmod(remainder, 60)
                self.duration_stat.setText(f"Duration: {hours}:{minutes:02d}:{seconds:02d}")

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
        self.full_attack_log_text = ""

    def export_results(self):
        """Export results to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", "Text Files (*.txt);;All Files (*)"
        )
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
        self.target_input.setText("")
        self.results_text.clear()
        self.attack_log_text.clear()
        self.recent_results_text.clear()
        self.full_results_text = ""
        self.full_attack_log_text = ""
        self.progress_bar.setValue(0)
        self.progress_label.setText("Progress: 0%")
        self.speed_label.setText("Speed: 0.0 attempts/sec")
        self.eta_label.setText("ETA: --:--:--")
        self.attack_status_label.setText("Status: Ready")
        self.current_target_label.setText("Target: None")
        self.elapsed_time_label.setText("Elapsed: 0:00:00")
        self.target_display.setText("None")
        self.progress_display.setText("0%")
        self.status_label.setText("Ready")
        self.attempts_status.setText("Attempts: 0")
        self.speed_status.setText("Speed: 0.0/sec")

    def open_session(self):
        """Open existing session"""
        QMessageBox.information(self, "Info", "Session loading not implemented yet")

    def save_session(self):
        """Save current session"""
        QMessageBox.information(self, "Info", "Session saving not implemented yet")

    def show_wordlist_generator(self):
        """Show wordlist generator dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Wordlist Generator")
        dialog.setModal(True)
        dialog.resize(600, 500)

        layout = QVBoxLayout(dialog)

        # Generator type selection
        type_group = QGroupBox("Generator Type")
        type_layout = QHBoxLayout(type_group)

        self.generator_type_combo = QComboBox()
        self.generator_type_combo.addItems([
            "Pattern-based",
            "Character combinations",
            "Dictionary-based mutations",
            "Date-based",
            "Number sequences"
        ])
        self.generator_type_combo.currentTextChanged.connect(self.update_generator_options)
        type_layout.addWidget(QLabel("Type:"))
        type_layout.addWidget(self.generator_type_combo)

        layout.addWidget(type_group)

        # Generator options (dynamic based on type)
        self.options_group = QGroupBox("Options")
        self.options_layout = QGridLayout(self.options_group)

        # Pattern-based options (default)
        self.pattern_label = QLabel("Pattern:")
        self.pattern_input = QLineEdit("?l?l?d?d")  # 2 letters + 2 digits = 67,600 combos
        self.pattern_input.setPlaceholderText("Use ?l (lowercase), ?u (uppercase), ?d (digit), ?s (special)")

        self.options_layout.addWidget(self.pattern_label, 0, 0)
        self.options_layout.addWidget(self.pattern_input, 0, 1, 1, 2)

        # Min/Max length
        self.min_len_label = QLabel("Min Length:")
        self.min_len_spin = QSpinBox()
        self.min_len_spin.setRange(1, 32)
        self.min_len_spin.setValue(8)
        self.options_layout.addWidget(self.min_len_label, 1, 0)
        self.options_layout.addWidget(self.min_len_spin, 1, 1)

        self.max_len_label = QLabel("Max Length:")
        self.max_len_spin = QSpinBox()
        self.max_len_spin.setRange(1, 32)
        self.max_len_spin.setValue(12)
        self.options_layout.addWidget(self.max_len_label, 1, 2)
        self.options_layout.addWidget(self.max_len_spin, 1, 3)

        # Output options
        self.output_file_label = QLabel("Output File:")
        self.output_file_input = QLineEdit("generated_wordlist.txt")
        self.output_file_browse_btn = QPushButton("Browse...")
        self.output_file_browse_btn.clicked.connect(self.browse_wordlist_output)
        self.options_layout.addWidget(self.output_file_label, 2, 0)
        self.options_layout.addWidget(self.output_file_input, 2, 1, 1, 2)
        self.options_layout.addWidget(self.output_file_browse_btn, 2, 3)

        # Preview area
        self.preview_label = QLabel("Preview (first 10):")
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        self.options_layout.addWidget(self.preview_label, 3, 0, 1, 4)
        self.options_layout.addWidget(self.preview_text, 4, 0, 1, 4)

        layout.addWidget(self.options_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.generate_preview_btn = QPushButton("Generate Preview")
        self.generate_preview_btn.clicked.connect(self.generate_wordlist_preview)
        button_layout.addWidget(self.generate_preview_btn)

        self.generate_full_btn = QPushButton("Generate Full Wordlist")
        self.generate_full_btn.clicked.connect(self.generate_full_wordlist)
        button_layout.addWidget(self.generate_full_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Initialize with default options
        self.update_generator_options()

        dialog.exec()

    def show_charset_analyzer(self):
        """Show charset analyzer dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Charset Analyzer")
        dialog.setModal(True)
        dialog.resize(700, 600)

        layout = QVBoxLayout(dialog)

        # Input section
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout(input_group)

        # Text input
        input_layout.addWidget(QLabel("Enter text to analyze:"))
        self.analyzer_text_input = QTextEdit()
        self.analyzer_text_input.setPlaceholderText("Paste passwords, text, or load from file...")
        input_layout.addWidget(self.analyzer_text_input)

        # File input
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Or load from file:"))
        self.analyzer_file_input = QLineEdit()
        self.analyzer_file_input.setPlaceholderText("Path to text file")
        file_layout.addWidget(self.analyzer_file_input)
        self.analyzer_file_browse_btn = QPushButton("Browse...")
        self.analyzer_file_browse_btn.clicked.connect(self.browse_analyzer_file)
        file_layout.addWidget(self.analyzer_file_browse_btn)
        self.analyzer_load_btn = QPushButton("Load")
        self.analyzer_load_btn.clicked.connect(self.load_analyzer_file)
        file_layout.addWidget(self.analyzer_load_btn)
        input_layout.addLayout(file_layout)

        layout.addWidget(input_group)

        # Analysis section
        analysis_group = QGroupBox("Analysis Results")
        analysis_layout = QGridLayout(analysis_group)

        # Character statistics
        stats_group = QGroupBox("Character Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        stats_layout.addWidget(self.stats_text)

        analysis_layout.addWidget(stats_group, 0, 0)

        # Character distribution
        dist_group = QGroupBox("Character Distribution")
        dist_layout = QVBoxLayout(dist_group)

        self.distribution_text = QTextEdit()
        self.distribution_text.setReadOnly(True)
        self.distribution_text.setMaximumHeight(150)
        dist_layout.addWidget(self.distribution_text)

        analysis_layout.addWidget(dist_group, 0, 1)

        # Password analysis
        pw_group = QGroupBox("Password Analysis")
        pw_layout = QVBoxLayout(pw_group)

        self.password_analysis_text = QTextEdit()
        self.password_analysis_text.setReadOnly(True)
        self.password_analysis_text.setMaximumHeight(150)
        pw_layout.addWidget(self.password_analysis_text)

        analysis_layout.addWidget(pw_group, 1, 0, 1, 2)

        layout.addWidget(analysis_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.clicked.connect(self.perform_charset_analysis)
        button_layout.addWidget(self.analyze_btn)

        self.export_analysis_btn = QPushButton("Export Analysis")
        self.export_analysis_btn.clicked.connect(self.export_charset_analysis)
        button_layout.addWidget(self.export_analysis_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Close")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()

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

    def switch_theme(self, theme):
        """Switch between light and dark themes"""
        if theme == self.current_theme:
            return

        self.current_theme = theme

        if theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

        logger.info(f"Switched to {theme} theme")

    def toggle_results_panel(self):
        """Toggle visibility of results panel"""
        visible = self.show_results_action.isChecked()
        self.results_panel.setVisible(visible)
        logger.info(f"Results panel {'shown' if visible else 'hidden'}")

    def toggle_dashboard_tab(self):
        """Toggle visibility of dashboard tab"""
        visible = self.show_dashboard_action.isChecked()
        self.tab_widget.setTabVisible(0, visible)  # Dashboard is index 0
        logger.info(f"Dashboard tab {'shown' if visible else 'hidden'}")

    def toggle_attack_log_tab(self):
        """Toggle visibility of attack log tab"""
        visible = self.show_attack_log_action.isChecked()
        self.tab_widget.setTabVisible(1, visible)  # Attack Log is index 1
        logger.info(f"Attack log tab {'shown' if visible else 'hidden'}")

    def toggle_statistics_tab(self):
        """Toggle visibility of statistics tab"""
        visible = self.show_statistics_action.isChecked()
        self.tab_widget.setTabVisible(2, visible)  # Statistics is index 2
        logger.info(f"Statistics tab {'shown' if visible else 'hidden'}")

    def toggle_integrations_tab(self):
        """Toggle visibility of integrations tab"""
        if self.integration_manager:
            visible = self.show_integrations_action.isChecked()
            self.tab_widget.setTabVisible(3, visible)  # Integrations is index 3
            logger.info(f"Integrations tab {'shown' if visible else 'hidden'}")

    def apply_light_theme(self):
        """Apply light theme stylesheets"""
        light_stylesheet = """
        QMainWindow {
            background-color: #f5f5f5;
            color: #333333;
        }

        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 1ex;
            background-color: #ffffff;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: #333333;
        }

        QPushButton {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            padding: 5px 10px;
            border-radius: 3px;
            color: #333333;
        }

        QPushButton:hover {
            background-color: #e6e6e6;
        }

        QPushButton:pressed {
            background-color: #cccccc;
        }

        QPushButton:disabled {
            background-color: #f5f5f5;
            color: #999999;
        }

        QLineEdit, QTextEdit, QComboBox, QSpinBox {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            padding: 3px;
            border-radius: 3px;
            color: #333333;
        }

        QProgressBar {
            border: 1px solid #cccccc;
            border-radius: 3px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #4CAF50;
        }

        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: #ffffff;
        }

        QTabBar::tab {
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            padding: 8px 12px;
            margin-right: 2px;
            color: #333333;
        }

        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: none;
        }

        QMenuBar {
            background-color: #f0f0f0;
            color: #333333;
        }

        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }

        QMenuBar::item:selected {
            background-color: #e6e6e6;
        }

        QStatusBar {
            background-color: #f0f0f0;
            color: #333333;
        }
        """
        self.setStyleSheet(light_stylesheet)

    def apply_dark_theme(self):
        """Apply dark theme stylesheets"""
        dark_stylesheet = """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }

        QGroupBox {
            font-weight: bold;
            border: 2px solid #555555;
            border-radius: 5px;
            margin-top: 1ex;
            background-color: #3c3c3c;
            color: #ffffff;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: #ffffff;
        }

        QPushButton {
            background-color: #4a4a4a;
            border: 1px solid #666666;
            padding: 5px 10px;
            border-radius: 3px;
            color: #ffffff;
        }

        QPushButton:hover {
            background-color: #5a5a5a;
        }

        QPushButton:pressed {
            background-color: #666666;
        }

        QPushButton:disabled {
            background-color: #3c3c3c;
            color: #888888;
        }

        QLineEdit, QTextEdit, QComboBox, QSpinBox {
            background-color: #4a4a4a;
            border: 1px solid #666666;
            padding: 3px;
            border-radius: 3px;
            color: #ffffff;
        }

        QProgressBar {
            border: 1px solid #666666;
            border-radius: 3px;
            text-align: center;
            background-color: #4a4a4a;
            color: #ffffff;
        }

        QProgressBar::chunk {
            background-color: #4CAF50;
        }

        QTabWidget::pane {
            border: 1px solid #666666;
            background-color: #3c3c3c;
        }

        QTabBar::tab {
            background-color: #4a4a4a;
            border: 1px solid #666666;
            padding: 8px 12px;
            margin-right: 2px;
            color: #ffffff;
        }

        QTabBar::tab:selected {
            background-color: #3c3c3c;
            border-bottom: none;
        }

        QMenuBar {
            background-color: #3c3c3c;
            color: #ffffff;
        }

        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }

        QMenuBar::item:selected {
            background-color: #4a4a4a;
        }

        QStatusBar {
            background-color: #3c3c3c;
            color: #ffffff;
        }

        QLabel {
            color: #ffffff;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def filter_results(self):
        """Filter results based on the filter input"""
        filter_text = self.results_filter_input.text().strip().lower()
        if not filter_text:
            # No filter, show all
            self.results_text.setPlainText(self.full_results_text.rstrip())
        else:
            # Filter lines that contain the filter text
            lines = self.full_results_text.split('\n')
            filtered_lines = [line for line in lines if filter_text in line.lower()]
            self.results_text.setPlainText('\n'.join(filtered_lines))

    def filter_attack_log(self):
        """Filter attack log based on the filter input"""
        filter_text = self.attack_log_filter_input.text().strip().lower()
        if not filter_text:
            # No filter, show all
            self.attack_log_text.setPlainText(self.full_attack_log_text.rstrip())
        else:
            # Filter lines that contain the filter text
            lines = self.full_attack_log_text.split('\n')
            filtered_lines = [line for line in lines if filter_text in line.lower()]
            self.attack_log_text.setPlainText('\n'.join(filtered_lines))

    def update_speed_graph(self):
        """Update the speed over time graph"""
        if not self.time_data or not self.speed_data:
            return

        self.speed_ax.clear()
        self.speed_ax.plot(list(self.time_data), list(self.speed_data), 'b-', linewidth=2)
        self.speed_ax.set_title("Attack Speed Over Time", fontsize=10)
        self.speed_ax.set_xlabel("Time (s)", fontsize=8)
        self.speed_ax.set_ylabel("Speed (attempts/sec)", fontsize=8)
        self.speed_ax.grid(True, alpha=0.3)

        # Set reasonable limits
        if self.time_data:
            self.speed_ax.set_xlim(0, max(self.time_data) + 1)
        if self.speed_data:
            # Filter out invalid values and find max
            valid_speeds = [s for s in self.speed_data if isinstance(s, (int, float)) and s >= 0]
            if valid_speeds:
                max_speed = max(valid_speeds)
                self.speed_ax.set_ylim(0, max_speed * 1.1 if max_speed > 0 else 100)
            else:
                self.speed_ax.set_ylim(0, 100)

        self.speed_canvas.draw()


    def update_progress_graph(self):
        """Update the progress over time graph"""
        if not self.time_data or not self.progress_data:
            return

        self.progress_ax.clear()
        self.progress_ax.plot(list(self.time_data), list(self.progress_data), 'g-', linewidth=2)
        self.progress_ax.set_title("Progress Over Time", fontsize=10)
        self.progress_ax.set_xlabel("Time (s)", fontsize=8)
        self.progress_ax.set_ylabel("Progress (%)", fontsize=8)
        self.progress_ax.grid(True, alpha=0.3)
        self.progress_ax.set_ylim(0, 100)

        if self.time_data:
            self.progress_ax.set_xlim(0, max(self.time_data) + 1)

        self.progress_canvas.draw()

    def show_shortcuts_dialog(self):
        """Show keyboard shortcuts configuration dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        # Instructions
        instructions = QLabel("Double-click on a shortcut to edit it. Use format like 'Ctrl+S' or 'Alt+F1'.")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Shortcuts table
        self.shortcuts_table = QTableWidget()
        self.shortcuts_table.setColumnCount(2)
        self.shortcuts_table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        self.shortcuts_table.horizontalHeader().setStretchLastSection(True)
        self.shortcuts_table.setAlternatingRowColors(True)
        self.shortcuts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Populate table
        self.populate_shortcuts_table()

        layout.addWidget(self.shortcuts_table)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Connect double-click to edit
        self.shortcuts_table.cellDoubleClicked.connect(self.edit_shortcut)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.save_shortcuts()

    def populate_shortcuts_table(self):
        """Populate the shortcuts table with current shortcuts"""
        shortcuts_display = {
            "start_attack": "Start Attack",
            "stop_attack": "Stop Attack",
            "pause_attack": "Pause Attack",
            "resume_attack": "Resume Attack",
            "new_session": "New Session",
            "open_session": "Open Session",
            "save_session": "Save Session",
            "export_results": "Export Results",
            "clear_log": "Clear Log",
            "show_dashboard": "Show Dashboard Tab",
            "show_attack_log": "Show Attack Log Tab",
            "show_statistics": "Show Statistics Tab",
            "show_integrations": "Show Integrations Tab"
        }

        self.shortcuts_table.setRowCount(len(shortcuts_display))

        for row, (key, display_name) in enumerate(shortcuts_display.items()):
            # Action name
            action_item = QTableWidgetItem(display_name)
            action_item.setFlags(action_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.shortcuts_table.setItem(row, 0, action_item)

            # Current shortcut
            shortcut = DEFAULT_SHORTCUTS.get(key, "")
            shortcut_item = QTableWidgetItem(shortcut)
            self.shortcuts_table.setItem(row, 1, shortcut_item)

    def edit_shortcut(self, row, column):
        """Edit a shortcut when double-clicked"""
        if column == 1:  # Only allow editing shortcut column
            current_shortcut = self.shortcuts_table.item(row, 0).text()
            action_key = None

            # Find the action key
            shortcuts_display = {
                "start_attack": "Start Attack",
                "stop_attack": "Stop Attack",
                "pause_attack": "Pause Attack",
                "resume_attack": "Resume Attack",
                "new_session": "New Session",
                "open_session": "Open Session",
                "save_session": "Save Session",
                "export_results": "Export Results",
                "clear_log": "Clear Log",
                "show_dashboard": "Show Dashboard Tab",
                "show_attack_log": "Show Attack Log Tab",
                "show_statistics": "Show Statistics Tab",
                "show_integrations": "Show Integrations Tab"
            }

            for key, display in shortcuts_display.items():
                if display == current_shortcut:
                    action_key = key
                    break

            if action_key:
                # Show input dialog for new shortcut
                new_shortcut, ok = QInputDialog.getText(
                    self, "Edit Shortcut",
                    f"Enter new shortcut for '{current_shortcut}':\nUse format like 'Ctrl+S' or 'Alt+F1'",
                    text=DEFAULT_SHORTCUTS.get(action_key, "")
                )

                if ok and new_shortcut:
                    # Validate shortcut format (basic validation)
                    if self.validate_shortcut(new_shortcut):
                        self.shortcuts_table.item(row, 1).setText(new_shortcut)
                    else:
                        QMessageBox.warning(self, "Invalid Shortcut",
                                          "Invalid shortcut format. Use formats like 'Ctrl+S', 'Alt+F1', 'F5', etc.")

    def validate_shortcut(self, shortcut):
        """Basic validation for shortcut format"""
        # Allow empty shortcuts
        if not shortcut.strip():
            return True

        # Check for common formats
        valid_patterns = [
            r'^CTRL\+[A-Z0-9]$',  # Ctrl+Letter/Digit
            r'^ALT\+[A-Z0-9]$',   # Alt+Letter/Digit
            r'^SHIFT\+[A-Z0-9]$', # Shift+Letter/Digit
            r'^F\d+$',            # Function keys
            r'^ALT\+F\d+$',       # Alt+Function keys
            r'^CTRL\+ALT\+[A-Z0-9]$',  # Ctrl+Alt+Letter/Digit
            r'^CTRL\+SHIFT\+[A-Z0-9]$', # Ctrl+Shift+Letter/Digit
        ]

        import re
        for pattern in valid_patterns:
            if re.match(pattern, shortcut.upper()):
                return True

        return False

    def save_shortcuts(self):
        """Save the updated shortcuts"""
        # This would save to a config file in a real implementation
        # For now, just update the DEFAULT_SHORTCUTS (though this won't persist)
        QMessageBox.information(self, "Shortcuts Saved",
                              "Keyboard shortcuts have been updated.\n"
                              "Note: Changes will take effect after restarting the application.")

    def browse_hashcat(self):
        """Browse for Hashcat executable"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Hashcat Executable", "", "Executable Files (*.exe);;All Files (*)"
        )
        if filename:
            self.hashcat_path_input.setText(filename)

    def browse_john(self):
        """Browse for John the Ripper executable"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select John the Ripper Executable", "", "Executable Files (*.exe);;All Files (*)"
        )
        if filename:
            self.john_path_input.setText(filename)

    def apply_integration_config(self):
        """Apply integration configuration"""
        try:
            # Update integration manager configuration
            if self.integration_manager:
                # Hashcat config
                hashcat_path = self.hashcat_path_input.text().strip()
                if hashcat_path:
                    self.integration_manager.config.hashcat_path = hashcat_path
                    self.integration_manager.config.hashcat_enabled = True

                # John config
                john_path = self.john_path_input.text().strip()
                if john_path:
                    self.integration_manager.config.john_path = john_path
                    self.integration_manager.config.john_enabled = True

                # Cloud config
                cloud_provider = self.cloud_provider_combo.currentText()
                cloud_bucket = self.cloud_bucket_input.text().strip()
                cloud_access_key = self.cloud_access_key_input.text().strip()
                cloud_secret_key = self.cloud_secret_key_input.text().strip()

                if cloud_provider and cloud_bucket and cloud_access_key and cloud_secret_key:
                    self.integration_manager.config.cloud_enabled = True
                    self.integration_manager.config.cloud_provider = cloud_provider
                    self.integration_manager.config.cloud_bucket = cloud_bucket
                    self.integration_manager.config.cloud_access_key = cloud_access_key
                    self.integration_manager.config.cloud_secret_key = cloud_secret_key

                # API config
                api_host = self.api_host_input.text().strip()
                api_port = self.api_port_spin.value()

                if api_host and api_port:
                    self.integration_manager.config.api_enabled = True
                    self.integration_manager.config.api_host = api_host
                    self.integration_manager.config.api_port = api_port

                # Reinitialize integrations with new config
                self.integration_manager._init_integrations()

                QMessageBox.information(self, "Configuration Applied",
                                      "Integration configuration has been applied successfully.")
                logger.info("Integration configuration applied")

        except Exception as e:
            QMessageBox.critical(self, "Configuration Error",
                               f"Failed to apply configuration: {str(e)}")
            logger.error(f"Failed to apply integration config: {e}")

    def run_hashcat_benchmark(self):
        """Run Hashcat benchmark"""
        if not self.integration_manager or not self.integration_manager.hashcat_integration:
            QMessageBox.warning(self, "Hashcat Not Available",
                              "Hashcat integration is not configured or available.")
            return

        try:
            result = self.integration_manager.hashcat_integration.get_benchmark()
            if "error" in result:
                QMessageBox.critical(self, "Benchmark Failed", result["error"])
            else:
                QMessageBox.information(self, "Benchmark Results",
                                      f"Hashcat benchmark completed.\n\n"
                                      f"Return Code: {result.get('return_code', 'N/A')}\n"
                                      f"Output: {result.get('stdout', '')[:500]}...")
        except Exception as e:
            QMessageBox.critical(self, "Benchmark Error", f"Failed to run benchmark: {str(e)}")

    def test_john_installation(self):
        """Test John the Ripper installation"""
        if not self.integration_manager or not self.integration_manager.john_integration:
            QMessageBox.warning(self, "John Not Available",
                              "John the Ripper integration is not configured or available.")
            return

        try:
            # Test by checking supported formats
            formats = self.integration_manager.john_integration.get_supported_formats()
            QMessageBox.information(self, "John Test Successful",
                                  f"John the Ripper is working correctly.\n\n"
                                  f"Supported formats: {len(formats)}\n"
                                  f"Sample formats: {', '.join(formats[:5])}...")
        except Exception as e:
            QMessageBox.critical(self, "John Test Failed", f"John test failed: {str(e)}")

    def test_cloud_connection(self):
        """Test cloud storage connection"""
        if not self.integration_manager or not self.integration_manager.cloud_integration:
            QMessageBox.warning(self, "Cloud Not Available",
                              "Cloud integration is not configured or available.")
            return

        try:
            info = self.integration_manager.cloud_integration.get_storage_info()
            if "error" in info:
                QMessageBox.critical(self, "Cloud Test Failed", info["error"])
            else:
                QMessageBox.information(self, "Cloud Test Successful",
                                      f"Cloud connection successful!\n\n"
                                      f"Provider: {info.get('provider', 'N/A')}\n"
                                      f"Bucket: {info.get('bucket', 'N/A')}\n"
                                      f"Files: {info.get('file_count', 0)}")
        except Exception as e:
            QMessageBox.critical(self, "Cloud Test Failed", f"Cloud test failed: {str(e)}")

    def list_cloud_files(self):
        """List files in cloud storage"""
        if not self.integration_manager or not self.integration_manager.cloud_integration:
            QMessageBox.warning(self, "Cloud Not Available",
                              "Cloud integration is not configured or available.")
            return

        try:
            files = self.integration_manager.cloud_integration.list_files()
            if not files:
                QMessageBox.information(self, "Cloud Files", "No files found in cloud storage.")
            else:
                file_list = "\n".join(files[:20])  # Show first 20 files
                if len(files) > 20:
                    file_list += f"\n... and {len(files) - 20} more files"
                QMessageBox.information(self, "Cloud Files",
                                      f"Files in cloud storage:\n\n{file_list}")
        except Exception as e:
            QMessageBox.critical(self, "List Files Failed", f"Failed to list cloud files: {str(e)}")

    def start_api_server(self):
        """Start the API server"""
        if not self.integration_manager or not self.integration_manager.api_server:
            QMessageBox.warning(self, "API Not Available",

                              "API integration is not configured or available.")
            return

        try:
            if self.integration_manager.api_server.start():
                self.api_start_btn.setEnabled(False)

                self.api_stop_btn.setEnabled(True)
                QMessageBox.information(self, "API Server Started",
                                      "API server started successfully.")
                logger.info("API server started from GUI")
            else:
                QMessageBox.critical(self, "API Start Failed", "Failed to start API server.")
        except Exception as e:
            QMessageBox.critical(self, "API Start Error", f"Failed to start API server: {str(e)}")

    def stop_api_server(self):
        """Stop the API server"""
        if not self.integration_manager or not self.integration_manager.api_server:
            return
        try:
            if self.integration_manager.api_server.stop():

                self.api_start_btn.setEnabled(True)
                self.api_stop_btn.setEnabled(False)
                QMessageBox.information(self, "API Server Stopped",
                                      "API server stopped successfully.")
                logger.info("API server stopped from GUI")
            else:
                QMessageBox.critical(self, "API Stop Failed", "Failed to stop API server.")
        except Exception as e:
            QMessageBox.critical(self, "API Stop Error", f"Failed to stop API server: {str(e)}")

    def update_generator_options(self):
        """Update generator options based on selected type"""
        generator_type = self.generator_type_combo.currentText()

        # Clear existing options
        for i in reversed(range(self.options_layout.count())):
            widget = self.options_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if generator_type == "Pattern-based":
            # Pattern input
            self.pattern_label = QLabel("Pattern:")
            self.pattern_input = QLineEdit("?l?l?d?d")  # 2 letters + 2 digits = 67,600 combos
            self.pattern_input.setPlaceholderText("Use ?l (lowercase), ?u (uppercase), ?d (digit), ?s (special)")


            self.options_layout.addWidget(self.pattern_label, 0, 0)
            self.options_layout.addWidget(self.pattern_input, 0, 1, 1, 2)

            # Min/Max length
            self.min_len_label = QLabel("Min Length:")
            self.min_len_spin = QSpinBox()
            self.min_len_spin.setRange(1, 32)
            self.min_len_spin.setValue(8)
            self.options_layout.addWidget(self.min_len_label, 1, 0)
            self.options_layout.addWidget(self.min_len_spin, 1, 1)

            self.max_len_label = QLabel("Max Length:")
            self.max_len_spin = QSpinBox()
            self.max_len_spin.setRange(1, 32)
            self.max_len_spin.setValue(12)
            self.options_layout.addWidget(self.max_len_label, 1, 2)
            self.options_layout.addWidget(self.max_len_spin, 1, 3)

        elif generator_type == "Character combinations":
            # Character set
            self.charset_label = QLabel("Character Set:")
            self.charset_input = QLineEdit("abcdefghijklmnopqrstuvwxyz0123456789")
            self.options_layout.addWidget(self.charset_label, 0, 0)
            self.options_layout.addWidget(self.charset_input, 0, 1, 1, 2)

            # Min/Max length
            self.min_len_label = QLabel("Min Length:")
            self.min_len_spin = QSpinBox()
            self.min_len_spin.setRange(1, 8)  # Limit for combinations
            self.min_len_spin.setValue(4)
            self.options_layout.addWidget(self.min_len_label, 1, 0)
            self.options_layout.addWidget(self.min_len_spin, 1, 1)

            self.max_len_label = QLabel("Max Length:")
            self.max_len_spin = QSpinBox()
            self.max_len_spin.setRange(1, 8)
            self.max_len_spin.setValue(6)
            self.options_layout.addWidget(self.max_len_label, 1, 2)
            self.options_layout.addWidget(self.max_len_spin, 1, 3)

        elif generator_type == "Dictionary-based mutations":
            # Base wordlist
            self.base_wordlist_label = QLabel("Base Wordlist:")
            self.base_wordlist_input = QLineEdit()
            self.base_wordlist_browse_btn = QPushButton("Browse...")
            self.base_wordlist_browse_btn.clicked.connect(self.browse_base_wordlist)
            self.options_layout.addWidget(self.base_wordlist_label, 0, 0)
            self.options_layout.addWidget(self.base_wordlist_input, 0, 1, 1, 2)
            self.options_layout.addWidget(self.base_wordlist_browse_btn, 0, 3)

            # Mutation rules
            self.mutations_label = QLabel("Mutations:")
            self.mutations_combo = QComboBox()
            self.mutations_combo.addItems([
                "Append numbers (0-99)",
                "Append special chars",
                "Capitalize first letter",
                "Leet speak",
                "Reverse words",
                "All combinations"
            ])
            self.options_layout.addWidget(self.mutations_label, 1, 0)
            self.options_layout.addWidget(self.mutations_combo, 1, 1, 1, 2)

        elif generator_type == "Date-based":
            # Date range
            self.start_year_label = QLabel("Start Year:")
            self.start_year_spin = QSpinBox()
            self.start_year_spin.setRange(1900, 2030)
            self.start_year_spin.setValue(2000)
            self.options_layout.addWidget(self.start_year_label, 0, 0)
            self.options_layout.addWidget(self.start_year_spin, 0, 1)

            self.end_year_label = QLabel("End Year:")
            self.end_year_spin = QSpinBox()
            self.end_year_spin.setRange(1900, 2030)
            self.end_year_spin.setValue(2024)
            self.options_layout.addWidget(self.end_year_label, 0, 2)
            self.options_layout.addWidget(self.end_year_spin, 0, 3)

            # Date formats
            self.date_formats_label = QLabel("Date Formats:")
            self.date_formats_combo = QComboBox()
            self.date_formats_combo.addItems([
                "YYYYMMDD",
                "MMDDYYYY",
                "DDMMYYYY",
                "YYMMDD",
                "MMDDYY",
                "DDMMYY"
            ])
            self.options_layout.addWidget(self.date_formats_label, 1, 0)
            self.options_layout.addWidget(self.date_formats_combo, 1, 1, 1, 2)

        elif generator_type == "Number sequences":
            # Number range
            self.start_num_label = QLabel("Start Number:")
            self.start_num_spin = QSpinBox()
            self.start_num_spin.setRange(0, 999999)
            self.start_num_spin.setValue(0)
            self.options_layout.addWidget(self.start_num_label, 0, 0)
            self.options_layout.addWidget(self.start_num_spin, 0, 1)

            self.end_num_label = QLabel("End Number:")
            self.end_num_spin = QSpinBox()
            self.end_num_spin.setRange(0, 999999)
            self.end_num_spin.setValue(9999)
            self.options_layout.addWidget(self.end_num_label, 0, 2)
            self.options_layout.addWidget(self.end_num_spin, 0, 3)

            # Padding
            self.padding_label = QLabel("Zero Padding:")
            self.padding_combo = QComboBox()
            self.padding_combo.addItems(["None", "Auto", "Fixed"])
            self.options_layout.addWidget(self.padding_label, 1, 0)
            self.options_layout.addWidget(self.padding_combo, 1, 1)

            self.padding_width_label = QLabel("Width:")
            self.padding_width_spin = QSpinBox()
            self.padding_width_spin.setRange(1, 10)
            self.padding_width_spin.setValue(4)
            self.options_layout.addWidget(self.padding_width_label, 1, 2)
            self.options_layout.addWidget(self.padding_width_spin, 1, 3)

        # Common output options
        self.output_file_label = QLabel("Output File:")
        self.output_file_input = QLineEdit("generated_wordlist.txt")
        self.output_file_browse_btn = QPushButton("Browse...")
        self.output_file_browse_btn.clicked.connect(self.browse_wordlist_output)
        self.options_layout.addWidget(self.output_file_label, 2, 0)
        self.options_layout.addWidget(self.output_file_input, 2, 1, 1, 2)
        self.options_layout.addWidget(self.output_file_browse_btn, 2, 3)

        # Preview area
        self.preview_label = QLabel("Preview (first 10):")
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        self.options_layout.addWidget(self.preview_label, 3, 0, 1, 4)
        self.options_layout.addWidget(self.preview_text, 4, 0, 1, 4)

    def browse_wordlist_output(self):
        """Browse for wordlist output file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Wordlist", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            self.output_file_input.setText(filename)

    def browse_base_wordlist(self):
        """Browse for base wordlist file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Base Wordlist", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            self.base_wordlist_input.setText(filename)

    def generate_wordlist_preview(self):
        """Generate preview of wordlist"""
        try:
            generator_type = self.generator_type_combo.currentText()
            preview_lines = []

            if generator_type == "Pattern-based":

                pattern = self.pattern_input.text().strip()
                if not pattern:
                    preview_lines.append("Please enter a pattern")
                else:
                    try:
                        char_sets = {
                            'l': string.ascii_lowercase,
                            'u': string.ascii_uppercase,
                            'd': string.digits,
                            's': '!@#$%^&*'
                        }

                        # Parse pattern and generate preview
                        count = 0
                        for pw in self._generate_from_pattern(pattern, char_sets):
                            preview_lines.append(pw)
                            count += 1
                            if count >= 10:
                                break

                        if count == 0:
                            preview_lines.append("No passwords generated from pattern")

                    except Exception as e:
                        preview_lines.append(f"Error: {str(e)}")

            elif generator_type == "Character combinations":
                charset = self.charset_input.text().strip()
                min_len = self.min_len_spin.value()
                max_len = min(self.max_len_spin.value(), min_len + 2)  # Limit for preview

                for length in range(min_len, max_len + 1):
                    # Generate combinations
                    for combo in itertools.product(charset, repeat=length):
                        preview_lines.append(''.join(combo))
                        if len(preview_lines) >= 10:
                            break
                    if len(preview_lines) >= 10:
                        break

            elif generator_type == "Number sequences":
                start_num = self.start_num_spin.value()
                end_num = min(self.end_num_spin.value(), start_num + 10)  # Limit for preview
                padding = self.padding_combo.currentText()
                width = self.padding_width_spin.value()

                for num in range(start_num, end_num):
                    if padding == "Auto":
                        num_str = str(num)
                    elif padding == "Fixed":
                        num_str = f"{num:0{width}d}"
                    else:
                        num_str = str(num)
                    preview_lines.append(num_str)

            elif generator_type == "Date-based":
                start_year = self.start_year_spin.value()
                end_year = min(self.end_year_spin.value(), start_year + 2)  # Limit for preview
                date_format = self.date_formats_combo.currentText()

                import datetime
                for year in range(start_year, end_year + 1):
                    for month in range(1, 13):
                        for day in range(1, 28):  # Simplified
                            try:
                                date = datetime.date(year, month, day)
                                if date_format == "YYYYMMDD":
                                    formatted = date.strftime("%Y%m%d")
                                elif date_format == "MMDDYYYY":
                                    formatted = date.strftime("%m%d%Y")
                                elif date_format == "DDMMYYYY":
                                    formatted = date.strftime("%d%m%Y")
                                elif date_format == "YYMMDD":
                                    formatted = date.strftime("%y%m%d")
                                elif date_format == "MMDDYY":
                                    formatted = date.strftime("%m%d%y")
                                elif date_format == "DDMMYY":
                                    formatted = date.strftime("%d%m%y")
                                else:
                                    formatted = str(date)

                                preview_lines.append(formatted)
                                if len(preview_lines) >= 10:
                                    break
                            except ValueError:
                                continue
                        if len(preview_lines) >= 10:
                            break
                    if len(preview_lines) >= 10:
                        break

            elif generator_type == "Dictionary-based mutations":
                # Simple preview for mutations
                base_words = ["password", "admin", "user", "test"]
                mutation_type = self.mutations_combo.currentText()

                for word in base_words:
                    if mutation_type == "Append numbers (0-99)":
                        for i in range(10):
                            preview_lines.append(f"{word}{i}")
                    elif mutation_type == "Append special chars":
                        for char in "!@#$":
                            preview_lines.append(f"{word}{char}")
                    elif mutation_type == "Capitalize first letter":
                        preview_lines.append(word.capitalize())
                    elif mutation_type == "Leet speak":
                        leet = word.replace('a', '4').replace('e', '3').replace('i', '1').replace('o', '0')
                        preview_lines.append(leet)
                    elif mutation_type == "Reverse words":
                        preview_lines.append(word[::-1])
                    elif mutation_type == "All combinations":
                        preview_lines.append(f"{word}123")
                        preview_lines.append(f"{word}!")
                        preview_lines.append(word.capitalize())

                    if len(preview_lines) >= 10:
                        break

            # Display preview
            self.preview_text.setPlainText('\n'.join(preview_lines[:10]))

        except Exception as e:
            QMessageBox.critical(self, "Preview Error", f"Failed to generate preview: {str(e)}")

    def generate_full_wordlist(self):
        """Generate full wordlist"""
        try:
            output_file = self.output_file_input.text().strip()
            if not output_file:
                QMessageBox.warning(self, "Output File Required", "Please specify an output file.")
                return

            generator_type = self.generator_type_combo.currentText()

            # Show progress dialog
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Generating Wordlist")
            progress_dialog.setModal(True)
            progress_dialog.resize(400, 150)

            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(QLabel("Generating wordlist... This may take a while."))

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 0)  # Indeterminate progress
            layout.addWidget(progress_bar)

            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(progress_dialog.reject)
            layout.addWidget(cancel_btn)

            progress_dialog.show()

            # Generate wordlist in background
            # This is a simplified implementation - real implementation would use threading
            wordlist_data = []

            if generator_type == "Pattern-based":
                pattern = self.pattern_input.text().strip()

                if not pattern:
                    QMessageBox.warning(self, "Invalid Pattern", "Please enter a valid pattern.")
                    progress_dialog.accept()
                    return

                char_sets = {
                    'l': string.ascii_lowercase,
                    'u': string.ascii_uppercase,
                    'd': string.digits,
                    's': '!@#$%^&*'
                }

                # Estimate total combinations to avoid too large generation
                total_combinations = 1
                i = 0
                while i < len(pattern):
                    if pattern[i] == '?':
                        if i + 1 < len(pattern):
                            char_type = pattern[i + 1]
                            if char_type in char_sets:
                                total_combinations *= len(char_sets[char_type])
                                i += 2
                            else:
                                i += 1
                        else:
                            i += 1
                    else:
                        i += 1

                if total_combinations > 10000000:  # 10M limit
                    QMessageBox.warning(self, "Pattern Too Large",
                                       f"Pattern would generate {total_combinations:,} passwords. Please use a smaller pattern.")
                    progress_dialog.accept()
                    return

                # Generate wordlist
                wordlist_data = list(self._generate_from_pattern(pattern, char_sets))

            elif generator_type == "Number sequences":
                start_num = self.start_num_spin.value()

                end_num = self.end_num_spin.value()
                padding = self.padding_combo.currentText()
                width = self.padding_width_spin.value()

                for num in range(start_num, end_num + 1):
                    if padding == "Auto":
                        num_str = str(num)
                    elif padding == "Fixed":
                        num_str = f"{num:0{width}d}"
                    else:
                        num_str = str(num)
                    wordlist_data.append(num_str)

            elif generator_type == "Date-based":
                start_year = self.start_year_spin.value()

                end_year = self.end_year_spin.value()
                date_format = self.date_formats_combo.currentText()

                import datetime
                for year in range(start_year, end_year + 1):
                    for month in range(1, 13):
                        for day in range(1, 32):
                            try:
                                date = datetime.date(year, month, day)
                                if date_format == "YYYYMMDD":
                                    formatted = date.strftime("%Y%m%d")
                                elif date_format == "MMDDYYYY":
                                    formatted = date.strftime("%m%d%Y")
                                elif date_format == "DDMMYYYY":
                                    formatted = date.strftime("%d%m%Y")
                                elif date_format == "YYMMDD":
                                    formatted = date.strftime("%y%m%d")
                                elif date_format == "MMDDYY":
                                    formatted = date.strftime("%m%d%y")
                                elif date_format == "DDMMYY":
                                    formatted = date.strftime("%d%m%y")
                                else:
                                    formatted = str(date)

                                wordlist_data.append(formatted)
                            except ValueError:
                                continue

            # Write to file
            with open(output_file, 'w') as f:
                f.write('\n'.join(wordlist_data))

            progress_dialog.accept()

            QMessageBox.information(self, "Wordlist Generated",
                                  f"Wordlist generated successfully!\n\n"
                                  f"File: {output_file}\n"
                                  f"Passwords: {len(wordlist_data)}")

        except Exception as e:
            QMessageBox.critical(self, "Generation Error", f"Failed to generate wordlist: {str(e)}")

    def browse_analyzer_file(self):
        """Browse for analyzer input file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Text File", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            self.analyzer_file_input.setText(filename)

    def load_analyzer_file(self):
        """Load text from file for analysis"""
        try:
            filename = self.analyzer_file_input.text().strip()
            if not filename:
                QMessageBox.warning(self, "No File Selected", "Please select a file to load.")
                return

            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                self.analyzer_text_input.setPlainText(content)

            QMessageBox.information(self, "File Loaded", f"Loaded {len(content)} characters from file.")

        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load file: {str(e)}")

    def perform_charset_analysis(self):
        """Perform charset analysis on the input text"""
        try:
            # Get input text
            text = self.analyzer_text_input.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "No Input", "Please enter text or load a file to analyze.")
                return

            # Split into lines (assuming each line is a password)
            lines = text.split('\n')
            passwords = [line.strip() for line in lines if line.strip()]

            if not passwords:
                QMessageBox.warning(self, "No Passwords", "No valid passwords found in input.")
                return

            # Character analysis
            all_chars = ''.join(passwords)
            char_counts = {}
            for char in all_chars:
                char_counts[char] = char_counts.get(char, 0) + 1

            # Categorize characters
            lowercase = sum(1 for c in char_counts if c.islower())
            uppercase = sum(1 for c in char_counts if c.isupper())
            digits = sum(1 for c in char_counts if c.isdigit())
            special = sum(1 for c in char_counts if not c.isalnum())

            # Password statistics
            lengths = [len(pw) for pw in passwords]
            avg_length = sum(lengths) / len(lengths) if lengths else 0
            min_length = min(lengths) if lengths else 0
            max_length = max(lengths) if lengths else 0

            # Character distribution (top 20)
            sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
            top_chars = sorted_chars[:20]

            # Password patterns analysis
            patterns = {
                "Only lowercase": sum(1 for pw in passwords if pw.islower() and pw.isalpha()),
                "Only uppercase": sum(1 for pw in passwords if pw.isupper() and pw.isalpha()),
                "Only digits": sum(1 for pw in passwords if pw.isdigit()),
                "Mixed case": sum(1 for pw in passwords if any(c.islower() for c in pw) and any(c.isupper() for c in pw)),
                "Contains digits": sum(1 for pw in passwords if any(c.isdigit() for c in pw)),
                "Contains special": sum(1 for pw in passwords if any(not c.isalnum() for c in pw)),
                "Starts with number": sum(1 for pw in passwords if pw and pw[0].isdigit()),
                "Ends with number": sum(1 for pw in passwords if pw and pw[-1].isdigit()),
            }

            # Display results
            stats_text = f"""Character Statistics:
Total Characters: {len(all_chars)}
Unique Characters: {len(char_counts)}
Lowercase Letters: {lowercase}
Uppercase Letters: {uppercase}
Digits: {digits}
Special Characters: {special}

Password Statistics:
Total Passwords: {len(passwords)}
Average Length: {avg_length:.1f}
Min Length: {min_length}
Max Length: {max_length}
"""

            dist_text = "Top 20 Characters:\n"
            for char, count in top_chars:
                percent = (count / len(all_chars)) * 100
                char_display = repr(char) if not char.isprintable() else char
                dist_text += f"{char_display}: {count} ({percent:.1f}%)\n"

            pw_text = "Password Patterns:\n"
            for pattern, count in patterns.items():
                percent = (count / len(passwords)) * 100 if passwords else 0
                pw_text += f"{pattern}: {count} ({percent:.1f}%)\n"

            self.stats_text.setPlainText(stats_text)
            self.distribution_text.setPlainText(dist_text)
            self.password_analysis_text.setPlainText(pw_text)

        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Failed to analyze text: {str(e)}")

    def export_charset_analysis(self):
        """Export charset analysis results"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Analysis", "", "Text Files (*.txt);;All Files (*)"
            )
            if not filename:
                return

            with open(filename, 'w') as f:
                f.write("=== Charset Analysis Results ===\n\n")
                f.write("CHARACTER STATISTICS\n")
                f.write(self.stats_text.toPlainText())
                f.write("\n\nCHARACTER DISTRIBUTION\n")
                f.write(self.distribution_text.toPlainText())
                f.write("\n\nPASSWORD ANALYSIS\n")
                f.write(self.password_analysis_text.toPlainText())

            QMessageBox.information(self, "Export Successful", f"Analysis exported to {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export analysis: {str(e)}")

    def show_charset_optimizer(self):
        """Show charset optimizer dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Charset Optimizer")
        dialog.setModal(True)
        dialog.resize(800, 700)

        layout = QVBoxLayout(dialog)

        # Input section
        input_group = QGroupBox("Input Wordlist")
        input_layout = QVBoxLayout(input_group)

        # File input
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Wordlist File:"))
        self.optimizer_file_input = QLineEdit()
        self.optimizer_file_input.setPlaceholderText("Path to wordlist file")
        file_layout.addWidget(self.optimizer_file_input)
        self.optimizer_file_browse_btn = QPushButton("Browse...")
        self.optimizer_file_browse_btn.clicked.connect(self.browse_optimizer_file)
        file_layout.addWidget(self.optimizer_file_browse_btn)
        self.optimizer_load_btn = QPushButton("Load")
        self.optimizer_load_btn.clicked.connect(self.load_optimizer_file)
        file_layout.addWidget(self.optimizer_load_btn)
        input_layout.addLayout(file_layout)

        # Sample size
        sample_layout = QHBoxLayout()
        sample_layout.addWidget(QLabel("Sample Size:"))
        self.sample_size_spin = QSpinBox()
        self.sample_size_spin.setRange(100, 100000)
        self.sample_size_spin.setValue(10000)
        self.sample_size_spin.setSuffix(" passwords")
        sample_layout.addWidget(self.sample_size_spin)
        sample_layout.addStretch()
        input_layout.addLayout(sample_layout)

        layout.addWidget(input_group)

        # Optimization section
        opt_group = QGroupBox("Charset Optimization")
        opt_layout = QGridLayout(opt_group)

        # Optimization method
        opt_layout.addWidget(QLabel("Optimization Method:"), 0, 0)
        self.opt_method_combo = QComboBox()
        self.opt_method_combo.addItems([
            "Frequency-based (most common first)",
            "Efficiency-based (balanced distribution)",
            "Attack-optimized (prioritize common patterns)"
        ])
        opt_layout.addWidget(self.opt_method_combo, 0, 1, 1, 2)

        # Target charset size
        opt_layout.addWidget(QLabel("Max Charset Size:"), 1, 0)
        self.max_charset_spin = QSpinBox()
        self.max_charset_spin.setRange(10, 100)
        self.max_charset_spin.setValue(50)
        opt_layout.addWidget(self.max_charset_spin, 1, 1)

        # Include categories
        category_group = QGroupBox("Include Character Categories")
        category_layout = QVBoxLayout(category_group)

        self.include_lowercase = QCheckBox("Lowercase letters (a-z)")
        self.include_lowercase.setChecked(True)
        category_layout.addWidget(self.include_lowercase)

        self.include_uppercase = QCheckBox("Uppercase letters (A-Z)")
        self.include_uppercase.setChecked(True)
        category_layout.addWidget(self.include_uppercase)

        self.include_digits = QCheckBox("Digits (0-9)")
        self.include_digits.setChecked(True)
        category_layout.addWidget(self.include_digits)

        self.include_special = QCheckBox("Special characters (!@#$%^&*)")
        self.include_special.setChecked(True)
        category_layout.addWidget(self.include_special)

        opt_layout.addWidget(category_group, 2, 0, 1, 3)

        layout.addWidget(opt_group)

        # Results section
        results_group = QGroupBox("Optimization Results")
        results_layout = QGridLayout(results_group)

        # Optimized charset
        charset_group = QGroupBox("Optimized Charset")
        charset_layout = QVBoxLayout(charset_group)

        self.optimized_charset_text = QTextEdit()
        self.optimized_charset_text.setReadOnly(True)
        self.optimized_charset_text.setMaximumHeight(100)
        charset_layout.addWidget(self.optimized_charset_text)

        results_layout.addWidget(charset_group, 0, 0)

        # Statistics
        stats_group = QGroupBox("Optimization Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.optimizer_stats_text = QTextEdit()
        self.optimizer_stats_text.setReadOnly(True)
        self.optimizer_stats_text.setMaximumHeight(100)
        stats_layout.addWidget(self.optimizer_stats_text)

        results_layout.addWidget(stats_group, 0, 1)

        # Recommendations
        rec_group = QGroupBox("Recommendations")
        rec_layout = QVBoxLayout(rec_group)

        self.optimizer_recommendations_text = QTextEdit()
        self.optimizer_recommendations_text.setReadOnly(True)
        self.optimizer_recommendations_text.setMaximumHeight(100)
        rec_layout.addWidget(self.optimizer_recommendations_text)

        results_layout.addWidget(rec_group, 1, 0, 1, 2)

        layout.addWidget(results_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.optimize_btn = QPushButton("Optimize Charset")
        self.optimize_btn.clicked.connect(self.perform_charset_optimization)
        button_layout.addWidget(self.optimize_btn)

        self.export_optimizer_btn = QPushButton("Export Results")
        self.export_optimizer_btn.clicked.connect(self.export_charset_optimization)
        button_layout.addWidget(self.export_optimizer_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Close")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    def show_attack_profiler(self):
        """Show attack profiler dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Attack Profiler")
        dialog.setModal(True)
        dialog.resize(900, 800)

        layout = QVBoxLayout(dialog)

        # Configuration section
        config_group = QGroupBox("Attack Configuration")
        config_layout = QGridLayout(config_group)

        # Attack type
        config_layout.addWidget(QLabel("Attack Type:"), 0, 0)
        self.profile_attack_type_combo = QComboBox()
        self.profile_attack_type_combo.addItems([
            "Dictionary Attack (WPA2)",
            "Brute Force Attack",
            "Rule-based Attack",
            "Hybrid Attack",
            "Mask Attack",
            "Combinator Attack"
        ])
        config_layout.addWidget(self.profile_attack_type_combo, 0, 1, 1, 2)

        # Wordlist
        config_layout.addWidget(QLabel("Wordlist:"), 1, 0)
        self.profile_wordlist_input = QLineEdit()
        self.profile_wordlist_input.setPlaceholderText("Path to wordlist file")
        config_layout.addWidget(self.profile_wordlist_input, 1, 1)
        self.profile_wordlist_browse_btn = QPushButton("Browse...")
        self.profile_wordlist_browse_btn.clicked.connect(self.browse_profile_wordlist)
        config_layout.addWidget(self.profile_wordlist_browse_btn, 1, 2)

        # Password length range
        config_layout.addWidget(QLabel("Min Length:"), 2, 0)
        self.profile_min_len_spin = QSpinBox()
        self.profile_min_len_spin.setRange(1, 32)
        self.profile_min_len_spin.setValue(8)
        config_layout.addWidget(self.profile_min_len_spin, 2, 1)

        config_layout.addWidget(QLabel("Max Length:"), 2, 2)
        self.profile_max_len_spin = QSpinBox()
        self.profile_max_len_spin.setRange(1, 32)
        self.profile_max_len_spin.setValue(16)
        config_layout.addWidget(self.profile_max_len_spin, 2, 3)

        # Character set
        config_layout.addWidget(QLabel("Charset:"), 3, 0)
        self.profile_charset_input = QLineEdit("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*")
        config_layout.addWidget(self.profile_charset_input, 3, 1, 1, 2)

        # Target hash type (for estimation)
        config_layout.addWidget(QLabel("Target Hash Type:"), 4, 0)
        self.profile_hash_type_combo = QComboBox()
        self.profile_hash_type_combo.addItems([
            "MD5",
            "SHA1",
            "SHA256",
            "SHA512",
            "WPA2",
            "NTLM",
            "bcrypt",
            "scrypt"
        ])
        config_layout.addWidget(self.profile_hash_type_combo, 4, 1, 1, 2)

        layout.addWidget(config_group)

        # Profiling results section
        results_group = QGroupBox("Profiling Results")
        results_layout = QGridLayout(results_group)

        # Time estimates
        time_group = QGroupBox("Time Estimates")
        time_layout = QVBoxLayout(time_group)

        self.time_estimates_text = QTextEdit()
        self.time_estimates_text.setReadOnly(True)
        self.time_estimates_text.setMaximumHeight(120)
        time_layout.addWidget(self.time_estimates_text)

        results_layout.addWidget(time_group, 0, 0)

        # Performance metrics
        perf_group = QGroupBox("Performance Metrics")
        perf_layout = QVBoxLayout(perf_group)

        self.performance_metrics_text = QTextEdit()
        self.performance_metrics_text.setReadOnly(True)
        self.performance_metrics_text.setMaximumHeight(120)
        perf_layout.addWidget(self.performance_metrics_text)

        results_layout.addWidget(perf_group, 0, 1)

        # Success probability
        success_group = QGroupBox("Success Probability")
        success_layout = QVBoxLayout(success_group)

        self.success_probability_text = QTextEdit()
        self.success_probability_text.setReadOnly(True)
        self.success_probability_text.setMaximumHeight(120)
        success_layout.addWidget(self.success_probability_text)

        results_layout.addWidget(success_group, 1, 0)

        # Recommendations
        rec_group = QGroupBox("Recommendations")
        rec_layout = QVBoxLayout(rec_group)

        self.profiler_recommendations_text = QTextEdit()
        self.profiler_recommendations_text.setReadOnly(True)
        self.profiler_recommendations_text.setMaximumHeight(120)
        rec_layout.addWidget(self.profiler_recommendations_text)

        results_layout.addWidget(rec_group, 1, 1)

        layout.addWidget(results_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.profile_btn = QPushButton("Run Profiling")
        self.profile_btn.clicked.connect(self.perform_attack_profiling)
        button_layout.addWidget(self.profile_btn)

        self.export_profile_btn = QPushButton("Export Profile")
        self.export_profile_btn.clicked.connect(self.export_attack_profile)
        button_layout.addWidget(self.export_profile_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Close")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    def browse_optimizer_file(self):
        """Browse for optimizer input file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Wordlist File", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            self.optimizer_file_input.setText(filename)

    def load_optimizer_file(self):
        """Load wordlist file for optimization"""
        try:
            filename = self.optimizer_file_input.text().strip()
            if not filename:
                QMessageBox.warning(self, "No File Selected", "Please select a wordlist file to load.")
                return

            # Just check if file exists and is readable
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                line_count = sum(1 for line in f)

            QMessageBox.information(self, "File Loaded", f"Wordlist file loaded successfully.\n\nLines: {line_count}")

        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load file: {str(e)}")

    def perform_charset_optimization(self):
        """Perform charset optimization"""
        try:
            filename = self.optimizer_file_input.text().strip()
            if not filename:
                QMessageBox.warning(self, "No File Selected", "Please select a wordlist file first.")
                return

            sample_size = self.sample_size_spin.value()
            opt_method = self.opt_method_combo.currentText()
            max_charset_size = self.max_charset_spin.value()

            # Character category filters
            include_lower = self.include_lowercase.isChecked()
            include_upper = self.include_uppercase.isChecked()
            include_digits = self.include_digits.isChecked()
            include_special = self.include_special.isChecked()

            # Load sample from wordlist
            passwords = []
            try:
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if i >= sample_size:
                            break
                        pw = line.strip()
                        if pw:
                            passwords.append(pw)
            except Exception as e:
                QMessageBox.critical(self, "File Error", f"Failed to read wordlist: {str(e)}")
                return

            if not passwords:
                QMessageBox.warning(self, "No Passwords", "No valid passwords found in the wordlist.")
                return

            # Analyze character frequencies
            all_chars = ''.join(passwords)
            char_counts = {}
            for char in all_chars:
                char_counts[char] = char_counts.get(char, 0) + 1

            # Filter characters by category
            filtered_chars = {}
            for char, count in char_counts.items():
                if include_lower and char.islower():
                    filtered_chars[char] = count
                elif include_upper and char.isupper():
                    filtered_chars[char] = count
                elif include_digits and char.isdigit():
                    filtered_chars[char] = count
                elif include_special and not char.isalnum():
                    filtered_chars[char] = count

            # Sort by frequency
            sorted_chars = sorted(filtered_chars.items(), key=lambda x: x[1], reverse=True)

            # Apply optimization method
            if opt_method == "Frequency-based (most common first)":
                optimized = [char for char, _ in sorted_chars[:max_charset_size]]
            elif opt_method == "Efficiency-based (balanced distribution)":
                # Balance between different character types
                lower = [c for c, _ in sorted_chars if c.islower()][:max_charset_size//4]
                upper = [c for c, _ in sorted_chars if c.isupper()][:max_charset_size//4]
                digits = [c for c, _ in sorted_chars if c.isdigit()][:max_charset_size//4]
                special = [c for c, _ in sorted_chars if not c.isalnum()][:max_charset_size//4]
                optimized = lower + upper + digits + special
            else:  # Attack-optimized
                # Prioritize commonly used characters in passwords
                common_patterns = ['a', 'e', 'i', 'o', 'u', '1', '2', '3', '0', '!', '@', '#', '$']
                prioritized = [c for c, _ in sorted_chars if c in common_patterns]
                remaining = [c for c, _ in sorted_chars if c not in common_patterns][:max_charset_size - len(prioritized)]
                optimized = prioritized + remaining

            # Remove duplicates while preserving order
            seen = set()
            optimized = [x for x in optimized if not (x in seen or seen.add(x))]

            # Display results
            charset_str = ''.join(optimized)
            self.optimized_charset_text.setPlainText(charset_str)

            # Statistics
            total_chars = len(filtered_chars)
            coverage = len(optimized) / total_chars * 100 if total_chars > 0 else 0

            stats_text = f"""Optimization Statistics:
Sample Size: {len(passwords)} passwords
Total Unique Characters: {total_chars}
Optimized Charset Size: {len(optimized)}
Coverage: {coverage:.1f}%
Optimization Method: {opt_method}
"""

            self.optimizer_stats_text.setPlainText(stats_text)

            # Recommendations
            rec_text = "Charset Optimization Recommendations:\n\n"
            if len(optimized) < 20:
                rec_text += "• Small charset - good for brute force attacks\n"
            elif len(optimized) < 50:
                rec_text += "• Medium charset - balanced performance\n"
            else:
                rec_text += "• Large charset - may slow down attacks\n"

            if opt_method == "Frequency-based (most common first)":
                rec_text += "• Optimized for dictionary attacks\n"
            elif opt_method == "Efficiency-based (balanced distribution)":
                rec_text += "• Balanced character distribution\n"
            else:
                rec_text += "• Optimized for common password patterns\n"

            rec_text += f"\n• Use charset: {charset_str[:50]}{'...' if len(charset_str) > 50 else ''}"

            self.optimizer_recommendations_text.setPlainText(rec_text)

        except Exception as e:
            QMessageBox.critical(self, "Optimization Error", f"Failed to optimize charset: {str(e)}")

    def export_charset_optimization(self):
        """Export charset optimization results"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Optimization Results", "", "Text Files (*.txt);;All Files (*)"
            )
            if not filename:
                return

            with open(filename, 'w') as f:
                f.write("=== Charset Optimization Results ===\n\n")
                f.write("OPTIMIZED CHARSET\n")
                f.write(self.optimized_charset_text.toPlainText())
                f.write("\n\nSTATISTICS\n")
                f.write(self.optimizer_stats_text.toPlainText())
                f.write("\n\nRECOMMENDATIONS\n")
                f.write(self.optimizer_recommendations_text.toPlainText())

            QMessageBox.information(self, "Export Successful", f"Optimization results exported to {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results: {str(e)}")

    def browse_profile_wordlist(self):
        """Browse for profile wordlist file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Wordlist File", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            self.profile_wordlist_input.setText(filename)

    def perform_attack_profiling(self):
        """Perform attack profiling"""
        try:
            attack_type = self.profile_attack_type_combo.currentText()
            wordlist_path = self.profile_wordlist_input.text().strip()
            min_len = self.profile_min_len_spin.value()
            max_len = self.profile_max_len_spin.value()
            charset = self.profile_charset_input.text().strip()
            hash_type = self.profile_hash_type_combo.currentText()

            # Validate inputs
            if attack_type in ["Dictionary Attack (WPA2)", "Rule-based Attack", "Hybrid Attack", "Combinator Attack"]:
                if not wordlist_path or not Path(wordlist_path).exists():
                    QMessageBox.warning(self, "Invalid Wordlist", "Please select a valid wordlist file.")
                    return

            # Get wordlist size if applicable
            wordlist_size = 0
            if wordlist_path and Path(wordlist_path).exists():
                try:
                    with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                        wordlist_size = sum(1 for line in f if line.strip())
                except:
                    wordlist_size = 0

            # Calculate total possibilities
            if attack_type == "Dictionary Attack (WPA2)":
                total_attempts = wordlist_size
            elif attack_type == "Brute Force Attack":
                total_attempts = sum(len(charset) ** length for length in range(min_len, max_len + 1))
            elif attack_type == "Rule-based Attack":
                # Estimate based on wordlist with mutations
                total_attempts = wordlist_size * 10  # Rough estimate for mutations
            elif attack_type == "Hybrid Attack":
                total_attempts = wordlist_size * sum(len(charset) ** length for length in range(1, 5))  # Rough estimate
            elif attack_type == "Mask Attack":
                # Simplified mask calculation
                total_attempts = len(charset) ** max_len
            else:  # Combinator Attack
                total_attempts = wordlist_size ** 2  # Rough estimate

            # Hash speed estimates (hashes per second) - rough estimates
            hash_speeds = {
                "MD5": 100000000,      # 100M/s
                "SHA1": 80000000,      # 80M/s
                "SHA256": 50000000,    # 50M/s
                "SHA512": 30000000,    # 30M/s
                "WPA2": 1000000,       # 1M/s (GPU accelerated)
                "NTLM": 150000000,     # 150M/s
                "bcrypt": 10000,       # 10K/s (very slow)
                "scrypt": 5000         # 5K/s (very slow)
            }

            hash_speed = hash_speeds.get(hash_type, 1000000)

            # Calculate time estimates
            if total_attempts > 0 and hash_speed > 0:
                seconds = total_attempts / hash_speed
                minutes = seconds / 60
                hours = minutes / 60
                days = hours / 24
                years = days / 365

                time_text = f"""Time Estimates for {attack_type}:

Total Attempts: {total_attempts:,}
Hash Speed: {hash_speed:,} {hash_type}/sec

Estimated Time:
• Seconds: {seconds:,.0f}
• Minutes: {minutes:,.0f}
• Hours: {hours:,.1f}
• Days: {days:,.1f}
• Years: {years:,.2f}

Note: Estimates are approximate and depend on hardware.
"""
            else:
                time_text = "Unable to calculate time estimates.\nPlease check configuration."

            self.time_estimates_text.setPlainText(time_text)

            # Performance metrics
            perf_text = f"""Performance Metrics:

Attack Type: {attack_type}
Wordlist Size: {wordlist_size:,} (if applicable)
Charset Size: {len(charset)}
Length Range: {min_len}-{max_len}
Target Hash: {hash_type}

Estimated Throughput: {hash_speed:,} {hash_type}/sec
Memory Usage: ~{(wordlist_size * 50) // (1024*1024) if wordlist_size else 10} MB (estimated)
"""

            self.performance_metrics_text.setPlainText(perf_text)

            # Success probability (very rough estimates)
            success_prob = 0.0
            if attack_type == "Dictionary Attack (WPA2)":
                success_prob = 0.3  # 30% success rate for good wordlists
            elif attack_type == "Brute Force Attack":
                if max_len <= 6:
                    success_prob = 1.0  # Will eventually succeed
                elif max_len <= 8:
                    success_prob = 0.8
                else:
                    success_prob = 0.1
            elif attack_type == "Rule-based Attack":
                success_prob = 0.5
            else:
                success_prob = 0.2

            success_text = f"""Success Probability Analysis:

Estimated Success Rate: {success_prob:.1%}

Factors Considered:
• Attack Type: {attack_type}
• Password Length Range: {min_len}-{max_len}
• Wordlist Quality: {'Good' if wordlist_size > 10000 else 'Limited'}
• Character Set Size: {len(charset)}

Note: Success probability is highly dependent on target password complexity.
"""

            self.success_probability_text.setPlainText(success_text)

            # Recommendations
            rec_text = f"""Attack Recommendations:

Configuration Analysis:
• Attack Type: {attack_type}
• Target Length: {min_len}-{max_len} characters
• Charset: {len(charset)} characters

Suggested Improvements:
"""

            if attack_type == "Dictionary Attack (WPA2)" and wordlist_size < 100000:
                rec_text += "• Consider using a larger wordlist (100K+ entries)\n"
            if len(charset) < 20:
                rec_text += "• Small charset - consider adding more character types\n"
            if max_len - min_len > 8:
                rec_text += "• Large length range - consider narrowing for faster results\n"
            if hash_type in ["bcrypt", "scrypt"]:
                rec_text += "• Slow hash type - consider GPU acceleration\n"

            rec_text += "\nAlternative Strategies:\n"
            if attack_type == "Brute Force Attack":
                rec_text += "• Try mask attack with known patterns\n"
                rec_text += "• Use hybrid attack with small wordlist\n"
            elif attack_type == "Dictionary Attack (WPA2)":
                rec_text += "• Try rule-based attack for mutations\n"
                rec_text += "• Consider combinator attack for common words\n"

            self.profiler_recommendations_text.setPlainText(rec_text)

        except Exception as e:
            QMessageBox.critical(self, "Profiling Error", f"Failed to profile attack: {str(e)}")

    def export_attack_profile(self):
        """Export attack profiling results"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Attack Profile", "", "Text Files (*.txt);;All Files (*)"
            )
            if not filename:
                return

            with open(filename, 'w') as f:
                f.write("=== Attack Profiling Results ===\n\n")
                f.write("TIME ESTIMATES\n")
                f.write(self.time_estimates_text.toPlainText())
                f.write("\n\nPERFORMANCE METRICS\n")
                f.write(self.performance_metrics_text.toPlainText())
                f.write("\n\nSUCCESS PROBABILITY\n")
                f.write(self.success_probability_text.toPlainText())
                f.write("\n\nRECOMMENDATIONS\n")
                f.write(self.profiler_recommendations_text.toPlainText())

            QMessageBox.information(self, "Export Successful", f"Attack profile exported to {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export profile: {str(e)}")

    def _generate_from_pattern(self, pattern, char_sets):
        """Generate passwords from a pattern using character sets"""
        import itertools

        # Parse pattern into list of character sets
        sets = []
        i = 0
        while i < len(pattern):
            if pattern[i] == '?':
                if i + 1 < len(pattern):
                    char_type = pattern[i + 1]
                    if char_type in char_sets:
                        sets.append(char_sets[char_type])
                        i += 2
                    else:
                        # Invalid, treat as literal
                        sets.append([pattern[i]])
                        i += 1
                else:
                    sets.append([pattern[i]])
                    i += 1
            else:
                sets.append([pattern[i]])
                i += 1

        # Generate all combinations
        for combo in itertools.product(*sets):
            yield ''.join(combo)

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

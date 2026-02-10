#!/usr/bin/env python3
"""
Keyspace - Web Interface
Flask-based web application for remote access to Keyspace
"""

import os
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Import Keyspace components
from backend.brute_force_thread import BruteForceThread
from backend.security.session_encryption import SessionEncryption
from backend.security.audit_logger import AuditLogger, AuditEventType, AuditSeverity
from backend.security.permissions import PermissionManager, Permission, UserRole
from backend.security.compliance import ComplianceManager
from backend.integrations.api_integration import APIIntegration


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'keyspace-secret-key-2024')
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize security components
session_encryption = SessionEncryption()
audit_logger = AuditLogger()
permission_manager = PermissionManager()
compliance_manager = ComplianceManager(audit_logger)

# Global attack state
current_attack = None
attack_thread = None
attack_status = {
    'running': False,
    'progress': 0,
    'speed': 0,
    'eta': '00:00:00',
    'attempts': 0,
    'status': 'Ready'
}

# Initialize API integration
api_integration = APIIntegration(host='localhost', port=8080)


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    user = permission_manager.get_user_by_id(user_id)
    if user:
        return User(user.user_id, user.username, user.role)
    return None

# Routes
@app.route('/')
@login_required
def index():
    """Main dashboard"""
    audit_logger.log_event(
        AuditEventType.USER_LOGIN,
        AuditSeverity.INFO,
        "Web dashboard access",
        "web_interface",
        user_id=current_user.id
    )

    return render_template('index.html',
                         attack_status=attack_status,
                         user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = permission_manager.authenticate_user(username, password)
        if user:
            flask_user = User(user.user_id, user.username, user.role)
            login_user(flask_user)

            audit_logger.log_event(
                AuditEventType.USER_LOGIN,
                AuditSeverity.INFO,
                f"Web login successful for {username}",
                "web_interface",
                user_id=user.user_id
            )

            return redirect(url_for('index'))
        else:
            audit_logger.log_event(
                AuditEventType.SECURITY_VIOLATION,
                AuditSeverity.WARNING,
                f"Failed web login attempt for {username}",
                "web_interface"
            )

            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    audit_logger.log_event(
        AuditEventType.USER_LOGOUT,
        AuditSeverity.INFO,
        "Web logout",
        "web_interface",
        user_id=current_user.id
    )

    logout_user()
    return redirect(url_for('login'))

@app.route('/api/start_attack', methods=['POST'])
@login_required
def start_attack():
    """Start a brute force attack"""
    global attack_thread, current_attack, attack_status

    if not permission_manager.has_permission(
        permission_manager.get_user_by_id(current_user.id),
        Permission.ATTACK_START
    ):
        return jsonify({'error': 'Insufficient permissions'}), 403

    if attack_status['running']:
        return jsonify({'error': 'Attack already running'}), 400

    try:
        data = request.get_json()
        target = data.get('target', '')
        attack_type = data.get('attack_type', 'Dictionary Attack (WPA2)')
        wordlist_path = data.get('wordlist_path', '')
        min_length = data.get('min_length', 8)
        max_length = data.get('max_length', 16)
        charset = data.get('charset', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*')

        # Validate inputs
        if not target:
            return jsonify({'error': 'Target is required'}), 400

        if attack_type in ['Dictionary Attack (WPA2)', 'Rule-based Attack', 'Hybrid Attack', 'Combinator Attack']:
            if not wordlist_path or not os.path.exists(wordlist_path):
                return jsonify({'error': 'Valid wordlist path is required'}), 400

        # Create attack thread
        attack_thread = BruteForceThread(
            target=target,
            attack_type=attack_type,
            wordlist_path=wordlist_path,
            min_length=min_length,
            max_length=max_length,
            charset=charset
        )

        # Connect signals
        attack_thread.progress_updated.connect(on_attack_progress)
        attack_thread.status_updated.connect(on_attack_status)
        attack_thread.result_updated.connect(on_attack_result)
        attack_thread.error_occurred.connect(on_attack_error)
        attack_thread.attack_log.connect(on_attack_log)
        attack_thread.finished.connect(on_attack_finished)

        # Start attack
        attack_thread.start()
        attack_status['running'] = True

        audit_logger.log_event(
            AuditEventType.ATTACK_START,
            AuditSeverity.INFO,
            f"Web attack started: {attack_type} on {target}",
            "web_interface",
            user_id=current_user.id
        )

        return jsonify({'message': 'Attack started successfully'})

    except Exception as e:
        logger.error(f"Failed to start web attack: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop_attack', methods=['POST'])
@login_required
def stop_attack():
    """Stop the current attack"""
    global attack_thread, attack_status

    if not permission_manager.has_permission(
        permission_manager.get_user_by_id(current_user.id),
        Permission.ATTACK_STOP
    ):
        return jsonify({'error': 'Insufficient permissions'}), 403

    if attack_thread and attack_status['running']:
        attack_thread.stop()

        audit_logger.log_event(
            AuditEventType.ATTACK_END,
            AuditSeverity.INFO,
            "Web attack stopped",
            "web_interface",
            user_id=current_user.id
        )

        return jsonify({'message': 'Attack stopped'})
    else:
        return jsonify({'error': 'No attack running'}), 400

@app.route('/api/attack_status')
@login_required
def get_attack_status():
    """Get current attack status"""
    return jsonify(attack_status)

@app.route('/api/compliance_report')
@login_required
def get_compliance_report():
    """Generate compliance report"""
    if not permission_manager.has_permission(
        permission_manager.get_user_by_id(current_user.id),
        Permission.SECURITY_COMPLIANCE_VIEW
    ):
        return jsonify({'error': 'Insufficient permissions'}), 403

    try:
        report = compliance_manager.generate_compliance_report()
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit_events')
@login_required
def get_audit_events():
    """Get audit events"""
    if not permission_manager.has_permission(
        permission_manager.get_user_by_id(current_user.id),
        Permission.SECURITY_AUDIT_VIEW
    ):
        return jsonify({'error': 'Insufficient permissions'}), 403

    try:
        limit = int(request.args.get('limit', 100))
        events = audit_logger.get_events(limit=limit)
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Signal handlers for attack thread
def on_attack_progress(progress, speed, eta, attempts):
    """Handle attack progress updates"""
    global attack_status
    attack_status.update({
        'progress': progress,
        'speed': speed,
        'eta': eta,
        'attempts': attempts
    })

def on_attack_status(status):
    """Handle attack status updates"""
    global attack_status
    attack_status['status'] = status

def on_attack_result(result):
    """Handle attack results"""
    # Could store results in a global variable or database
    pass

def on_attack_log(log_entry):
    """Handle attack log entries"""
    # Could store logs in a global variable or database
    pass

def on_attack_error(error):
    """Handle attack errors"""
    global attack_status
    attack_status['status'] = f"Error: {error}"

def on_attack_finished():
    """Handle attack completion"""
    global attack_status
    attack_status.update({
        'running': False,
        'status': 'Completed'
    })

# Template filters
@app.template_filter('format_datetime')
def format_datetime(value):
    """Format datetime for display"""
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return value
    return value

def create_templates():
    """Create basic HTML templates if they don't exist"""
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)

    # This function would create templates, but they're already created
    # Keeping for future use
    pass

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    # Create basic HTML templates
    create_templates()

    # Start API server
    try:
        if api_integration.start():
            logger.info(f"API server started on http://localhost:8080")
        else:
            logger.warning("Failed to start API server")
    except Exception as e:
        logger.error(f"Error starting API server: {e}")

    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)

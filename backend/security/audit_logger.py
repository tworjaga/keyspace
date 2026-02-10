"""
Audit Logging Module
Provides comprehensive audit logging for security events and user actions
"""

import json
import logging
import hashlib
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class AuditEventType(Enum):
    """Types of audit events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    ATTACK_START = "attack_start"
    ATTACK_END = "attack_end"
    ATTACK_PAUSE = "attack_pause"
    ATTACK_RESUME = "attack_resume"
    CONFIG_CHANGE = "config_change"
    FILE_ACCESS = "file_access"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"
    PASSWORD_FOUND = "password_found"
    SECURITY_VIOLATION = "security_violation"
    SYSTEM_ERROR = "system_error"


class AuditSeverity(Enum):
    """Severity levels for audit events"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Represents an audit event"""
    timestamp: str
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: str
    session_id: str
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: str = ""
    user_agent: str = ""
    checksum: str = ""

    def __post_init__(self):
        """Generate checksum after initialization"""
        if not self.checksum:
            event_dict = asdict(self)
            event_dict.pop('checksum', None)  # Remove checksum from calculation
            event_str = json.dumps(event_dict, sort_keys=True, default=str)
            self.checksum = hashlib.sha256(event_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Create from dictionary"""
        # Convert string enums back to enum objects
        data['event_type'] = AuditEventType(data['event_type'])
        data['severity'] = AuditSeverity(data['severity'])
        return cls(**data)


class AuditLogger:
    """Thread-safe audit logging system"""

    def __init__(self, log_dir: str = "logs/audit", max_file_size: int = 10*1024*1024):
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size
        self._lock = threading.Lock()
        self._current_user = "system"
        self._current_session = ""

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)

        # Don't propagate to root logger
        self.logger.propagate = False

    def set_user_context(self, user_id: str, session_id: str = ""):
        """Set current user and session context"""
        with self._lock:
            self._current_user = user_id or "system"
            self._current_session = session_id

    def log_event(self, event_type: AuditEventType, severity: AuditSeverity,
                  action: str, resource: str, details: Dict[str, Any] = None,
                  user_id: str = None, session_id: str = None) -> bool:
        """Log an audit event"""
        try:
            event = AuditEvent(
                timestamp=datetime.now().isoformat(),
                event_type=event_type,
                severity=severity,
                user_id=user_id or self._current_user,
                session_id=session_id or self._current_session,
                action=action,
                resource=resource,
                details=details or {}
            )

            # Write to file
            self._write_event(event)

            # Also log to standard logger
            log_message = f"AUDIT: {event.event_type.value} - {action} on {resource}"
            if severity == AuditSeverity.ERROR:
                self.logger.error(log_message)
            elif severity == AuditSeverity.WARNING:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)

            return True

        except Exception as e:
            print(f"Failed to log audit event: {e}")
            return False

    def _write_event(self, event: AuditEvent):
        """Write audit event to file"""
        with self._lock:
            # Create log filename based on date
            date_str = datetime.now().strftime("%Y%m%d")
            log_file = self.log_dir / f"audit_{date_str}.log"

            # Check if we need to rotate the file
            if log_file.exists() and log_file.stat().st_size > self.max_file_size:
                # Rotate file
                backup_file = self.log_dir / f"audit_{date_str}_{int(datetime.now().timestamp())}.log"
                log_file.rename(backup_file)
                log_file = self.log_dir / f"audit_{date_str}.log"

            # Write event as JSON
            with open(log_file, 'a', encoding='utf-8') as f:
                json.dump(event.to_dict(), f, default=str)
                f.write('\n')

    def get_events(self, start_date: str = None, end_date: str = None,
                   event_type: AuditEventType = None, user_id: str = None,
                   limit: int = 1000) -> List[AuditEvent]:
        """Retrieve audit events with optional filtering"""
        events = []

        try:
            # Find relevant log files
            log_files = list(self.log_dir.glob("audit_*.log"))
            log_files.sort(reverse=True)  # Most recent first

            for log_file in log_files:
                if len(events) >= limit:
                    break

                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if len(events) >= limit:
                                break

                            line = line.strip()
                            if not line:
                                continue

                            try:
                                event_data = json.loads(line)
                                event = AuditEvent.from_dict(event_data)

                                # Apply filters
                                if start_date and event.timestamp < start_date:
                                    continue
                                if end_date and event.timestamp > end_date:
                                    continue
                                if event_type and event.event_type != event_type:
                                    continue
                                if user_id and event.user_id != user_id:
                                    continue

                                events.append(event)

                            except (json.JSONDecodeError, KeyError, ValueError):
                                continue  # Skip corrupted lines

                except Exception:
                    continue  # Skip files that can't be read

        except Exception as e:
            print(f"Failed to retrieve audit events: {e}")

        return events

    def generate_audit_report(self, start_date: str, end_date: str,
                             output_file: str = None) -> Dict[str, Any]:
        """Generate a comprehensive audit report"""
        try:
            events = self.get_events(start_date=start_date, end_date=end_date, limit=10000)

            report = {
                "report_period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "summary": {
                    "total_events": len(events),
                    "events_by_type": {},
                    "events_by_severity": {},
                    "events_by_user": {},
                    "critical_events": []
                },
                "events": [event.to_dict() for event in events[:1000]]  # Limit for report
            }

            # Analyze events
            for event in events:
                # Count by type
                event_type = event.event_type.value
                report["summary"]["events_by_type"][event_type] = \
                    report["summary"]["events_by_type"].get(event_type, 0) + 1

                # Count by severity
                severity = event.severity.value
                report["summary"]["events_by_severity"][severity] = \
                    report["summary"]["events_by_severity"].get(severity, 0) + 1

                # Count by user
                report["summary"]["events_by_user"][event.user_id] = \
                    report["summary"]["events_by_user"].get(event.user_id, 0) + 1

                # Track critical events
                if event.severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
                    report["summary"]["critical_events"].append(event.to_dict())

            # Save report if requested
            if output_file:
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2, default=str)

            return report

        except Exception as e:
            print(f"Failed to generate audit report: {e}")
            return {"error": str(e)}

    def verify_log_integrity(self, log_file: str = None) -> Dict[str, Any]:
        """Verify the integrity of audit logs"""
        result = {
            "valid_entries": 0,
            "invalid_entries": 0,
            "corrupted_files": [],
            "integrity_status": "unknown"
        }

        try:
            log_files = [Path(log_file)] if log_file else list(self.log_dir.glob("audit_*.log"))

            for file_path in log_files:
                if not file_path.exists():
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if not line:
                                continue

                            try:
                                event_data = json.loads(line)
                                event = AuditEvent.from_dict(event_data)

                                # Verify checksum
                                expected_checksum = event.checksum
                                event.checksum = ""
                                actual_checksum = hashlib.sha256(
                                    json.dumps(asdict(event), sort_keys=True, default=str).encode()
                                ).hexdigest()

                                if expected_checksum == actual_checksum:
                                    result["valid_entries"] += 1
                                else:
                                    result["invalid_entries"] += 1

                            except Exception:
                                result["invalid_entries"] += 1

                except Exception:
                    result["corrupted_files"].append(str(file_path))

            # Determine overall status
            total_entries = result["valid_entries"] + result["invalid_entries"]
            if result["invalid_entries"] == 0 and not result["corrupted_files"]:
                result["integrity_status"] = "good"
            elif result["invalid_entries"] / max(total_entries, 1) < 0.01:  # Less than 1% corruption
                result["integrity_status"] = "acceptable"
            else:
                result["integrity_status"] = "compromised"

        except Exception as e:
            result["error"] = str(e)

        return result

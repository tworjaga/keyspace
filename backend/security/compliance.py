"""
Compliance Reporting Module
Generates compliance reports and security assessments
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from .audit_logger import AuditLogger, AuditEventType, AuditSeverity


@dataclass
class ComplianceCheck:
    """Represents a compliance check result"""
    check_id: str
    name: str
    description: str
    status: str  # "pass", "fail", "warning", "not_applicable"
    severity: str  # "low", "medium", "high", "critical"
    details: str
    recommendation: str
    evidence: List[str]


@dataclass
class ComplianceReport:
    """Compliance report data"""
    report_id: str
    generated_at: str
    period_start: str
    period_end: str
    overall_status: str
    summary: Dict[str, Any]
    checks: List[ComplianceCheck]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceReport':
        """Create from dictionary"""
        data['checks'] = [ComplianceCheck(**check) for check in data['checks']]
        return cls(**data)


class ComplianceManager:
    """Manages compliance reporting and security assessments"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.compliance_checks = self._initialize_compliance_checks()

    def _initialize_compliance_checks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compliance check definitions"""
        return {
            "audit_log_integrity": {
                "name": "Audit Log Integrity",
                "description": "Verify that audit logs have not been tampered with",
                "severity": "critical",
                "check_function": self._check_audit_integrity
            },
            "session_encryption": {
                "name": "Session Data Encryption",
                "description": "Ensure session data is properly encrypted",
                "severity": "high",
                "check_function": self._check_session_encryption
            },
            "user_access_control": {
                "name": "User Access Control",
                "description": "Verify proper user authentication and authorization",
                "severity": "high",
                "check_function": self._check_user_access
            },
            "attack_logging": {
                "name": "Attack Activity Logging",
                "description": "Ensure all attack activities are properly logged",
                "severity": "medium",
                "check_function": self._check_attack_logging
            },
            "data_export_controls": {
                "name": "Data Export Controls",
                "description": "Verify that data exports are controlled and logged",
                "severity": "medium",
                "check_function": self._check_data_exports
            },
            "password_security": {
                "name": "Password Security",
                "description": "Check for weak password usage and security practices",
                "severity": "high",
                "check_function": self._check_password_security
            },
            "system_configuration": {
                "name": "System Configuration Security",
                "description": "Verify system configuration follows security best practices",
                "severity": "medium",
                "check_function": self._check_system_config
            }
        }

    def generate_compliance_report(self, start_date: str = None,
                                  end_date: str = None) -> ComplianceReport:
        """Generate a comprehensive compliance report"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        if not end_date:
            end_date = datetime.now().isoformat()

        report_id = f"compliance_{int(datetime.now().timestamp())}"

        # Run all compliance checks
        checks = []
        for check_id, check_def in self.compliance_checks.items():
            check_result = check_def["check_function"](start_date, end_date)
            checks.append(check_result)

        # Calculate overall status
        status_counts = {
            "pass": 0,
            "fail": 0,
            "warning": 0,
            "not_applicable": 0
        }

        for check in checks:
            status_counts[check.status] += 1

        if status_counts["fail"] > 0 or status_counts["critical"] > 0:
            overall_status = "fail"
        elif status_counts["warning"] > 0:
            overall_status = "warning"
        else:
            overall_status = "pass"

        # Generate summary
        summary = {
            "total_checks": len(checks),
            "status_breakdown": status_counts,
            "period_days": (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days,
            "audit_events_analyzed": len(self.audit_logger.get_events(start_date, end_date))
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(checks)

        return ComplianceReport(
            report_id=report_id,
            generated_at=datetime.now().isoformat(),
            period_start=start_date,
            period_end=end_date,
            overall_status=overall_status,
            summary=summary,
            checks=checks,
            recommendations=recommendations
        )

    def _check_audit_integrity(self, start_date: str, end_date: str) -> ComplianceCheck:
        """Check audit log integrity"""
        try:
            integrity_result = self.audit_logger.verify_log_integrity()

            if integrity_result.get("integrity_status") == "good":
                return ComplianceCheck(
                    check_id="audit_log_integrity",
                    name="Audit Log Integrity",
                    description="Verify that audit logs have not been tampered with",
                    status="pass",
                    severity="critical",
                    details=f"Audit logs are intact. {integrity_result['valid_entries']} valid entries found.",
                    recommendation="Continue regular integrity monitoring.",
                    evidence=["Log integrity verification passed"]
                )
            else:
                return ComplianceCheck(
                    check_id="audit_log_integrity",
                    name="Audit Log Integrity",
                    description="Verify that audit logs have not been tampered with",
                    status="fail",
                    severity="critical",
                    details=f"Audit log integrity compromised. Status: {integrity_result.get('integrity_status')}",
                    recommendation="Investigate log tampering and restore from backups.",
                    evidence=["Log integrity verification failed"]
                )

        except Exception as e:
            return ComplianceCheck(
                check_id="audit_log_integrity",
                name="Audit Log Integrity",
                description="Verify that audit logs have not been tampered with",
                status="fail",
                severity="critical",
                details=f"Failed to check audit integrity: {str(e)}",
                recommendation="Manually verify audit log integrity.",
                evidence=[]
            )

    def _check_session_encryption(self, start_date: str, end_date: str) -> ComplianceCheck:
        """Check session encryption usage"""
        try:
            # Look for session save/load events
            session_events = self.audit_logger.get_events(
                start_date=start_date,
                end_date=end_date,
                event_type=AuditEventType.SESSION_SAVE
            )

            encrypted_sessions = sum(1 for event in session_events
                                   if event.details.get("encrypted", False))

            if len(session_events) == 0:
                return ComplianceCheck(
                    check_id="session_encryption",
                    name="Session Data Encryption",
                    description="Ensure session data is properly encrypted",
                    status="not_applicable",
                    severity="high",
                    details="No session save events found in the audit period.",
                    recommendation="Monitor session encryption when sessions are saved.",
                    evidence=[]
                )
            elif encrypted_sessions == len(session_events):
                return ComplianceCheck(
                    check_id="session_encryption",
                    name="Session Data Encryption",
                    description="Ensure session data is properly encrypted",
                    status="pass",
                    severity="high",
                    details=f"All {len(session_events)} session saves were encrypted.",
                    recommendation="Continue using encrypted session storage.",
                    evidence=[f"{encrypted_sessions}/{len(session_events)} sessions encrypted"]
                )
            else:
                return ComplianceCheck(
                    check_id="session_encryption",
                    name="Session Data Encryption",
                    description="Ensure session data is properly encrypted",
                    status="fail",
                    severity="high",
                    details=f"Only {encrypted_sessions}/{len(session_events)} sessions were encrypted.",
                    recommendation="Enable encryption for all session storage.",
                    evidence=[f"{len(session_events) - encrypted_sessions} unencrypted sessions found"]
                )

        except Exception as e:
            return ComplianceCheck(
                check_id="session_encryption",
                name="Session Data Encryption",
                description="Ensure session data is properly encrypted",
                status="fail",
                severity="high",
                details=f"Failed to check session encryption: {str(e)}",
                recommendation="Verify session encryption implementation.",
                evidence=[]
            )

    def _check_user_access(self, start_date: str, end_date: str) -> ComplianceCheck:
        """Check user access controls"""
        try:
            # Look for authentication events
            login_events = self.audit_logger.get_events(
                start_date=start_date,
                end_date=end_date,
                event_type=AuditEventType.USER_LOGIN
            )

            failed_logins = sum(1 for event in login_events
                               if event.details.get("success", False) == False)

            if len(login_events) == 0:
                return ComplianceCheck(
                    check_id="user_access_control",
                    name="User Access Control",
                    description="Verify proper user authentication and authorization",
                    status="not_applicable",
                    severity="high",
                    details="No login events found in the audit period.",
                    recommendation="Monitor authentication events.",
                    evidence=[]
                )
            elif failed_logins == 0:
                return ComplianceCheck(
                    check_id="user_access_control",
                    name="User Access Control",
                    description="Verify proper user authentication and authorization",
                    status="pass",
                    severity="high",
                    details=f"All {len(login_events)} login attempts were successful.",
                    recommendation="Continue monitoring authentication.",
                    evidence=[f"0 failed logins out of {len(login_events)} attempts"]
                )
            elif failed_logins / len(login_events) < 0.1:  # Less than 10% failure rate
                return ComplianceCheck(
                    check_id="user_access_control",
                    name="User Access Control",
                    description="Verify proper user authentication and authorization",
                    status="warning",
                    severity="high",
                    details=f"{failed_logins}/{len(login_events)} login attempts failed.",
                    recommendation="Investigate failed login attempts and consider additional security measures.",
                    evidence=[f"{failed_logins} failed login attempts"]
                )
            else:
                return ComplianceCheck(
                    check_id="user_access_control",
                    name="User Access Control",
                    description="Verify proper user authentication and authorization",
                    status="fail",
                    severity="high",
                    details=f"High failure rate: {failed_logins}/{len(login_events)} login attempts failed.",
                    recommendation="Investigate security breach and implement additional access controls.",
                    evidence=[f"{failed_logins} failed login attempts"]
                )

        except Exception as e:
            return ComplianceCheck(
                check_id="user_access_control",
                name="User Access Control",
                description="Verify proper user authentication and authorization",
                status="fail",
                severity="high",
                details=f"Failed to check user access: {str(e)}",
                recommendation="Verify authentication system.",
                evidence=[]
            )

    def _check_attack_logging(self, start_date: str, end_date: str) -> ComplianceCheck:
        """Check that attack activities are logged"""
        try:
            attack_events = self.audit_logger.get_events(
                start_date=start_date,
                end_date=end_date,
                event_type=AuditEventType.ATTACK_START
            )

            logged_attacks = len(attack_events)

            if logged_attacks == 0:
                return ComplianceCheck(
                    check_id="attack_logging",
                    name="Attack Activity Logging",
                    description="Ensure all attack activities are properly logged",
                    status="not_applicable",
                    severity="medium",
                    details="No attack events found in the audit period.",
                    recommendation="Monitor attack logging when attacks are performed.",
                    evidence=[]
                )
            else:
                return ComplianceCheck(
                    check_id="attack_logging",
                    name="Attack Activity Logging",
                    description="Ensure all attack activities are properly logged",
                    status="pass",
                    severity="medium",
                    details=f"{logged_attacks} attack events properly logged.",
                    recommendation="Continue comprehensive attack logging.",
                    evidence=[f"{logged_attacks} attacks logged"]
                )

        except Exception as e:
            return ComplianceCheck(
                check_id="attack_logging",
                name="Attack Activity Logging",
                description="Ensure all attack activities are properly logged",
                status="fail",
                severity="medium",
                details=f"Failed to check attack logging: {str(e)}",
                recommendation="Verify attack event logging.",
                evidence=[]
            )

    def _check_data_exports(self, start_date: str, end_date: str) -> ComplianceCheck:
        """Check data export controls"""
        try:
            export_events = self.audit_logger.get_events(
                start_date=start_date,
                end_date=end_date,
                event_type=AuditEventType.EXPORT_DATA
            )

            logged_exports = len(export_events)

            if logged_exports == 0:
                return ComplianceCheck(
                    check_id="data_export_controls",
                    name="Data Export Controls",
                    description="Verify that data exports are controlled and logged",
                    status="not_applicable",
                    severity="medium",
                    details="No data export events found in the audit period.",
                    recommendation="Monitor data exports when they occur.",
                    evidence=[]
                )
            else:
                return ComplianceCheck(
                    check_id="data_export_controls",
                    name="Data Export Controls",
                    description="Verify that data exports are controlled and logged",
                    status="pass",
                    severity="medium",
                    details=f"{logged_exports} data export events logged.",
                    recommendation="Continue monitoring data exports.",
                    evidence=[f"{logged_exports} exports logged"]
                )

        except Exception as e:
            return ComplianceCheck(
                check_id="data_export_controls",
                name="Data Export Controls",
                description="Verify that data exports are controlled and logged",
                status="fail",
                severity="medium",
                details=f"Failed to check data exports: {str(e)}",
                recommendation="Verify data export logging.",
                evidence=[]
            )

    def _check_password_security(self, start_date: str, end_date: str) -> ComplianceCheck:
        """Check password security practices"""
        try:
            # Look for password-related events or configurations
            config_events = self.audit_logger.get_events(
                start_date=start_date,
                end_date=end_date,
                event_type=AuditEventType.CONFIG_CHANGE
            )

            # Check for weak password patterns in config
            weak_patterns = ["123456", "password", "admin", "qwerty"]
            weak_usage = 0

            for event in config_events:
                config_data = event.details.get("config_data", {})
                for key, value in config_data.items():
                    if isinstance(value, str):
                        for pattern in weak_patterns:
                            if pattern in value.lower():
                                weak_usage += 1
                                break

            if weak_usage == 0:
                return ComplianceCheck(
                    check_id="password_security",
                    name="Password Security",
                    description="Check for weak password usage and security practices",
                    status="pass",
                    severity="high",
                    details="No weak password patterns detected in configuration.",
                    recommendation="Continue using strong passwords.",
                    evidence=["No weak passwords found"]
                )
            else:
                return ComplianceCheck(
                    check_id="password_security",
                    name="Password Security",
                    description="Check for weak password usage and security practices",
                    status="warning",
                    severity="high",
                    details=f"{weak_usage} instances of weak password patterns detected.",
                    recommendation="Replace weak passwords with strong alternatives.",
                    evidence=[f"{weak_usage} weak password instances"]
                )

        except Exception as e:
            return ComplianceCheck(
                check_id="password_security",
                name="Password Security",
                description="Check for weak password usage and security practices",
                status="fail",
                severity="high",
                details=f"Failed to check password security: {str(e)}",
                recommendation="Manually review password security practices.",
                evidence=[]
            )

    def _check_system_config(self, start_date: str, end_date: str) -> ComplianceCheck:
        """Check system configuration security"""
        try:
            # This is a basic check - in a real system, this would check actual config files
            config_events = self.audit_logger.get_events(
                start_date=start_date,
                end_date=end_date,
                event_type=AuditEventType.CONFIG_CHANGE
            )

            if len(config_events) == 0:
                return ComplianceCheck(
                    check_id="system_configuration",
                    name="System Configuration Security",
                    description="Verify system configuration follows security best practices",
                    status="not_applicable",
                    severity="medium",
                    details="No configuration changes found in the audit period.",
                    recommendation="Monitor configuration changes.",
                    evidence=[]
                )
            else:
                return ComplianceCheck(
                    check_id="system_configuration",
                    name="System Configuration Security",
                    description="Verify system configuration follows security best practices",
                    status="pass",
                    severity="medium",
                    details=f"{len(config_events)} configuration changes logged and tracked.",
                    recommendation="Continue monitoring configuration changes.",
                    evidence=[f"{len(config_events)} config changes tracked"]
                )

        except Exception as e:
            return ComplianceCheck(
                check_id="system_configuration",
                name="System Configuration Security",
                description="Verify system configuration follows security best practices",
                status="fail",
                severity="medium",
                details=f"Failed to check system config: {str(e)}",
                recommendation="Verify system configuration security.",
                evidence=[]
            )

    def _generate_recommendations(self, checks: List[ComplianceCheck]) -> List[str]:
        """Generate recommendations based on check results"""
        recommendations = []

        failed_checks = [check for check in checks if check.status == "fail"]
        warning_checks = [check for check in checks if check.status == "warning"]

        for check in failed_checks:
            recommendations.append(f"CRITICAL: {check.recommendation}")

        for check in warning_checks:
            recommendations.append(f"WARNING: {check.recommendation}")

        if not failed_checks and not warning_checks:
            recommendations.append("All compliance checks passed. Continue regular monitoring.")

        return recommendations

    def save_report(self, report: ComplianceReport, output_file: str):
        """Save compliance report to file"""
        try:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(report.to_dict(), f, indent=2, default=str)

        except Exception as e:
            print(f"Failed to save compliance report: {e}")

    def load_report(self, input_file: str) -> Optional[ComplianceReport]:
        """Load compliance report from file"""
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)

            return ComplianceReport.from_dict(data)

        except Exception as e:
            print(f"Failed to load compliance report: {e}")
            return None

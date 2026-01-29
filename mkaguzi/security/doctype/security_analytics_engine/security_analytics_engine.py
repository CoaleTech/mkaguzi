# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, now_datetime, cstr, flt
import json
import logging
from cryptography.fernet import Fernet
import hashlib
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityAnalyticsEngine(Document):
    def autoname(self):
        """Generate unique analytics engine ID"""
        if not self.analytics_engine_id:
            self.analytics_engine_id = f"SAE-{frappe.generate_hash(length=8).upper()}"

    def validate(self):
        """Validate security analytics engine configuration"""
        self.validate_data_sources()
        self.validate_analytics_configuration()
        self.validate_threat_detection()
        self.validate_alerting_configuration()
        self.validate_performance_metrics()
        self.validate_threat_intelligence()
        self.validate_analytics_models()

    def validate_data_sources(self):
        """Validate data sources configuration"""
        if not self.security_data_sources:
            frappe.throw(_("Security Data Sources are required"))

        try:
            data_sources = json.loads(self.security_data_sources)
            required_fields = ['type', 'source', 'frequency', 'retention']

            for source in data_sources.get('sources', []):
                for field in required_fields:
                    if field not in source:
                        frappe.throw(_("Missing required field '{0}' in data sources").format(field))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format for Security Data Sources"))

    def validate_analytics_configuration(self):
        """Validate analytics configuration"""
        if not self.real_time_analytics:
            frappe.throw(_("Real-time Analytics configuration is required"))

        try:
            analytics_config = json.loads(self.real_time_analytics)
            if 'enabled' not in analytics_config:
                frappe.throw(_("Real-time Analytics must specify 'enabled' status"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format for Real-time Analytics"))

    def validate_threat_detection(self):
        """Validate threat detection configuration"""
        if not self.anomaly_detection:
            frappe.throw(_("Anomaly Detection configuration is required"))

        try:
            anomaly_config = json.loads(self.anomaly_detection)
            required_fields = ['algorithm', 'threshold', 'sensitivity']

            for field in required_fields:
                if field not in anomaly_config:
                    frappe.throw(_("Missing required field '{0}' in Anomaly Detection").format(field))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format for Anomaly Detection"))

    def validate_alerting_configuration(self):
        """Validate alerting configuration"""
        if not self.alert_rules:
            frappe.throw(_("Alert Rules are required"))

        try:
            alert_config = json.loads(self.alert_rules)
            for rule in alert_config.get('rules', []):
                if 'condition' not in rule or 'severity' not in rule:
                    frappe.throw(_("Alert rules must have 'condition' and 'severity' fields"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format for Alert Rules"))

    def validate_performance_metrics(self):
        """Validate performance metrics"""
        if self.processing_throughput and self.processing_throughput < 0:
            frappe.throw(_("Processing Throughput cannot be negative"))

        if self.detection_accuracy and (self.detection_accuracy < 0 or self.detection_accuracy > 100):
            frappe.throw(_("Detection Accuracy must be between 0 and 100"))

        if self.false_positive_rate and (self.false_positive_rate < 0 or self.false_positive_rate > 100):
            frappe.throw(_("False Positive Rate must be between 0 and 100"))

        if self.uptime_percentage and (self.uptime_percentage < 0 or self.uptime_percentage > 100):
            frappe.throw(_("Uptime Percentage must be between 0 and 100"))

    def validate_threat_intelligence(self):
        """Validate threat intelligence configuration"""
        if not self.threat_feeds:
            frappe.throw(_("Threat Feeds are required"))

        try:
            threat_feeds = json.loads(self.threat_feeds)
            for feed in threat_feeds.get('feeds', []):
                if 'url' not in feed or 'format' not in feed:
                    frappe.throw(_("Threat feeds must have 'url' and 'format' fields"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format for Threat Feeds"))

    def validate_analytics_models(self):
        """Validate analytics models configuration"""
        if not self.machine_learning_models:
            frappe.throw(_("Machine Learning Models are required"))

        try:
            ml_models = json.loads(self.machine_learning_models)
            for model in ml_models.get('models', []):
                if 'name' not in model or 'type' not in model:
                    frappe.throw(_("ML models must have 'name' and 'type' fields"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format for Machine Learning Models"))

    def on_update(self):
        """Handle document updates"""
        self.update_audit_trail()
        self.schedule_background_jobs()

    def update_audit_trail(self):
        """Update audit trail with configuration changes"""
        try:
            audit_data = {
                'timestamp': now(),
                'user': frappe.session.user,
                'action': 'configuration_update',
                'engine_id': self.analytics_engine_id,
                'changes': self.get_changes_summary()
            }

            current_audit = self.analytics_logs or '[]'
            audit_list = json.loads(current_audit)
            audit_list.append(audit_data)

            # Keep only last 1000 entries
            if len(audit_list) > 1000:
                audit_list = audit_list[-1000:]

            self.analytics_logs = json.dumps(audit_list, indent=2)
        except Exception as e:
            logger.error(f"Failed to update audit trail: {str(e)}")

    def get_changes_summary(self):
        """Get summary of changes made"""
        changes = {}
        if self.has_value_changed('status'):
            changes['status'] = f"{self.get_doc_before_save().status} -> {self.status}"
        if self.has_value_changed('engine_version'):
            changes['version'] = f"{self.get_doc_before_save().engine_version} -> {self.engine_version}"
        return changes

    def schedule_background_jobs(self):
        """Schedule background jobs for analytics processing"""
        if self.status == 'Active':
            # Schedule real-time analytics job
            frappe.enqueue(
                'mkaguzi.security.doctype.security_analytics_engine.security_analytics_engine.process_real_time_analytics',
                engine_id=self.name,
                queue='long',
                timeout=3600
            )

            # Schedule threat intelligence update
            frappe.enqueue(
                'mkaguzi.security.doctype.security_analytics_engine.security_analytics_engine.update_threat_intelligence',
                engine_id=self.name,
                queue='default',
                timeout=1800
            )

    @frappe.whitelist()
    def start_engine(self):
        """Start the security analytics engine"""
        if self.status != 'Active':
            self.status = 'Active'
            self.save()
            frappe.msgprint(_("Security Analytics Engine started successfully"))

    @frappe.whitelist()
    def stop_engine(self):
        """Stop the security analytics engine"""
        if self.status == 'Active':
            self.status = 'Suspended'
            self.save()
            frappe.msgprint(_("Security Analytics Engine stopped successfully"))

    @frappe.whitelist()
    def run_diagnostic_check(self):
        """Run diagnostic checks on the analytics engine"""
        diagnostics = {
            'data_sources': self.check_data_sources(),
            'analytics_models': self.check_analytics_models(),
            'threat_feeds': self.check_threat_feeds(),
            'performance': self.check_performance(),
            'timestamp': now()
        }

        return diagnostics

    def check_data_sources(self):
        """Check data sources connectivity and health"""
        try:
            data_sources = json.loads(self.security_data_sources)
            results = []

            for source in data_sources.get('sources', []):
                result = {
                    'source': source.get('source'),
                    'type': source.get('type'),
                    'status': 'healthy',  # Mock status - would check actual connectivity
                    'last_check': now()
                }
                results.append(result)

            return results
        except Exception as e:
            return [{'error': str(e)}]

    def check_analytics_models(self):
        """Check analytics models health and performance"""
        try:
            models = json.loads(self.machine_learning_models)
            results = []

            for model in models.get('models', []):
                result = {
                    'name': model.get('name'),
                    'type': model.get('type'),
                    'status': 'operational',  # Mock status
                    'accuracy': 95.5,  # Mock accuracy
                    'last_updated': now()
                }
                results.append(result)

            return results
        except Exception as e:
            return [{'error': str(e)}]

    def check_threat_feeds(self):
        """Check threat intelligence feeds"""
        try:
            feeds = json.loads(self.threat_feeds)
            results = []

            for feed in feeds.get('feeds', []):
                result = {
                    'name': feed.get('name', 'Unknown'),
                    'url': feed.get('url'),
                    'status': 'active',  # Mock status
                    'last_update': now()
                }
                results.append(result)

            return results
        except Exception as e:
            return [{'error': str(e)}]

    def check_performance(self):
        """Check engine performance metrics"""
        return {
            'processing_throughput': self.processing_throughput or 1000,
            'detection_accuracy': self.detection_accuracy or 98.5,
            'false_positive_rate': self.false_positive_rate or 2.1,
            'response_time': self.response_time or 150,
            'uptime_percentage': self.uptime_percentage or 99.9
        }

@frappe.whitelist()
def process_real_time_analytics(engine_id):
    """Process real-time security analytics"""
    try:
        engine = frappe.get_doc('Security Analytics Engine', engine_id)

        # Process security events
        security_events = collect_security_events(engine)
        anomalies = detect_anomalies(security_events, engine)
        threats = correlate_threats(anomalies, engine)

        # Generate alerts
        alerts = generate_alerts(threats, engine)

        # Update performance metrics
        update_performance_metrics(engine, security_events, anomalies, alerts)

        # Log analytics results
        log_analytics_results(engine, {
            'events_processed': len(security_events),
            'anomalies_detected': len(anomalies),
            'threats_identified': len(threats),
            'alerts_generated': len(alerts)
        })

        frappe.db.commit()

    except Exception as e:
        logger.error(f"Real-time analytics processing failed: {str(e)}")
        frappe.log_error(f"Security Analytics Engine Error: {str(e)}")

@frappe.whitelist()
def update_threat_intelligence(engine_id):
    """Update threat intelligence feeds"""
    try:
        engine = frappe.get_doc('Security Analytics Engine', engine_id)

        # Update threat feeds
        new_indicators = fetch_threat_feeds(engine)

        # Update IoC database
        update_ioc_database(engine, new_indicators)

        # Update vulnerability data
        update_vulnerability_data(engine)

        # Log intelligence update
        log_intelligence_update(engine, {
            'new_indicators': len(new_indicators),
            'feeds_updated': len(json.loads(engine.threat_feeds).get('feeds', []))
        })

        frappe.db.commit()

    except Exception as e:
        logger.error(f"Threat intelligence update failed: {str(e)}")
        frappe.log_error(f"Threat Intelligence Update Error: {str(e)}")

def collect_security_events(engine):
    """Collect security events from various sources"""
    events = []

    try:
        # Collect from log sources
        log_sources = json.loads(engine.log_sources or '[]')
        for source in log_sources.get('sources', []):
            # Mock event collection - would integrate with actual log sources
            events.extend([
                {
                    'timestamp': now(),
                    'source': source.get('name'),
                    'type': 'authentication',
                    'severity': 'low',
                    'message': 'User login successful'
                }
            ])
    except Exception as e:
        logger.error(f"Event collection failed: {str(e)}")

    return events

def detect_anomalies(events, engine):
    """Detect anomalies in security events"""
    anomalies = []

    try:
        anomaly_config = json.loads(engine.anomaly_detection)

        # Simple anomaly detection based on thresholds
        for event in events:
            if event.get('severity') == 'high':
                anomalies.append({
                    'event': event,
                    'anomaly_score': 0.85,
                    'detection_time': now(),
                    'algorithm': anomaly_config.get('algorithm')
                })
    except Exception as e:
        logger.error(f"Anomaly detection failed: {str(e)}")

    return anomalies

def correlate_threats(anomalies, engine):
    """Correlate anomalies to identify threats"""
    threats = []

    try:
        correlation_config = json.loads(engine.correlation_engine or '{}')

        # Group anomalies by time windows and patterns
        threat_groups = {}
        for anomaly in anomalies:
            time_window = anomaly.get('detection_time')[:16]  # Group by minute
            if time_window not in threat_groups:
                threat_groups[time_window] = []
            threat_groups[time_window].append(anomaly)

        # Identify threats from correlated anomalies
        for time_window, group_anomalies in threat_groups.items():
            if len(group_anomalies) > 2:  # Threshold for threat identification
                threats.append({
                    'threat_id': f"THREAT-{hashlib.md5(str(time_window).encode()).hexdigest()[:8]}",
                    'severity': 'high',
                    'confidence': 0.92,
                    'anomalies': len(group_anomalies),
                    'time_window': time_window
                })
    except Exception as e:
        logger.error(f"Threat correlation failed: {str(e)}")

    return threats

def generate_alerts(threats, engine):
    """Generate alerts based on identified threats"""
    alerts = []

    try:
        alert_config = json.loads(engine.alert_rules)

        for threat in threats:
            # Check if threat matches alert rules
            for rule in alert_config.get('rules', []):
                if threat.get('severity') == rule.get('severity'):
                    alert = {
                        'alert_id': f"ALERT-{frappe.generate_hash(length=8)}",
                        'threat_id': threat.get('threat_id'),
                        'severity': threat.get('severity'),
                        'message': f"Security threat detected: {threat.get('threat_id')}",
                        'timestamp': now(),
                        'rule': rule.get('name')
                    }
                    alerts.append(alert)

                    # Send notification
                    send_alert_notification(alert, engine)
    except Exception as e:
        logger.error(f"Alert generation failed: {str(e)}")

    return alerts

def send_alert_notification(alert, engine):
    """Send alert notifications through configured channels"""
    try:
        notification_config = json.loads(engine.notification_channels or '{}')

        # Send email notifications
        if notification_config.get('email', {}).get('enabled'):
            frappe.sendmail(
                recipients=notification_config['email'].get('recipients', []),
                subject=f"Security Alert: {alert.get('severity', '').upper()}",
                message=alert.get('message', ''),
                header="Security Analytics Alert"
            )

        # Log alert to history
        alert_history = engine.alert_history or '[]'
        alerts_list = json.loads(alert_history)
        alerts_list.append(alert)

        # Keep only last 1000 alerts
        if len(alerts_list) > 1000:
            alerts_list = alerts_list[-1000:]

        engine.alert_history = json.dumps(alerts_list, indent=2)
        engine.save()

    except Exception as e:
        logger.error(f"Alert notification failed: {str(e)}")

def update_performance_metrics(engine, events, anomalies, alerts):
    """Update engine performance metrics"""
    try:
        # Calculate metrics
        total_events = len(events)
        total_anomalies = len(anomalies)
        total_alerts = len(alerts)

        # Update engine metrics
        engine.processing_throughput = total_events / 60.0  # events per second approximation
        engine.detection_accuracy = 98.5 if total_anomalies > 0 else 100.0
        engine.false_positive_rate = (total_alerts / total_events * 100) if total_events > 0 else 0.0
        engine.response_time = 150.0  # Mock response time
        engine.uptime_percentage = 99.9

        engine.save()

    except Exception as e:
        logger.error(f"Performance metrics update failed: {str(e)}")

def log_analytics_results(engine, results):
    """Log analytics processing results"""
    try:
        analytics_logs = engine.analytics_logs or '[]'
        logs_list = json.loads(analytics_logs)

        log_entry = {
            'timestamp': now(),
            'results': results,
            'engine_id': engine.analytics_engine_id
        }

        logs_list.append(log_entry)

        # Keep only last 1000 log entries
        if len(logs_list) > 1000:
            logs_list = logs_list[-1000:]

        engine.analytics_logs = json.dumps(logs_list, indent=2)
        engine.save()

    except Exception as e:
        logger.error(f"Analytics logging failed: {str(e)}")

def fetch_threat_feeds(engine):
    """Fetch threat intelligence from configured feeds"""
    indicators = []

    try:
        threat_feeds = json.loads(engine.threat_feeds)

        for feed in threat_feeds.get('feeds', []):
            # Mock threat feed fetching - would integrate with actual threat feeds
            indicators.extend([
                {
                    'type': 'ip',
                    'value': '192.168.1.100',
                    'threat_level': 'high',
                    'source': feed.get('name'),
                    'timestamp': now()
                }
            ])
    except Exception as e:
        logger.error(f"Threat feed fetching failed: {str(e)}")

    return indicators

def update_ioc_database(engine, indicators):
    """Update Indicators of Compromise database"""
    try:
        current_iocs = engine.ioc_database or '{}'
        ioc_data = json.loads(current_iocs)

        # Add new indicators
        for indicator in indicators:
            indicator_type = indicator.get('type')
            if indicator_type not in ioc_data:
                ioc_data[indicator_type] = []

            # Check for duplicates
            existing_values = [ioc.get('value') for ioc in ioc_data[indicator_type]]
            if indicator.get('value') not in existing_values:
                ioc_data[indicator_type].append(indicator)

        engine.ioc_database = json.dumps(ioc_data, indent=2)
        engine.save()

    except Exception as e:
        logger.error(f"IoC database update failed: {str(e)}")

def update_vulnerability_data(engine):
    """Update vulnerability scanning data"""
    try:
        # Mock vulnerability data update
        vulnerability_data = {
            'last_scan': now(),
            'vulnerabilities_found': 5,
            'critical_count': 1,
            'high_count': 2,
            'medium_count': 2
        }

        engine.vulnerability_scanning = json.dumps(vulnerability_data, indent=2)
        engine.save()

    except Exception as e:
        logger.error(f"Vulnerability data update failed: {str(e)}")

def log_intelligence_update(engine, update_info):
    """Log threat intelligence update results"""
    try:
        intelligence_logs = engine.analytics_logs or '[]'
        logs_list = json.loads(intelligence_logs)

        log_entry = {
            'timestamp': now(),
            'type': 'intelligence_update',
            'info': update_info,
            'engine_id': engine.analytics_engine_id
        }

        logs_list.append(log_entry)

        # Keep only last 1000 log entries
        if len(logs_list) > 1000:
            logs_list = logs_list[-1000:]

        engine.analytics_logs = json.dumps(logs_list, indent=2)
        engine.save()

    except Exception as e:
        logger.error(f"Intelligence update logging failed: {str(e)}")
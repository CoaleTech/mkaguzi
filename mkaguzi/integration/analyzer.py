# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, now_datetime, cstr, flt, getdate, add_days, date_diff
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import pandas as pd
from decimal import Decimal

logger = logging.getLogger(__name__)

class AuditDataAnalyzer:
    """
    Analyzes audit trail data for patterns, anomalies, and insights
    """

    def __init__(self):
        self.risk_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2
        }

    def analyze_audit_trails(self, filters=None, date_range=None):
        """
        Comprehensive analysis of audit trail data

        Args:
            filters: Dictionary of filters to apply
            date_range: Tuple of (start_date, end_date)

        Returns:
            dict: Analysis results
        """
        try:
            # Get audit trail data
            audit_data = self._get_audit_trail_data(filters, date_range)

            if not audit_data:
                return {"message": "No audit data found for the specified criteria"}

            analysis_results = {
                'summary': self._generate_summary_stats(audit_data),
                'risk_analysis': self._analyze_risk_patterns(audit_data),
                'user_activity': self._analyze_user_activity(audit_data),
                'doctype_patterns': self._analyze_doctype_patterns(audit_data),
                'temporal_patterns': self._analyze_temporal_patterns(audit_data),
                'anomaly_detection': self._detect_anomalies(audit_data),
                'recommendations': self._generate_recommendations(audit_data)
            }

            return analysis_results

        except Exception as e:
            logger.error(f"Audit analysis failed: {str(e)}")
            return {"error": str(e)}

    def generate_audit_report(self, report_type, filters=None, date_range=None):
        """
        Generate specific audit reports

        Args:
            report_type: Type of report ('risk', 'activity', 'compliance', 'anomaly')
            filters: Dictionary of filters
            date_range: Date range tuple

        Returns:
            dict: Report data
        """
        try:
            audit_data = self._get_audit_trail_data(filters, date_range)

            if report_type == 'risk':
                return self._generate_risk_report(audit_data)
            elif report_type == 'activity':
                return self._generate_activity_report(audit_data)
            elif report_type == 'compliance':
                return self._generate_compliance_report(audit_data)
            elif report_type == 'anomaly':
                return self._generate_anomaly_report(audit_data)
            else:
                return {"error": f"Unknown report type: {report_type}"}

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return {"error": str(e)}

    def _get_audit_trail_data(self, filters=None, date_range=None):
        """Get audit trail data with filters"""
        try:
            conditions = []

            if filters:
                if filters.get('doctype'):
                    conditions.append(f"doctype_name = '{filters['doctype']}'")
                if filters.get('user'):
                    conditions.append(f"user = '{filters['user']}'")
                if filters.get('action'):
                    conditions.append(f"action = '{filters['action']}'")
                if filters.get('risk_level'):
                    conditions.append(f"risk_level = '{filters['risk_level']}'")

            if date_range:
                start_date, end_date = date_range
                conditions.append(f"creation >= '{start_date}' AND creation <= '{end_date}'")

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            query = f"""
                SELECT name, doctype_name, docname, user, action, risk_level,
                       risk_score, changes_summary, creation, modified
                FROM `tabAudit Trail`
                WHERE {where_clause}
                ORDER BY creation DESC
                LIMIT 10000
            """

            return frappe.db.sql(query, as_dict=True)

        except Exception as e:
            logger.error(f"Failed to get audit trail data: {str(e)}")
            return []

    def _generate_summary_stats(self, audit_data):
        """Generate summary statistics"""
        try:
            total_entries = len(audit_data)
            unique_doctypes = len(set(d['doctype_name'] for d in audit_data))
            unique_users = len(set(d['user'] for d in audit_data))
            unique_actions = len(set(d['action'] for d in audit_data))

            # Risk level distribution
            risk_levels = Counter(d['risk_level'] for d in audit_data)

            # Date range
            if audit_data:
                earliest = min(d['creation'] for d in audit_data)
                latest = max(d['creation'] for d in audit_data)
            else:
                earliest = latest = None

            return {
                'total_entries': total_entries,
                'unique_doctypes': unique_doctypes,
                'unique_users': unique_users,
                'unique_actions': unique_actions,
                'risk_distribution': dict(risk_levels),
                'date_range': {'earliest': earliest, 'latest': latest}
            }

        except Exception as e:
            logger.error(f"Failed to generate summary stats: {str(e)}")
            return {}

    def _analyze_risk_patterns(self, audit_data):
        """Analyze risk patterns in audit data"""
        try:
            risk_analysis = {
                'high_risk_activities': [],
                'risk_by_doctype': {},
                'risk_by_user': {},
                'risk_trends': []
            }

            # High risk activities
            high_risk_entries = [d for d in audit_data if d.get('risk_level') == 'High']
            risk_analysis['high_risk_activities'] = high_risk_entries[:10]  # Top 10

            # Risk by doctype
            doctype_risks = defaultdict(list)
            for entry in audit_data:
                doctype_risks[entry['doctype_name']].append(entry.get('risk_score', 0))

            for doctype, scores in doctype_risks.items():
                avg_risk = sum(scores) / len(scores) if scores else 0
                risk_analysis['risk_by_doctype'][doctype] = {
                    'average_risk': round(avg_risk, 2),
                    'total_entries': len(scores),
                    'high_risk_count': len([s for s in scores if s >= self.risk_thresholds['high']])
                }

            # Risk by user
            user_risks = defaultdict(list)
            for entry in audit_data:
                user_risks[entry['user']].append(entry.get('risk_score', 0))

            for user, scores in user_risks.items():
                avg_risk = sum(scores) / len(scores) if scores else 0
                risk_analysis['risk_by_user'][user] = {
                    'average_risk': round(avg_risk, 2),
                    'total_entries': len(scores),
                    'high_risk_count': len([s for s in scores if s >= self.risk_thresholds['high']])
                }

            return risk_analysis

        except Exception as e:
            logger.error(f"Failed to analyze risk patterns: {str(e)}")
            return {}

    def _analyze_user_activity(self, audit_data):
        """Analyze user activity patterns"""
        try:
            user_activity = {
                'most_active_users': [],
                'user_action_patterns': {},
                'suspicious_patterns': []
            }

            # User activity counts
            user_counts = Counter(d['user'] for d in audit_data)
            user_activity['most_active_users'] = user_counts.most_common(10)

            # User action patterns
            user_actions = defaultdict(Counter)
            for entry in audit_data:
                user_actions[entry['user']][entry['action']] += 1

            user_activity['user_action_patterns'] = dict(user_actions)

            # Detect suspicious patterns (e.g., unusual login times, bulk operations)
            suspicious = self._detect_suspicious_user_patterns(audit_data)
            user_activity['suspicious_patterns'] = suspicious

            return user_activity

        except Exception as e:
            logger.error(f"Failed to analyze user activity: {str(e)}")
            return {}

    def _analyze_doctype_patterns(self, audit_data):
        """Analyze patterns by doctype"""
        try:
            doctype_patterns = {
                'most_audited_doctypes': [],
                'doctype_action_distribution': {},
                'doctype_risk_patterns': {}
            }

            # Most audited doctypes
            doctype_counts = Counter(d['doctype_name'] for d in audit_data)
            doctype_patterns['most_audited_doctypes'] = doctype_counts.most_common(10)

            # Action distribution by doctype
            doctype_actions = defaultdict(Counter)
            for entry in audit_data:
                doctype_actions[entry['doctype_name']][entry['action']] += 1

            doctype_patterns['doctype_action_distribution'] = dict(doctype_actions)

            # Risk patterns by doctype
            doctype_risks = defaultdict(list)
            for entry in audit_data:
                doctype_risks[entry['doctype_name']].append({
                    'action': entry['action'],
                    'risk_level': entry.get('risk_level'),
                    'risk_score': entry.get('risk_score', 0)
                })

            for doctype, patterns in doctype_risks.items():
                risk_summary = {
                    'total_actions': len(patterns),
                    'risky_actions': len([p for p in patterns if p['risk_score'] >= self.risk_thresholds['medium']]),
                    'most_common_risky_action': None
                }

                risky_actions = [p['action'] for p in patterns if p['risk_score'] >= self.risk_thresholds['medium']]
                if risky_actions:
                    risk_summary['most_common_risky_action'] = Counter(risky_actions).most_common(1)[0][0]

                doctype_patterns['doctype_risk_patterns'][doctype] = risk_summary

            return doctype_patterns

        except Exception as e:
            logger.error(f"Failed to analyze doctype patterns: {str(e)}")
            return {}

    def _analyze_temporal_patterns(self, audit_data):
        """Analyze temporal patterns in audit data"""
        try:
            temporal_patterns = {
                'hourly_distribution': {},
                'daily_distribution': {},
                'weekly_patterns': {},
                'peak_activity_times': []
            }

            # Convert to datetime objects
            timestamps = []
            for entry in audit_data:
                if isinstance(entry['creation'], str):
                    timestamps.append(getdate(entry['creation']))
                else:
                    timestamps.append(entry['creation'])

            # Hourly distribution
            hourly_counts = Counter(ts.hour for ts in timestamps)
            temporal_patterns['hourly_distribution'] = dict(hourly_counts)

            # Daily distribution
            daily_counts = Counter(ts.strftime('%A') for ts in timestamps)
            temporal_patterns['daily_distribution'] = dict(daily_counts)

            # Peak activity times (top 3 hours)
            peak_hours = hourly_counts.most_common(3)
            temporal_patterns['peak_activity_times'] = peak_hours

            return temporal_patterns

        except Exception as e:
            logger.error(f"Failed to analyze temporal patterns: {str(e)}")
            return {}

    def _detect_anomalies(self, audit_data):
        """Detect anomalies in audit data"""
        try:
            anomalies = {
                'unusual_user_activity': [],
                'bulk_operations': [],
                'high_risk_clusters': [],
                'suspicious_timings': []
            }

            # Detect bulk operations (many operations by same user in short time)
            bulk_ops = self._detect_bulk_operations(audit_data)
            anomalies['bulk_operations'] = bulk_ops

            # Detect unusual user activity
            unusual_activity = self._detect_unusual_user_activity(audit_data)
            anomalies['unusual_user_activity'] = unusual_activity

            # Detect high risk clusters
            risk_clusters = self._detect_risk_clusters(audit_data)
            anomalies['high_risk_clusters'] = risk_clusters

            return anomalies

        except Exception as e:
            logger.error(f"Failed to detect anomalies: {str(e)}")
            return {}

    def _detect_bulk_operations(self, audit_data):
        """Detect bulk operations"""
        try:
            bulk_threshold = 10  # operations per minute
            bulk_operations = []

            # Group by user and time window
            user_time_groups = defaultdict(list)

            for entry in audit_data:
                user = entry['user']
                timestamp = entry['creation']
                if isinstance(timestamp, str):
                    timestamp = getdate(timestamp)

                # Round to minute
                minute_key = timestamp.replace(second=0, microsecond=0)
                user_time_groups[(user, minute_key)].append(entry)

            for (user, minute), entries in user_time_groups.items():
                if len(entries) >= bulk_threshold:
                    bulk_operations.append({
                        'user': user,
                        'timestamp': minute,
                        'operation_count': len(entries),
                        'operations': [e['action'] for e in entries[:5]]  # Sample
                    })

            return bulk_operations

        except Exception as e:
            logger.error(f"Failed to detect bulk operations: {str(e)}")
            return []

    def _detect_unusual_user_activity(self, audit_data):
        """Detect unusual user activity patterns"""
        try:
            unusual_patterns = []

            # Calculate baseline activity per user
            user_activity = defaultdict(list)
            for entry in audit_data:
                user_activity[entry['user']].append(entry['creation'])

            # Simple anomaly detection: users with activity outside normal hours
            for user, timestamps in user_activity.items():
                hours = []
                for ts in timestamps:
                    if isinstance(ts, str):
                        ts = getdate(ts)
                    hours.append(ts.hour)

                # Check for activity during unusual hours (e.g., 2-5 AM)
                unusual_hours = [h for h in hours if 2 <= h <= 5]
                if unusual_hours and len(unusual_hours) > len(hours) * 0.1:  # >10% of activity
                    unusual_patterns.append({
                        'user': user,
                        'unusual_hour_activity': len(unusual_hours),
                        'total_activity': len(hours),
                        'pattern': 'Late night activity'
                    })

            return unusual_patterns

        except Exception as e:
            logger.error(f"Failed to detect unusual user activity: {str(e)}")
            return []

    def _detect_risk_clusters(self, audit_data):
        """Detect clusters of high-risk activities"""
        try:
            risk_clusters = []

            # Sort by time
            sorted_data = sorted(audit_data, key=lambda x: x['creation'])

            # Look for sequences of high-risk activities
            cluster_threshold = 5  # within 5 minutes
            current_cluster = []

            for entry in sorted_data:
                if entry.get('risk_score', 0) >= self.risk_thresholds['high']:
                    if current_cluster:
                        # Check time difference
                        last_time = current_cluster[-1]['creation']
                        current_time = entry['creation']

                        if isinstance(last_time, str):
                            last_time = getdate(last_time)
                        if isinstance(current_time, str):
                            current_time = getdate(current_time)

                        if (current_time - last_time).total_seconds() <= cluster_threshold * 60:
                            current_cluster.append(entry)
                        else:
                            # End current cluster if it has enough entries
                            if len(current_cluster) >= 3:
                                risk_clusters.append({
                                    'start_time': current_cluster[0]['creation'],
                                    'end_time': current_cluster[-1]['creation'],
                                    'count': len(current_cluster),
                                    'users': list(set(c['user'] for c in current_cluster))
                                })
                            current_cluster = [entry]
                    else:
                        current_cluster = [entry]

            # Check final cluster
            if len(current_cluster) >= 3:
                risk_clusters.append({
                    'start_time': current_cluster[0]['creation'],
                    'end_time': current_cluster[-1]['creation'],
                    'count': len(current_cluster),
                    'users': list(set(c['user'] for c in current_cluster))
                })

            return risk_clusters

        except Exception as e:
            logger.error(f"Failed to detect risk clusters: {str(e)}")
            return []

    def _detect_suspicious_user_patterns(self, audit_data):
        """Detect suspicious user patterns"""
        try:
            suspicious_patterns = []

            # Check for users with high-risk activity
            user_risk_scores = defaultdict(list)
            for entry in audit_data:
                user_risk_scores[entry['user']].append(entry.get('risk_score', 0))

            for user, scores in user_risk_scores.items():
                avg_risk = sum(scores) / len(scores) if scores else 0
                high_risk_count = len([s for s in scores if s >= self.risk_thresholds['high']])

                if high_risk_count >= 5:  # Threshold for suspicious
                    suspicious_patterns.append({
                        'user': user,
                        'high_risk_activities': high_risk_count,
                        'average_risk_score': round(avg_risk, 2),
                        'pattern': 'High frequency of high-risk activities'
                    })

            return suspicious_patterns

        except Exception as e:
            logger.error(f"Failed to detect suspicious patterns: {str(e)}")
            return []

    def _generate_recommendations(self, audit_data):
        """Generate recommendations based on analysis"""
        try:
            recommendations = []

            # Analyze risk patterns for recommendations
            risk_analysis = self._analyze_risk_patterns(audit_data)

            # High risk doctype recommendations
            high_risk_doctypes = [
                doctype for doctype, data in risk_analysis.get('risk_by_doctype', {}).items()
                if data.get('average_risk', 0) >= self.risk_thresholds['high']
            ]

            if high_risk_doctypes:
                recommendations.append({
                    'type': 'security',
                    'priority': 'high',
                    'title': 'Review High-Risk Doctypes',
                    'description': f'Consider additional controls for: {", ".join(high_risk_doctypes[:3])}',
                    'action_items': [
                        'Implement additional approval workflows',
                        'Add field-level audit logging',
                        'Review user permissions'
                    ]
                })

            # User activity recommendations
            user_analysis = self._analyze_user_activity(audit_data)
            suspicious_users = user_analysis.get('suspicious_patterns', [])

            if suspicious_users:
                recommendations.append({
                    'type': 'monitoring',
                    'priority': 'high',
                    'title': 'Monitor Suspicious User Activity',
                    'description': f'Found {len(suspicious_users)} users with suspicious patterns',
                    'action_items': [
                        'Review user access logs',
                        'Implement additional authentication',
                        'Monitor for continued suspicious activity'
                    ]
                })

            # Temporal pattern recommendations
            temporal_analysis = self._analyze_temporal_patterns(audit_data)
            peak_hours = temporal_analysis.get('peak_activity_times', [])

            if peak_hours:
                peak_hour = peak_hours[0][0] if peak_hours else None
                if peak_hour and (peak_hour < 6 or peak_hour > 22):  # Outside business hours
                    recommendations.append({
                        'type': 'operational',
                        'priority': 'medium',
                        'title': 'Review After-Hours Activity',
                        'description': f'Significant activity detected at hour {peak_hour}',
                        'action_items': [
                            'Verify business justification for after-hours access',
                            'Implement time-based access controls',
                            'Review activity logs for this period'
                        ]
                    })

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            return []

    def _generate_risk_report(self, audit_data):
        """Generate risk-focused report"""
        risk_analysis = self._analyze_risk_patterns(audit_data)

        return {
            'report_type': 'Risk Analysis Report',
            'generated_at': now(),
            'high_risk_activities': risk_analysis.get('high_risk_activities', []),
            'risk_by_doctype': risk_analysis.get('risk_by_doctype', {}),
            'risk_by_user': risk_analysis.get('risk_by_user', {}),
            'recommendations': self._generate_recommendations(audit_data)
        }

    def _generate_activity_report(self, audit_data):
        """Generate activity-focused report"""
        activity_analysis = self._analyze_user_activity(audit_data)
        temporal_analysis = self._analyze_temporal_patterns(audit_data)

        return {
            'report_type': 'User Activity Report',
            'generated_at': now(),
            'most_active_users': activity_analysis.get('most_active_users', []),
            'user_action_patterns': activity_analysis.get('user_action_patterns', {}),
            'temporal_patterns': temporal_analysis,
            'suspicious_patterns': activity_analysis.get('suspicious_patterns', [])
        }

    def _generate_compliance_report(self, audit_data):
        """Generate compliance-focused report"""
        summary = self._generate_summary_stats(audit_data)
        doctype_patterns = self._analyze_doctype_patterns(audit_data)

        return {
            'report_type': 'Compliance Report',
            'generated_at': now(),
            'audit_coverage': summary,
            'doctype_compliance': doctype_patterns,
            'compliance_gaps': self._identify_compliance_gaps(audit_data)
        }

    def _generate_anomaly_report(self, audit_data):
        """Generate anomaly-focused report"""
        anomalies = self._detect_anomalies(audit_data)

        return {
            'report_type': 'Anomaly Detection Report',
            'generated_at': now(),
            'detected_anomalies': anomalies,
            'severity_assessment': self._assess_anomaly_severity(anomalies)
        }

    def _identify_compliance_gaps(self, audit_data):
        """Identify potential compliance gaps"""
        try:
            gaps = []

            # Check for doctypes without recent audits
            doctype_timestamps = defaultdict(list)
            for entry in audit_data:
                doctype_timestamps[entry['doctype_name']].append(entry['creation'])

            for doctype, timestamps in doctype_timestamps.items():
                latest_audit = max(timestamps)
                days_since_audit = date_diff(now(), latest_audit)

                if days_since_audit > 30:  # No audit in last 30 days
                    gaps.append({
                        'doctype': doctype,
                        'days_since_last_audit': days_since_audit,
                        'severity': 'high' if days_since_audit > 90 else 'medium'
                    })

            return gaps

        except Exception as e:
            logger.error(f"Failed to identify compliance gaps: {str(e)}")
            return []

    def _assess_anomaly_severity(self, anomalies):
        """Assess the severity of detected anomalies"""
        try:
            severity_score = 0

            # Weight different anomaly types
            severity_score += len(anomalies.get('bulk_operations', [])) * 2
            severity_score += len(anomalies.get('high_risk_clusters', [])) * 3
            severity_score += len(anomalies.get('unusual_user_activity', [])) * 1
            severity_score += len(anomalies.get('suspicious_timings', [])) * 1

            if severity_score >= 10:
                severity = 'critical'
            elif severity_score >= 5:
                severity = 'high'
            elif severity_score >= 2:
                severity = 'medium'
            else:
                severity = 'low'

            return {
                'severity_level': severity,
                'severity_score': severity_score,
                'assessment': f'Detected {sum(len(v) for v in anomalies.values())} anomalies'
            }

        except Exception as e:
            logger.error(f"Failed to assess anomaly severity: {str(e)}")
            return {'severity_level': 'unknown', 'severity_score': 0}

# Global analyzer instance
audit_analyzer = AuditDataAnalyzer()

@frappe.whitelist()
def analyze_audit_data(filters=None, date_range=None):
    """API endpoint for audit data analysis"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    filters = json.loads(filters) if isinstance(filters, str) else filters
    date_range = json.loads(date_range) if isinstance(date_range, str) else date_range

    result = audit_analyzer.analyze_audit_trails(filters, date_range)
    return result

@frappe.whitelist()
def generate_audit_report(report_type, filters=None, date_range=None):
    """API endpoint for generating audit reports"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    filters = json.loads(filters) if isinstance(filters, str) else filters
    date_range = json.loads(date_range) if isinstance(date_range, str) else date_range

    result = audit_analyzer.generate_audit_report(report_type, filters, date_range)
    return result

@frappe.whitelist()
def get_audit_insights(time_period='30_days'):
    """API endpoint for quick audit insights"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    # Calculate date range
    end_date = now()
    if time_period == '7_days':
        start_date = add_days(end_date, -7)
    elif time_period == '30_days':
        start_date = add_days(end_date, -30)
    elif time_period == '90_days':
        start_date = add_days(end_date, -90)
    else:
        start_date = add_days(end_date, -30)

    date_range = (start_date, end_date)

    # Get basic analysis
    analysis = audit_analyzer.analyze_audit_trails(date_range=date_range)

    # Return key insights
    return {
        'time_period': time_period,
        'summary': analysis.get('summary', {}),
        'top_risks': analysis.get('risk_analysis', {}).get('high_risk_activities', [])[:5],
        'recommendations': analysis.get('recommendations', [])[:3]
    }
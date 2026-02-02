# Risk Agent for Multi-Agent System
# =============================================================================
# Agent for predictive risk assessment and dynamic threshold adjustment

import frappe
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from .agent_base import AuditAgent


class RiskAgent(AuditAgent):
    """
    Agent for predictive risk assessment, dynamic threshold adjustment,
    and cross-module risk aggregation.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the Risk Agent"""
        super().__init__(agent_id, config)
        self.agent_type = 'RiskAgent'

        # Configuration
        self.prediction_horizon_days = config.get('prediction_horizon_days', 30) if config else 30
        self.threshold_sensitivity = config.get('threshold_sensitivity', 0.5) if config else 0.5
        self.min_data_points = config.get('min_data_points', 100) if config else 100

        # Subscribe to relevant message types
        self.subscribe(['risk_assessment_request', 'threshold_adjustment_request'])

    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a risk assessment task

        Args:
            task_data: Task data dictionary

        Returns:
            Task result dictionary
        """
        task_type = task_data.get('task_type')

        if task_type == 'predict_risks':
            return self.predict_risks(task_data.get('module'), task_data.get('timeframe'))
        elif task_type == 'assess_module_risks':
            return self.assess_module_risks(task_data.get('module_name'))
        elif task_type == 'adjust_thresholds':
            return self.adjust_thresholds(task_data.get('risk_type'))
        elif task_type == 'aggregate_risks':
            return self.aggregate_risks(task_data.get('risk_findings', []))
        elif task_type == 'assess_financial_risk':
            return self.assess_financial_risk(task_data)
        elif task_type == 'assess_hr_risk':
            return self.assess_hr_risk(task_data)
        elif task_type == 'assess_inventory_risk':
            return self.assess_inventory_risk(task_data)
        else:
            return {
                'status': 'error',
                'error': f'Unknown task type: {task_type}'
            }

    def predict_risks(self, module: Optional[str] = None,
                     timeframe: Optional[int] = None) -> Dict[str, Any]:
        """
        Predict future audit risks using historical data

        Args:
            module: Module to predict risks for
            timeframe: Prediction timeframe in days

        Returns:
            Risk predictions with confidence scores
        """
        try:
            timeframe = timeframe or self.prediction_horizon_days

            # Get historical findings
            historical_findings = self._get_historical_findings(
                module=module,
                days_back=90
            )

            if len(historical_findings) < self.min_data_points:
                return {
                    'status': 'success',
                    'message': 'Insufficient historical data for prediction',
                    'predictions': []
                }

            # Analyze patterns
            predictions = self._analyze_risk_patterns(historical_findings, timeframe)

            # Calculate confidence based on data quality
            confidence = self._calculate_prediction_confidence(historical_findings)

            return {
                'status': 'success',
                'module': module or 'all',
                'timeframe_days': timeframe,
                'predictions': predictions,
                'confidence': confidence,
                'historical_data_points': len(historical_findings)
            }

        except Exception as e:
            frappe.log_error(f"Risk Prediction Error: {str(e)}", "Risk Agent")
            return {'status': 'error', 'error': str(e)}

    def assess_module_risks(self, module_name: str) -> Dict[str, Any]:
        """
        Assess risks for a specific module

        Args:
            module_name: Name of the module to assess

        Returns:
            Module risk assessment results
        """
        try:
            # Get module-specific risk indicators
            risk_indicators = self._get_module_risk_indicators(module_name)

            if not risk_indicators:
                return {
                    'status': 'success',
                    'module': module_name,
                    'risk_level': 'Low',
                    'indicators': [],
                    'message': 'No risk indicators found for this module'
                }

            # Calculate risk scores
            risk_scores = []
            for indicator in risk_indicators:
                score = self._calculate_indicator_score(indicator)
                risk_scores.append({
                    'indicator': indicator.get('name'),
                    'score': score,
                    'value': indicator.get('current_value'),
                    'threshold': indicator.get('threshold')
                })

            # Determine overall risk level
            avg_score = statistics.mean([r['score'] for r in risk_scores]) if risk_scores else 0

            if avg_score > 0.7:
                overall_risk = 'High'
            elif avg_score > 0.4:
                overall_risk = 'Medium'
            else:
                overall_risk = 'Low'

            # Create or update risk assessment document
            self._create_risk_assessment(module_name, overall_risk, risk_scores)

            return {
                'status': 'success',
                'module': module_name,
                'overall_risk_level': overall_risk,
                'average_risk_score': round(avg_score, 4),
                'indicators': risk_scores
            }

        except Exception as e:
            frappe.log_error(f"Module Risk Assessment Error [{module_name}]: {str(e)}", "Risk Agent")
            return {'status': 'error', 'error': str(e)}

    def adjust_thresholds(self, risk_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Adapt risk thresholds based on historical patterns

        Args:
            risk_type: Type of risk to adjust thresholds for

        Returns:
            Threshold adjustment results
        """
        try:
            # Get false positive rate
            false_positive_rate = self._calculate_false_positive_rate(risk_type)

            # Calculate optimal threshold based on sensitivity
            current_threshold = self._get_current_threshold(risk_type)
            adjusted_threshold = self._calculate_optimal_threshold(
                current_threshold,
                false_positive_rate,
                self.threshold_sensitivity
            )

            # Store adjusted threshold
            self._set_threshold(risk_type, adjusted_threshold)

            return {
                'status': 'success',
                'risk_type': risk_type,
                'previous_threshold': current_threshold,
                'adjusted_threshold': adjusted_threshold,
                'false_positive_rate': false_positive_rate,
                'adjustment_reason': 'Dynamic adjustment based on historical accuracy'
            }

        except Exception as e:
            frappe.log_error(f"Threshold Adjustment Error: {str(e)}", "Risk Agent")
            return {'status': 'error', 'error': str(e)}

    def aggregate_risks(self, risk_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate risks across modules for enterprise view

        Args:
            risk_findings: List of risk finding dictionaries

        Returns:
            Aggregated risk results
        """
        try:
            # Group related risks
            risk_groups = self._group_related_risks(risk_findings)

            # Calculate compound risk
            compound_risks = []
            for group_name, group_findings in risk_groups.items():
                compound_score = self._calculate_compound_risk(group_findings)
                compound_risks.append({
                    'group': group_name,
                    'finding_count': len(group_findings),
                    'compound_risk_score': compound_score,
                    'risk_level': 'High' if compound_score > 0.7 else 'Medium' if compound_score > 0.4 else 'Low'
                })

            # Prioritize by impact
            compound_risks.sort(key=lambda x: x['compound_risk_score'], reverse=True)

            return {
                'status': 'success',
                'total_findings': len(risk_findings),
                'risk_groups': len(risk_groups),
                'compound_risks': compound_risks,
                'top_risks': compound_risks[:5]
            }

        except Exception as e:
            frappe.log_error(f"Risk Aggregation Error: {str(e)}", "Risk Agent")
            return {'status': 'error', 'error': str(e)}

    def assess_financial_risk(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess financial module risks"""
        return self.assess_module_risks('financial')

    def assess_hr_risk(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess HR module risks"""
        return self.assess_module_risks('hr')

    def assess_inventory_risk(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess inventory module risks"""
        return self.assess_module_risks('inventory')

    def _get_historical_findings(self, module: Optional[str] = None,
                                days_back: int = 90) -> List[Dict[str, Any]]:
        """Get historical audit findings for analysis"""
        try:
            filters = {
                'creation': ['>=', datetime.now() - timedelta(days=days_back)]
            }

            if module:
                filters['module'] = module

            findings = frappe.get_all('Audit Finding',
                filters=filters,
                fields=['name', 'severity', 'risk_rating', 'module',
                       'reported_date', 'status', 'target_completion_date']
            )

            return findings

        except Exception as e:
            frappe.log_error(f"Error fetching historical findings: {str(e)}", "Risk Agent")
            return []

    def _analyze_risk_patterns(self, findings: List[Dict[str, Any]],
                              timeframe: int) -> List[Dict[str, Any]]:
        """Analyze historical findings for risk patterns"""
        predictions = []

        # Group by module
        module_findings = defaultdict(list)
        for finding in findings:
            module = finding.get('module', 'general')
            module_findings[module].append(finding)

        # Analyze each module
        for module, module_finding_list in module_findings.items():
            # Calculate trend
            recent_count = len([f for f in module_finding_list
                              if f.get('reported_date') >= datetime.now() - timedelta(days=30)])
            older_count = len(module_finding_list) - recent_count

            # Predict future risk
            if recent_count > older_count * 1.5:
                predicted_risk = 'increasing'
                confidence = 'high'
            elif recent_count < older_count * 0.5:
                predicted_risk = 'decreasing'
                confidence = 'medium'
            else:
                predicted_risk = 'stable'
                confidence = 'medium'

            predictions.append({
                'module': module,
                'predicted_risk_level': predicted_risk,
                'confidence': confidence,
                'recent_findings': recent_count,
                'predicted_findings': int(recent_count * (1 + (timeframe / 30) * 0.1))  # Simple projection
            })

        return predictions

    def _calculate_prediction_confidence(self, findings: List[Dict[str, Any]]) -> str:
        """Calculate confidence score for predictions"""
        # More data = higher confidence
        data_points = len(findings)

        if data_points > 500:
            return 'high'
        elif data_points > 200:
            return 'medium'
        else:
            return 'low'

    def _get_module_risk_indicators(self, module_name: str) -> List[Dict[str, Any]]:
        """Get risk indicators for a specific module"""
        try:
            if not frappe.db.table_exists('Risk Indicator'):
                return []

            indicators = frappe.get_all('Risk Indicator',
                filters={
                    'module': module_name,
                    'active': 1
                },
                fields=['name', 'indicator_type', 'threshold', 'current_value']
            )

            return indicators

        except Exception as e:
            frappe.log_error(f"Error fetching risk indicators: {str(e)}", "Risk Agent")
            return []

    def _calculate_indicator_score(self, indicator: Dict[str, Any]) -> float:
        """Calculate risk score for an indicator"""
        try:
            current = float(indicator.get('current_value', 0))
            threshold = float(indicator.get('threshold', 1))

            # Simple ratio - can be enhanced
            if threshold > 0:
                score = min(current / threshold, 1.0)
            else:
                score = 0.5

            return score

        except Exception:
            return 0.5

    def _create_risk_assessment(self, module: str, risk_level: str,
                               risk_scores: List[Dict[str, Any]]) -> None:
        """Create or update risk assessment document"""
        try:
            if not frappe.db.table_exists('Risk Assessment'):
                return

            assessment_date = datetime.now().date()

            # Check if assessment exists for today
            existing = frappe.db.exists('Risk Assessment', {
                'module': module,
                'assessment_date': assessment_date
            })

            assessment_data = {
                'doctype': 'Risk Assessment',
                'module': module,
                'assessment_date': assessment_date,
                'overall_risk_level': risk_level,
                'risk_indicators': frappe.as_json(risk_scores),
                'source_agent': self.agent_type
            }

            if existing:
                doc = frappe.get_doc('Risk Assessment', existing)
                doc.update(assessment_data)
            else:
                doc = frappe.get_doc(assessment_data)

            doc.save()
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Failed to create risk assessment: {str(e)}", "Risk Agent")

    def _calculate_false_positive_rate(self, risk_type: Optional[str]) -> float:
        """Calculate historical false positive rate for a risk type"""
        # Placeholder - would need to track actual vs predicted
        return 0.1  # 10% false positive rate as default

    def _get_current_threshold(self, risk_type: Optional[str]) -> float:
        """Get current threshold for a risk type"""
        # Placeholder - would retrieve from configuration
        return 0.7

    def _calculate_optimal_threshold(self, current: float, fp_rate: float,
                                    sensitivity: float) -> float:
        """Calculate optimal threshold based on performance"""
        # Adjust threshold based on false positive rate
        if fp_rate > 0.2:  # Too many false positives
            return current * (1 + sensitivity * 0.1)
        elif fp_rate < 0.05:  # Very few false positives - can be more sensitive
            return current * (1 - sensitivity * 0.1)
        return current

    def _set_threshold(self, risk_type: Optional[str], threshold: float) -> None:
        """Store adjusted threshold"""
        # Placeholder - would store to configuration
        self.set_state(f'threshold_{risk_type}', threshold)

    def _group_related_risks(self, findings: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Group related risks by similarity"""
        groups = defaultdict(list)

        for finding in findings:
            # Group by module and severity
            key = f"{finding.get('module', 'general')}_{finding.get('severity', 'Medium')}"
            groups[key].append(finding)

        return groups

    def _calculate_compound_risk(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate compound risk score for a group of findings"""
        if not findings:
            return 0.0

        # Severity weights
        severity_weights = {
            'Critical': 1.0,
            'High': 0.8,
            'Medium': 0.5,
            'Low': 0.2
        }

        # Weighted average
        total_weight = 0
        weighted_sum = 0

        for finding in findings:
            severity = finding.get('severity', 'Medium')
            weight = severity_weights.get(severity, 0.5)
            weighted_sum += weight
            total_weight += 1

        return weighted_sum / total_weight if total_weight > 0 else 0

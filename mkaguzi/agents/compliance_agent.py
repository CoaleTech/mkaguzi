# Compliance Agent for Multi-Agent System
# =============================================================================
# Agent for regulatory compliance verification and gap analysis

import frappe
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .agent_base import AuditAgent


class ComplianceAgent(AuditAgent):
    """
    Agent for regulatory requirement verification, compliance gap identification,
    and adaptive compliance checking.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the Compliance Agent"""
        super().__init__(agent_id, config)
        self.agent_type = 'ComplianceAgent'

        # Configuration
        self.auto_update_checks = config.get('auto_update_checks', True) if config else True
        self.severity_threshold = config.get('severity_threshold', 'medium') if config else 'medium'
        self.regulatory_sources = config.get('regulatory_sources', []) if config else []

        # Subscribe to relevant message types
        self.subscribe(['compliance_check_request', 'compliance_update_request'])

    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a compliance task

        Args:
            task_data: Task data dictionary

        Returns:
            Task result dictionary
        """
        task_type = task_data.get('task_type')

        if task_type == 'verify_compliance':
            return self.verify_compliance(task_data.get('requirement'))
        elif task_type == 'identify_gaps':
            return self.identify_gaps(task_data.get('framework'))
        elif task_type == 'update_checks':
            return self.update_on_regulatory_change(task_data.get('new_regulations'))
        elif task_type == 'run_compliance_check':
            return self.run_compliance_check(task_data.get('check_name'))
        elif task_type == 'get_compliance_status':
            return self.get_compliance_status(task_data.get('framework'))
        elif task_type == 'generate_compliance_report':
            return self.generate_compliance_report(task_data)
        else:
            return {
                'status': 'error',
                'error': f'Unknown task type: {task_type}'
            }

    def verify_compliance(self, requirement: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verify compliance with a regulatory requirement

        Args:
            requirement: Requirement to verify

        Returns:
            Compliance verification results
        """
        try:
            if not requirement:
                # Run all compliance checks
                return self._run_all_compliance_checks()

            requirement_id = requirement.get('requirement_id')
            requirement_name = requirement.get('requirement_name')

            # Get requirement details
            if frappe.db.table_exists('Compliance Requirement'):
                req_doc = frappe.get_doc('Compliance Requirement', requirement_id)
            else:
                # Use provided requirement data
                req_doc = requirement

            # Collect evidence
            evidence = self._collect_compliance_evidence(req_doc)

            # Verify each requirement clause
            verifications = []
            all_compliant = True

            clauses = req_doc.get('clauses', []) if hasattr(req_doc, 'get') else []
            if not clauses:
                clauses = self._get_default_clauses()

            for clause in clauses:
                result = self._verify_clause(clause, evidence)
                verifications.append(result)
                if not result.get('compliant'):
                    all_compliant = False

            # Calculate overall compliance percentage
            compliant_count = sum(1 for v in verifications if v.get('compliant'))
            compliance_percentage = (compliant_count / len(verifications) * 100) if verifications else 0

            # Create compliance result
            self._create_compliance_result(
                requirement_id or requirement_name,
                compliance_percentage,
                verifications
            )

            return {
                'status': 'success',
                'requirement': requirement_name,
                'compliance_percentage': round(compliance_percentage, 2),
                'overall_compliant': all_compliant,
                'verifications': verifications,
                'evidence_count': len(evidence)
            }

        except Exception as e:
            frappe.log_error(f"Compliance Verification Error: {str(e)}", "Compliance Agent")
            return {'status': 'error', 'error': str(e)}

    def identify_gaps(self, framework: Optional[str] = None) -> Dict[str, Any]:
        """
        Identify compliance gaps vs requirements

        Args:
            framework: Framework to check gaps for

        Returns:
            Compliance gap analysis
        """
        try:
            if not framework:
                framework = 'General'

            # Get all requirements for the framework
            requirements = self._get_framework_requirements(framework)

            gaps = []

            for requirement in requirements:
                # Check if compliant
                verification = self.verify_compliance(requirement)

                if not verification.get('overall_compliant'):
                    # Identify specific gaps
                    gap_details = self._analyze_compliance_gaps(
                        requirement,
                        verification.get('verifications', [])
                    )

                    gaps.append({
                        'requirement': requirement.get('requirement_name'),
                        'severity': self._assess_gap_severity(gap_details),
                        'gap_count': len(gap_details),
                        'gaps': gap_details
                    })

            # Prioritize gaps by severity
            gaps.sort(key=lambda x: self._severity_score(x.get('severity', 'Low')), reverse=True)

            return {
                'status': 'success',
                'framework': framework,
                'total_requirements': len(requirements),
                'gaps_identified': len(gaps),
                'compliance_rate': round((len(requirements) - len(gaps)) / len(requirements) * 100, 2) if requirements else 0,
                'gaps': gaps[:20]  # Top 20 gaps
            }

        except Exception as e:
            frappe.log_error(f"Gap Identification Error: {str(e)}", "Compliance Agent")
            return {'status': 'error', 'error': str(e)}

    def update_on_regulatory_change(self, new_regulations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Adapt compliance checks when regulations change

        Args:
            new_regulations: List of new regulatory updates

        Returns:
            Update results
        """
        try:
            updated_checks = []
            created_requirements = []

            for regulation in new_regulations:
                # Parse regulation
                regulation_id = regulation.get('regulation_id')
                changes = regulation.get('changes', [])

                # Update existing requirements or create new ones
                for change in changes:
                    if change.get('action') == 'update':
                        # Update existing requirement
                        updated = self._update_compliance_requirement(change)
                        if updated:
                            updated_checks.append(updated)
                    elif change.get('action') == 'create':
                        # Create new requirement
                        created = self._create_compliance_requirement(change)
                        if created:
                            created_requirements.append(created)

            # Notify stakeholders of changes
            if updated_checks or created_requirements:
                self._notify_regulatory_changes(updated_checks, created_requirements)

            return {
                'status': 'success',
                'updated_checks': len(updated_checks),
                'created_requirements': len(created_requirements),
                'details': {
                    'updated': updated_checks,
                    'created': created_requirements
                }
            }

        except Exception as e:
            frappe.log_error(f"Regulatory Update Error: {str(e)}", "Compliance Agent")
            return {'status': 'error', 'error': str(e)}

    def run_compliance_check(self, check_name: str) -> Dict[str, Any]:
        """
        Run an individual compliance check

        Args:
            check_name: Name of the compliance check

        Returns:
            Check results
        """
        try:
            if not frappe.db.table_exists('Compliance Check'):
                return {'status': 'error', 'error': 'Compliance Check DocType not found'}

            check_doc = frappe.get_doc('Compliance Check', check_name)

            # Execute the check
            check_result = self._execute_check(check_doc)

            # Update check status
            check_doc.last_run_date = datetime.now()
            check_doc.last_run_result = check_result.get('status', 'Unknown')
            check_doc.last_run_details = frappe.as_json(check_result)
            check_doc.save()

            frappe.db.commit()

            return check_result

        except Exception as e:
            frappe.log_error(f"Compliance Check Execution Error: {str(e)}", "Compliance Agent")
            return {'status': 'error', 'error': str(e)}

    def get_compliance_status(self, framework: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current compliance status

        Args:
            framework: Optional framework filter

        Returns:
            Compliance status summary
        """
        try:
            if not frappe.db.table_exists('Compliance Result'):
                return {'status': 'error', 'error': 'Compliance Result DocType not found'}

            # Get recent compliance results
            filters = {}
            if framework:
                filters['framework'] = framework

            recent_results = frappe.get_all('Compliance Result',
                filters=filters,
                fields=['name', 'compliance_check', 'check_date', 'status', 'compliance_score'],
                order_by='check_date desc',
                limit=100
            )

            # Calculate summary
            total_checks = len(recent_results)
            compliant = sum(1 for r in recent_results if r.get('status') == 'Compliant')
            partially_compliant = sum(1 for r in recent_results if r.get('status') == 'Partially Compliant')
            non_compliant = sum(1 for r in recent_results if r.get('status') == 'Non-Compliant')

            avg_score = sum(r.get('compliance_score', 0) for r in recent_results) / total_checks if total_checks > 0 else 0

            return {
                'status': 'success',
                'framework': framework or 'All',
                'summary': {
                    'total_checks': total_checks,
                    'compliant': compliant,
                    'partially_compliant': partially_compliant,
                    'non_compliant': non_compliant,
                    'compliance_rate': round((compliant + partially_compliant * 0.5) / total_checks * 100, 2) if total_checks > 0 else 0,
                    'average_score': round(avg_score, 2)
                },
                'recent_results': recent_results[:10]
            }

        except Exception as e:
            frappe.log_error(f"Compliance Status Error: {str(e)}", "Compliance Agent")
            return {'status': 'error', 'error': str(e)}

    def generate_compliance_report(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report

        Args:
            task_data: Report parameters

        Returns:
            Compliance report
        """
        try:
            framework = task_data.get('framework')
            start_date = task_data.get('start_date')
            end_date = task_data.get('end_date')

            # Get compliance status
            status = self.get_compliance_status(framework)

            # Identify gaps
            gaps = self.identify_gaps(framework)

            # Get detailed findings
            findings = self._get_compliance_findings(framework, start_date, end_date)

            return {
                'status': 'success',
                'framework': framework,
                'report_date': datetime.now().isoformat(),
                'summary': status.get('summary', {}),
                'gaps': gaps,
                'findings': findings[:50],
                'recommendations': self._generate_compliance_recommendations(gaps)
            }

        except Exception as e:
            frappe.log_error(f"Compliance Report Generation Error: {str(e)}", "Compliance Agent")
            return {'status': 'error', 'error': str(e)}

    def _run_all_compliance_checks(self) -> Dict[str, Any]:
        """Run all active compliance checks"""
        try:
            if not frappe.db.table_exists('Compliance Check'):
                return {'status': 'error', 'error': 'Compliance Check DocType not found'}

            checks = frappe.get_all('Compliance Check',
                filters={'status': 'Active'},
                fields=['name']
            )

            results = []
            for check in checks:
                result = self.run_compliance_check(check['name'])
                results.append({
                    'check': check['name'],
                    'result': result
                })

            return {
                'status': 'success',
                'checks_run': len(results),
                'results': results
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def _collect_compliance_evidence(self, requirement) -> List[Dict[str, Any]]:
        """Collect evidence for compliance verification"""
        evidence = []

        # Query relevant documents based on requirement type
        req_type = requirement.get('compliance_type', 'general')

        if req_type == 'financial':
            evidence = frappe.get_all('Audit GL Entry',
                filters={'creation': ['>=', datetime.now() - timedelta(days=90)]},
                fields=['name', 'account_no', 'debit', 'credit', 'posting_date'],
                limit=100
            )
        elif req_type == 'access_control':
            evidence = frappe.get_all('User',
                filters={'enabled': 1},
                fields=['name', 'role_profile_name', 'creation']
            )

        return evidence

    def _verify_clause(self, clause: Dict[str, Any], evidence: List[Dict]) -> Dict[str, Any]:
        """Verify a specific compliance clause"""
        # Simplified verification logic
        compliant = len(evidence) > 0

        return {
            'clause': clause.get('description', 'Unknown'),
            'compliant': compliant,
            'evidence_count': len(evidence),
            'findings': [] if compliant else ['Insufficient evidence']
        }

    def _get_default_clauses(self) -> List[Dict[str, Any]]:
        """Get default compliance clauses"""
        return [
            {'description': 'Basic controls in place', 'required': True},
            {'description': 'Documentation maintained', 'required': True},
            {'description': 'Regular reviews conducted', 'required': True}
        ]

    def _create_compliance_result(self, requirement_id: str, compliance_percentage: float,
                                 verifications: List[Dict]) -> None:
        """Create compliance result document"""
        try:
            if not frappe.db.table_exists('Compliance Result'):
                return

            result = frappe.get_doc({
                'doctype': 'Compliance Result',
                'compliance_check': requirement_id,
                'check_date': datetime.now().date(),
                'status': 'Compliant' if compliance_percentage >= 95 else 'Partially Compliant' if compliance_percentage >= 80 else 'Non-Compliant',
                'compliance_score': compliance_percentage,
                'findings': frappe.as_json(verifications),
                'source_agent': self.agent_type
            })

            result.insert()
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Failed to create compliance result: {str(e)}", "Compliance Agent")

    def _get_framework_requirements(self, framework: str) -> List[Dict[str, Any]]:
        """Get all requirements for a framework"""
        if frappe.db.table_exists('Compliance Requirement'):
            return frappe.get_all('Compliance Requirement',
                filters={'framework': framework},
                fields=['name', 'requirement_name', 'compliance_type']
            )
        return []

    def _analyze_compliance_gaps(self, requirement: Dict, verifications: List[Dict]) -> List[Dict]:
        """Analyze specific compliance gaps"""
        gaps = []

        for verification in verifications:
            if not verification.get('compliant'):
                gaps.append({
                    'clause': verification.get('clause'),
                    'findings': verification.get('findings', []),
                    'severity': 'medium'
                })

        return gaps

    def _assess_gap_severity(self, gaps: List[Dict]) -> str:
        """Assess overall severity of compliance gaps"""
        if not gaps:
            return 'Low'

        high_severity = sum(1 for g in gaps if g.get('severity') == 'high')
        if high_severity > 0:
            return 'High'
        elif len(gaps) > 3:
            return 'Medium'
        return 'Low'

    def _severity_score(self, severity: str) -> float:
        """Convert severity to numeric score"""
        scores = {'High': 1.0, 'Medium': 0.5, 'Low': 0.2}
        return scores.get(severity, 0.5)

    def _execute_check(self, check_doc) -> Dict[str, Any]:
        """Execute a compliance check"""
        # Simplified execution
        return {
            'status': 'success',
            'compliant': True,
            'findings': []
        }

    def _update_compliance_requirement(self, change: Dict) -> Optional[str]:
        """Update an existing compliance requirement"""
        # Placeholder for update logic
        return change.get('requirement_id')

    def _create_compliance_requirement(self, change: Dict) -> Optional[str]:
        """Create a new compliance requirement"""
        # Placeholder for creation logic
        return f"new_requirement_{datetime.now().timestamp()}"

    def _notify_regulatory_changes(self, updated: List, created: List) -> None:
        """Notify stakeholders of regulatory changes"""
        try:
            # Create notification
            if frappe.db.table_exists('Compliance Alert'):
                alert = frappe.get_doc({
                    'doctype': 'Compliance Alert',
                    'alert_title': 'Regulatory Requirements Updated',
                    'alert_message': f'{len(updated)} requirements updated, {len(created)} new requirements added.',
                    'severity': 'Medium',
                    'source': 'Compliance Agent'
                })
                alert.insert()
                frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Failed to notify regulatory changes: {str(e)}", "Compliance Agent")

    def _get_compliance_findings(self, framework: Optional[str], start_date: Optional[str],
                                end_date: Optional[str]) -> List[Dict]:
        """Get compliance findings for report"""
        if not frappe.db.table_exists('Compliance Alert'):
            return []

        filters = {}
        if framework:
            filters['framework'] = framework

        return frappe.get_all('Compliance Alert',
            filters=filters,
            fields=['name', 'alert_title', 'severity', 'creation'],
            order_by='creation desc',
            limit=50
        )

    def _generate_compliance_recommendations(self, gaps: Dict) -> List[str]:
        """Generate recommendations based on compliance gaps"""
        recommendations = []

        if gaps.get('gaps_identified', 0) > 0:
            recommendations.append('Address identified compliance gaps promptly')
            recommendations.append('Schedule follow-up compliance review')

        if gaps.get('compliance_rate', 100) < 80:
            recommendations.append('Implement additional controls for non-compliant areas')
            recommendations.append('Provide compliance training to relevant staff')

        return recommendations

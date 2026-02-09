# Asset Agent for Multi-Agent System
# =============================================================================
# Agent for asset management analysis and fixed asset auditing

import frappe
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .agent_base import AuditAgent
from ..utils.erpnext_queries import get_assets, get_gl_entries, get_journal_entries


class AssetAgent(AuditAgent):
    """
    Agent for asset management analysis, depreciation review,
    and fixed asset auditing.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the Asset Agent"""
        super().__init__(agent_id, config)
        self.agent_type = 'Asset'

        # Configuration
        self.max_batch_size = config.get('max_batch_size', 1000) if config else 1000
        self.depreciation_threshold = config.get('depreciation_threshold', 0.05) if config else 0.05

        # Subscribe to relevant message types
        self.subscribe(['asset_analysis_request', 'depreciation_review_request'])

    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an asset analysis task

        Args:
            task_data: Task data dictionary

        Returns:
            Task result dictionary
        """
        task_type = task_data.get('task_type')

        if task_type == 'analyze_assets':
            return self.analyze_assets(task_data)
        elif task_type == 'review_depreciation':
            return self.review_depreciation(task_data)
        elif task_type == 'audit_asset_disposals':
            return self.audit_asset_disposals(task_data)
        elif task_type == 'check_asset_existence':
            return self.check_asset_existence(task_data)
        elif task_type == 'analyze_asset_utilization':
            return self.analyze_asset_utilization(task_data)
        else:
            return {
                'status': 'error',
                'error': f'Unknown task type: {task_type}'
            }

    def analyze_assets(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive asset analysis including valuation, depreciation, and utilization

        Args:
            task_data: Analysis parameters

        Returns:
            Asset analysis results
        """
        try:
            company = task_data.get('company')
            asset_category = task_data.get('asset_category')
            limit = task_data.get('limit', self.max_batch_size)

            if not company:
                return {'status': 'error', 'error': 'Missing required parameter: company'}

            # Get assets using shared query layer
            filters = {}
            if asset_category:
                filters['asset_category'] = asset_category

            assets = get_assets(
                company=company,
                filters=filters,
                limit=limit
            )

            # Analyze assets
            analysis_results = {
                'total_assets': len(assets),
                'total_value': sum(asset['gross_purchase_amount'] for asset in assets),
                'total_depreciation': sum(asset['value_after_depreciation'] for asset in assets),
                'net_book_value': 0,
                'fully_depreciated': [],
                'under_utilized': [],
                'high_value_assets': []
            }

            analysis_results['net_book_value'] = analysis_results['total_value'] - analysis_results['total_depreciation']

            for asset in assets:
                # Check for fully depreciated assets
                if asset['value_after_depreciation'] <= 0:
                    analysis_results['fully_depreciated'].append(asset)

                # Check for high value assets
                if asset['gross_purchase_amount'] > 100000:  # Configurable threshold
                    analysis_results['high_value_assets'].append(asset)

                # Check for assets without custodian/location
                if not asset.get('custodian') or not asset.get('location'):
                    analysis_results['under_utilized'].append(asset)

            # Create findings
            findings = []
            if analysis_results['fully_depreciated']:
                finding_result = self.create_audit_finding(
                    finding_title=f'Fully Depreciated Assets - {len(analysis_results["fully_depreciated"])} found',
                    finding_type='Asset Management',
                    severity='Low',
                    condition=f'Found {len(analysis_results["fully_depreciated"])} assets that are fully depreciated',
                    criteria='Assets should be reviewed for potential disposal when fully depreciated',
                    cause='Normal depreciation process completion',
                    consequence='Potential holding of obsolete assets, storage costs',
                    recommendation='Review for disposal or reclassification',
                    risk_category='Operational',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            if analysis_results['under_utilized']:
                finding_result = self.create_audit_finding(
                    finding_title=f'Unassigned Assets - {len(analysis_results["under_utilized"])} found',
                    finding_type='Asset Control',
                    severity='Medium',
                    condition=f'Found {len(analysis_results["under_utilized"])} assets without assigned custodian or location',
                    criteria='All assets should have assigned custodians and locations for proper control',
                    cause='Incomplete asset registration or transfer processes',
                    consequence='Increased risk of loss, theft, or misappropriation',
                    recommendation='Complete asset assignments and implement regular physical verification',
                    risk_category='Operational',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            return {
                'status': 'success',
                'analysis': analysis_results,
                'findings': findings
            }

        except Exception as e:
            frappe.log_error(f"Asset Analysis Error: {str(e)}", "Asset Agent")
            return {'status': 'error', 'error': str(e)}

    def review_depreciation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review depreciation calculations and schedules

        Args:
            task_data: Review parameters

        Returns:
            Depreciation review results
        """
        try:
            company = task_data.get('company')
            from_date = task_data.get('from_date')
            to_date = task_data.get('to_date')

            if not company or not from_date or not to_date:
                return {'status': 'error', 'error': 'Missing required parameters'}

            # Get assets
            assets = get_assets(company=company)

            # Get depreciation journal entries
            depreciation_entries = get_journal_entries(
                from_date=from_date,
                to_date=to_date,
                company=company,
                filters={'voucher_type': ['in', ['Journal Entry']]}  # Filter for depreciation entries
            )

            # Analyze depreciation patterns
            issues = {
                'missing_depreciation': [],
                'irregular_amounts': [],
                'timing_issues': []
            }

            # Check for assets without recent depreciation
            current_date = datetime.now().date()
            for asset in assets:
                if asset['status'] == 'Submitted':  # Active assets
                    # Check if depreciation was recorded in the period
                    asset_depr = [entry for entry in depreciation_entries
                                if asset['name'] in str(entry.get('remark', '')) or
                                   asset['name'] in str(entry.get('user_remark', ''))]

                    if not asset_depr:
                        # Check if asset should have depreciation
                        if asset['gross_purchase_amount'] > asset['value_after_depreciation']:
                            issues['missing_depreciation'].append(asset)

            # Create findings
            findings = []
            if issues['missing_depreciation']:
                finding_result = self.create_audit_finding(
                    finding_title=f'Missing Depreciation Entries - {len(issues["missing_depreciation"])} assets',
                    finding_type='Depreciation Review',
                    severity='High',
                    condition=f'Found {len(issues["missing_depreciation"])} assets without depreciation entries in the review period',
                    criteria='Active depreciable assets should have regular depreciation entries',
                    cause='System errors, calculation issues, or manual process failures',
                    consequence='Understated depreciation expense and overstated asset values',
                    recommendation='Review depreciation schedules and ensure all required entries are posted',
                    risk_category='Financial',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            return {
                'status': 'success',
                'assets_reviewed': len(assets),
                'depreciation_entries': len(depreciation_entries),
                'issues_found': sum(len(v) for v in issues.values()),
                'findings': findings
            }

        except Exception as e:
            frappe.log_error(f"Depreciation Review Error: {str(e)}", "Asset Agent")
            return {'status': 'error', 'error': str(e)}

    def audit_asset_disposals(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit asset disposal transactions

        Args:
            task_data: Audit parameters

        Returns:
            Asset disposal audit results
        """
        try:
            company = task_data.get('company')
            from_date = task_data.get('from_date')
            to_date = task_data.get('to_date')

            if not company or not from_date or not to_date:
                return {'status': 'error', 'error': 'Missing required parameters'}

            # Get journal entries related to asset disposals
            disposal_entries = get_journal_entries(
                from_date=from_date,
                to_date=to_date,
                company=company
            )

            # Filter for disposal-related entries (this would need more sophisticated filtering in production)
            potential_disposals = [entry for entry in disposal_entries
                                 if 'disposal' in str(entry.get('remark', '')).lower() or
                                    'sale' in str(entry.get('remark', '')).lower()]

            findings = []
            if potential_disposals:
                finding_result = self.create_audit_finding(
                    finding_title=f'Asset Disposal Transactions - {len(potential_disposals)} found',
                    finding_type='Asset Disposal Review',
                    severity='Medium',
                    condition=f'Found {len(potential_disposals)} potential asset disposal transactions requiring review',
                    criteria='Asset disposals should be properly authorized and documented',
                    cause='Normal asset lifecycle management',
                    consequence='Potential for improper disposals or documentation issues',
                    recommendation='Review disposal documentation and ensure proper approvals',
                    risk_category='Operational',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            return {
                'status': 'success',
                'disposals_found': len(potential_disposals),
                'findings': findings
            }

        except Exception as e:
            frappe.log_error(f"Asset Disposal Audit Error: {str(e)}", "Asset Agent")
            return {'status': 'error', 'error': str(e)}

    def check_asset_existence(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check physical existence of assets

        Args:
            task_data: Check parameters

        Returns:
            Asset existence check results
        """
        try:
            company = task_data.get('company')
            sample_size = task_data.get('sample_size', 50)

            if not company:
                return {'status': 'error', 'error': 'Missing required parameter: company'}

            # Get assets
            assets = get_assets(company=company, limit=sample_size)

            # In a real implementation, this would integrate with physical verification systems
            # For now, we'll flag assets that haven't been verified recently
            unverified_assets = []
            for asset in assets:
                # Check if asset has been verified in the last year (simplified check)
                last_verification = asset.get('last_verification_date')
                if not last_verification:
                    unverified_assets.append(asset)

            findings = []
            if unverified_assets:
                finding_result = self.create_audit_finding(
                    finding_title=f'Unverified Assets - {len(unverified_assets)} found',
                    finding_type='Asset Verification',
                    severity='Medium',
                    condition=f'Found {len(unverified_assets)} assets without recent physical verification',
                    criteria='Assets should be physically verified periodically',
                    cause='Incomplete verification processes or missing records',
                    consequence='Increased risk of asset loss or misappropriation',
                    recommendation='Conduct physical verification and update records',
                    risk_category='Operational',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            return {
                'status': 'success',
                'assets_checked': len(assets),
                'unverified_count': len(unverified_assets),
                'findings': findings
            }

        except Exception as e:
            frappe.log_error(f"Asset Existence Check Error: {str(e)}", "Asset Agent")
            return {'status': 'error', 'error': str(e)}

    def analyze_asset_utilization(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze asset utilization rates

        Args:
            task_data: Analysis parameters

        Returns:
            Asset utilization analysis results
        """
        try:
            company = task_data.get('company')

            if not company:
                return {'status': 'error', 'error': 'Missing required parameter: company'}

            # Get assets
            assets = get_assets(company=company)

            # Analyze utilization (simplified - in production would use maintenance/usage logs)
            utilization_analysis = {
                'high_utilization': [],
                'low_utilization': [],
                'idle_assets': []
            }

            # This is a simplified analysis - real implementation would use actual usage data
            for asset in assets:
                # Placeholder logic for demonstration
                if asset['status'] == 'Submitted':
                    # Assume some assets are under-utilized based on simplistic criteria
                    if not asset.get('custodian'):
                        utilization_analysis['idle_assets'].append(asset)

            findings = []
            if utilization_analysis['idle_assets']:
                finding_result = self.create_audit_finding(
                    finding_title=f'Potentially Idle Assets - {len(utilization_analysis["idle_assets"])} found',
                    finding_type='Asset Utilization',
                    severity='Low',
                    condition=f'Found {len(utilization_analysis["idle_assets"])} assets that may not be actively used',
                    criteria='Assets should be utilized effectively or considered for disposal',
                    cause='Changed business needs or excess capacity',
                    consequence='Unnecessary holding costs and storage requirements',
                    recommendation='Review asset utilization and consider disposal or redeployment',
                    risk_category='Operational',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            return {
                'status': 'success',
                'assets_analyzed': len(assets),
                'utilization_analysis': utilization_analysis,
                'findings': findings
            }

        except Exception as e:
            frappe.log_error(f"Asset Utilization Analysis Error: {str(e)}", "Asset Agent")
            return {'status': 'error', 'error': str(e)}
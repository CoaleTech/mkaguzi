# Financial Agent for Multi-Agent System
# =============================================================================
# Agent for deep financial transaction analysis and fraud detection

import frappe
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .agent_base import AuditAgent


class FinancialAgent(AuditAgent):
    """
    Agent for deep financial transaction analysis, fraud detection,
    and intelligent reconciliation.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the Financial Agent"""
        super().__init__(agent_id, config)
        self.agent_type = 'FinancialAgent'

        # Configuration
        self.max_batch_size = config.get('max_batch_size', 1000) if config else 1000
        self.fraud_threshold = config.get('fraud_threshold', 0.7) if config else 0.7

        # Subscribe to relevant message types
        self.subscribe(['financial_analysis_request', 'fraud_detection_request'])

    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a financial analysis task

        Args:
            task_data: Task data dictionary

        Returns:
            Task result dictionary
        """
        task_type = task_data.get('task_type')

        if task_type == 'analyze_transactions':
            return self.analyze_transactions(task_data)
        elif task_type == 'detect_fraud':
            return self.detect_fraud_patterns(task_data.get('transactions', []))
        elif task_type == 'reconcile_gl':
            return self.auto_reconcile(task_data.get('accounts', []), task_data.get('period'))
        elif task_type == 'analyze_journal_entries':
            return self.analyze_journal_entries(task_data)
        elif task_type == 'duplicate_payment_check':
            return self.check_duplicate_payments(task_data)
        elif task_type == 'benford_analysis':
            return self.run_benford_analysis(task_data)
        else:
            return {
                'status': 'error',
                'error': f'Unknown task type: {task_type}'
            }

    def analyze_transactions(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep transaction analysis with anomaly detection

        Args:
            task_data: Analysis parameters including date range, accounts, etc.

        Returns:
            Analysis results with anomalies and risk scores
        """
        try:
            start_date = task_data.get('start_date')
            end_date = task_data.get('end_date')
            accounts = task_data.get('accounts', [])
            limit = task_data.get('limit', self.max_batch_size)

            # Query GL entries
            filters = {'posting_date': ['>=', start_date]} if start_date else {}
            if end_date:
                filters['posting_date'] = ['<=', end_date]

            if accounts:
                filters['account_no'] = ['in', accounts]

            entries = frappe.get_all('Audit GL Entry',
                filters=filters,
                fields=['name', 'account_no', 'debit', 'credit', 'posting_date',
                       'against_account', 'voucher_type', 'voucher_no', 'creation'],
                limit=limit,
                order_by='posting_date desc'
            )

            # Analyze for anomalies
            anomalies = []
            risk_scores = []

            for entry in entries:
                # Calculate risk score for this entry
                risk_score = self._calculate_transaction_risk(entry)
                risk_scores.append(risk_score)

                # Flag high-risk transactions
                if risk_score > self.fraud_threshold:
                    anomalies.append({
                        'entry': entry.name,
                        'account': entry.account_no,
                        'amount': entry.debit or entry.credit,
                        'date': entry.posting_date,
                        'risk_score': risk_score,
                        'reasons': self._get_risk_reasons(entry)
                    })

            # Calculate statistics
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            high_risk_count = len([r for r in risk_scores if r > self.fraud_threshold])

            # Create finding if significant anomalies found
            if anomalies:
                self._create_fraud_finding(anomalies, task_data)

            return {
                'status': 'success',
                'analyzed_count': len(entries),
                'average_risk_score': round(avg_risk, 4),
                'high_risk_count': high_risk_count,
                'anomalies': anomalies[:50],  # Limit to 50
                'summary': {
                    'total_debit': sum(e.debit or 0 for e in entries),
                    'total_credit': sum(e.credit or 0 for e in entries),
                    'unique_accounts': len(set(e.account_no for e in entries))
                }
            }

        except Exception as e:
            frappe.log_error(f"Transaction Analysis Error: {str(e)}", "Financial Agent")
            return {'status': 'error', 'error': str(e)}

    def detect_fraud_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify suspicious transaction patterns

        Args:
            transactions: List of transaction data

        Returns:
            Fraud pattern analysis results
        """
        try:
            patterns = {
                'round_numbers': [],
                'same_amount_same_day': [],
                'unusual_timing': [],
                'vendor_suspicious': []
            }

            # Analyze transaction timing
            time_groups = defaultdict(list)
            amount_groups = defaultdict(list)

            for tx in transactions:
                amount = tx.get('debit', 0) or tx.get('credit', 0)
                date = tx.get('posting_date')
                vendor = tx.get('against_account')

                # Check for round numbers (suspicious for fraud)
                if amount > 0 and amount == int(amount) and amount % 1000 == 0:
                    patterns['round_numbers'].append(tx)

                # Group by date and amount
                if date:
                    time_groups[date].append(tx)
                if amount:
                    amount_groups[amount].append(tx)

            # Check for same amount multiple times same day
            for date, txs in time_groups.items():
                amounts = defaultdict(int)
                for tx in txs:
                    amt = tx.get('debit', 0) or tx.get('credit', 0)
                    amounts[amt] += 1

                for amt, count in amounts.items():
                    if count > 3 and amt > 0:  # Same amount > 3 times in a day
                        patterns['same_amount_same_day'].extend([
                            {'date': date, 'amount': amt, 'count': count}
                        ])

            # Check for unusual timing (weekends, late night)
            for tx in transactions:
                tx_time = tx.get('creation')
                if tx_time:
                    tx_hour = tx_time.hour if hasattr(tx_time, 'hour') else 0
                    tx_weekday = tx_time.weekday() if hasattr(tx_time, 'weekday') else 0

                    if tx_weekday >= 5:  # Weekend
                        patterns['unusual_timing'].append(tx)
                    elif tx_hour < 6 or tx_hour > 22:  # Late night/early morning
                        patterns['unusual_timing'].append(tx)

            return {
                'status': 'success',
                'patterns_detected': sum(len(v) for v in patterns.values()),
                'patterns': patterns,
                'risk_level': 'high' if patterns['round_numbers'] or patterns['same_amount_same_day'] else 'normal'
            }

        except Exception as e:
            frappe.log_error(f"Fraud Detection Error: {str(e)}", "Financial Agent")
            return {'status': 'error', 'error': str(e)}

    def auto_reconcile(self, accounts: List[str], period: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Automatic account reconciliation

        Args:
            accounts: List of accounts to reconcile
            period: Period dict with start_date and end_date

        Returns:
            Reconciliation results
        """
        try:
            results = {
                'accounts_reconciled': [],
                'unreconciled_entries': [],
                'adjustments_needed': []
            }

            for account in accounts:
                # Get entries for this account
                filters = {'account_no': account}

                if period:
                    if period.get('start_date'):
                        filters['posting_date'] = ['>=', period.get('start_date')]
                    if period.get('end_date'):
                        filters['posting_date'] = ['<=', period.get('end_date')]

                entries = frappe.get_all('Audit GL Entry',
                    filters=filters,
                    fields=['name', 'debit', 'credit', 'reconciliation_status']
                )

                # Calculate totals
                total_debit = sum(e.debit or 0 for e in entries)
                total_credit = sum(e.credit or 0 for e in entries)
                unreconciled = [e for e in entries if e.reconciliation_status != 'Reconciled']

                # Check if balanced
                difference = abs(total_debit - total_credit)

                account_result = {
                    'account': account,
                    'total_debit': total_debit,
                    'total_credit': total_credit,
                    'difference': difference,
                    'entry_count': len(entries),
                    'unreconciled_count': len(unreconciled),
                    'status': 'balanced' if difference < 0.01 else 'unbalanced'
                }

                results['accounts_reconciled'].append(account_result)

                if unreconciled:
                    results['unreconciled_entries'].extend([
                        {'account': account, 'entry': e.name} for e in unreconciled[:10]
                    ])

                if difference > 0.01:
                    results['adjustments_needed'].append({
                        'account': account,
                        'adjustment_amount': difference,
                        'suggested_action': 'Debit' if total_debit < total_credit else 'Credit'
                    })

            return {
                'status': 'success',
                'summary': results
            }

        except Exception as e:
            frappe.log_error(f"Auto Reconcile Error: {str(e)}", "Financial Agent")
            return {'status': 'error', 'error': str(e)}

    def analyze_journal_entries(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze journal entries for risk indicators

        Args:
            task_data: Analysis parameters

        Returns:
            Journal entry analysis results
        """
        try:
            from mkaguzi.api.analytics import analyze_journal_entry_risk

            start_date = task_data.get('start_date')
            end_date = task_data.get('end_date')

            # Use existing analytics function
            result = analyze_journal_entry_risk(start_date=start_date, end_date=end_date)

            return {
                'status': 'success',
                **result
            }

        except Exception as e:
            frappe.log_error(f"Journal Entry Analysis Error: {str(e)}", "Financial Agent")
            return {'status': 'error', 'error': str(e)}

    def check_duplicate_payments(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for duplicate payments

        Args:
            task_data: Check parameters

        Returns:
            Duplicate payment check results
        """
        try:
            from mkaguzi.api.analytics import detect_duplicate_payments

            date_range_days = task_data.get('date_range_days', 30)
            amount_tolerance = task_data.get('amount_tolerance', 0.01)

            # Use existing analytics function
            result = detect_duplicate_payments(
                date_range_days=date_range_days,
                amount_tolerance=amount_tolerance
            )

            return {
                'status': 'success',
                **result
            }

        except Exception as e:
            frappe.log_error(f"Duplicate Payment Check Error: {str(e)}", "Financial Agent")
            return {'status': 'error', 'error': str(e)}

    def run_benford_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run Benford's Law analysis on transaction amounts

        Args:
            task_data: Analysis parameters

        Returns:
            Benford's Law analysis results
        """
        try:
            from mkaguzi.api.analytics import analyze_benford_law

            start_date = task_data.get('start_date')
            end_date = task_data.get('end_date')
            account = task_data.get('account')

            # Use existing analytics function
            result = analyze_benford_law(
                start_date=start_date,
                end_date=end_date,
                account=account
            )

            return {
                'status': 'success',
                **result
            }

        except Exception as e:
            frappe.log_error(f"Benford Analysis Error: {str(e)}", "Financial Agent")
            return {'status': 'error', 'error': str(e)}

    def _calculate_transaction_risk(self, entry: Dict[str, Any]) -> float:
        """Calculate risk score for a single transaction"""
        risk_score = 0.0

        # Large amount risk
        amount = entry.debit or entry.credit or 0
        if amount > 100000:
            risk_score += 0.3
        elif amount > 10000:
            risk_score += 0.1

        # Round number risk (potential fake)
        if amount > 0 and amount == int(amount) and amount % 1000 == 0:
            risk_score += 0.2

        # Weekend/late night posting
        if hasattr(entry.get('creation'), 'hour'):
            entry_hour = entry.creation.hour
            if entry_hour < 6 or entry_hour > 22:
                risk_score += 0.1

        # Unusual account combinations
        suspicious_combinations = [
            ('Cash', 'Expense'),
            ('Suspense', 'Revenue'),
            ('Clearing', 'Asset')
        ]
        # Simplified check
        if entry.against_account and 'Suspense' in entry.against_account:
            risk_score += 0.3

        return min(risk_score, 1.0)

    def _get_risk_reasons(self, entry: Dict[str, Any]) -> List[str]:
        """Get list of risk reasons for an entry"""
        reasons = []

        amount = entry.debit or entry.credit or 0
        if amount > 100000:
            reasons.append('Large amount')
        if amount > 0 and amount == int(amount) and amount % 1000 == 0:
            reasons.append('Round number')

        if entry.against_account and 'Suspense' in entry.against_account:
            reasons.append('Suspense account used')

        return reasons

    def _create_fraud_finding(self, anomalies: List[Dict[str, Any]],
                             task_data: Dict[str, Any]) -> None:
        """Create an audit finding for detected fraud patterns"""
        try:
            if not frappe.db.table_exists('Audit Finding'):
                return

            finding = frappe.get_doc({
                'doctype': 'Audit Finding',
                'finding_title': f'Financial Anomalies Detected - {datetime.now().strftime("%Y-%m-%d")}',
                'finding_description': f'Detected {len(anomalies)} high-risk financial transactions requiring investigation.',
                'criteria': 'Transactions should not have unusual patterns indicating potential fraud',
                'condition': f'{len(anomalies)} transactions with risk score above threshold',
                'cause': 'Potential fraudulent activity or control weakness',
                'consequence': 'Financial loss or misstatement',
                'corrective_action': 'Investigate transactions and strengthen controls',
                'severity': 'High' if len(anomalies) > 10 else 'Medium',
                'status': 'Open',
                'risk_rating': 'High',
                'source_agent': self.agent_type,
                'auto_generated': 1
            })

            finding.insert()
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Failed to create fraud finding: {str(e)}", "Financial Agent")

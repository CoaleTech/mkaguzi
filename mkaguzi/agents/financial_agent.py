# Financial Agent for Multi-Agent System
# =============================================================================
# Agent for deep financial transaction analysis and fraud detection

import frappe
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .agent_base import AuditAgent
from ..utils.erpnext_queries import get_gl_entries, get_sales_invoices, get_purchase_invoices, get_payment_entries, get_journal_entries


class FinancialAgent(AuditAgent):
    """
    Agent for deep financial transaction analysis, fraud detection,
    and intelligent reconciliation.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the Financial Agent"""
        super().__init__(agent_id, config)
        self.agent_type = 'Financial'

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
        elif task_type == 'audit_sales_invoices':
            return self.audit_sales_invoices(task_data)
        elif task_type == 'audit_purchase_invoices':
            return self.audit_purchase_invoices(task_data)
        elif task_type == 'audit_payment_entries':
            return self.audit_payment_entries(task_data)
        elif task_type == 'audit_journal_entries':
            return self.audit_journal_entries(task_data)
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
            from_date = task_data.get('from_date')
            to_date = task_data.get('to_date')
            company = task_data.get('company')
            accounts = task_data.get('accounts', [])
            limit = task_data.get('limit', self.max_batch_size)

            if not from_date or not to_date or not company:
                return {'status': 'error', 'error': 'Missing required parameters: from_date, to_date, company'}

            # Query GL entries using shared query layer
            filters = {}
            if accounts:
                filters['account'] = ['in', accounts]

            entries = get_gl_entries(
                from_date=from_date,
                to_date=to_date,
                company=company,
                filters=filters,
                limit=limit
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
                        'entry': entry['name'],
                        'account': entry['account'],
                        'amount': entry['debit'] or entry['credit'],
                        'date': entry['posting_date'],
                        'risk_score': risk_score,
                        'reasons': self._get_risk_reasons(entry)
                    })

            # Calculate statistics
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            high_risk_count = len([r for r in risk_scores if r > self.fraud_threshold])

            # Create finding if significant anomalies found
            findings = []
            if anomalies:
                finding_result = self._create_fraud_finding(anomalies, task_data)
                if finding_result:
                    findings.append(finding_result)

            return {
                'status': 'success',
                'analyzed_count': len(entries),
                'average_risk_score': round(avg_risk, 4),
                'high_risk_count': high_risk_count,
                'findings': findings,
                'anomalies': anomalies[:50],  # Limit to 50
                'summary': {
                    'total_debit': sum(e['debit'] or 0 for e in entries),
                    'total_credit': sum(e['credit'] or 0 for e in entries),
                    'unique_accounts': len(set(e['account'] for e in entries))
                }
            }

        except Exception as e:
            try:
                frappe.log_error(message=f"Transaction Analysis Error: {str(e)}", title="Transaction Analysis Error")
            except Exception:
                pass
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
                vendor = tx.get('party')

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
            try:
                frappe.log_error(message=f"Fraud Detection Error: {str(e)}", title="Fraud Detection Error")
            except Exception:
                pass
            return {'status': 'error', 'error': str(e)}

    def auto_reconcile(self, accounts: List[str], period: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Automatic account reconciliation

        Args:
            accounts: List of accounts to reconcile
            period: Period dict with from_date and to_date

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
                # Get entries for this account using shared query layer
                from_date = period.get('from_date') if period else None
                to_date = period.get('to_date') if period else None
                company = period.get('company') if period else None

                if not from_date or not to_date or not company:
                    return {'status': 'error', 'error': 'Missing required period parameters: from_date, to_date, company'}

                entries = get_gl_entries(
                    from_date=from_date,
                    to_date=to_date,
                    company=company,
                    filters={'account': account}
                )

                # Calculate totals
                total_debit = sum(e['debit'] or 0 for e in entries)
                total_credit = sum(e['credit'] or 0 for e in entries)
                # Note: reconciliation_status field doesn't exist in GL Entry, so we'll assume all are unreconciled
                unreconciled = entries  # All entries are considered unreconciled for now

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
                        {'account': account, 'entry': e['name']} for e in unreconciled[:10]
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
            try:
                frappe.log_error(message=f"Auto Reconcile Error: {str(e)}", title="Auto Reconcile Error")
            except Exception:
                pass
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

    def audit_sales_invoices(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit sales invoices for anomalies and compliance issues

        Args:
            task_data: Audit parameters

        Returns:
            Sales invoice audit results
        """
        try:
            from_date = task_data.get('from_date')
            to_date = task_data.get('to_date')
            company = task_data.get('company')
            limit = task_data.get('limit', self.max_batch_size)

            if not from_date or not to_date or not company:
                return {'status': 'error', 'error': 'Missing required parameters: from_date, to_date, company'}

            invoices = get_sales_invoices(
                from_date=from_date,
                to_date=to_date,
                company=company,
                limit=limit
            )

            findings = []
            overdue_invoices = []
            returns_credits = []

            for invoice in invoices:
                # Check for overdue invoices
                if invoice['outstanding_amount'] > 0 and invoice['status'] == 'Overdue':
                    overdue_invoices.append(invoice)

                # Check for returns/credit notes
                if invoice['is_return']:
                    returns_credits.append(invoice)

            # Create findings
            if overdue_invoices:
                finding_result = self.create_audit_finding(
                    finding_title=f'Overdue Sales Invoices - {len(overdue_invoices)} found',
                    finding_type='Accounts Receivable Issue',
                    severity='Medium',
                    condition=f'Found {len(overdue_invoices)} overdue sales invoices requiring collection follow-up',
                    criteria='All sales invoices should be collected within agreed payment terms',
                    cause='Customer payment delays, credit control weaknesses, or economic factors',
                    consequence='Cash flow impact and potential bad debt write-offs',
                    recommendation='Review credit terms, strengthen collection processes, and assess customer creditworthiness',
                    risk_category='Financial',
                    financial_impact=sum(inv['outstanding_amount'] for inv in overdue_invoices),
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            if returns_credits:
                finding_result = self.create_audit_finding(
                    finding_title=f'Sales Returns/Credit Notes - {len(returns_credits)} found',
                    finding_type='Sales Transaction Review',
                    severity='Low',
                    condition=f'Found {len(returns_credits)} sales returns or credit notes requiring review',
                    criteria='Sales returns should follow established approval and documentation procedures',
                    cause='Product quality issues, customer dissatisfaction, or sales policy changes',
                    consequence='Revenue reduction and inventory adjustments',
                    recommendation='Review return authorization processes and product quality controls',
                    risk_category='Operational',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            return {
                'status': 'success',
                'audited_count': len(invoices),
                'overdue_count': len(overdue_invoices),
                'returns_count': len(returns_credits),
                'findings': findings
            }

        except Exception as e:
            try:
                frappe.log_error(message=f"Sales Invoice Audit Error: {str(e)}", title="Sales Invoice Audit Error")
            except Exception:
                pass
            return {'status': 'error', 'error': str(e)}

    def audit_purchase_invoices(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit purchase invoices for anomalies and compliance issues

        Args:
            task_data: Audit parameters

        Returns:
            Purchase invoice audit results
        """
        try:
            from_date = task_data.get('from_date')
            to_date = task_data.get('to_date')
            company = task_data.get('company')
            limit = task_data.get('limit', self.max_batch_size)

            if not from_date or not to_date or not company:
                return {'status': 'error', 'error': 'Missing required parameters: from_date, to_date, company'}

            invoices = get_purchase_invoices(
                from_date=from_date,
                to_date=to_date,
                company=company,
                limit=limit
            )

            findings = []
            on_hold_invoices = []
            duplicate_bills = []

            for invoice in invoices:
                # Check for on-hold invoices
                if invoice['on_hold']:
                    on_hold_invoices.append(invoice)

                # Check for potential duplicate bill numbers
                if invoice['bill_no']:
                    # Simple duplicate check - in production this would be more sophisticated
                    similar_bills = [inv for inv in invoices
                                   if inv['name'] != invoice['name']
                                   and inv['bill_no'] == invoice['bill_no']
                                   and inv['supplier'] == invoice['supplier']]
                    if similar_bills:
                        duplicate_bills.append(invoice)

            # Create findings
            if on_hold_invoices:
                finding_result = self.create_audit_finding(
                    finding_title=f'On-Hold Purchase Invoices - {len(on_hold_invoices)} found',
                    finding_type='Accounts Payable Issue',
                    severity='Medium',
                    condition=f'Found {len(on_hold_invoices)} purchase invoices on hold requiring resolution',
                    criteria='Purchase invoices should be processed timely without undue holds',
                    cause='Disputed amounts, missing approvals, or documentation issues',
                    consequence='Delayed payments, supplier relationship issues, and cash flow inefficiencies',
                    recommendation='Review hold reasons and streamline approval processes',
                    risk_category='Financial',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            if duplicate_bills:
                finding_result = self.create_audit_finding(
                    finding_title=f'Potential Duplicate Bill Numbers - {len(duplicate_bills)} found',
                    finding_type='Vendor Invoice Review',
                    severity='High',
                    condition=f'Found {len(duplicate_bills)} invoices with potential duplicate bill numbers',
                    criteria='Each vendor invoice should have a unique bill number',
                    cause='Data entry errors, duplicate processing, or fraudulent activity',
                    consequence='Duplicate payments and financial misstatement',
                    recommendation='Implement duplicate bill number validation and review flagged invoices',
                    risk_category='Financial',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            return {
                'status': 'success',
                'audited_count': len(invoices),
                'on_hold_count': len(on_hold_invoices),
                'duplicate_count': len(duplicate_bills),
                'findings': findings
            }

        except Exception as e:
            try:
                frappe.log_error(message=f"Purchase Invoice Audit Error: {str(e)}", title="Purchase Invoice Audit Error")
            except Exception:
                pass
            return {'status': 'error', 'error': str(e)}

    def audit_payment_entries(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit payment entries for anomalies and unusual patterns

        Args:
            task_data: Audit parameters

        Returns:
            Payment entry audit results
        """
        try:
            from_date = task_data.get('from_date')
            to_date = task_data.get('to_date')
            company = task_data.get('company')
            limit = task_data.get('limit', self.max_batch_size)

            if not from_date or not to_date or not company:
                return {'status': 'error', 'error': 'Missing required parameters: from_date, to_date, company'}

            payments = get_payment_entries(
                from_date=from_date,
                to_date=to_date,
                company=company,
                limit=limit
            )

            findings = []
            large_payments = []
            unusual_patterns = []

            for payment in payments:
                amount = payment['paid_amount']

                # Check for large payments
                if amount > 100000:  # Configurable threshold
                    large_payments.append(payment)

                # Check for unusual patterns (round numbers, etc.)
                if amount > 0 and amount == int(amount) and amount % 10000 == 0:
                    unusual_patterns.append(payment)

            # Create findings
            if large_payments:
                finding_result = self.create_audit_finding(
                    finding_title=f'Large Payment Entries - {len(large_payments)} found',
                    finding_type='Payment Review',
                    severity='Medium',
                    condition=f'Found {len(large_payments)} payment entries exceeding normal thresholds',
                    criteria='Large payments should have appropriate approvals and documentation',
                    cause='Large vendor payments, capital expenditures, or unusual business transactions',
                    consequence='Risk of unauthorized payments or control weaknesses',
                    recommendation='Review approval processes for large payments and verify supporting documentation',
                    risk_category='Financial',
                    financial_impact=sum(p['paid_amount'] for p in large_payments),
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            if unusual_patterns:
                finding_result = self.create_audit_finding(
                    finding_title=f'Unusual Payment Patterns - {len(unusual_patterns)} found',
                    finding_type='Payment Anomaly',
                    severity='Low',
                    condition=f'Found {len(unusual_patterns)} payments with unusual amount patterns (round numbers)',
                    criteria='Payment amounts should follow normal business patterns',
                    cause='Potential control weaknesses or unusual business requirements',
                    consequence='Possible fraud indicators or process inefficiencies',
                    recommendation='Review payment approval processes and amount validation controls',
                    risk_category='Operational',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            return {
                'status': 'success',
                'audited_count': len(payments),
                'large_payments_count': len(large_payments),
                'unusual_patterns_count': len(unusual_patterns),
                'findings': findings
            }

        except Exception as e:
            try:
                frappe.log_error(message=f"Payment Entry Audit Error: {str(e)}", title="Payment Entry Audit Error")
            except Exception:
                pass
            return {'status': 'error', 'error': str(e)}

    def audit_journal_entries(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit journal entries for anomalies and control issues

        Args:
            task_data: Audit parameters

        Returns:
            Journal entry audit results
        """
        try:
            from_date = task_data.get('from_date')
            to_date = task_data.get('to_date')
            company = task_data.get('company')
            limit = task_data.get('limit', self.max_batch_size)

            if not from_date or not to_date or not company:
                return {'status': 'error', 'error': 'Missing required parameters: from_date, to_date, company'}

            journals = get_journal_entries(
                from_date=from_date,
                to_date=to_date,
                company=company,
                limit=limit
            )

            findings = []
            round_entries = []
            weekend_entries = []

            for journal in journals:
                # Check for round number entries (potential adjustment entries)
                total_amount = journal['total_debit'] or journal['total_credit'] or 0
                if total_amount > 0 and total_amount == int(total_amount) and total_amount % 1000 == 0:
                    round_entries.append(journal)

                # Check for weekend entries (unusual timing)
                posting_date = frappe.utils.getdate(journal['posting_date'])
                if posting_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    weekend_entries.append(journal)

            # Create findings
            if round_entries:
                finding_result = self.create_audit_finding(
                    finding_title=f'Round Number Journal Entries - {len(round_entries)} found',
                    finding_type='Journal Entry Review',
                    severity='Low',
                    condition=f'Found {len(round_entries)} journal entries with round number amounts',
                    criteria='Journal entries should reflect actual business transactions',
                    cause='Period-end adjustments, estimation entries, or potential manipulation',
                    consequence='Possible earnings management or control weaknesses',
                    recommendation='Review journal entry approval processes and supporting documentation',
                    risk_category='Financial',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            if weekend_entries:
                finding_result = self.create_audit_finding(
                    finding_title=f'Weekend Journal Entries - {len(weekend_entries)} found',
                    finding_type='Timing Anomaly',
                    severity='Low',
                    condition=f'Found {len(weekend_entries)} journal entries posted on weekends',
                    criteria='Journal entries should follow normal business hours',
                    cause='Urgent corrections, automated processes, or control weaknesses',
                    consequence='Potential lack of review and approval processes',
                    recommendation='Review weekend posting policies and approval requirements',
                    risk_category='Operational',
                    engagement_reference=task_data.get('engagement_reference')
                )
                findings.append(finding_result)

            return {
                'status': 'success',
                'audited_count': len(journals),
                'round_entries_count': len(round_entries),
                'weekend_entries_count': len(weekend_entries),
                'findings': findings
            }

        except Exception as e:
            try:
                frappe.log_error(message=f"Journal Entry Audit Error: {str(e)}", title="Journal Entry Audit Error")
            except Exception:
                pass
            return {'status': 'error', 'error': str(e)}

    def _calculate_transaction_risk(self, entry: Dict[str, Any]) -> float:
        """Calculate risk score for a single transaction"""
        risk_score = 0.0

        # Large amount risk
        amount = entry.get('debit', 0) or entry.get('credit', 0)
        if amount > 100000:
            risk_score += 0.3
        elif amount > 10000:
            risk_score += 0.1

        # Round number risk (potential fake)
        if amount > 0 and amount == int(amount) and amount % 1000 == 0:
            risk_score += 0.2

        # Weekend/late night posting
        posting_date = frappe.utils.getdate(entry.get('posting_date'))
        if posting_date and posting_date.weekday() >= 5:  # Weekend
            risk_score += 0.1

        # Unusual account combinations
        suspicious_combinations = [
            ('Cash', 'Expense'),
            ('Suspense', 'Revenue'),
            ('Clearing', 'Asset')
        ]
        # Simplified check
        if entry.get('party') and 'Suspense' in str(entry.get('party')):
            risk_score += 0.3

        return min(risk_score, 1.0)

    def _get_risk_reasons(self, entry: Dict[str, Any]) -> List[str]:
        """Get list of risk reasons for an entry"""
        reasons = []

        amount = entry.get('debit', 0) or entry.get('credit', 0)
        if amount > 100000:
            reasons.append('Large amount')
        if amount > 0 and amount == int(amount) and amount % 1000 == 0:
            reasons.append('Round number')

        posting_date = frappe.utils.getdate(entry.get('posting_date'))
        if posting_date and posting_date.weekday() >= 5:
            reasons.append('Weekend posting')

        if entry.get('party') and 'Suspense' in str(entry.get('party')):
            reasons.append('Suspense account used')

        return reasons

    def _create_fraud_finding(self, anomalies: List[Dict[str, Any]],
                             task_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Create an audit finding for detected fraud patterns using shared method"""
        try:
            severity = 'High' if len(anomalies) > 10 else 'Medium'
            
            # Build detailed condition with anomaly examples
            condition_details = f"Identified {len(anomalies)} high-risk financial transactions with risk scores above threshold.\n\n"
            condition_details += "Key anomalies detected:\n"
            for i, anomaly in enumerate(anomalies[:5]):  # Show first 5 examples
                condition_details += f"- {anomaly.get('document_name', 'Unknown')}: Risk Score {anomaly.get('risk_score', 0):.2f}\n"
            if len(anomalies) > 5:
                condition_details += f"... and {len(anomalies) - 5} more transactions\n"
            
            # Calculate total financial exposure
            financial_impact = sum(anomaly.get('amount', 0) for anomaly in anomalies)
            
            finding_result = self.create_audit_finding(
                finding_title=f'Financial Anomalies Detected - {datetime.now().strftime("%Y-%m-%d")}',
                finding_type='Fraud Indicator',
                severity=severity,
                condition=condition_details,
                criteria='All financial transactions should follow established patterns and controls to prevent fraudulent activity',
                cause='Potential fraudulent activity, control weaknesses, or unusual business transactions requiring investigation',
                consequence='Risk of financial loss, misstatement of financial records, and regulatory non-compliance',
                recommendation='Immediately investigate flagged transactions, strengthen financial controls, and implement enhanced monitoring for similar patterns',
                risk_category='Financial',
                financial_impact=financial_impact,
                engagement_reference=task_data.get('engagement_reference')
            )
            
            return finding_result
            
        except Exception as e:
            try:
                frappe.log_error(message=f"Failed to create fraud finding: {str(e)}", title="Fraud Finding Error")
            except Exception:
                pass
            return None

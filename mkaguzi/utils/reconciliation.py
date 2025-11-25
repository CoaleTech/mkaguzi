import frappe
from frappe import _
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

class ReconciliationEngine:
    """
    Engine for performing various reconciliation operations
    """

    @staticmethod
    def reconcile_bank_statement(bank_account, statement_date, statement_balance):
        """
        Reconcile bank statement with GL entries
        """
        try:
            # Get GL entries for the bank account up to statement date
            gl_entries = frappe.db.sql("""
                SELECT
                    posting_date,
                    document_no,
                    description,
                    debit_amount,
                    credit_amount,
                    (debit_amount - credit_amount) as net_amount
                FROM `tabGL Entry`
                WHERE account_no = %s
                AND posting_date <= %s
                ORDER BY posting_date, document_no
            """, (bank_account, statement_date), as_dict=True)

            # Calculate book balance
            book_balance = sum([entry.net_amount for entry in gl_entries])

            # Calculate reconciliation difference
            difference = float(statement_balance) - book_balance

            # Find outstanding items (uncleared transactions)
            outstanding_items = []

            # This is a simplified reconciliation - real implementation would track cleared items
            if abs(difference) > 0.01:  # Allow for small rounding differences
                outstanding_items.append({
                    'type': 'Bank Reconciliation Difference',
                    'amount': difference,
                    'description': f"Difference between statement balance ({statement_balance}) and book balance ({book_balance:.2f})"
                })

            return {
                'book_balance': book_balance,
                'statement_balance': statement_balance,
                'difference': difference,
                'outstanding_items': outstanding_items,
                'reconciled': abs(difference) <= 0.01
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Bank Reconciliation Error"))
            raise

    @staticmethod
    def reconcile_customer_balances(period):
        """
        Reconcile customer balances between AR and sales transactions
        """
        try:
            period_doc = frappe.get_doc('Data Period', period)
            start_date = period_doc.start_date
            end_date = period_doc.end_date

            # Get customer ledger entries
            customer_entries = frappe.db.sql("""
                SELECT
                    customer_no,
                    customer_name,
                    SUM(CASE WHEN entry_type = 'Sale' THEN amount ELSE 0 END) as sales_amount,
                    SUM(CASE WHEN entry_type = 'Payment' THEN -amount ELSE 0 END) as payments_amount,
                    SUM(amount) as net_amount
                FROM `tabCustomer Ledger Entry`
                WHERE posting_date BETWEEN %s AND %s
                GROUP BY customer_no, customer_name
                HAVING ABS(SUM(amount)) > 0.01
                ORDER BY ABS(SUM(amount)) DESC
            """, (start_date, end_date), as_dict=True)

            # Get AR balances from GL
            ar_balances = frappe.db.sql("""
                SELECT
                    SUBSTRING_INDEX(SUBSTRING_INDEX(description, ' - ', 1), 'Customer: ', -1) as customer_no,
                    SUM(debit_amount - credit_amount) as ar_balance
                FROM `tabGL Entry`
                WHERE account_no LIKE '1300%'  -- AR account range
                AND posting_date <= %s
                GROUP BY customer_no
                HAVING ABS(ar_balance) > 0.01
            """, (end_date,), as_dict=True)

            # Create reconciliation mapping
            reconciliation_results = []

            for entry in customer_entries:
                # Find matching AR balance
                ar_balance = next((ar['ar_balance'] for ar in ar_balances
                                 if ar['customer_no'] == entry['customer_no']), 0)

                difference = entry['net_amount'] - ar_balance

                reconciliation_results.append({
                    'customer_no': entry['customer_no'],
                    'customer_name': entry['customer_name'],
                    'ledger_balance': entry['net_amount'],
                    'ar_balance': ar_balance,
                    'difference': difference,
                    'status': 'Matched' if abs(difference) <= 0.01 else 'Unmatched'
                })

            # Find AR balances without ledger entries
            ledger_customers = {entry['customer_no'] for entry in customer_entries}
            unmatched_ar = [ar for ar in ar_balances if ar['customer_no'] not in ledger_customers]

            for ar in unmatched_ar:
                reconciliation_results.append({
                    'customer_no': ar['customer_no'],
                    'customer_name': 'Unknown',
                    'ledger_balance': 0,
                    'ar_balance': ar['ar_balance'],
                    'difference': -ar['ar_balance'],
                    'status': 'AR Only'
                })

            return {
                'reconciliation_date': datetime.now(),
                'period': period,
                'total_customers': len(reconciliation_results),
                'matched_customers': len([r for r in reconciliation_results if r['status'] == 'Matched']),
                'unmatched_customers': len([r for r in reconciliation_results if r['status'] != 'Matched']),
                'results': reconciliation_results
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Customer Balance Reconciliation Error"))
            raise

    @staticmethod
    def reconcile_vendor_balances(period):
        """
        Reconcile vendor balances between AP and purchase transactions
        """
        try:
            period_doc = frappe.get_doc('Data Period', period)
            start_date = period_doc.start_date
            end_date = period_doc.end_date

            # Get vendor ledger entries
            vendor_entries = frappe.db.sql("""
                SELECT
                    vendor_no,
                    vendor_name,
                    SUM(CASE WHEN entry_type = 'Purchase' THEN amount ELSE 0 END) as purchase_amount,
                    SUM(CASE WHEN entry_type = 'Payment' THEN -amount ELSE 0 END) as payments_amount,
                    SUM(amount) as net_amount
                FROM `tabVendor Ledger Entry`
                WHERE posting_date BETWEEN %s AND %s
                GROUP BY vendor_no, vendor_name
                HAVING ABS(SUM(amount)) > 0.01
                ORDER BY ABS(SUM(amount)) DESC
            """, (start_date, end_date), as_dict=True)

            # Get AP balances from GL
            ap_balances = frappe.db.sql("""
                SELECT
                    SUBSTRING_INDEX(SUBSTRING_INDEX(description, ' - ', 1), 'Vendor: ', -1) as vendor_no,
                    SUM(credit_amount - debit_amount) as ap_balance
                FROM `tabGL Entry`
                WHERE account_no LIKE '2100%'  -- AP account range
                AND posting_date <= %s
                GROUP BY vendor_no
                HAVING ABS(ap_balance) > 0.01
            """, (end_date,), as_dict=True)

            # Create reconciliation mapping
            reconciliation_results = []

            for entry in vendor_entries:
                # Find matching AP balance
                ap_balance = next((ap['ap_balance'] for ap in ap_balances
                                 if ap['vendor_no'] == entry['vendor_no']), 0)

                difference = entry['net_amount'] - ap_balance

                reconciliation_results.append({
                    'vendor_no': entry['vendor_no'],
                    'vendor_name': entry['vendor_name'],
                    'ledger_balance': entry['net_amount'],
                    'ap_balance': ap_balance,
                    'difference': difference,
                    'status': 'Matched' if abs(difference) <= 0.01 else 'Unmatched'
                })

            # Find AP balances without ledger entries
            ledger_vendors = {entry['vendor_no'] for entry in vendor_entries}
            unmatched_ap = [ap for ap in ap_balances if ap['vendor_no'] not in ledger_vendors]

            for ap in unmatched_ap:
                reconciliation_results.append({
                    'vendor_no': ap['vendor_no'],
                    'vendor_name': 'Unknown',
                    'ledger_balance': 0,
                    'ap_balance': ap['ap_balance'],
                    'difference': -ap['ap_balance'],
                    'status': 'AP Only'
                })

            return {
                'reconciliation_date': datetime.now(),
                'period': period,
                'total_vendors': len(reconciliation_results),
                'matched_vendors': len([r for r in reconciliation_results if r['status'] == 'Matched']),
                'unmatched_vendors': len([r for r in reconciliation_results if r['status'] != 'Matched']),
                'results': reconciliation_results
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Vendor Balance Reconciliation Error"))
            raise

    @staticmethod
    def reconcile_inventory_stock(period):
        """
        Reconcile inventory stock between item ledger and GL
        """
        try:
            period_doc = frappe.get_doc('Data Period', period)
            end_date = period_doc.end_date

            # Get inventory balances from item ledger
            item_ledger_balances = frappe.db.sql("""
                SELECT
                    item_no,
                    SUM(remaining_quantity) as ledger_quantity,
                    SUM(remaining_quantity * unit_cost) as ledger_value
                FROM `tabItem Ledger Entry`
                WHERE data_period = %s
                GROUP BY item_no
                HAVING ABS(ledger_quantity) > 0.01
            """, (period,), as_dict=True)

            # Get inventory balances from GL (COGS and inventory accounts)
            gl_inventory_balances = frappe.db.sql("""
                SELECT
                    SUBSTRING_INDEX(SUBSTRING_INDEX(description, ' - ', 1), 'Item: ', -1) as item_no,
                    SUM(debit_amount - credit_amount) as gl_balance
                FROM `tabGL Entry`
                WHERE account_no LIKE '1400%'  -- Inventory account range
                AND posting_date <= %s
                GROUP BY item_no
                HAVING ABS(gl_balance) > 0.01
            """, (end_date,), as_dict=True)

            # Create reconciliation mapping
            reconciliation_results = []

            for ledger in item_ledger_balances:
                # Find matching GL balance
                gl_balance = next((gl['gl_balance'] for gl in gl_inventory_balances
                                 if gl['item_no'] == ledger['item_no']), 0)

                difference = ledger['ledger_value'] - gl_balance

                reconciliation_results.append({
                    'item_no': ledger['item_no'],
                    'ledger_quantity': ledger['ledger_quantity'],
                    'ledger_value': ledger['ledger_value'],
                    'gl_balance': gl_balance,
                    'difference': difference,
                    'status': 'Matched' if abs(difference) <= 0.01 else 'Unmatched'
                })

            # Find GL balances without ledger entries
            ledger_items = {ledger['item_no'] for ledger in item_ledger_balances}
            unmatched_gl = [gl for gl in gl_inventory_balances if gl['item_no'] not in ledger_items]

            for gl in unmatched_gl:
                reconciliation_results.append({
                    'item_no': gl['item_no'],
                    'ledger_quantity': 0,
                    'ledger_value': 0,
                    'gl_balance': gl['gl_balance'],
                    'difference': -gl['gl_balance'],
                    'status': 'GL Only'
                })

            return {
                'reconciliation_date': datetime.now(),
                'period': period,
                'total_items': len(reconciliation_results),
                'matched_items': len([r for r in reconciliation_results if r['status'] == 'Matched']),
                'unmatched_items': len([r for r in reconciliation_results if r['status'] != 'Matched']),
                'results': reconciliation_results
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Inventory Stock Reconciliation Error"))
            raise

    @staticmethod
    def perform_three_way_reconciliation(customer_no, period):
        """
        Perform three-way reconciliation: Sales Invoice -> Customer Ledger -> GL
        """
        try:
            period_doc = frappe.get_doc('Data Period', period)
            start_date = period_doc.start_date
            end_date = period_doc.end_date

            # Get sales invoice amounts
            sales_invoices = frappe.db.sql("""
                SELECT
                    document_no,
                    posting_date,
                    amount,
                    customer_no
                FROM `tabSales Invoice Header`
                WHERE customer_no = %s
                AND posting_date BETWEEN %s AND %s
                ORDER BY posting_date
            """, (customer_no, start_date, end_date), as_dict=True)

            # Get customer ledger entries
            ledger_entries = frappe.db.sql("""
                SELECT
                    document_no,
                    posting_date,
                    amount,
                    entry_type
                FROM `tabCustomer Ledger Entry`
                WHERE customer_no = %s
                AND posting_date BETWEEN %s AND %s
                ORDER BY posting_date
            """, (customer_no, start_date, end_date), as_dict=True)

            # Get GL entries for AR account
            gl_entries = frappe.db.sql("""
                SELECT
                    document_no,
                    posting_date,
                    debit_amount,
                    credit_amount,
                    (debit_amount - credit_amount) as net_amount
                FROM `tabGL Entry`
                WHERE account_no LIKE '1300%'  -- AR account
                AND description LIKE %s
                AND posting_date BETWEEN %s AND %s
                ORDER BY posting_date
            """, (f'Customer: {customer_no}%', start_date, end_date), as_dict=True)

            # Calculate totals
            sales_total = sum([inv['amount'] for inv in sales_invoices])
            ledger_total = sum([entry['amount'] for entry in ledger_entries])
            gl_total = sum([entry['net_amount'] for entry in gl_entries])

            # Perform reconciliation
            reconciliation_details = []

            # Check sales vs ledger
            sales_ledger_diff = sales_total - ledger_total
            reconciliation_details.append({
                'comparison': 'Sales Invoices vs Customer Ledger',
                'source_1_total': sales_total,
                'source_2_total': ledger_total,
                'difference': sales_ledger_diff,
                'status': 'Matched' if abs(sales_ledger_diff) <= 0.01 else 'Unmatched'
            })

            # Check ledger vs GL
            ledger_gl_diff = ledger_total - gl_total
            reconciliation_details.append({
                'comparison': 'Customer Ledger vs GL',
                'source_1_total': ledger_total,
                'source_2_total': gl_total,
                'difference': ledger_gl_diff,
                'status': 'Matched' if abs(ledger_gl_diff) <= 0.01 else 'Unmatched'
            })

            # Check sales vs GL
            sales_gl_diff = sales_total - gl_total
            reconciliation_details.append({
                'comparison': 'Sales Invoices vs GL',
                'source_1_total': sales_total,
                'source_2_total': gl_total,
                'difference': sales_gl_diff,
                'status': 'Matched' if abs(sales_gl_diff) <= 0.01 else 'Unmatched'
            })

            return {
                'customer_no': customer_no,
                'period': period,
                'reconciliation_date': datetime.now(),
                'totals': {
                    'sales_invoices': sales_total,
                    'customer_ledger': ledger_total,
                    'gl_entries': gl_total
                },
                'reconciliation_details': reconciliation_details,
                'overall_status': 'Fully Reconciled' if all(detail['status'] == 'Matched' for detail in reconciliation_details) else 'Reconciliation Issues Found'
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Three-Way Reconciliation Error"))
            raise


@frappe.whitelist()
def perform_reconciliation(reconciliation_type, **kwargs):
    """
    Main reconciliation function
    """
    try:
        engine = ReconciliationEngine()

        if reconciliation_type == 'bank_statement':
            return engine.reconcile_bank_statement(
                kwargs.get('bank_account'),
                kwargs.get('statement_date'),
                kwargs.get('statement_balance')
            )
        elif reconciliation_type == 'customer_balances':
            return engine.reconcile_customer_balances(kwargs.get('period'))
        elif reconciliation_type == 'vendor_balances':
            return engine.reconcile_vendor_balances(kwargs.get('period'))
        elif reconciliation_type == 'inventory_stock':
            return engine.reconcile_inventory_stock(kwargs.get('period'))
        elif reconciliation_type == 'three_way':
            return engine.perform_three_way_reconciliation(
                kwargs.get('customer_no'),
                kwargs.get('period')
            )
        else:
            frappe.throw(_("Unknown reconciliation type"))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Reconciliation Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_reconciliation_report(reconciliation_type, period=None):
    """
    Generate reconciliation report
    """
    try:
        if reconciliation_type == 'customer_balances':
            return ReconciliationEngine.reconcile_customer_balances(period)
        elif reconciliation_type == 'vendor_balances':
            return ReconciliationEngine.reconcile_vendor_balances(period)
        elif reconciliation_type == 'inventory_stock':
            return ReconciliationEngine.reconcile_inventory_stock(period)
        else:
            frappe.throw(_("Unsupported reconciliation type for reporting"))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Reconciliation Report Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def validate_reconciliation_thresholds(reconciliation_data, thresholds=None):
    """
    Validate reconciliation results against thresholds
    """
    try:
        data = frappe.parse_json(reconciliation_data) if isinstance(reconciliation_data, str) else reconciliation_data

        default_thresholds = {
            'max_difference': 100.00,  # Maximum allowed difference
            'max_percentage': 0.1,     # Maximum allowed percentage difference (10%)
            'critical_difference': 1000.00  # Critical difference threshold
        }

        if thresholds:
            thresholds = frappe.parse_json(thresholds) if isinstance(thresholds, str) else thresholds
            default_thresholds.update(thresholds)

        validation_results = []

        for result in data.get('results', []):
            difference = abs(result.get('difference', 0))
            amount = abs(result.get('ledger_balance', 0) or result.get('ar_balance', 0) or result.get('ap_balance', 0))

            # Calculate percentage difference
            percentage_diff = (difference / amount * 100) if amount > 0 else 0

            # Determine severity
            if difference > default_thresholds['critical_difference']:
                severity = 'Critical'
            elif difference > default_thresholds['max_difference'] or percentage_diff > default_thresholds['max_percentage']:
                severity = 'High'
            elif difference > 0:
                severity = 'Medium'
            else:
                severity = 'Low'

            validation_results.append({
                'record_id': result.get('customer_no') or result.get('vendor_no') or result.get('item_no'),
                'difference': difference,
                'percentage_difference': percentage_diff,
                'severity': severity,
                'within_thresholds': difference <= default_thresholds['max_difference'] and percentage_diff <= default_thresholds['max_percentage']
            })

        # Summary
        critical_count = len([r for r in validation_results if r['severity'] == 'Critical'])
        high_count = len([r for r in validation_results if r['severity'] == 'High'])
        within_thresholds = len([r for r in validation_results if r['within_thresholds']])

        return {
            'validation_results': validation_results,
            'summary': {
                'total_records': len(validation_results),
                'within_thresholds': within_thresholds,
                'critical_issues': critical_count,
                'high_issues': high_count,
                'overall_compliance': (within_thresholds / len(validation_results) * 100) if validation_results else 100
            },
            'thresholds_used': default_thresholds
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Reconciliation Validation Error"))
        frappe.throw(str(e))
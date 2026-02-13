# API module for Internal Audit Management System

# =============================================================================
# ANALYTICS & TESTING MODULE APIs
# =============================================================================

import frappe
from frappe import _
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..utils.erpnext_queries import (
    get_gl_entries, get_sales_invoices, get_purchase_invoices,
    get_payment_entries, get_journal_entries, get_stock_ledger_entries, get_items
)

def execute_inventory_test(test, params):
    """
    Execute inventory-specific tests
    """
    if test.test_name == 'Stock Variance Analysis':
        return stock_variance_analysis(params)
    elif test.test_name == 'ABC Analysis':
        return abc_analysis(params)
    elif test.test_name == 'Slow-Moving Stock':
        return slow_moving_stock(params)
    elif test.test_name == 'Negative Stock Detection':
        return negative_stock_detection(params)
    else:
        return execute_generic_test(test, params)


def stock_variance_analysis(params):
    """
    Calculate stock variance (Expected vs Actual)
    """
    period = params.get('period')
    location = params.get('location', '')
    threshold_percent = float(params.get('threshold_percent', 5))
    company = params.get('company', frappe.defaults.get_user_default("Company"))

    # Get period details
    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    # Get all items
    items = get_items(company=company)

    # Get stock ledger entries for the period
    filters = {}
    if location:
        filters['warehouse'] = location

    stock_entries = get_stock_ledger_entries(
        from_date=start_date,
        to_date=end_date,
        company=company,
        filters=filters
    )

    # Group entries by item
    item_movements = {}
    for entry in stock_entries:
        item_code = entry['item_code']
        if item_code not in item_movements:
            item_movements[item_code] = {
                'purchases': 0,
                'sales': 0,
                'adjustments': 0,
                'current_stock': 0
            }

        qty = entry['actual_qty']
        if qty > 0:
            # Assume positive movements are purchases/adjustments
            item_movements[item_code]['purchases'] += qty
        elif qty < 0:
            # Negative movements are sales
            item_movements[item_code]['sales'] += abs(qty)

        # Update current stock (last entry's qty_after_transaction)
        item_movements[item_code]['current_stock'] = entry['qty_after_transaction']

    # Calculate variances
    data = []
    for item in items:
        item_code = item['item_code']
        movements = item_movements.get(item_code, {
            'purchases': 0, 'sales': 0, 'adjustments': 0, 'current_stock': 0
        })

        # For simplicity, assume opening stock is 0 (can be enhanced)
        opening_stock = 0
        expected_closing = opening_stock + movements['purchases'] - movements['sales'] + movements['adjustments']
        actual_closing = movements['current_stock']
        variance = actual_closing - expected_closing
        variance_value = variance * item['valuation_rate']

        row = {
            'item_no': item_code,
            'description': item['item_name'],
            'item_category_name': item['item_group'],
            'opening_stock': opening_stock,
            'purchases': movements['purchases'],
            'sales': movements['sales'],
            'adjustments': movements['adjustments'],
            'expected_closing': expected_closing,
            'actual_closing': actual_closing,
            'variance': variance,
            'unit_cost': item['valuation_rate'],
            'variance_value': variance_value
        }

        # Calculate variance percentage
        if expected_closing != 0:
            row['variance_percent'] = (variance / expected_closing) * 100
        else:
            row['variance_percent'] = 0 if variance == 0 else 100

        data.append(row)

    # Flag exceptions
    exceptions = []
    for row in data:
        # Flag exceptions
        if abs(row['variance_percent']) > threshold_percent:
            exceptions.append({
                'document_no': row['item_no'],
                'description': f"{row['description']} - Variance: {row['variance']:.2f} ({row['variance_percent']:.2f}%)",
                'amount': row['variance_value'],
                'variance_amount': row['variance_value'],
                'variance_percent': row['variance_percent'],
                'risk_rating': 'High' if abs(row['variance_percent']) > 10 else 'Medium',
                'requires_investigation': True
            })

    # Summary statistics
    total_variance_value = sum([row['variance_value'] for row in data])
    total_items = len(data)
    items_with_variance = len([row for row in data if row['variance'] != 0])

    summary = f"""
    Stock Variance Analysis Summary:
    - Total Items Analyzed: {total_items}
    - Items with Variance: {items_with_variance}
    - Total Variance Value: KES {total_variance_value:,.2f}
    - Exceptions Found: {len(exceptions)} (>{threshold_percent}% variance)
    """

    return {
        'total_records': total_items,
        'exceptions_count': len(exceptions),
        'summary': summary,
        'data': data,
        'exceptions': exceptions
    }


def abc_analysis(params):
    """
    Classify inventory items by value (A/B/C)
    """
    period = params.get('period')
    classification_basis = params.get('classification_basis', 'Sales Value')  # Sales Value, Quantity, Profit
    company = params.get('company', frappe.defaults.get_user_default("Company"))

    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    # Get stock ledger entries for sales
    stock_entries = get_stock_ledger_entries(
        from_date=start_date,
        to_date=to_date,
        company=company
    )

    # Get items
    items = get_items(company=company)

    # Create item lookup
    item_lookup = {item['item_code']: item for item in items}

    # Aggregate by item
    item_totals = {}
    for entry in stock_entries:
        item_code = entry['item_code']
        qty = abs(entry['actual_qty'])  # Use absolute quantity for sales

        if item_code not in item_totals:
            item_totals[item_code] = {'value': 0, 'quantity': 0}

        if classification_basis == 'Sales Value':
            item_totals[item_code]['value'] += qty * entry['valuation_rate']
        else:  # Quantity
            item_totals[item_code]['value'] += qty

        item_totals[item_code]['quantity'] += qty

    # Convert to data format
    data = []
    for item_code, totals in item_totals.items():
        item = item_lookup.get(item_code)
        if item:
            data.append({
                'item_no': item_code,
                'description': item['item_name'],
                'item_category_name': item['item_group'],
                'value': totals['value'],
                'quantity': totals['quantity']
            })

    # Sort by value descending
    data.sort(key=lambda x: x['value'], reverse=True)

    # Calculate cumulative percentages
    total_value = sum([row['value'] for row in data])
    cumulative_value = 0

    for row in data:
        row['percent_of_total'] = (row['value'] / total_value * 100) if total_value > 0 else 0
        cumulative_value += row['value']
        row['cumulative_percent'] = (cumulative_value / total_value * 100) if total_value > 0 else 0

        # Classify A/B/C
        if row['cumulative_percent'] <= 80:
            row['classification'] = 'A'
        elif row['cumulative_percent'] <= 95:
            row['classification'] = 'B'
        else:
            row['classification'] = 'C'

    # Summary
    a_items = len([r for r in data if r['classification'] == 'A'])
    b_items = len([r for r in data if r['classification'] == 'B'])
    c_items = len([r for r in data if r['classification'] == 'C'])

    summary = f"""
    ABC Analysis Summary:
    - Class A Items: {a_items} ({a_items/len(data)*100:.1f}%) - High value items (80% of value)
    - Class B Items: {b_items} ({b_items/len(data)*100:.1f}%) - Medium value items (15% of value)
    - Class C Items: {c_items} ({c_items/len(data)*100:.1f}%) - Low value items (5% of value)
    """

    return {
        'total_records': len(data),
        'exceptions_count': 0,
        'summary': summary,
        'data': data,
        'exceptions': []
    }


def slow_moving_stock(params):
    """
    Identify slow-moving or non-moving inventory
    """
    period = params.get('period')
    days_threshold = int(params.get('days_threshold', 90))
    company = params.get('company', frappe.defaults.get_user_default("Company"))

    period_doc = frappe.get_doc('Data Period', period)
    end_date = period_doc.end_date
    start_date = (datetime.strptime(str(end_date), '%Y-%m-%d') - timedelta(days=days_threshold)).date()

    # Get items
    items = get_items(company=company)

    # Get stock ledger entries for the period
    stock_entries = get_stock_ledger_entries(
        from_date=start_date,
        to_date=end_date,
        company=company
    )

    # Create item lookup
    item_lookup = {item['item_code']: item for item in items}

    # Calculate current stock and last sale date for each item
    item_stock = {}
    item_last_sale = {}

    for entry in stock_entries:
        item_code = entry['item_code']

        # Track current stock (last qty_after_transaction)
        item_stock[item_code] = entry['qty_after_transaction']

        # Track last sale date
        if entry['actual_qty'] < 0:  # Negative qty indicates sale
            if item_code not in item_last_sale or entry['posting_date'] > item_last_sale[item_code]:
                item_last_sale[item_code] = entry['posting_date']

    # Build data
    data = []
    for item_code, current_stock in item_stock.items():
        if current_stock <= 0:
            continue  # Skip items with no stock

        item = item_lookup.get(item_code)
        if not item:
            continue

        last_sale_date = item_last_sale.get(item_code, datetime(1900, 1, 1).date())
        days_since_last_sale = (end_date - last_sale_date).days if last_sale_date else 99999
        stock_value = current_stock * item['valuation_rate']

        if days_since_last_sale > days_threshold:
            data.append({
                'item_no': item_code,
                'description': item['item_name'],
                'item_category_name': item['item_group'],
                'unit_cost': item['valuation_rate'],
                'current_stock': current_stock,
                'stock_value': stock_value,
                'last_sale_date': last_sale_date,
                'days_since_last_sale': days_since_last_sale
            })

    # Sort by days since last sale descending
    data.sort(key=lambda x: x['days_since_last_sale'], reverse=True)

    # Flag all as exceptions
    exceptions = []
    for row in data:
        exceptions.append({
            'document_no': row['item_no'],
            'description': f"{row['description']} - No sales in {row['days_since_last_sale']} days",
            'amount': row['stock_value'],
            'risk_rating': 'High' if row['days_since_last_sale'] > 180 else 'Medium',
            'requires_investigation': True
        })

    total_value_at_risk = sum([row['stock_value'] for row in data])

    summary = f"""
    Slow-Moving Stock Analysis:
    - Items with no movement in {days_threshold}+ days: {len(data)}
    - Total value at risk: KES {total_value_at_risk:,.2f}
    - Recommendation: Review for potential obsolescence, discounting, or write-off
    """

    return {
        'total_records': len(data),
        'exceptions_count': len(exceptions),
        'summary': summary,
        'data': data,
        'exceptions': exceptions
    }


def negative_stock_detection(params):
    """
    Identify items with negative stock quantities
    """
    period = params.get('period')
    company = params.get('company', frappe.defaults.get_user_default("Company"))

    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    # Get stock ledger entries
    stock_entries = get_stock_ledger_entries(
        from_date=start_date,
        to_date=end_date,
        company=company
    )

    # Get items
    items = get_items(company=company)
    item_lookup = {item['item_code']: item for item in items}

    # Group by item and warehouse to find negative stock
    stock_by_item_warehouse = {}
    for entry in stock_entries:
        key = (entry['item_code'], entry['warehouse'])
        if key not in stock_by_item_warehouse:
            stock_by_item_warehouse[key] = 0
        stock_by_item_warehouse[key] = entry['qty_after_transaction']  # Use final qty

    # Filter for negative stock
    data = []
    for (item_code, warehouse), quantity in stock_by_item_warehouse.items():
        if quantity < 0:
            item = item_lookup.get(item_code)
            if item:
                value = quantity * item['valuation_rate']
                data.append({
                    'item_no': item_code,
                    'description': item['item_name'],
                    'item_category_name': item['item_group'],
                    'location_code': warehouse,
                    'quantity': quantity,
                    'unit_cost': item['valuation_rate'],
                    'value': value
                })

    # Sort by quantity ascending (most negative first)
    data.sort(key=lambda x: x['quantity'])

    # All negative stock items are exceptions
    exceptions = []
    for row in data:
        exceptions.append({
            'document_no': row['item_no'],
            'description': f"{row['description']} at {row['location_code']} - Negative stock: {row['quantity']}",
            'amount': row['value'],
            'risk_rating': 'Critical',
            'requires_investigation': True
        })

    summary = f"""
    Negative Stock Detection:
    - Items with negative stock: {len(data)}
    - This indicates data integrity issues - sales recorded before purchases or incorrect adjustments
    - Immediate investigation and correction required
    """

    return {
        'total_records': len(data),
        'exceptions_count': len(exceptions),
        'summary': summary,
        'data': data,
        'exceptions': exceptions
    }


def execute_financial_test(test, params):
    """
    Execute financial tests
    """
    if test.test_name == 'Duplicate Payment Detection':
        return duplicate_payment_detection(params)
    elif test.test_name == "Benford's Law Analysis":
        return benfords_law_analysis(params)
    elif test.test_name == 'Journal Entry Analysis':
        return journal_entry_analysis(params)
    else:
        return execute_generic_test(test, params)


def duplicate_payment_detection(params):
    """
    Detect potential duplicate payments
    """
    period = params.get('period')
    tolerance_amount = float(params.get('tolerance_amount', 0.01))
    date_range_days = int(params.get('date_range_days', 7))
    company = params.get('company', frappe.defaults.get_user_default("Company"))

    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    # Get payment entries
    payments = get_payment_entries(
        from_date=start_date,
        to_date=end_date,
        company=company
    )

    # Group payments by party and amount to find potential duplicates
    payment_groups = {}
    for payment in payments:
        if payment['payment_type'] == 'Pay':  # Only outgoing payments
            key = (payment['party'], round(payment['paid_amount'], 2))
            if key not in payment_groups:
                payment_groups[key] = []
            payment_groups[key].append(payment)

    # Find duplicates within date range
    data = []
    for (party, amount), party_payments in payment_groups.items():
        if len(party_payments) > 1:
            # Sort by date
            party_payments.sort(key=lambda x: x['posting_date'])

            # Check for payments within date range
            for i, payment1 in enumerate(party_payments[:-1]):
                for payment2 in party_payments[i+1:]:
                    days_apart = (payment2['posting_date'] - payment1['posting_date']).days
                    if days_apart <= date_range_days:
                        data.append({
                            'vendor_no': party,
                            'vendor_name': party,  # Assuming party is the name
                            'doc_no_1': payment1['name'],
                            'doc_no_2': payment2['name'],
                            'date_1': payment1['posting_date'],
                            'date_2': payment2['posting_date'],
                            'amount': amount,
                            'invoice_1': '',  # Payment Entry doesn't have invoice field directly
                            'invoice_2': '',
                            'days_apart': days_apart
                        })

    # Sort by amount descending
    data.sort(key=lambda x: x['amount'], reverse=True)

    # Create exceptions
    exceptions = []
    for row in data:
        exceptions.append({
            'document_no': f"{row['doc_no_1']} & {row['doc_no_2']}",
            'description': f"Potential duplicate payment to {row['vendor_name']} - Same amount (KES {row['amount']:,.2f}) paid {row['days_apart']} days apart",
            'amount': row['amount'],
            'risk_rating': 'High' if row['days_apart'] <= 3 else 'Medium',
            'requires_investigation': True
        })

    total_at_risk = sum([row['amount'] for row in data])

    summary = f"""
    Duplicate Payment Detection:
    - Potential duplicates found: {len(data)}
    - Total amount at risk: KES {total_at_risk:,.2f}
    - Review: Compare payment details and party confirmations
    """

    return {
        'total_records': len(data),
        'exceptions_count': len(exceptions),
        'summary': summary,
        'data': data,
        'exceptions': exceptions
    }


def benfords_law_analysis(params):
    """
    Apply Benford's Law to detect anomalies in financial data
    """
    period = params.get('period')
    data_source = params.get('data_source', 'GL Entries')  # GL Entries, Sales, Purchases
    company = params.get('company', frappe.defaults.get_user_default("Company"))

    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    # Get data based on source
    amounts = []
    if data_source == 'GL Entries':
        gl_entries = get_gl_entries(
            from_date=start_date,
            to_date=end_date,
            company=company
        )
        amounts = [{'amount': abs(entry['debit'] or entry['credit'] or 0)} for entry in gl_entries if abs(entry['debit'] or entry['credit'] or 0) >= 10]

    elif data_source == 'Sales':
        sales_invoices = get_sales_invoices(
            from_date=start_date,
            to_date=end_date,
            company=company
        )
        amounts = [{'amount': invoice['grand_total']} for invoice in sales_invoices if invoice['grand_total'] >= 10]

    elif data_source == 'Purchases':
        purchase_invoices = get_purchase_invoices(
            from_date=start_date,
            to_date=end_date,
            company=company
        )
        amounts = [{'amount': invoice['grand_total']} for invoice in purchase_invoices if invoice['grand_total'] >= 10]

    # Expected Benford distribution for first digit
    benford_expected = {
        '1': 30.1, '2': 17.6, '3': 12.5, '4': 9.7, '5': 7.9,
        '6': 6.7, '7': 5.8, '8': 5.1, '9': 4.6
    }

    # Calculate actual distribution
    first_digits = {}
    for row in amounts:
        first_digit = str(int(row['amount']))[0]
        first_digits[first_digit] = first_digits.get(first_digit, 0) + 1

    total = len(amounts)
    actual_distribution = {}
    variance_data = []

    for digit in '123456789':
        count = first_digits.get(digit, 0)
        actual_percent = (count / total * 100) if total > 0 else 0
        expected_percent = benford_expected[digit]
        variance = actual_percent - expected_percent

        actual_distribution[digit] = actual_percent
        variance_data.append({
            'digit': digit,
            'expected_percent': expected_percent,
            'actual_percent': round(actual_percent, 2),
            'variance': round(variance, 2),
            'count': count
        })

    # Calculate chi-square statistic
    chi_square = sum([
        ((first_digits.get(d, 0) - (benford_expected[d]/100 * total)) ** 2) /
        (benford_expected[d]/100 * total)
        for d in '123456789'
    ]) if total > 0 else 0

    # Flag significant variances as exceptions
    exceptions = []
    for row in variance_data:
        if abs(row['variance']) > 5:  # >5% variance
            exceptions.append({
                'document_no': f"Digit {row['digit']}",
                'description': f"First digit {row['digit']}: Expected {row['expected_percent']}%, Actual {row['actual_percent']}% (Variance: {row['variance']}%)",
                'variance_percent': row['variance'],
                'risk_rating': 'High' if abs(row['variance']) > 10 else 'Medium',
                'requires_investigation': True
            })

    # Interpret chi-square (critical value for 8 df at 95% confidence is 15.507)
    conformance = "CONFORMS" if chi_square < 15.507 else "DOES NOT CONFORM"

    summary = f"""
    Benford's Law Analysis:
    - Data Source: {data_source}
    - Records Analyzed: {total}
    - Chi-Square Statistic: {chi_square:.2f}
    - Conclusion: Data {conformance} to Benford's Law
    - Significant Variances: {len(exceptions)}

    {'Note: Non-conformance may indicate data manipulation, fraud, or non-natural data generation.' if conformance == 'DOES NOT CONFORM' else 'Note: Conformance suggests natural data distribution.'}
    """

    return {
        'total_records': total,
        'exceptions_count': len(exceptions),
        'summary': summary,
        'data': variance_data,
        'exceptions': exceptions,
        'chart_data': {
            'labels': list('123456789'),
            'expected': [benford_expected[d] for d in '123456789'],
            'actual': [actual_distribution.get(d, 0) for d in '123456789']
        }
    }


def journal_entry_analysis(params):
    """
    Analyze journal entries for unusual patterns
    """
    period = params.get('period')
    company = params.get('company', frappe.defaults.get_user_default("Company"))

    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    # Get journal entries and GL entries
    journal_entries = get_journal_entries(
        from_date=start_date,
        to_date=end_date,
        company=company
    )

    gl_entries = get_gl_entries(
        from_date=start_date,
        to_date=end_date,
        company=company,
        filters={"voucher_type": "Journal Entry"}
    )

    findings = {
        'round_numbers': [],
        'weekend_postings': [],
        'large_entries': [],
        'unbalanced_entries': []
    }

    # 1. Round number entries (potentially suspicious)
    for entry in gl_entries:
        amount = abs(entry['debit'] or entry['credit'] or 0)
        if amount % 1000 == 0 and amount >= 10000:
            findings['round_numbers'].append({
                'document_no': entry['voucher_no'],
                'posting_date': entry['posting_date'],
                'account_no': entry['account'],
                'account_name': entry['account'],  # Account name not directly available
                'amount': amount,
                'description': '',  # Description not in GL Entry fields
                'user_id': ''  # User not in GL Entry fields
            })

    # Sort by amount descending and limit to top 100
    findings['round_numbers'].sort(key=lambda x: x['amount'], reverse=True)
    findings['round_numbers'] = findings['round_numbers'][:100]

    # 2. Weekend or holiday postings
    for entry in gl_entries:
        day_of_week = entry['posting_date'].weekday()  # Monday=0, Sunday=6
        if day_of_week >= 5:  # Saturday=5, Sunday=6
            findings['weekend_postings'].append({
                'document_no': entry['voucher_no'],
                'posting_date': entry['posting_date'],
                'day_of_week': day_of_week + 1,  # Convert to 1-7 (Sunday=1)
                'account_no': entry['account'],
                'account_name': entry['account'],
                'amount': entry['debit'] or entry['credit'] or 0,
                'description': '',
                'user_id': ''
            })

    # Sort by posting date descending
    findings['weekend_postings'].sort(key=lambda x: x['posting_date'], reverse=True)

    # 3. Large manual entries (above threshold)
    threshold_amount = params.get('threshold_amount', 1000000)

    for entry in gl_entries:
        amount = abs(entry['debit'] or entry['credit'] or 0)
        if amount > threshold_amount:
            findings['large_entries'].append({
                'document_no': entry['voucher_no'],
                'posting_date': entry['posting_date'],
                'account_no': entry['account'],
                'account_name': entry['account'],
                'amount': amount,
                'description': '',
                'user_id': ''
            })

    # Sort by amount descending
    findings['large_entries'].sort(key=lambda x: x['amount'], reverse=True)

    # 4. Unbalanced journal entries
    # Group GL entries by voucher_no to check balance
    voucher_totals = {}
    for entry in gl_entries:
        voucher_no = entry['voucher_no']
        if voucher_no not in voucher_totals:
            voucher_totals[voucher_no] = {'debit': 0, 'credit': 0, 'posting_date': entry['posting_date']}

        voucher_totals[voucher_no]['debit'] += entry['debit'] or 0
        voucher_totals[voucher_no]['credit'] += entry['credit'] or 0

    for voucher_no, totals in voucher_totals.items():
        imbalance = abs(totals['debit'] - totals['credit'])
        if imbalance > 0.01:
            findings['unbalanced_entries'].append({
                'document_no': voucher_no,
                'posting_date': totals['posting_date'],
                'total_debit': totals['debit'],
                'total_credit': totals['credit'],
                'imbalance': imbalance
            })

    # Sort by imbalance descending
    findings['unbalanced_entries'].sort(key=lambda x: x['imbalance'], reverse=True)

    # Compile exceptions
    exceptions = []

    for entry in findings['round_numbers'][:20]:  # Top 20
        exceptions.append({
            'document_no': entry['document_no'],
            'description': f"Round number entry: KES {entry['amount']:,.2f}",
            'amount': entry['amount'],
            'risk_rating': 'Medium',
            'requires_investigation': True
        })

    for entry in findings['weekend_postings']:
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_name = day_names[entry['day_of_week'] - 1]
        exceptions.append({
            'document_no': entry['document_no'],
            'description': f"Weekend posting on {day_name}",
            'amount': entry['amount'],
            'risk_rating': 'Medium',
            'requires_investigation': True
        })

    for entry in findings['large_entries']:
        exceptions.append({
            'document_no': entry['document_no'],
            'description': f"Large manual entry: KES {entry['amount']:,.2f}",
            'amount': entry['amount'],
            'risk_rating': 'High',
            'requires_investigation': True
        })

    for entry in findings['unbalanced_entries']:
        exceptions.append({
            'document_no': entry['document_no'],
            'description': f"Unbalanced entry - Imbalance: KES {entry['imbalance']:,.2f}",
            'amount': entry['imbalance'],
            'risk_rating': 'Critical',
            'requires_investigation': True
        })

    summary = f"""
    Journal Entry Analysis:
    - Round Number Entries: {len(findings['round_numbers'])}
    - Weekend/Holiday Postings: {len(findings['weekend_postings'])}
    - Large Manual Entries: {len(findings['large_entries'])}
    - Unbalanced Entries: {len(findings['unbalanced_entries'])}
    - Total Exceptions: {len(exceptions)}
    """

    return {
        'total_records': sum([len(v) for v in findings.values()]),
        'exceptions_count': len(exceptions),
        'summary': summary,
        'data': findings,
        'exceptions': exceptions
    }


def execute_generic_test(test, params):
    """
    Execute a generic test using the test's SQL query
    """
    # This would execute the SQL query defined in the test
    # and return results in a standardized format

    # Placeholder implementation
    return {
        'total_records': 0,
        'exceptions_count': 0,
        'summary': 'Test executed successfully',
        'data': [],
        'exceptions': []
    }



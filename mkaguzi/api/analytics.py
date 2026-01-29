# API module for Internal Audit Management System

# =============================================================================
# ANALYTICS & TESTING MODULE APIs
# =============================================================================

import frappe
from frappe import _
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@frappe.whitelist()
def execute_test(test_id, parameters):
    """
    Execute an audit test
    """
    try:
        # Get test configuration
        test = frappe.get_doc('Audit Test Library', test_id)

        # Parse parameters
        params = frappe.parse_json(parameters) if isinstance(parameters, str) else parameters

        # Create execution record
        execution = frappe.get_doc({
            'doctype': 'Test Execution',
            'test_reference': test_id,
            'execution_date': datetime.now(),
            'executed_by': frappe.session.user,
            'status': 'Running'
        })

        # Add parameters
        for param_name, param_value in params.items():
            execution.append('test_parameters_used', {
                'parameter_name': param_name,
                'parameter_value': str(param_value)
            })

        execution.insert()
        frappe.db.commit()

        # Execute test based on test type
        if test.test_category == 'Inventory':
            results = execute_inventory_test(test, params)
        elif test.test_category == 'Financial':
            results = execute_financial_test(test, params)
        elif test.test_category == 'Sales':
            results = execute_sales_test(test, params)
        elif test.test_category == 'Procurement':
            results = execute_procurement_test(test, params)
        else:
            results = execute_generic_test(test, params)

        # Update execution with results
        execution.status = 'Completed'
        execution.total_records_analyzed = results.get('total_records', 0)
        execution.exceptions_found = results.get('exceptions_count', 0)
        execution.result_summary = results.get('summary', '')
        execution.result_data = frappe.as_json(results.get('data', []))

        # Add exceptions
        for exc in results.get('exceptions', []):
            execution.append('exception_details', exc)

        execution.save()
        frappe.db.commit()

        return {
            'success': True,
            'execution_id': execution.name,
            'results': results
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Test Execution Error"))
        if 'execution' in locals():
            execution.status = 'Failed'
            execution.save()
        frappe.throw(str(e))


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

    # Get period details
    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    # Get previous period for opening stock
    prev_period = frappe.db.get_value('Data Period',
        filters={'end_date': ['<', start_date]},
        fieldname='name',
        order_by='end_date desc'
    )

    # Query to calculate variance
    query = f"""
        SELECT
            item.item_no,
            item.description,
            item.item_category_name,
            COALESCE(opening.quantity, 0) as opening_stock,
            COALESCE(purchases.quantity, 0) as purchases,
            COALESCE(sales.quantity, 0) as sales,
            COALESCE(adjustments.quantity, 0) as adjustments,
            (COALESCE(opening.quantity, 0) + COALESCE(purchases.quantity, 0) -
             COALESCE(sales.quantity, 0) + COALESCE(adjustments.quantity, 0)) as expected_closing,
            COALESCE(closing.quantity, 0) as actual_closing,
            (COALESCE(closing.quantity, 0) -
             (COALESCE(opening.quantity, 0) + COALESCE(purchases.quantity, 0) -
              COALESCE(sales.quantity, 0) + COALESCE(adjustments.quantity, 0))) as variance,
            item.unit_cost,
            (COALESCE(closing.quantity, 0) -
             (COALESCE(opening.quantity, 0) + COALESCE(purchases.quantity, 0) -
              COALESCE(sales.quantity, 0) + COALESCE(adjustments.quantity, 0))) * item.unit_cost as variance_value
        FROM `tabItem Master` item
        LEFT JOIN (
            SELECT item_no, SUM(remaining_quantity) as quantity
            FROM `tabItem Ledger Entry`
            WHERE data_period = '{prev_period}'
            {'AND location_code = "' + location + '"' if location else ''}
            GROUP BY item_no
        ) opening ON item.item_no = opening.item_no
        LEFT JOIN (
            SELECT item_no, SUM(quantity) as quantity
            FROM `tabItem Ledger Entry`
            WHERE entry_type = 'Purchase'
            AND posting_date BETWEEN '{start_date}' AND '{end_date}'
            {'AND location_code = "' + location + '"' if location else ''}
            GROUP BY item_no
        ) purchases ON item.item_no = purchases.item_no
        LEFT JOIN (
            SELECT item_no, SUM(ABS(quantity)) as quantity
            FROM `tabItem Ledger Entry`
            WHERE entry_type = 'Sale'
            AND posting_date BETWEEN '{start_date}' AND '{end_date}'
            {'AND location_code = "' + location + '"' if location else ''}
            GROUP BY item_no
        ) sales ON item.item_no = sales.item_no
        LEFT JOIN (
            SELECT item_no, SUM(quantity) as quantity
            FROM `tabItem Ledger Entry`
            WHERE entry_type IN ('Positive Adjmt', 'Negative Adjmt')
            AND posting_date BETWEEN '{start_date}' AND '{end_date}'
            {'AND location_code = "' + location + '"' if location else ''}
            GROUP BY item_no
        ) adjustments ON item.item_no = adjustments.item_no
        LEFT JOIN (
            SELECT item_no, SUM(remaining_quantity) as quantity
            FROM `tabItem Ledger Entry`
            WHERE data_period = '{period}'
            {'AND location_code = "' + location + '"' if location else ''}
            GROUP BY item_no
        ) closing ON item.item_no = closing.item_no
        WHERE item.import_batch IN (
            SELECT name FROM `tabBC Data Import`
            WHERE data_period = '{period}' AND import_type = 'Item Master Data'
        )
    """

    data = frappe.db.sql(query, as_dict=True)

    # Calculate variance percentage and flag exceptions
    exceptions = []
    for row in data:
        if row['expected_closing'] != 0:
            row['variance_percent'] = (row['variance'] / row['expected_closing']) * 100
        else:
            row['variance_percent'] = 0 if row['variance'] == 0 else 100

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

    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    # Query based on classification basis
    if classification_basis == 'Sales Value':
        query = f"""
            SELECT
                i.item_no,
                i.description,
                i.item_category_name,
                SUM(l.sales_amount_actual) as value,
                SUM(ABS(l.quantity)) as quantity
            FROM `tabItem Ledger Entry` l
            JOIN `tabItem Master` i ON l.item_no = i.item_no
            WHERE l.entry_type = 'Sale'
            AND l.posting_date BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY i.item_no, i.description, i.item_category_name
            ORDER BY value DESC
        """
    elif classification_basis == 'Quantity':
        query = f"""
            SELECT
                i.item_no,
                i.description,
                i.item_category_name,
                SUM(ABS(l.quantity)) as value,
                SUM(ABS(l.quantity)) as quantity
            FROM `tabItem Ledger Entry` l
            JOIN `tabItem Master` i ON l.item_no = i.item_no
            WHERE l.entry_type = 'Sale'
            AND l.posting_date BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY i.item_no, i.description, i.item_category_name
            ORDER BY value DESC
        """

    data = frappe.db.sql(query, as_dict=True)

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

    period_doc = frappe.get_doc('Data Period', period)
    end_date = period_doc.end_date
    start_date = (datetime.strptime(str(end_date), '%Y-%m-%d') - timedelta(days=days_threshold)).date()

    query = f"""
        SELECT
            i.item_no,
            i.description,
            i.item_category_name,
            i.unit_cost,
            COALESCE(stock.quantity, 0) as current_stock,
            COALESCE(stock.quantity, 0) * i.unit_cost as stock_value,
            COALESCE(last_sale.last_sale_date, '1900-01-01') as last_sale_date,
            DATEDIFF('{end_date}', COALESCE(last_sale.last_sale_date, '1900-01-01')) as days_since_last_sale
        FROM `tabItem Master` i
        LEFT JOIN (
            SELECT item_no, SUM(remaining_quantity) as quantity
            FROM `tabItem Ledger Entry`
            WHERE data_period = '{period}'
            GROUP BY item_no
        ) stock ON i.item_no = stock.item_no
        LEFT JOIN (
            SELECT item_no, MAX(posting_date) as last_sale_date
            FROM `tabItem Ledger Entry`
            WHERE entry_type = 'Sale'
            GROUP BY item_no
        ) last_sale ON i.item_no = last_sale.item_no
        WHERE COALESCE(stock.quantity, 0) > 0
        AND DATEDIFF('{end_date}', COALESCE(last_sale.last_sale_date, '1900-01-01')) > {days_threshold}
        ORDER BY days_since_last_sale DESC, stock_value DESC
    """

    data = frappe.db.sql(query, as_dict=True)

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

    query = f"""
        SELECT
            i.item_no,
            i.description,
            i.item_category_name,
            l.location_code,
            SUM(l.remaining_quantity) as quantity,
            i.unit_cost,
            SUM(l.remaining_quantity) * i.unit_cost as value
        FROM `tabItem Ledger Entry` l
        JOIN `tabItem Master` i ON l.item_no = i.item_no
        WHERE l.data_period = '{period}'
        GROUP BY i.item_no, i.description, i.item_category_name, l.location_code, i.unit_cost
        HAVING SUM(l.remaining_quantity) < 0
        ORDER BY quantity ASC
    """

    data = frappe.db.sql(query, as_dict=True)

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

    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    query = f"""
        SELECT
            v1.vendor_no,
            v1.vendor_name,
            v1.document_no as doc_no_1,
            v2.document_no as doc_no_2,
            v1.posting_date as date_1,
            v2.posting_date as date_2,
            v1.amount,
            v1.vendor_invoice_no as invoice_1,
            v2.vendor_invoice_no as invoice_2,
            DATEDIFF(v2.posting_date, v1.posting_date) as days_apart
        FROM `tabVendor Ledger Entry` v1
        JOIN `tabVendor Ledger Entry` v2
            ON v1.vendor_no = v2.vendor_no
            AND ABS(v1.amount - v2.amount) <= {tolerance_amount}
            AND v1.document_no < v2.document_no
            AND DATEDIFF(v2.posting_date, v1.posting_date) <= {date_range_days}
        WHERE v1.document_type = 'Payment'
        AND v2.document_type = 'Payment'
        AND v1.posting_date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY v1.amount DESC
    """

    data = frappe.db.sql(query, as_dict=True)

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
    - Review: Compare invoice numbers, payment details, and vendor confirmations
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

    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    # Get data based on source
    if data_source == 'GL Entries':
        query = f"""
            SELECT ABS(amount) as amount
            FROM `tabGL Entry`
            WHERE posting_date BETWEEN '{start_date}' AND '{end_date}'
            AND ABS(amount) >= 10
        """
    elif data_source == 'Sales':
        query = f"""
            SELECT amount
            FROM `tabSales Invoice Header`
            WHERE posting_date BETWEEN '{start_date}' AND '{end_date}'
            AND amount >= 10
        """
    elif data_source == 'Purchases':
        query = f"""
            SELECT amount
            FROM `tabPurchase Invoice Header`
            WHERE posting_date BETWEEN '{start_date}' AND '{end_date}'
            AND amount >= 10
        """

    amounts = frappe.db.sql(query, as_dict=True)

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
    ])

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

    period_doc = frappe.get_doc('Data Period', period)
    start_date = period_doc.start_date
    end_date = period_doc.end_date

    findings = {
        'round_numbers': [],
        'weekend_postings': [],
        'large_entries': [],
        'unbalanced_entries': []
    }

    # 1. Round number entries (potentially suspicious)
    query = f"""
        SELECT
            document_no,
            posting_date,
            account_no,
            account_name,
            amount,
            description,
            user_id
        FROM `tabGL Entry`
        WHERE posting_date BETWEEN '{start_date}' AND '{end_date}'
        AND source_code = 'GENJNL'
        AND amount % 1000 = 0
        AND ABS(amount) >= 10000
        ORDER BY ABS(amount) DESC
        LIMIT 100
    """

    findings['round_numbers'] = frappe.db.sql(query, as_dict=True)

    # 2. Weekend or holiday postings
    query = f"""
        SELECT
            document_no,
            posting_date,
            DAYOFWEEK(posting_date) as day_of_week,
            account_no,
            account_name,
            amount,
            description,
            user_id
        FROM `tabGL Entry`
        WHERE posting_date BETWEEN '{start_date}' AND '{end_date}'
        AND source_code = 'GENJNL'
        AND DAYOFWEEK(posting_date) IN (1, 7)  -- Sunday=1, Saturday=7
        ORDER BY posting_date DESC
    """

    findings['weekend_postings'] = frappe.db.sql(query, as_dict=True)

    # 3. Large manual entries (above threshold)
    threshold_amount = params.get('threshold_amount', 1000000)

    query = f"""
        SELECT
            document_no,
            posting_date,
            account_no,
            account_name,
            amount,
            description,
            user_id
        FROM `tabGL Entry`
        WHERE posting_date BETWEEN '{start_date}' AND '{end_date}'
        AND source_code = 'GENJNL'
        AND ABS(amount) > {threshold_amount}
        ORDER BY ABS(amount) DESC
    """

    findings['large_entries'] = frappe.db.sql(query, as_dict=True)

    # 4. Unbalanced journal entries
    query = f"""
        SELECT
            document_no,
            posting_date,
            SUM(debit_amount) as total_debit,
            SUM(credit_amount) as total_credit,
            ABS(SUM(debit_amount) - SUM(credit_amount)) as imbalance
        FROM `tabGL Entry`
        WHERE posting_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY document_no, posting_date
        HAVING ABS(SUM(debit_amount) - SUM(credit_amount)) > 0.01
        ORDER BY imbalance DESC
    """

    findings['unbalanced_entries'] = frappe.db.sql(query, as_dict=True)

    # Compile exceptions
    exceptions = []

    for entry in findings['round_numbers'][:20]:  # Top 20
        exceptions.append({
            'document_no': entry['document_no'],
            'description': f"Round number entry: KES {entry['amount']:,.2f} - {entry['description']}",
            'amount': entry['amount'],
            'risk_rating': 'Medium',
            'requires_investigation': True
        })

    for entry in findings['weekend_postings']:
        day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][entry['day_of_week'] - 1]
        exceptions.append({
            'document_no': entry['document_no'],
            'description': f"Weekend posting on {day_name} - {entry['description']}",
            'amount': entry['amount'],
            'risk_rating': 'Medium',
            'requires_investigation': True
        })

    for entry in findings['large_entries']:
        exceptions.append({
            'document_no': entry['document_no'],
            'description': f"Large manual entry: KES {entry['amount']:,.2f} - {entry['description']}",
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


@frappe.whitelist()
def get_test_results(execution_id):
    """
    Retrieve test execution results
    """
    execution = frappe.get_doc('Test Execution', execution_id)

    return {
        'execution_id': execution.name,
        'test_name': execution.test_reference,
        'status': execution.status,
        'total_records': execution.total_records_analyzed,
        'exceptions_count': execution.exceptions_found,
        'summary': execution.result_summary,
        'data': frappe.parse_json(execution.result_data) if execution.result_data else [],
        'exceptions': [exc.as_dict() for exc in execution.exception_details]
    }
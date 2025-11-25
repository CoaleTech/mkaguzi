import frappe
from frappe import _
import pandas as pd
import csv
import io
from datetime import datetime
import chardet

class CSVParser:
    """
    Enhanced CSV parser with encoding detection and data validation
    """

    @staticmethod
    def detect_encoding(file_content):
        """
        Detect the encoding of file content
        """
        try:
            result = chardet.detect(file_content)
            return result.get('encoding', 'utf-8')
        except:
            return 'utf-8'

    @staticmethod
    def parse_csv_file(file_path, delimiter=',', has_header=True, encoding=None):
        """
        Parse CSV file with automatic encoding detection
        """
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Detect encoding if not provided
            if not encoding:
                encoding = CSVParser.detect_encoding(file_content)

            # Parse CSV
            content_str = file_content.decode(encoding, errors='replace')
            csv_reader = csv.reader(io.StringIO(content_str), delimiter=delimiter)

            rows = list(csv_reader)

            if not rows:
                return {'success': False, 'error': 'File is empty'}

            # Extract header and data
            if has_header:
                header = rows[0]
                data_rows = rows[1:]
            else:
                # Generate column names
                header = [f'Column_{i+1}' for i in range(len(rows[0]))]
                data_rows = rows

            # Convert to list of dictionaries
            data = []
            for row in data_rows:
                if len(row) == len(header):
                    row_dict = dict(zip(header, row))
                    data.append(row_dict)

            return {
                'success': True,
                'header': header,
                'data': data,
                'total_rows': len(data),
                'encoding': encoding,
                'delimiter': delimiter
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def parse_csv_content(content, delimiter=',', has_header=True, encoding='utf-8'):
        """
        Parse CSV content string
        """
        try:
            csv_reader = csv.reader(io.StringIO(content), delimiter=delimiter)

            rows = list(csv_reader)

            if not rows:
                return {'success': False, 'error': 'Content is empty'}

            # Extract header and data
            if has_header:
                header = rows[0]
                data_rows = rows[1:]
            else:
                header = [f'Column_{i+1}' for i in range(len(rows[0]))]
                data_rows = rows

            # Convert to list of dictionaries
            data = []
            for row in data_rows:
                if len(row) == len(header):
                    row_dict = dict(zip(header, row))
                    data.append(row_dict)

            return {
                'success': True,
                'header': header,
                'data': data,
                'total_rows': len(data)
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def validate_csv_structure(data, required_columns=None, column_mappings=None):
        """
        Validate CSV structure and data
        """
        try:
            if not data or 'header' not in data or 'data' not in data:
                return {'valid': False, 'error': 'Invalid CSV data structure'}

            header = data['header']
            rows = data['data']

            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'column_count': len(header),
                'row_count': len(rows)
            }

            # Check required columns
            if required_columns:
                missing_columns = []
                for req_col in required_columns:
                    if req_col not in header:
                        missing_columns.append(req_col)

                if missing_columns:
                    validation_results['valid'] = False
                    validation_results['errors'].append(f"Missing required columns: {', '.join(missing_columns)}")

            # Check for empty rows
            empty_rows = 0
            for i, row in enumerate(rows):
                if all(not str(value).strip() for value in row.values()):
                    empty_rows += 1

            if empty_rows > 0:
                validation_results['warnings'].append(f"Found {empty_rows} empty rows")

            # Check column consistency
            inconsistent_rows = []
            for i, row in enumerate(rows):
                if len(row) != len(header):
                    inconsistent_rows.append(i + 1)

            if inconsistent_rows:
                validation_results['valid'] = False
                validation_results['errors'].append(f"Inconsistent column count in rows: {inconsistent_rows}")

            # Validate data types and formats
            data_validation = CSVParser.validate_data_types(rows, column_mappings)
            validation_results['errors'].extend(data_validation.get('errors', []))
            validation_results['warnings'].extend(data_validation.get('warnings', []))

            if data_validation.get('errors'):
                validation_results['valid'] = False

            return validation_results

        except Exception as e:
            return {'valid': False, 'error': str(e)}

    @staticmethod
    def validate_data_types(rows, column_mappings=None):
        """
        Validate data types in CSV rows
        """
        errors = []
        warnings = []

        if not column_mappings:
            return {'errors': errors, 'warnings': warnings}

        for i, row in enumerate(rows):
            row_num = i + 2  # Account for header row

            for col_name, expected_type in column_mappings.items():
                if col_name in row:
                    value = str(row[col_name]).strip()

                    if not value:  # Skip empty values
                        continue

                    # Type validation
                    if expected_type == 'number':
                        try:
                            float(value.replace(',', '').replace(' ', ''))
                        except ValueError:
                            errors.append(f"Row {row_num}, Column '{col_name}': Invalid number format")

                    elif expected_type == 'date':
                        # Try common date formats
                        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d']
                        valid_date = False
                        for fmt in date_formats:
                            try:
                                datetime.strptime(value, fmt)
                                valid_date = True
                                break
                            except ValueError:
                                continue

                        if not valid_date:
                            errors.append(f"Row {row_num}, Column '{col_name}': Invalid date format")

                    elif expected_type == 'boolean':
                        if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no', 'y', 'n']:
                            warnings.append(f"Row {row_num}, Column '{col_name}': Unexpected boolean value")

        return {'errors': errors, 'warnings': warnings}

    @staticmethod
    def clean_csv_data(data, cleaning_rules=None):
        """
        Clean and standardize CSV data
        """
        try:
            cleaned_data = []
            cleaning_stats = {
                'total_rows': len(data.get('data', [])),
                'cleaned_rows': 0,
                'corrections_made': 0
            }

            for row in data.get('data', []):
                cleaned_row = {}

                for col, value in row.items():
                    original_value = str(value).strip()

                    # Apply cleaning rules
                    if cleaning_rules and col in cleaning_rules:
                        rules = cleaning_rules[col]

                        # Trim whitespace
                        if rules.get('trim', True):
                            cleaned_value = original_value.strip()
                        else:
                            cleaned_value = original_value

                        # Convert to uppercase/lowercase
                        if rules.get('uppercase'):
                            cleaned_value = cleaned_value.upper()
                        elif rules.get('lowercase'):
                            cleaned_value = cleaned_value.lower()

                        # Remove specific characters
                        if rules.get('remove_chars'):
                            for char in rules['remove_chars']:
                                cleaned_value = cleaned_value.replace(char, '')

                        # Replace values
                        if rules.get('replace_values'):
                            for old_val, new_val in rules['replace_values'].items():
                                if cleaned_value == old_val:
                                    cleaned_value = new_val

                        # Number formatting
                        if rules.get('type') == 'number':
                            try:
                                # Remove commas and spaces
                                cleaned_value = cleaned_value.replace(',', '').replace(' ', '')
                                float(cleaned_value)  # Validate it's a number
                            except ValueError:
                                cleaned_value = original_value  # Keep original if invalid

                        # Date formatting
                        if rules.get('type') == 'date' and rules.get('date_format'):
                            try:
                                parsed_date = datetime.strptime(cleaned_value, rules['date_format'])
                                cleaned_value = parsed_date.strftime('%Y-%m-%d')
                            except ValueError:
                                pass  # Keep original if parsing fails

                    else:
                        # Default cleaning: trim whitespace
                        cleaned_value = original_value.strip()

                    cleaned_row[col] = cleaned_value

                    # Track changes
                    if cleaned_value != original_value:
                        cleaning_stats['corrections_made'] += 1

                cleaned_data.append(cleaned_row)
                cleaning_stats['cleaned_rows'] += 1

            return {
                'success': True,
                'cleaned_data': cleaned_data,
                'cleaning_stats': cleaning_stats
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def generate_csv_preview(data, max_rows=10):
        """
        Generate a preview of CSV data
        """
        try:
            header = data.get('header', [])
            rows = data.get('data', [])[:max_rows]

            preview = {
                'header': header,
                'rows': rows,
                'total_rows': len(data.get('data', [])),
                'preview_rows': len(rows),
                'has_more': len(data.get('data', [])) > max_rows
            }

            return preview

        except Exception as e:
            return {'error': str(e)}


@frappe.whitelist()
def parse_and_validate_csv(file_path, data_type=None, delimiter=',', has_header=True):
    """
    Parse and validate CSV file for import
    """
    try:
        # Parse CSV
        parser = CSVParser()
        parsed_data = parser.parse_csv_file(file_path, delimiter, has_header)

        if not parsed_data['success']:
            return parsed_data

        # Get validation rules based on data type
        validation_rules = {}
        if data_type:
            from .validators import get_validation_rules
            validation_rules = get_validation_rules(data_type)

        # Validate structure
        validation_result = parser.validate_csv_structure(parsed_data, validation_rules.get('required_columns'))

        # Generate preview
        preview = parser.generate_csv_preview(parsed_data)

        return {
            'success': True,
            'parsed_data': parsed_data,
            'validation': validation_result,
            'preview': preview,
            'data_type': data_type
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("CSV Parse and Validate Error"))
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def clean_csv_data(csv_data, cleaning_rules=None):
    """
    Clean CSV data using specified rules
    """
    try:
        data = frappe.parse_json(csv_data) if isinstance(csv_data, str) else csv_data
        rules = frappe.parse_json(cleaning_rules) if isinstance(cleaning_rules, str) else cleaning_rules

        parser = CSVParser()
        result = parser.clean_csv_data(data, rules)

        return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("CSV Data Cleaning Error"))
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def get_csv_column_mappings(data_type):
    """
    Get standard column mappings for different data types
    """
    mappings = {
        'customer_master': {
            'Customer No': 'customer_no',
            'Customer Name': 'customer_name',
            'PIN': 'pin',
            'Phone No': 'phone_no',
            'Email': 'email',
            'Postal Address': 'postal_address',
            'Credit Limit': 'credit_limit'
        },
        'vendor_master': {
            'Vendor No': 'vendor_no',
            'Vendor Name': 'vendor_name',
            'KRA PIN': 'kra_pin',
            'Phone No': 'phone_no',
            'Email': 'email',
            'Postal Address': 'postal_address'
        },
        'item_master': {
            'Item No': 'item_no',
            'Description': 'description',
            'Unit Cost': 'unit_cost',
            'Unit Price': 'unit_price',
            'Category': 'item_category_name'
        },
        'gl_entries': {
            'Posting Date': 'posting_date',
            'Document No': 'document_no',
            'Account No': 'account_no',
            'Account Name': 'account_name',
            'Debit Amount': 'debit_amount',
            'Credit Amount': 'credit_amount',
            'Description': 'description'
        }
    }

    return mappings.get(data_type, {})
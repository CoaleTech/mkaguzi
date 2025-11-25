import frappe
from frappe import _
import pandas as pd
import os
from datetime import datetime

@frappe.whitelist()
def upload_csv(import_type):
    """
    Handle CSV file upload
    """
    try:
        # Get uploaded file
        file = frappe.request.files.get('file')

        if not file:
            frappe.throw(_("No file uploaded"))

        # Save file temporarily
        file_path = save_uploaded_file(file)

        # Create import record
        import_doc = frappe.get_doc({
            'doctype': 'BC Data Import',
            'import_type': import_type,
            'import_file': file_path,
            'status': 'Draft',
            'imported_by': frappe.session.user
        })
        import_doc.insert()

        return {
            'success': True,
            'import_id': import_doc.name,
            'message': _('File uploaded successfully')
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("CSV Upload Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def validate_import(import_id):
    """
    Validate CSV data before import
    """
    try:
        import_doc = frappe.get_doc('BC Data Import', import_id)

        # Get import type configuration
        import_type = frappe.get_doc('CSV Import Type', import_doc.import_type)

        # Read CSV file
        df = pd.read_csv(import_doc.import_file)

        validation_results = {
            'total_rows': len(df),
            'errors': [],
            'warnings': [],
            'status': 'Pass'
        }

        # 1. Validate headers
        required_columns = [m.csv_column_name for m in import_type.field_mappings if m.is_required]
        missing_columns = set(required_columns) - set(df.columns)

        if missing_columns:
            validation_results['errors'].append({
                'type': 'Missing Columns',
                'message': f"Missing required columns: {', '.join(missing_columns)}"
            })
            validation_results['status'] = 'Fail'

        # 2. Validate data types
        for index, row in df.iterrows():
            for mapping in import_type.field_mappings:
                col_name = mapping.csv_column_name
                if col_name not in df.columns:
                    continue

                value = row[col_name]

                # Check required fields
                if mapping.is_required and pd.isna(value):
                    validation_results['errors'].append({
                        'row': index + 2,  # +2 for header and 0-index
                        'column': col_name,
                        'type': 'Required Field',
                        'message': f"{col_name} is required but empty"
                    })

                # Check data type
                if not pd.isna(value):
                    if mapping.data_type == 'Number' and not isinstance(value, (int, float)):
                        try:
                            float(value)
                        except:
                            validation_results['errors'].append({
                                'row': index + 2,
                                'column': col_name,
                                'type': 'Data Type',
                                'message': f"{col_name} should be numeric"
                            })

                    elif mapping.data_type == 'Date':
                        try:
                            pd.to_datetime(value)
                        except:
                            validation_results['errors'].append({
                                'row': index + 2,
                                'column': col_name,
                                'type': 'Data Type',
                                'message': f"{col_name} is not a valid date"
                            })

        # 3. Business rule validations
        if import_doc.import_type == 'General Ledger Entries':
            # Check debit = credit
            if 'debit_amount' in df.columns and 'credit_amount' in df.columns:
                total_debit = df['debit_amount'].sum()
                total_credit = df['credit_amount'].sum()

                if abs(total_debit - total_credit) > 0.01:
                    validation_results['warnings'].append({
                        'type': 'Reconciliation',
                        'message': f"Debit ({total_debit}) does not equal Credit ({total_credit})"
                    })

        # 4. Duplicate detection
        if 'document_no' in df.columns:
            duplicates = df[df.duplicated(subset=['document_no'], keep=False)]
            if len(duplicates) > 0:
                validation_results['warnings'].append({
                    'type': 'Duplicates',
                    'message': f"Found {len(duplicates)} duplicate document numbers"
                })

        # Update import doc with validation results
        import_doc.status = 'Validated' if validation_results['status'] == 'Pass' else 'Validation Failed'
        import_doc.total_rows = validation_results['total_rows']
        import_doc.failed_rows = len(validation_results['errors'])
        import_doc.warnings_count = len(validation_results['warnings'])

        # Save validation errors
        for error in validation_results['errors']:
            import_doc.append('error_log', {
                'row_number': error.get('row', 0),
                'column_name': error.get('column', ''),
                'error_type': error.get('type', ''),
                'error_message': error.get('message', ''),
                'row_data': ''
            })

        import_doc.save()

        return validation_results

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("CSV Validation Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def process_import(import_id):
    """
    Process validated CSV import
    """
    try:
        import_doc = frappe.get_doc('BC Data Import', import_id)

        if import_doc.status != 'Validated':
            frappe.throw(_("Import must be validated before processing"))

        # Update status
        import_doc.status = 'Processing'
        import_doc.save()
        frappe.db.commit()

        # Get import configuration
        import_type = frappe.get_doc('CSV Import Type', import_doc.import_type)
        target_doctype = import_type.target_doctype

        # Read CSV
        df = pd.read_csv(import_doc.import_file)

        success_count = 0
        error_count = 0

        # Process each row
        for index, row in df.iterrows():
            try:
                # Map CSV columns to DocType fields
                doc_data = {'doctype': target_doctype}

                for mapping in import_type.field_mappings:
                    csv_col = mapping.csv_column_name
                    target_field = mapping.target_field

                    if csv_col in row and not pd.isna(row[csv_col]):
                        value = row[csv_col]

                        # Apply transformations
                        if mapping.data_type == 'Date':
                            value = pd.to_datetime(value).date()
                        elif mapping.data_type == 'Currency' or mapping.data_type == 'Number':
                            value = float(value)

                        doc_data[target_field] = value

                # Add import batch reference
                doc_data['import_batch'] = import_doc.name
                doc_data['data_period'] = import_doc.import_period

                # Create document
                doc = frappe.get_doc(doc_data)
                doc.insert(ignore_permissions=True)
                success_count += 1

            except Exception as e:
                error_count += 1
                import_doc.append('error_log', {
                    'row_number': index + 2,
                    'error_type': 'Import Error',
                    'error_message': str(e),
                    'row_data': str(row.to_dict())
                })

        # Update import status
        import_doc.status = 'Completed' if error_count == 0 else 'Partially Completed'
        import_doc.successfully_imported = success_count
        import_doc.failed_rows = error_count
        import_doc.save()
        frappe.db.commit()

        return {
            'success': True,
            'imported': success_count,
            'failed': error_count,
            'message': _(f"Import completed: {success_count} records imported, {error_count} failed")
        }

    except Exception as e:
        import_doc.status = 'Failed'
        import_doc.save()
        frappe.db.commit()
        frappe.log_error(frappe.get_traceback(), _("CSV Import Processing Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_import_progress(import_id):
    """
    Get real-time import progress
    """
    import_doc = frappe.get_doc('BC Data Import', import_id)

    return {
        'status': import_doc.status,
        'total_rows': import_doc.total_rows,
        'successfully_imported': import_doc.successfully_imported,
        'failed_rows': import_doc.failed_rows,
        'progress_percent': (import_doc.successfully_imported / import_doc.total_rows * 100) if import_doc.total_rows > 0 else 0
    }


def save_uploaded_file(file):
    """
    Save uploaded file to files directory
    """
    filename = file.filename
    file_path = frappe.get_site_path('private', 'files', filename)

    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save file
    file.save(file_path)

    return file_path
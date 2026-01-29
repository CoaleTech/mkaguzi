import frappe
from frappe import _
import re
from datetime import datetime, date
import phonenumbers

class KenyanDataValidator:
    """
    Validator class for Kenyan business data
    """

    @staticmethod
    def validate_pin(pin):
        """
        Validate Kenyan PIN (Personal Identification Number)
        Format: A123456789X or A1234567890X
        """
        if not pin:
            return False, "PIN is required"

        # Remove any spaces or hyphens
        pin = pin.replace(' ', '').replace('-', '').upper()

        # Check basic format
        pin_pattern = r'^A\d{9}[A-Z0-9]$'
        if not re.match(pin_pattern, pin):
            return False, "Invalid PIN format. Should be A followed by 9 digits and end with a letter or digit"

        # Validate check digit algorithm
        try:
            digits = [int(c) for c in pin[1:-1]]  # Extract digits
            check_digit = pin[-1]

            # KRA PIN uses a modulo 11 check digit algorithm
            weights = [2, 7, 6, 5, 4, 3, 2]  # Weights for positions
            weighted_sum = sum(d * w for d, w in zip(digits, weights))

            remainder = weighted_sum % 11
            calculated_check = 11 - remainder if remainder > 1 else 1

            if check_digit.isdigit():
                if calculated_check % 10 != int(check_digit):
                    return False, "Invalid PIN - check digit mismatch"
            # If check digit is letter, accept format match

            return True, "Valid PIN"

        except (ValueError, TypeError, AttributeError) as e:
            frappe.log_error(f"PIN validation error: {str(e)}", "PIN Validation")
            return False, "Invalid PIN structure"

    @staticmethod
    def validate_phone_number(phone):
        """
        Validate Kenyan phone number
        """
        if not phone:
            return False, "Phone number is required"

        try:
            # Parse phone number
            parsed = phonenumbers.parse(phone, "KE")

            # Check if valid and Kenyan
            if not phonenumbers.is_valid_number(parsed):
                return False, "Invalid phone number"

            if not phonenumbers.is_valid_number_for_region(parsed, "KE"):
                return False, "Not a valid Kenyan phone number"

            # Format to international format
            formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

            return True, f"Valid phone number: {formatted}"

        except phonenumbers.NumberParseException:
            return False, "Invalid phone number format"

    @staticmethod
    def validate_id_number(id_number):
        """
        Validate Kenyan National ID number
        Format: 6 digits (birth date) + 3 digits (serial) + 1 check digit
        """
        if not id_number:
            return False, "ID number is required"

        # Remove any spaces
        id_number = id_number.replace(' ', '')

        # Check length
        if len(id_number) != 10:
            return False, "ID number must be 10 digits"

        # Check if all digits
        if not id_number.isdigit():
            return False, "ID number must contain only digits"

        # Extract components
        birth_date_str = id_number[:6]
        serial = id_number[6:9]
        check_digit = int(id_number[9])

        # Validate birth date
        try:
            birth_date = datetime.strptime(birth_date_str, '%y%m%d').date()
            today = date.today()

            # Check if birth date is not in future
            if birth_date > today:
                return False, "Birth date cannot be in the future"

            # Check if person is not too old (reasonable age check)
            age = (today - birth_date).days / 365.25
            if age > 120:
                return False, "Invalid birth date - age too high"

        except ValueError:
            return False, "Invalid birth date format in ID number"

        # Validate check digit properly (Kenyan ID uses modulo 11)
        try:
            digits = [int(d) for d in id_number[:9]]
            weights = [9, 8, 7, 6, 5, 4, 3, 2, 1]
            weighted_sum = sum(d * w for d, w in zip(digits, weights))
            calculated_check = weighted_sum % 11

            if calculated_check != check_digit:
                frappe.log_error(f"ID check digit mismatch for {id_number[:6]}", "ID Validation")
                return False, "Invalid ID number - check digit validation failed"

        except (ValueError, IndexError) as e:
            frappe.log_error(f"ID check digit calculation error: {str(e)}", "ID Validation")
            return False, "Invalid ID number structure"

        return True, "Valid ID number"

    @staticmethod
    def validate_email(email):
        """
        Validate email address
        """
        if not email:
            return False, "Email is required"

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            return False, "Invalid email format"

        return True, "Valid email address"

    @staticmethod
    def validate_business_name(name):
        """
        Validate business name
        """
        if not name:
            return False, "Business name is required"

        name = name.strip()

        if len(name) < 2:
            return False, "Business name too short"

        if len(name) > 100:
            return False, "Business name too long"

        # Check for invalid characters
        if re.search(r'[<>"/\\|?*]', name):
            return False, "Business name contains invalid characters"

        return True, "Valid business name"

    @staticmethod
    def validate_postal_address(address):
        """
        Validate postal address
        """
        if not address:
            return False, "Postal address is required"

        address = address.strip()

        if len(address) < 10:
            return False, "Address too short - please provide complete address"

        if len(address) > 200:
            return False, "Address too long"

        # Check for basic address components
        required_parts = ['P.O', 'BOX']  # Kenyan postal addresses typically have P.O. BOX
        has_postal = any(part.upper() in address.upper() for part in required_parts)

        if not has_postal:
            # Allow non-postal addresses but warn
            return True, "Address provided (consider using P.O. Box for official correspondence)"

        return True, "Valid postal address"

    @staticmethod
    def validate_amount(amount, min_value=0, max_value=None):
        """
        Validate monetary amount
        """
        try:
            amount = float(amount)

            if amount < min_value:
                return False, f"Amount cannot be less than {min_value}"

            if max_value and amount > max_value:
                return False, f"Amount cannot exceed {max_value}"

            # Check for suspicious rounding
            if amount == round(amount, -3):  # Rounded to nearest 1000
                return True, "Amount is rounded to nearest 1000 - please verify"

            return True, "Valid amount"

        except (ValueError, TypeError):
            return False, "Invalid amount format"

    @staticmethod
    def validate_date(date_str, min_date=None, max_date=None):
        """
        Validate date string
        """
        if not date_str:
            return False, "Date is required"

        try:
            parsed_date = datetime.strptime(str(date_str), '%Y-%m-%d').date()

            if min_date and parsed_date < min_date:
                return False, f"Date cannot be before {min_date}"

            if max_date and parsed_date > max_date:
                return False, f"Date cannot be after {max_date}"

            return True, "Valid date"

        except ValueError:
            return False, "Invalid date format (use YYYY-MM-DD)"

    @staticmethod
    def validate_bank_account(account_number, bank_code=None):
        """
        Validate Kenyan bank account number
        """
        if not account_number:
            return False, "Account number is required"

        # Remove spaces and hyphens
        account_number = account_number.replace(' ', '').replace('-', '')

        # Check length (most Kenyan accounts are 10-16 digits)
        if not 10 <= len(account_number) <= 16:
            return False, "Account number length invalid"

        # Check if all digits
        if not account_number.isdigit():
            return False, "Account number must contain only digits"

        # Basic format validation
        # Could add bank-specific validation if bank_code is provided

        return True, "Valid account number format"

    @staticmethod
    def validate_kra_pin(kra_pin):
        """
        Validate KRA PIN (Kenya Revenue Authority)
        Format: P051234567X or similar
        """
        if not kra_pin:
            return False, "KRA PIN is required"

        kra_pin = kra_pin.replace(' ', '').upper()

        # KRA PIN format: Letter + 9 digits + Letter/Number
        kra_pattern = r'^[A-Z]\d{9}[A-Z0-9]$'

        if not re.match(kra_pattern, kra_pin):
            return False, "Invalid KRA PIN format"

        return True, "Valid KRA PIN"


@frappe.whitelist()
def validate_import_data(data_type, value):
    """
    Validate import data based on type
    """
    validator = KenyanDataValidator()

    if data_type == 'pin':
        return validator.validate_pin(value)
    elif data_type == 'phone':
        return validator.validate_phone_number(value)
    elif data_type == 'id_number':
        return validator.validate_id_number(value)
    elif data_type == 'email':
        return validator.validate_email(value)
    elif data_type == 'business_name':
        return validator.validate_business_name(value)
    elif data_type == 'postal_address':
        return validator.validate_postal_address(value)
    elif data_type == 'amount':
        return validator.validate_amount(value)
    elif data_type == 'date':
        return validator.validate_date(value)
    elif data_type == 'bank_account':
        return validator.validate_bank_account(value)
    elif data_type == 'kra_pin':
        return validator.validate_kra_pin(value)
    else:
        return False, f"Unknown validation type: {data_type}"


@frappe.whitelist()
def validate_csv_row(row_data, validation_rules):
    """
    Validate a CSV row against validation rules
    """
    try:
        data = frappe.parse_json(row_data) if isinstance(row_data, str) else row_data
        rules = frappe.parse_json(validation_rules) if isinstance(validation_rules, str) else validation_rules

        errors = []
        warnings = []

        for field, rule in rules.items():
            if field in data:
                value = data[field]

                # Skip validation if field is empty and not required
                if not value and not rule.get('required', False):
                    continue

                # Check required fields
                if rule.get('required', False) and not value:
                    errors.append(f"{field}: Required field is empty")
                    continue

                # Type validation
                field_type = rule.get('type', 'string')
                if field_type == 'number':
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        errors.append(f"{field}: Must be a valid number")
                        continue
                elif field_type == 'date':
                    if not KenyanDataValidator.validate_date(value)[0]:
                        errors.append(f"{field}: Invalid date format")
                        continue
                elif field_type == 'email':
                    if not KenyanDataValidator.validate_email(value)[0]:
                        errors.append(f"{field}: Invalid email format")
                        continue

                # Custom validation
                if rule.get('validator'):
                    validator_name = rule['validator']
                    is_valid, message = validate_import_data(validator_name, value)
                    if not is_valid:
                        if 'please verify' in message.lower() or 'consider' in message.lower():
                            warnings.append(f"{field}: {message}")
                        else:
                            errors.append(f"{field}: {message}")

                # Range validation
                if field_type == 'number' and 'min' in rule:
                    try:
                        num_value = float(value)
                        if num_value < rule['min']:
                            errors.append(f"{field}: Value below minimum ({rule['min']})")
                    except (ValueError, TypeError):
                        pass

                if field_type == 'number' and 'max' in rule:
                    try:
                        num_value = float(value)
                        if num_value > rule['max']:
                            errors.append(f"{field}: Value above maximum ({rule['max']})")
                    except (ValueError, TypeError):
                        pass

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'error_count': len(errors),
            'warning_count': len(warnings)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("CSV Row Validation Error"))
        return {
            'valid': False,
            'errors': [str(e)],
            'warnings': [],
            'error_count': 1,
            'warning_count': 0
        }


@frappe.whitelist()
def get_validation_rules(data_type):
    """
    Get validation rules for different data types
    """
    rules = {
        'customer_master': {
            'customer_no': {'required': True, 'type': 'string', 'max_length': 20},
            'customer_name': {'required': True, 'type': 'string', 'validator': 'business_name'},
            'pin': {'required': False, 'type': 'string', 'validator': 'pin'},
            'phone_no': {'required': False, 'type': 'string', 'validator': 'phone'},
            'email': {'required': False, 'type': 'string', 'validator': 'email'},
            'postal_address': {'required': False, 'type': 'string', 'validator': 'postal_address'},
            'credit_limit': {'required': False, 'type': 'number', 'min': 0}
        },
        'vendor_master': {
            'vendor_no': {'required': True, 'type': 'string', 'max_length': 20},
            'vendor_name': {'required': True, 'type': 'string', 'validator': 'business_name'},
            'kra_pin': {'required': False, 'type': 'string', 'validator': 'kra_pin'},
            'phone_no': {'required': False, 'type': 'string', 'validator': 'phone'},
            'email': {'required': False, 'type': 'string', 'validator': 'email'},
            'postal_address': {'required': False, 'type': 'string', 'validator': 'postal_address'}
        },
        'item_master': {
            'item_no': {'required': True, 'type': 'string', 'max_length': 20},
            'description': {'required': True, 'type': 'string', 'max_length': 100},
            'unit_cost': {'required': False, 'type': 'number', 'min': 0},
            'unit_price': {'required': False, 'type': 'number', 'min': 0}
        },
        'gl_entries': {
            'posting_date': {'required': True, 'type': 'date'},
            'document_no': {'required': True, 'type': 'string'},
            'account_no': {'required': True, 'type': 'string'},
            'debit_amount': {'required': False, 'type': 'number', 'min': 0},
            'credit_amount': {'required': False, 'type': 'number', 'min': 0}
        }
    }

    return rules.get(data_type, {})
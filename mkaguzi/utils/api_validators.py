"""API Input Validation Utilities for Mkaguzi

This module provides validation functions for API endpoints to ensure
data integrity and security.
"""

import frappe
from frappe import _
from typing import Any, Dict, List, Optional


def validate_audit_trail_params(doctype: Optional[str] = None,
                                 docname: Optional[str] = None,
                                 limit: int = 100,
                                 start: int = 0) -> Dict[str, Any]:
    """Validate audit trail query parameters

    Args:
        doctype: Filter by document type
        docname: Filter by document name
        limit: Maximum number of entries to return
        start: Offset for pagination

    Returns:
        Dictionary with validated parameters

    Raises:
        frappe.ValidationError: If validation fails
    """
    errors = []

    # Validate limit
    if not isinstance(limit, int):
        errors.append("Limit must be an integer")
    elif limit < 1:
        errors.append("Limit must be a positive integer")
    elif limit > 1000:
        errors.append("Limit cannot exceed 1000")

    # Validate start
    if not isinstance(start, int):
        errors.append("Start must be an integer")
    elif start < 0:
        errors.append("Start must be a non-negative integer")

    # Validate doctype if provided
    if doctype:
        if not isinstance(doctype, str):
            errors.append("DocType must be a string")
        elif not frappe.db.exists('DocType', doctype):
            errors.append(f"DocType '{doctype}' does not exist")

    # Validate docname if doctype is provided
    if docname:
        if not isinstance(docname, str):
            errors.append("DocName must be a string")
        elif not doctype:
            errors.append("DocType must be provided when DocName is specified")

    if errors:
        frappe.throw(_("Validation Error: ") + ", ".join(errors), title=_('Invalid Parameters'))

    return {
        'doctype': doctype,
        'docname': docname,
        'limit': min(limit, 1000),
        'start': start
    }


def validate_check_type(check_type: str) -> str:
    """Validate integrity check type

    Args:
        check_type: The type of check to run

    Returns:
        The validated check type

    Raises:
        frappe.ValidationError: If check type is invalid
    """
    valid_types = ['full', 'data', 'config']

    if not isinstance(check_type, str):
        frappe.throw(_("Check type must be a string"))

    if check_type not in valid_types:
        frappe.throw(_(f"Invalid check type. Must be one of: {', '.join(valid_types)}"))

    return check_type


def validate_notification_data(notification_type: str,
                               recipients: List[str],
                               data: Dict[str, Any]) -> None:
    """Validate notification parameters

    Args:
        notification_type: Type of notification (email, system, sms)
        recipients: List of recipient addresses
        data: Notification data dictionary

    Raises:
        frappe.ValidationError: If validation fails
    """
    errors = []

    # Validate notification type
    valid_types = ['email', 'system', 'sms']
    if notification_type not in valid_types:
        errors.append(f"Invalid notification type: {notification_type}. Must be one of: {', '.join(valid_types)}")

    # Validate recipients
    if not isinstance(recipients, list):
        errors.append("Recipients must be a list")
    elif not recipients:
        errors.append("Recipients list cannot be empty")
    else:
        for recipient in recipients:
            if not isinstance(recipient, str):
                errors.append(f"Invalid recipient: {recipient} (must be string)")
            elif notification_type == 'email':
                if '@' not in recipient:
                    errors.append(f"Invalid email address: {recipient}")

    # Validate data structure
    if not isinstance(data, dict):
        errors.append("Data must be a dictionary")

    if errors:
        frappe.throw(_("Notification Validation Error: ") + ", ".join(errors))


def sanitize_input_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input to prevent injection attacks

    Args:
        value: The string to sanitize
        max_length: Maximum length for the string

    Returns:
        Sanitized string

    Raises:
        frappe.ValidationError: If input contains dangerous patterns
    """
    if not isinstance(value, str):
        frappe.throw(_("Expected string value"))

    # Remove potential SQL injection patterns
    dangerous_patterns = ['--', ';', 'DROP', 'DELETE', 'TRUNCATE', 'UNION', 'SELECT',
                         'INSERT', 'UPDATE', 'EXEC', 'EXECUTE', 'xp_', 'sp_']
    value_upper = value.upper()

    for pattern in dangerous_patterns:
        if pattern in value_upper:
            frappe.throw(_("Input contains potentially dangerous patterns"))

    # Check for XSS patterns
    xss_patterns = ['<script', 'javascript:', 'onerror=', 'onload=', 'onclick=']
    value_lower = value.lower()

    for pattern in xss_patterns:
        if pattern in value_lower:
            frappe.throw(_("Input contains potentially dangerous script patterns"))

    # Truncate to max length
    return value[:max_length]


def validate_program_data(program_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate audit program data

    Args:
        program_data: Program data dictionary

    Returns:
        Validated program data

    Raises:
        frappe.ValidationError: If validation fails
    """
    if not isinstance(program_data, dict):
        frappe.throw(_("Program data must be a dictionary"))

    required_fields = ['name', 'audit_areas', 'start_date']
    missing_fields = [f for f in required_fields if f not in program_data]

    if missing_fields:
        frappe.throw(_(f"Missing required fields: {', '.join(missing_fields)}"))

    # Validate audit_areas is a list
    if not isinstance(program_data.get('audit_areas'), list):
        frappe.throw(_("audit_areas must be a list"))

    # Validate start_date format
    from datetime import datetime
    try:
        datetime.strptime(program_data.get('start_date'), '%Y-%m-%d')
    except (ValueError, TypeError):
        frappe.throw(_("start_date must be in YYYY-MM-DD format"))

    return program_data


def validate_module_name(module_name: str, valid_modules: List[str]) -> str:
    """Validate module name against list of valid modules

    Args:
        module_name: The module name to validate
        valid_modules: List of valid module names

    Returns:
        The validated module name

    Raises:
        frappe.ValidationError: If module is invalid
    """
    if module_name and module_name not in valid_modules:
        frappe.throw(_(f"Invalid module: {module_name}. Must be one of: {', '.join(valid_modules)}"))

    return module_name


def validate_date_range(start_date: str, end_date: str = None) -> tuple:
    """Validate date range parameters

    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: Optional end date string (YYYY-MM-DD)

    Returns:
        Tuple of validated (start_date, end_date)

    Raises:
        frappe.ValidationError: If date format is invalid or range is invalid
    """
    from datetime import datetime

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        frappe.throw(_("start_date must be in YYYY-MM-DD format"))

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            frappe.throw(_("end_date must be in YYYY-MM-DD format"))

        if end < start:
            frappe.throw(_("end_date must be after start_date"))

        return start, end

    return start, None


def validate_positive_integer(value: int, field_name: str = "Value",
                              max_value: int = None) -> int:
    """Validate that a value is a positive integer

    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        max_value: Optional maximum value

    Returns:
        The validated integer

    Raises:
        frappe.ValidationError: If validation fails
    """
    if not isinstance(value, int):
        frappe.throw(_(f"{field_name} must be an integer"))

    if value < 0:
        frappe.throw(_(f"{field_name} must be non-negative"))

    if max_value is not None and value > max_value:
        frappe.throw(_(f"{field_name} cannot exceed {max_value}"))

    return value


def validate_risk_level(risk_level: str) -> str:
    """Validate risk level value

    Args:
        risk_level: The risk level to validate

    Returns:
        The validated risk level

    Raises:
        frappe.ValidationError: If risk level is invalid
    """
    valid_levels = ['Low', 'Medium', 'High', 'Critical']

    if risk_level not in valid_levels:
        frappe.throw(_(f"Invalid risk level. Must be one of: {', '.join(valid_levels)}"))

    return risk_level


def validate_severity(severity: str) -> str:
    """Validate severity value

    Args:
        severity: The severity to validate

    Returns:
        The validated severity

    Raises:
        frappe.ValidationError: If severity is invalid
    """
    valid_severities = ['Low', 'Medium', 'High', 'Critical']

    if severity not in valid_severities:
        frappe.throw(_(f"Invalid severity. Must be one of: {', '.join(valid_severities)}"))

    return severity


def validate_email(email: str) -> str:
    """Validate email address format

    Args:
        email: The email address to validate

    Returns:
        The validated email

    Raises:
        frappe.ValidationError: If email format is invalid
    """
    import re

    if not isinstance(email, str):
        frappe.throw(_("Email must be a string"))

    # Basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        frappe.throw(_(f"Invalid email address: {email}"))

    return email


def validate_user_list(users: List[str]) -> List[str]:
    """Validate that all users in list exist

    Args:
        users: List of user IDs

    Returns:
        The validated list of users

    Raises:
        frappe.ValidationError: If any user doesn't exist
    """
    if not isinstance(users, list):
        frappe.throw(_("Users must be a list"))

    invalid_users = []
    for user in users:
        if not frappe.db.exists('User', user):
            invalid_users.append(user)

    if invalid_users:
        frappe.throw(_(f"Invalid users: {', '.join(invalid_users)}"))

    return users


def validate_doctype_exists(doctype: str) -> str:
    """Validate that a DocType exists

    Args:
        doctype: The DocType to validate

    Returns:
        The validated DocType name

    Raises:
        frappe.ValidationError: If DocType doesn't exist
    """
    if not frappe.db.exists('DocType', doctype):
        frappe.throw(_(f"DocType '{doctype}' does not exist"))

    return doctype


def validate_period_days(days: int) -> int:
    """Validate period days parameter

    Args:
        days: Number of days for period

    Returns:
        Validated days value

    Raises:
        frappe.ValidationError: If days is invalid
    """
    if not isinstance(days, int):
        frappe.throw(_("Period days must be an integer"))

    if days < 1:
        frappe.throw(_("Period days must be at least 1"))

    if days > 3650:  # Max 10 years
        frappe.throw(_("Period days cannot exceed 3650 (10 years)"))

    return days

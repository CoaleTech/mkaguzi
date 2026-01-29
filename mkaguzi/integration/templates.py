# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, now_datetime, cstr, flt
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AuditTemplateManager:
    """
    Manages reusable audit templates and automated audit program generation
    """

    def __init__(self):
        self.templates = self._load_default_templates()

    def _load_default_templates(self):
        """Load default audit templates for different categories"""
        return {
            'Financial': {
                'name': 'Financial Audit Template',
                'description': 'Comprehensive financial audit covering GL, journals, and payments',
                'tests': [
                    {
                        'name': 'GL Balance Verification',
                        'type': 'balance_check',
                        'doctypes': ['GL Entry'],
                        'frequency': 'daily',
                        'risk_level': 'high'
                    },
                    {
                        'name': 'Journal Entry Review',
                        'type': 'approval_check',
                        'doctypes': ['Journal Entry'],
                        'frequency': 'daily',
                        'risk_level': 'high'
                    },
                    {
                        'name': 'Payment Reconciliation',
                        'type': 'reconciliation',
                        'doctypes': ['Payment Entry', 'Bank Transaction'],
                        'frequency': 'daily',
                        'risk_level': 'medium'
                    },
                    {
                        'name': 'Duplicate Transaction Detection',
                        'type': 'duplicate_check',
                        'doctypes': ['Journal Entry', 'Payment Entry'],
                        'frequency': 'weekly',
                        'risk_level': 'medium'
                    }
                ]
            },
            'Payroll': {
                'name': 'Payroll Audit Template',
                'description': 'Payroll compliance and accuracy verification',
                'tests': [
                    {
                        'name': 'Salary Calculation Verification',
                        'type': 'calculation_check',
                        'doctypes': ['Salary Slip'],
                        'frequency': 'monthly',
                        'risk_level': 'high'
                    },
                    {
                        'name': 'Tax Deduction Validation',
                        'type': 'compliance_check',
                        'doctypes': ['Salary Slip'],
                        'frequency': 'monthly',
                        'risk_level': 'high'
                    },
                    {
                        'name': 'Overtime Calculation Review',
                        'type': 'calculation_check',
                        'doctypes': ['Salary Slip'],
                        'frequency': 'monthly',
                        'risk_level': 'medium'
                    }
                ]
            },
            'HR': {
                'name': 'HR Audit Template',
                'description': 'Human resources compliance and data integrity',
                'tests': [
                    {
                        'name': 'Employee Data Completeness',
                        'type': 'data_integrity',
                        'doctypes': ['Employee'],
                        'frequency': 'quarterly',
                        'risk_level': 'medium'
                    },
                    {
                        'name': 'Attendance Verification',
                        'type': 'accuracy_check',
                        'doctypes': ['Attendance'],
                        'frequency': 'monthly',
                        'risk_level': 'medium'
                    },
                    {
                        'name': 'Leave Balance Validation',
                        'type': 'calculation_check',
                        'doctypes': ['Leave Application'],
                        'frequency': 'monthly',
                        'risk_level': 'low'
                    }
                ]
            },
            'Inventory': {
                'name': 'Inventory Audit Template',
                'description': 'Stock accuracy and valuation verification',
                'tests': [
                    {
                        'name': 'Stock Variance Analysis',
                        'type': 'variance_check',
                        'doctypes': ['Stock Entry', 'Stock Reconciliation'],
                        'frequency': 'weekly',
                        'risk_level': 'high'
                    },
                    {
                        'name': 'Negative Stock Detection',
                        'type': 'threshold_check',
                        'doctypes': ['Item'],
                        'frequency': 'daily',
                        'risk_level': 'high'
                    },
                    {
                        'name': 'ABC Analysis',
                        'type': 'classification_check',
                        'doctypes': ['Item'],
                        'frequency': 'monthly',
                        'risk_level': 'medium'
                    }
                ]
            },
            'Procurement': {
                'name': 'Procurement Audit Template',
                'description': 'Purchase process compliance and efficiency',
                'tests': [
                    {
                        'name': 'Purchase Order Approval',
                        'type': 'approval_check',
                        'doctypes': ['Purchase Order'],
                        'frequency': 'weekly',
                        'risk_level': 'medium'
                    },
                    {
                        'name': 'Vendor Price Analysis',
                        'type': 'comparison_check',
                        'doctypes': ['Purchase Order', 'Supplier Quotation'],
                        'frequency': 'monthly',
                        'risk_level': 'medium'
                    },
                    {
                        'name': 'Three-Way Match Verification',
                        'type': 'matching_check',
                        'doctypes': ['Purchase Order', 'Purchase Receipt', 'Purchase Invoice'],
                        'frequency': 'weekly',
                        'risk_level': 'high'
                    }
                ]
            },
            'Access': {
                'name': 'Access Control Audit Template',
                'description': 'User access and security verification',
                'tests': [
                    {
                        'name': 'User Access Review',
                        'type': 'access_check',
                        'doctypes': ['User', 'User Permission'],
                        'frequency': 'quarterly',
                        'risk_level': 'high'
                    },
                    {
                        'name': 'Role Permission Analysis',
                        'type': 'permission_check',
                        'doctypes': ['Role', 'Role Permission'],
                        'frequency': 'quarterly',
                        'risk_level': 'high'
                    },
                    {
                        'name': 'Segregation of Duties',
                        'type': 'segregation_check',
                        'doctypes': ['User', 'Role'],
                        'frequency': 'quarterly',
                        'risk_level': 'high'
                    }
                ]
            }
        }

    def get_template_for_category(self, category):
        """
        Get audit template for a specific category

        Args:
            category: Audit category (Financial, Payroll, etc.)

        Returns:
            dict: Template configuration
        """
        return self.templates.get(category, {})

    def create_audit_program_from_template(self, category, engagement_name=None):
        """
        Create an audit program from a template

        Args:
            category: Audit category
            engagement_name: Optional engagement reference

        Returns:
            dict: Created audit program details
        """
        try:
            template = self.get_template_for_category(category)
            if not template:
                return {"success": False, "error": f"No template found for category {category}"}

            # Create audit program
            program = frappe.get_doc({
                'doctype': 'Audit Program',
                'program_name': f"{template['name']} - {now().strftime('%Y-%m-%d')}",
                'audit_category': category,
                'description': template['description'],
                'template_used': template['name'],
                'engagement_reference': engagement_name,
                'status': 'Draft'
            })

            # Add test procedures from template
            for test in template['tests']:
                program.append('test_procedures', {
                    'test_name': test['name'],
                    'test_type': test['type'],
                    'doctypes_covered': json.dumps(test['doctypes']),
                    'frequency': test['frequency'],
                    'risk_level': test['risk_level'],
                    'sample_size': self._calculate_sample_size(test),
                    'status': 'Not Started'
                })

            program.insert(ignore_permissions=True)

            return {
                "success": True,
                "program_name": program.name,
                "tests_created": len(template['tests'])
            }

        except Exception as e:
            logger.error(f"Failed to create audit program from template: {str(e)}")
            return {"success": False, "error": str(e)}

    def _calculate_sample_size(self, test):
        """
        Calculate appropriate sample size based on test configuration

        Args:
            test: Test configuration

        Returns:
            int: Recommended sample size
        """
        base_sizes = {
            'daily': 10,
            'weekly': 25,
            'monthly': 50,
            'quarterly': 100
        }

        risk_multipliers = {
            'low': 0.5,
            'medium': 1.0,
            'high': 1.5
        }

        base_size = base_sizes.get(test.get('frequency', 'monthly'), 50)
        risk_multiplier = risk_multipliers.get(test.get('risk_level', 'medium'), 1.0)

        return int(base_size * risk_multiplier)

    def customize_template(self, category, customizations):
        """
        Create a customized version of a template

        Args:
            category: Base template category
            customizations: Dictionary of customizations

        Returns:
            dict: Customized template
        """
        try:
            template = self.templates.get(category, {}).copy()

            if not template:
                return {"success": False, "error": f"No template found for category {category}"}

            # Apply customizations
            if 'name' in customizations:
                template['name'] = customizations['name']

            if 'description' in customizations:
                template['description'] = customizations['description']

            if 'tests' in customizations:
                # Merge custom tests with existing ones
                existing_tests = {test['name']: test for test in template['tests']}
                for custom_test in customizations['tests']:
                    test_name = custom_test.get('name')
                    if test_name in existing_tests:
                        # Update existing test
                        existing_tests[test_name].update(custom_test)
                    else:
                        # Add new test
                        template['tests'].append(custom_test)

            return {"success": True, "template": template}

        except Exception as e:
            logger.error(f"Failed to customize template: {str(e)}")
            return {"success": False, "error": str(e)}

    def save_custom_template(self, template_data):
        """
        Save a custom template for future use

        Args:
            template_data: Template configuration

        Returns:
            dict: Save result
        """
        try:
            # Create Audit Test Template doctype entry
            template_doc = frappe.get_doc({
                'doctype': 'Audit Test Template',
                'template_name': template_data['name'],
                'audit_category': template_data.get('category', 'Custom'),
                'description': template_data.get('description', ''),
                'tests': json.dumps(template_data['tests']),
                'is_custom': 1,
                'created_by': frappe.session.user
            })

            template_doc.insert(ignore_permissions=True)

            return {"success": True, "template_name": template_doc.name}

        except Exception as e:
            logger.error(f"Failed to save custom template: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_available_templates(self):
        """
        Get all available audit templates

        Returns:
            list: Available templates
        """
        templates = []

        # Add default templates
        for category, template in self.templates.items():
            templates.append({
                'name': template['name'],
                'category': category,
                'description': template['description'],
                'test_count': len(template['tests']),
                'type': 'default'
            })

        # Add custom templates from database
        try:
            custom_templates = frappe.get_all('Audit Test Template',
                fields=['template_name', 'audit_category', 'description', 'tests'],
                filters={'is_custom': 1}
            )

            for template in custom_templates:
                templates.append({
                    'name': template.template_name,
                    'category': template.audit_category,
                    'description': template.description,
                    'test_count': len(json.loads(template.tests or '[]')),
                    'type': 'custom'
                })

        except Exception as e:
            logger.error(f"Failed to load custom templates: {str(e)}")

        return templates

    def validate_template(self, template_data):
        """
        Validate template configuration

        Args:
            template_data: Template to validate

        Returns:
            dict: Validation result
        """
        errors = []

        # Check required fields
        if not template_data.get('name'):
            errors.append("Template name is required")

        if not template_data.get('category'):
            errors.append("Template category is required")

        # Validate tests
        tests = template_data.get('tests', [])
        if not tests:
            errors.append("At least one test is required")

        for i, test in enumerate(tests):
            if not test.get('name'):
                errors.append(f"Test {i+1}: Name is required")

            if not test.get('type'):
                errors.append(f"Test {i+1}: Type is required")

            if not test.get('doctypes'):
                errors.append(f"Test {i+1}: Doctypes are required")

            valid_frequencies = ['daily', 'weekly', 'monthly', 'quarterly']
            if test.get('frequency') not in valid_frequencies:
                errors.append(f"Test {i+1}: Invalid frequency")

            valid_risks = ['low', 'medium', 'high']
            if test.get('risk_level') not in valid_risks:
                errors.append(f"Test {i+1}: Invalid risk level")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

# Global template manager instance
template_manager = AuditTemplateManager()

@frappe.whitelist()
def get_audit_templates():
    """API endpoint to get available audit templates"""
    return template_manager.get_available_templates()

@frappe.whitelist()
def create_program_from_template(category, engagement_name=None):
    """API endpoint to create audit program from template"""
    if not frappe.has_permission('Audit Program', 'create'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    result = template_manager.create_audit_program_from_template(category, engagement_name)
    return result

@frappe.whitelist()
def customize_audit_template(category, customizations):
    """API endpoint to customize an audit template"""
    customizations = json.loads(customizations) if isinstance(customizations, str) else customizations
    result = template_manager.customize_template(category, customizations)
    return result

@frappe.whitelist()
def save_custom_template(template_data):
    """API endpoint to save a custom template"""
    if not frappe.has_permission('Audit Test Template', 'create'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    template_data = json.loads(template_data) if isinstance(template_data, str) else template_data
    result = template_manager.save_custom_template(template_data)
    return result

@frappe.whitelist()
def validate_template_config(template_data):
    """API endpoint to validate template configuration"""
    template_data = json.loads(template_data) if isinstance(template_data, str) else template_data
    result = template_manager.validate_template(template_data)
    return result
import unittest
import json
from unittest.mock import patch, MagicMock

import frappe
from frappe.tests.utils import FrappeTestCase

from mkaguzi.api.templates import (
    get_templates, get_template, create_template, update_template,
    delete_template, duplicate_template, render_template,
    get_template_categories, get_template_stats, validate_template_content
)


class TestReportTemplateBuilder(FrappeTestCase):
    def setUp(self):
        # Create test data with unique names
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        self.test_template_data = {
            "template_name": f"Test Report Template {unique_id}",
            "template_type": "Report",
            "category": "Audit Report",
            "description": "Test template for report builder",
            "template_content": "# Test Report\n\nThis is a test report template.",
            "template_config": {
                "builder": {
                    "components": [
                        {
                            "id": "comp_1",
                            "type": "heading",
                            "properties": {"text": "Test Report", "level": 1}
                        }
                    ],
                    "settings": {
                        "name": f"Test Report Template {unique_id}",
                        "category": "Audit Report",
                        "pageSize": "A4",
                        "orientation": "portrait"
                    }
                }
            },
            "template_engine": "Jinja2",
            "is_active": True,
            "is_default": False
        }

    def tearDown(self):
        # Clean up test data - delete all templates created during this test
        frappe.db.rollback()
        
        # More aggressive cleanup - delete any templates that might have been created
        try:
            # Get all templates and delete them
            templates = frappe.db.get_all("Template Registry", fields=["name"])
            for template in templates:
                try:
                    frappe.delete_doc("Template Registry", template.name, force=True, ignore_permissions=True)
                except:
                    pass
            frappe.db.commit()
        except:
            pass

    def test_create_template(self):
        """Test creating a new template"""
        result = create_template(self.test_template_data)

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["template_name"], self.test_template_data["template_name"])

        # Verify template was created
        template = frappe.get_doc("Template Registry", result["data"]["name"])
        self.assertEqual(template.template_name, self.test_template_data["template_name"])
        self.assertEqual(template.template_type, "Report")
        self.assertTrue(template.is_active)

    def test_create_template_duplicate_name(self):
        """Test creating template with duplicate name"""
        # Create first template
        create_template(self.test_template_data)

        # Try to create duplicate
        with self.assertRaises(frappe.ValidationError):
            create_template(self.test_template_data)

    def test_get_template(self):
        """Test getting a specific template"""
        # Create template first
        create_result = create_template(self.test_template_data)
        template_id = create_result["data"]["name"]

        # Get template
        result = get_template(template_id)

        self.assertEqual(result["template_name"], self.test_template_data["template_name"])
        self.assertEqual(result["template_type"], "Report")
        self.assertIsInstance(result["template_config"], dict)

    def test_update_template(self):
        """Test updating an existing template"""
        # Create template first
        create_result = create_template(self.test_template_data)
        template_id = create_result["data"]["name"]

        # Update template
        update_data = {
            "template_id": template_id,
            "template_name": "Updated Test Report Template",
            "description": "Updated description",
            "is_active": False
        }

        result = update_template(update_data)

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["template_name"], "Updated Test Report Template")

        # Verify update
        template = frappe.get_doc("Template Registry", template_id)
        self.assertEqual(template.template_name, "Updated Test Report Template")
        self.assertEqual(template.description, "Updated description")
        self.assertFalse(template.is_active)

    def test_delete_template(self):
        """Test deleting a template"""
        # Create template first
        create_result = create_template(self.test_template_data)
        template_id = create_result["data"]["name"]

        # Delete template
        result = delete_template(template_id)

        self.assertTrue(result["success"])

        # Verify deletion
        self.assertFalse(frappe.db.exists("Template Registry", template_id))

    def test_duplicate_template(self):
        """Test duplicating a template"""
        # Create template first
        create_result = create_template(self.test_template_data)
        template_id = create_result["data"]["name"]

        # Duplicate template
        result = duplicate_template(template_id, "Duplicated Template")

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["template_name"], "Duplicated Template")

        # Verify duplicate exists
        duplicate = frappe.get_doc("Template Registry", result["data"]["name"])
        self.assertEqual(duplicate.template_name, "Duplicated Template")
        self.assertEqual(duplicate.template_type, "Report")

    def test_render_template(self):
        """Test rendering a template"""
        # Create template with variables
        template_data = self.test_template_data.copy()
        template_data["template_content"] = "Hello {{ name }}! Total: {{ total | default(0) }}"

        create_result = create_template(template_data)
        template_id = create_result["data"]["name"]

        # Render template
        context = {"name": "World", "total": 100}
        result = render_template(template_id, context)

        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "Hello World! Total: 100")

        # Verify usage count increased
        template = frappe.get_doc("Template Registry", template_id)
        self.assertEqual(template.usage_count, 1)

    def test_get_templates_with_filters(self):
        """Test getting templates with filters"""
        # Create multiple templates
        create_template(self.test_template_data)

        audit_template = self.test_template_data.copy()
        audit_template["template_name"] = "Audit Template"
        audit_template["category"] = "Audit Report"
        create_template(audit_template)

        compliance_template = self.test_template_data.copy()
        compliance_template["template_name"] = "Compliance Template"
        compliance_template["category"] = "Compliance"
        create_template(compliance_template)

        # Test category filter
        results = get_templates({"category": "Audit Report"})
        self.assertEqual(len(results), 2)

        # Test search filter
        results = get_templates({"search": "Compliance"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["template_name"], "Compliance Template")

    def test_validate_template_content(self):
        """Test template content validation"""
        # Valid Jinja2 template
        result = validate_template_content("Hello {{ name }}!")
        self.assertTrue(result["valid"])

        # Invalid Jinja2 template
        result = validate_template_content("Hello {{ name")
        self.assertFalse(result["valid"])
        self.assertIn("Template syntax error", result["message"])

    def test_get_template_categories(self):
        """Test getting template categories"""
        # Create templates with different categories
        create_template(self.test_template_data)

        compliance_template = self.test_template_data.copy()
        compliance_template["template_name"] = "Compliance Template"
        compliance_template["category"] = "Compliance"
        create_template(compliance_template)

        categories = get_template_categories()
        self.assertIn("Audit Report", categories)
        self.assertIn("Compliance", categories)

    def test_get_template_stats(self):
        """Test getting template statistics"""
        # Create some templates
        create_template(self.test_template_data)

        inactive_template = self.test_template_data.copy()
        inactive_template["template_name"] = "Inactive Template"
        inactive_template["is_active"] = False
        create_template(inactive_template)

        stats = get_template_stats()
        self.assertEqual(stats["total_templates"], 2)
        self.assertEqual(stats["active_templates"], 1)

    def test_default_template_logic(self):
        """Test default template logic (only one default per type)"""
        # Create first default template
        template1 = self.test_template_data.copy()
        template1["is_default"] = True
        result1 = create_template(template1)

        # Create second default template of same type
        template2 = self.test_template_data.copy()
        template2["template_name"] = "Second Default Template"
        template2["is_default"] = True
        result2 = create_template(template2)

        # Check that only second template is default
        template1_doc = frappe.get_doc("Template Registry", result1["data"]["name"])
        template2_doc = frappe.get_doc("Template Registry", result2["data"]["name"])

        self.assertFalse(template1_doc.is_default)
        self.assertTrue(template2_doc.is_default)


if __name__ == '__main__':
    unittest.main()
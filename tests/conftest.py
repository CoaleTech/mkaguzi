# -*- coding: utf-8 -*-
"""
Pytest configuration for Mkaguzi tests
"""

import pytest
import frappe
from frappe.tests.utils import FrappeTestCase


@pytest.fixture(scope="session", autouse=True)
def frappe_app():
    """Initialize Frappe app for testing"""
    frappe.init(site="/Users/mac/ERPNext/internalaudit/sites/ukaguzi")
    frappe.connect()
    yield
    frappe.destroy()


@pytest.fixture(scope="function")
def db_transaction():
    """Provide database transaction for each test"""
    frappe.db.begin()
    yield
    frappe.db.rollback()


@pytest.fixture
def test_user():
    """Create a test user for testing"""
    if not frappe.db.exists("User", "test@example.com"):
        user = frappe.new_doc("User")
        user.email = "test@example.com"
        user.first_name = "Test"
        user.last_name = "User"
        user.insert(ignore_permissions=True)
    return frappe.get_doc("User", "test@example.com")


@pytest.fixture
def audit_engagement():
    """Create a test audit engagement"""
    engagement = frappe.new_doc("Audit Engagement")
    engagement.engagement_title = "Test Audit Engagement"
    engagement.engagement_type = "Financial Audit"
    engagement.status = "planned"
    engagement.planned_start_date = "2025-01-01"
    engagement.planned_end_date = "2025-01-31"
    engagement.insert(ignore_permissions=True)
    return engagement


@pytest.fixture
def audit_test_library():
    """Create a test audit test library entry"""
    test = frappe.new_doc("Audit Test Library")
    test.test_name = "Test Duplicate Detection"
    test.test_category = "Duplicate Detection"
    test.description = "Test for detecting duplicates"
    test.test_logic_type = "SQL Query"
    test.sql_query = "SELECT * FROM tabUser WHERE 1=1"
    test.insert(ignore_permissions=True)
    return test
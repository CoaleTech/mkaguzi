#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic validation script for Mkaguzi Integration
Tests core functions without Frappe context
"""

import sys
import os

# Add the app path to sys.path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
sys.path.insert(0, app_dir)

def test_module_mapping():
    """Test module mapping function"""
    print("Testing module mapping...")

    # Import the function directly
    try:
        from mkaguzi.integration.sync import get_module_for_doctype

        test_cases = [
            ('GL Entry', 'Financial'),
            ('Employee', 'HR'),
            ('Stock Entry', 'Inventory'),
            ('User', 'Access Control'),
            ('Sales Invoice', 'Financial'),
            ('Unknown DocType', 'General')
        ]

        passed = 0
        for doctype, expected in test_cases:
            result = get_module_for_doctype(doctype)
            if result == expected:
                print(f"  ✅ {doctype} -> {result}")
                passed += 1
            else:
                print(f"  ❌ {doctype} -> {result} (expected {expected})")

        return passed == len(test_cases)

    except Exception as e:
        print(f"  ❌ Error testing module mapping: {e}")
        return False


def test_risk_assessment():
    """Test risk assessment function"""
    print("Testing risk assessment...")

    try:
        from mkaguzi.integration.sync import assess_risk_level

        class MockDoc:
            def __init__(self, doctype):
                self.doctype = doctype

        test_cases = [
            ('GL Entry', 'HIGH'),
            ('User', 'HIGH'),
            ('Employee', 'MEDIUM'),
            ('Item', 'LOW')
        ]

        passed = 0
        for doctype, expected in test_cases:
            doc = MockDoc(doctype)
            result = assess_risk_level(doc)
            if result == expected:
                print(f"  ✅ {doctype} -> {result}")
                passed += 1
            else:
                print(f"  ❌ {doctype} -> {result} (expected {expected})")

        return passed == len(test_cases)

    except Exception as e:
        print(f"  ❌ Error testing risk assessment: {e}")
        return False


def test_controller_import():
    """Test controller imports"""
    print("Testing controller imports...")

    try:
        from mkaguzi.controllers.integration_controllers import (
            financial_controller, hr_controller, inventory_controller, access_controller
        )

        controllers = [financial_controller, hr_controller, inventory_controller, access_controller]
        passed = 0

        for controller in controllers:
            if hasattr(controller, 'sync_financial_transaction') or \
               hasattr(controller, 'sync_hr_transaction') or \
               hasattr(controller, 'sync_inventory_transaction') or \
               hasattr(controller, 'sync_access_transaction'):
                print(f"  ✅ Controller {controller.__class__.__name__} imported successfully")
                passed += 1
            else:
                print(f"  ❌ Controller {controller.__class__.__name__} missing methods")

        return passed == len(controllers)

    except Exception as e:
        print(f"  ❌ Error testing controller imports: {e}")
        return False


def test_doctype_import():
    """Test doctype class import"""
    print("Testing doctype class import...")

    try:
        from mkaguzi.integration.doctype.audit_trail_entry.audit_trail_entry import AuditTrailEntry

        # Check if class has expected methods
        expected_methods = ['validate', 'on_update', 'get_changes_summary', 'get_related_findings']
        passed = 0

        for method in expected_methods:
            if hasattr(AuditTrailEntry, method):
                print(f"  ✅ Method {method} found")
                passed += 1
            else:
                print(f"  ❌ Method {method} missing")

        return passed == len(expected_methods)

    except Exception as e:
        print(f"  ❌ Error testing doctype import: {e}")
        return False


def main():
    """Run all validation tests"""
    print("🔍 Mkaguzi Integration Basic Validation")
    print("=" * 45)

    tests = [
        test_module_mapping,
        test_risk_assessment,
        test_controller_import,
        test_doctype_import
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()

    print("=" * 45)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All basic validations passed!")
        print("✅ Integration synchronization framework is ready")
        return True
    else:
        print("⚠️  Some validations failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test runner for Mkaguzi audit tests
"""

import sys
import os

# Add the apps directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def run_simple_test():
    """Run a simple test without full Frappe initialization"""
    print("Running simple audit test validation...")

    # Test basic imports
    try:
        import frappe
        print("✓ Frappe import successful")
    except ImportError as e:
        print(f"✗ Frappe import failed: {e}")
        return False

    # Test basic doctypes exist (without full initialization)
    try:
        # Check if our test files can be imported
        sys.path.insert(0, os.path.dirname(__file__))

        # Test import of test modules
        import test_audit_test_library
        print("✓ Test audit test library module imported")

        import test_test_execution
        print("✓ Test execution module imported")

        import test_test_parameters
        print("✓ Test parameters module imported")

        import test_test_results
        print("✓ Test results module imported")

        import test_test_thresholds
        print("✓ Test thresholds module imported")

        import test_integration
        print("✓ Integration test module imported")

        print("\n✓ All test modules imported successfully!")
        print("✓ Test structure validation complete!")
        return True

    except ImportError as e:
        print(f"✗ Test module import failed: {e}")
        return False

if __name__ == "__main__":
    success = run_simple_test()
    sys.exit(0 if success else 1)
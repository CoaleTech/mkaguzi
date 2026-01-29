#!/usr/bin/env python3
"""
Test runner for Mkaguzi Internal Audit Management System
Comprehensive test execution and reporting
"""

import sys
import os
import time
import unittest
import coverage
import argparse
from pathlib import Path
from datetime import datetime
from mkaguzi.tests.test_config import (
    setup_test_environment,
    teardown_test_environment,
    load_ci_config,
    test_config
)


class TestRunner:
    """Comprehensive test runner for the audit system"""

    def __init__(self, args=None):
        self.args = args or self._parse_args()
        self.start_time = None
        self.end_time = None
        self.results = {}
        self.coverage = None

        # Setup test environment
        setup_test_environment()

        if self.args.ci:
            load_ci_config()

    def _parse_args(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description='Mkaguzi Audit System Test Runner')

        parser.add_argument('--ci', action='store_true',
                          help='Run in CI mode with CI-specific configuration')
        parser.add_argument('--coverage', action='store_true',
                          help='Generate coverage report')
        parser.add_argument('--verbose', '-v', action='store_true',
                          help='Verbose output')
        parser.add_argument('--pattern', default='test_*.py',
                          help='Test file pattern (default: test_*.py)')
        parser.add_argument('--module', help='Run specific test module')
        parser.add_argument('--report-dir', default='test_reports',
                          help='Directory for test reports')
        parser.add_argument('--fail-fast', action='store_true',
                          help='Stop on first failure')
        parser.add_argument('--performance', action='store_true',
                          help='Include performance tests')

        return parser.parse_args()

    def discover_tests(self):
        """Discover all test files"""
        test_dir = Path(__file__).parent
        test_files = []

        if self.args.module:
            # Run specific test module
            module_file = test_dir / f'{self.args.module}.py'
            if module_file.exists():
                test_files.append(str(module_file))
            else:
                print(f"Test module not found: {module_file}")
                return []
        else:
            # Discover all test files
            for pattern in self.args.pattern.split(','):
                test_files.extend(test_dir.glob(pattern.strip()))

        return [str(f) for f in test_files if f.is_file()]

    def setup_coverage(self):
        """Setup coverage measurement"""
        if self.args.coverage or test_config.get('coverage_report', True):
            self.coverage = coverage.Coverage(
                source=['mkaguzi'],
                omit=['*/tests/*', '*/test_*', '*/__pycache__/*']
            )
            self.coverage.start()

    def teardown_coverage(self):
        """Generate coverage report"""
        if self.coverage:
            self.coverage.stop()
            self.coverage.save()

            # Generate reports
            report_dir = Path(self.args.report_dir)
            report_dir.mkdir(exist_ok=True)

            # HTML report
            html_report = report_dir / 'coverage_html'
            self.coverage.html_report(directory=str(html_report))

            # XML report for CI
            xml_report = report_dir / 'coverage.xml'
            self.coverage.xml_report(outfile=str(xml_report))

            # Console report
            print("\n=== COVERAGE REPORT ===")
            self.coverage.report()

    def run_tests(self):
        """Run all discovered tests"""
        self.start_time = time.time()

        test_files = self.discover_tests()
        if not test_files:
            print("No test files found!")
            return False

        print(f"Running tests from {len(test_files)} files...")

        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        # Load tests from each file
        for test_file in test_files:
            try:
                module_name = Path(test_file).stem
                module = __import__(f'mkaguzi.tests.{module_name}', fromlist=[module_name])

                # Load test classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, unittest.TestCase):
                        if self._should_run_test_class(attr):
                            suite.addTests(loader.loadTestsFromTestCase(attr))

            except Exception as e:
                print(f"Error loading tests from {test_file}: {e}")
                continue

        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=2 if self.args.verbose else 1,
            failfast=self.args.fail_fast
        )

        self.results = runner.run(suite)
        self.end_time = time.time()

        return self.results.wasSuccessful()

    def _should_run_test_class(self, test_class):
        """Determine if test class should be run based on configuration"""
        class_name = test_class.__name__

        # Skip performance tests unless explicitly requested
        if 'Performance' in class_name and not self.args.performance:
            if not test_config.get('enable_performance_tests', True):
                return False

        return True

    def generate_report(self):
        """Generate comprehensive test report"""
        if not self.results:
            return

        report_dir = Path(self.args.report_dir)
        report_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'test_report_{timestamp}.json'

        report_data = {
            'timestamp': timestamp,
            'duration': self.end_time - self.start_time,
            'tests_run': self.results.testsRun,
            'failures': len(self.results.failures),
            'errors': len(self.results.errors),
            'skipped': len(getattr(self.results, 'skipped', [])),
            'success': self.results.wasSuccessful(),
            'configuration': {
                'ci_mode': self.args.ci,
                'coverage_enabled': bool(self.coverage),
                'performance_tests': self.args.performance,
                'fail_fast': self.args.fail_fast
            },
            'failures_detail': [
                {
                    'test': str(failure[0]),
                    'error': str(failure[1])
                } for failure in self.results.failures
            ],
            'errors_detail': [
                {
                    'test': str(error[0]),
                    'error': str(error[1])
                } for error in self.results.errors
            ]
        }

        # Save JSON report
        with open(report_file, 'w') as f:
            import json
            json.dump(report_data, f, indent=2, default=str)

        # Save text summary
        summary_file = report_dir / f'test_summary_{timestamp}.txt'
        with open(summary_file, 'w') as f:
            f.write("=== MKAGUZI AUDIT SYSTEM TEST REPORT ===\n\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Duration: {report_data['duration']:.2f} seconds\n")
            f.write(f"Tests Run: {report_data['tests_run']}\n")
            f.write(f"Failures: {report_data['failures']}\n")
            f.write(f"Errors: {report_data['errors']}\n")
            f.write(f"Success: {report_data['success']}\n\n")

            if report_data['failures_detail']:
                f.write("FAILURES:\n")
                for failure in report_data['failures_detail']:
                    f.write(f"- {failure['test']}: {failure['error'][:100]}...\n")

            if report_data['errors_detail']:
                f.write("\nERRORS:\n")
                for error in report_data['errors_detail']:
                    f.write(f"- {error['test']}: {error['error'][:100]}...\n")

        print(f"\nTest reports saved to: {report_dir}")
        print(f"- JSON Report: {report_file}")
        print(f"- Summary: {summary_file}")

        if self.coverage:
            print(f"- Coverage HTML: {report_dir}/coverage_html/index.html")
            print(f"- Coverage XML: {report_dir}/coverage.xml")

    def print_summary(self):
        """Print test execution summary"""
        if not self.results:
            return

        duration = self.end_time - self.start_time

        print(f"\n{'='*60}")
        print("PHASE 10: TESTING FRAMEWORK IMPLEMENTATION")
        print(f"{'='*60}")
        print(f"Tests Run: {self.results.testsRun}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Failures: {len(self.results.failures)}")
        print(f"Errors: {len(self.results.errors)}")

        if self.results.wasSuccessful():
            print("🎉 RESULT: ALL TESTS PASSED")
            print("Phase 10 Testing Framework: SUCCESS")
        else:
            print("❌ RESULT: TESTS FAILED")
            print("Phase 10 Testing Framework: NEEDS ATTENTION")

            if self.results.failures:
                print(f"\nFailures ({len(self.results.failures)}):")
                for i, (test, traceback) in enumerate(self.results.failures[:5], 1):
                    print(f"  {i}. {test}")

            if self.results.errors:
                print(f"\nErrors ({len(self.results.errors)}):")
                for i, (test, traceback) in enumerate(self.results.errors[:5], 1):
                    print(f"  {i}. {test}")

        print(f"{'='*60}")

    def run(self):
        """Main execution method"""
        try:
            print("Starting Mkaguzi Audit System Test Suite...")
            print(f"Test Environment: {'CI' if self.args.ci else 'Development'}")
            print(f"Coverage: {'Enabled' if self.args.coverage else 'Disabled'}")
            print(f"Performance Tests: {'Enabled' if self.args.performance else 'Disabled'}")
            print("-" * 50)

            # Setup coverage
            self.setup_coverage()

            # Run tests
            success = self.run_tests()

            # Generate reports
            self.generate_report()
            self.teardown_coverage()
            self.print_summary()

            # Cleanup
            teardown_test_environment()

            return success

        except Exception as e:
            print(f"Test execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    runner = TestRunner()
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
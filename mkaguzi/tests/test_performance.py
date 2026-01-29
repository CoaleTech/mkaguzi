#!/usr/bin/env python3
"""
Performance tests for Mkaguzi audit system
"""

import pytest
import time
import statistics
from mkaguzi.api import AuditAPI
from mkaguzi.tests.test_config import TestUtils


@pytest.mark.performance
class TestAPIPerformance:
    """Performance tests for API operations"""

    def setup_method(self):
        self.api = AuditAPI()

    def test_get_system_status_performance(self):
        """Test get_system_status response time"""
        times = []

        # Run multiple times to get average
        for _ in range(10):
            start_time = time.time()
            result = self.api.get_system_status()
            end_time = time.time()

            times.append(end_time - start_time)
            TestUtils.assert_valid_api_response(result)

        avg_time = statistics.mean(times)
        max_time = max(times)

        # Assert reasonable performance (adjust thresholds as needed)
        assert avg_time < 2.0, f"Average response time too slow: {avg_time:.3f}s"
        assert max_time < 5.0, f"Max response time too slow: {max_time:.3f}s"

        print(f"System status performance - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")

    def test_get_audit_trail_performance(self):
        """Test get_audit_trail response time"""
        times = []

        for _ in range(5):
            start_time = time.time()
            result = self.api.get_audit_trail(limit=50)
            end_time = time.time()

            times.append(end_time - start_time)
            assert 'entries' in result
            assert 'total' in result

        avg_time = statistics.mean(times)
        assert avg_time < 3.0, f"Audit trail query too slow: {avg_time:.3f}s"

        print(f"Audit trail performance - Avg: {avg_time:.3f}s")

    def test_bulk_dashboard_updates_performance(self):
        """Test bulk dashboard update performance"""
        start_time = time.time()
        result = self.api.update_dashboard_data()
        end_time = time.time()

        duration = end_time - start_time

        assert duration < 10.0, f"Bulk dashboard update too slow: {duration:.3f}s"
        assert result['overall_status'] in ['success', 'partial']

        print(f"Bulk dashboard update performance: {duration:.3f}s")


@pytest.mark.performance
class TestControllerPerformance:
    """Performance tests for controller operations"""

    def test_controller_initialization_performance(self):
        """Test controller initialization times"""
        from mkaguzi.controllers.audit_controllers import (
            AuditGLController,
            AuditDoctypeCatalogController,
            AuditIntegrityReportController
        )

        controllers = [
            AuditGLController,
            AuditDoctypeCatalogController,
            AuditIntegrityReportController
        ]

        times = []
        for controller_class in controllers:
            start_time = time.time()
            controller = controller_class()
            end_time = time.time()

            times.append(end_time - start_time)
            assert controller is not None

        avg_time = statistics.mean(times)
        assert avg_time < 0.1, f"Controller initialization too slow: {avg_time:.3f}s"

        print(f"Controller initialization performance - Avg: {avg_time:.3f}s")


@pytest.mark.performance
@pytest.mark.slow
class TestSystemLoadPerformance:
    """Performance tests under system load"""

    def setup_method(self):
        self.api = AuditAPI()

    def test_concurrent_api_calls_performance(self):
        """Test performance under concurrent API calls"""
        import threading

        results = []
        errors = []

        def make_api_call():
            try:
                start_time = time.time()
                result = self.api.get_system_status()
                end_time = time.time()

                results.append({
                    'duration': end_time - start_time,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                errors.append(str(e))
                results.append({
                    'duration': 0,
                    'success': False,
                    'error': str(e)
                })

        # Simulate concurrent calls
        threads = []
        num_threads = 5

        for _ in range(num_threads):
            thread = threading.Thread(target=make_api_call)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Analyze results
        successful_calls = [r for r in results if r['success']]
        durations = [r['duration'] for r in successful_calls]

        assert len(successful_calls) == num_threads, f"Some API calls failed: {errors}"
        assert len(durations) > 0, "No successful calls to measure"

        avg_duration = statistics.mean(durations)
        max_duration = max(durations)

        assert avg_duration < 3.0, f"Average concurrent call too slow: {avg_duration:.3f}s"
        assert max_duration < 8.0, f"Max concurrent call too slow: {max_duration:.3f}s"

        print(f"Concurrent API calls - Avg: {avg_duration:.3f}s, Max: {max_duration:.3f}s")

    def test_memory_usage_during_bulk_operations(self):
        """Test memory usage during bulk operations"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform bulk operations
        for _ in range(20):
            self.api.get_system_status()
            self.api.get_audit_trail(limit=10)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Assert reasonable memory usage (adjust threshold as needed)
        assert memory_increase < 50, f"Excessive memory usage: +{memory_increase:.1f}MB"

        print(f"Memory usage - Initial: {initial_memory:.1f}MB, Final: {final_memory:.1f}MB, Increase: {memory_increase:.1f}MB")


@pytest.mark.performance
class TestDatabasePerformance:
    """Performance tests for database operations"""

    def setup_method(self):
        self.api = AuditAPI()

    def test_audit_trail_query_performance_under_load(self):
        """Test audit trail queries under simulated load"""
        # Create multiple queries to simulate load
        query_times = []

        filters = [
            {},
            {'document_type': 'GL Entry'},
            {'operation': 'Create'},
            {'module': 'Financial'},
            {'document_type': 'GL Entry', 'operation': 'Create'}
        ]

        for filter_set in filters:
            start_time = time.time()
            result = self.api.get_audit_trail(limit=20, **filter_set)
            end_time = time.time()

            query_times.append(end_time - start_time)
            assert 'entries' in result

        avg_query_time = statistics.mean(query_times)
        assert avg_query_time < 2.0, f"Audit trail queries too slow: {avg_query_time:.3f}s"

        print(f"Audit trail query performance - Avg: {avg_query_time:.3f}s")


# Performance test utilities
def benchmark_function(func, iterations=100, *args, **kwargs):
    """Benchmark a function over multiple iterations"""
    times = []

    for _ in range(iterations):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        times.append(end_time - start_time)

    return {
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
        'iterations': iterations
    }


def assert_performance_threshold(benchmark_result, max_avg_time, max_max_time=None):
    """Assert that benchmark results meet performance thresholds"""
    assert benchmark_result['avg_time'] < max_avg_time, \
        f"Average time {benchmark_result['avg_time']:.3f}s exceeds threshold {max_avg_time}s"

    if max_max_time:
        assert benchmark_result['max_time'] < max_max_time, \
            f"Max time {benchmark_result['max_time']:.3f}s exceeds threshold {max_max_time}s"
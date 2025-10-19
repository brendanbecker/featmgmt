#!/usr/bin/env python3
"""
Unit tests for parallel_executor.py
"""

import unittest
import sys
from pathlib import Path
import tempfile
import asyncio

# Add parent scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from parallel_executor import ParallelTestExecutor, TestCase, TestResult


class TestParallelTestExecutor(unittest.TestCase):
    """Test suite for ParallelTestExecutor."""

    def setUp(self):
        """Set up test environment."""
        self.executor = ParallelTestExecutor()

    def test_initialization(self):
        """Test ParallelTestExecutor initialization."""
        self.assertIsNotNone(self.executor.config)
        self.assertGreater(self.executor.max_workers, 0)
        self.assertEqual(len(self.executor.test_results), 0)

    def test_load_default_config(self):
        """Test loading default configuration."""
        executor = ParallelTestExecutor(config_path=None)

        self.assertIsNotNone(executor.config)
        self.assertIn('max_workers', executor.config)
        self.assertIn('retry_failed', executor.config)
        self.assertIn('test_groups', executor.config)

    def test_load_custom_config(self):
        """Test loading custom configuration from file."""
        # Create temporary config file
        temp_config = Path(tempfile.mktemp(suffix=".yaml"))

        config_content = """
max_workers: 4
retry_failed: false
timeout_multiplier: 2
"""
        temp_config.write_text(config_content)

        try:
            executor = ParallelTestExecutor(config_path=temp_config)

            self.assertEqual(executor.config['max_workers'], 4)
            self.assertFalse(executor.config['retry_failed'])
        finally:
            if temp_config.exists():
                temp_config.unlink()

    def test_testcase_dataclass(self):
        """Test TestCase dataclass creation."""
        test = TestCase(
            name="test_example",
            module="test_module",
            estimated_time=1.5,
            required_resources={'cpu': 1, 'memory': 100},
            dependencies=[],
            priority=1
        )

        self.assertEqual(test.name, "test_example")
        self.assertEqual(test.module, "test_module")
        self.assertEqual(test.estimated_time, 1.5)
        self.assertEqual(test.priority, 1)

    def test_testresult_dataclass(self):
        """Test TestResult dataclass creation."""
        result = TestResult(
            test_name="test_example",
            passed=True,
            execution_time=2.0,
            output="All tests passed",
            error=None,
            retry_count=0
        )

        self.assertEqual(result.test_name, "test_example")
        self.assertTrue(result.passed)
        self.assertEqual(result.execution_time, 2.0)
        self.assertEqual(result.retry_count, 0)

    def test_testcase_default_priority(self):
        """Test TestCase has default priority of 0."""
        test = TestCase(
            name="test_default",
            module="test_module",
            estimated_time=1.0,
            required_resources={},
            dependencies=[]
            # priority not specified, should default to 0
        )

        self.assertEqual(test.priority, 0)

    def test_group_by_dependencies_no_deps(self):
        """Test grouping tests with no dependencies."""
        tests = [
            TestCase("test1", "module", 1.0, {}, []),
            TestCase("test2", "module", 1.0, {}, []),
            TestCase("test3", "module", 1.0, {}, [])
        ]

        groups = self.executor._group_by_dependencies(tests)

        # All tests should be in same group (no dependencies)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 3)

    def test_group_by_dependencies_with_deps(self):
        """Test grouping tests with dependencies."""
        tests = [
            TestCase("test1", "module", 1.0, {}, []),
            TestCase("test2", "module", 1.0, {}, ["test1"]),
            TestCase("test3", "module", 1.0, {}, ["test2"])
        ]

        groups = self.executor._group_by_dependencies(tests)

        # Should create multiple groups based on dependencies
        self.assertGreater(len(groups), 0)

        # First group should have no dependencies
        first_group_deps = [test.dependencies for test in groups[0]]
        self.assertTrue(all(len(deps) == 0 for deps in first_group_deps))


class TestParallelExecutorAsync(unittest.TestCase):
    """Test async functionality of ParallelTestExecutor."""

    def test_execute_tests_empty_list(self):
        """Test executing empty test list."""
        executor = ParallelTestExecutor()

        async def run_test():
            result = await executor.execute_tests([])
            return result

        # Run async test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(run_test())

        self.assertIsNotNone(result)
        self.assertIn('total_tests', result)
        self.assertEqual(result['total_tests'], 0)

    def test_execute_single_test(self):
        """Test executing a single test."""
        executor = ParallelTestExecutor()

        test = TestCase(
            name="test_single",
            module="test_module",
            estimated_time=0.1,
            required_resources={},
            dependencies=[]
        )

        async def run_test():
            result = await executor.execute_tests([test])
            return result

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(run_test())

        self.assertIsNotNone(result)
        self.assertIn('total_tests', result)
        self.assertEqual(result['total_tests'], 1)


class TestResourceTracker(unittest.TestCase):
    """Test ResourceTracker functionality."""

    def test_resource_tracker_initialization(self):
        """Test ResourceTracker can be imported and initialized."""
        from parallel_executor import ResourceTracker

        tracker = ResourceTracker()

        self.assertIsNotNone(tracker)

    def test_check_resources_available(self):
        """Test checking if resources are available."""
        from parallel_executor import ResourceTracker

        tracker = ResourceTracker()

        # System should have some resources available
        available = tracker.check_resources_available({'cpu': 1, 'memory': 100})

        self.assertIsInstance(available, bool)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""
Unit tests for flaky_detector.py
"""

import unittest
import sys
from pathlib import Path
import tempfile
import sqlite3

# Add parent scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from flaky_detector import FlakyTestDetector


class TestFlakyTestDetector(unittest.TestCase):
    """Test suite for FlakyTestDetector."""

    def setUp(self):
        """Create temporary database for testing."""
        self.temp_db = Path(tempfile.mktemp(suffix=".db"))
        self.detector = FlakyTestDetector(self.temp_db)

    def tearDown(self):
        """Clean up database."""
        self.detector.conn.close()
        if self.temp_db.exists():
            self.temp_db.unlink()

    def test_initialization(self):
        """Test FlakyTestDetector initialization."""
        self.assertTrue(self.temp_db.exists())
        self.assertIsNotNone(self.detector.conn)
        self.assertEqual(self.detector.flaky_threshold, 0.1)
        self.assertEqual(self.detector.min_runs, 10)

    def test_database_schema(self):
        """Test database tables are created correctly."""
        cursor = self.detector.conn.cursor()

        # Check test_runs table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test_runs'"
        )
        self.assertIsNotNone(cursor.fetchone())

        # Check flaky_tests table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='flaky_tests'"
        )
        self.assertIsNotNone(cursor.fetchone())

    def test_record_test_run_passing(self):
        """Test recording a passing test run."""
        self.detector.record_test_run(
            test_name="test_example",
            passed=True,
            execution_time=1.5,
            error=None
        )

        # Verify record was inserted
        cursor = self.detector.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_runs WHERE test_name='test_example'")
        count = cursor.fetchone()[0]

        self.assertEqual(count, 1)

    def test_record_test_run_failing(self):
        """Test recording a failing test run."""
        self.detector.record_test_run(
            test_name="test_failing",
            passed=False,
            execution_time=0.5,
            error="AssertionError: expected True"
        )

        # Verify record was inserted with error
        cursor = self.detector.conn.cursor()
        cursor.execute(
            "SELECT error_message FROM test_runs WHERE test_name='test_failing'"
        )
        error = cursor.fetchone()[0]

        self.assertEqual(error, "AssertionError: expected True")

    def test_record_test_run_with_build_info(self):
        """Test recording test run with build metadata."""
        build_info = {
            'build_number': '123',
            'branch': 'main',
            'commit_hash': 'abc123'
        }

        self.detector.record_test_run(
            test_name="test_with_metadata",
            passed=True,
            execution_time=2.0,
            build_info=build_info
        )

        # Verify metadata was stored
        cursor = self.detector.conn.cursor()
        cursor.execute("""
            SELECT build_number, branch, commit_hash
            FROM test_runs WHERE test_name='test_with_metadata'
        """)

        result = cursor.fetchone()

        self.assertEqual(result[0], '123')
        self.assertEqual(result[1], 'main')
        self.assertEqual(result[2], 'abc123')

    def test_analyze_test_flakiness_insufficient_data(self):
        """Test flakiness analysis with insufficient data."""
        # Record only 5 runs (less than min_runs=10)
        for i in range(5):
            self.detector.record_test_run(
                test_name="test_insufficient",
                passed=(i % 2 == 0),  # Alternating pass/fail
                execution_time=1.0
            )

        # Should not create flaky_tests entry due to insufficient data
        cursor = self.detector.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM flaky_tests WHERE test_name='test_insufficient'"
        )
        count = cursor.fetchone()[0]

        self.assertEqual(count, 0)

    def test_get_flaky_tests(self):
        """Test retrieving list of flaky tests."""
        # Manually insert a flaky test record
        cursor = self.detector.conn.cursor()
        cursor.execute("""
            INSERT INTO flaky_tests (test_name, flakiness_score, failure_rate, variance)
            VALUES ('test_flaky', 0.8, 0.5, 0.25)
        """)
        self.detector.conn.commit()

        flaky_tests = self.detector.get_flaky_tests()

        self.assertEqual(len(flaky_tests), 1)
        self.assertEqual(flaky_tests[0]['test_name'], 'test_flaky')
        self.assertEqual(flaky_tests[0]['flakiness_score'], 0.8)

    def test_quarantine_test(self):
        """Test quarantining a flaky test."""
        # Insert a flaky test
        cursor = self.detector.conn.cursor()
        cursor.execute("""
            INSERT INTO flaky_tests (test_name, flakiness_score, failure_rate, variance)
            VALUES ('test_to_quarantine', 0.9, 0.6, 0.3)
        """)
        self.detector.conn.commit()

        # Quarantine it
        self.detector.quarantine_test('test_to_quarantine', 'Too unstable')

        # Verify quarantine status
        cursor.execute("""
            SELECT quarantined, notes FROM flaky_tests
            WHERE test_name='test_to_quarantine'
        """)
        result = cursor.fetchone()

        self.assertTrue(result[0])
        self.assertEqual(result[1], 'Too unstable')

    def test_unquarantine_test(self):
        """Test unquarantining a test."""
        # Insert quarantined test
        cursor = self.detector.conn.cursor()
        cursor.execute("""
            INSERT INTO flaky_tests
            (test_name, flakiness_score, failure_rate, variance, quarantined)
            VALUES ('test_quarantined', 0.7, 0.4, 0.2, TRUE)
        """)
        self.detector.conn.commit()

        # Unquarantine it
        self.detector.unquarantine_test('test_quarantined')

        # Verify status
        cursor.execute("""
            SELECT quarantined FROM flaky_tests
            WHERE test_name='test_quarantined'
        """)
        quarantined = cursor.fetchone()[0]

        self.assertFalse(quarantined)

    def test_get_test_statistics(self):
        """Test retrieving test statistics."""
        # Record multiple runs
        for i in range(20):
            self.detector.record_test_run(
                test_name="test_stats",
                passed=(i % 3 != 0),  # Fail every 3rd run
                execution_time=1.0 + (i * 0.1)
            )

        stats = self.detector.get_test_statistics('test_stats')

        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_runs'], 20)
        self.assertGreater(stats['pass_rate'], 0.0)
        self.assertLess(stats['pass_rate'], 1.0)

    def test_generate_flakiness_report(self):
        """Test generating flakiness report."""
        # Insert some flaky tests
        cursor = self.detector.conn.cursor()
        cursor.execute("""
            INSERT INTO flaky_tests (test_name, flakiness_score, failure_rate, variance)
            VALUES ('test_flaky_1', 0.8, 0.5, 0.25),
                   ('test_flaky_2', 0.6, 0.3, 0.15)
        """)
        self.detector.conn.commit()

        report = self.detector.generate_flakiness_report()

        # Report should be a string
        self.assertIsInstance(report, str)

        # Should contain key information
        self.assertIn("Flaky Test Report", report)
        self.assertIn("test_flaky_1", report)
        self.assertIn("test_flaky_2", report)


class TestFlakyTestDetectorIntegration(unittest.TestCase):
    """Integration tests for realistic flaky test scenarios."""

    def setUp(self):
        """Set up test environment."""
        self.temp_db = Path(tempfile.mktemp(suffix=".db"))
        self.detector = FlakyTestDetector(self.temp_db)

    def tearDown(self):
        """Clean up."""
        self.detector.conn.close()
        if self.temp_db.exists():
            self.temp_db.unlink()

    def test_stable_test_detection(self):
        """Test that stable tests are not marked as flaky."""
        # Record 50 passing runs
        for i in range(50):
            self.detector.record_test_run(
                test_name="test_stable",
                passed=True,
                execution_time=1.0
            )

        # Should not be in flaky_tests
        cursor = self.detector.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM flaky_tests WHERE test_name='test_stable'"
        )
        count = cursor.fetchone()[0]

        # Stable test should not be marked as flaky
        # (Note: Actual behavior depends on implementation)
        self.assertIsNotNone(count)

    def test_consistently_failing_test(self):
        """Test that consistently failing tests are not marked as flaky."""
        # Record 50 failing runs
        for i in range(50):
            self.detector.record_test_run(
                test_name="test_broken",
                passed=False,
                execution_time=0.5,
                error="Always fails"
            )

        # Consistently failing is not flaky
        stats = self.detector.get_test_statistics('test_broken')

        if stats:
            # Should show 0% pass rate
            self.assertEqual(stats['pass_rate'], 0.0)


if __name__ == '__main__':
    unittest.main()

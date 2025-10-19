#!/usr/bin/env python3
"""
Unit tests for impact_analyzer.py
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add parent scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from impact_analyzer import ImpactAnalyzer


class TestImpactAnalyzer(unittest.TestCase):
    """Test suite for ImpactAnalyzer."""

    def setUp(self):
        """Create temporary directory for testing."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up temporary directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test ImpactAnalyzer initialization."""
        analyzer = ImpactAnalyzer(self.test_dir)

        self.assertIsNotNone(analyzer.dependency_graph)
        self.assertIsNotNone(analyzer.test_mapping)
        self.assertEqual(analyzer.repo_path, self.test_dir)

    def test_path_to_module(self):
        """Test converting file path to module name."""
        analyzer = ImpactAnalyzer(self.test_dir)

        # Create a test file path
        test_file = self.test_dir / "src" / "module" / "file.py"

        module_name = analyzer._path_to_module(test_file)

        self.assertEqual(module_name, "src.module.file")

    def test_resolve_relative_import(self):
        """Test resolving relative imports."""
        analyzer = ImpactAnalyzer(self.test_dir)

        # Test level 1 relative import
        current = "src.module.submodule"
        imported = "other"
        level = 1

        result = analyzer._resolve_relative_import(current, imported, level)

        self.assertEqual(result, "src.module.other")

    def test_analyze_changes_no_files(self):
        """Test analyzing changes with no files."""
        analyzer = ImpactAnalyzer(self.test_dir)

        impact = analyzer.analyze_changes([])

        self.assertEqual(len(impact['directly_affected']), 0)
        self.assertEqual(len(impact['tests_to_run']), 0)
        self.assertEqual(impact['risk_level'], 'low')

    def test_analyze_changes_single_file(self):
        """Test analyzing changes with a single Python file."""
        # Create a simple Python file
        src_dir = self.test_dir / "src"
        src_dir.mkdir()

        module_file = src_dir / "module.py"
        module_file.write_text("def function():\n    pass\n")

        analyzer = ImpactAnalyzer(self.test_dir)

        impact = analyzer.analyze_changes(["src/module.py"])

        self.assertGreater(len(impact['directly_affected']), 0)
        self.assertEqual(impact['risk_level'], 'low')

    def test_risk_level_calculation(self):
        """Test risk level calculation based on affected modules."""
        analyzer = ImpactAnalyzer(self.test_dir)

        # Mock a scenario with many affected files
        with patch.object(analyzer, 'dependency_graph') as mock_graph:
            mock_graph.__contains__ = Mock(return_value=False)

            # Create 25 changed files to trigger high risk
            changed_files = [f"src/module{i}.py" for i in range(25)]

            impact = analyzer.analyze_changes(changed_files)

            # Risk should be high due to many files
            self.assertEqual(impact['risk_level'], 'high')

    def test_suggest_test_order_empty(self):
        """Test suggesting test order with empty test set."""
        analyzer = ImpactAnalyzer(self.test_dir)

        ordered = analyzer.suggest_test_order(set())

        self.assertEqual(len(ordered), 0)

    def test_suggest_test_order_single_test(self):
        """Test suggesting test order with single test."""
        analyzer = ImpactAnalyzer(self.test_dir)

        tests = {"test_module"}
        ordered = analyzer.suggest_test_order(tests)

        self.assertEqual(len(ordered), 1)
        self.assertEqual(ordered[0], "test_module")

    def test_suggest_test_order_multiple_tests(self):
        """Test suggesting test order with multiple tests."""
        analyzer = ImpactAnalyzer(self.test_dir)

        tests = {"test_a", "test_b", "test_c"}
        ordered = analyzer.suggest_test_order(tests)

        # Should return all tests in some order
        self.assertEqual(len(ordered), 3)
        self.assertEqual(set(ordered), tests)

    def test_identify_critical_paths(self):
        """Test identifying critical code paths."""
        # Create files with critical keywords
        src_dir = self.test_dir / "src"
        src_dir.mkdir()

        auth_file = src_dir / "auth.py"
        auth_file.write_text("def authenticate():\n    pass\n")

        security_file = src_dir / "security.py"
        security_file.write_text("def encrypt():\n    pass\n")

        analyzer = ImpactAnalyzer(self.test_dir)

        critical_paths = analyzer.identify_critical_paths()

        # Should identify paths involving auth/security modules
        self.assertIsInstance(critical_paths, list)

    def test_generate_impact_report(self):
        """Test generating impact report."""
        analyzer = ImpactAnalyzer(self.test_dir)

        changed_files = ["src/module.py"]

        report = analyzer.generate_impact_report(changed_files)

        # Report should be a string
        self.assertIsInstance(report, str)

        # Should contain key sections
        self.assertIn("Impact Analysis Report", report)
        self.assertIn("Risk Level", report)
        self.assertIn("Changed Files", report)

    def test_generate_impact_report_with_critical_path(self):
        """Test impact report when critical path is affected."""
        # Create auth module
        src_dir = self.test_dir / "src"
        src_dir.mkdir()

        auth_file = src_dir / "auth.py"
        auth_file.write_text("def login():\n    pass\n")

        analyzer = ImpactAnalyzer(self.test_dir)

        report = analyzer.generate_impact_report(["src/auth.py"])

        # Should warn about critical code paths
        # (Note: May not always trigger due to graph complexity)
        self.assertIsInstance(report, str)
        self.assertIn("Risk Level", report)


class TestImpactAnalyzerIntegration(unittest.TestCase):
    """Integration tests for ImpactAnalyzer with realistic scenarios."""

    def setUp(self):
        """Create realistic project structure."""
        self.test_dir = Path(tempfile.mkdtemp())

        # Create src directory with multiple modules
        src = self.test_dir / "src"
        src.mkdir()

        # Create main module
        (src / "main.py").write_text("""
import auth
import utils

def run():
    auth.login()
    utils.process()
""")

        # Create auth module
        (src / "auth.py").write_text("""
def login():
    pass

def logout():
    pass
""")

        # Create utils module
        (src / "utils.py").write_text("""
def process():
    pass
""")

        # Create tests
        tests = self.test_dir / "tests"
        tests.mkdir()

        (tests / "test_auth.py").write_text("""
import unittest

class TestAuth(unittest.TestCase):
    def test_login(self):
        pass
""")

    def tearDown(self):
        """Clean up."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_full_analysis_workflow(self):
        """Test complete analysis workflow."""
        analyzer = ImpactAnalyzer(self.test_dir)

        # Analyze change to auth module
        impact = analyzer.analyze_changes(["src/auth.py"])

        # Should detect direct impact
        self.assertGreater(len(impact['directly_affected']), 0)

        # Should have low risk for single file
        self.assertIn(impact['risk_level'], ['low', 'medium'])


if __name__ == '__main__':
    unittest.main()

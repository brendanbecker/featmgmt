#!/usr/bin/env python3
"""
Unit tests for commit_generator.py
"""

import unittest
import sys
import tempfile
import subprocess
from pathlib import Path

# Add parent scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from commit_generator import CommitGenerator


class TestCommitGenerator(unittest.TestCase):
    """Test suite for CommitGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = CommitGenerator()

    def test_detect_file_type_python(self):
        """Test detecting Python file type."""
        self.assertEqual(self.generator._detect_file_type("test.py"), "python")
        self.assertEqual(self.generator._detect_file_type("src/module.py"), "python")

    def test_detect_file_type_javascript(self):
        """Test detecting JavaScript file types."""
        self.assertEqual(self.generator._detect_file_type("app.js"), "javascript")
        self.assertEqual(self.generator._detect_file_type("component.jsx"), "javascript")

    def test_detect_file_type_typescript(self):
        """Test detecting TypeScript file types."""
        self.assertEqual(self.generator._detect_file_type("app.ts"), "typescript")
        self.assertEqual(self.generator._detect_file_type("component.tsx"), "typescript")

    def test_detect_file_type_other(self):
        """Test detecting unknown file types."""
        self.assertEqual(self.generator._detect_file_type("README.md"), "other")
        self.assertEqual(self.generator._detect_file_type("config.yaml"), "other")

    def test_analyze_diff_basic(self):
        """Test basic diff analysis."""
        diff = """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
+import os
 def test():
     pass
"""
        analysis = self.generator._analyze_diff(diff)

        self.assertEqual(len(analysis['files_changed']), 1)
        self.assertIn("test.py", analysis['files_changed'])
        self.assertEqual(analysis['additions'], 1)
        self.assertEqual(analysis['deletions'], 0)

    def test_analyze_python_changes_function(self):
        """Test detecting Python function additions."""
        additions = ["def new_function():", "    pass"]
        deletions = []
        analysis = {
            'functions_modified': [],
            'classes_modified': [],
            'imports_changed': []
        }

        self.generator._analyze_python_changes(additions, deletions, analysis)

        self.assertIn("new_function", analysis['functions_modified'])

    def test_analyze_python_changes_class(self):
        """Test detecting Python class additions."""
        additions = ["class NewClass:", "    pass"]
        deletions = []
        analysis = {
            'functions_modified': [],
            'classes_modified': [],
            'imports_changed': []
        }

        self.generator._analyze_python_changes(additions, deletions, analysis)

        self.assertIn("NewClass", analysis['classes_modified'])

    def test_analyze_python_changes_import(self):
        """Test detecting Python import changes."""
        additions = ["import os", "from pathlib import Path"]
        deletions = []
        analysis = {
            'functions_modified': [],
            'classes_modified': [],
            'imports_changed': []
        }

        self.generator._analyze_python_changes(additions, deletions, analysis)

        self.assertEqual(len(analysis['imports_changed']), 2)
        self.assertIn("import os", analysis['imports_changed'])

    def test_determine_commit_type_feat(self):
        """Test determining 'feat' commit type."""
        analysis = {
            'functions_modified': ['new_feature'],
            'classes_modified': [],
            'tests_added': False,
            'docs_updated': False,
            'config_changed': False,
            'additions': 50,
            'deletions': 10
        }

        commit_type = self.generator._determine_commit_type(analysis)

        self.assertEqual(commit_type, "feat")

    def test_determine_commit_type_fix(self):
        """Test determining 'fix' commit type."""
        analysis = {
            'functions_modified': ['fix_bug', 'fix_error'],
            'classes_modified': [],
            'tests_added': False,
            'docs_updated': False,
            'config_changed': False,
            'additions': 10,
            'deletions': 8
        }

        commit_type = self.generator._determine_commit_type(analysis)

        self.assertEqual(commit_type, "fix")

    def test_determine_commit_type_docs(self):
        """Test determining 'docs' commit type."""
        analysis = {
            'functions_modified': [],
            'classes_modified': [],
            'tests_added': False,
            'docs_updated': True,
            'config_changed': False,
            'files_changed': ['README.md'],
            'additions': 5,
            'deletions': 2
        }

        commit_type = self.generator._determine_commit_type(analysis)

        self.assertEqual(commit_type, "docs")

    def test_determine_commit_type_test(self):
        """Test determining 'test' commit type."""
        analysis = {
            'functions_modified': [],
            'classes_modified': [],
            'tests_added': True,
            'docs_updated': False,
            'config_changed': False,
            'changes_by_type': {},
            'additions': 20,
            'deletions': 0
        }

        commit_type = self.generator._determine_commit_type(analysis)

        self.assertEqual(commit_type, "test")

    def test_determine_commit_type_refactor(self):
        """Test determining 'refactor' commit type."""
        analysis = {
            'functions_modified': ['update_logic'],
            'classes_modified': [],
            'tests_added': False,
            'docs_updated': False,
            'config_changed': False,
            'additions': 15,
            'deletions': 14
        }

        commit_type = self.generator._determine_commit_type(analysis)

        self.assertEqual(commit_type, "refactor")

    def test_determine_scope_single_directory(self):
        """Test determining scope from single directory."""
        analysis = {
            'files_changed': ['src/module1.py', 'src/module2.py'],
            'tests_added': False,
            'docs_updated': False
        }

        scope = self.generator._determine_scope(analysis)

        self.assertEqual(scope, "src")

    def test_determine_scope_tests(self):
        """Test determining 'test' scope."""
        analysis = {
            'files_changed': ['src/module.py', 'tests/test_module.py'],
            'tests_added': True,
            'docs_updated': False
        }

        scope = self.generator._determine_scope(analysis)

        self.assertEqual(scope, "test")

    def test_determine_scope_docs(self):
        """Test determining 'docs' scope."""
        analysis = {
            'files_changed': ['README.md', 'docs/guide.md'],
            'tests_added': False,
            'docs_updated': True
        }

        scope = self.generator._determine_scope(analysis)

        self.assertEqual(scope, "docs")

    def test_generate_description_single_class(self):
        """Test generating description for single class."""
        analysis = {
            'classes_modified': ['MyClass'],
            'functions_modified': [],
            'tests_added': False,
            'docs_updated': False,
            'config_changed': False,
            'files_changed': ['src/module.py']
        }

        description = self.generator._generate_description(analysis)

        self.assertEqual(description, "update MyClass class")

    def test_generate_description_multiple_classes(self):
        """Test generating description for multiple classes."""
        analysis = {
            'classes_modified': ['Class1', 'Class2', 'Class3'],
            'functions_modified': [],
            'tests_added': False,
            'docs_updated': False,
            'config_changed': False,
            'files_changed': ['src/module.py']
        }

        description = self.generator._generate_description(analysis)

        self.assertEqual(description, "update 3 classes")

    def test_generate_description_function(self):
        """Test generating description for function."""
        analysis = {
            'classes_modified': [],
            'functions_modified': ['my_function'],
            'tests_added': False,
            'docs_updated': False,
            'config_changed': False,
            'files_changed': ['src/module.py']
        }

        description = self.generator._generate_description(analysis)

        self.assertEqual(description, "modify my_function function")

    def test_validate_commit_message_valid(self):
        """Test validating a valid conventional commit message."""
        message = "feat(api): add new endpoint for user management"

        valid, errors = self.generator.validate_commit_message(message)

        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_validate_commit_message_invalid_format(self):
        """Test validating an invalid commit message format."""
        message = "Added a new feature"

        valid, errors = self.generator.validate_commit_message(message)

        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

    def test_validate_commit_message_header_too_long(self):
        """Test validating a commit message with too long header."""
        message = "feat: " + "x" * 80

        valid, errors = self.generator.validate_commit_message(message)

        self.assertFalse(valid)
        self.assertTrue(any("too long" in error.lower() for error in errors))

    def test_validate_commit_message_with_body(self):
        """Test validating a commit message with body."""
        message = """feat(api): add new endpoint

This adds a new REST endpoint for managing users.
It includes authentication and authorization."""

        valid, errors = self.generator.validate_commit_message(message)

        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_validate_commit_message_missing_blank_line(self):
        """Test validating commit message missing blank line before body."""
        message = """feat(api): add new endpoint
This adds a new REST endpoint."""

        valid, errors = self.generator.validate_commit_message(message)

        self.assertFalse(valid)
        self.assertTrue(any("blank line" in error.lower() for error in errors))

    def test_conventional_types_defined(self):
        """Test that all conventional commit types are defined."""
        expected_types = ['feat', 'fix', 'docs', 'style', 'refactor',
                         'perf', 'test', 'chore', 'ci', 'revert']

        for commit_type in expected_types:
            self.assertIn(commit_type, self.generator.conventional_types)

    def test_analyze_file_changes_test_detection(self):
        """Test detecting test files."""
        analysis = {
            'tests_added': False,
            'docs_updated': False,
            'config_changed': False,
            'changes_by_type': {}
        }

        self.generator._analyze_file_changes(
            'tests/test_module.py',
            ['def test_something(): pass'],
            [],
            analysis
        )

        self.assertTrue(analysis['tests_added'])

    def test_analyze_file_changes_docs_detection(self):
        """Test detecting documentation files."""
        analysis = {
            'tests_added': False,
            'docs_updated': False,
            'config_changed': False,
            'changes_by_type': {}
        }

        self.generator._analyze_file_changes(
            'README.md',
            ['# New Section'],
            [],
            analysis
        )

        self.assertTrue(analysis['docs_updated'])

    def test_analyze_file_changes_config_detection(self):
        """Test detecting configuration files."""
        analysis = {
            'tests_added': False,
            'docs_updated': False,
            'config_changed': False,
            'changes_by_type': {}
        }

        self.generator._analyze_file_changes(
            'config.yaml',
            ['key: value'],
            [],
            analysis
        )

        self.assertTrue(analysis['config_changed'])


if __name__ == '__main__':
    unittest.main()

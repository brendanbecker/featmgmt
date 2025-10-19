#!/usr/bin/env python3
"""
Unit tests for conflict_resolver.py
"""

import unittest
import sys
from pathlib import Path

# Add parent scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from conflict_resolver import ConflictResolver, ConflictType


class TestConflictResolver(unittest.TestCase):
    """Test suite for ConflictResolver class."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = ConflictResolver()

    def test_parse_conflict_markers_simple(self):
        """Test parsing simple 2-way conflict markers."""
        content = """normal line
<<<<<<< HEAD
our change
=======
their change
>>>>>>> branch
normal line 2"""

        conflicts = self.resolver._parse_conflict_markers(content)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]['ours'].strip(), 'our change')
        self.assertEqual(conflicts[0]['theirs'].strip(), 'their change')

    def test_parse_conflict_markers_three_way(self):
        """Test parsing 3-way conflict markers with base."""
        content = """<<<<<<< HEAD
our change
||||||| base
base change
=======
their change
>>>>>>> branch"""

        conflicts = self.resolver._parse_conflict_markers(content)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]['ours'].strip(), 'our change')
        self.assertEqual(conflicts[0]['base'].strip(), 'base change')
        self.assertEqual(conflicts[0]['theirs'].strip(), 'their change')

    def test_parse_conflict_markers_multiple(self):
        """Test parsing multiple conflicts in same file."""
        content = """<<<<<<< HEAD
conflict 1 ours
=======
conflict 1 theirs
>>>>>>> branch
normal line
<<<<<<< HEAD
conflict 2 ours
=======
conflict 2 theirs
>>>>>>> branch"""

        conflicts = self.resolver._parse_conflict_markers(content)

        self.assertEqual(len(conflicts), 2)

    def test_classify_conflict_whitespace(self):
        """Test classifying whitespace-only conflicts."""
        conflict = {
            'ours': '    code with spaces',
            'theirs': '\tcode with tabs'
        }

        conflict_type = self.resolver._classify_conflict(conflict)

        self.assertEqual(conflict_type, ConflictType.WHITESPACE)

    def test_classify_conflict_imports(self):
        """Test classifying import conflicts."""
        conflict = {
            'ours': 'import os\nimport sys',
            'theirs': 'import sys\nimport pathlib'
        }

        conflict_type = self.resolver._classify_conflict(conflict)

        self.assertEqual(conflict_type, ConflictType.IMPORTS)

    def test_classify_conflict_version(self):
        """Test classifying version conflicts."""
        conflict = {
            'ours': 'version = "1.2.3"',
            'theirs': 'version = "1.2.4"'
        }

        conflict_type = self.resolver._classify_conflict(conflict)

        self.assertEqual(conflict_type, ConflictType.VERSION)

    def test_classify_conflict_comment(self):
        """Test classifying comment-only conflicts."""
        conflict = {
            'ours': '# Comment version 1',
            'theirs': '# Comment version 2'
        }

        conflict_type = self.resolver._classify_conflict(conflict)

        self.assertEqual(conflict_type, ConflictType.COMMENT)

    def test_classify_conflict_simple_code(self):
        """Test classifying simple code conflicts."""
        conflict = {
            'ours': 'x = 1',
            'theirs': 'x = 2'
        }

        conflict_type = self.resolver._classify_conflict(conflict)

        self.assertEqual(conflict_type, ConflictType.SIMPLE_CODE)

    def test_classify_conflict_complex_code(self):
        """Test classifying complex code conflicts."""
        conflict = {
            'ours': '''def function1():
    complex logic here
    with many lines
    of code
    that differs''',
            'theirs': '''def function2():
    different complex logic
    with different approach
    using different methods
    completely different'''
        }

        conflict_type = self.resolver._classify_conflict(conflict)

        self.assertEqual(conflict_type, ConflictType.COMPLEX_CODE)

    def test_is_auto_resolvable_whitespace(self):
        """Test that whitespace conflicts are auto-resolvable."""
        self.assertTrue(self.resolver._is_auto_resolvable(ConflictType.WHITESPACE))

    def test_is_auto_resolvable_imports(self):
        """Test that import conflicts are auto-resolvable."""
        self.assertTrue(self.resolver._is_auto_resolvable(ConflictType.IMPORTS))

    def test_is_auto_resolvable_version(self):
        """Test that version conflicts are auto-resolvable."""
        self.assertTrue(self.resolver._is_auto_resolvable(ConflictType.VERSION))

    def test_is_auto_resolvable_comment(self):
        """Test that comment conflicts are auto-resolvable."""
        self.assertTrue(self.resolver._is_auto_resolvable(ConflictType.COMMENT))

    def test_is_auto_resolvable_simple_code(self):
        """Test that simple code conflicts are auto-resolvable."""
        self.assertTrue(self.resolver._is_auto_resolvable(ConflictType.SIMPLE_CODE))

    def test_is_auto_resolvable_complex_code(self):
        """Test that complex code conflicts are NOT auto-resolvable."""
        self.assertFalse(self.resolver._is_auto_resolvable(ConflictType.COMPLEX_CODE))

    def test_merge_imports_simple(self):
        """Test merging simple import statements."""
        ours = "import os\nimport sys"
        theirs = "import sys\nimport pathlib"

        merged = self.resolver._merge_imports(ours, theirs)

        self.assertIn("import os", merged)
        self.assertIn("import sys", merged)
        self.assertIn("import pathlib", merged)

    def test_merge_imports_duplicates(self):
        """Test merging imports removes duplicates."""
        ours = "import os\nimport sys"
        theirs = "import os\nimport pathlib"

        merged = self.resolver._merge_imports(ours, theirs)

        # Count occurrences of 'import os'
        self.assertEqual(merged.count("import os"), 1)

    def test_merge_imports_sorted(self):
        """Test that merged imports are sorted."""
        ours = "from pathlib import Path\nimport os"
        theirs = "import sys"

        merged = self.resolver._merge_imports(ours, theirs)

        lines = [line for line in merged.split('\n') if line.strip()]
        # Should sort: import statements first, then from statements
        import_lines = [line for line in lines if line.startswith('import ')]
        from_lines = [line for line in lines if line.startswith('from ')]

        # Import lines should come before from lines
        if import_lines and from_lines:
            import_idx = lines.index(import_lines[0])
            from_idx = lines.index(from_lines[0])
            self.assertLess(import_idx, from_idx)

    def test_resolve_version_conflict_higher_wins(self):
        """Test that higher version wins in version conflicts."""
        ours = 'version = "1.2.3"'
        theirs = 'version = "1.2.4"'

        resolved = self.resolver._resolve_version_conflict(ours, theirs)

        self.assertIn("1.2.4", resolved)

    def test_resolve_version_conflict_major_version(self):
        """Test version resolution with major version differences."""
        ours = 'version = "1.5.9"'
        theirs = 'version = "2.0.0"'

        resolved = self.resolver._resolve_version_conflict(ours, theirs)

        self.assertIn("2.0.0", resolved)

    def test_resolve_version_conflict_ours_higher(self):
        """Test version resolution when ours is higher."""
        ours = 'version = "1.3.0"'
        theirs = 'version = "1.2.9"'

        resolved = self.resolver._resolve_version_conflict(ours, theirs)

        self.assertIn("1.3.0", resolved)

    def test_resolve_single_conflict_whitespace(self):
        """Test resolving whitespace conflicts."""
        conflict = {
            'type': ConflictType.WHITESPACE,
            'ours': '    code',  # spaces
            'theirs': '\tcode'   # tabs
        }

        resolved = self.resolver._resolve_single_conflict(conflict)

        self.assertIsNotNone(resolved)
        self.assertIn('code', resolved)

    def test_resolve_single_conflict_imports(self):
        """Test resolving import conflicts."""
        conflict = {
            'type': ConflictType.IMPORTS,
            'ours': 'import os\nimport sys',
            'theirs': 'import sys\nimport pathlib'
        }

        resolved = self.resolver._resolve_single_conflict(conflict)

        self.assertIsNotNone(resolved)
        self.assertIn('import os', resolved)
        self.assertIn('import pathlib', resolved)

    def test_resolve_single_conflict_version(self):
        """Test resolving version conflicts."""
        conflict = {
            'type': ConflictType.VERSION,
            'ours': 'version = "1.0.0"',
            'theirs': 'version = "1.0.1"'
        }

        resolved = self.resolver._resolve_single_conflict(conflict)

        self.assertIsNotNone(resolved)
        self.assertIn("1.0.1", resolved)

    def test_resolve_single_conflict_comment(self):
        """Test resolving comment conflicts."""
        conflict = {
            'type': ConflictType.COMMENT,
            'ours': '# Comment A',
            'theirs': '# Comment B'
        }

        resolved = self.resolver._resolve_single_conflict(conflict)

        self.assertIsNotNone(resolved)
        # Should merge both comments
        self.assertIn('Comment A', resolved)
        self.assertIn('Comment B', resolved)

    def test_resolve_single_conflict_simple_code(self):
        """Test resolving simple code conflicts."""
        conflict = {
            'type': ConflictType.SIMPLE_CODE,
            'ours': 'x = 1',
            'theirs': 'x = 2'
        }

        resolved = self.resolver._resolve_single_conflict(conflict)

        self.assertIsNotNone(resolved)

    def test_resolve_single_conflict_complex_code(self):
        """Test that complex code conflicts return None."""
        conflict = {
            'type': ConflictType.COMPLEX_CODE,
            'ours': 'complex code',
            'theirs': 'different complex code'
        }

        resolved = self.resolver._resolve_single_conflict(conflict)

        self.assertIsNone(resolved)

    def test_create_conflict_report(self):
        """Test creating conflict resolution report."""
        conflicts = [
            {
                'file': 'test1.py',
                'total_conflicts': 2,
                'auto_resolvable': True,
                'conflicts': [
                    {'type': ConflictType.IMPORTS, 'auto_resolvable': True},
                    {'type': ConflictType.WHITESPACE, 'auto_resolvable': True}
                ]
            },
            {
                'file': 'test2.py',
                'total_conflicts': 1,
                'auto_resolvable': False,
                'conflicts': [
                    {'type': ConflictType.COMPLEX_CODE, 'auto_resolvable': False}
                ]
            }
        ]

        report = self.resolver.create_conflict_report(conflicts)

        self.assertIn("test1.py", report)
        self.assertIn("test2.py", report)
        self.assertIn("2", report)  # Total files
        self.assertIn("1/2", report)  # Auto-resolvable count

    def test_is_simple_code_conflict_single_line(self):
        """Test that single-line changes are considered simple."""
        result = self.resolver._is_simple_code_conflict("x = 1", "x = 2")

        self.assertTrue(result)

    def test_is_simple_code_conflict_two_lines(self):
        """Test that two-line changes are considered simple."""
        result = self.resolver._is_simple_code_conflict(
            "x = 1\ny = 2",
            "x = 2\ny = 3"
        )

        self.assertTrue(result)

    def test_is_simple_code_conflict_many_lines(self):
        """Test that many-line changes may not be simple."""
        ours = "\n".join([f"line {i}" for i in range(20)])
        theirs = "\n".join([f"different {i}" for i in range(20)])

        result = self.resolver._is_simple_code_conflict(ours, theirs)

        # This should be False due to large diff
        self.assertFalse(result)

    def test_conflict_patterns_defined(self):
        """Test that all conflict patterns are defined."""
        self.assertIn(ConflictType.WHITESPACE, self.resolver.conflict_patterns)
        self.assertIn(ConflictType.IMPORTS, self.resolver.conflict_patterns)
        self.assertIn(ConflictType.VERSION, self.resolver.conflict_patterns)
        self.assertIn(ConflictType.COMMENT, self.resolver.conflict_patterns)


if __name__ == '__main__':
    unittest.main()

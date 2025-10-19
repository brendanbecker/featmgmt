#!/usr/bin/env python3
"""
Unit tests for dependency analyzer.
"""

import json
import pytest
from pathlib import Path
import tempfile
import shutil
import sys

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from analyze_dependencies import DependencyAnalyzer


class TestDependencyAnalyzer:
    """Test suite for DependencyAnalyzer class."""

    @pytest.fixture
    def temp_feature_dir(self):
        """Create a temporary feature directory structure for testing."""
        temp_dir = tempfile.mkdtemp()
        feature_dir = Path(temp_dir)

        # Create bugs directory
        bugs_dir = feature_dir / 'bugs'
        bugs_dir.mkdir()

        # Create features directory
        features_dir = feature_dir / 'features'
        features_dir.mkdir()

        # Create sample bug with dependencies
        bug_001 = bugs_dir / 'BUG-001-sample-bug'
        bug_001.mkdir()
        (bug_001 / 'PROMPT.md').write_text("""
# BUG-001: Sample Bug

## Dependencies
Depends on: FEAT-002
Blocked by: BUG-003
""")

        # Create sample bug without dependencies
        bug_002 = bugs_dir / 'BUG-002-another-bug'
        bug_002.mkdir()
        (bug_002 / 'PROMPT.md').write_text("""
# BUG-002: Another Bug

No dependencies.
""")

        # Create sample bug that blocks others
        bug_003 = bugs_dir / 'BUG-003-blocker'
        bug_003.mkdir()
        (bug_003 / 'PROMPT.md').write_text("""
# BUG-003: Blocker Bug

This blocks other items.
""")

        # Create sample feature
        feat_002 = features_dir / 'FEAT-002-sample-feature'
        feat_002.mkdir()
        (feat_002 / 'PROMPT.md').write_text("""
# FEAT-002: Sample Feature

Requires: BUG-003
""")

        yield feature_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def analyzer(self, temp_feature_dir):
        """Create a DependencyAnalyzer instance."""
        return DependencyAnalyzer(temp_feature_dir)

    def test_initialization(self, temp_feature_dir):
        """Test that analyzer initializes correctly."""
        analyzer = DependencyAnalyzer(temp_feature_dir)
        assert analyzer.feature_dir == temp_feature_dir
        assert analyzer.graph is not None

    def test_extract_dependencies_with_deps(self, analyzer, temp_feature_dir):
        """Test extracting dependencies from a file with dependencies."""
        prompt_file = temp_feature_dir / 'bugs' / 'BUG-001-sample-bug' / 'PROMPT.md'
        deps = analyzer._extract_dependencies(prompt_file)

        assert 'FEAT-002' in deps
        assert 'BUG-003' in deps
        assert len(deps) == 2

    def test_extract_dependencies_without_deps(self, analyzer, temp_feature_dir):
        """Test extracting dependencies from a file without dependencies."""
        prompt_file = temp_feature_dir / 'bugs' / 'BUG-002-another-bug' / 'PROMPT.md'
        deps = analyzer._extract_dependencies(prompt_file)

        assert len(deps) == 0

    def test_scan_dependencies(self, analyzer):
        """Test scanning all items for dependencies."""
        dependencies = analyzer.scan_dependencies()

        # Should find all items
        assert 'BUG-001-sample-bug' in dependencies
        assert 'BUG-002-another-bug' in dependencies
        assert 'BUG-003-blocker' in dependencies
        assert 'FEAT-002-sample-feature' in dependencies

        # Check specific dependencies
        assert 'FEAT-002' in dependencies['BUG-001-sample-bug']
        assert 'BUG-003' in dependencies['BUG-001-sample-bug']
        assert 'BUG-003' in dependencies['FEAT-002-sample-feature']
        assert len(dependencies['BUG-002-another-bug']) == 0

    def test_graph_construction(self, analyzer):
        """Test that dependency graph is constructed correctly."""
        analyzer.scan_dependencies()

        # Check nodes exist
        assert 'BUG-001-sample-bug' in analyzer.graph.nodes()
        assert 'BUG-003-blocker' in analyzer.graph.nodes()

        # Check edges (dependencies)
        # BUG-001 depends on FEAT-002, which resolves to FEAT-002-sample-feature
        # so edge should be FEAT-002-sample-feature -> BUG-001-sample-bug
        assert analyzer.graph.has_edge('FEAT-002-sample-feature', 'BUG-001-sample-bug')
        assert analyzer.graph.has_edge('BUG-003-blocker', 'BUG-001-sample-bug')

    def test_find_critical_path(self, analyzer):
        """Test finding the critical path in dependency graph."""
        analyzer.scan_dependencies()
        critical_path = analyzer.find_critical_path()

        # Should have a path
        assert isinstance(critical_path, list)
        # BUG-003-blocker should be at the start as it blocks others
        assert critical_path[0] == 'BUG-003-blocker'

    def test_get_ready_items_empty_completed(self, analyzer):
        """Test getting ready items when nothing is completed."""
        analyzer.scan_dependencies()
        ready = analyzer.get_ready_items(set())

        # Items with no dependencies should be ready
        assert 'BUG-002-another-bug' in ready
        assert 'BUG-003-blocker' in ready
        # Items with dependencies should not be ready
        assert 'BUG-001-sample-bug' not in ready

    def test_get_ready_items_with_completed(self, analyzer):
        """Test getting ready items with some completed."""
        analyzer.scan_dependencies()
        # Use full IDs that match actual graph nodes
        completed = {'BUG-003-blocker', 'FEAT-002-sample-feature'}
        ready = analyzer.get_ready_items(completed)

        # Now BUG-001 should be ready since its dependencies are complete
        assert 'BUG-001-sample-bug' in ready
        assert 'BUG-002-another-bug' in ready

    def test_analyze_full_run(self, analyzer):
        """Test full analysis run."""
        results = analyzer.analyze()

        assert 'dependencies' in results
        assert 'critical_path' in results
        assert 'has_cycles' in results
        assert 'depth' in results
        assert 'components' in results

        # Should not have cycles in our test data
        assert results['has_cycles'] is False
        assert results['depth'] >= 0

    def test_empty_directory(self):
        """Test analyzer with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = DependencyAnalyzer(Path(temp_dir))
            results = analyzer.analyze()

            assert results['dependencies'] == {}
            assert results['critical_path'] == []
            assert results['has_cycles'] is False

    def test_circular_dependencies(self):
        """Test detection of circular dependencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            feature_dir = Path(temp_dir)
            bugs_dir = feature_dir / 'bugs'
            bugs_dir.mkdir()

            # Create circular dependency: BUG-001 -> BUG-002 -> BUG-001
            bug_001 = bugs_dir / 'BUG-001-circular'
            bug_001.mkdir()
            (bug_001 / 'PROMPT.md').write_text("Depends on: BUG-002")

            bug_002 = bugs_dir / 'BUG-002-circular'
            bug_002.mkdir()
            (bug_002 / 'PROMPT.md').write_text("Depends on: BUG-001-circular")

            analyzer = DependencyAnalyzer(feature_dir)
            results = analyzer.analyze()

            # Should detect cycle
            assert results['has_cycles'] is True
            assert results['depth'] == -1  # Invalid for cyclic graphs


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

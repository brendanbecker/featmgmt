#!/usr/bin/env python3
"""
Unit tests for pattern recognition.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil
import sys

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from pattern_recognition import PatternRecognizer


class TestPatternRecognizer:
    """Test suite for PatternRecognizer class."""

    @pytest.fixture
    def temp_completed_dir(self):
        """Create a temporary completed directory with sample items."""
        temp_dir = tempfile.mkdtemp()
        completed_dir = Path(temp_dir)

        # Create sample completed items
        items_data = [
            {
                'id': 'BUG-001',
                'title': 'Fixed Auth Issue',
                'components': ['auth', 'security'],
                'original_priority': 'P0',
                'status': 'completed',
                'completed_date': '2025-10-01',
                'estimated_hours': 4,
                'actual_hours': 6,
                'completion_time_hours': 6,
                'story_points': 5,
                'blockers': ['authentication', 'database']
            },
            {
                'id': 'BUG-002',
                'title': 'Fixed UI Bug',
                'components': ['ui'],
                'original_priority': 'P1',
                'status': 'completed',
                'completed_date': '2025-10-08',
                'estimated_hours': 2,
                'actual_hours': 3,
                'completion_time_hours': 3,
                'story_points': 3,
                'blockers': ['ui']
            },
            {
                'id': 'FEAT-001',
                'title': 'Added New Feature',
                'components': ['core', 'api'],
                'original_priority': 'P1',
                'status': 'completed',
                'completed_date': '2025-10-10',
                'estimated_hours': 8,
                'actual_hours': 10,
                'completion_time_hours': 10,
                'story_points': 8,
                'blockers': ['api']
            },
            {
                'id': 'BUG-003',
                'title': 'Failed Bug Fix',
                'components': ['data'],
                'original_priority': 'P2',
                'status': 'failed',
                'completed_date': '2025-10-15',
                'estimated_hours': 5,
                'actual_hours': 12,
                'completion_time_hours': 12,
                'story_points': 5,
                'blockers': ['database', 'performance']
            }
        ]

        for item_data in items_data:
            item_dir = completed_dir / item_data['id']
            item_dir.mkdir()
            metadata_file = item_dir / 'metadata.json'
            metadata_file.write_text(json.dumps(item_data, indent=2))

        yield completed_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def recognizer(self, temp_completed_dir):
        """Create a PatternRecognizer instance."""
        return PatternRecognizer(temp_completed_dir)

    def test_initialization(self, temp_completed_dir):
        """Test that recognizer initializes correctly."""
        recognizer = PatternRecognizer(temp_completed_dir)
        assert recognizer.completed_dir == temp_completed_dir
        assert recognizer.patterns is not None

    def test_load_completed_items(self, recognizer):
        """Test loading completed items from directory."""
        items = recognizer._load_completed_items()

        assert len(items) == 4
        assert any(item['id'] == 'BUG-001' for item in items)
        assert any(item['id'] == 'FEAT-001' for item in items)

    def test_load_completed_items_empty_directory(self):
        """Test loading from empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recognizer = PatternRecognizer(Path(temp_dir))
            items = recognizer._load_completed_items()
            assert items == []

    def test_analyze_completion_times(self, recognizer):
        """Test analysis of completion times by component."""
        items = recognizer._load_completed_items()
        times = recognizer._analyze_completion_times(items)

        assert 'auth' in times
        assert 'ui' in times
        assert 'core' in times

        # Check that statistics are calculated
        assert 'mean' in times['ui']
        assert 'median' in times['ui']
        assert 'stdev' in times['ui']

        # UI has only one item with 3 hours
        assert times['ui']['mean'] == 3

    def test_analyze_completion_times_multiple_items(self, recognizer):
        """Test completion times for components with multiple items."""
        items = recognizer._load_completed_items()
        times = recognizer._analyze_completion_times(items)

        # auth and security both appear in BUG-001
        if 'auth' in times:
            assert times['auth']['mean'] == 6

    def test_analyze_success_rates(self, recognizer):
        """Test analysis of success rates by priority."""
        items = recognizer._load_completed_items()
        rates = recognizer._analyze_success_rates(items)

        assert 'P0' in rates
        assert 'P1' in rates
        assert 'P2' in rates

        # P0 has 1 completed item out of 1 total
        assert rates['P0'] == 1.0

        # P1 has 2 completed items out of 2 total
        assert rates['P1'] == 1.0

        # P2 has 0 completed items out of 1 total (failed)
        assert rates['P2'] == 0.0

    def test_analyze_velocity_trend(self, recognizer):
        """Test analysis of velocity trend over time."""
        items = recognizer._load_completed_items()
        trend = recognizer._analyze_velocity_trend(items)

        assert len(trend) > 0
        assert all('week' in entry for entry in trend)
        assert all('items_completed' in entry for entry in trend)
        assert all('points_completed' in entry for entry in trend)

        # Check that weeks are sorted
        weeks = [entry['week'] for entry in trend]
        assert weeks == sorted(weeks)

    def test_identify_common_blockers(self, recognizer):
        """Test identification of common blockers."""
        items = recognizer._load_completed_items()
        blockers = recognizer._identify_common_blockers(items)

        assert len(blockers) > 0
        assert all('type' in blocker for blocker in blockers)
        assert all('frequency' in blocker for blocker in blockers)

        # 'database' appears in 2 items
        database_blocker = next((b for b in blockers if b['type'] == 'database'), None)
        assert database_blocker is not None
        assert database_blocker['frequency'] == 2

        # Blockers should be sorted by frequency (descending)
        frequencies = [b['frequency'] for b in blockers]
        assert frequencies == sorted(frequencies, reverse=True)

    def test_identify_common_blockers_limit(self, recognizer):
        """Test that common blockers are limited to top 10."""
        items = recognizer._load_completed_items()
        blockers = recognizer._identify_common_blockers(items)

        assert len(blockers) <= 10

    def test_analyze_effort_accuracy(self, recognizer):
        """Test analysis of effort estimation accuracy."""
        items = recognizer._load_completed_items()
        accuracy = recognizer._analyze_effort_accuracy(items)

        assert 'mean_error' in accuracy
        assert 'median_error' in accuracy
        assert 'typically_underestimate' in accuracy
        assert 'adjustment_factor' in accuracy

        # All our items have actual > estimated, so we underestimate
        assert accuracy['typically_underestimate'] is True
        assert accuracy['adjustment_factor'] > 1.0

    def test_analyze_effort_accuracy_insufficient_data(self):
        """Test effort accuracy with insufficient data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            completed_dir = Path(temp_dir)
            item_dir = completed_dir / 'BUG-001'
            item_dir.mkdir()

            # Item without effort data
            metadata = {'id': 'BUG-001', 'status': 'completed'}
            (item_dir / 'metadata.json').write_text(json.dumps(metadata))

            recognizer = PatternRecognizer(completed_dir)
            items = recognizer._load_completed_items()
            accuracy = recognizer._analyze_effort_accuracy(items)

            assert 'message' in accuracy
            assert accuracy['message'] == 'Insufficient data'

    def test_analyze_historical_patterns(self, recognizer):
        """Test full historical pattern analysis."""
        patterns = recognizer.analyze_historical_patterns()

        assert 'completion_time_by_component' in patterns
        assert 'success_rate_by_priority' in patterns
        assert 'velocity_trend' in patterns
        assert 'common_blockers' in patterns
        assert 'effort_accuracy' in patterns

    def test_get_recommendations_low_velocity(self):
        """Test recommendations for low velocity."""
        patterns = {
            'velocity_trend': [
                {'week': '2025-W40', 'items_completed': 2, 'points_completed': 5},
                {'week': '2025-W41', 'items_completed': 3, 'points_completed': 8},
                {'week': '2025-W42', 'items_completed': 1, 'points_completed': 2}
            ]
        }

        recognizer = PatternRecognizer(Path('.'))  # Path doesn't matter for this test
        recommendations = recognizer.get_recommendations(patterns)

        assert len(recommendations) > 0
        assert any('velocity' in rec.lower() for rec in recommendations)

    def test_get_recommendations_effort_accuracy(self):
        """Test recommendations for poor effort accuracy."""
        patterns = {
            'effort_accuracy': {
                'mean_error': 50,  # 50% underestimation
                'adjustment_factor': 1.5
            }
        }

        recognizer = PatternRecognizer(Path('.'))
        recommendations = recognizer.get_recommendations(patterns)

        assert len(recommendations) > 0
        assert any('estimate' in rec.lower() for rec in recommendations)

    def test_get_recommendations_common_blocker(self):
        """Test recommendations for frequent blockers."""
        patterns = {
            'common_blockers': [
                {'type': 'database', 'frequency': 10},
                {'type': 'api', 'frequency': 3}
            ]
        }

        recognizer = PatternRecognizer(Path('.'))
        recommendations = recognizer.get_recommendations(patterns)

        assert len(recommendations) > 0
        assert any('database' in rec.lower() for rec in recommendations)

    def test_get_recommendations_no_issues(self):
        """Test recommendations when there are no issues."""
        patterns = {
            'velocity_trend': [
                {'week': '2025-W40', 'items_completed': 10, 'points_completed': 25},
                {'week': '2025-W41', 'items_completed': 12, 'points_completed': 30},
                {'week': '2025-W42', 'items_completed': 11, 'points_completed': 28}
            ],
            'effort_accuracy': {
                'mean_error': 5,
                'adjustment_factor': 1.05
            },
            'common_blockers': [
                {'type': 'dependencies', 'frequency': 2}
            ]
        }

        recognizer = PatternRecognizer(Path('.'))
        recommendations = recognizer.get_recommendations(patterns)

        # Should have few or no recommendations
        assert len(recommendations) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

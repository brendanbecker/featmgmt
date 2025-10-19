#!/usr/bin/env python3
"""
Unit tests for priority calculator.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import sys

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from calculate_priority import PriorityCalculator


class TestPriorityCalculator:
    """Test suite for PriorityCalculator class."""

    @pytest.fixture
    def calculator(self):
        """Create a PriorityCalculator instance with default config."""
        return PriorityCalculator()

    @pytest.fixture
    def custom_config(self):
        """Create a custom configuration file."""
        config_data = {
            'weights': {
                'severity': 0.30,
                'age': 0.20,
                'dependencies': 0.20,
                'impact': 0.15,
                'effort': 0.10,
                'frequency': 0.05
            },
            'severity_scores': {
                'critical': 100,
                'high': 75,
                'medium': 50,
                'low': 25,
                'enhancement': 10
            },
            'age_thresholds': {
                'urgent': 1,
                'old': 7,
                'stale': 30
            }
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            return Path(f.name)

    def test_initialization_default_config(self):
        """Test initialization with default configuration."""
        calculator = PriorityCalculator()
        assert calculator.config is not None
        assert 'weights' in calculator.config
        assert 'severity_scores' in calculator.config

    def test_initialization_custom_config(self, custom_config):
        """Test initialization with custom configuration."""
        calculator = PriorityCalculator(custom_config)
        assert calculator.config['weights']['severity'] == 0.30
        custom_config.unlink()  # Cleanup

    def test_severity_score_critical(self, calculator):
        """Test severity scoring for critical items."""
        score = calculator._severity_score('critical')
        assert score == 100

    def test_severity_score_high(self, calculator):
        """Test severity scoring for high severity items."""
        score = calculator._severity_score('high')
        assert score == 75

    def test_severity_score_medium(self, calculator):
        """Test severity scoring for medium severity items."""
        score = calculator._severity_score('medium')
        assert score == 50

    def test_severity_score_low(self, calculator):
        """Test severity scoring for low severity items."""
        score = calculator._severity_score('low')
        assert score == 25

    def test_severity_score_enhancement(self, calculator):
        """Test severity scoring for enhancements."""
        score = calculator._severity_score('enhancement')
        assert score == 10

    def test_severity_score_unknown(self, calculator):
        """Test severity scoring for unknown severity."""
        score = calculator._severity_score('unknown')
        assert score == 50  # Default

    def test_age_score_new_item(self, calculator):
        """Test age scoring for very new items."""
        today = datetime.now().isoformat()
        score = calculator._age_score(today)
        assert score == 90

    def test_age_score_stale_item(self, calculator):
        """Test age scoring for very old items."""
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        score = calculator._age_score(old_date)
        assert score == 80

    def test_age_score_old_item(self, calculator):
        """Test age scoring for moderately old items."""
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        score = calculator._age_score(old_date)
        assert score == 60

    def test_age_score_recent_item(self, calculator):
        """Test age scoring for recent items."""
        recent_date = (datetime.now() - timedelta(days=3)).isoformat()
        score = calculator._age_score(recent_date)
        assert score == 40

    def test_age_score_no_date(self, calculator):
        """Test age scoring with no date provided."""
        score = calculator._age_score(None)
        assert score == 50

    def test_dependency_score_no_blockers(self, calculator):
        """Test dependency scoring with no blocked items."""
        score = calculator._dependency_score([])
        assert score == 0

    def test_dependency_score_one_blocker(self, calculator):
        """Test dependency scoring with one blocked item."""
        score = calculator._dependency_score(['BUG-001'])
        assert score == 50

    def test_dependency_score_few_blockers(self, calculator):
        """Test dependency scoring with a few blocked items."""
        score = calculator._dependency_score(['BUG-001', 'BUG-002', 'BUG-003'])
        assert score == 75

    def test_dependency_score_many_blockers(self, calculator):
        """Test dependency scoring with many blocked items."""
        score = calculator._dependency_score(['BUG-001', 'BUG-002', 'BUG-003', 'BUG-004', 'BUG-005'])
        assert score == 100

    def test_impact_score_no_components(self, calculator):
        """Test impact scoring with no components."""
        score = calculator._impact_score([])
        assert score == 25

    def test_impact_score_critical_component(self, calculator):
        """Test impact scoring with critical component."""
        score = calculator._impact_score(['core'])
        assert score == 100

    def test_impact_score_security_component(self, calculator):
        """Test impact scoring with security component."""
        score = calculator._impact_score(['security'])
        assert score == 100

    def test_impact_score_multiple_critical(self, calculator):
        """Test impact scoring with multiple critical components."""
        score = calculator._impact_score(['core', 'security', 'data'])
        assert score == 100

    def test_impact_score_wide_impact(self, calculator):
        """Test impact scoring with many non-critical components."""
        score = calculator._impact_score(['ui', 'api', 'docs', 'tests'])
        assert score == 75

    def test_impact_score_normal(self, calculator):
        """Test impact scoring with normal components."""
        score = calculator._impact_score(['ui', 'docs'])
        assert score == 50

    def test_effort_score_quick_win(self, calculator):
        """Test effort scoring for quick wins."""
        score = calculator._effort_score(2)
        assert score == 100

    def test_effort_score_small(self, calculator):
        """Test effort scoring for small tasks."""
        score = calculator._effort_score(6)
        assert score == 75

    def test_effort_score_medium(self, calculator):
        """Test effort scoring for medium tasks."""
        score = calculator._effort_score(20)
        assert score == 50

    def test_effort_score_large(self, calculator):
        """Test effort scoring for large tasks."""
        score = calculator._effort_score(80)
        assert score == 25

    def test_effort_score_unknown(self, calculator):
        """Test effort scoring for unknown effort."""
        score = calculator._effort_score(0)
        assert score == 50

    def test_frequency_score_single(self, calculator):
        """Test frequency scoring for single occurrence."""
        score = calculator._frequency_score(1)
        assert score == 25

    def test_frequency_score_few(self, calculator):
        """Test frequency scoring for few occurrences."""
        score = calculator._frequency_score(3)
        assert score == 50

    def test_frequency_score_many(self, calculator):
        """Test frequency scoring for many occurrences."""
        score = calculator._frequency_score(8)
        assert score == 75

    def test_frequency_score_very_frequent(self, calculator):
        """Test frequency scoring for very frequent occurrences."""
        score = calculator._frequency_score(15)
        assert score == 100

    def test_calculate_item_score_critical_bug(self, calculator):
        """Test calculating score for a critical bug."""
        item = {
            'severity': 'critical',
            'created': datetime.now().isoformat(),
            'blocking': ['BUG-002', 'BUG-003'],
            'components': ['core', 'security'],
            'estimated_hours': 4,
            'occurrences': 5
        }
        score = calculator.calculate_item_score(item)

        # Should be high priority
        assert score > 70

    def test_calculate_item_score_enhancement(self, calculator):
        """Test calculating score for an enhancement."""
        item = {
            'severity': 'enhancement',
            'created': (datetime.now() - timedelta(days=5)).isoformat(),
            'blocking': [],
            'components': ['ui'],
            'estimated_hours': 2,
            'occurrences': 1
        }
        score = calculator.calculate_item_score(item)

        # Should be lower priority
        assert score < 50

    def test_prioritize_items_ordering(self, calculator):
        """Test that items are prioritized correctly."""
        items = [
            {
                'id': 'FEAT-001',
                'severity': 'enhancement',
                'created': '2025-10-15',
                'blocking': [],
                'components': ['ui'],
                'estimated_hours': 2,
                'occurrences': 1,
                'priority': 'P2'
            },
            {
                'id': 'BUG-001',
                'severity': 'critical',
                'created': '2025-10-01',
                'blocking': ['FEAT-002', 'FEAT-003'],
                'components': ['core', 'security'],
                'estimated_hours': 4,
                'occurrences': 10,
                'priority': 'P0'
            },
            {
                'id': 'BUG-002',
                'severity': 'medium',
                'created': '2025-10-10',
                'blocking': [],
                'components': ['api'],
                'estimated_hours': 1,
                'occurrences': 2,
                'priority': 'P1'
            }
        ]

        prioritized = calculator.prioritize_items(items)

        # Critical bug should be first
        assert prioritized[0]['id'] == 'BUG-001'
        # Enhancement should be last
        assert prioritized[-1]['id'] == 'FEAT-001'

    def test_prioritize_items_adds_scores(self, calculator):
        """Test that prioritize_items adds scores to items."""
        items = [
            {
                'id': 'BUG-001',
                'severity': 'high',
                'created': '2025-10-15',
                'blocking': [],
                'components': ['core'],
                'estimated_hours': 2,
                'occurrences': 3
            }
        ]

        prioritized = calculator.prioritize_items(items)

        assert 'priority_score' in prioritized[0]
        assert 'priority_factors' in prioritized[0]
        assert 'severity' in prioritized[0]['priority_factors']
        assert 'age' in prioritized[0]['priority_factors']

    def test_empty_items_list(self, calculator):
        """Test prioritizing an empty list."""
        items = []
        prioritized = calculator.prioritize_items(items)
        assert prioritized == []

    def test_items_with_missing_fields(self, calculator):
        """Test prioritizing items with missing fields."""
        items = [
            {'id': 'BUG-001'},  # Missing most fields
            {
                'id': 'BUG-002',
                'severity': 'critical',
                'components': ['core']
            }
        ]

        # Should not raise exception
        prioritized = calculator.prioritize_items(items)
        assert len(prioritized) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

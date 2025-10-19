#!/usr/bin/env python3
"""
Multi-factor priority calculator for work items.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re

class PriorityCalculator:
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.scores = {}

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load priority calculation configuration."""
        if config_path and config_path.exists():
            return json.loads(config_path.read_text())

        # Default configuration
        return {
            'weights': {
                'severity': 0.25,
                'age': 0.15,
                'dependencies': 0.20,
                'impact': 0.20,
                'effort': 0.10,
                'frequency': 0.10
            },
            'severity_scores': {
                'critical': 100,
                'high': 75,
                'medium': 50,
                'low': 25,
                'enhancement': 10
            },
            'age_thresholds': {
                'urgent': 1,  # days
                'old': 7,
                'stale': 30
            }
        }

    def calculate_item_score(self, item: Dict) -> float:
        """Calculate priority score for a single item."""
        weights = self.config['weights']

        severity_score = self._severity_score(item.get('severity', 'medium'))
        age_score = self._age_score(item.get('created'))
        dep_score = self._dependency_score(item.get('blocking', []))
        impact_score = self._impact_score(item.get('components', []))
        effort_score = self._effort_score(item.get('estimated_hours', 0))
        frequency_score = self._frequency_score(item.get('occurrences', 1))

        total_score = (
            severity_score * weights['severity'] +
            age_score * weights['age'] +
            dep_score * weights['dependencies'] +
            impact_score * weights['impact'] +
            effort_score * weights['effort'] +
            frequency_score * weights['frequency']
        )

        return total_score

    def _severity_score(self, severity: str) -> float:
        """Score based on severity level."""
        return self.config['severity_scores'].get(severity.lower(), 50)

    def _age_score(self, created_date: Optional[str]) -> float:
        """Score based on item age."""
        if not created_date:
            return 50

        try:
            created = datetime.fromisoformat(created_date)
            age_days = (datetime.now() - created).days

            thresholds = self.config['age_thresholds']
            if age_days <= thresholds['urgent']:
                return 90  # New urgent items
            elif age_days >= thresholds['stale']:
                return 80  # Very old items need attention
            elif age_days >= thresholds['old']:
                return 60
            else:
                return 40
        except:
            return 50

    def _dependency_score(self, blocking: List[str]) -> float:
        """Score based on how many items this blocks."""
        if not blocking:
            return 0
        elif len(blocking) == 1:
            return 50
        elif len(blocking) <= 3:
            return 75
        else:
            return 100  # Critical blocker

    def _impact_score(self, components: List[str]) -> float:
        """Score based on affected components."""
        critical_components = {'core', 'security', 'data', 'auth', 'payment'}

        if not components:
            return 25

        if any(c in critical_components for c in components):
            return 100
        elif len(components) > 3:
            return 75  # Wide impact
        else:
            return 50

    def _effort_score(self, estimated_hours: float) -> float:
        """Score based on effort (prefer quick wins)."""
        if estimated_hours == 0:
            return 50  # Unknown effort
        elif estimated_hours <= 2:
            return 100  # Quick win
        elif estimated_hours <= 8:
            return 75
        elif estimated_hours <= 40:
            return 50
        else:
            return 25  # Large effort

    def _frequency_score(self, occurrences: int) -> float:
        """Score based on frequency of occurrence."""
        if occurrences <= 1:
            return 25
        elif occurrences <= 5:
            return 50
        elif occurrences <= 10:
            return 75
        else:
            return 100  # Very frequent issue

    def prioritize_items(self, items: List[Dict]) -> List[Dict]:
        """Calculate scores and sort items by priority."""
        for item in items:
            item['priority_score'] = self.calculate_item_score(item)
            item['priority_factors'] = {
                'severity': self._severity_score(item.get('severity', 'medium')),
                'age': self._age_score(item.get('created')),
                'dependencies': self._dependency_score(item.get('blocking', [])),
                'impact': self._impact_score(item.get('components', [])),
                'effort': self._effort_score(item.get('estimated_hours', 0)),
                'frequency': self._frequency_score(item.get('occurrences', 1))
            }

        # Sort by score (highest first), then by original priority as tiebreaker
        return sorted(items, key=lambda x: (-x['priority_score'], x.get('priority', 'P3')))

if __name__ == '__main__':
    calculator = PriorityCalculator()

    # Example items
    items = [
        {
            'id': 'BUG-001',
            'severity': 'critical',
            'created': '2024-10-01',
            'blocking': ['FEAT-002', 'FEAT-003'],
            'components': ['core', 'security'],
            'estimated_hours': 4
        },
        {
            'id': 'FEAT-001',
            'severity': 'enhancement',
            'created': '2024-10-15',
            'blocking': [],
            'components': ['ui'],
            'estimated_hours': 2
        }
    ]

    prioritized = calculator.prioritize_items(items)
    print(json.dumps(prioritized, indent=2, default=str))

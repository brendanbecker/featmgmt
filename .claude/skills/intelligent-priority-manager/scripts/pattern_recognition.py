#!/usr/bin/env python3
"""
Historical pattern recognition for priority optimization.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import statistics

class PatternRecognizer:
    def __init__(self, completed_dir: Path):
        self.completed_dir = completed_dir
        self.patterns = defaultdict(list)

    def analyze_historical_patterns(self) -> Dict:
        """Analyze completed items for patterns."""
        completed_items = self._load_completed_items()

        patterns = {
            'completion_time_by_component': self._analyze_completion_times(completed_items),
            'success_rate_by_priority': self._analyze_success_rates(completed_items),
            'velocity_trend': self._analyze_velocity_trend(completed_items),
            'common_blockers': self._identify_common_blockers(completed_items),
            'effort_accuracy': self._analyze_effort_accuracy(completed_items)
        }

        return patterns

    def _load_completed_items(self) -> List[Dict]:
        """Load all completed items."""
        items = []

        for item_dir in self.completed_dir.iterdir():
            if not item_dir.is_dir():
                continue

            metadata_file = item_dir / 'metadata.json'
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())
                items.append(metadata)

        return items

    def _analyze_completion_times(self, items: List[Dict]) -> Dict:
        """Analyze average completion times by component."""
        times_by_component = defaultdict(list)

        for item in items:
            if 'completion_time_hours' in item and 'components' in item:
                for component in item['components']:
                    times_by_component[component].append(item['completion_time_hours'])

        averages = {}
        for component, times in times_by_component.items():
            if times:
                averages[component] = {
                    'mean': statistics.mean(times),
                    'median': statistics.median(times),
                    'stdev': statistics.stdev(times) if len(times) > 1 else 0
                }

        return averages

    def _analyze_success_rates(self, items: List[Dict]) -> Dict:
        """Calculate success rates by original priority."""
        by_priority = defaultdict(lambda: {'total': 0, 'successful': 0})

        for item in items:
            priority = item.get('original_priority', 'P3')
            by_priority[priority]['total'] += 1
            if item.get('status') == 'completed':
                by_priority[priority]['successful'] += 1

        rates = {}
        for priority, counts in by_priority.items():
            if counts['total'] > 0:
                rates[priority] = counts['successful'] / counts['total']

        return rates

    def _analyze_velocity_trend(self, items: List[Dict]) -> List[Dict]:
        """Analyze team velocity over time."""
        # Group by week
        weekly_velocity = defaultdict(lambda: {'count': 0, 'total_points': 0})

        for item in items:
            if 'completed_date' in item:
                completed = datetime.fromisoformat(item['completed_date'])
                week = completed.isocalendar()[1]
                year = completed.year
                week_key = f"{year}-W{week:02d}"

                weekly_velocity[week_key]['count'] += 1
                weekly_velocity[week_key]['total_points'] += item.get('story_points', 1)

        # Convert to sorted list
        trend = []
        for week, data in sorted(weekly_velocity.items()):
            trend.append({
                'week': week,
                'items_completed': data['count'],
                'points_completed': data['total_points']
            })

        return trend

    def _identify_common_blockers(self, items: List[Dict]) -> List[Dict]:
        """Identify patterns in what blocks items."""
        blocker_frequency = defaultdict(int)

        for item in items:
            blockers = item.get('blockers', [])
            for blocker in blockers:
                blocker_frequency[blocker] += 1

        # Sort by frequency
        common_blockers = [
            {'type': blocker, 'frequency': freq}
            for blocker, freq in sorted(blocker_frequency.items(), key=lambda x: x[1], reverse=True)
        ]

        return common_blockers[:10]  # Top 10 blockers

    def _analyze_effort_accuracy(self, items: List[Dict]) -> Dict:
        """Analyze how accurate effort estimates are."""
        estimation_errors = []

        for item in items:
            if 'estimated_hours' in item and 'actual_hours' in item:
                estimated = item['estimated_hours']
                actual = item['actual_hours']
                if estimated > 0:
                    error_percentage = ((actual - estimated) / estimated) * 100
                    estimation_errors.append(error_percentage)

        if estimation_errors:
            return {
                'mean_error': statistics.mean(estimation_errors),
                'median_error': statistics.median(estimation_errors),
                'typically_underestimate': statistics.mean(estimation_errors) > 0,
                'adjustment_factor': 1 + (statistics.mean(estimation_errors) / 100)
            }

        return {'message': 'Insufficient data'}

    def get_recommendations(self, patterns: Dict) -> List[str]:
        """Generate recommendations based on patterns."""
        recommendations = []

        # Check velocity trend
        if 'velocity_trend' in patterns and len(patterns['velocity_trend']) > 2:
            recent_velocity = patterns['velocity_trend'][-3:]
            if all(week['items_completed'] < 5 for week in recent_velocity):
                recommendations.append("Velocity is low - consider reducing scope or adding resources")

        # Check effort accuracy
        if 'effort_accuracy' in patterns and 'adjustment_factor' in patterns['effort_accuracy']:
            factor = patterns['effort_accuracy']['adjustment_factor']
            if factor > 1.3:
                recommendations.append(f"Estimates are typically {(factor-1)*100:.0f}% under - adjust estimates upward")

        # Check common blockers
        if 'common_blockers' in patterns and patterns['common_blockers']:
            top_blocker = patterns['common_blockers'][0]
            if top_blocker['frequency'] > 5:
                recommendations.append(f"'{top_blocker['type']}' is a frequent blocker - prioritize resolving")

        return recommendations

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: pattern_recognition.py <feature-management-path>")
        sys.exit(1)

    # Use absolute path from argument and construct completed directory path
    base_path = Path(sys.argv[1]).resolve()
    completed_dir = base_path / "completed"

    recognizer = PatternRecognizer(completed_dir)
    patterns = recognizer.analyze_historical_patterns()
    recommendations = recognizer.get_recommendations(patterns)

    result = {
        'patterns': patterns,
        'recommendations': recommendations
    }

    print(json.dumps(result, indent=2, default=str))

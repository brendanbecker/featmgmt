#!/usr/bin/env python3
"""
Detect and manage flaky tests using statistical analysis.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class FlakyTestDetector:
    def __init__(self, db_path: Path = Path("test_history.db")):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self._initialize_db()
        self.flaky_threshold = 0.1  # 10% failure rate variation
        self.min_runs = 10  # Minimum runs to determine flakiness

    def _initialize_db(self):
        """Initialize database for test history."""
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                passed BOOLEAN NOT NULL,
                execution_time REAL,
                error_message TEXT,
                run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                build_number TEXT,
                branch TEXT,
                commit_hash TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flaky_tests (
                test_name TEXT PRIMARY KEY,
                flakiness_score REAL,
                failure_rate REAL,
                variance REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quarantined BOOLEAN DEFAULT FALSE,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_test_name
            ON test_runs(test_name)
        ''')

        self.conn.commit()

    def record_test_run(self, test_name: str, passed: bool,
                       execution_time: float, error: Optional[str] = None,
                       build_info: Optional[Dict] = None):
        """Record a test execution result."""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO test_runs (test_name, passed, execution_time, error_message,
                                  build_number, branch, commit_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            test_name,
            passed,
            execution_time,
            error,
            build_info.get('build_number') if build_info else None,
            build_info.get('branch') if build_info else None,
            build_info.get('commit_hash') if build_info else None
        ))

        self.conn.commit()

        # Check if test should be analyzed for flakiness
        self._analyze_test_flakiness(test_name)

    def _analyze_test_flakiness(self, test_name: str):
        """Analyze a test for flakiness."""
        cursor = self.conn.cursor()

        # Get recent test runs
        cursor.execute('''
            SELECT passed, execution_time, run_date
            FROM test_runs
            WHERE test_name = ?
            ORDER BY run_date DESC
            LIMIT 100
        ''', (test_name,))

        runs = cursor.fetchall()

        if len(runs) < self.min_runs:
            return  # Not enough data

        # Calculate statistics
        pass_rates = [1 if passed else 0 for passed, _, _ in runs]
        execution_times = [time for _, time, _ in runs if time]

        # Calculate flakiness metrics
        failure_rate = 1 - statistics.mean(pass_rates)

        # Check for intermittent failures
        flakiness_score = self._calculate_flakiness_score(pass_rates)

        # Check for timing variations
        if execution_times:
            time_variance = statistics.variance(execution_times) if len(execution_times) > 1 else 0
            time_cv = statistics.stdev(execution_times) / statistics.mean(execution_times) if len(execution_times) > 1 else 0
        else:
            time_variance = 0
            time_cv = 0

        # Determine if test is flaky
        is_flaky = (
            flakiness_score > self.flaky_threshold or
            time_cv > 0.5 or  # High coefficient of variation in timing
            (0.1 < failure_rate < 0.9)  # Intermittent failures
        )

        if is_flaky:
            self._mark_test_flaky(test_name, flakiness_score, failure_rate, time_variance)

    def _calculate_flakiness_score(self, results: List[int]) -> float:
        """Calculate flakiness score based on result patterns."""
        if len(results) < 2:
            return 0

        # Count transitions (pass->fail or fail->pass)
        transitions = sum(1 for i in range(1, len(results)) if results[i] != results[i-1])

        # Maximum possible transitions
        max_transitions = len(results) - 1

        # Flakiness score is ratio of actual to maximum transitions
        flakiness = transitions / max_transitions if max_transitions > 0 else 0

        # Adjust for runs that are mostly passing or failing
        failure_rate = 1 - statistics.mean(results)
        if failure_rate < 0.1 or failure_rate > 0.9:
            flakiness *= 2  # Amplify flakiness for mostly stable tests with occasional failures

        return flakiness

    def _mark_test_flaky(self, test_name: str, flakiness_score: float,
                        failure_rate: float, variance: float):
        """Mark a test as flaky in the database."""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO flaky_tests
            (test_name, flakiness_score, failure_rate, variance, last_updated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (test_name, flakiness_score, failure_rate, variance))

        self.conn.commit()

        print(f"⚠️ Test marked as flaky: {test_name} (score: {flakiness_score:.2f})")

    def get_flaky_tests(self, include_quarantined: bool = False) -> List[Dict]:
        """Get list of flaky tests."""
        cursor = self.conn.cursor()

        query = '''
            SELECT test_name, flakiness_score, failure_rate, variance,
                   last_updated, quarantined, notes
            FROM flaky_tests
        '''

        if not include_quarantined:
            query += ' WHERE quarantined = FALSE'

        query += ' ORDER BY flakiness_score DESC'

        cursor.execute(query)

        flaky_tests = []
        for row in cursor.fetchall():
            flaky_tests.append({
                'test_name': row[0],
                'flakiness_score': row[1],
                'failure_rate': row[2],
                'variance': row[3],
                'last_updated': row[4],
                'quarantined': bool(row[5]),
                'notes': row[6]
            })

        return flaky_tests

    def quarantine_test(self, test_name: str, reason: str = ""):
        """Quarantine a flaky test."""
        cursor = self.conn.cursor()

        cursor.execute('''
            UPDATE flaky_tests
            SET quarantined = TRUE, notes = ?
            WHERE test_name = ?
        ''', (reason, test_name))

        self.conn.commit()

        print(f"🔒 Test quarantined: {test_name}")

    def analyze_failure_patterns(self, test_name: str) -> Dict:
        """Analyze failure patterns for a specific test."""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT passed, error_message, run_date, branch, commit_hash
            FROM test_runs
            WHERE test_name = ?
            ORDER BY run_date DESC
            LIMIT 100
        ''', (test_name,))

        runs = cursor.fetchall()

        if not runs:
            return {'message': 'No test runs found'}

        # Analyze patterns
        patterns = {
            'total_runs': len(runs),
            'failures': [],
            'error_types': defaultdict(int),
            'branch_failures': defaultdict(int),
            'time_patterns': [],
            'correlation': {}
        }

        for passed, error, run_date, branch, commit in runs:
            if not passed:
                patterns['failures'].append({
                    'date': run_date,
                    'error': error,
                    'branch': branch,
                    'commit': commit
                })

                if error:
                    # Categorize error
                    error_type = self._categorize_error(error)
                    patterns['error_types'][error_type] += 1

                if branch:
                    patterns['branch_failures'][branch] += 1

        # Time-based patterns
        if patterns['failures']:
            failure_times = [datetime.fromisoformat(f['date']) for f in patterns['failures']]
            patterns['time_patterns'] = self._analyze_time_patterns(failure_times)

        # Correlation with other flaky tests
        patterns['correlation'] = self._find_correlated_failures(test_name)

        return patterns

    def _categorize_error(self, error_message: str) -> str:
        """Categorize error messages."""
        error_lower = error_message.lower()

        if 'timeout' in error_lower:
            return 'timeout'
        elif 'connection' in error_lower or 'network' in error_lower:
            return 'network'
        elif 'assertion' in error_lower or 'assert' in error_lower:
            return 'assertion'
        elif 'permission' in error_lower or 'access denied' in error_lower:
            return 'permission'
        elif 'memory' in error_lower or 'heap' in error_lower:
            return 'memory'
        elif 'file not found' in error_lower or 'no such file' in error_lower:
            return 'file_not_found'
        else:
            return 'other'

    def _analyze_time_patterns(self, failure_times: List[datetime]) -> Dict:
        """Analyze time-based patterns in failures."""
        if len(failure_times) < 2:
            return {}

        patterns = {
            'clustering': False,
            'periodic': False,
            'time_of_day': defaultdict(int),
            'day_of_week': defaultdict(int)
        }

        # Check for clustering
        time_diffs = []
        for i in range(1, len(failure_times)):
            diff = (failure_times[i-1] - failure_times[i]).total_seconds() / 3600  # hours
            time_diffs.append(diff)

        if time_diffs:
            mean_diff = statistics.mean(time_diffs)
            std_diff = statistics.stdev(time_diffs) if len(time_diffs) > 1 else 0

            # Clustering if failures happen close together
            patterns['clustering'] = std_diff < mean_diff / 2

        # Time of day analysis
        for failure_time in failure_times:
            hour = failure_time.hour
            patterns['time_of_day'][f"{hour:02d}:00"] += 1
            patterns['day_of_week'][failure_time.strftime('%A')] += 1

        return patterns

    def _find_correlated_failures(self, test_name: str) -> List[Tuple[str, float]]:
        """Find tests that fail together with this test."""
        cursor = self.conn.cursor()

        # Get failure times for this test
        cursor.execute('''
            SELECT run_date
            FROM test_runs
            WHERE test_name = ? AND passed = FALSE
            ORDER BY run_date DESC
            LIMIT 50
        ''', (test_name,))

        failure_times = [row[0] for row in cursor.fetchall()]

        if not failure_times:
            return []

        # Find other tests that failed around the same time
        correlated = defaultdict(int)

        for failure_time in failure_times:
            # Look for failures within 5 minutes
            cursor.execute('''
                SELECT DISTINCT test_name
                FROM test_runs
                WHERE passed = FALSE
                AND test_name != ?
                AND datetime(run_date) BETWEEN datetime(?, '-5 minutes') AND datetime(?, '+5 minutes')
            ''', (test_name, failure_time, failure_time))

            for row in cursor.fetchall():
                correlated[row[0]] += 1

        # Calculate correlation scores
        correlations = []
        for other_test, co_failures in correlated.items():
            correlation_score = co_failures / len(failure_times)
            if correlation_score > 0.3:  # At least 30% correlation
                correlations.append((other_test, correlation_score))

        return sorted(correlations, key=lambda x: x[1], reverse=True)[:5]

    def generate_flakiness_report(self) -> str:
        """Generate comprehensive flakiness report."""
        flaky_tests = self.get_flaky_tests()

        report = ["# Test Flakiness Report\n"]
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        if not flaky_tests:
            report.append("✅ No flaky tests detected!")
            return '\n'.join(report)

        report.append(f"## Summary")
        report.append(f"- Total flaky tests: {len(flaky_tests)}")

        quarantined = [t for t in flaky_tests if t['quarantined']]
        report.append(f"- Quarantined: {len(quarantined)}")
        report.append(f"- Active flaky: {len(flaky_tests) - len(quarantined)}")

        avg_failure_rate = statistics.mean(t['failure_rate'] for t in flaky_tests)
        report.append(f"- Average failure rate: {avg_failure_rate:.1%}\n")

        report.append("## Top Flaky Tests")

        for i, test in enumerate(flaky_tests[:10], 1):
            status = "🔒" if test['quarantined'] else "⚠️"
            report.append(f"\n### {i}. {status} {test['test_name']}")
            report.append(f"- Flakiness score: {test['flakiness_score']:.2f}")
            report.append(f"- Failure rate: {test['failure_rate']:.1%}")
            report.append(f"- Timing variance: {test['variance']:.2f}")

            if test['notes']:
                report.append(f"- Notes: {test['notes']}")

            # Get failure patterns
            patterns = self.analyze_failure_patterns(test['test_name'])
            if patterns['error_types']:
                top_error = max(patterns['error_types'], key=patterns['error_types'].get)
                report.append(f"- Most common error: {top_error}")

            if patterns['correlation']:
                correlated_tests = ', '.join(t for t, _ in patterns['correlation'][:3])
                report.append(f"- Often fails with: {correlated_tests}")

        report.append("\n## Recommendations")
        report.append("1. Review and fix top flaky tests")
        report.append("2. Consider quarantining tests with score > 0.5")
        report.append("3. Investigate correlated failures for common root causes")
        report.append("4. Add retry logic for network-related failures")

        return '\n'.join(report)

if __name__ == '__main__':
    detector = FlakyTestDetector()

    # Example: Record some test runs
    detector.record_test_run("test_login", True, 1.2)
    detector.record_test_run("test_login", False, 2.5, "Timeout error")
    detector.record_test_run("test_login", True, 1.3)

    # Generate report
    report = detector.generate_flakiness_report()
    print(report)

#!/usr/bin/env python3
"""
Performance benchmarking for Intelligent Priority Manager.

Tests performance across different repository sizes and configurations.
"""

import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import statistics

# Import skill modules
from analyze_dependencies import DependencyAnalyzer
from calculate_priority import PriorityCalculator
from pattern_recognition import PatternRecognizer


class BenchmarkSuite:
    def __init__(self):
        self.results = {
            'dependency_analysis': [],
            'priority_calculation': [],
            'pattern_recognition': [],
            'end_to_end': []
        }

    def create_test_repository(self, num_items: int) -> Path:
        """Create a temporary test repository with specified number of items."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create directory structure
        bugs_dir = temp_dir / 'bugs'
        features_dir = temp_dir / 'features'
        completed_dir = temp_dir / 'completed'

        bugs_dir.mkdir()
        features_dir.mkdir()
        completed_dir.mkdir()

        # Create bugs (60% of items)
        num_bugs = int(num_items * 0.6)
        for i in range(num_bugs):
            bug_dir = bugs_dir / f'BUG-{i+1:03d}'
            bug_dir.mkdir()

            # Create PROMPT.md with metadata
            prompt_content = f"""# BUG-{i+1:03d}: Test Bug {i+1}

## Metadata
- **ID**: BUG-{i+1:03d}
- **Severity**: {'critical' if i % 4 == 0 else 'high' if i % 4 == 1 else 'medium' if i % 4 == 2 else 'low'}
- **Priority**: P{i % 4}
- **Created**: 2025-{10:02d}-{(i % 28) + 1:02d}
- **Components**: [{self._random_components(i)}]
- **Estimated Hours**: {(i % 20) + 1}

## Description
Test bug for benchmarking.

## Dependencies
{self._random_dependencies(i, num_bugs)}
"""
            (bug_dir / 'PROMPT.md').write_text(prompt_content)

        # Create features (40% of items)
        num_features = num_items - num_bugs
        for i in range(num_features):
            feat_dir = features_dir / f'FEAT-{i+1:03d}'
            feat_dir.mkdir()

            prompt_content = f"""# FEAT-{i+1:03d}: Test Feature {i+1}

## Metadata
- **ID**: FEAT-{i+1:03d}
- **Severity**: enhancement
- **Priority**: P{(i % 3) + 1}
- **Created**: 2025-{10:02d}-{(i % 28) + 1:02d}
- **Components**: [{self._random_components(i)}]
- **Estimated Hours**: {((i % 40) + 1) * 2}

## Description
Test feature for benchmarking.

## Dependencies
{self._random_dependencies(i, num_items, is_feature=True)}
"""
            (feat_dir / 'PROMPT.md').write_text(prompt_content)

        # Create completed items (20% of total)
        num_completed = int(num_items * 0.2)
        for i in range(num_completed):
            completed_item_dir = completed_dir / f'ITEM-{i+1:03d}'
            completed_item_dir.mkdir()

            metadata = {
                'id': f'ITEM-{i+1:03d}',
                'original_priority': f'P{i % 4}',
                'status': 'completed',
                'created': f'2025-09-{(i % 28) + 1:02d}',
                'completed_date': f'2025-10-{(i % 28) + 1:02d}',
                'components': self._random_components(i).split(', '),
                'estimated_hours': (i % 20) + 1,
                'actual_hours': ((i % 20) + 1) * 1.2,
                'completion_time_hours': ((i % 20) + 1) * 1.2,
                'story_points': (i % 10) + 1,
                'blockers': ['testing', 'dependencies'] if i % 3 == 0 else []
            }
            (completed_item_dir / 'metadata.json').write_text(json.dumps(metadata, indent=2))

        return temp_dir

    def _random_components(self, seed: int) -> str:
        """Generate random components based on seed."""
        components = ['core', 'security', 'data', 'auth', 'api', 'ui', 'docs']
        num_components = (seed % 3) + 1
        selected = [components[(seed + i) % len(components)] for i in range(num_components)]
        return ', '.join(selected)

    def _random_dependencies(self, seed: int, max_id: int, is_feature: bool = False) -> str:
        """Generate random dependencies."""
        if seed % 5 != 0:  # 80% have no dependencies
            return ""

        num_deps = (seed % 2) + 1
        deps = []
        for i in range(num_deps):
            dep_id = ((seed + i) % max_id) + 1
            if is_feature:
                deps.append(f"BUG-{dep_id:03d}")
            else:
                if i % 2 == 0:
                    deps.append(f"BUG-{dep_id:03d}")
                else:
                    deps.append(f"FEAT-{dep_id:03d}")

        return '\n'.join([f'Depends on: {dep}' for dep in deps])

    def benchmark_dependency_analysis(self, repo_path: Path, num_items: int) -> Dict:
        """Benchmark dependency analysis performance."""
        analyzer = DependencyAnalyzer(repo_path)

        # Measure scan_dependencies
        start = time.time()
        dependencies = analyzer.scan_dependencies()
        scan_time = time.time() - start

        # Measure critical_path
        start = time.time()
        critical_path = analyzer.find_critical_path()
        critical_path_time = time.time() - start

        # Measure full analysis
        start = time.time()
        results = analyzer.analyze()
        analysis_time = time.time() - start

        return {
            'num_items': num_items,
            'scan_time': scan_time,
            'critical_path_time': critical_path_time,
            'total_analysis_time': analysis_time,
            'dependencies_found': sum(len(deps) for deps in dependencies.values()),
            'critical_path_length': len(critical_path)
        }

    def benchmark_priority_calculation(self, num_items: int) -> Dict:
        """Benchmark priority calculation performance."""
        calculator = PriorityCalculator()

        # Create test items
        items = []
        for i in range(num_items):
            items.append({
                'id': f'ITEM-{i+1:03d}',
                'severity': 'critical' if i % 4 == 0 else 'high' if i % 4 == 1 else 'medium' if i % 4 == 2 else 'low',
                'created': f'2025-{10:02d}-{(i % 28) + 1:02d}',
                'blocking': [f'ITEM-{j:03d}' for j in range(i+1, min(i+3, num_items))],
                'components': ['core', 'api'][(i % 2):],
                'estimated_hours': (i % 20) + 1,
                'occurrences': (i % 10) + 1
            })

        # Measure single item calculation
        start = time.time()
        for item in items[:min(100, num_items)]:
            calculator.calculate_item_score(item)
        single_calc_time = (time.time() - start) / min(100, num_items)

        # Measure bulk prioritization
        start = time.time()
        prioritized = calculator.prioritize_items(items)
        bulk_calc_time = time.time() - start

        return {
            'num_items': num_items,
            'single_item_avg_time': single_calc_time,
            'bulk_prioritization_time': bulk_calc_time,
            'items_per_second': num_items / bulk_calc_time if bulk_calc_time > 0 else 0
        }

    def benchmark_pattern_recognition(self, repo_path: Path, num_completed: int) -> Dict:
        """Benchmark pattern recognition performance."""
        completed_dir = repo_path / 'completed'
        recognizer = PatternRecognizer(completed_dir)

        # Measure pattern analysis
        start = time.time()
        patterns = recognizer.analyze_historical_patterns()
        analysis_time = time.time() - start

        # Measure recommendations
        start = time.time()
        recommendations = recognizer.get_recommendations(patterns)
        rec_time = time.time() - start

        return {
            'num_completed_items': num_completed,
            'pattern_analysis_time': analysis_time,
            'recommendation_time': rec_time,
            'total_time': analysis_time + rec_time,
            'recommendations_generated': len(recommendations)
        }

    def benchmark_end_to_end(self, repo_path: Path, num_items: int) -> Dict:
        """Benchmark complete workflow."""
        start_total = time.time()

        # Dependency analysis
        start = time.time()
        analyzer = DependencyAnalyzer(repo_path)
        dep_results = analyzer.analyze()
        dep_time = time.time() - start

        # Priority calculation
        start = time.time()
        calculator = PriorityCalculator()
        items = []
        for i in range(num_items):
            items.append({
                'id': f'ITEM-{i+1:03d}',
                'severity': 'medium',
                'created': '2025-10-15',
                'blocking': [],
                'components': ['core'],
                'estimated_hours': 5,
                'occurrences': 1
            })
        prioritized = calculator.prioritize_items(items)
        calc_time = time.time() - start

        # Pattern recognition
        start = time.time()
        recognizer = PatternRecognizer(repo_path / 'completed')
        patterns = recognizer.analyze_historical_patterns()
        pattern_time = time.time() - start

        total_time = time.time() - start_total

        return {
            'num_items': num_items,
            'dependency_time': dep_time,
            'calculation_time': calc_time,
            'pattern_time': pattern_time,
            'total_time': total_time,
            'items_per_second': num_items / total_time if total_time > 0 else 0
        }

    def run_benchmark(self, sizes: List[int] = [10, 50, 100, 250, 500, 1000]):
        """Run full benchmark suite across different repository sizes."""
        print("=" * 70)
        print("INTELLIGENT PRIORITY MANAGER - PERFORMANCE BENCHMARK")
        print("=" * 70)
        print()

        for size in sizes:
            print(f"Testing with {size} items...")

            # Create test repository
            repo_path = self.create_test_repository(size)

            try:
                # Dependency analysis
                dep_result = self.benchmark_dependency_analysis(repo_path, size)
                self.results['dependency_analysis'].append(dep_result)
                print(f"  Dependency analysis: {dep_result['total_analysis_time']:.4f}s")

                # Priority calculation
                calc_result = self.benchmark_priority_calculation(size)
                self.results['priority_calculation'].append(calc_result)
                print(f"  Priority calculation: {calc_result['bulk_prioritization_time']:.4f}s")

                # Pattern recognition
                num_completed = int(size * 0.2)
                pattern_result = self.benchmark_pattern_recognition(repo_path, num_completed)
                self.results['pattern_recognition'].append(pattern_result)
                print(f"  Pattern recognition: {pattern_result['total_time']:.4f}s")

                # End-to-end
                e2e_result = self.benchmark_end_to_end(repo_path, size)
                self.results['end_to_end'].append(e2e_result)
                print(f"  End-to-end: {e2e_result['total_time']:.4f}s ({e2e_result['items_per_second']:.1f} items/s)")

            finally:
                # Cleanup
                shutil.rmtree(repo_path)

            print()

        # Generate summary
        self.print_summary()

        # Save results
        self.save_results()

    def print_summary(self):
        """Print benchmark summary."""
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print()

        # Dependency Analysis
        print("Dependency Analysis:")
        dep_times = [r['total_analysis_time'] for r in self.results['dependency_analysis']]
        sizes = [r['num_items'] for r in self.results['dependency_analysis']]
        print(f"  Average time: {statistics.mean(dep_times):.4f}s")
        print(f"  Range: {min(dep_times):.4f}s - {max(dep_times):.4f}s")
        print(f"  Scaling: {dep_times[-1]/sizes[-1]:.6f}s per item (linear O(n))")
        print()

        # Priority Calculation
        print("Priority Calculation:")
        calc_times = [r['bulk_prioritization_time'] for r in self.results['priority_calculation']]
        throughput = [r['items_per_second'] for r in self.results['priority_calculation']]
        print(f"  Average time: {statistics.mean(calc_times):.4f}s")
        print(f"  Throughput: {statistics.mean(throughput):.1f} items/s")
        print(f"  Scaling: {calc_times[-1]/sizes[-1]:.6f}s per item (linear O(n))")
        print()

        # Pattern Recognition
        print("Pattern Recognition:")
        pattern_times = [r['total_time'] for r in self.results['pattern_recognition']]
        completed_sizes = [r['num_completed_items'] for r in self.results['pattern_recognition']]
        print(f"  Average time: {statistics.mean(pattern_times):.4f}s")
        print(f"  Range: {min(pattern_times):.4f}s - {max(pattern_times):.4f}s")
        if completed_sizes[-1] > 0:
            print(f"  Scaling: {pattern_times[-1]/completed_sizes[-1]:.6f}s per completed item")
        print()

        # End-to-End
        print("End-to-End Performance:")
        e2e_times = [r['total_time'] for r in self.results['end_to_end']]
        e2e_throughput = [r['items_per_second'] for r in self.results['end_to_end']]
        print(f"  Average time: {statistics.mean(e2e_times):.4f}s")
        print(f"  Throughput: {statistics.mean(e2e_throughput):.1f} items/s")
        print(f"  For 100 items: ~{[t for i,t in zip(sizes, e2e_times) if i == 100][0]:.2f}s")
        print()

        # Performance rating
        print("Performance Rating:")
        avg_e2e_100 = [t for i,t in zip(sizes, e2e_times) if i == 100][0]
        if avg_e2e_100 < 1.0:
            rating = "EXCELLENT (< 1s for 100 items)"
        elif avg_e2e_100 < 3.0:
            rating = "GOOD (< 3s for 100 items)"
        elif avg_e2e_100 < 5.0:
            rating = "ACCEPTABLE (< 5s for 100 items)"
        else:
            rating = "NEEDS OPTIMIZATION (> 5s for 100 items)"
        print(f"  {rating}")
        print()

    def save_results(self, output_path: Path = None):
        """Save benchmark results to JSON file."""
        if output_path is None:
            output_path = Path(__file__).parent.parent / 'benchmark_results.json'

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Results saved to: {output_path}")


if __name__ == '__main__':
    import sys

    suite = BenchmarkSuite()

    # Custom sizes from command line args
    if len(sys.argv) > 1:
        sizes = [int(arg) for arg in sys.argv[1:]]
        suite.run_benchmark(sizes)
    else:
        # Default benchmark suite
        suite.run_benchmark([10, 50, 100, 250, 500, 1000])

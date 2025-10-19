#!/usr/bin/env python3
"""
Test impact analysis based on code changes.
Maps code changes to affected tests.
"""

import ast
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import networkx as nx

class ImpactAnalyzer:
    def __init__(self, repo_path: Path = Path(".")):
        self.repo_path = repo_path
        self.dependency_graph = nx.DiGraph()
        self.test_mapping = defaultdict(set)
        self.coverage_data = {}
        self._build_dependency_graph()
        self._load_coverage_data()

    def _build_dependency_graph(self):
        """Build dependency graph of the codebase."""
        # Find all Python files (example for Python projects)
        python_files = list(self.repo_path.rglob("*.py"))

        for file_path in python_files:
            if 'test' not in str(file_path):
                self._analyze_file_dependencies(file_path)

    def _analyze_file_dependencies(self, file_path: Path):
        """Analyze dependencies for a single file."""
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())

            module_name = self._path_to_module(file_path)

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.dependency_graph.add_edge(module_name, alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_module = node.module
                        if node.level > 0:  # Relative import
                            imported_module = self._resolve_relative_import(
                                module_name, node.module, node.level
                            )
                        self.dependency_graph.add_edge(module_name, imported_module)

                # Track function and class definitions
                elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    full_name = f"{module_name}.{node.name}"
                    self.dependency_graph.add_node(full_name)
                    self.dependency_graph.add_edge(module_name, full_name)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _path_to_module(self, file_path: Path) -> str:
        """Convert file path to module name."""
        relative_path = file_path.relative_to(self.repo_path)
        module_parts = relative_path.with_suffix('').parts
        return '.'.join(module_parts)

    def _resolve_relative_import(self, current_module: str,
                                imported_module: str, level: int) -> str:
        """Resolve relative imports."""
        parts = current_module.split('.')
        if level > len(parts):
            return imported_module

        base_parts = parts[:-level] if level > 0 else parts
        if imported_module:
            base_parts.append(imported_module)

        return '.'.join(base_parts)

    def _load_coverage_data(self):
        """Load test coverage data if available."""
        coverage_file = self.repo_path / ".coverage"
        if coverage_file.exists():
            # Parse coverage data (simplified)
            result = subprocess.run(
                ["coverage", "json", "-o", "-"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                coverage_json = json.loads(result.stdout)
                self.coverage_data = coverage_json.get('files', {})
                self._build_test_mapping()

    def _build_test_mapping(self):
        """Build mapping of code to tests that cover it."""
        # This would parse test execution traces
        # For now, use naming conventions
        test_files = list(self.repo_path.rglob("test_*.py"))
        test_files.extend(list(self.repo_path.rglob("*_test.py")))

        for test_file in test_files:
            test_module = self._path_to_module(test_file)

            # Simple heuristic: test_foo.py tests foo.py
            if test_file.name.startswith("test_"):
                source_name = test_file.name[5:]
            elif test_file.name.endswith("_test.py"):
                source_name = test_file.name[:-8] + ".py"
            else:
                continue

            # Find corresponding source file
            source_candidates = list(self.repo_path.rglob(source_name))
            for source_file in source_candidates:
                if 'test' not in str(source_file.parent):
                    source_module = self._path_to_module(source_file)
                    self.test_mapping[source_module].add(test_module)

    def analyze_changes(self, changed_files: List[str]) -> Dict:
        """Analyze impact of file changes."""
        impact = {
            'directly_affected': set(),
            'indirectly_affected': set(),
            'tests_to_run': set(),
            'risk_level': 'low',
            'estimated_test_count': 0
        }

        # Analyze each changed file
        for file_path in changed_files:
            if file_path.endswith('.py'):
                module = self._path_to_module(Path(file_path))
                impact['directly_affected'].add(module)

                # Find dependent modules
                if module in self.dependency_graph:
                    dependents = nx.descendants(self.dependency_graph, module)
                    impact['indirectly_affected'].update(dependents)

                # Find tests that should run
                if module in self.test_mapping:
                    impact['tests_to_run'].update(self.test_mapping[module])

                # Check for indirect test dependencies
                for dependent in dependents:
                    if dependent in self.test_mapping:
                        impact['tests_to_run'].update(self.test_mapping[dependent])

        # Assess risk level
        total_affected = len(impact['directly_affected']) + len(impact['indirectly_affected'])
        if total_affected > 20:
            impact['risk_level'] = 'high'
        elif total_affected > 10:
            impact['risk_level'] = 'medium'

        impact['estimated_test_count'] = len(impact['tests_to_run'])

        return impact

    def suggest_test_order(self, tests: Set[str]) -> List[str]:
        """Suggest optimal test execution order."""
        # Order tests by:
        # 1. Historical failure rate (fail-fast)
        # 2. Execution time (quick tests first)
        # 3. Dependencies (independent tests first)

        test_scores = {}

        for test in tests:
            score = 0

            # Historical failure rate (would load from database)
            failure_rate = self._get_historical_failure_rate(test)
            score += failure_rate * 100

            # Execution time
            exec_time = self._get_average_execution_time(test)
            score -= exec_time  # Lower time = higher priority

            # Dependencies
            if test in self.dependency_graph:
                dep_count = len(list(self.dependency_graph.predecessors(test)))
                score -= dep_count * 10

            test_scores[test] = score

        # Sort by score (highest first)
        return sorted(tests, key=lambda t: test_scores[t], reverse=True)

    def _get_historical_failure_rate(self, test: str) -> float:
        """Get historical failure rate for a test."""
        # This would query a database of test results
        # For now, return mock data
        return 0.1

    def _get_average_execution_time(self, test: str) -> float:
        """Get average execution time for a test."""
        # This would query historical test timing data
        # For now, return mock data
        return 1.0

    def identify_critical_paths(self) -> List[List[str]]:
        """Identify critical code paths that need extensive testing."""
        critical_paths = []

        # Find paths to critical modules
        critical_modules = [
            node for node in self.dependency_graph.nodes()
            if any(keyword in node.lower()
                  for keyword in ['auth', 'security', 'payment', 'crypto', 'password'])
        ]

        for module in critical_modules:
            # Find all paths to this module
            for source in self.dependency_graph.nodes():
                if source != module:
                    try:
                        paths = list(nx.all_simple_paths(
                            self.dependency_graph, source, module, cutoff=5
                        ))
                        critical_paths.extend(paths)
                    except nx.NetworkXNoPath:
                        continue

        return critical_paths

    def generate_impact_report(self, changed_files: List[str]) -> str:
        """Generate detailed impact analysis report."""
        impact = self.analyze_changes(changed_files)

        report = ["# Test Impact Analysis Report\n"]
        report.append(f"**Risk Level**: {impact['risk_level'].upper()}\n")

        report.append("## Changed Files")
        for file in changed_files:
            report.append(f"- {file}")

        report.append(f"\n## Impact Summary")
        report.append(f"- Directly affected modules: {len(impact['directly_affected'])}")
        report.append(f"- Indirectly affected modules: {len(impact['indirectly_affected'])}")
        report.append(f"- Tests to run: {impact['estimated_test_count']}")

        if impact['tests_to_run']:
            report.append("\n## Recommended Test Execution")
            ordered_tests = self.suggest_test_order(impact['tests_to_run'])
            for i, test in enumerate(ordered_tests[:10], 1):
                report.append(f"{i}. {test}")

            if len(ordered_tests) > 10:
                report.append(f"... and {len(ordered_tests) - 10} more tests")

        # Critical paths affected
        critical_paths = self.identify_critical_paths()
        affected_critical = False
        for path in critical_paths:
            if any(module in impact['directly_affected'] or
                  module in impact['indirectly_affected']
                  for module in path):
                affected_critical = True
                break

        if affected_critical:
            report.append("\n⚠️ **Warning**: Changes affect critical code paths!")
            report.append("Recommend running full test suite.")

        return '\n'.join(report)

if __name__ == '__main__':
    analyzer = ImpactAnalyzer()

    # Get changed files from git
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1"],
        capture_output=True,
        text=True
    )

    changed_files = [f for f in result.stdout.strip().split('\n') if f]

    if changed_files:
        report = analyzer.generate_impact_report(changed_files)
        print(report)
    else:
        print("No changes detected")

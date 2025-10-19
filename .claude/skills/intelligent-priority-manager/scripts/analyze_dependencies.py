#!/usr/bin/env python3
"""
Dependency analyzer for work items.
Builds and analyzes dependency graphs.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import networkx as nx

class DependencyAnalyzer:
    def __init__(self, feature_dir: Path):
        self.feature_dir = feature_dir
        self.graph = nx.DiGraph()

    def scan_dependencies(self) -> Dict:
        """Scan all items for dependency declarations."""
        dependencies = {}
        all_items = []

        # First pass: collect all item IDs
        for item_type in ['bugs', 'features']:
            type_dir = self.feature_dir / item_type
            if not type_dir.exists():
                continue

            for item_dir in type_dir.iterdir():
                if not item_dir.is_dir():
                    continue

                prompt_file = item_dir / 'PROMPT.md'
                if not prompt_file.exists():
                    continue

                item_id = item_dir.name
                all_items.append(item_id)
                self.graph.add_node(item_id)

        # Second pass: extract dependencies and build graph
        for item_type in ['bugs', 'features']:
            type_dir = self.feature_dir / item_type
            if not type_dir.exists():
                continue

            for item_dir in type_dir.iterdir():
                if not item_dir.is_dir():
                    continue

                prompt_file = item_dir / 'PROMPT.md'
                if not prompt_file.exists():
                    continue

                item_id = item_dir.name
                deps = self._extract_dependencies(prompt_file)
                dependencies[item_id] = deps

                # Add edges to graph with dependency resolution
                # This allows short IDs like "BUG-002" to match "BUG-002-circular"
                for dep in deps:
                    resolved_dep = self._resolve_dependency(dep, all_items)
                    if resolved_dep:
                        self.graph.add_edge(resolved_dep, item_id)
                    else:
                        # If resolution fails, add edge with original ID
                        # (this handles external dependencies or nodes added separately)
                        self.graph.add_edge(dep, item_id)

        return dependencies

    def _resolve_dependency(self, dep_ref: str, all_items: List[str]) -> str:
        """
        Resolve a dependency reference to an actual item ID.
        Handles cases where 'BUG-002' should match 'BUG-002-circular'.

        Returns the resolved ID, or None if no match found.
        """
        # Exact match - highest priority
        if dep_ref in all_items:
            return dep_ref

        # Prefix match: find items that start with the dependency reference
        # e.g., 'BUG-002' matches 'BUG-002-circular'
        matches = [item for item in all_items if item.startswith(dep_ref + '-')]

        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            # Multiple matches - this is ambiguous, return first match
            # In practice this shouldn't happen with proper naming conventions
            return matches[0]

        # No match found
        return None

    def _extract_dependencies(self, prompt_file: Path) -> List[str]:
        """Extract dependency references from PROMPT.md."""
        content = prompt_file.read_text()

        # Look for various dependency patterns
        # Updated to capture full item IDs including suffixes (e.g., BUG-001-circular)
        patterns = [
            r'[Dd]epends on:?\s*([A-Z]+-\d+(?:-[\w-]+)?)',
            r'[Bb]locked by:?\s*([A-Z]+-\d+(?:-[\w-]+)?)',
            r'[Rr]equires:?\s*([A-Z]+-\d+(?:-[\w-]+)?)',
            r'\[([A-Z]+-\d+(?:-[\w-]+)?)\].*must be completed first'
        ]

        dependencies = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            dependencies.extend(matches)

        return list(set(dependencies))

    def find_critical_path(self) -> List[str]:
        """Find the longest dependency chain."""
        try:
            return nx.dag_longest_path(self.graph)
        except (nx.NetworkXError, nx.NetworkXUnfeasible):
            # Handle cycles - NetworkXUnfeasible is raised when graph contains a cycle
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                print(f"Warning: Circular dependencies detected: {cycles}")
            return []

    def get_ready_items(self, completed: Set[str]) -> List[str]:
        """Get items with all dependencies satisfied."""
        ready = []

        for node in self.graph.nodes():
            if node in completed:
                continue

            predecessors = set(self.graph.predecessors(node))
            if predecessors.issubset(completed):
                ready.append(node)

        return ready

    def analyze(self) -> Dict:
        """Run full dependency analysis."""
        dependencies = self.scan_dependencies()

        return {
            'dependencies': dependencies,
            'critical_path': self.find_critical_path(),
            'has_cycles': not nx.is_directed_acyclic_graph(self.graph),
            'depth': nx.dag_longest_path_length(self.graph) if nx.is_directed_acyclic_graph(self.graph) else -1,
            'components': list(nx.weakly_connected_components(self.graph))
        }

if __name__ == '__main__':
    analyzer = DependencyAnalyzer(Path('./feature-management'))
    results = analyzer.analyze()
    print(json.dumps(results, indent=2, default=str))

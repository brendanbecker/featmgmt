#!/usr/bin/env python3
"""
Cross-project impact analysis for changes.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import networkx as nx
import ast
import yaml

class CrossProjectImpactAnalyzer:
    def __init__(self, registry):
        self.registry = registry
        self.impact_graph = nx.DiGraph()
        self.api_changes = {}
        self.breaking_changes = []

    def analyze_change_impact(self, project_id: str,
                             changed_files: List[str]) -> Dict:
        """Analyze impact of changes across all projects."""
        project = self.registry.get_project(project_id)

        if not project:
            return {'error': 'Project not found'}

        impact = {
            'source_project': project.name,
            'changed_files': changed_files,
            'directly_affected': [],
            'transitively_affected': [],
            'breaking_changes': [],
            'api_changes': [],
            'risk_level': 'low',
            'recommendations': []
        }

        # Analyze what changed
        changes = self._analyze_changes(Path(project.path), changed_files)

        # Check for API changes
        if changes['api_changes']:
            impact['api_changes'] = changes['api_changes']

            # Find projects that depend on this one
            dependent_projects = self._find_dependent_projects(project_id)
            impact['directly_affected'] = dependent_projects

            # Check for breaking changes
            breaking = self._detect_breaking_changes(changes)
            if breaking:
                impact['breaking_changes'] = breaking
                impact['risk_level'] = 'high'

        # Find transitively affected projects
        for dep_project_id in dependent_projects:
            transitive = self._find_dependent_projects(dep_project_id)
            impact['transitively_affected'].extend(transitive)

        impact['transitively_affected'] = list(set(impact['transitively_affected']))

        # Assess overall risk
        impact['risk_level'] = self._assess_risk(impact)

        # Generate recommendations
        impact['recommendations'] = self._generate_recommendations(impact)

        return impact

    def _analyze_changes(self, project_path: Path,
                        changed_files: List[str]) -> Dict:
        """Analyze what changed in the files."""
        changes = {
            'api_changes': [],
            'config_changes': [],
            'schema_changes': [],
            'dependency_changes': []
        }

        for file_path in changed_files:
            full_path = project_path / file_path

            if not full_path.exists():
                continue

            # Check for API changes (simplified)
            if file_path.endswith('.py'):
                api_changes = self._detect_api_changes(full_path)
                if api_changes:
                    changes['api_changes'].extend(api_changes)

            # Check for configuration changes
            elif file_path.endswith(('.json', '.yaml', '.yml')):
                changes['config_changes'].append(file_path)

            # Check for schema changes
            elif 'schema' in file_path or 'model' in file_path:
                changes['schema_changes'].append(file_path)

            # Check for dependency changes
            elif file_path in ['requirements.txt', 'package.json', 'setup.py']:
                changes['dependency_changes'].append(file_path)

        return changes

    def _detect_api_changes(self, file_path: Path) -> List[Dict]:
        """Detect API changes in a Python file."""
        try:
            # Get the diff
            result = subprocess.run(
                ['git', 'diff', 'HEAD~1', str(file_path)],
                cwd=file_path.parent,
                capture_output=True,
                text=True
            )

            if not result.stdout:
                return []

            api_changes = []

            # Parse for function/class changes (simplified)
            for line in result.stdout.split('\n'):
                if line.startswith('-def ') or line.startswith('-class '):
                    # Removed function/class
                    api_changes.append({
                        'type': 'removed',
                        'signature': line[1:].strip(),
                        'file': str(file_path)
                    })
                elif line.startswith('+def ') or line.startswith('+class '):
                    # Added function/class
                    api_changes.append({
                        'type': 'added',
                        'signature': line[1:].strip(),
                        'file': str(file_path)
                    })

            return api_changes

        except Exception as e:
            print(f"Error detecting API changes: {e}")
            return []

    def _detect_breaking_changes(self, changes: Dict) -> List[Dict]:
        """Detect breaking changes from the change analysis."""
        breaking = []

        for api_change in changes['api_changes']:
            if api_change['type'] == 'removed':
                breaking.append({
                    'type': 'api_removed',
                    'description': f"Removed: {api_change['signature']}",
                    'file': api_change['file'],
                    'severity': 'high'
                })
            elif api_change['type'] == 'modified':
                # Check if signature changed (simplified)
                breaking.append({
                    'type': 'api_modified',
                    'description': f"Modified: {api_change['signature']}",
                    'file': api_change['file'],
                    'severity': 'medium'
                })

        # Schema changes are often breaking
        for schema_file in changes['schema_changes']:
            breaking.append({
                'type': 'schema_change',
                'description': f"Schema modified: {schema_file}",
                'file': schema_file,
                'severity': 'high'
            })

        return breaking

    def _find_dependent_projects(self, project_id: str) -> List[str]:
        """Find projects that depend on the given project."""
        cursor = self.registry.conn.cursor()

        cursor.execute('''
            SELECT project_id
            FROM dependencies
            WHERE dependency_id = ?
        ''', (project_id,))

        return [row[0] for row in cursor.fetchall()]

    def _assess_risk(self, impact: Dict) -> str:
        """Assess the overall risk level of changes."""
        if impact['breaking_changes']:
            return 'high'

        total_affected = len(impact['directly_affected']) + len(impact['transitively_affected'])

        if total_affected > 5:
            return 'high'
        elif total_affected > 2:
            return 'medium'
        else:
            return 'low'

    def _generate_recommendations(self, impact: Dict) -> List[str]:
        """Generate recommendations based on impact analysis."""
        recommendations = []

        if impact['breaking_changes']:
            recommendations.append("⚠️ Breaking changes detected - coordinate with affected teams")
            recommendations.append("📝 Update documentation and migration guides")
            recommendations.append("🔄 Consider versioning strategy (major version bump)")

        if impact['directly_affected']:
            affected_names = [
                self.registry.get_project(pid).name
                for pid in impact['directly_affected'][:3]
            ]
            recommendations.append(f"🔔 Notify teams: {', '.join(affected_names)}")

        if impact['risk_level'] == 'high':
            recommendations.append("🧪 Run integration tests across affected projects")
            recommendations.append("🚀 Consider staged rollout")

        if impact['api_changes']:
            recommendations.append("📚 Update API documentation")

        return recommendations

    def generate_impact_report(self, project_id: str,
                              changed_files: List[str]) -> str:
        """Generate a detailed impact report."""
        impact = self.analyze_change_impact(project_id, changed_files)

        report = ["# Cross-Project Impact Analysis\n"]

        report.append(f"**Source Project**: {impact['source_project']}")
        report.append(f"**Risk Level**: {impact['risk_level'].upper()}")
        report.append(f"**Changed Files**: {len(impact['changed_files'])}\n")

        if impact['breaking_changes']:
            report.append("## ⚠️ Breaking Changes")
            for change in impact['breaking_changes']:
                report.append(f"- **{change['severity'].upper()}**: {change['description']}")
                report.append(f"  File: `{change['file']}`")
            report.append("")

        if impact['directly_affected']:
            report.append("## 🎯 Directly Affected Projects")
            for project_id in impact['directly_affected']:
                project = self.registry.get_project(project_id)
                if project:
                    report.append(f"- {project.name} ({project.type})")
            report.append("")

        if impact['transitively_affected']:
            report.append("## 🔄 Transitively Affected Projects")
            for project_id in impact['transitively_affected'][:10]:
                project = self.registry.get_project(project_id)
                if project:
                    report.append(f"- {project.name}")

            if len(impact['transitively_affected']) > 10:
                report.append(f"- ... and {len(impact['transitively_affected']) - 10} more")
            report.append("")

        if impact['recommendations']:
            report.append("## 💡 Recommendations")
            for rec in impact['recommendations']:
                report.append(f"- {rec}")

        return '\n'.join(report)

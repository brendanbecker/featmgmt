#!/usr/bin/env python3
"""
Coordinate releases across multiple projects.
"""

import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import networkx as nx

@dataclass
class Release:
    project_id: str
    version: str
    release_date: str
    dependencies: Dict[str, str]  # project_id -> version
    changes: List[str]
    status: str  # planned, in-progress, completed, failed

class ReleaseCoordinator:
    def __init__(self, registry):
        self.registry = registry
        self.release_plan = []
        self.version_map = {}

    def plan_coordinated_release(self, projects: List[str],
                                release_type: str = "minor") -> Dict:
        """Plan a coordinated release across multiple projects."""
        plan = {
            'release_id': self._generate_release_id(),
            'release_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'projects': [],
            'dependency_order': [],
            'version_bumps': {},
            'risks': [],
            'timeline': []
        }

        # Build dependency graph for involved projects
        dep_graph = self._build_release_dependency_graph(projects)

        # Determine release order
        try:
            release_order = list(nx.topological_sort(dep_graph))
            plan['dependency_order'] = release_order
        except nx.NetworkXError:
            plan['risks'].append("Circular dependencies detected - manual coordination required")
            release_order = projects

        # Plan version bumps
        for project_id in release_order:
            project = self.registry.get_project(project_id)
            if project:
                current_version = project.version or "0.0.0"
                new_version = self._bump_version(current_version, release_type)

                plan['version_bumps'][project_id] = {
                    'project_name': project.name,
                    'current': current_version,
                    'new': new_version,
                    'type': release_type
                }

        # Check for compatibility issues
        compatibility_issues = self._check_version_compatibility(plan['version_bumps'])
        if compatibility_issues:
            plan['risks'].extend(compatibility_issues)

        # Generate timeline
        plan['timeline'] = self._generate_release_timeline(release_order)

        # Add project details
        for project_id in release_order:
            project = self.registry.get_project(project_id)
            if project:
                plan['projects'].append({
                    'id': project_id,
                    'name': project.name,
                    'type': project.type,
                    'path': project.path,
                    'dependencies': project.dependencies
                })

        return plan

    def _generate_release_id(self) -> str:
        """Generate unique release ID."""
        return f"REL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def _build_release_dependency_graph(self, projects: List[str]) -> nx.DiGraph:
        """Build dependency graph for release planning."""
        graph = nx.DiGraph()

        for project_id in projects:
            graph.add_node(project_id)

            # Get dependencies
            cursor = self.registry.conn.cursor()
            cursor.execute('''
                SELECT dependency_id
                FROM dependencies
                WHERE project_id = ? AND dependency_id IN ({})
            '''.format(','.join('?' * len(projects))),
            [project_id] + projects)

            for dep_id, in cursor.fetchall():
                graph.add_edge(dep_id, project_id)  # dep must release before project

        return graph

    def _bump_version(self, current: str, bump_type: str) -> str:
        """Bump version according to semver."""
        # Fallback for non-semver versions
        parts = current.split('.')
        if len(parts) == 3:
            if bump_type == "major":
                return f"{int(parts[0])+1}.0.0"
            elif bump_type == "minor":
                return f"{parts[0]}.{int(parts[1])+1}.0"
            elif bump_type == "patch":
                return f"{parts[0]}.{parts[1]}.{int(parts[2])+1}"
        return current

    def _check_version_compatibility(self, version_bumps: Dict) -> List[str]:
        """Check for version compatibility issues."""
        issues = []

        for project_id, bump_info in version_bumps.items():
            if bump_info['type'] == 'major':
                # Major version bumps may break dependencies
                dependents = self._find_dependents(project_id)
                if dependents:
                    dependent_names = [
                        version_bumps.get(d, {}).get('project_name', d)
                        for d in dependents
                    ]
                    issues.append(
                        f"Major version bump for {bump_info['project_name']} "
                        f"may break: {', '.join(dependent_names)}"
                    )

        return issues

    def _find_dependents(self, project_id: str) -> List[str]:
        """Find projects that depend on given project."""
        cursor = self.registry.conn.cursor()
        cursor.execute('''
            SELECT project_id FROM dependencies WHERE dependency_id = ?
        ''', (project_id,))
        return [row[0] for row in cursor.fetchall()]

    def _generate_release_timeline(self, release_order: List[str]) -> List[Dict]:
        """Generate release timeline."""
        timeline = []
        base_date = datetime.now()

        for i, project_id in enumerate(release_order):
            project = self.registry.get_project(project_id)
            if project:
                # Stagger releases by 2 hours
                release_time = base_date + timedelta(hours=i*2)

                timeline.append({
                    'sequence': i + 1,
                    'project': project.name,
                    'scheduled_time': release_time.isoformat(),
                    'estimated_duration': '30 minutes',
                    'prerequisites': self._get_prerequisites(project_id, release_order[:i])
                })

        return timeline

    def _get_prerequisites(self, project_id: str,
                          completed_projects: List[str]) -> List[str]:
        """Get prerequisites for releasing a project."""
        prerequisites = []

        # Check dependencies
        cursor = self.registry.conn.cursor()
        cursor.execute('''
            SELECT p.name
            FROM dependencies d
            JOIN projects p ON d.dependency_id = p.id
            WHERE d.project_id = ? AND d.dependency_id IN ({})
        '''.format(','.join('?' * len(completed_projects)) if completed_projects else '""'),
        [project_id] + completed_projects)

        for name, in cursor.fetchall():
            prerequisites.append(f"{name} released")

        return prerequisites

    def execute_release(self, release_plan: Dict, dry_run: bool = True) -> Dict:
        """Execute a coordinated release."""
        results = {
            'release_id': release_plan['release_id'],
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'success': True,
            'projects_released': [],
            'failures': []
        }

        for project_info in release_plan['projects']:
            project_id = project_info['id']
            project_name = project_info['name']
            new_version = release_plan['version_bumps'][project_id]['new']

            print(f"📦 Releasing {project_name} v{new_version}...")

            if dry_run:
                print(f"  [DRY RUN] Would release {project_name}")
                results['projects_released'].append({
                    'project': project_name,
                    'version': new_version,
                    'status': 'dry-run'
                })
            else:
                try:
                    # Execute release steps
                    self._execute_project_release(project_id, new_version)

                    results['projects_released'].append({
                        'project': project_name,
                        'version': new_version,
                        'status': 'success'
                    })

                    print(f"  ✅ Successfully released {project_name}")

                except Exception as e:
                    print(f"  ❌ Failed to release {project_name}: {e}")
                    results['failures'].append({
                        'project': project_name,
                        'error': str(e)
                    })
                    results['success'] = False

                    # Decide whether to continue or abort
                    if not self._should_continue_after_failure(project_id, release_plan):
                        print("🛑 Aborting release due to critical failure")
                        break

        results['completed_at'] = datetime.now().isoformat()
        return results

    def _execute_project_release(self, project_id: str, new_version: str):
        """Execute release for a single project."""
        project = self.registry.get_project(project_id)

        if not project:
            raise ValueError(f"Project {project_id} not found")

        project_path = Path(project.path)

        # Update version
        self._update_project_version(project_path, new_version)

        # Run tests
        self._run_release_tests(project_path)

        # Build artifacts
        self._build_release_artifacts(project_path)

        # Tag release
        self._tag_release(project_path, new_version)

        # Push changes
        self._push_release(project_path)

    def _update_project_version(self, project_path: Path, version: str):
        """Update project version in various files."""
        # Update package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
            data['version'] = version
            with open(package_json, 'w') as f:
                json.dump(data, f, indent=2)

        # Update VERSION file
        version_file = project_path / "VERSION"
        version_file.write_text(version)

        # Commit changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=project_path,
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", f"chore: bump version to {version}"],
            cwd=project_path,
            check=True
        )

    def _run_release_tests(self, project_path: Path):
        """Run release tests."""
        result = subprocess.run(
            ["npm", "test"],  # Or appropriate test command
            cwd=project_path,
            capture_output=True
        )

        if result.returncode != 0:
            raise Exception(f"Tests failed: {result.stderr.decode()}")

    def _build_release_artifacts(self, project_path: Path):
        """Build release artifacts."""
        # This would vary by project type
        pass

    def _tag_release(self, project_path: Path, version: str):
        """Create git tag for release."""
        subprocess.run(
            ["git", "tag", f"v{version}"],
            cwd=project_path,
            check=True
        )

    def _push_release(self, project_path: Path):
        """Push release to remote."""
        subprocess.run(
            ["git", "push", "origin", "main", "--tags"],
            cwd=project_path,
            check=True
        )

    def _should_continue_after_failure(self, failed_project: str,
                                      plan: Dict) -> bool:
        """Determine if release should continue after failure."""
        # Check if any remaining projects depend on the failed one
        remaining_projects = [
            p['id'] for p in plan['projects']
            if p['id'] != failed_project
        ]

        for project_id in remaining_projects:
            project = self.registry.get_project(project_id)
            if project and failed_project in [
                self.registry.get_project(name=dep).id
                for dep in project.dependencies
                if self.registry.get_project(name=dep)
            ]:
                return False  # Don't continue if dependencies broken

        return True  # Can continue if no dependencies affected

#!/usr/bin/env python3
"""
Registry and discovery system for featmgmt projects.
"""

import json
import yaml
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import subprocess
import hashlib
import networkx as nx

@dataclass
class Project:
    id: str
    name: str
    path: str
    type: str  # standard, gitops, library, service
    version: str
    dependencies: List[str]
    description: str
    last_updated: str
    status: str  # active, maintenance, deprecated
    metadata: Dict

class ProjectRegistry:
    def __init__(self, registry_path: Path = Path("~/.featmgmt/registry.db").expanduser()):
        self.registry_path = registry_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.registry_path))
        self._initialize_db()
        self.dependency_graph = nx.DiGraph()

    def _initialize_db(self):
        """Initialize registry database."""
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                type TEXT NOT NULL,
                version TEXT,
                description TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT,
                UNIQUE(path)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dependencies (
                project_id TEXT NOT NULL,
                dependency_id TEXT NOT NULL,
                version_constraint TEXT,
                dependency_type TEXT DEFAULT 'runtime',
                PRIMARY KEY (project_id, dependency_id),
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (dependency_id) REFERENCES projects(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_components (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                type TEXT,
                owner_project_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_project_id) REFERENCES projects(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS component_usage (
                component_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                version_used TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (component_id, project_id),
                FOREIGN KEY (component_id) REFERENCES shared_components(id),
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')

        self.conn.commit()

    def discover_projects(self, search_paths: List[Path] = None) -> List[Project]:
        """Discover featmgmt projects in the filesystem."""
        if not search_paths:
            search_paths = [
                Path.home() / "projects",
                Path.home() / "workspace",
                Path("/workspace"),
                Path.cwd()
            ]

        # Handle single Path object
        if isinstance(search_paths, Path):
            search_paths = [search_paths]

        discovered = []

        for search_path in search_paths:
            if not search_path.exists():
                continue

            # Look for feature-management directories
            for fm_dir in search_path.rglob("feature-management"):
                if self._is_valid_featmgmt_project(fm_dir):
                    project = self._analyze_project(fm_dir.parent)
                    if project:
                        discovered.append(project)

        return discovered

    def _is_valid_featmgmt_project(self, fm_dir: Path) -> bool:
        """Check if directory is a valid featmgmt project."""
        required_files = ["OVERPROMPT.md", "README.md"]
        required_dirs = ["bugs", "features"]

        for req_file in required_files:
            if not (fm_dir / req_file).exists():
                return False

        for req_dir in required_dirs:
            if not (fm_dir / req_dir).is_dir():
                return False

        return True

    def _analyze_project(self, project_path: Path) -> Optional[Project]:
        """Analyze a project and extract metadata."""
        try:
            # Read project configuration
            config_file = project_path / "feature-management" / ".agent-config.json"
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
            else:
                config = {}

            # Detect project type
            overprompt = project_path / "feature-management" / "OVERPROMPT.md"
            with open(overprompt) as f:
                overprompt_content = f.read()

            if "gitops" in overprompt_content.lower():
                project_type = "gitops"
            else:
                project_type = "standard"

            # Extract version from package.json, setup.py, etc.
            version = self._extract_version(project_path)

            # Extract dependencies
            dependencies = self._extract_dependencies(project_path)

            # Generate project ID
            project_id = hashlib.md5(str(project_path).encode()).hexdigest()[:12]

            project = Project(
                id=project_id,
                name=project_path.name,
                path=str(project_path),
                type=project_type,
                version=version or "0.0.0",
                dependencies=dependencies,
                description=config.get('description', ''),
                last_updated=datetime.now().isoformat(),
                status="active",
                metadata=config
            )

            return project

        except Exception as e:
            print(f"Error analyzing project {project_path}: {e}")
            return None

    def _extract_version(self, project_path: Path) -> Optional[str]:
        """Extract project version from various sources."""
        # Try package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                return data.get('version')

        # Try setup.py
        setup_py = project_path / "setup.py"
        if setup_py.exists():
            with open(setup_py) as f:
                content = f.read()
                import re
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)

        # Try version file
        version_file = project_path / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()

        return None

    def _extract_dependencies(self, project_path: Path) -> List[str]:
        """Extract project dependencies."""
        dependencies = []

        # Check requirements.txt
        requirements = project_path / "requirements.txt"
        if requirements.exists():
            with open(requirements) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name
                        pkg = line.split('==')[0].split('>=')[0].split('<=')[0]
                        dependencies.append(pkg)

        # Check package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                if 'dependencies' in data:
                    dependencies.extend(data['dependencies'].keys())

        return dependencies

    def register_project(self, project: Project) -> bool:
        """Register a project in the registry."""
        cursor = self.conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO projects
                (id, name, path, type, version, description, last_updated, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project.id,
                project.name,
                project.path,
                project.type,
                project.version,
                project.description,
                project.last_updated,
                project.status,
                json.dumps(project.metadata)
            ))

            # Register dependencies
            for dep in project.dependencies:
                # Check if dependency is another registered project
                cursor.execute('''
                    SELECT id FROM projects WHERE name = ?
                ''', (dep,))

                result = cursor.fetchone()
                if result:
                    dep_id = result[0]
                    cursor.execute('''
                        INSERT OR REPLACE INTO dependencies
                        (project_id, dependency_id, version_constraint)
                        VALUES (?, ?, ?)
                    ''', (project.id, dep_id, "*"))

            self.conn.commit()

            # Update dependency graph
            self.dependency_graph.add_node(project.id)

            return True

        except Exception as e:
            print(f"Error registering project: {e}")
            self.conn.rollback()
            return False

    def add_dependency(self, project_id: str, dependency_id: str,
                      version_constraint: str = "*") -> bool:
        """Add a dependency relationship between projects."""
        cursor = self.conn.cursor()

        try:
            # Verify both projects exist
            cursor.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
            if not cursor.fetchone():
                print(f"Error: Project {project_id} not found")
                return False

            cursor.execute('SELECT id FROM projects WHERE id = ?', (dependency_id,))
            if not cursor.fetchone():
                print(f"Error: Dependency project {dependency_id} not found")
                return False

            # Add dependency
            cursor.execute('''
                INSERT OR REPLACE INTO dependencies
                (project_id, dependency_id, version_constraint)
                VALUES (?, ?, ?)
            ''', (project_id, dependency_id, version_constraint))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error adding dependency: {e}")
            self.conn.rollback()
            return False

    def get_dependencies(self, project_id: str) -> List[Dict]:
        """Get all direct dependencies for a project."""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT d.dependency_id, d.version_constraint, p.name, p.version
            FROM dependencies d
            JOIN projects p ON d.dependency_id = p.id
            WHERE d.project_id = ?
        ''', (project_id,))

        dependencies = []
        for row in cursor.fetchall():
            dependencies.append({
                'dependency_id': row[0],
                'version_constraint': row[1],
                'name': row[2],
                'version': row[3]
            })

        return dependencies

    def get_project(self, project_id: str = None, name: str = None,
                   path: str = None) -> Optional[Dict]:
        """Get project by ID, name, or path. Returns dict representation."""
        cursor = self.conn.cursor()

        if project_id:
            cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        elif name:
            cursor.execute('SELECT * FROM projects WHERE name = ?', (name,))
        elif path:
            cursor.execute('SELECT * FROM projects WHERE path = ?', (path,))
        else:
            return None

        row = cursor.fetchone()

        if row:
            # Get dependencies
            cursor.execute('''
                SELECT p.name
                FROM dependencies d
                JOIN projects p ON d.dependency_id = p.id
                WHERE d.project_id = ?
            ''', (row[0],))

            dependencies = [r[0] for r in cursor.fetchall()]

            project = Project(
                id=row[0],
                name=row[1],
                path=row[2],
                type=row[3],
                version=row[4],
                dependencies=dependencies,
                description=row[5],
                last_updated=row[6],
                status=row[7],
                metadata=json.loads(row[8]) if row[8] else {}
            )

            # Return as dict for API consistency
            return asdict(project)

        return None

    def list_projects(self, status: str = "active") -> List[Project]:
        """List all registered projects."""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT * FROM projects WHERE status = ?
            ORDER BY name
        ''', (status,))

        projects = []
        for row in cursor.fetchall():
            # Get dependencies
            cursor.execute('''
                SELECT p.name
                FROM dependencies d
                JOIN projects p ON d.dependency_id = p.id
                WHERE d.project_id = ?
            ''', (row[0],))

            dependencies = [r[0] for r in cursor.fetchall()]

            project = Project(
                id=row[0],
                name=row[1],
                path=row[2],
                type=row[3],
                version=row[4],
                dependencies=dependencies,
                description=row[5],
                last_updated=row[6],
                status=row[7],
                metadata=json.loads(row[8]) if row[8] else {}
            )
            projects.append(project)

        return projects

    def build_dependency_graph(self) -> nx.DiGraph:
        """Build complete dependency graph of all projects."""
        cursor = self.conn.cursor()

        # Get all projects
        cursor.execute('SELECT id, name FROM projects')
        for project_id, name in cursor.fetchall():
            self.dependency_graph.add_node(project_id, name=name)

        # Get all dependencies
        cursor.execute('SELECT project_id, dependency_id FROM dependencies')
        for project_id, dep_id in cursor.fetchall():
            self.dependency_graph.add_edge(project_id, dep_id)

        return self.dependency_graph

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the project graph."""
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            return cycles
        except:
            return []

    def get_dependency_order(self) -> List[str]:
        """Get projects in dependency order (for building/releasing)."""
        try:
            return list(nx.topological_sort(self.dependency_graph))
        except nx.NetworkXError:
            # Has cycles, return best effort order
            return list(self.dependency_graph.nodes())

class SharedComponentManager:
    """Manage shared components across projects."""

    def __init__(self, registry: ProjectRegistry):
        self.registry = registry

    def register_component(self, name: str, version: str,
                          component_type: str, owner_project_id: str) -> str:
        """Register a shared component."""
        cursor = self.registry.conn.cursor()

        component_id = hashlib.md5(f"{name}:{version}".encode()).hexdigest()[:12]

        cursor.execute('''
            INSERT OR REPLACE INTO shared_components
            (id, name, version, type, owner_project_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (component_id, name, version, component_type, owner_project_id))

        self.registry.conn.commit()

        return component_id

    def track_usage(self, component_id: str, project_id: str, version_used: str):
        """Track component usage by a project."""
        cursor = self.registry.conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO component_usage
            (component_id, project_id, version_used, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (component_id, project_id, version_used))

        self.registry.conn.commit()

    def find_version_mismatches(self) -> List[Dict]:
        """Find components with version mismatches across projects."""
        cursor = self.registry.conn.cursor()

        cursor.execute('''
            SELECT
                sc.name,
                sc.version as latest_version,
                cu.version_used,
                p.name as project_name,
                cu.last_updated
            FROM component_usage cu
            JOIN shared_components sc ON cu.component_id = sc.id
            JOIN projects p ON cu.project_id = p.id
            WHERE cu.version_used != sc.version
            ORDER BY sc.name, p.name
        ''')

        mismatches = []
        for row in cursor.fetchall():
            mismatches.append({
                'component': row[0],
                'latest_version': row[1],
                'used_version': row[2],
                'project': row[3],
                'last_updated': row[4]
            })

        return mismatches

if __name__ == '__main__':
    registry = ProjectRegistry()

    # Discover projects
    print("🔍 Discovering projects...")
    projects = registry.discover_projects()

    for project in projects:
        print(f"Found: {project.name} ({project.type}) at {project.path}")
        registry.register_project(project)

    # Build dependency graph
    graph = registry.build_dependency_graph()

    # Check for circular dependencies
    cycles = registry.find_circular_dependencies()
    if cycles:
        print("⚠️ Circular dependencies detected:")
        for cycle in cycles:
            print(f"  {' -> '.join(cycle)}")

    # Get build order
    order = registry.get_dependency_order()
    print("\n📦 Recommended build order:")
    for i, project_id in enumerate(order, 1):
        project = registry.get_project(project_id)
        if project:
            print(f"  {i}. {project.name}")

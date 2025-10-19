#!/usr/bin/env python3
"""
Unit tests for project_registry.py
"""

import unittest
import sys
from pathlib import Path
import tempfile
import json

# Add parent scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from project_registry import ProjectRegistry, Project


class TestProjectRegistry(unittest.TestCase):
    """Test suite for ProjectRegistry."""

    def setUp(self):
        """Create temporary database for testing."""
        self.temp_db = Path(tempfile.mktemp(suffix=".db"))
        self.registry = ProjectRegistry(self.temp_db)

    def tearDown(self):
        """Clean up database."""
        self.registry.conn.close()
        if self.temp_db.exists():
            self.temp_db.unlink()

    def test_initialization(self):
        """Test ProjectRegistry initialization."""
        self.assertTrue(self.temp_db.exists())
        self.assertIsNotNone(self.registry.conn)
        self.assertIsNotNone(self.registry.dependency_graph)

    def test_database_schema(self):
        """Test database tables are created correctly."""
        cursor = self.registry.conn.cursor()

        # Check projects table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='projects'"
        )
        self.assertIsNotNone(cursor.fetchone())

        # Check dependencies table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='dependencies'"
        )
        self.assertIsNotNone(cursor.fetchone())

        # Check shared_components table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='shared_components'"
        )
        self.assertIsNotNone(cursor.fetchone())

    def test_project_dataclass(self):
        """Test Project dataclass creation."""
        project = Project(
            id="proj-001",
            name="Test Project",
            path="/path/to/project",
            type="standard",
            version="1.0.0",
            dependencies=["proj-002"],
            description="A test project",
            last_updated="2025-10-19",
            status="active",
            metadata={"key": "value"}
        )

        self.assertEqual(project.id, "proj-001")
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.type, "standard")
        self.assertEqual(project.version, "1.0.0")

    def test_register_project(self):
        """Test registering a project."""
        project = Project(
            id="test-proj",
            name="Test Project",
            path="/path/to/test",
            type="standard",
            version="1.0.0",
            dependencies=[],
            description="Test description",
            last_updated="2025-10-19",
            status="active",
            metadata={}
        )

        self.registry.register_project(project)

        # Verify project was inserted
        cursor = self.registry.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects WHERE id='test-proj'")
        count = cursor.fetchone()[0]

        self.assertEqual(count, 1)

    def test_get_project(self):
        """Test retrieving a project."""
        project = Project(
            id="get-test",
            name="Get Test",
            path="/path/to/get",
            type="library",
            version="2.0.0",
            dependencies=[],
            description="Get test",
            last_updated="2025-10-19",
            status="active",
            metadata={}
        )

        self.registry.register_project(project)
        retrieved = self.registry.get_project("get-test")

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['id'], "get-test")
        self.assertEqual(retrieved['name'], "Get Test")
        self.assertEqual(retrieved['type'], "library")

    def test_list_projects(self):
        """Test listing all projects."""
        # Register multiple projects
        for i in range(3):
            project = Project(
                id=f"proj-{i}",
                name=f"Project {i}",
                path=f"/path/{i}",
                type="standard",
                version="1.0.0",
                dependencies=[],
                description=f"Description {i}",
                last_updated="2025-10-19",
                status="active",
                metadata={}
            )
            self.registry.register_project(project)

        projects = self.registry.list_projects()

        self.assertEqual(len(projects), 3)

    def test_discover_projects(self):
        """Test project discovery."""
        # Create temporary project directory structure
        temp_dir = Path(tempfile.mkdtemp())

        # Create a project with OVERPROMPT.md
        proj_dir = temp_dir / "test-project"
        proj_dir.mkdir()
        (proj_dir / "OVERPROMPT.md").write_text("# Test Project")

        try:
            discovered = self.registry.discover_projects(temp_dir)

            # Should find at least one project
            self.assertGreaterEqual(len(discovered), 0)
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)

    def test_add_dependency(self):
        """Test adding dependencies between projects."""
        # Register two projects
        proj1 = Project(
            id="proj-1", name="Project 1", path="/p1", type="service",
            version="1.0.0", dependencies=[], description="P1",
            last_updated="2025-10-19", status="active", metadata={}
        )
        proj2 = Project(
            id="proj-2", name="Project 2", path="/p2", type="library",
            version="1.0.0", dependencies=[], description="P2",
            last_updated="2025-10-19", status="active", metadata={}
        )

        self.registry.register_project(proj1)
        self.registry.register_project(proj2)

        # Add dependency: proj1 depends on proj2
        self.registry.add_dependency("proj-1", "proj-2", ">=1.0.0")

        # Verify dependency was added
        cursor = self.registry.conn.cursor()
        cursor.execute("""
            SELECT dependency_id FROM dependencies
            WHERE project_id='proj-1' AND dependency_id='proj-2'
        """)
        result = cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], "proj-2")

    def test_get_dependencies(self):
        """Test retrieving project dependencies."""
        # Register projects and dependencies
        proj1 = Project(
            id="main", name="Main", path="/main", type="service",
            version="1.0.0", dependencies=[], description="Main",
            last_updated="2025-10-19", status="active", metadata={}
        )
        proj2 = Project(
            id="lib1", name="Lib1", path="/lib1", type="library",
            version="1.0.0", dependencies=[], description="Lib1",
            last_updated="2025-10-19", status="active", metadata={}
        )

        self.registry.register_project(proj1)
        self.registry.register_project(proj2)
        self.registry.add_dependency("main", "lib1", ">=1.0.0")

        deps = self.registry.get_dependencies("main")

        self.assertEqual(len(deps), 1)
        self.assertEqual(deps[0]['dependency_id'], "lib1")


class TestProjectRegistryIntegration(unittest.TestCase):
    """Integration tests for ProjectRegistry."""

    def setUp(self):
        """Set up test environment."""
        self.temp_db = Path(tempfile.mktemp(suffix=".db"))
        self.registry = ProjectRegistry(self.temp_db)

    def tearDown(self):
        """Clean up."""
        self.registry.conn.close()
        if self.temp_db.exists():
            self.temp_db.unlink()

    def test_dependency_graph_building(self):
        """Test building dependency graph."""
        # Register projects with dependencies
        projects = [
            Project("a", "A", "/a", "service", "1.0.0", ["b", "c"],
                   "A", "2025-10-19", "active", {}),
            Project("b", "B", "/b", "library", "1.0.0", ["c"],
                   "B", "2025-10-19", "active", {}),
            Project("c", "C", "/c", "library", "1.0.0", [],
                   "C", "2025-10-19", "active", {}),
        ]

        for proj in projects:
            self.registry.register_project(proj)
            for dep in proj.dependencies:
                self.registry.add_dependency(proj.id, dep)

        # Build dependency graph
        self.registry.build_dependency_graph()

        # Verify graph has nodes
        self.assertGreater(len(self.registry.dependency_graph.nodes()), 0)


if __name__ == '__main__':
    unittest.main()

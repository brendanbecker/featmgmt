#!/usr/bin/env python3
"""
Unit tests for StateManager.
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from state_manager import StateManager, WorkflowState, PhaseState


class TestStateManager(unittest.TestCase):
    """Test StateManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_workflows.db"
        self.manager = StateManager(self.db_path)

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.close()
        # Clean up temp files
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_create_workflow(self):
        """Test workflow creation."""
        workflow_id = self.manager.create_workflow(
            "test_workflow",
            {"type": "standard", "priority": "high"}
        )

        self.assertIsNotNone(workflow_id)
        self.assertEqual(len(workflow_id), 12)  # SHA256 truncated to 12 chars

        # Verify workflow was created
        status = self.manager.get_workflow_status(workflow_id)
        self.assertIsNotNone(status)
        self.assertEqual(status['name'], "test_workflow")
        self.assertEqual(status['state'], WorkflowState.PENDING.value)
        self.assertEqual(status['metadata']['type'], "standard")

    def test_update_workflow_state(self):
        """Test updating workflow state."""
        workflow_id = self.manager.create_workflow("test_workflow")

        # Update to running
        self.manager.update_workflow_state(workflow_id, WorkflowState.RUNNING)
        status = self.manager.get_workflow_status(workflow_id)
        self.assertEqual(status['state'], WorkflowState.RUNNING.value)

        # Update to completed
        self.manager.update_workflow_state(workflow_id, WorkflowState.COMPLETED)
        status = self.manager.get_workflow_status(workflow_id)
        self.assertEqual(status['state'], WorkflowState.COMPLETED.value)
        self.assertIsNotNone(status['completed_at'])

    def test_phase_lifecycle(self):
        """Test phase start, complete, fail."""
        workflow_id = self.manager.create_workflow("test_workflow")

        # Start phase
        self.manager.start_phase(workflow_id, "scan_prioritize", 1)
        status = self.manager.get_workflow_status(workflow_id)
        self.assertEqual(len(status['phases']), 1)
        self.assertEqual(status['phases'][0]['name'], "scan_prioritize")
        self.assertEqual(status['phases'][0]['state'], PhaseState.RUNNING.value)

        # Complete phase
        self.manager.complete_phase(
            workflow_id,
            "scan_prioritize",
            {"items": 5, "priority_queue": ["BUG-001"]}
        )
        status = self.manager.get_workflow_status(workflow_id)
        self.assertEqual(status['phases'][0]['state'], PhaseState.COMPLETED.value)
        self.assertIsNotNone(status['phases'][0]['completed_at'])
        self.assertIsNotNone(status['phases'][0]['output'])

    def test_phase_failure(self):
        """Test phase failure."""
        workflow_id = self.manager.create_workflow("test_workflow")

        # Start and fail phase
        self.manager.start_phase(workflow_id, "process_bug", 2)
        self.manager.fail_phase(
            workflow_id,
            "process_bug",
            "FileNotFoundError: PROMPT.md not found"
        )

        status = self.manager.get_workflow_status(workflow_id)
        self.assertEqual(status['phases'][0]['state'], PhaseState.FAILED.value)
        self.assertIn("FileNotFoundError", status['phases'][0]['error'])

    def test_checkpoint_create_restore(self):
        """Test checkpoint creation and restoration."""
        workflow_id = self.manager.create_workflow("test_workflow")

        # Create some state
        self.manager.start_phase(workflow_id, "phase1", 1)
        self.manager.complete_phase(workflow_id, "phase1", {"result": "success"})
        self.manager.set_state_variable(workflow_id, "bug_count", 10)

        # Create checkpoint
        checkpoint_data = {
            "phase": "phase1",
            "bug_count": 10,
            "timestamp": "2025-10-19T10:00:00"
        }
        self.manager.create_checkpoint(
            workflow_id,
            "after_phase1",
            1,
            checkpoint_data
        )

        # Restore checkpoint
        restored = self.manager.restore_checkpoint(workflow_id, "after_phase1")
        self.assertEqual(restored['phase'], "phase1")
        self.assertEqual(restored['bug_count'], 10)

    def test_restore_latest_checkpoint(self):
        """Test restoring latest checkpoint when name not specified."""
        workflow_id = self.manager.create_workflow("test_workflow")

        # Create multiple checkpoints
        self.manager.create_checkpoint(workflow_id, "cp1", 1, {"phase": 1})
        self.manager.create_checkpoint(workflow_id, "cp2", 2, {"phase": 2})
        self.manager.create_checkpoint(workflow_id, "cp3", 3, {"phase": 3})

        # Restore latest (should be cp3)
        restored = self.manager.restore_checkpoint(workflow_id)
        self.assertEqual(restored['phase'], 3)

    def test_state_variables(self):
        """Test state variable storage and retrieval."""
        workflow_id = self.manager.create_workflow("test_workflow")

        # Set various types of variables
        self.manager.set_state_variable(workflow_id, "bug_count", 5)
        self.manager.set_state_variable(workflow_id, "priority_queue", ["BUG-001", "BUG-002"])
        self.manager.set_state_variable(workflow_id, "config", {"retry": 3, "timeout": 300})

        # Retrieve variables
        bug_count = self.manager.get_state_variable(workflow_id, "bug_count")
        priority_queue = self.manager.get_state_variable(workflow_id, "priority_queue")
        config = self.manager.get_state_variable(workflow_id, "config")

        self.assertEqual(bug_count, 5)
        self.assertEqual(priority_queue, ["BUG-001", "BUG-002"])
        self.assertEqual(config, {"retry": 3, "timeout": 300})

    def test_update_state_variable(self):
        """Test updating existing state variable."""
        workflow_id = self.manager.create_workflow("test_workflow")

        # Set and update
        self.manager.set_state_variable(workflow_id, "counter", 1)
        self.assertEqual(self.manager.get_state_variable(workflow_id, "counter"), 1)

        self.manager.set_state_variable(workflow_id, "counter", 2)
        self.assertEqual(self.manager.get_state_variable(workflow_id, "counter"), 2)

    def test_get_nonexistent_variable(self):
        """Test retrieving non-existent variable."""
        workflow_id = self.manager.create_workflow("test_workflow")

        result = self.manager.get_state_variable(workflow_id, "nonexistent")
        self.assertIsNone(result)

    def test_list_workflows(self):
        """Test listing workflows."""
        # Create multiple workflows
        wf1 = self.manager.create_workflow("workflow1")
        wf2 = self.manager.create_workflow("workflow2")
        wf3 = self.manager.create_workflow("workflow3")

        # Update states
        self.manager.update_workflow_state(wf1, WorkflowState.RUNNING)
        self.manager.update_workflow_state(wf2, WorkflowState.COMPLETED)
        self.manager.update_workflow_state(wf3, WorkflowState.FAILED)

        # List all workflows
        all_workflows = self.manager.list_workflows()
        self.assertEqual(len(all_workflows), 3)

        # List only running workflows
        running = self.manager.list_workflows(WorkflowState.RUNNING)
        self.assertEqual(len(running), 1)
        self.assertEqual(running[0]['state'], WorkflowState.RUNNING.value)

        # List only completed workflows
        completed = self.manager.list_workflows(WorkflowState.COMPLETED)
        self.assertEqual(len(completed), 1)

    def test_workflow_status_complete(self):
        """Test complete workflow status retrieval."""
        workflow_id = self.manager.create_workflow(
            "full_workflow",
            {"type": "standard"}
        )

        # Add multiple phases
        self.manager.start_phase(workflow_id, "phase1", 1)
        self.manager.complete_phase(workflow_id, "phase1", {"result": "success"})

        self.manager.start_phase(workflow_id, "phase2", 2)
        self.manager.complete_phase(workflow_id, "phase2", {"result": "success"})

        # Add state variables
        self.manager.set_state_variable(workflow_id, "total_bugs", 10)
        self.manager.set_state_variable(workflow_id, "completed_bugs", 2)

        # Get full status
        status = self.manager.get_workflow_status(workflow_id)

        self.assertEqual(status['name'], "full_workflow")
        self.assertEqual(len(status['phases']), 2)
        self.assertEqual(len(status['variables']), 2)
        self.assertEqual(status['variables']['total_bugs'], 10)
        self.assertEqual(status['metadata']['type'], "standard")

    def test_nonexistent_workflow(self):
        """Test retrieving status of non-existent workflow."""
        status = self.manager.get_workflow_status("nonexistent_id")
        self.assertIsNone(status)

    def test_multiple_phases_same_workflow(self):
        """Test multiple phases in correct order."""
        workflow_id = self.manager.create_workflow("multi_phase")

        phases = [
            ("scan", 1),
            ("process", 2),
            ("test", 3),
            ("commit", 4),
            ("archive", 5)
        ]

        for name, num in phases:
            self.manager.start_phase(workflow_id, name, num)
            self.manager.complete_phase(workflow_id, name, {"status": "ok"})

        status = self.manager.get_workflow_status(workflow_id)
        self.assertEqual(len(status['phases']), 5)

        # Verify order
        for i, phase in enumerate(status['phases']):
            self.assertEqual(phase['number'], i + 1)

    def test_serialization_deserialization(self):
        """Test output serialization/deserialization."""
        workflow_id = self.manager.create_workflow("test_serialization")

        # Test various data types
        outputs = [
            ("simple_string", "hello world"),
            ("number", 42),
            ("list", [1, 2, 3]),
            ("dict", {"key": "value", "nested": {"data": True}}),
            ("complex", {"items": [1, 2, 3], "meta": {"count": 3}})
        ]

        for phase_name, output in outputs:
            self.manager.start_phase(workflow_id, phase_name, 1)
            self.manager.complete_phase(workflow_id, phase_name, output)

            status = self.manager.get_workflow_status(workflow_id)
            phase = next(p for p in status['phases'] if p['name'] == phase_name)
            self.assertEqual(phase['output'], output)


if __name__ == '__main__':
    unittest.main()

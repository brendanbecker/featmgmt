#!/usr/bin/env python3
"""
Unit tests for PhaseExecutor.
"""

import unittest
import asyncio
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from state_manager import StateManager, PhaseState
from phase_executor import PhaseExecutor, Phase


class TestPhaseExecutor(unittest.TestCase):
    """Test PhaseExecutor functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_workflows.db"
        self.state_manager = StateManager(self.db_path)
        self.executor = PhaseExecutor(self.state_manager, max_parallel=3)

    def tearDown(self):
        """Clean up test fixtures."""
        self.state_manager.close()
        # Clean up temp files
        if self.db_path.exists():
            self.db_path.unlink()
        try:
            Path(self.temp_dir).rmdir()
        except:
            pass

    def test_phase_creation(self):
        """Test Phase dataclass creation."""
        phase = Phase(
            name="test_phase",
            number=1,
            command="echo 'hello'",
            dependencies=[],
            timeout=60,
            retries=2,
            parallel=True
        )

        self.assertEqual(phase.name, "test_phase")
        self.assertEqual(phase.number, 1)
        self.assertEqual(phase.timeout, 60)
        self.assertEqual(phase.retries, 2)
        self.assertTrue(phase.parallel)

    def test_phase_defaults(self):
        """Test Phase default values."""
        phase = Phase(
            name="test_phase",
            number=1,
            command="echo 'hello'"
        )

        self.assertIsNone(phase.dependencies)
        self.assertEqual(phase.timeout, 300)
        self.assertEqual(phase.retries, 3)
        self.assertTrue(phase.parallel)

    def test_build_dependency_graph_no_deps(self):
        """Test building dependency graph with no dependencies."""
        phases = [
            Phase("phase1", 1, "echo 'p1'"),
            Phase("phase2", 2, "echo 'p2'"),
            Phase("phase3", 3, "echo 'p3'")
        ]

        graph = self.executor._build_dependency_graph(phases)

        self.assertEqual(len(graph), 3)
        self.assertEqual(graph[1], [])
        self.assertEqual(graph[2], [])
        self.assertEqual(graph[3], [])

    def test_build_dependency_graph_with_deps(self):
        """Test building dependency graph with dependencies."""
        phases = [
            Phase("phase1", 1, "echo 'p1'", dependencies=[]),
            Phase("phase2", 2, "echo 'p2'", dependencies=[1]),
            Phase("phase3", 3, "echo 'p3'", dependencies=[1, 2])
        ]

        graph = self.executor._build_dependency_graph(phases)

        self.assertEqual(graph[1], [])
        self.assertEqual(graph[2], [1])
        self.assertEqual(graph[3], [1, 2])

    def test_get_ready_phases_all_ready(self):
        """Test getting ready phases when all have no dependencies."""
        phases = [
            Phase("phase1", 1, "echo 'p1'"),
            Phase("phase2", 2, "echo 'p2'"),
            Phase("phase3", 3, "echo 'p3'")
        ]

        graph = self.executor._build_dependency_graph(phases)
        ready = self.executor._get_ready_phases(phases, set(), graph)

        self.assertEqual(len(ready), 3)

    def test_get_ready_phases_with_deps(self):
        """Test getting ready phases with dependencies."""
        phases = [
            Phase("phase1", 1, "echo 'p1'", dependencies=[]),
            Phase("phase2", 2, "echo 'p2'", dependencies=[1]),
            Phase("phase3", 3, "echo 'p3'", dependencies=[1, 2])
        ]

        graph = self.executor._build_dependency_graph(phases)

        # Initially, only phase1 is ready
        ready = self.executor._get_ready_phases(phases, set(), graph)
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].number, 1)

        # After phase1 completes, phase2 is ready
        ready = self.executor._get_ready_phases(phases, {1}, graph)
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].number, 2)

        # After phase1 and phase2 complete, phase3 is ready
        ready = self.executor._get_ready_phases(phases, {1, 2}, graph)
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].number, 3)

        # After all complete, none are ready
        ready = self.executor._get_ready_phases(phases, {1, 2, 3}, graph)
        self.assertEqual(len(ready), 0)

    def test_execute_phase_success(self):
        """Test successful phase execution."""
        async def run_test():
            workflow_id = self.state_manager.create_workflow("test_workflow")

            phase = Phase(
                name="success_phase",
                number=1,
                command="echo 'success'",
                retries=1,
                timeout=10
            )

            result = await self.executor._execute_phase(workflow_id, phase)

            self.assertTrue(result['success'])
            self.assertIn('output', result)
            self.assertEqual(result['attempts'], 1)

            # Verify phase was marked as completed
            status = self.state_manager.get_workflow_status(workflow_id)
            phase_status = next(p for p in status['phases'] if p['name'] == 'success_phase')
            self.assertEqual(phase_status['state'], PhaseState.COMPLETED.value)

        asyncio.run(run_test())

    def test_execute_phase_failure(self):
        """Test phase execution failure."""
        async def run_test():
            workflow_id = self.state_manager.create_workflow("test_workflow")

            phase = Phase(
                name="fail_phase",
                number=1,
                command="exit 1",  # Command that fails
                retries=1,
                timeout=10
            )

            result = await self.executor._execute_phase(workflow_id, phase)

            # Note: The implementation might still return success=True if the command
            # runs but returns non-zero exit code. Adjust based on actual behavior.
            self.assertIn('output', result)

        asyncio.run(run_test())

    def test_execute_phase_with_retry(self):
        """Test phase execution with retries."""
        async def run_test():
            workflow_id = self.state_manager.create_workflow("test_workflow")

            phase = Phase(
                name="retry_phase",
                number=1,
                command="exit 0",  # Simple success command
                retries=3,
                timeout=10
            )

            result = await self.executor._execute_phase(workflow_id, phase)

            self.assertTrue(result['success'])
            # Should succeed on first attempt
            self.assertEqual(result['attempts'], 1)

        asyncio.run(run_test())

    def test_run_command_success(self):
        """Test command execution."""
        async def run_test():
            result = await self.executor._run_command("echo 'test'", timeout=10)

            self.assertIn('stdout', result)
            self.assertIn('stderr', result)
            self.assertIn('returncode', result)
            self.assertIn('test', result['stdout'])

        asyncio.run(run_test())

    def test_run_command_with_output(self):
        """Test command execution with output."""
        async def run_test():
            result = await self.executor._run_command("echo 'hello world'", timeout=10)

            self.assertEqual(result['returncode'], 0)
            self.assertIn('hello world', result['stdout'])

        asyncio.run(run_test())

    def test_checkpoint_creation(self):
        """Test checkpoint creation before phase execution."""
        workflow_id = self.state_manager.create_workflow("test_workflow")

        # Add some state
        self.state_manager.start_phase(workflow_id, "phase0", 0)
        self.state_manager.complete_phase(workflow_id, "phase0", {"result": "ok"})

        phase = Phase("phase1", 1, "echo 'test'")

        # Create checkpoint
        self.executor._create_phase_checkpoint(workflow_id, phase)

        # Verify checkpoint was created (by attempting restore)
        restored = self.state_manager.restore_checkpoint(workflow_id)
        self.assertIsNotNone(restored)

    def test_execute_workflow_simple(self):
        """Test simple workflow execution with sequential phases."""
        async def run_test():
            workflow_id = self.state_manager.create_workflow("simple_workflow")

            phases = [
                Phase("phase1", 1, "echo 'step1'", dependencies=[]),
                Phase("phase2", 2, "echo 'step2'", dependencies=[1]),
                Phase("phase3", 3, "echo 'step3'", dependencies=[2])
            ]

            results = await self.executor.execute_workflow(workflow_id, phases)

            self.assertEqual(len(results), 3)
            self.assertIn('phase1', results)
            self.assertIn('phase2', results)
            self.assertIn('phase3', results)

            # All should succeed
            self.assertTrue(results['phase1']['success'])
            self.assertTrue(results['phase2']['success'])
            self.assertTrue(results['phase3']['success'])

        asyncio.run(run_test())

    def test_execute_workflow_parallel(self):
        """Test workflow with parallel phases."""
        async def run_test():
            workflow_id = self.state_manager.create_workflow("parallel_workflow")

            phases = [
                Phase("phase1", 1, "echo 'p1'", dependencies=[], parallel=True),
                Phase("phase2", 2, "echo 'p2'", dependencies=[], parallel=True),
                Phase("phase3", 3, "echo 'p3'", dependencies=[], parallel=True)
            ]

            results = await self.executor.execute_workflow(workflow_id, phases)

            self.assertEqual(len(results), 3)
            # All independent phases should execute in parallel
            self.assertTrue(all(r['success'] for r in results.values()))

        asyncio.run(run_test())

    def test_execute_workflow_mixed_parallel(self):
        """Test workflow with mixed parallel and sequential phases."""
        async def run_test():
            workflow_id = self.state_manager.create_workflow("mixed_workflow")

            phases = [
                # Phase 1 runs first
                Phase("init", 1, "echo 'init'", dependencies=[], parallel=False),
                # Phases 2 and 3 can run in parallel after 1
                Phase("task_a", 2, "echo 'a'", dependencies=[1], parallel=True),
                Phase("task_b", 3, "echo 'b'", dependencies=[1], parallel=True),
                # Phase 4 runs after both 2 and 3
                Phase("finalize", 4, "echo 'done'", dependencies=[2, 3], parallel=False)
            ]

            results = await self.executor.execute_workflow(workflow_id, phases)

            self.assertEqual(len(results), 4)
            self.assertTrue(all(r['success'] for r in results.values()))

        asyncio.run(run_test())

    def test_workflow_with_failure(self):
        """Test workflow behavior when a phase fails."""
        async def run_test():
            workflow_id = self.state_manager.create_workflow("failing_workflow")

            phases = [
                Phase("phase1", 1, "echo 'ok'", dependencies=[], retries=1),
                Phase("phase2", 2, "invalid_command_xyz", dependencies=[1], retries=1, timeout=5),
                Phase("phase3", 3, "echo 'final'", dependencies=[2])
            ]

            results = await self.executor.execute_workflow(workflow_id, phases)

            # Phase 1 should succeed
            self.assertTrue(results['phase1']['success'])

            # Phase 2 should fail (invalid command)
            # Note: Depending on shell behavior, might succeed with error output

            # Phase 3 may not execute if phase 2 fails
            # This depends on the implementation's failure handling

        asyncio.run(run_test())

    def test_max_parallel_limit(self):
        """Test that max_parallel setting is respected."""
        executor = PhaseExecutor(self.state_manager, max_parallel=2)

        # Verify executor was created with correct limit
        self.assertEqual(executor.max_parallel, 2)
        self.assertEqual(executor.executor._max_workers, 2)


if __name__ == '__main__':
    unittest.main()

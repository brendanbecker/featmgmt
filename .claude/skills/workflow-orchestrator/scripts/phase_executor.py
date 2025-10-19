#!/usr/bin/env python3
"""
Phase execution engine with parallel support.
"""

import asyncio
import concurrent.futures
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import json
import logging
from pathlib import Path
import subprocess
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Phase:
    name: str
    number: int
    command: str
    dependencies: List[int] = None
    timeout: int = 300  # seconds
    retries: int = 3
    parallel: bool = True

class PhaseExecutor:
    def __init__(self, state_manager, max_parallel: int = 3):
        self.state_manager = state_manager
        self.max_parallel = max_parallel
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel)

    async def execute_workflow(self, workflow_id: str, phases: List[Phase]) -> Dict:
        """Execute workflow phases with dependency management."""
        results = {}
        completed_phases = set()

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(phases)

        while len(completed_phases) < len(phases):
            # Find phases ready to execute
            ready_phases = self._get_ready_phases(
                phases, completed_phases, dependency_graph
            )

            if not ready_phases:
                # Deadlock or all phases complete
                break

            # Execute ready phases in parallel
            if len(ready_phases) == 1 or not any(p.parallel for p in ready_phases):
                # Sequential execution
                for phase in ready_phases:
                    result = await self._execute_phase(workflow_id, phase)
                    results[phase.name] = result
                    if result['success']:
                        completed_phases.add(phase.number)
            else:
                # Parallel execution
                tasks = []
                for phase in ready_phases:
                    if phase.parallel:
                        task = asyncio.create_task(
                            self._execute_phase(workflow_id, phase)
                        )
                        tasks.append((phase, task))
                    else:
                        # Execute non-parallel phases sequentially
                        result = await self._execute_phase(workflow_id, phase)
                        results[phase.name] = result
                        if result['success']:
                            completed_phases.add(phase.number)

                # Wait for parallel tasks
                for phase, task in tasks:
                    result = await task
                    results[phase.name] = result
                    if result['success']:
                        completed_phases.add(phase.number)

        return results

    def _build_dependency_graph(self, phases: List[Phase]) -> Dict[int, List[int]]:
        """Build dependency graph from phases."""
        graph = {}

        for phase in phases:
            if phase.dependencies:
                graph[phase.number] = phase.dependencies
            else:
                graph[phase.number] = []

        return graph

    def _get_ready_phases(self, phases: List[Phase],
                         completed: set, graph: Dict) -> List[Phase]:
        """Get phases ready for execution."""
        ready = []

        for phase in phases:
            if phase.number in completed:
                continue

            dependencies = graph.get(phase.number, [])
            if all(dep in completed for dep in dependencies):
                ready.append(phase)

        return ready

    async def _execute_phase(self, workflow_id: str, phase: Phase) -> Dict:
        """Execute a single phase with retry logic."""
        logger.info(f"Executing phase: {phase.name}")

        # Mark phase as started
        self.state_manager.start_phase(workflow_id, phase.name, phase.number)

        attempt = 0
        last_error = None

        while attempt < phase.retries:
            try:
                # Create checkpoint before execution
                self._create_phase_checkpoint(workflow_id, phase)

                # Execute the command
                result = await self._run_command(phase.command, phase.timeout)

                # Mark phase as completed
                self.state_manager.complete_phase(
                    workflow_id, phase.name, result
                )

                logger.info(f"Phase {phase.name} completed successfully")

                return {
                    'success': True,
                    'output': result,
                    'attempts': attempt + 1
                }

            except Exception as e:
                last_error = str(e)
                attempt += 1
                logger.warning(f"Phase {phase.name} failed (attempt {attempt}/{phase.retries}): {e}")

                if attempt < phase.retries:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)

        # Mark phase as failed after all retries
        self.state_manager.fail_phase(workflow_id, phase.name, last_error)

        return {
            'success': False,
            'error': last_error,
            'attempts': attempt
        }

    async def _run_command(self, command: str, timeout: int) -> Dict:
        """Run a command with timeout."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            return {
                'stdout': stdout.decode('utf-8'),
                'stderr': stderr.decode('utf-8'),
                'returncode': process.returncode
            }

        except asyncio.TimeoutError:
            process.kill()
            raise Exception(f"Command timed out after {timeout} seconds")

    def _create_phase_checkpoint(self, workflow_id: str, phase: Phase):
        """Create a checkpoint before phase execution."""
        checkpoint_name = f"phase_{phase.number}_{phase.name}"

        # Get current state
        status = self.state_manager.get_workflow_status(workflow_id)

        # Create checkpoint
        self.state_manager.create_checkpoint(
            workflow_id,
            checkpoint_name,
            phase.number,
            status
        )

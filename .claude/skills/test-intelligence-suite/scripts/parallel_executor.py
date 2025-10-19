#!/usr/bin/env python3
"""
Intelligent parallel test execution with resource management.
"""

import asyncio
import multiprocessing
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import psutil
import yaml

@dataclass
class TestCase:
    name: str
    module: str
    estimated_time: float
    required_resources: Dict[str, int]  # CPU, memory, etc.
    dependencies: List[str]
    priority: int = 0

@dataclass
class TestResult:
    test_name: str
    passed: bool
    execution_time: float
    output: str
    error: Optional[str] = None
    retry_count: int = 0

class ParallelTestExecutor:
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.max_workers = self.config.get('max_workers', multiprocessing.cpu_count())
        self.test_results = []
        self.resource_tracker = ResourceTracker()
        self.test_queue = asyncio.Queue()
        self.running_tests = set()

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load test execution configuration."""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)

        # Default configuration
        return {
            'max_workers': multiprocessing.cpu_count(),
            'timeout_multiplier': 3,
            'retry_failed': True,
            'max_retries': 2,
            'resource_limits': {
                'max_cpu_percent': 80,
                'max_memory_percent': 70
            },
            'test_groups': {
                'unit': {'parallel': True, 'timeout': 60},
                'integration': {'parallel': True, 'timeout': 300},
                'e2e': {'parallel': False, 'timeout': 600}
            }
        }

    async def execute_tests(self, tests: List[TestCase]) -> Dict:
        """Execute tests in parallel with resource management."""
        start_time = time.time()

        # Sort tests by priority and estimated time
        sorted_tests = sorted(tests, key=lambda t: (-t.priority, t.estimated_time))

        # Group tests by dependencies
        test_groups = self._group_by_dependencies(sorted_tests)

        # Initialize workers
        workers = []
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._test_worker(i))
            workers.append(worker)

        # Queue tests
        for group in test_groups:
            for test in group:
                await self.test_queue.put(test)

        # Wait for all tests to complete
        await self.test_queue.join()

        # Cancel workers
        for worker in workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*workers, return_exceptions=True)

        execution_time = time.time() - start_time

        return self._generate_execution_summary(execution_time)

    def _group_by_dependencies(self, tests: List[TestCase]) -> List[List[TestCase]]:
        """Group tests by dependencies for proper execution order."""
        groups = []
        remaining_tests = tests.copy()
        completed_tests = set()

        while remaining_tests:
            current_group = []

            for test in remaining_tests[:]:
                # Check if all dependencies are satisfied
                if all(dep in completed_tests for dep in test.dependencies):
                    current_group.append(test)
                    remaining_tests.remove(test)

            if not current_group:
                # Circular dependency or missing dependency
                print("Warning: Unable to resolve test dependencies")
                current_group = remaining_tests
                remaining_tests = []

            groups.append(current_group)
            completed_tests.update(test.name for test in current_group)

        return groups

    async def _test_worker(self, worker_id: int):
        """Worker to execute tests from the queue."""
        while True:
            try:
                test = await self.test_queue.get()

                # Check resource availability
                await self._wait_for_resources(test)

                # Execute test
                self.running_tests.add(test.name)
                result = await self._execute_single_test(test)
                self.test_results.append(result)

                # Handle failed tests
                if not result.passed and self.config['retry_failed']:
                    if result.retry_count < self.config['max_retries']:
                        # Re-queue for retry
                        test.priority += 10  # Lower priority for retries
                        await self.test_queue.put(test)

                self.running_tests.remove(test.name)
                self.test_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                self.test_queue.task_done()

    async def _wait_for_resources(self, test: TestCase):
        """Wait until resources are available for test execution."""
        while True:
            if self.resource_tracker.can_allocate(test.required_resources):
                self.resource_tracker.allocate(test.required_resources)
                break
            await asyncio.sleep(0.1)

    async def _execute_single_test(self, test: TestCase) -> TestResult:
        """Execute a single test case."""
        start_time = time.time()

        # Determine test runner command
        if test.module.endswith('.py'):
            cmd = f"python -m pytest {test.module}::{test.name} -v"
        else:
            cmd = f"python -m pytest {test.name} -v"

        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            timeout = test.estimated_time * self.config['timeout_multiplier']
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            execution_time = time.time() - start_time
            passed = process.returncode == 0

            return TestResult(
                test_name=test.name,
                passed=passed,
                execution_time=execution_time,
                output=stdout.decode('utf-8'),
                error=stderr.decode('utf-8') if not passed else None
            )

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test.name,
                passed=False,
                execution_time=execution_time,
                output="",
                error=f"Test timed out after {timeout} seconds"
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test.name,
                passed=False,
                execution_time=execution_time,
                output="",
                error=str(e)
            )

        finally:
            # Release resources
            self.resource_tracker.release(test.required_resources)

    def _generate_execution_summary(self, total_time: float) -> Dict:
        """Generate summary of test execution."""
        passed_tests = [r for r in self.test_results if r.passed]
        failed_tests = [r for r in self.test_results if not r.passed]

        summary = {
            'total_tests': len(self.test_results),
            'passed': len(passed_tests),
            'failed': len(failed_tests),
            'pass_rate': len(passed_tests) / len(self.test_results) * 100 if self.test_results else 0,
            'total_time': total_time,
            'average_time': sum(r.execution_time for r in self.test_results) / len(self.test_results) if self.test_results else 0,
            'parallel_efficiency': self._calculate_parallel_efficiency(total_time),
            'failed_tests': [
                {
                    'name': r.test_name,
                    'error': r.error,
                    'execution_time': r.execution_time
                }
                for r in failed_tests
            ]
        }

        return summary

    def _calculate_parallel_efficiency(self, actual_time: float) -> float:
        """Calculate how efficient the parallel execution was."""
        if not self.test_results:
            return 0

        sequential_time = sum(r.execution_time for r in self.test_results)
        theoretical_parallel_time = sequential_time / self.max_workers

        if theoretical_parallel_time > 0:
            efficiency = (theoretical_parallel_time / actual_time) * 100
            return min(100, efficiency)  # Cap at 100%

        return 0

class ResourceTracker:
    """Track and manage system resources for test execution."""

    def __init__(self):
        self.allocated_cpu = 0
        self.allocated_memory = 0
        self.max_cpu = psutil.cpu_count() * 100
        self.max_memory = psutil.virtual_memory().total

    def can_allocate(self, resources: Dict[str, int]) -> bool:
        """Check if resources can be allocated."""
        required_cpu = resources.get('cpu', 10)
        required_memory = resources.get('memory', 100 * 1024 * 1024)  # 100MB default

        current_cpu = psutil.cpu_percent()
        current_memory = psutil.virtual_memory().percent

        if current_cpu + required_cpu > 80:  # 80% CPU limit
            return False

        if current_memory + (required_memory / self.max_memory * 100) > 70:  # 70% memory limit
            return False

        return True

    def allocate(self, resources: Dict[str, int]):
        """Allocate resources."""
        self.allocated_cpu += resources.get('cpu', 10)
        self.allocated_memory += resources.get('memory', 100 * 1024 * 1024)

    def release(self, resources: Dict[str, int]):
        """Release allocated resources."""
        self.allocated_cpu -= resources.get('cpu', 10)
        self.allocated_memory -= resources.get('memory', 100 * 1024 * 1024)

        # Ensure non-negative
        self.allocated_cpu = max(0, self.allocated_cpu)
        self.allocated_memory = max(0, self.allocated_memory)

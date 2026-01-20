#!/usr/bin/env python3
"""Monitor files for inquiry research completion.

This module provides file-based monitoring for the inquiry-collector skill.
It watches the research/ directory for agent output files and detects
completion markers.
"""

import os
import re
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    from .utils import (
        ensure_research_dir,
        estimate_content_completeness,
        get_timestamp,
        has_completion_marker,
        logger,
        print_progress,
        print_warning,
    )
except ImportError:
    from utils import (
        ensure_research_dir,
        estimate_content_completeness,
        get_timestamp,
        has_completion_marker,
        logger,
        print_progress,
        print_warning,
    )


class FileStatus(Enum):
    """Status of a research file."""

    NOT_FOUND = "not_found"
    PARTIAL = "partial"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class ResearchFile:
    """Information about a research output file."""

    path: Path
    agent_number: int
    status: FileStatus = FileStatus.NOT_FOUND
    content: str = ""
    last_modified: Optional[float] = None
    error: Optional[str] = None


class FileMonitor:
    """Monitor research/ directory for agent output files.

    Supports two modes:
    1. Existing files: Check for files already present
    2. Watch mode: Wait for files to be created/completed

    Completion is detected by:
    - Presence of completion markers (## Conclusion, ---END---)
    - File not modified for a configurable period (stable)
    - Content completeness heuristics
    """

    # File naming patterns
    FILE_PATTERNS = [
        r"agent[_-]?(\d+)\.md",
        r"research[_-]?(\d+)\.md",
        r"report[_-]?(\d+)\.md",
    ]

    def __init__(
        self,
        inquiry_path: Path,
        expected_agents: int,
        timeout: int = 300,
        stable_seconds: int = 60,
    ):
        """Initialize file monitor.

        Args:
            inquiry_path: Path to inquiry directory
            expected_agents: Number of expected research agents
            timeout: Timeout in seconds for agent completion
            stable_seconds: Seconds of no modification to consider file stable
        """
        self.inquiry_path = Path(inquiry_path)
        self.research_dir = ensure_research_dir(self.inquiry_path)
        self.expected_agents = expected_agents
        self.timeout = timeout
        self.stable_seconds = stable_seconds
        self.files: list[ResearchFile] = []

    def scan_existing(self) -> list[ResearchFile]:
        """Scan research/ directory for existing files.

        Returns list of found ResearchFile objects.
        """
        self.files = []

        if not self.research_dir.exists():
            return self.files

        for item in self.research_dir.iterdir():
            if not item.is_file() or not item.suffix == ".md":
                continue

            agent_num = self._extract_agent_number(item.name)
            if agent_num is None:
                continue

            research_file = ResearchFile(
                path=item,
                agent_number=agent_num,
            )

            self._read_and_check_file(research_file)
            self.files.append(research_file)

        self.files.sort(key=lambda f: f.agent_number)
        return self.files

    def _extract_agent_number(self, filename: str) -> Optional[int]:
        """Extract agent number from filename."""
        for pattern in self.FILE_PATTERNS:
            match = re.match(pattern, filename, re.IGNORECASE)
            if match:
                return int(match.group(1))

        # Try generic number extraction
        match = re.search(r"(\d+)", filename)
        if match:
            return int(match.group(1))

        return None

    def _read_and_check_file(self, research_file: ResearchFile) -> None:
        """Read file content and check completion status."""
        try:
            research_file.content = research_file.path.read_text()
            research_file.last_modified = research_file.path.stat().st_mtime

            # Check for completion
            if has_completion_marker(research_file.content):
                research_file.status = FileStatus.COMPLETE
            elif self._is_file_stable(research_file):
                # File hasn't changed and has reasonable content
                if estimate_content_completeness(research_file.content) > 0.5:
                    research_file.status = FileStatus.COMPLETE
                else:
                    research_file.status = FileStatus.PARTIAL
            else:
                research_file.status = FileStatus.PARTIAL

        except Exception as e:
            research_file.status = FileStatus.ERROR
            research_file.error = str(e)
            logger.error(f"Error reading {research_file.path}: {e}")

    def _is_file_stable(self, research_file: ResearchFile) -> bool:
        """Check if file hasn't been modified recently."""
        if research_file.last_modified is None:
            return False

        age = time.time() - research_file.last_modified
        return age > self.stable_seconds

    def wait_for_completion(self, poll_interval: float = 5.0) -> list[ResearchFile]:
        """Wait for all expected agent files to be complete.

        Args:
            poll_interval: Seconds between directory checks

        Returns:
            List of ResearchFile objects (complete or timed out)
        """
        start_time = time.time()

        print_progress(f"Waiting for {self.expected_agents} research files...")

        while True:
            self.scan_existing()

            # Check if all expected files are complete
            complete_count = sum(
                1 for f in self.files if f.status == FileStatus.COMPLETE
            )

            elapsed = time.time() - start_time
            print_progress(
                f"\rProgress: {complete_count}/{self.expected_agents} complete "
                f"({elapsed:.0f}s elapsed)",
                end="",
            )

            if complete_count >= self.expected_agents:
                print_progress("")  # Newline
                return self.files

            # Check timeout
            if elapsed > self.timeout:
                print_progress("")  # Newline
                print_warning(f"Timeout after {self.timeout}s")
                return self.files

            time.sleep(poll_interval)

    def get_missing_agents(self) -> list[int]:
        """Get list of agent numbers without files."""
        found_nums = {f.agent_number for f in self.files}
        return [
            i for i in range(1, self.expected_agents + 1)
            if i not in found_nums
        ]

    def get_incomplete_agents(self) -> list[int]:
        """Get list of agent numbers that haven't completed."""
        complete_nums = {
            f.agent_number
            for f in self.files
            if f.status == FileStatus.COMPLETE
        }

        return [
            i for i in range(1, self.expected_agents + 1)
            if i not in complete_nums
        ]

    def all_complete(self) -> bool:
        """Check if all expected agents have completed."""
        if len(self.files) < self.expected_agents:
            return False

        return all(
            f.status == FileStatus.COMPLETE
            for f in self.files[:self.expected_agents]
        )

    def get_completion_summary(self) -> dict:
        """Get summary of file completion status."""
        complete = [f for f in self.files if f.status == FileStatus.COMPLETE]
        partial = [f for f in self.files if f.status == FileStatus.PARTIAL]
        errors = [f for f in self.files if f.status == FileStatus.ERROR]

        return {
            "expected": self.expected_agents,
            "found": len(self.files),
            "complete": len(complete),
            "partial": len(partial),
            "errors": len(errors),
            "missing_agents": self.get_missing_agents(),
            "incomplete_agents": self.get_incomplete_agents(),
        }


def check_files(
    inquiry_path: Path,
    expected_agents: int,
) -> tuple[list[ResearchFile], dict]:
    """Quick check of existing files without waiting.

    Returns:
        Tuple of (files, summary)
    """
    monitor = FileMonitor(inquiry_path, expected_agents)
    files = monitor.scan_existing()
    summary = monitor.get_completion_summary()
    return files, summary


def wait_for_files(
    inquiry_path: Path,
    expected_agents: int,
    timeout: int = 300,
    poll_interval: float = 5.0,
) -> tuple[list[ResearchFile], dict]:
    """Wait for files to be complete.

    Returns:
        Tuple of (files, summary)
    """
    monitor = FileMonitor(inquiry_path, expected_agents, timeout=timeout)
    files = monitor.wait_for_completion(poll_interval=poll_interval)
    summary = monitor.get_completion_summary()
    return files, summary

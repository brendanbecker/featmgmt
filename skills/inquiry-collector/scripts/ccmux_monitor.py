#!/usr/bin/env python3
"""Monitor ccmux sessions for inquiry research completion.

This module provides ccmux session monitoring for the inquiry-collector skill.
It uses ccmux MCP tools to track agent sessions and extract their output.

Note: This module is designed to be called from within a Claude Code session
where ccmux MCP tools are available. For standalone testing, use the mock
functions or file_monitor.py instead.
"""

import json
import re
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    from .utils import (
        get_timestamp,
        has_completion_marker,
        logger,
        print_progress,
        print_warning,
    )
except ImportError:
    from utils import (
        get_timestamp,
        has_completion_marker,
        logger,
        print_progress,
        print_warning,
    )


class AgentStatus(Enum):
    """Status of a research agent."""

    PENDING = "pending"
    WORKING = "working"
    COMPLETE = "complete"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class AgentSession:
    """Information about an agent's ccmux session."""

    session_id: str
    pane_id: str
    agent_number: int
    status: AgentStatus = AgentStatus.PENDING
    output: str = ""
    error: Optional[str] = None


class CcmuxMonitor:
    """Monitor ccmux sessions for research agent completion.

    This class provides methods to find, monitor, and extract output from
    ccmux sessions tagged with an inquiry ID.

    In a Claude Code context, the actual MCP tool calls would be made by
    the assistant. This class provides the logic and data structures.
    """

    def __init__(self, inquiry_id: str, expected_agents: int, timeout: int = 300):
        """Initialize monitor.

        Args:
            inquiry_id: The inquiry ID (e.g., INQ-001)
            expected_agents: Number of expected research agents
            timeout: Timeout in seconds for agent completion
        """
        self.inquiry_id = inquiry_id.upper()
        self.expected_agents = expected_agents
        self.timeout = timeout
        self.sessions: list[AgentSession] = []

    def find_sessions_command(self) -> str:
        """Generate command to find sessions tagged with inquiry.

        Returns MCP tool call parameters as JSON for ccmux_list_panes.
        """
        return json.dumps({"session": None})  # List all sessions

    def parse_sessions_response(self, response: dict) -> list[AgentSession]:
        """Parse ccmux_list_panes response to find inquiry sessions.

        Args:
            response: Response from ccmux_list_panes

        Returns:
            List of AgentSession objects for matching sessions
        """
        sessions = []

        panes = response.get("panes", [])
        for pane in panes:
            tags = pane.get("tags", [])

            # Check if this pane is tagged for our inquiry
            if self._matches_inquiry_tag(tags):
                agent_num = self._extract_agent_number(tags, pane.get("name", ""))

                session = AgentSession(
                    session_id=pane.get("session_id", ""),
                    pane_id=pane.get("pane_id", ""),
                    agent_number=agent_num,
                    status=self._map_status(pane.get("status", "")),
                )
                sessions.append(session)

        self.sessions = sorted(sessions, key=lambda s: s.agent_number)
        return self.sessions

    def _matches_inquiry_tag(self, tags: list[str]) -> bool:
        """Check if tags include this inquiry's tag."""
        for tag in tags:
            tag_upper = tag.upper()
            if self.inquiry_id in tag_upper or tag_upper == self.inquiry_id:
                return True
        return False

    def _extract_agent_number(self, tags: list[str], name: str) -> int:
        """Extract agent number from tags or name.

        Looks for patterns like:
        - agent-1, agent-2
        - research-1, research-2
        - INQ-001-agent-1
        """
        # Check tags first
        for tag in tags:
            match = re.search(r"(?:agent|research)[_-]?(\d+)", tag, re.IGNORECASE)
            if match:
                return int(match.group(1))

        # Check name
        match = re.search(r"(?:agent|research)[_-]?(\d+)", name, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Default to next available number
        return len(self.sessions) + 1

    def _map_status(self, ccmux_status: str) -> AgentStatus:
        """Map ccmux status to AgentStatus."""
        status_map = {
            "complete": AgentStatus.COMPLETE,
            "idle": AgentStatus.COMPLETE,
            "working": AgentStatus.WORKING,
            "waiting_for_input": AgentStatus.WORKING,
            "blocked": AgentStatus.PENDING,
            "error": AgentStatus.ERROR,
        }
        return status_map.get(ccmux_status.lower(), AgentStatus.PENDING)

    def get_pane_output_command(self, pane_id: str, lines: int = 2000) -> str:
        """Generate command to read pane output.

        Returns MCP tool call parameters as JSON for ccmux_read_pane.
        """
        return json.dumps({"pane_id": pane_id, "lines": lines})

    def parse_pane_output(self, response: dict, session: AgentSession) -> str:
        """Parse ccmux_read_pane response.

        Args:
            response: Response from ccmux_read_pane
            session: AgentSession to update

        Returns:
            Output content
        """
        output = response.get("output", response.get("content", ""))
        session.output = output

        # Check for completion marker in output
        if has_completion_marker(output):
            session.status = AgentStatus.COMPLETE

        return output

    def get_status_command(self, pane_id: str) -> str:
        """Generate command to get pane status.

        Returns MCP tool call parameters as JSON for ccmux_get_status.
        """
        return json.dumps({"pane_id": pane_id})

    def parse_status_response(self, response: dict, session: AgentSession) -> AgentStatus:
        """Parse ccmux_get_status response.

        Args:
            response: Response from ccmux_get_status
            session: AgentSession to update

        Returns:
            Updated status
        """
        status_str = response.get("status", "").lower()
        session.status = self._map_status(status_str)
        return session.status

    def all_complete(self) -> bool:
        """Check if all expected agents have completed."""
        if len(self.sessions) < self.expected_agents:
            return False

        return all(
            s.status == AgentStatus.COMPLETE
            for s in self.sessions[:self.expected_agents]
        )

    def get_incomplete_agents(self) -> list[int]:
        """Get list of agent numbers that haven't completed."""
        complete_nums = {
            s.agent_number
            for s in self.sessions
            if s.status == AgentStatus.COMPLETE
        }

        return [
            i for i in range(1, self.expected_agents + 1)
            if i not in complete_nums
        ]

    def get_completion_summary(self) -> dict:
        """Get summary of agent completion status."""
        complete = [s for s in self.sessions if s.status == AgentStatus.COMPLETE]
        pending = [s for s in self.sessions if s.status == AgentStatus.PENDING]
        working = [s for s in self.sessions if s.status == AgentStatus.WORKING]
        errors = [s for s in self.sessions if s.status == AgentStatus.ERROR]

        return {
            "expected": self.expected_agents,
            "found": len(self.sessions),
            "complete": len(complete),
            "pending": len(pending),
            "working": len(working),
            "errors": len(errors),
            "incomplete_agents": self.get_incomplete_agents(),
        }


def create_monitor_instructions(
    inquiry_id: str,
    expected_agents: int,
    timeout: int = 300,
) -> str:
    """Generate instructions for monitoring via Claude Code.

    Since ccmux tools are MCP tools called by Claude, this generates
    the instruction text for the monitoring workflow.
    """
    return f"""
## ccmux Monitoring Instructions for {inquiry_id}

To collect research outputs from ccmux sessions:

### 1. Find Sessions

Use `ccmux_list_panes` to find sessions tagged with "{inquiry_id}":

```
Expected to find {expected_agents} sessions tagged with "{inquiry_id}" or "agent-N"
```

### 2. Check Status

For each found session, use `ccmux_get_status` with the pane_id.

Look for status: "complete" or "idle"

### 3. Extract Output

For complete sessions, use `ccmux_read_pane` with:
- pane_id: [from step 1]
- lines: 2000

### 4. Timeout Handling

If agents don't complete within {timeout} seconds:
- Mark as timeout
- Generate partial report
- Note incomplete agents in summary

### 5. Completion

All {expected_agents} agents must reach "complete" or "idle" status,
OR the output must contain a completion marker (## Conclusion, ## Summary).
"""

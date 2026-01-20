#!/usr/bin/env python3
"""Shared utilities for inquiry-collector skill."""

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def find_inquiry_path(inquiry_id: str, base_path: Optional[Path] = None) -> Optional[Path]:
    """Find the inquiry directory by ID.

    Searches for directories matching INQ-XXX pattern in:
    1. Provided base_path
    2. ./inquiries/
    3. ./feature-management/inquiries/
    """
    if base_path is None:
        base_path = Path.cwd()

    # Normalize inquiry ID format
    if not inquiry_id.upper().startswith("INQ-"):
        inquiry_id = f"INQ-{inquiry_id}"
    inquiry_id = inquiry_id.upper()

    # Search paths in order of preference
    search_paths = [
        base_path / "inquiries",
        base_path / "feature-management" / "inquiries",
        base_path,
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Look for directory starting with inquiry_id
        for item in search_path.iterdir():
            if item.is_dir() and item.name.upper().startswith(inquiry_id):
                return item

    return None


def load_inquiry_report(inquiry_path: Path) -> dict[str, Any]:
    """Load and parse inquiry_report.json."""
    report_path = inquiry_path / "inquiry_report.json"

    if not report_path.exists():
        raise FileNotFoundError(f"inquiry_report.json not found in {inquiry_path}")

    with open(report_path) as f:
        return json.load(f)


def save_inquiry_report(inquiry_path: Path, report: dict[str, Any]) -> None:
    """Save inquiry_report.json with proper formatting."""
    report_path = inquiry_path / "inquiry_report.json"

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
        f.write("\n")


def update_inquiry_phase(
    inquiry_path: Path,
    new_phase: str,
    notes: Optional[str] = None,
) -> dict[str, Any]:
    """Update inquiry phase and add to history.

    Args:
        inquiry_path: Path to inquiry directory
        new_phase: New phase value
        notes: Optional notes for the transition

    Returns:
        Updated inquiry report
    """
    report = load_inquiry_report(inquiry_path)

    today = datetime.now().strftime("%Y-%m-%d")

    # Add to phase history
    if "phase_history" not in report:
        report["phase_history"] = []

    history_entry = {
        "phase": new_phase,
        "entered_date": today,
    }
    if notes:
        history_entry["notes"] = notes

    report["phase_history"].append(history_entry)

    # Update current phase and status
    report["phase"] = new_phase
    report["status"] = new_phase
    report["updated_date"] = today

    save_inquiry_report(inquiry_path, report)
    return report


def ensure_research_dir(inquiry_path: Path) -> Path:
    """Ensure research/ directory exists."""
    research_dir = inquiry_path / "research"
    research_dir.mkdir(exist_ok=True)
    return research_dir


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date() -> str:
    """Get current date in ISO format."""
    return datetime.now().strftime("%Y-%m-%d")


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def parse_markdown_sections(content: str) -> dict[str, str]:
    """Parse markdown content into sections by heading.

    Returns dict mapping heading text to section content.
    """
    sections = {}
    current_heading = None
    current_content = []

    for line in content.split("\n"):
        # Check for heading (## or ###)
        heading_match = re.match(r"^#{1,3}\s+(.+)$", line)

        if heading_match:
            # Save previous section
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_content).strip()

            current_heading = heading_match.group(1).strip()
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_heading is not None:
        sections[current_heading] = "\n".join(current_content).strip()

    return sections


def has_completion_marker(content: str) -> bool:
    """Check if content has a completion marker.

    Markers:
    - ## Conclusion section
    - ## Summary section
    - ---END--- marker
    """
    content_lower = content.lower()

    markers = [
        r"^##\s+conclusion",
        r"^##\s+summary",
        r"---end---",
        r"\*\*completed\*\*",
    ]

    for marker in markers:
        if re.search(marker, content_lower, re.MULTILINE):
            return True

    return False


def estimate_content_completeness(content: str) -> float:
    """Estimate how complete a research report is (0.0 to 1.0).

    Checks for presence of expected sections.
    """
    expected_sections = [
        "problem",
        "approach",
        "evidence",
        "finding",
        "recommendation",
        "conclusion",
    ]

    content_lower = content.lower()
    found = sum(1 for section in expected_sections if section in content_lower)

    return found / len(expected_sections)


def print_progress(message: str, end: str = "\n") -> None:
    """Print progress message to stdout."""
    print(message, end=end, flush=True)


def print_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"ERROR: {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print warning message to stderr."""
    print(f"WARNING: {message}", file=sys.stderr)

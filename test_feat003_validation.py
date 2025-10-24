#!/usr/bin/env python3
"""
Test validation script for FEAT-003: work-item-creation-agent
This script validates agent definition files for:
- File integrity and existence
- Markdown structure and syntax
- Required sections presence
- JSON code block syntax (allowing template placeholders)
- Cross-references and consistency
- Integration point documentation
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Tuple, Dict, Set

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors: List[str] = []
        self.warnings_list: List[str] = []

    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"{GREEN}✓{RESET} {test_name}")

    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"{RED}✗{RESET} {test_name}")
        print(f"  {RED}{error}{RESET}")

    def add_warning(self, test_name: str, warning: str):
        self.warnings += 1
        self.warnings_list.append(f"{test_name}: {warning}")
        print(f"{YELLOW}⚠{RESET} {test_name}")
        print(f"  {YELLOW}{warning}{RESET}")

    def print_summary(self):
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.passed + self.failed + self.warnings}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"{YELLOW}Warnings: {self.warnings}{RESET}")

        if self.failed > 0:
            print(f"\n{RED}FAILURES:{RESET}")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings > 0:
            print(f"\n{YELLOW}WARNINGS:{RESET}")
            for warning in self.warnings_list:
                print(f"  - {warning}")

        return self.failed == 0


def test_file_exists(file_path: Path, results: TestResult):
    """Test that a file exists and is readable"""
    test_name = f"File exists: {file_path.name}"
    if not file_path.exists():
        results.add_fail(test_name, f"File not found: {file_path}")
        return False
    if not file_path.is_file():
        results.add_fail(test_name, f"Path is not a file: {file_path}")
        return False
    results.add_pass(test_name)
    return True


def test_file_not_empty(file_path: Path, results: TestResult):
    """Test that a file is not empty"""
    test_name = f"File not empty: {file_path.name}"
    try:
        content = file_path.read_text()
        if len(content.strip()) == 0:
            results.add_fail(test_name, "File is empty")
            return False
        results.add_pass(test_name)
        return True
    except Exception as e:
        results.add_fail(test_name, f"Error reading file: {e}")
        return False


def test_markdown_structure(file_path: Path, results: TestResult):
    """Test basic markdown structure"""
    test_name = f"Markdown structure: {file_path.name}"
    try:
        content = file_path.read_text()

        # Check for H1 header (title)
        if not re.search(r'^# .+', content, re.MULTILINE):
            results.add_fail(test_name, "Missing H1 header (# title)")
            return False

        # Check for H2 headers (sections)
        h2_headers = re.findall(r'^## .+', content, re.MULTILINE)
        if len(h2_headers) < 3:
            results.add_warning(test_name, f"Only {len(h2_headers)} H2 sections found (expected at least 3)")

        results.add_pass(test_name)
        return True
    except Exception as e:
        results.add_fail(test_name, f"Error analyzing markdown: {e}")
        return False


def extract_json_blocks(content: str) -> List[Tuple[str, int]]:
    """Extract JSON code blocks with line numbers"""
    json_blocks = []
    lines = content.split('\n')
    in_json_block = False
    current_block = []
    block_start_line = 0

    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```json'):
            in_json_block = True
            current_block = []
            block_start_line = i
        elif line.strip() == '```' and in_json_block:
            in_json_block = False
            if current_block:
                json_blocks.append(('\n'.join(current_block), block_start_line))
        elif in_json_block:
            current_block.append(line)

    return json_blocks


def is_template_json(json_str: str) -> bool:
    """Check if JSON block contains template placeholders"""
    template_patterns = [
        r'\{[a-zA-Z_]+\}',  # {variable}
        r'\{[a-zA-Z_]+\.[a-zA-Z_]+\}',  # {metadata.field}
        r'//\s*',  # JSON comments
        r'\.\.\.',  # Ellipsis
        r'Type-specific fields:',
        r'For bugs:',
        r'For features:',
        r'For human_actions:',
    ]

    for pattern in template_patterns:
        if re.search(pattern, json_str):
            return True
    return False


def test_json_blocks_structure(file_path: Path, results: TestResult):
    """Test that JSON code blocks have valid structure (allowing templates)"""
    test_name = f"JSON structure: {file_path.name}"
    try:
        content = file_path.read_text()
        json_blocks = extract_json_blocks(content)

        if len(json_blocks) == 0:
            results.add_warning(test_name, "No JSON code blocks found")
            return True

        template_blocks = 0
        valid_blocks = 0
        invalid_blocks = []

        for i, (block, line_num) in enumerate(json_blocks, 1):
            # Check if it's a template
            if is_template_json(block):
                template_blocks += 1
                continue

            # Try to parse as actual JSON
            try:
                json.loads(block)
                valid_blocks += 1
            except json.JSONDecodeError as e:
                # Check if it looks like it should be valid JSON
                if not is_template_json(block):
                    invalid_blocks.append((i, line_num, str(e)))

        if invalid_blocks:
            for block_num, line_num, error in invalid_blocks:
                results.add_warning(f"{test_name} (block {block_num} at line {line_num})",
                                   f"Potentially invalid JSON: {error}")
        else:
            results.add_pass(f"{test_name} ({template_blocks} templates, {valid_blocks} valid)")

        return len(invalid_blocks) == 0
    except Exception as e:
        results.add_fail(test_name, f"Error checking JSON blocks: {e}")
        return False


def test_required_sections(file_path: Path, required_sections: List[str], results: TestResult):
    """Test that required sections are present"""
    test_name = f"Required sections: {file_path.name}"
    try:
        content = file_path.read_text()
        missing_sections = []

        for section in required_sections:
            # Look for H2 or H3 headers
            pattern = rf'^##[#]? {re.escape(section)}'
            if not re.search(pattern, content, re.MULTILINE):
                missing_sections.append(section)

        if missing_sections:
            results.add_fail(test_name, f"Missing sections: {', '.join(missing_sections)}")
            return False

        results.add_pass(test_name)
        return True
    except Exception as e:
        results.add_fail(test_name, f"Error checking sections: {e}")
        return False


def test_cross_references(file_path: Path, referenced_items: List[str], results: TestResult):
    """Test that cross-referenced items exist"""
    test_name = f"Cross-references: {file_path.name}"
    try:
        content = file_path.read_text()
        missing_refs = []

        for ref in referenced_items:
            if ref not in content:
                missing_refs.append(ref)

        if missing_refs:
            results.add_warning(test_name, f"Missing references: {', '.join(missing_refs)}")
            return False

        results.add_pass(test_name)
        return True
    except Exception as e:
        results.add_fail(test_name, f"Error checking references: {e}")
        return False


def test_work_item_creation_agent(base_path: Path, results: TestResult):
    """Test work-item-creation-agent.md"""
    print(f"\n{BLUE}Testing work-item-creation-agent.md{RESET}")
    print("-" * 80)

    file_path = base_path / "claude-agents/shared/work-item-creation-agent.md"

    # Basic file tests
    if not test_file_exists(file_path, results):
        return
    if not test_file_not_empty(file_path, results):
        return

    # Structure tests
    test_markdown_structure(file_path, results)
    test_json_blocks_structure(file_path, results)

    # Required sections
    required_sections = [
        "Purpose",
        "Capabilities",
        "Input Format",
        "Processing Steps",
        "Output Format",
        "Error Handling",
        "Integration Points"
    ]
    test_required_sections(file_path, required_sections, results)

    # Cross-references
    cross_refs = [
        "test-runner-agent",
        "retrospective-agent",
        "bug_report.json",
        "feature_request.json",
        "action_report.json",
        "PROMPT.md",
        "INSTRUCTIONS.md"
    ]
    test_cross_references(file_path, cross_refs, results)


def test_test_runner_agent_updates(base_path: Path, results: TestResult):
    """Test test-runner-agent.md updates"""
    print(f"\n{BLUE}Testing test-runner-agent.md updates{RESET}")
    print("-" * 80)

    file_path = base_path / "claude-agents/standard/test-runner-agent.md"

    # Basic file tests
    if not test_file_exists(file_path, results):
        return
    if not test_file_not_empty(file_path, results):
        return

    # Check for delegation to work-item-creation-agent
    test_name = "Delegates to work-item-creation-agent"
    try:
        content = file_path.read_text()

        if "work-item-creation-agent" not in content:
            results.add_fail(test_name, "No mention of work-item-creation-agent")
            return

        if "Delegated to work-item-creation-agent" not in content:
            results.add_warning(test_name, "Missing delegation section header")

        # Check for Task tool invocation example
        if "Subagent: work-item-creation-agent" not in content:
            results.add_fail(test_name, "Missing Task tool invocation example")
            return

        results.add_pass(test_name)
    except Exception as e:
        results.add_fail(test_name, f"Error checking delegation: {e}")


def test_retrospective_agent_updates(base_path: Path, results: TestResult):
    """Test retrospective-agent.md updates"""
    print(f"\n{BLUE}Testing retrospective-agent.md updates{RESET}")
    print("-" * 80)

    file_path = base_path / "claude-agents/shared/retrospective-agent.md"

    # Basic file tests
    if not test_file_exists(file_path, results):
        return
    if not test_file_not_empty(file_path, results):
        return

    # Check for delegation to work-item-creation-agent
    test_name = "Delegates to work-item-creation-agent"
    try:
        content = file_path.read_text()

        if "work-item-creation-agent" not in content:
            results.add_fail(test_name, "No mention of work-item-creation-agent")
            return

        # Check for bug creation workflow
        if "Bug Creation Workflow (Delegated to work-item-creation-agent)" not in content:
            results.add_fail(test_name, "Missing bug creation delegation section")
            return

        # Check for feature creation workflow
        if "Feature Creation Workflow (Delegated to work-item-creation-agent)" not in content:
            results.add_fail(test_name, "Missing feature creation delegation section")
            return

        # Check for Task tool invocation examples
        invocations = re.findall(r'Subagent: work-item-creation-agent', content)
        if len(invocations) < 2:
            results.add_warning(test_name, f"Only {len(invocations)} invocation examples (expected at least 2)")

        results.add_pass(test_name)
    except Exception as e:
        results.add_fail(test_name, f"Error checking delegation: {e}")


def test_sync_agents_script(base_path: Path, results: TestResult):
    """Test sync-agents.sh will sync work-item-creation-agent"""
    print(f"\n{BLUE}Testing sync-agents.sh script{RESET}")
    print("-" * 80)

    file_path = base_path / "scripts/sync-agents.sh"

    # Basic file tests
    if not test_file_exists(file_path, results):
        return
    if not test_file_not_empty(file_path, results):
        return

    test_name = "sync-agents.sh will sync work-item-creation-agent"
    try:
        content = file_path.read_text()

        # Check that script uses auto-discovery pattern
        if "claude-agents/shared" in content and "*.md" in content:
            # Verify the actual file exists
            agent_file = base_path / "claude-agents/shared/work-item-creation-agent.md"
            if agent_file.exists():
                results.add_pass(test_name + " (auto-discovery)")
            else:
                results.add_fail(test_name, "work-item-creation-agent.md not found in claude-agents/shared/")
        else:
            # Fallback: check if explicitly mentioned
            if "work-item-creation-agent" in content:
                results.add_pass(test_name)
            else:
                results.add_fail(test_name, "Script doesn't use auto-discovery and doesn't mention work-item-creation-agent")
    except Exception as e:
        results.add_fail(test_name, f"Error checking sync-agents.sh: {e}")


def test_feature_metadata(base_path: Path, results: TestResult):
    """Test FEAT-003 metadata and completion status"""
    print(f"\n{BLUE}Testing FEAT-003 metadata{RESET}")
    print("-" * 80)

    file_path = base_path / "feature-management/features/FEAT-003-work-item-creation-agent/feature_request.json"

    # Basic file tests
    if not test_file_exists(file_path, results):
        return
    if not test_file_not_empty(file_path, results):
        return

    test_name = "FEAT-003 metadata valid"
    try:
        content = file_path.read_text()
        metadata = json.loads(content)

        # Check required fields
        required_fields = ["feature_id", "title", "component", "priority", "status"]
        missing = [f for f in required_fields if f not in metadata]
        if missing:
            results.add_fail(test_name, f"Missing fields: {', '.join(missing)}")
            return

        # Check feature_id
        if metadata.get("feature_id") != "FEAT-003":
            results.add_fail(test_name, f"Invalid feature_id: {metadata.get('feature_id')}")
            return

        # Check status
        if metadata.get("status") != "completed":
            results.add_warning(test_name, f"Status is '{metadata.get('status')}', expected 'completed'")

        # Check component
        if metadata.get("component") != "agents/shared":
            results.add_warning(test_name, f"Component is '{metadata.get('component')}', expected 'agents/shared'")

        results.add_pass(test_name)
    except json.JSONDecodeError as e:
        results.add_fail(test_name, f"Invalid JSON: {e}")
    except Exception as e:
        results.add_fail(test_name, f"Error checking metadata: {e}")


def test_file_sizes(base_path: Path, results: TestResult):
    """Test that agent files are substantial (not stubs)"""
    print(f"\n{BLUE}Testing file sizes and completeness{RESET}")
    print("-" * 80)

    files_to_check = [
        ("claude-agents/shared/work-item-creation-agent.md", 20000),  # At least 20KB
        ("claude-agents/standard/test-runner-agent.md", 15000),  # At least 15KB
        ("claude-agents/shared/retrospective-agent.md", 30000),  # At least 30KB
    ]

    for file_path_str, min_size in files_to_check:
        file_path = base_path / file_path_str
        test_name = f"File size adequate: {file_path.name}"

        if not file_path.exists():
            results.add_fail(test_name, f"File not found")
            continue

        size = file_path.stat().st_size
        if size < min_size:
            results.add_warning(test_name, f"File is {size} bytes (expected at least {min_size})")
        else:
            results.add_pass(f"{test_name} ({size} bytes)")


def main():
    print(f"{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}FEAT-003 Test Validation Suite{RESET}")
    print(f"{BLUE}Testing: work-item-creation-agent and related updates{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}")

    # Determine base path
    base_path = Path(__file__).parent.resolve()
    print(f"Base path: {base_path}\n")

    results = TestResult()

    # Run all tests
    test_work_item_creation_agent(base_path, results)
    test_test_runner_agent_updates(base_path, results)
    test_retrospective_agent_updates(base_path, results)
    test_sync_agents_script(base_path, results)
    test_feature_metadata(base_path, results)
    test_file_sizes(base_path, results)

    # Print summary
    success = results.print_summary()

    print(f"\n{BLUE}{'=' * 80}{RESET}")
    if success:
        print(f"{GREEN}✓ All tests passed!{RESET}")
        print(f"{GREEN}FEAT-003 implementation is valid and complete.{RESET}")
    else:
        print(f"{RED}✗ Some tests failed.{RESET}")
        print(f"{YELLOW}Please review failures and fix issues.{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

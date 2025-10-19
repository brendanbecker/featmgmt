#!/usr/bin/env python3
"""
Intelligent commit message generation from code changes.
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import ast
import json

class CommitGenerator:
    def __init__(self, repo_path: Path = Path(".")):
        self.repo_path = repo_path
        self.conventional_types = {
            'feat': 'A new feature',
            'fix': 'A bug fix',
            'docs': 'Documentation only changes',
            'style': 'Formatting, missing semicolons, etc',
            'refactor': 'Code change that neither fixes a bug nor adds a feature',
            'perf': 'Code change that improves performance',
            'test': 'Adding missing tests',
            'chore': 'Maintain. Changes to build process, auxiliary tools, libraries',
            'ci': 'CI related changes',
            'revert': 'Revert to a commit'
        }

    def generate_commit_message(self, staged: bool = True) -> str:
        """Generate commit message from changes."""
        # Get diff
        diff = self._get_diff(staged)

        if not diff:
            return "chore: minor updates"

        # Analyze changes
        analysis = self._analyze_diff(diff)

        # Determine commit type
        commit_type = self._determine_commit_type(analysis)

        # Generate scope
        scope = self._determine_scope(analysis)

        # Generate description
        description = self._generate_description(analysis)

        # Generate body
        body = self._generate_body(analysis)

        # Format as conventional commit
        message = f"{commit_type}"
        if scope:
            message += f"({scope})"
        message += f": {description}"

        if body:
            message += f"\n\n{body}"

        # Add footer if there are breaking changes
        if analysis.get('breaking_changes'):
            message += f"\n\nBREAKING CHANGE: {analysis['breaking_changes']}"

        return message

    def _get_diff(self, staged: bool) -> str:
        """Get git diff."""
        cmd = ["git", "diff"]
        if staged:
            cmd.append("--cached")

        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        return result.stdout

    def _analyze_diff(self, diff: str) -> Dict:
        """Analyze diff to understand changes."""
        analysis = {
            'files_changed': [],
            'additions': 0,
            'deletions': 0,
            'changes_by_type': {},
            'functions_modified': [],
            'classes_modified': [],
            'imports_changed': [],
            'tests_added': False,
            'docs_updated': False,
            'config_changed': False,
            'breaking_changes': None
        }

        current_file = None
        file_additions = []
        file_deletions = []

        for line in diff.split('\n'):
            # New file
            if line.startswith('diff --git'):
                if current_file and (file_additions or file_deletions):
                    self._analyze_file_changes(
                        current_file, file_additions, file_deletions, analysis
                    )

                match = re.search(r'b/(.+)', line)
                if match:
                    current_file = match.group(1)
                    analysis['files_changed'].append(current_file)
                    file_additions = []
                    file_deletions = []

            # Added line
            elif line.startswith('+') and not line.startswith('+++'):
                file_additions.append(line[1:])
                analysis['additions'] += 1

            # Deleted line
            elif line.startswith('-') and not line.startswith('---'):
                file_deletions.append(line[1:])
                analysis['deletions'] += 1

        # Analyze last file
        if current_file and (file_additions or file_deletions):
            self._analyze_file_changes(
                current_file, file_additions, file_deletions, analysis
            )

        return analysis

    def _analyze_file_changes(self, filename: str, additions: List[str],
                             deletions: List[str], analysis: Dict):
        """Analyze changes in a specific file."""
        # Detect file type
        file_type = self._detect_file_type(filename)

        if file_type not in analysis['changes_by_type']:
            analysis['changes_by_type'][file_type] = {'files': 0, 'changes': 0}

        analysis['changes_by_type'][file_type]['files'] += 1
        analysis['changes_by_type'][file_type]['changes'] += len(additions) + len(deletions)

        # Check for specific patterns
        if 'test' in filename.lower() or 'spec' in filename.lower():
            analysis['tests_added'] = True

        if filename.endswith(('.md', '.rst', '.txt')):
            analysis['docs_updated'] = True

        if filename.endswith(('.yml', '.yaml', '.json', '.toml', '.ini', '.cfg')):
            analysis['config_changed'] = True

        # Analyze code changes
        if file_type == 'python':
            self._analyze_python_changes(additions, deletions, analysis)
        elif file_type == 'javascript':
            self._analyze_js_changes(additions, deletions, analysis)

        # Check for breaking changes
        for line in deletions:
            if 'def ' in line or 'class ' in line or 'function ' in line:
                # API change detected
                if not analysis['breaking_changes']:
                    analysis['breaking_changes'] = "API changes detected"

    def _detect_file_type(self, filename: str) -> str:
        """Detect file type from filename."""
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab'
        }

        for ext, lang in extensions.items():
            if filename.endswith(ext):
                return lang

        return 'other'

    def _analyze_python_changes(self, additions: List[str],
                               deletions: List[str], analysis: Dict):
        """Analyze Python-specific changes."""
        for line in additions:
            # Function definitions
            if re.match(r'\s*def\s+(\w+)', line):
                match = re.search(r'def\s+(\w+)', line)
                if match:
                    analysis['functions_modified'].append(match.group(1))

            # Class definitions
            elif re.match(r'\s*class\s+(\w+)', line):
                match = re.search(r'class\s+(\w+)', line)
                if match:
                    analysis['classes_modified'].append(match.group(1))

            # Import statements
            elif line.strip().startswith(('import ', 'from ')):
                analysis['imports_changed'].append(line.strip())

    def _analyze_js_changes(self, additions: List[str],
                           deletions: List[str], analysis: Dict):
        """Analyze JavaScript-specific changes."""
        for line in additions:
            # Function definitions
            if 'function ' in line or '=>' in line:
                match = re.search(r'function\s+(\w+)|const\s+(\w+)\s*=.*=>', line)
                if match:
                    func_name = match.group(1) or match.group(2)
                    if func_name:
                        analysis['functions_modified'].append(func_name)

            # Class definitions
            elif re.match(r'\s*class\s+(\w+)', line):
                match = re.search(r'class\s+(\w+)', line)
                if match:
                    analysis['classes_modified'].append(match.group(1))

            # Import statements
            elif line.strip().startswith(('import ', 'const ', 'let ', 'var ')) and 'require' in line:
                analysis['imports_changed'].append(line.strip())

    def _determine_commit_type(self, analysis: Dict) -> str:
        """Determine the conventional commit type."""
        # Priority order for determining type
        if analysis.get('breaking_changes'):
            return 'feat!'  # Breaking change
        elif analysis['tests_added'] and not analysis['changes_by_type'].get('python'):
            return 'test'
        elif analysis['docs_updated'] and len(analysis['files_changed']) == 1:
            return 'docs'
        elif 'fix' in ' '.join(analysis['functions_modified']).lower():
            return 'fix'
        elif analysis['functions_modified'] or analysis['classes_modified']:
            # Check if it's a refactor (similar lines added/deleted)
            if abs(analysis['additions'] - analysis['deletions']) < 10:
                return 'refactor'
            else:
                return 'feat'
        elif analysis['config_changed']:
            return 'chore'
        else:
            return 'chore'

    def _determine_scope(self, analysis: Dict) -> Optional[str]:
        """Determine the scope of changes."""
        if len(analysis['files_changed']) == 0:
            return None

        # If all changes in same directory
        directories = set()
        for file in analysis['files_changed']:
            parts = Path(file).parts
            if len(parts) > 1:
                directories.add(parts[0])

        if len(directories) == 1:
            return list(directories)[0]

        # If changes focused on specific type
        if analysis['tests_added']:
            return 'test'
        elif analysis['docs_updated']:
            return 'docs'

        return None

    def _generate_description(self, analysis: Dict) -> str:
        """Generate commit description."""
        descriptions = []

        # Based on what was modified
        if analysis['classes_modified']:
            if len(analysis['classes_modified']) == 1:
                descriptions.append(f"update {analysis['classes_modified'][0]} class")
            else:
                descriptions.append(f"update {len(analysis['classes_modified'])} classes")

        if analysis['functions_modified']:
            if len(analysis['functions_modified']) == 1:
                descriptions.append(f"modify {analysis['functions_modified'][0]} function")
            else:
                descriptions.append(f"modify {len(analysis['functions_modified'])} functions")

        if analysis['tests_added']:
            descriptions.append("add tests")

        if analysis['docs_updated']:
            descriptions.append("update documentation")

        if analysis['config_changed']:
            descriptions.append("update configuration")

        if descriptions:
            return ' and '.join(descriptions[:2])  # Limit to 2 items

        # Fallback
        return f"update {len(analysis['files_changed'])} files"

    def _generate_body(self, analysis: Dict) -> str:
        """Generate commit body with details."""
        body_parts = []

        # List modified files by type
        if len(analysis['files_changed']) > 3:
            body_parts.append("Modified files:")
            for file_type, info in analysis['changes_by_type'].items():
                body_parts.append(f"- {file_type}: {info['files']} files")

        # List specific changes
        if analysis['functions_modified']:
            body_parts.append(f"\nFunctions: {', '.join(analysis['functions_modified'][:5])}")

        if analysis['classes_modified']:
            body_parts.append(f"Classes: {', '.join(analysis['classes_modified'])}")

        # Statistics
        if analysis['additions'] + analysis['deletions'] > 50:
            body_parts.append(f"\n+{analysis['additions']} -{analysis['deletions']}")

        return '\n'.join(body_parts) if body_parts else ""

    def validate_commit_message(self, message: str) -> Tuple[bool, List[str]]:
        """Validate a commit message against conventional commit format."""
        errors = []

        lines = message.split('\n')
        if not lines:
            errors.append("Empty commit message")
            return False, errors

        header = lines[0]

        # Check header length
        if len(header) > 72:
            errors.append(f"Header too long ({len(header)} > 72 characters)")

        # Check conventional format
        pattern = r'^(feat|fix|docs|style|refactor|perf|test|chore|ci|revert)(\(.+\))?!?: .+'
        if not re.match(pattern, header):
            errors.append("Header doesn't follow conventional commit format")

        # Check body (if present)
        if len(lines) > 2:
            if lines[1] != '':
                errors.append("Missing blank line between header and body")

            for i, line in enumerate(lines[2:], 2):
                if len(line) > 80:
                    errors.append(f"Line {i+1} too long ({len(line)} > 80 characters)")

        return len(errors) == 0, errors

if __name__ == '__main__':
    generator = CommitGenerator()

    # Generate commit message
    message = generator.generate_commit_message()
    print("Generated commit message:")
    print("=" * 50)
    print(message)
    print("=" * 50)

    # Validate
    valid, errors = generator.validate_commit_message(message)
    if valid:
        print("✅ Commit message is valid")
    else:
        print("❌ Validation errors:")
        for error in errors:
            print(f"  - {error}")

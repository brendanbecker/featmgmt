#!/usr/bin/env python3
"""
Intelligent git conflict resolution system.
"""

import re
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from enum import Enum
import difflib
import ast

class ConflictType(Enum):
    WHITESPACE = "whitespace"
    IMPORTS = "imports"
    VERSION = "version"
    COMMENT = "comment"
    SIMPLE_CODE = "simple_code"
    COMPLEX_CODE = "complex_code"
    BINARY = "binary"

class ConflictResolver:
    def __init__(self, repo_path: Path = Path(".")):
        self.repo_path = repo_path
        self.conflict_patterns = {
            ConflictType.WHITESPACE: r'^[\s\t]*',
            ConflictType.IMPORTS: r'^(import|from .* import)',
            ConflictType.VERSION: r'["\']?\d+\.\d+\.\d+["\']?',
            ConflictType.COMMENT: r'^\s*(#|//|/\*|\*)',
        }

    def detect_conflicts(self) -> List[Dict]:
        """Detect all merge conflicts in the repository."""
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        conflicted_files = result.stdout.strip().split('\n') if result.stdout else []
        conflicts = []

        for file_path in conflicted_files:
            if file_path:
                conflict_info = self.analyze_conflict(Path(file_path))
                conflicts.append(conflict_info)

        return conflicts

    def analyze_conflict(self, file_path: Path) -> Dict:
        """Analyze a single conflicted file."""
        full_path = self.repo_path / file_path

        with open(full_path, 'r') as f:
            content = f.read()

        # Parse conflict markers
        conflicts = self._parse_conflict_markers(content)

        # Classify each conflict
        classified_conflicts = []
        for conflict in conflicts:
            conflict_type = self._classify_conflict(conflict)
            classified_conflicts.append({
                'type': conflict_type,
                'ours': conflict['ours'],
                'theirs': conflict['theirs'],
                'base': conflict.get('base'),
                'auto_resolvable': self._is_auto_resolvable(conflict_type)
            })

        return {
            'file': str(file_path),
            'conflicts': classified_conflicts,
            'total_conflicts': len(conflicts),
            'auto_resolvable': all(c['auto_resolvable'] for c in classified_conflicts),
            'file_type': file_path.suffix
        }

    def _parse_conflict_markers(self, content: str) -> List[Dict]:
        """Parse git conflict markers from file content."""
        conflicts = []
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            if lines[i].startswith('<<<<<<<'):
                # Found conflict start
                conflict = {'start': i}
                ours_lines = []
                theirs_lines = []
                base_lines = []

                i += 1
                # Collect "ours" section
                while i < len(lines) and not lines[i].startswith('|||||||') and not lines[i].startswith('======='):
                    ours_lines.append(lines[i])
                    i += 1

                # Check for base section (3-way merge)
                if i < len(lines) and lines[i].startswith('|||||||'):
                    i += 1
                    while i < len(lines) and not lines[i].startswith('======='):
                        base_lines.append(lines[i])
                        i += 1

                # Skip ======= marker
                if i < len(lines) and lines[i].startswith('======='):
                    i += 1

                # Collect "theirs" section
                while i < len(lines) and not lines[i].startswith('>>>>>>>'):
                    theirs_lines.append(lines[i])
                    i += 1

                conflict['end'] = i
                conflict['ours'] = '\n'.join(ours_lines)
                conflict['theirs'] = '\n'.join(theirs_lines)
                if base_lines:
                    conflict['base'] = '\n'.join(base_lines)

                conflicts.append(conflict)

            i += 1

        return conflicts

    def _classify_conflict(self, conflict: Dict) -> ConflictType:
        """Classify the type of conflict."""
        ours = conflict['ours'].strip()
        theirs = conflict['theirs'].strip()

        # Check for whitespace-only differences
        if ours.replace(' ', '').replace('\t', '') == theirs.replace(' ', '').replace('\t', ''):
            return ConflictType.WHITESPACE

        # Check for import conflicts
        if all(re.match(self.conflict_patterns[ConflictType.IMPORTS], line.strip())
               for line in ours.split('\n') + theirs.split('\n') if line.strip()):
            return ConflictType.IMPORTS

        # Check for version conflicts
        if re.search(self.conflict_patterns[ConflictType.VERSION], ours) and \
           re.search(self.conflict_patterns[ConflictType.VERSION], theirs):
            return ConflictType.VERSION

        # Check for comment-only conflicts
        if all(re.match(self.conflict_patterns[ConflictType.COMMENT], line.strip())
               for line in ours.split('\n') + theirs.split('\n') if line.strip()):
            return ConflictType.COMMENT

        # Analyze code complexity
        if self._is_simple_code_conflict(ours, theirs):
            return ConflictType.SIMPLE_CODE

        return ConflictType.COMPLEX_CODE

    def _is_simple_code_conflict(self, ours: str, theirs: str) -> bool:
        """Determine if a code conflict is simple enough for auto-resolution."""
        # Simple heuristics for now
        ours_lines = ours.split('\n')
        theirs_lines = theirs.split('\n')

        # If conflict is just a single line change
        if len(ours_lines) <= 2 and len(theirs_lines) <= 2:
            return True

        # If changes don't overlap (additions in different places)
        diff = difflib.unified_diff(ours_lines, theirs_lines, lineterm='')
        diff_lines = list(diff)
        if len(diff_lines) < 10:  # Small diff
            return True

        return False

    def _is_auto_resolvable(self, conflict_type: ConflictType) -> bool:
        """Check if a conflict type can be automatically resolved."""
        return conflict_type in [
            ConflictType.WHITESPACE,
            ConflictType.IMPORTS,
            ConflictType.VERSION,
            ConflictType.COMMENT,
            ConflictType.SIMPLE_CODE
        ]

    def resolve_conflicts(self, file_path: Path, strategy: str = "auto") -> bool:
        """Resolve conflicts in a file."""
        conflict_info = self.analyze_conflict(file_path)

        if strategy == "auto" and not conflict_info['auto_resolvable']:
            print(f"Cannot auto-resolve conflicts in {file_path}")
            return False

        full_path = self.repo_path / file_path
        with open(full_path, 'r') as f:
            content = f.read()

        resolved_content = content

        for conflict in conflict_info['conflicts']:
            if conflict['auto_resolvable']:
                resolution = self._resolve_single_conflict(conflict)
                if resolution:
                    # Replace conflict with resolution
                    conflict_pattern = r'<<<<<<<.*?>>>>>>>.*?\n'
                    resolved_content = re.sub(
                        conflict_pattern,
                        resolution + '\n',
                        resolved_content,
                        count=1,
                        flags=re.DOTALL
                    )

        # Write resolved content
        with open(full_path, 'w') as f:
            f.write(resolved_content)

        # Stage the resolved file
        subprocess.run(["git", "add", str(file_path)], cwd=self.repo_path)

        return True

    def _resolve_single_conflict(self, conflict: Dict) -> Optional[str]:
        """Resolve a single conflict based on its type."""
        conflict_type = conflict['type']
        ours = conflict['ours']
        theirs = conflict['theirs']

        if conflict_type == ConflictType.WHITESPACE:
            # Prefer properly formatted version
            return ours if ours.count('    ') > theirs.count('\t') else theirs

        elif conflict_type == ConflictType.IMPORTS:
            # Merge and sort imports
            return self._merge_imports(ours, theirs)

        elif conflict_type == ConflictType.VERSION:
            # Use higher semantic version
            return self._resolve_version_conflict(ours, theirs)

        elif conflict_type == ConflictType.COMMENT:
            # Merge comments
            return f"{ours}\n{theirs}" if ours != theirs else ours

        elif conflict_type == ConflictType.SIMPLE_CODE:
            # For simple conflicts, prefer the newer change
            # In real implementation, would use more sophisticated logic
            return theirs  # Prefer incoming changes for now

        return None

    def _merge_imports(self, ours: str, theirs: str) -> str:
        """Merge and sort import statements."""
        imports = set()

        for line in ours.split('\n'):
            if line.strip():
                imports.add(line.strip())

        for line in theirs.split('\n'):
            if line.strip():
                imports.add(line.strip())

        # Sort imports (stdlib, third-party, local)
        sorted_imports = sorted(imports, key=lambda x: (
            not x.startswith('import'),
            'from .' in x,
            x
        ))

        return '\n'.join(sorted_imports)

    def _resolve_version_conflict(self, ours: str, theirs: str) -> str:
        """Resolve version conflicts using semantic versioning."""
        import re

        def extract_version(text):
            match = re.search(r'(\d+)\.(\d+)\.(\d+)', text)
            if match:
                return tuple(map(int, match.groups()))
            return (0, 0, 0)

        our_version = extract_version(ours)
        their_version = extract_version(theirs)

        # Use the higher version
        if their_version > our_version:
            return theirs
        return ours

    def create_conflict_report(self, conflicts: List[Dict]) -> str:
        """Create a detailed conflict resolution report."""
        report = ["# Conflict Resolution Report\n"]
        report.append(f"Total files with conflicts: {len(conflicts)}\n")

        auto_resolvable = sum(1 for c in conflicts if c['auto_resolvable'])
        report.append(f"Auto-resolvable: {auto_resolvable}/{len(conflicts)}\n")

        report.append("\n## Conflict Details\n")

        for conflict_info in conflicts:
            report.append(f"\n### {conflict_info['file']}")
            report.append(f"- Total conflicts: {conflict_info['total_conflicts']}")
            report.append(f"- Auto-resolvable: {'Yes' if conflict_info['auto_resolvable'] else 'No'}")

            report.append("\nConflict types:")
            for conflict in conflict_info['conflicts']:
                status = "✅" if conflict['auto_resolvable'] else "❌"
                report.append(f"  {status} {conflict['type'].value}")

        return '\n'.join(report)

if __name__ == '__main__':
    resolver = ConflictResolver()

    # Detect conflicts
    conflicts = resolver.detect_conflicts()

    if conflicts:
        print("Conflicts detected:")
        for conflict in conflicts:
            print(f"  - {conflict['file']}: {conflict['total_conflicts']} conflicts")

        # Generate report
        report = resolver.create_conflict_report(conflicts)
        print("\n" + report)

        # Attempt auto-resolution
        for conflict in conflicts:
            if conflict['auto_resolvable']:
                if resolver.resolve_conflicts(Path(conflict['file'])):
                    print(f"✅ Auto-resolved: {conflict['file']}")
                else:
                    print(f"❌ Failed to resolve: {conflict['file']}")
    else:
        print("No conflicts detected")

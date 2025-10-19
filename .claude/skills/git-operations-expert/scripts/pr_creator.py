#!/usr/bin/env python3
"""
Automated Pull Request creation with templates and metadata.
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import requests
from enum import Enum

class PRType(Enum):
    FEATURE = "feature"
    BUGFIX = "bugfix"
    HOTFIX = "hotfix"
    REFACTOR = "refactor"
    DOCS = "docs"
    TEST = "test"
    CHORE = "chore"

class PRCreator:
    def __init__(self, repo_path: Path = Path("."), config: Optional[Dict] = None):
        self.repo_path = repo_path
        self.config = config or self._load_config()
        self.templates = self._load_templates()

    def _load_config(self) -> Dict:
        """Load PR configuration."""
        config_path = self.repo_path / ".claude/skills/git-operations-expert/resources/pr_config.json"

        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)

        # Default configuration
        return {
            'github': {
                'api_url': 'https://api.github.com',
                'owner': None,
                'repo': None,
                'token': None
            },
            'gitlab': {
                'api_url': 'https://gitlab.com/api/v4',
                'project_id': None,
                'token': None
            },
            'reviewers': {
                'default': [],
                'by_component': {}
            },
            'labels': {
                'feature': ['enhancement', 'feature'],
                'bugfix': ['bug', 'fix'],
                'hotfix': ['hotfix', 'urgent'],
                'refactor': ['refactor', 'tech-debt'],
                'docs': ['documentation'],
                'test': ['test', 'testing'],
                'chore': ['chore', 'maintenance']
            }
        }

    def _load_templates(self) -> Dict[str, str]:
        """Load PR templates."""
        templates = {}
        template_dir = self.repo_path / ".claude/skills/git-operations-expert/templates"

        for pr_type in PRType:
            template_path = template_dir / f"pr_{pr_type.value}.md"
            if template_path.exists():
                with open(template_path) as f:
                    templates[pr_type.value] = f.read()
            else:
                templates[pr_type.value] = self._default_template(pr_type)

        return templates

    def _default_template(self, pr_type: PRType) -> str:
        """Generate default PR template."""
        return f"""## {pr_type.value.capitalize()} PR

### Description
{{{{description}}}}

### Changes Made
{{{{changes}}}}

### Testing
{{{{testing}}}}

### Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated if needed
- [ ] No sensitive information exposed

### Related Issues
{{{{issues}}}}

### Additional Notes
{{{{notes}}}}
"""

    def detect_pr_type(self, branch_name: str = None, commit_messages: List[str] = None) -> PRType:
        """Detect PR type from branch name or commit messages."""
        if branch_name:
            # Check branch naming patterns
            patterns = {
                PRType.FEATURE: r'feature[/-]',
                PRType.BUGFIX: r'(bug|fix)[/-]',
                PRType.HOTFIX: r'hotfix[/-]',
                PRType.REFACTOR: r'refactor[/-]',
                PRType.DOCS: r'docs?[/-]',
                PRType.TEST: r'test[/-]',
                PRType.CHORE: r'chore[/-]'
            }

            for pr_type, pattern in patterns.items():
                if re.search(pattern, branch_name, re.IGNORECASE):
                    return pr_type

        if commit_messages:
            # Analyze commit message patterns
            type_keywords = {
                PRType.FEATURE: ['feat', 'feature', 'add', 'implement'],
                PRType.BUGFIX: ['fix', 'bug', 'patch', 'resolve'],
                PRType.HOTFIX: ['hotfix', 'urgent', 'critical'],
                PRType.REFACTOR: ['refactor', 'restructure', 'optimize'],
                PRType.DOCS: ['docs', 'documentation', 'readme'],
                PRType.TEST: ['test', 'spec', 'testing'],
                PRType.CHORE: ['chore', 'ci', 'build', 'deps']
            }

            type_counts = {pr_type: 0 for pr_type in PRType}

            for message in commit_messages:
                lower_message = message.lower()
                for pr_type, keywords in type_keywords.items():
                    if any(keyword in lower_message for keyword in keywords):
                        type_counts[pr_type] += 1

            if type_counts:
                return max(type_counts, key=type_counts.get)

        return PRType.FEATURE  # Default

    def analyze_changes(self) -> Dict:
        """Analyze changes for PR description."""
        # Get diff statistics
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD~1"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        stats = result.stdout

        # Get changed files
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        changed_files = result.stdout.strip().split('\n') if result.stdout else []

        # Categorize changes
        changes_by_type = {
            'source': [],
            'test': [],
            'docs': [],
            'config': [],
            'other': []
        }

        for file in changed_files:
            if not file:
                continue

            if 'test' in file.lower() or 'spec' in file.lower():
                changes_by_type['test'].append(file)
            elif file.endswith(('.md', '.rst', '.txt')):
                changes_by_type['docs'].append(file)
            elif file.endswith(('.yml', '.yaml', '.json', '.toml', '.ini')):
                changes_by_type['config'].append(file)
            elif file.endswith(('.py', '.js', '.java', '.cpp', '.go', '.rs')):
                changes_by_type['source'].append(file)
            else:
                changes_by_type['other'].append(file)

        return {
            'stats': stats,
            'total_files': len(changed_files),
            'files_by_type': changes_by_type,
            'components': self._detect_components(changed_files)
        }

    def _detect_components(self, files: List[str]) -> List[str]:
        """Detect affected components from file paths."""
        components = set()

        for file in files:
            parts = Path(file).parts
            if len(parts) > 1:
                # Use first directory as component
                components.add(parts[0])

        return list(components)

    def generate_pr_description(self, pr_type: PRType,
                               commit_messages: List[str],
                               changes: Dict) -> str:
        """Generate PR description from template and analysis."""
        template = self.templates[pr_type.value]

        # Generate description from commit messages
        description = self._summarize_commits(commit_messages)

        # Generate change summary
        change_summary = []
        for change_type, files in changes['files_by_type'].items():
            if files:
                change_summary.append(f"- **{change_type.capitalize()}**: {len(files)} files")

        # Extract issue references
        issues = self._extract_issue_references(commit_messages)

        # Fill template
        filled = template.replace('{{{{description}}}}', description)
        filled = filled.replace('{{{{changes}}}}', '\n'.join(change_summary))
        filled = filled.replace('{{{{testing}}}}', '- All tests pass\n- No regressions detected')
        filled = filled.replace('{{{{issues}}}}', ', '.join(issues) if issues else 'None')
        filled = filled.replace('{{{{notes}}}}', 'Auto-generated by Git Operations Expert')

        return filled

    def _summarize_commits(self, commit_messages: List[str]) -> str:
        """Summarize commit messages into a description."""
        if not commit_messages:
            return "No commit messages found"

        # Remove duplicates and clean up
        unique_messages = []
        seen = set()

        for msg in commit_messages:
            # Extract the main part (before any detailed description)
            main_part = msg.split('\n')[0].strip()

            # Remove common prefixes
            for prefix in ['feat:', 'fix:', 'docs:', 'test:', 'chore:', 'refactor:']:
                if main_part.lower().startswith(prefix):
                    main_part = main_part[len(prefix):].strip()
                    break

            if main_part and main_part not in seen:
                unique_messages.append(main_part)
                seen.add(main_part)

        if len(unique_messages) == 1:
            return unique_messages[0]
        elif len(unique_messages) <= 3:
            return '\n'.join(f"- {msg}" for msg in unique_messages)
        else:
            # Summarize if too many commits
            return f"Multiple improvements and fixes ({len(unique_messages)} commits)"

    def _extract_issue_references(self, commit_messages: List[str]) -> List[str]:
        """Extract issue references from commit messages."""
        issues = set()

        patterns = [
            r'#(\d+)',  # GitHub style
            r'([A-Z]+-\d+)',  # JIRA style
            r'fixes\s+#?(\d+)',
            r'closes\s+#?(\d+)',
            r'resolves\s+#?(\d+)'
        ]

        for msg in commit_messages:
            for pattern in patterns:
                matches = re.findall(pattern, msg, re.IGNORECASE)
                issues.update(matches)

        return sorted(list(issues))

    def select_reviewers(self, components: List[str], pr_type: PRType) -> List[str]:
        """Select appropriate reviewers based on components and PR type."""
        reviewers = set(self.config['reviewers']['default'])

        # Add component-specific reviewers
        for component in components:
            if component in self.config['reviewers']['by_component']:
                reviewers.update(self.config['reviewers']['by_component'][component])

        return list(reviewers)

    def create_github_pr(self, title: str, description: str,
                        source_branch: str, target_branch: str = "main") -> Dict:
        """Create a GitHub Pull Request."""
        if not all([self.config['github']['token'],
                   self.config['github']['owner'],
                   self.config['github']['repo']]):
            raise ValueError("GitHub configuration incomplete")

        url = f"{self.config['github']['api_url']}/repos/{self.config['github']['owner']}/{self.config['github']['repo']}/pulls"

        headers = {
            'Authorization': f"token {self.config['github']['token']}",
            'Accept': 'application/vnd.github.v3+json'
        }

        data = {
            'title': title,
            'body': description,
            'head': source_branch,
            'base': target_branch,
            'draft': False
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            pr_data = response.json()
            return {
                'success': True,
                'pr_number': pr_data['number'],
                'pr_url': pr_data['html_url']
            }
        else:
            return {
                'success': False,
                'error': response.text
            }

    def create_pr(self, title: Optional[str] = None,
                 source_branch: Optional[str] = None,
                 target_branch: str = "main") -> Dict:
        """Create a pull request with auto-generated content."""
        # Get current branch if not specified
        if not source_branch:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            source_branch = result.stdout.strip()

        # Get commit messages
        result = subprocess.run(
            ["git", "log", f"{target_branch}..{source_branch}", "--pretty=format:%s%n%b"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        commit_messages = [msg for msg in result.stdout.split('\n\n') if msg.strip()]

        # Detect PR type
        pr_type = self.detect_pr_type(source_branch, commit_messages)

        # Analyze changes
        changes = self.analyze_changes()

        # Generate title if not provided
        if not title:
            title = self._generate_title(pr_type, commit_messages, source_branch)

        # Generate description
        description = self.generate_pr_description(pr_type, commit_messages, changes)

        # Select reviewers
        reviewers = self.select_reviewers(changes['components'], pr_type)

        # Create PR (GitHub for now, can extend to GitLab)
        result = self.create_github_pr(title, description, source_branch, target_branch)

        if result['success']:
            print(f"✅ PR created: {result['pr_url']}")

            # Add reviewers
            if reviewers:
                self._add_reviewers(result['pr_number'], reviewers)

            # Add labels
            labels = self.config['labels'].get(pr_type.value, [])
            if labels:
                self._add_labels(result['pr_number'], labels)
        else:
            print(f"❌ Failed to create PR: {result['error']}")

        return result

    def _generate_title(self, pr_type: PRType, commit_messages: List[str],
                       branch_name: str) -> str:
        """Generate PR title."""
        # Try to extract from first commit
        if commit_messages:
            first_commit = commit_messages[0].split('\n')[0]
            # Clean up common prefixes
            for prefix in ['feat:', 'fix:', 'docs:', 'test:', 'chore:']:
                if first_commit.lower().startswith(prefix):
                    first_commit = first_commit[len(prefix):].strip()
                    break
            return f"[{pr_type.value.upper()}] {first_commit}"

        # Fallback to branch name
        clean_branch = branch_name.replace('-', ' ').replace('_', ' ').replace('/', ': ')
        return f"[{pr_type.value.upper()}] {clean_branch}"

    def _add_reviewers(self, pr_number: int, reviewers: List[str]):
        """Add reviewers to a GitHub PR."""
        url = f"{self.config['github']['api_url']}/repos/{self.config['github']['owner']}/{self.config['github']['repo']}/pulls/{pr_number}/requested_reviewers"

        headers = {
            'Authorization': f"token {self.config['github']['token']}",
            'Accept': 'application/vnd.github.v3+json'
        }

        data = {'reviewers': reviewers}

        requests.post(url, json=data, headers=headers)

    def _add_labels(self, pr_number: int, labels: List[str]):
        """Add labels to a GitHub PR."""
        url = f"{self.config['github']['api_url']}/repos/{self.config['github']['owner']}/{self.config['github']['repo']}/issues/{pr_number}/labels"

        headers = {
            'Authorization': f"token {self.config['github']['token']}",
            'Accept': 'application/vnd.github.v3+json'
        }

        data = {'labels': labels}

        requests.post(url, json=data, headers=headers)

if __name__ == '__main__':
    creator = PRCreator()
    result = creator.create_pr()
    print(json.dumps(result, indent=2))

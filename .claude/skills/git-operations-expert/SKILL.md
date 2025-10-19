---
name: Git Operations Expert
description: Advanced git operations with intelligent conflict resolution, PR automation, and branch management
---

# Git Operations Expert

## When to Use
This skill is automatically invoked when:
- Committing code changes
- Creating pull/merge requests
- Resolving merge conflicts
- Managing branches
- Performing rollbacks
- Enforcing git workflows

## Capabilities
- **Conflict Resolution**: Intelligent merge conflict resolution strategies
- **PR Automation**: Create PRs with appropriate templates and metadata
- **Branch Management**: Create, merge, and delete branches following best practices
- **Commit Intelligence**: Generate semantic commit messages from changes
- **Hook Integration**: Pre-commit, pre-push, and post-merge hooks
- **Rollback Support**: Safe rollback with reflog tracking

## Conflict Resolution Strategies

### Automatic Resolution
- Whitespace and formatting conflicts
- Import statement ordering
- Package version conflicts (using semantic versioning rules)
- Comment-only changes

### Semi-Automatic Resolution
- Simple code conflicts with clear precedence
- Configuration file merges
- Documentation conflicts

### Manual Escalation
- Complex logic changes
- Architectural conflicts
- Security-sensitive code

## PR/MR Templates
- Bug fix template
- Feature template
- Hotfix template
- Documentation template
- Refactoring template

## Configuration
See `resources/git_config.yaml` for repository-specific settings.

## Usage

### Conflict Resolution
```bash
./integrate.sh resolve
```

Detects and automatically resolves common merge conflicts. For complex conflicts, creates a detailed report and suggests manual resolution strategies.

### Pull Request Creation
```bash
./integrate.sh pr
```

Analyzes changes, detects PR type, selects appropriate template, and creates PR with:
- Auto-generated title and description
- Appropriate labels
- Suggested reviewers based on component ownership
- Linked issues from commit messages

### Commit Message Generation
```bash
./integrate.sh commit
```

Generates conventional commit messages by analyzing:
- Changed files and their types
- Modified functions and classes
- Import changes
- Test additions
- Documentation updates

### Repository Status
```bash
./integrate.sh status
```

Shows comprehensive repository status including:
- Current branch and tracking information
- Uncommitted changes
- Recent commit history
- Conflict status (if any)

## Integration with OVERPROMPT Workflow

This skill replaces the `git-ops-agent` in the automated bug resolution workflow:

**Phase 4: Git Operations**
- Automatically generates semantic commit messages from bug fixes
- Commits changes with proper conventional commit format
- Pushes to appropriate branch (master/main or feature branch)

**Phase 5: Update Status & Archive**
- Updates bug status in feature-management
- Moves completed items to archive
- Commits tracking changes

## Advanced Features

### Branch Protection Compliance
- Validates commits against branch protection rules
- Prevents force pushes to protected branches
- Enforces required PR approvals

### Semantic Versioning
- Automatically determines version bumps from commit types
- Suggests version numbers for releases
- Validates version conflicts in dependency files

### Git Hooks
Pre-configured hooks for:
- **pre-commit**: Linting, formatting, basic tests
- **pre-push**: Full test suite, security checks
- **post-merge**: Dependency updates, notifications

## Examples

### Example 1: Auto-resolve Import Conflicts
```bash
# Conflict detected in imports
./integrate.sh resolve
# Output:
# ✅ Auto-resolved: src/utils.py (import conflict merged and sorted)
```

### Example 2: Create Feature PR
```bash
# On feature branch with multiple commits
./integrate.sh pr
# Output:
# 📊 Analyzing changes...
# 🎯 Detected PR type: FEATURE
# 📝 Generated description from 3 commits
# 👥 Added reviewers: @alice, @bob
# 🏷️  Added labels: enhancement, feature
# ✅ PR created: https://github.com/owner/repo/pull/123
```

### Example 3: Generate Commit Message
```bash
git add .
./integrate.sh commit
# Output:
# Generated commit message:
# ==================================================
# feat(orchestrator): add workflow state persistence
#
# Modified files:
# - python: 3 files
#
# Functions: save_state, load_state, validate_checkpoint
#
# +127 -32
# ==================================================
# Use this commit message? (y/n/e to edit):
```

## Script Reference

### conflict_resolver.py
Intelligent conflict detection and resolution system supporting:
- Multiple conflict type classification
- Automatic resolution for safe conflict types
- Detailed conflict reports
- Safe fallback for complex conflicts

### pr_creator.py
Automated PR creation with:
- PR type detection from branch names and commits
- Template selection and filling
- Change analysis and categorization
- Reviewer and label assignment
- GitHub/GitLab API integration

### commit_generator.py
Commit message generation following conventional commits:
- Analyzes staged/unstaged changes
- Detects commit type (feat/fix/docs/etc.)
- Determines scope from file changes
- Generates descriptive commit messages
- Validates message format

## Configuration Options

See `resources/git_config.yaml` for full configuration reference.

Key settings:
- **repository.default_branch**: Main branch name
- **repository.protected_branches**: Branches requiring PR workflow
- **commit.conventional**: Enable conventional commit format
- **merge.default_strategy**: Merge strategy preference
- **conflicts.auto_resolve_types**: Which conflicts to auto-resolve
- **pull_requests.min_approvals**: Required PR approvals

## Troubleshooting

**Conflict resolution fails:**
- Check `conflicts.auto_resolve_types` in config
- Review conflict report for manual resolution guidance
- Use `git diff --name-only --diff-filter=U` to see conflicted files

**PR creation fails:**
- Verify GitHub/GitLab token in environment or config
- Check repository owner and name in config
- Ensure target branch exists

**Commit message validation fails:**
- Review conventional commit format requirements
- Use `-e` option to manually edit generated message
- Check header length (<= 72 characters)

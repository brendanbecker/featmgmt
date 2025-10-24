# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is featmgmt?

featmgmt is a template repository that provides a standardized pattern for managing bugs, features, and tasks with autonomous Claude Code agents. It uses a multi-phase workflow orchestrated by subagents to automatically scan, prioritize, implement, test, and archive work items.

## Common Commands

### Initialize New Project

**Standard variant (application development):**
```bash
./scripts/init-project.sh standard /path/to/myproject/feature-management myproject "backend,frontend,api"
```

**GitOps variant (infrastructure management):**
```bash
./scripts/init-project.sh gitops /path/to/infra/feature-management infra "kubernetes,helm,builds"
```

### Sync Subagents to Project

Copy agent definitions to global or local `.claude/agents/` directory:

**Global installation (recommended):**
```bash
./scripts/sync-agents.sh --global standard
# or
./scripts/sync-agents.sh --global gitops
```

**Local installation (project-specific):**
```bash
./scripts/sync-agents.sh standard /path/to/myproject
# or
./scripts/sync-agents.sh gitops /path/to/infra
```

**⚠️ IMPORTANT: After syncing agents, restart your Claude Code session** for the agents to be discovered and available for use.

## Agent Installation

### How Agent Installation Works

featmgmt uses **both global and local** installation options for custom agents:

- **Discovery**: Claude Code discovers agents from `.claude/agents/` directories
- **Restart Required**: After installing or updating agents, you MUST restart the Claude Code session
- **Priority**: Local agents (project-specific) take precedence over global agents if both exist

### Installation Locations

#### Global Installation (~/.claude/agents/)

Agents installed globally are available to **all projects** on your system.

**Benefits:**
- ✅ Agents work across all featmgmt-enabled projects
- ✅ Update once, affects all projects
- ✅ Cleaner project repositories (no .claude/ directory needed)
- ✅ Recommended for most users

**Drawbacks:**
- ⚠️ Different projects might need different agent versions
- ⚠️ Changes affect all projects simultaneously

**Install globally:**
```bash
./scripts/sync-agents.sh --global standard
```

#### Local Installation (project/.claude/agents/)

Agents installed locally are scoped to a **specific project**.

**Benefits:**
- ✅ Version isolation per project
- ✅ Safe to customize agents for specific needs
- ✅ Explicit control over agent updates
- ✅ Git-trackable agent definitions (if desired)

**Drawbacks:**
- ⚠️ Duplication across projects using same agents
- ⚠️ Must sync separately for each project

**Install locally:**
```bash
./scripts/sync-agents.sh standard /path/to/myproject
```

### Session Restart Required

**Critical:** Claude Code only discovers agents at session start. After installing or updating agents:

1. Close your Claude Code session
2. Reopen Claude Code
3. Verify agents are available (they should appear in available agents list)

### Choosing Global vs Local

**Use Global Installation when:**
- You use featmgmt across multiple projects
- You want simplicity and consistency
- You don't need project-specific agent customizations
- You're okay with all projects using the same agent versions

**Use Local Installation when:**
- You need different agent versions for different projects
- You want to customize agents for specific project needs
- You're managing a single large project
- You want agents version-controlled with the project

**Hybrid Approach:**
- Install shared agents globally (~/.claude/agents/)
- Install customized agents locally (project/.claude/agents/)
- Local agents override global ones with the same name

### Update Existing Project

Compare project with latest template:
```bash
./scripts/compare-with-template.sh /path/to/project/feature-management standard
```

Dry run to see what would change:
```bash
./scripts/update-project.sh --dry-run /path/to/project/feature-management
```

Apply updates (creates automatic backup):
```bash
./scripts/update-project.sh /path/to/project/feature-management
```

### Script Permissions

If scripts fail with permission errors:
```bash
chmod +x scripts/*.sh
```

## Architecture Overview

### Two-Variant System

featmgmt provides **two distinct variants** for different use cases:

**Standard Variant:**
- For application development (web apps, APIs, services, libraries)
- Uses: `scan-prioritize-agent`, `bug-processor-agent`, `test-runner-agent`
- Workflow: Bug triage → Implementation → Testing → Git ops → Archive

**GitOps Variant:**
- For infrastructure management (Kubernetes, CI/CD, IaC)
- Uses: `task-scanner-agent`, `infra-executor-agent`, `verification-agent`
- Workflow: Task scanning → Infrastructure execution → Cluster verification → Git ops → Archive

**Shared Components:**
- Both variants share `git-ops-agent`, `retrospective-agent`, and `summary-reporter-agent`
- Both use the same directory structure (bugs/, features/, completed/, deprecated/, human-actions/, agent_runs/)
- Configuration files: `.featmgmt-version`, `.featmgmt-config.json`, `.agent-config.json`

### Template Repository Pattern

featmgmt is the **source of truth** for:
- OVERPROMPT.md workflow definitions (separate files per variant)
- Subagent definitions in `claude-agents/`
- Directory structure and file formats
- Configuration schemas

Projects **consume** templates via:
- `init-project.sh` - Creates new feature-management directory from templates
- `update-project.sh` - Pulls latest template changes (with backups)
- `sync-agents.sh` - Syncs agent definitions to `.claude/agents/`

### Workflow Execution Flow

1. User opens `OVERPROMPT.md` in target project's feature-management directory
2. **Phase 1**: Scan & Prioritize → Invoke `scan-prioritize-agent` to build priority queue
3. **Phase 2**: Process → Invoke variant-specific processor (`bug-processor-agent` or `infra-executor-agent`)
4. **Phase 3**: Test/Verify → Invoke `test-runner-agent` or `verification-agent`
5. **Phase 4**: Git Operations → Invoke `git-ops-agent` to commit and push
6. **Phase 5**: Archive → Invoke `git-ops-agent` to move completed items to `completed/`
7. **Phase 6**: Retrospective → Invoke `retrospective-agent` to analyze session and reprioritize
8. **Phase 7**: Report → Invoke `summary-reporter-agent` to generate session report

OVERPROMPT loops through bugs/features until queue is empty or iteration limit is reached.

### Subagent Invocation

**CRITICAL**: Always use the Task tool to invoke subagents. They are located in the consuming project's `.claude/agents/` directory, NOT in the featmgmt repository.

Example invocation:
```markdown
Task tool parameters:
- subagent_type: "scan-prioritize-agent"
- description: "Scan and prioritize bugs/features"
- prompt: "Scan the feature-management repository at /path/to/project/feature-management..."
```

### Directory Structure

Created by `init-project.sh`:
```
feature-management/
├── OVERPROMPT.md              # Self-executing workflow (variant-specific)
├── README.md                   # Project-specific documentation
├── agent_actions.md            # Agent reference guide
├── .agent-config.json          # Agent behavior configuration
├── .featmgmt-version           # Template version tracking
├── .featmgmt-config.json       # Project metadata
├── .gitignore                  # Git ignore rules
├── bugs/                       # Bug reports and PROMPT.md files
│   └── bugs.md                 # Summary table
├── features/                   # Feature requests
│   └── features.md             # Summary table
├── completed/                  # Archived completed items
├── deprecated/                 # Obsolete items
├── human-actions/              # Items requiring human intervention
└── agent_runs/                 # Session reports
```

### Bug/Feature File Structure

Each bug/feature lives in its own directory:
```
bugs/BUG-XXX-slug/
├── PROMPT.md          # Required: Self-executing implementation instructions
├── bug_report.json    # Required: Metadata (ID, priority, status, component)
├── PLAN.md            # Optional: Implementation plan
├── TASKS.md           # Optional: Task breakdown
└── comments.md        # Optional: Notes and updates
```

## Configuration Files

### .featmgmt-version
Single line containing version number (e.g., "1.0.0"). Used by `update-project.sh` to track template version.

### .featmgmt-config.json
Project metadata and customization tracking:
```json
{
  "project_name": "myproject",
  "project_type": "standard",
  "featmgmt_version": "1.0.0",
  "initialized_at": "2025-10-18T10:00:00Z",
  "components": ["backend", "frontend"],
  "customizations": {
    "description": "Track local changes here"
  }
}
```

### .agent-config.json
Agent behavior configuration:
```json
{
  "version": "1.0.0",
  "project_name": "myproject",
  "project_type": "standard",
  "duplicate_similarity_threshold": 0.75,
  "available_tags": ["backend", "frontend", "api", ...],
  "component_detection_keywords": {...},
  "severity_keywords": {...}
}
```

## Customization Philosophy

Templates are **starting points, not constraints**. Projects should customize:

**Freely customize:**
- OVERPROMPT.md workflow steps and paths
- .agent-config.json tags and keywords
- Add custom subagents (copy from `claude-agents/` and modify)
- Add custom scripts to feature-management/scripts/
- Add project-specific sections to OVERPROMPT.md

**Keep standard:**
- Directory names (bugs/, features/, completed/)
- Required files (PROMPT.md, bug_report.json)
- Summary file format (bugs.md, features.md column headers)
- Version tracking files

**Document everything:**
- Track customizations in `.featmgmt-config.json`
- Use git commits for version control of changes
- Add project docs to feature-management/docs/

## Update Strategy

Updates create automatic backups before modifying files. Rollback options:

```bash
# View backup
ls -la /path/to/feature-management/.featmgmt-backup-*/

# Rollback via git
cd /path/to/feature-management
git reset --hard HEAD~1

# Manual merge if needed
diff OVERPROMPT.md .featmgmt-backup-*/OVERPROMPT.md
```

## Prerequisites

- Git
- Bash (Linux/macOS/WSL)
- jq (for JSON processing)
- Claude Code

Install jq:
```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

## Key Design Decisions

### Why Two Variants Instead of Parameterization?

Application development and infrastructure management have fundamentally different workflows. Separate OVERPROMPT files are clearer and easier to maintain than heavily parameterized templates.

### Why Bash Scripts?

- Available on all Linux/macOS/WSL environments
- Simple file operations and git commands
- Easy to read and modify
- Minimal dependencies (only jq required)

### Why Git Submodules (Optional)?

feature-management can be:
- A regular directory in the project (simpler)
- A git submodule (enables sharing across projects and independent versioning)

### Why Shared Agents?

Git operations, retrospectives, and reporting are identical for both variants. Shared agents mean improvements benefit all projects using the pattern.

## Version Tracking

featmgmt uses semantic versioning:
- **Major (X.0.0)**: Breaking changes requiring migration
- **Minor (1.X.0)**: New features, backward compatible
- **Patch (1.0.X)**: Bug fixes, backward compatible

Current version stored in `VERSION` file at repository root.

## Important Files

**In featmgmt repository:**
- `templates/OVERPROMPT-standard.md` - Standard variant workflow template
- `templates/OVERPROMPT-gitops.md` - GitOps variant workflow template
- `templates/.agent-config.json.template` - Agent configuration template
- `claude-agents/{standard,gitops,shared}/` - Subagent definitions
- `scripts/init-project.sh` - Project initialization
- `scripts/sync-agents.sh` - Agent synchronization
- `scripts/update-project.sh` - Template updates
- `scripts/compare-with-template.sh` - Comparison tool
- `VERSION` - Current template version

**In consuming projects:**
- `feature-management/OVERPROMPT.md` - The workflow to run with Claude Code
- `feature-management/.agent-config.json` - Customize tags/components here
- `feature-management/bugs/bugs.md` - Bug summary table
- `feature-management/features/features.md` - Feature summary table
- `.claude/agents/` - Synced subagent definitions

## Documentation

- `docs/ARCHITECTURE.md` - Design decisions and component architecture
- `docs/SETUP.md` - Detailed setup instructions
- `docs/CUSTOMIZATION.md` - Customization options and examples
- `docs/UPDATING.md` - Update procedures and troubleshooting
- `README.md` - Quick start and overview

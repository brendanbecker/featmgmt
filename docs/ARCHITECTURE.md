# Architecture

This document explains the design and architecture of the featmgmt pattern.

## Overview

featmgmt is a template repository for managing bug reports, feature requests, and automated resolution workflows using Claude Code subagents. It provides a standardized structure and tooling that can be adopted by any project.

## Core Concepts

### 1. Template Repository Pattern

featmgmt serves as the **source of truth** for:
- Directory structures
- Workflow definitions (OVERPROMPT.md)
- Subagent definitions
- Configuration schemas

Projects **consume** the pattern via:
- `init-project.sh` - Initial setup
- `update-project.sh` - Receiving updates
- `sync-agents.sh` - Syncing subagent definitions

### 2. Two Variants: Standard vs GitOps

**Why Two Variants?**

Application development and infrastructure management have fundamentally different workflows:

| Aspect | Standard (Apps) | GitOps (Infrastructure) |
|--------|----------------|------------------------|
| **Primary Activity** | Feature implementation | Infrastructure changes |
| **Testing** | Unit/integration tests | Cluster verification |
| **Deployment** | CI/CD pipelines | Flux CD reconciliation |
| **Verification** | Test suites | kubectl checks |
| **Tools** | pytest, jest, etc. | kubectl, flux, helm |

**What's Different Between Variants?**

1. **OVERPROMPT.md** - Workflow steps adapted to domain
2. **Subagents** - Domain-specific agents (bug-processor vs infra-executor)
3. **.agent-config.json** - Component tags (app components vs infrastructure components)

**What's The Same?**

- Directory structure (bugs/, features/, completed/, etc.)
- Shared agents (git-ops, retrospective, summary-reporter)
- File formats (PROMPT.md, bug_report.json, etc.)
- Update mechanisms

### 3. Unified Directory Structure

All projects use the same structure regardless of variant:

```
bugs/           # Issues (bugs for apps, infrastructure bugs for gitops)
features/       # Enhancements (features for apps, infrastructure improvements for gitops)
completed/      # Archived items
deprecated/     # Obsolete items
human-actions/  # Items requiring human intervention
agent_runs/     # Session logs and reports
```

This uniformity enables:
- Single set of scripts works for all projects
- Easier transitions between project types
- Consistent reporting and retrospectives

## Component Architecture

### Templates

**Purpose:** Source files that get copied to projects

```
templates/
├── OVERPROMPT-standard.md       # Standard workflow
├── OVERPROMPT-gitops.md         # GitOps workflow
├── .agent-config.json.template  # Configuration template
├── agent_actions.md             # Agent reference
├── README.md.template           # Project docs template
└── .gitignore                   # Git ignore patterns
```

**Key Design Decision:** Separate OVERPROMPT files for each variant rather than parameterization, because workflows differ significantly.

### Subagents

**Purpose:** Specialized Claude Code agents for workflow phases

```
claude-agents/
├── standard/                    # Standard variant agents
│   ├── scan-prioritize-agent.md
│   ├── bug-processor-agent.md
│   └── test-runner-agent.md
├── gitops/                      # GitOps variant agents
│   ├── task-scanner-agent.md
│   ├── infra-executor-agent.md
│   └── verification-agent.md
└── shared/                      # Common agents
    ├── retrospective-agent.md
    ├── summary-reporter-agent.md
    └── git-history-agent.md
```

**Subagent Workflow (Standard):**

```
OVERPROMPT.md
    │
    ├─→ [Phase 1] scan-prioritize-agent
    │       └─→ Builds priority queue
    │
    ├─→ [Phase 2] bug-processor-agent
    │       └─→ Executes PROMPT.md instructions
    │
    ├─→ [Phase 3] test-runner-agent
    │       └─→ Runs tests, creates human actions if failures
    │
    ├─→ [Phase 4] Archive (direct execution)
    │       └─→ Moves completed items to completed/, commits
    │
    ├─→ [Phase 5] retrospective-agent (shared)
    │       └─→ Reviews session, reprioritizes backlog, commits changes
    │
    └─→ [Phase 6] summary-reporter-agent (shared)
            └─→ Generates session report

Note: Each agent commits its own work - bug-processor-agent commits implementation,
retrospective-agent commits reprioritization, etc. Git operations are intrinsic to
each agent's responsibilities.
```

**Subagent Workflow (GitOps):**

```
OVERPROMPT.md
    │
    ├─→ [Phase 1] task-scanner-agent
    │       └─→ Builds priority queue
    │
    ├─→ [Phase 2] infra-executor-agent
    │       └─→ Executes infrastructure tasks
    │
    ├─→ [Phase 3] verification-agent
    │       └─→ Verifies cluster state
    │
    ├─→ [Phase 4] Archive (direct execution)
    │       └─→ Moves completed tasks to completed/, commits
    │
    ├─→ [Phase 5] retrospective-agent (shared)
    │       └─→ Reviews session, reprioritizes backlog, commits changes
    │
    └─→ [Phase 6] summary-reporter-agent (shared)
            └─→ Generates session report

Note: Each agent commits its own work - infra-executor-agent commits infrastructure
changes, retrospective-agent commits reprioritization, etc. Git operations are
intrinsic to each agent's responsibilities.
```

### Status and State Management

**Status Lifecycle**: All work items follow consistent status transitions:

| Status | Set By | Meaning |
|--------|--------|---------|
| `new` | work-item-creation-agent | Created but not started |
| `in_progress` | bug-processor-agent | Currently being implemented |
| `resolved` | OVERPROMPT Phase 4 | Completed successfully |
| `deprecated` | retrospective-agent | Obsolete/superseded |
| `merged` | retrospective-agent | Consolidated into another item |

**Audit Trail**: The combination of `created_date`, `started_date`, `updated_date`, and `completed_date` provides complete timeline tracking for metrics and analysis.

**Concurrent Safety**: The `in_progress` status acts as a basic lock mechanism, preventing multiple agents from starting the same item simultaneously.

### Scripts

**Purpose:** Automation tools for setup, updates, and synchronization

```
scripts/
├── init-project.sh            # Initialize new project
├── update-project.sh          # Update existing project
├── sync-agents.sh             # Sync subagent definitions
└── compare-with-template.sh   # Compare project with template
```

**Script Design Principles:**
1. **Idempotent** - Can run multiple times safely
2. **Atomic** - Create backups before changes
3. **Transparent** - Show what will change (--dry-run)
4. **Reversible** - Can rollback via git or backups

## Data Flow

### Initialization Flow

```
User runs init-project.sh
    ↓
Copy templates → Create directories → Substitute variables
    ↓
Initialize git → Create summary files → Set version
    ↓
feature-management/ directory ready
    ↓
User runs sync-agents.sh
    ↓
Copy variant agents → Copy shared agents
    ↓
.claude/agents/ populated
```

### Update Flow

```
User runs update-project.sh
    ↓
Check .featmgmt-version
    ↓
Compare current vs latest
    ↓
Create backup
    ↓
Update templates (preserve customizations)
    ↓
Update version files
    ↓
Log changes to UPDATE_LOG.md
    ↓
Commit changes
```

### Workflow Execution Flow

```
User opens OVERPROMPT.md in Claude Code
    ↓
OVERPROMPT auto-starts (Phase 1)
    ↓
Invoke scan-prioritize-agent → Get priority queue
    ↓
IF queue empty → Invoke retrospective + summary → EXIT
    ↓
Invoke bug-processor-agent → Implement highest priority item
    ↓
Invoke test-runner-agent → Verify implementation
    ↓
Bug-processor commits its own changes
    ↓
Archive to completed/ (direct execution)
    ↓
Loop back to Phase 1 OR proceed to Phase 6
    ↓
Invoke retrospective-agent → Reprioritize backlog
    ↓
Invoke summary-reporter-agent → Generate report
    ↓
EXIT
```

## Configuration Management

### Version Tracking

**. featmgmt-version:**
- Single line: version number (e.g., "1.0.0")
- Indicates which template version the project uses
- Updated by update-project.sh

**.featmgmt-config.json:**
```json
{
  "project_name": "myproject",
  "project_type": "standard",
  "featmgmt_version": "1.0.0",
  "initialized_at": "2025-10-18T10:00:00Z",
  "components": ["backend", "frontend", "api"],
  "customizations": {
    "description": "Track local changes here"
  }
}
```

Purpose: Track project metadata and customizations

**.agent-config.json:**
```json
{
  "version": "1.0.0",
  "project_name": "myproject",
  "project_type": "standard",
  "available_tags": ["backend", "frontend", ...],
  "component_detection_keywords": {...},
  "severity_keywords": {...}
}
```

Purpose: Configure agent behavior (component detection, tagging)

### Customization Strategy

**Philosophy:** Templates are starting points, not constraints.

Projects can customize:
- OVERPROMPT.md workflow steps
- .agent-config.json tags and keywords
- Directory structure (add new dirs)
- Subagent prompts (copy and modify)

**Preserving Customizations:**
- update-project.sh creates backups before updating
- Manual merge required if significant changes
- .featmgmt-config.json documents customizations

## Design Decisions

### Why Submodules?

**Option 1: Git Submodules** (Chosen)
- Separate repository for feature-management
- Independent version control
- Can be shared across projects

**Option 2: Monorepo**
- Everything in one repository
- Simpler but less flexible
- Harder to share patterns

**Decision:** Submodules for maximum flexibility

### Why Bash Scripts?

**Alternatives Considered:**
- Python scripts (more portable, but requires Python)
- Node.js scripts (requires Node)
- Make/Makefile (less portable)

**Decision:** Bash scripts for:
- Available on all Linux/macOS/WSL
- Simple file operations and git commands
- Easy to read and modify
- No additional dependencies (except jq)

### Why Two Variants Instead of Parameterization?

**Option 1: Parameterized Single OVERPROMPT** (Rejected)
```markdown
{{#if gitops}}
  Run kubectl commands
{{else}}
  Run pytest
{{/if}}
```

**Option 2: Separate OVERPROMPT Files** (Chosen)

**Decision:** Workflows are too different to parameterize cleanly. Separate files are clearer and easier to maintain.

### Why Shared Agents?

git-ops, retrospective, and summary-reporter agents are identical for both variants because:
- Git operations don't differ between app and infra
- Retrospective logic applies to both domains
- Report generation format is the same

**Benefit:** Fixes and improvements to shared agents benefit all projects.

## Scalability Considerations

### Multiple Project Types

**Future Expansion:**
- Add new variants (e.g., "mobile", "data-science")
- Copy claude-agents/standard → claude-agents/mobile
- Create templates/OVERPROMPT-mobile.md
- Scripts remain unchanged

### Cross-Project Reports

**Future Enhancement:**
- Aggregate agent_runs/ across all projects
- Dashboard showing bugs/features across portfolio
- Cross-project retrospectives

### Template Evolution

**Versioning Strategy:**
- Semantic versioning (1.0.0, 1.1.0, 2.0.0)
- Migration guides for breaking changes
- compare-with-template.sh shows diff

## Security Considerations

### No Secrets in Templates

Templates never contain:
- API keys
- Passwords
- Personal access tokens

Projects must add secrets via:
- Environment variables
- Secure secret management
- .gitignore for sensitive files

### Git Submodule Security

When using submodules:
- Verify submodule URL before adding
- Pin to specific commits (not floating)
- Review updates before pulling

## Future Enhancements

### Planned Features

1. **Smart Merge for Updates**
   - 3-way merge of OVERPROMPT.md
   - Preserve local customizations automatically

2. **Template Variables**
   - {{PROJECT_PATH}} substitution in OVERPROMPT.md
   - Makes templates more portable

3. **Multiple Languages**
   - Python implementation of scripts
   - For Windows non-WSL users

4. **Web Dashboard**
   - Visualize bugs/features across projects
   - Session reports aggregation
   - Retrospective insights

### Extension Points

- Custom subagents (copy and modify)
- Additional workflow phases
- Project-specific OVERPROMPT sections
- Custom scripts in feature-management/scripts/

## References

- [SETUP.md](./SETUP.md) - Setup guide
- [CUSTOMIZATION.md](./CUSTOMIZATION.md) - Customization options
- [UPDATING.md](./UPDATING.md) - Update procedures

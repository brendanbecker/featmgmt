# Setup Guide

This guide explains how to use the featmgmt pattern to initialize a new feature-management submodule for your project.

## Prerequisites

- Git installed
- Bash shell (Linux/macOS/WSL)
- `jq` command-line tool for JSON processing

## Quick Start

### 1. Clone featmgmt Repository

```bash
git clone <featmgmt-repo-url> featmgmt
cd featmgmt
```

### 2. Initialize New Feature-Management Submodule

**For standard projects (application development):**

```bash
./scripts/init-project.sh standard /path/to/myproject/feature-management myproject "backend,frontend,api"
```

**For GitOps projects (infrastructure management):**

```bash
./scripts/init-project.sh gitops /path/to/infra-project/feature-management infra-project "infrastructure,builds,deployments"
```

### 3. Sync Subagents to Parent Project

```bash
./scripts/sync-agents.sh standard /path/to/myproject
# or
./scripts/sync-agents.sh gitops /path/to/infra-project
```

### 4. Add as Git Submodule (Optional)

If you want feature-management as a separate repository:

```bash
cd /path/to/myproject
git submodule add <feature-management-repo-url> feature-management
git commit -m "Add feature-management submodule"
```

## Detailed Steps

### Step 1: Choose Project Type

**Standard Type:**
- For application development projects
- Uses: scan-prioritize-agent, bug-processor-agent, test-runner-agent
- Best for: Web apps, APIs, services, libraries
- Workflow: Bug triage → Implementation → Testing → Git operations

**GitOps Type:**
- For infrastructure and deployment management
- Uses: task-scanner-agent, infra-executor-agent, verification-agent
- Best for: Kubernetes clusters, CI/CD pipelines, infrastructure-as-code
- Workflow: Task scanning → Infrastructure execution → Verification → Git operations

### Step 2: Run init-project.sh

The init script creates:
- Directory structure (bugs/, features/, completed/, etc.)
- Template files (OVERPROMPT.md, .agent-config.json, README.md)
- Summary files (bugs/bugs.md, features/features.md)
- Version tracking files (.featmgmt-version, .featmgmt-config.json)
- Initialized git repository

**Arguments:**
1. **type**: "standard" or "gitops"
2. **target-path**: Where to create the feature-management directory
3. **project-name**: Your project's name
4. **components**: Comma-separated list of components (optional)

**Example:**

```bash
./scripts/init-project.sh standard \
  ../triager/feature-management \
  triager \
  "orchestrator,classifier-worker,duplicate-worker"
```

### Step 3: Customize Configuration

After initialization, review and customize:

**OVERPROMPT.md:**
- Verify project-specific paths
- Adjust workflow steps if needed
- Customize agent invocation parameters

**.agent-config.json:**
- Add project-specific tags
- Define component detection keywords
- Adjust similarity thresholds

**README.md:**
- Add project-specific documentation
- Document local conventions
- Add team guidelines

### Step 4: Sync Subagents

Copy subagent definitions to your project's `.claude/agents/` directory:

```bash
./scripts/sync-agents.sh standard /path/to/myproject
```

This copies:
- Variant-specific agents (standard or gitops)
- Shared agents (git-ops, retrospective)

Verify agents are synced:

```bash
ls -la /path/to/myproject/.claude/agents/
```

### Step 5: Test the Workflow

Create a test bug to verify the workflow:

```bash
cd /path/to/myproject/feature-management/bugs
mkdir BUG-001-test
cd BUG-001-test

# Create a simple PROMPT.md
cat > PROMPT.md << 'EOF'
# BUG-001: Test Bug

## Description
This is a test bug to verify the automated workflow.

## Acceptance Criteria
- [ ] Echo "Test successful" to console
- [ ] Create test file in /tmp/

## Implementation
Run: echo "Test successful" && touch /tmp/test-bug-001
EOF

# Update bugs/bugs.md to include this bug
```

Then run the OVERPROMPT.md with Claude Code to test.

## Directory Structure

After initialization, your feature-management directory will look like:

```
feature-management/
├── .featmgmt-version              # Version tracking
├── .featmgmt-config.json          # Project configuration
├── .agent-config.json             # Agent configuration
├── .gitignore                     # Git ignore rules
├── OVERPROMPT.md                  # Workflow automation
├── README.md                      # Project-specific docs
├── agent_actions.md               # Agent reference
│
├── bugs/                          # Bug reports
│   ├── bugs.md                    # Summary file
│   └── BUG-XXX-slug/              # Individual bugs
│       ├── PROMPT.md
│       ├── PLAN.md
│       ├── TASKS.md
│       ├── bug_report.json
│       └── comments.md
│
├── features/                      # Feature requests
│   ├── features.md                # Summary file
│   └── FEAT-XXX-slug/             # Individual features
│
├── completed/                     # Archived completed items
├── deprecated/                    # Deprecated items
├── human-actions/                 # Items needing human intervention
│
└── agent_runs/                    # Session reports
    ├── session-[timestamp].md
    └── retrospective-[timestamp].md
```

## Next Steps

1. **Review Documentation**: Read [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the pattern
2. **Customize**: See [CUSTOMIZATION.md](./CUSTOMIZATION.md) for customization options
3. **Create Issues**: Start adding bugs and features to your backlog
4. **Run Workflow**: Execute OVERPROMPT.md with Claude Code
5. **Keep Updated**: Periodically run update-project.sh to get template updates

## Troubleshooting

### Script Permission Denied

```bash
chmod +x scripts/*.sh
```

### jq Not Found

Install jq:
- Ubuntu/Debian: `sudo apt-get install jq`
- macOS: `brew install jq`
- Windows (WSL): `sudo apt-get install jq`

### Git Not Initialized

If git fails to initialize:

```bash
cd /path/to/feature-management
git init
git add .
git commit -m "Initialize from featmgmt"
```

### Subagents Not Found

Ensure agents are synced:

```bash
./scripts/sync-agents.sh <type> /path/to/project
ls -la /path/to/project/.claude/agents/
```

## Support

For issues, questions, or feature requests:
- Review [ARCHITECTURE.md](./ARCHITECTURE.md) for design decisions
- Check [CUSTOMIZATION.md](./CUSTOMIZATION.md) for configuration options
- See [UPDATING.md](./UPDATING.md) for update procedures

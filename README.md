# featmgmt

**Feature Management Pattern for Claude Code Automation**

A template repository for standardized bug tracking, feature management, and automated resolution workflows using Claude Code subagents.

## What is featmgmt?

featmgmt provides a proven pattern for managing bugs, features, and tasks with autonomous Claude Code agents. It includes:

- **Unified Directory Structure** - Consistent organization across all projects
- **Automated Workflows** - Self-executing OVERPROMPT.md for bug resolution
- **Specialized Subagents** - Purpose-built agents for each workflow phase
- **Two Variants** - Standard (app development) and GitOps (infrastructure)
- **Easy Updates** - Scripts to keep projects synchronized with latest templates

## Quick Start

### 1. Clone Repository

```bash
git clone <featmgmt-repo-url> featmgmt
cd featmgmt
```

### 2. Initialize New Project

**For Application Development:**

```bash
./scripts/init-project.sh standard \
  /path/to/myproject/feature-management \
  myproject \
  "backend,frontend,api"
```

**For Infrastructure/GitOps:**

```bash
./scripts/init-project.sh gitops \
  /path/to/infra/feature-management \
  infra \
  "kubernetes,helm,builds"
```

### 3. Sync Subagents

```bash
./scripts/sync-agents.sh standard /path/to/myproject
# or
./scripts/sync-agents.sh gitops /path/to/infra
```

### 4. Start Using

```bash
cd /path/to/myproject/feature-management

# Create a bug
mkdir -p bugs/BUG-001-example
cd bugs/BUG-001-example

# Add self-executing instructions
cat > PROMPT.md << 'EOF'
# BUG-001: Example Bug

## Description
Fix the login timeout issue

## Acceptance Criteria
- [ ] Increase session timeout to 30 minutes
- [ ] Add timeout warning notification
- [ ] Update tests

## Implementation
[Detailed implementation steps...]
EOF

# Run automated workflow
# Open ../OVERPROMPT.md in Claude Code
```

## Features

### Unified Structure

All projects use the same directory structure:

```
feature-management/
├── bugs/              # Bug reports with implementation plans
├── features/          # Feature requests with specs
├── completed/         # Archived completed items
├── deprecated/        # Obsolete items
├── human-actions/     # Items requiring human intervention
└── agent_runs/        # Automated session reports
```

### Automated Workflows

OVERPROMPT.md defines a 7-phase autonomous workflow:

1. **Scan & Prioritize** - Build priority queue from bugs/features
2. **Process** - Execute implementation from PROMPT.md
3. **Test/Verify** - Run tests or verify infrastructure
4. **Git Operations** - Commit and push changes
5. **Archive** - Move completed items
6. **Retrospective** - Reprioritize backlog based on learnings
7. **Report** - Generate session summary

### Specialized Subagents

**Standard Variant (App Development):**
- `scan-prioritize-agent` - Triage and prioritization
- `bug-processor-agent` - Implementation execution
- `test-runner-agent` - Test execution and validation

**GitOps Variant (Infrastructure):**
- `task-scanner-agent` - Infrastructure task scanning
- `infra-executor-agent` - Infrastructure changes
- `verification-agent` - Kubernetes/cluster verification

**Shared (Both Variants):**
- `retrospective-agent` - Session analysis and reprioritization
- `summary-reporter-agent` - Report generation
- `git-history-agent` - Historical analysis and regression investigation

### Easy Updates

Keep projects synchronized with latest templates:

```bash
# Check for updates
./scripts/compare-with-template.sh /path/to/project/feature-management standard

# Dry run update
./scripts/update-project.sh --dry-run /path/to/project/feature-management

# Apply update
./scripts/update-project.sh /path/to/project/feature-management
```

## Project Variants

### Standard: Application Development

**Best For:**
- Web applications
- APIs and microservices
- Mobile apps
- Libraries and SDKs

**Workflow Focus:**
- Bug triage and classification
- Feature implementation
- Unit and integration testing
- Code review automation

**Example Projects:**
- triager (Bug triage system)
- ccbot (Discord bot)
- midwestmtg (MTG library management)

### GitOps: Infrastructure Management

**Best For:**
- Kubernetes clusters
- CI/CD pipelines
- Infrastructure-as-Code
- DevOps automation

**Workflow Focus:**
- Infrastructure task execution
- Kubernetes deployments
- Cluster health verification
- GitOps reconciliation

**Example Projects:**
- beckerkube (Kubernetes infrastructure)

## Directory Structure

```
featmgmt/
├── README.md                    # This file
├── VERSION                      # Current version (1.0.0)
│
├── templates/                   # Template files for projects
│   ├── OVERPROMPT-standard.md
│   ├── OVERPROMPT-gitops.md
│   ├── .agent-config.json.template
│   ├── agent_actions.md
│   ├── README.md.template
│   └── .gitignore
│
├── claude-agents/               # Subagent definitions
│   ├── standard/                # Standard variant agents
│   ├── gitops/                  # GitOps variant agents
│   └── shared/                  # Common agents
│
├── scripts/                     # Automation scripts
│   ├── init-project.sh          # Initialize new project
│   ├── update-project.sh        # Update existing project
│   ├── sync-agents.sh           # Sync subagents
│   └── compare-with-template.sh # Compare with template
│
└── docs/                        # Documentation
    ├── SETUP.md                 # Setup guide
    ├── CUSTOMIZATION.md         # Customization options
    ├── ARCHITECTURE.md          # Design decisions
    └── UPDATING.md              # Update procedures
```

## Documentation

- **[SETUP.md](docs/SETUP.md)** - Detailed setup instructions
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Pattern design and rationale
- **[CUSTOMIZATION.md](docs/CUSTOMIZATION.md)** - How to customize for your project
- **[UPDATING.md](docs/UPDATING.md)** - Update procedures and troubleshooting

## Use Cases

### Autonomous Bug Resolution

```bash
# Agent automatically:
# 1. Scans bugs/ directory
# 2. Builds priority queue
# 3. Implements highest priority bug
# 4. Runs tests
# 5. Commits and pushes
# 6. Archives completed bug
# 7. Repeats until queue empty
```

### Infrastructure Automation

```bash
# Agent automatically:
# 1. Scans infrastructure tasks
# 2. Executes kubectl/helm/flux commands
# 3. Verifies cluster health
# 4. Commits infrastructure changes
# 5. Archives completed tasks
# 6. Generates deployment report
```

### Sprint Planning

```bash
# Generate priority queue
./scripts/compare-with-template.sh /path/to/project/feature-management standard

# Review bugs.md and features.md
# Automated agents process items during sprint
# Retrospective agent analyzes outcomes
# Reprioritize for next sprint
```

## Requirements

- **Git** - Version control
- **Bash** - Shell scripting (Linux/macOS/WSL)
- **jq** - JSON processing
- **Claude Code** - For running workflows and subagents

### Installing jq

```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq

# Windows (WSL)
sudo apt-get install jq
```

## Examples

### Example 1: Bug Resolution

```bash
# Initialize project
./scripts/init-project.sh standard ../myapp/feature-management myapp

# Sync agents
./scripts/sync-agents.sh standard ../myapp

# Create bug
cd ../myapp/feature-management/bugs
mkdir BUG-001-login-timeout
cd BUG-001-login-timeout
cat > PROMPT.md << 'EOF'
# BUG-001: Login Timeout Too Short

## Description
Users are being logged out after 5 minutes of inactivity.

## Acceptance Criteria
- [ ] Increase session timeout to 30 minutes
- [ ] Add "session expiring soon" warning at 28 minutes
- [ ] Update tests to verify new timeout

## Implementation
- Update AUTH_SESSION_TIMEOUT in config
- Add timeout warning component
- Update auth tests
EOF

# Run workflow
# Open ../OVERPROMPT.md in Claude Code
```

### Example 2: Infrastructure Task

```bash
# Initialize GitOps project
./scripts/init-project.sh gitops ../infra/feature-management infra "builds,deployments"

# Sync agents
./scripts/sync-agents.sh gitops ../infra

# Create infrastructure bug
cd ../infra/feature-management/bugs
mkdir BUG-001-registry-config
cd BUG-001-registry-config
cat > PROMPT.md << 'EOF'
# BUG-001: Fix Registry Configuration

## Description
Container registry IP needs to be updated.

## Acceptance Criteria
- [ ] Update registry IP in HelmReleases
- [ ] Rebuild and push service images
- [ ] Verify deployments reconcile
- [ ] Verify pods pull images successfully

## Implementation
- Update infra/registry/helmrelease.yaml
- Run image rebuild script
- Flux reconcile
- Verify with kubectl get pods -A
EOF

# Run workflow
# Open ../OVERPROMPT.md in Claude Code
```

## Customization

featmgmt is designed to be customized. Common customizations:

- **Workflow steps** - Modify OVERPROMPT.md phases
- **Component tags** - Update .agent-config.json
- **Custom agents** - Add project-specific subagents
- **Directory structure** - Add additional directories
- **Testing strategy** - Customize test-runner-agent

See [CUSTOMIZATION.md](docs/CUSTOMIZATION.md) for details.

## Updating

Keep your projects up to date:

```bash
# Check current version
cat /path/to/project/feature-management/.featmgmt-version

# Check latest version
cat featmgmt/VERSION

# Update project
./scripts/update-project.sh /path/to/project/feature-management
```

See [UPDATING.md](docs/UPDATING.md) for update procedures and troubleshooting.

## Migration

### Existing Projects

To adopt featmgmt pattern for existing bug/feature tracking:

```bash
# 1. Add version tracking
cd /path/to/existing/feature-management
echo "1.0.0" > .featmgmt-version

# 2. Create config
cat > .featmgmt-config.json << EOF
{
  "project_name": "myproject",
  "project_type": "standard",
  "featmgmt_version": "1.0.0"
}
EOF

# 3. Compare with template
cd /path/to/featmgmt
./scripts/compare-with-template.sh /path/to/existing/feature-management standard

# 4. Apply updates
./scripts/update-project.sh /path/to/existing/feature-management
```

## FAQ

**Q: Do I need to use git submodules?**

A: No. feature-management can be a regular directory in your project. Submodules are optional but recommended for sharing across projects.

**Q: Can I customize the workflows?**

A: Yes! Templates are starting points. Customize OVERPROMPT.md, agents, and configs for your needs. See [CUSTOMIZATION.md](docs/CUSTOMIZATION.md).

**Q: What if updates break my customizations?**

A: Updates create automatic backups. You can rollback via git or restore from backup. See [UPDATING.md](docs/UPDATING.md).

**Q: Can I create custom agents?**

A: Yes! Copy an agent from claude-agents/ to your project's .claude/agents/ and modify. Custom agents are preserved during updates.

**Q: Which variant should I choose?**

A: Use **standard** for application development (features, bugs, tests). Use **gitops** for infrastructure management (kubernetes, deployments, verification).

**Q: How do I contribute improvements?**

A: Submit PRs to featmgmt repo. Improvements benefit all projects using the pattern!

## Versioning

featmgmt uses semantic versioning:

- **Major (X.0.0)** - Breaking changes, migration required
- **Minor (1.X.0)** - New features, backward compatible
- **Patch (1.0.X)** - Bug fixes, backward compatible

Current version: **1.0.0**

## License

[Specify your license here]

## Contributing

Contributions welcome! Areas for improvement:

- Additional project variants
- Enhanced merge strategies for updates
- Additional subagents
- Cross-project reporting
- Web dashboard

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues]
- Examples: [examples/](examples/)

## Credits

Created for managing multi-project bug tracking and feature automation with Claude Code.

Inspired by actual projects: triager, ccbot, midwestmtg, beckerkube.

---

**Get Started:** `./scripts/init-project.sh standard /path/to/project/feature-management myproject`

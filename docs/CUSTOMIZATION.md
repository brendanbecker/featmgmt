# Customization Guide

This guide explains how to customize the featmgmt pattern for your project's specific needs.

## Philosophy

featmgmt templates are **starting points, not constraints**. Every project is different, and you should customize the pattern to fit your workflow, not the other way around.

## What Can Be Customized

### 1. OVERPROMPT.md (Workflow Definition)

**Customization Level:** High - This is YOUR workflow

**Common Customizations:**

#### Adjust Paths
```markdown
# Original
**Subagent locations**: `/home/becker/projects/triager/.claude/agents/`

# Customized
**Subagent locations**: `/home/alice/workspace/myproject/.claude/agents/`
```

#### Modify Phase Steps
```markdown
# Add a new phase
## Phase 3.5: Security Scan → INVOKE security-scanner-agent
```

#### Change Iteration Limits
```markdown
# Original
- **Limit loop iterations** to prevent infinite loops (max 5 bugs per session)

# Customized (for more aggressive automation)
- **Limit loop iterations** to prevent infinite loops (max 10 bugs per session)
```

#### Customize Exit Conditions
```markdown
# Add custom exit condition
- **Explicit STOP command** in any bug's comments.md OR
- **Friday 5 PM** - Stop for weekend
```

**How to Preserve:**
Document changes in `.featmgmt-config.json`:
```json
{
  "customizations": {
    "overprompt": {
      "max_iterations": 10,
      "added_phases": ["security-scan"],
      "modified_paths": true
    }
  }
}
```

### 2. .agent-config.json (Agent Behavior)

**Customization Level:** High - Project-specific tags and keywords

**Common Customizations:**

#### Add Project-Specific Tags
```json
{
  "available_tags": [
    "backend",
    "frontend",
    "mobile-app",      // Added
    "third-party-api", // Added
    "payment-system",  // Added
    "infrastructure",
    ...
  ]
}
```

#### Define Component Keywords
```json
{
  "component_detection_keywords": {
    "backend": ["api", "server", "database", "backend"],
    "payment-system": ["stripe", "payment", "checkout", "billing"],
    "mobile-app": ["ios", "android", "mobile", "app"]
  }
}
```

#### Adjust Thresholds
```json
{
  "duplicate_similarity_threshold": 0.85  // Stricter duplicate detection
}
```

**Best Practice:** Keep .agent-config.json up to date as your project evolves.

### 3. Subagent Definitions

**Customization Level:** Medium - Copy and modify agents

**When to Customize:**
- Need domain-specific verification steps
- Want different prioritization logic
- Have custom git workflows
- Need integration with external tools

**How to Customize:**

1. **Copy agent from featmgmt:**
   ```bash
   cp featmgmt/claude-agents/standard/bug-processor-agent.md \
      myproject/.claude/agents/bug-processor-agent.md
   ```

2. **Modify as needed:**
   ```markdown
   # Add custom step
   ### Step 5: Run Security Scan
   Run: npm audit --audit-level=high
   ```

3. **Document customization:**
   ```bash
   echo "bug-processor-agent.md: Added security scan step" >> \
     feature-management/.featmgmt-config.json
   ```

**Note:** Customized agents won't be overwritten by sync-agents.sh (they only copy if file doesn't exist).

### 4. Directory Structure

**Customization Level:** Low - Structure is intentionally uniform

**Allowed Additions:**
```
feature-management/
├── ...
├── archived/          # Additional archive category
├── blocked/           # Blocked items separate from deprecated
├── docs/              # Additional documentation
└── scripts/           # Project-specific scripts
```

**Not Recommended:**
- Renaming core directories (bugs/, features/, completed/)
- Changing file formats (PROMPT.md, TASKS.md)
- Modifying summary file structure (bugs.md, features.md)

**Reason:** Core structure needs to remain consistent for scripts to work.

### 5. Bug/Feature Structure

**Customization Level:** Medium - Add files, keep required ones

**Required Files (per bug/feature):**
```
BUG-XXX-slug/
├── PROMPT.md          # Required: Self-executing instructions
├── bug_report.json    # Required: Metadata
└── ...
```

**Optional Additions:**
```
BUG-XXX-slug/
├── PROMPT.md
├── PLAN.md
├── TASKS.md
├── bug_report.json
├── comments.md
├── SPEC.md            # Added: Detailed specification
├── DESIGN.md          # Added: Design documentation
├── screenshots/       # Added: Visual references
└── test-data/         # Added: Test fixtures
```

### 6. Summary Files Format

**Customization Level:** Low - Format must be parseable

**Required Columns:**
```markdown
| ID | Title | Priority | Status | Component | Location |
```

**Optional Additions:**
```markdown
| ID | Title | Priority | Status | Component | Assignee | Estimate | Location |
```

**Script Compatibility:** If you modify summary file format, update scan-prioritize-agent to parse new columns.

### 7. Human Actions Structure

**Customization Level:** Medium - Add files, keep required ones

**Required Files (per action):**
```
human-actions/ACTION-XXX-slug/
├── action_report.json    # Required: Metadata
├── INSTRUCTIONS.md       # Required: Steps to complete action
└── ...
```

**action_report.json Schema:**
```json
{
  "action_id": "ACTION-001",
  "title": "Brief description of human action required",
  "component": "string (related component)",
  "urgency": "critical|high|medium|low",
  "status": "pending|in_progress|completed",
  "created_date": "YYYY-MM-DD",
  "updated_date": "YYYY-MM-DD",
  "assigned_to": "string|null",
  "tags": ["array", "of", "tags"],
  "required_expertise": "Description of skills/access needed",
  "estimated_time": "How long this will take (e.g., '30 minutes', '2 hours')",
  "description": "Detailed description of what needs to be done",
  "reason": "Why human intervention is needed instead of automation",
  "blocking_items": ["BUG-XXX", "FEAT-YYY"],
  "evidence": {
    "error_messages": "Optional error details",
    "context": "Optional additional context"
  }
}
```

**Key Field: blocking_items**

The `blocking_items` field is an array of bug/feature IDs that cannot be processed until this human action is completed. This enables the scan-prioritize-agent to:

- Detect blocking relationships between human actions and work items
- Calculate effective urgency based on highest blocked priority
- Warn users about blocked items in the priority queue
- Prevent wasted agent cycles on items that cannot proceed

**Example Usage:**
```json
{
  "action_id": "ACTION-001",
  "title": "Get production database credentials from ops team",
  "urgency": "medium",
  "blocking_items": ["BUG-003", "BUG-005", "FEAT-007"]
}
```

If BUG-003 is priority P0, scan-prioritize-agent will:

### Work Item Status Lifecycle

All work items (bugs and features) follow a consistent status lifecycle:

**Status Values:**
- `"new"` - Created by work-item-creation-agent, not yet started
- `"in_progress"` - bug-processor-agent has begun implementation
- `"resolved"` - Implementation completed and item archived
- `"deprecated"` - retrospective-agent marked as obsolete
- `"merged"` - retrospective-agent merged into another item

**Lifecycle Flow:**
```
new → in_progress → resolved → [archived to completed/]
  ↓         ↓
deprecated  deprecated
  ↓         ↓
merged    merged
```

**Date Tracking:**
- `created_date`: When work-item-creation-agent created the item
- `started_date`: When bug-processor-agent marked it in_progress (new field)
- `updated_date`: Last modification timestamp
- `completed_date`: When OVERPROMPT archived to completed/
- `deprecated_date`: When retrospective-agent deprecated it
- `merged_date`: When retrospective-agent merged it

**Consistency with Human Actions:**

Human actions use a similar 3-state model:
- `"pending"` → `"in_progress"` → `"completed"`

This alignment ensures consistent status semantics across all work item types.
1. Recalculate ACTION-001 urgency to "critical" (blocks P0 item)
2. Mark BUG-003 as blocked in priority queue
3. Display prominent warning to complete ACTION-001 first
4. Include ACTION-001 in human_actions_required output

**Optional Additions:**
```
ACTION-XXX-slug/
├── action_report.json
├── INSTRUCTIONS.md
├── comments.md           # Added: Progress notes
├── screenshots/          # Added: Visual guides
├── credentials.md        # Added: Access details (git-ignored!)
└── verification.md       # Added: How to verify completion
```

## Variant-Specific Customizations

### Standard Variant

**Test Commands:**
```markdown
# Customize test runner
Run tests: npm test           # Original
Run tests: poetry run pytest  # Customized for Python project
```

**Component Types:**
```json
{
  "available_tags": [
    "react-frontend",      // Instead of generic "frontend"
    "graphql-api",         // Instead of generic "api"
    "postgres-database"    // Specific database
  ]
}
```

### GitOps Variant

**Verification Commands:**
```markdown
# Customize infrastructure checks
kubectl get pods -A                          # Original
kubectl get pods -A && istioctl proxy-status # Added: Istio check
```

**Infrastructure Components:**
```json
{
  "available_tags": [
    "kubernetes",
    "helm",
    "flux",
    "istio",              // Added: Service mesh
    "cert-manager",       // Added: Certificate management
    "sealed-secrets"      // Added: Secret management
  ]
}
```

## Advanced Customizations

### Custom Subagents

Create entirely new agents for project-specific needs:

**Example: security-scanner-agent.md**
```markdown
---
name: security-scanner-agent
description: Scans codebase for security vulnerabilities
tools: Bash, Read, Grep
---

# Security Scanner Agent

## Purpose
Run security scans on code changes before committing.

## Tools to Run
- npm audit
- trivy
- git-secrets
- Custom static analysis

## Output
Return security scan results with severity levels.
```

Add to OVERPROMPT.md:
```markdown
## Phase 3.5: Security Scan → INVOKE security-scanner-agent
```

### Project-Specific Scripts

Add custom automation in feature-management/scripts/:

**Example: weekly-report.sh**
```bash
#!/bin/bash
# Generate weekly summary of bugs/features

cd $(dirname $0)/..

echo "Weekly Report: $(date +%Y-%m-%d)"
echo ""
echo "Bugs Completed This Week:"
git log --since="1 week ago" --grep="^Archive BUG-" --oneline
echo ""
echo "Features Implemented This Week:"
git log --since="1 week ago" --grep="^Archive FEAT-" --oneline
```

### Custom OVERPROMPT Sections

Add project-specific instructions:

```markdown
## Project-Specific Rules

### Database Migrations
- All schema changes require migration files
- Test migrations in staging before production
- Update SCHEMA.md after schema changes

### API Changes
- Update OpenAPI spec when changing endpoints
- Increment API version for breaking changes
- Add deprecation notices before removing endpoints

### Security Requirements
- No hardcoded credentials (use environment variables)
- All endpoints require authentication except /health
- Sanitize all user inputs
```

## Preserving Customizations During Updates

### Strategy 1: Document in .featmgmt-config.json

```json
{
  "customizations": {
    "description": "List all customizations here",
    "overprompt_sections_added": [
      "Phase 3.5: Security Scan",
      "Project-Specific Rules section"
    ],
    "overprompt_paths_modified": true,
    "custom_agents": [
      "security-scanner-agent",
      "performance-profiler-agent"
    ],
    "custom_tags": [
      "payment-system",
      "third-party-api"
    ]
  }
}
```

### Strategy 2: Backup Before Updates

```bash
# Always run update with --dry-run first
./scripts/update-project.sh --dry-run ../myproject/feature-management

# Review changes
# Then run actual update (creates automatic backup)
./scripts/update-project.sh ../myproject/feature-management

# If issues, rollback
cd ../myproject/feature-management
git reset --hard HEAD~1
```

### Strategy 3: Manual Merge

If update overwrites customizations:

```bash
# Compare current with backup
diff OVERPROMPT.md .featmgmt-backup-*/OVERPROMPT.md

# Manually merge customizations back
# Edit OVERPROMPT.md to restore custom sections
git add OVERPROMPT.md
git commit --amend
```

## Best Practices

### 1. Document Everything

**In .featmgmt-config.json:**
- List all customizations
- Explain why you made changes
- Note dependencies

**In feature-management/docs/:**
- Team conventions
- Project-specific workflows
- Customization rationale

### 2. Test Customizations

After customizing:
```bash
# Test workflow with a dummy bug
cd feature-management
# Create test bug
# Run OVERPROMPT.md
# Verify agents work correctly
```

### 3. Keep Core Structure

**Don't modify:**
- Directory names (bugs/, features/, completed/)
- Required files (PROMPT.md, bug_report.json)
- Summary file column headers
- Version files (.featmgmt-version)

**Why:** Scripts depend on these conventions.

### 4. Version Your Customizations

```bash
# Commit customizations separately
git add OVERPROMPT.md
git commit -m "Customize OVERPROMPT: Add security scan phase"

git add .agent-config.json
git commit -m "Customize tags: Add payment-system component"
```

**Benefit:** Easy to see what you've customized when reviewing git history.

### 5. Contribute Back

If your customization would benefit others:
1. Generalize the change
2. Submit PR to featmgmt repo
3. Help improve the pattern for everyone

## Human-in-the-Loop Workflow with PR Review

Agents can create work items on a separate branch for human review before they enter the master backlog. This creates a quality control checkpoint where humans can consolidate, refine, or reject auto-created items.

### Benefits

- **Quality Control**: Catch agent mistakes before they waste processing cycles
- **Pattern Recognition**: "These 5 bugs are symptoms of one root cause"
- **Batch Review**: Review all auto-created items from a session at once
- **Easy Rejection**: Close PR to discard all items if agent misbehaved
- **Preserves Autonomy**: Processing is still autonomous, just gated at input
- **Audit Trail**: PR shows what was created and why

### Workflow

```
Agent detects issue(s)
    ↓
Agent creates branch: "auto-items-YYYY-MM-DD-HHMMSS"
    ↓
Invoke work-item-creation-agent multiple times (items created on branch)
    ↓
Agent commits all items with descriptive message
    ↓
Agent pushes branch to origin
    ↓
Agent creates PR using `gh pr create`
    ↓
Human reviews PR:
  - Consolidates duplicates
  - Improves descriptions
  - Rejects false positives
  - Approves valid items
    ↓
Merge PR → Items enter master backlog
    ↓
Next OVERPROMPT session processes approved items
```

### When to Use

**Use PR workflow when:**
- Creating 3+ items in a single session (batch review valuable)
- Items are based on pattern detection and may need consolidation
- Creating speculative items that might be false positives
- Multiple items might share a root cause

**Commit directly to master when:**
- Single critical item that should enter backlog immediately
- Human has already approved the item (e.g., user-requested bug/feature)
- High-confidence item creation

### Example Usage

#### retrospective-agent Creates 5 Pattern-Based Bugs

**Agent workflow:**
```markdown
1. Pattern analysis detects recurring test failures
2. Generate branch name: auto-items-2025-10-24-153045
3. For each bug:
   - Invoke work-item-creation-agent with branch_name and auto_commit: false
4. Stage all created items: git add bugs/
5. Commit with descriptive message listing all items
6. Push branch: git push -u origin auto-items-2025-10-24-153045
7. Create PR with gh pr create:
   - Title: "Auto-created items from retrospective-agent - 2025-10-24"
   - Body: Summary of all items with links to PROMPT.md
   - Labels: "auto-created"
8. Return PR URL to user
```

**Human reviews PR:**
- Realizes bugs #1-3 share root cause (OAuth token handling)
- Consolidates into single comprehensive bug
- Improves description with additional context
- Merges PR

**Result**: 3 bugs instead of 5, better specified, enters master backlog for processing.

#### test-runner-agent Creates Bugs from 7 Test Failures

**Agent workflow:**
```markdown
1. Test run detects 7 failures
2. Threshold check: 7 ≥ 5, use PR workflow
3. Generate branch name: auto-items-2025-10-24-161030
4. For each failure:
   - Invoke work-item-creation-agent with branch_name and auto_commit: false
5. Stage all bugs: git add bugs/
6. Commit with test failure details
7. Push branch and create PR
8. PR includes test run statistics and failure details
```

**Human reviews PR:**
- Sees 4 failures are in same module (authentication)
- Identifies they're symptoms of missing error handling
- Consolidates to 1 bug + 1 feature request
- Rejects 1 bug as environmental issue (test setup)
- Merges PR

**Result**: 2 items instead of 7, better prioritized, no false positives in backlog.

### Agent Support

Agents that support PR-based workflows:

- **work-item-creation-agent**: Accepts optional `branch_name` parameter
  - If provided: Creates/checks out branch before creating files
  - If not provided: Works on current branch (backward compatible)

- **retrospective-agent**: Creates PR for 3+ items from pattern analysis
  - Threshold: 3+ items → PR workflow
  - 1-2 items → Direct commit to master

- **test-runner-agent**: Creates PR for 5+ test failures
  - Threshold: 5+ failures → PR workflow
  - 1-4 failures → Direct commit to master

### Technical Details

**Branch Naming Convention**: `auto-items-YYYY-MM-DD-HHMMSS`

**Example**: `auto-items-2025-10-24-153045`

**work-item-creation-agent Input**:
```json
{
  "item_type": "bug",
  "title": "Recurring test failure in OAuth module",
  "branch_name": "auto-items-2025-10-24-153045",
  "auto_commit": false,
  ...
}
```

**PR Creation** (using GitHub CLI):
```bash
gh pr create \
  --title "Auto-created items from retrospective-agent - 2025-10-24" \
  --body "..." \
  --base master \
  --label "auto-created"
```

**GitHub CLI Requirement**: This feature requires `gh` (GitHub CLI) to be installed. If not available, agents will provide manual instructions for creating PRs via git push and GitHub web interface.

### Customizing the Workflow

**Adjust Thresholds**:

In your agent customizations or agent-config.json:
```json
{
  "pr_workflow_thresholds": {
    "retrospective_agent_min_items": 5,  // Default: 3
    "test_runner_agent_min_failures": 10  // Default: 5
  }
}
```

**Custom PR Templates**:

Customize PR body templates in your local agent copies to match your team's review process.

**Additional Labels**:

Add project-specific labels to PRs for better filtering:
```bash
gh pr create ... --label "auto-created" --label "needs-triage" --label "sprint-planning"
```

## Example Customizations

### Example 1: Python Project with Poetry

**.agent-config.json:**
```json
{
  "available_tags": [
    "api",
    "workers",
    "models",
    "poetry-dependencies"
  ],
  "component_detection_keywords": {
    "api": ["fastapi", "endpoint", "router"],
    "workers": ["celery", "task", "worker"],
    "models": ["pydantic", "sqlalchemy", "model"]
  }
}
```

**OVERPROMPT.md customization:**
```markdown
## Phase 3: Test → INVOKE test-runner-agent

**Invoke test-runner-agent:**
\`\`\`
Task tool parameters:
- prompt: "Set up test environment with poetry install,
           activate virtual environment, run pytest with coverage"
\`\`\`
```

### Example 2: Kubernetes Infrastructure Project

**.agent-config.json:**
```json
{
  "available_tags": [
    "kubernetes",
    "helm-charts",
    "flux-kustomizations",
    "network-policies",
    "rbac",
    "monitoring"
  ],
  "component_detection_keywords": {
    "helm-charts": ["helm", "chart", "values.yaml"],
    "flux-kustomizations": ["flux", "kustomization", "gitops"],
    "network-policies": ["network", "policy", "ingress", "egress"]
  }
}
```

**OVERPROMPT.md customization:**
```markdown
## Phase 3: Verify → INVOKE verification-agent

**Verification steps:**
1. Flux reconciliation status
2. Pod health checks
3. Service mesh status (Istio)
4. Certificate validity
5. Network policy enforcement
```

## When NOT to Customize

### Red Flags

- Changing file formats breaks parsers
- Renaming core directories breaks scripts
- Removing required files breaks agents
- Drastically different workflow than template

**If you need radical changes:** Consider forking featmgmt and creating your own variant rather than heavy customization.

## Getting Help

If customization breaks something:

1. **Check UPDATE_LOG.md** - See what changed
2. **Compare with template** - Run compare-with-template.sh
3. **Review backups** - Look in .featmgmt-backup-*/
4. **Test with minimal bug** - Create simple test case
5. **Rollback if needed** - git reset or restore from backup

## Summary

**Customize Freely:**
- OVERPROMPT.md workflow
- .agent-config.json tags
- Add custom agents
- Add custom scripts
- Add project documentation

**Keep Standard:**
- Directory structure
- File naming conventions
- Summary file format
- Required files

**Document Everything:**
- .featmgmt-config.json
- Git commit messages
- Local docs/

The featmgmt pattern is designed to be customized. Make it yours!

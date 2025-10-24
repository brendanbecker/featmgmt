# BUG-003: Subagents not available - scan-prioritize-agent and others missing

**Priority**: P0
**Component**: agents/infrastructure
**Severity**: critical
**Status**: new

## Problem Statement

The OVERPROMPT.md workflow requires specialized subagents (scan-prioritize-agent, bug-processor-agent, test-runner-agent, git-ops-agent, retrospective-agent, summary-reporter-agent) but they don't exist in `.claude/agents/` directory. This forces manual fallback execution for all phases, which:

- Increases error risk
- Makes sessions harder to review
- Defeats the purpose of agent delegation
- Violates the OVERPROMPT's design intent

## Root Cause Investigation Needed

1. **Check if agents can be installed globally** in `~/.claude/agents/` (user home directory)
2. If yes, update `scripts/sync-agents.sh` to support both:
   - Local project: `.claude/agents/` (current behavior)
   - Global: `~/.claude/agents/` (new option)
3. Update `scripts/init-project.sh` to offer global vs local agent installation
4. Document the recommended approach in CLAUDE.md

## Implementation Tasks

### Task 1: Research Global Agent Installation

**File**: Investigation work

```bash
# Test if Claude Code supports global agents in ~/.claude/agents/
mkdir -p ~/.claude/agents/test-agent
# Create a minimal test agent
# Verify if Claude Code can find and invoke it from any project
```

Document findings:
- Does `~/.claude/agents/` work for global agent availability?
- Are there any limitations or caveats?
- What's the recommended approach?

### Task 2: Update sync-agents.sh (If Global Works)

**File**: `scripts/sync-agents.sh`

Add `--global` flag support:

```bash
# New flag handling
GLOBAL=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --global)
      GLOBAL=true
      shift
      ;;
    # ... existing cases ...
  esac
done

# Update target directory logic
if [ "$GLOBAL" = true ]; then
  TARGET_DIR="$HOME/.claude/agents"
  echo "Syncing to global agents directory: $TARGET_DIR"
else
  TARGET_DIR="$PROJECT_ROOT/.claude/agents"
  echo "Syncing to project agents directory: $TARGET_DIR"
fi
```

### Task 3: Update init-project.sh

**File**: `scripts/init-project.sh`

Add agent installation prompt:

```bash
# After project type selection, before copying templates
echo ""
echo "Agent Installation Location:"
echo "  1) Local (.claude/agents/ in project) - agents available only for this project"
echo "  2) Global (~/.claude/agents/) - agents available for all projects"
echo ""
read -p "Choose installation location [1-2]: " agent_location

if [ "$agent_location" = "2" ]; then
  SYNC_GLOBAL="--global"
else
  SYNC_GLOBAL=""
fi

# Later, when syncing agents:
"$SCRIPT_DIR/sync-agents.sh" $SYNC_GLOBAL "$PROJECT_TYPE" "$TARGET_DIR"
```

### Task 4: Update Documentation

**File**: `CLAUDE.md`

Add section on agent installation:

```markdown
## Agent Installation

featmgmt subagents can be installed in two locations:

### Global Installation (Recommended)

Agents are available to all projects using featmgmt:
```bash
./scripts/sync-agents.sh --global standard
# or
./scripts/sync-agents.sh --global gitops
```

Agents installed to: `~/.claude/agents/`

**Benefits:**
- Agents available across all projects
- Single source of truth - update once, affects all
- Cleaner project repositories (no .claude/ directory)

**Drawbacks:**
- Different projects might need different agent versions
- Changes affect all projects simultaneously

### Local Installation

Agents are scoped to specific project:
```bash
./scripts/sync-agents.sh standard /path/to/project
```

Agents installed to: `/path/to/project/.claude/agents/`

**Benefits:**
- Version isolation per project
- Safe to customize agents for specific needs
- Explicit control over agent updates

**Drawbacks:**
- Duplication across projects
- Must sync separately for each project
```

### Task 5: Verify All Required Agents

Ensure all 6 required agents exist in `claude-agents/`:

1. **scan-prioritize-agent** (shared)
2. **bug-processor-agent** (standard) / **infra-executor-agent** (gitops)
3. **test-runner-agent** (standard) / **verification-agent** (gitops)
4. **git-ops-agent** (shared)
5. **retrospective-agent** (shared)
6. **summary-reporter-agent** (shared)

Check agent definitions are complete and up-to-date.

### Task 6: Test OVERPROMPT Workflow

After agents are installed (global or local):

1. Open `feature-management/OVERPROMPT.md`
2. Execute Phase 1: Scan & Prioritize
3. Verify agent invocation works (no manual fallback)
4. Execute remaining phases
5. Verify all agent delegations succeed

## Acceptance Criteria

- [ ] Investigate whether `~/.claude/agents/` works for global agent availability
- [ ] If yes, update `sync-agents.sh` to support `--global` flag
- [ ] Update `init-project.sh` to ask: "Install agents globally or locally?"
- [ ] Ensure all 6 required agents are properly installed and discoverable
- [ ] Test OVERPROMPT.md workflow with proper agent delegation (no manual fallbacks)
- [ ] Update documentation with installation recommendations
- [ ] All phases successfully delegate to specialized agents
- [ ] Session outputs are structured (from agents, not manual execution)

## Evidence of Success

- Running OVERPROMPT.md successfully invokes agents without "agent not found" errors
- Session reports show structured outputs from each agent phase
- `ls ~/.claude/agents/` or `ls .claude/agents/` shows all 6 required agents
- Documentation clearly explains installation options and tradeoffs

## Notes

This is a **critical blocker** for the autonomous workflow. Until agents are properly installed, OVERPROMPT cannot function as designed. Prioritize this investigation and implementation.

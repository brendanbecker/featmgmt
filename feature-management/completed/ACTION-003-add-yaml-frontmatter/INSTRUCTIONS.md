# ACTION-003: Add YAML Frontmatter to Agent Definitions

## Related To
- **Bug**: BUG-005
- **Component**: claude-agents
- **Priority**: P2

## Objective
Add proper YAML frontmatter to agent definition files that are missing it, ensuring Claude Code can properly discover and register all agents.

## Issue Details

**Found During**: Verification of BUG-005 changes
**Impact**: Agents without frontmatter may not be properly recognized by Claude Code

### Agents Missing Frontmatter

1. **work-item-creation-agent.md** (claude-agents/shared/)
2. **task-scanner-agent.md** (claude-agents/gitops/)
3. **infra-executor-agent.md** (claude-agents/gitops/)
4. **verification-agent.md** (claude-agents/gitops/)

### Agents With Proper Frontmatter (Examples)

- retrospective-agent.md ✅
- summary-reporter-agent.md ✅
- bug-processor-agent.md ✅
- scan-prioritize-agent.md ✅
- test-runner-agent.md ✅

## YAML Frontmatter Pattern

```yaml
---
name: agent-name
description: Brief description of agent purpose and responsibilities
tools: Read, Write, Edit, Bash, Grep, Glob
---
```

## Steps to Complete

### 1. Add Frontmatter to work-item-creation-agent.md

**File**: `/home/becker/projects/featmgmt/claude-agents/shared/work-item-creation-agent.md`

**Add at the very beginning:**
```yaml
---
name: work-item-creation-agent
description: Standardized creation of bugs, features, and human action items with duplicate detection, ID generation, and optional auto-commit
tools: Read, Write, Bash, Grep, Glob
---

```

### 2. Add Frontmatter to task-scanner-agent.md

**File**: `/home/becker/projects/featmgmt/claude-agents/gitops/task-scanner-agent.md`

**Add at the very beginning:**
```yaml
---
name: task-scanner-agent
description: Scans infrastructure task repositories for active and backlog tasks, builds priority queue based on criticality and dependencies
tools: Read, Grep, Bash
---

```

### 3. Add Frontmatter to infra-executor-agent.md

**File**: `/home/becker/projects/featmgmt/claude-agents/gitops/infra-executor-agent.md`

**Add at the very beginning:**
```yaml
---
name: infra-executor-agent
description: Executes infrastructure tasks including builds, deployments, configs, and cluster operations, following acceptance criteria and committing changes
tools: Read, Edit, Write, Bash, Grep, Glob
---

```

### 4. Add Frontmatter to verification-agent.md

**File**: `/home/becker/projects/featmgmt/claude-agents/gitops/verification-agent.md`

**Add at the very beginning:**
```yaml
---
name: verification-agent
description: Verifies infrastructure changes, checks cluster health, service availability, deployments, and image registry status
tools: Bash, Read, Grep
---

```

## Verification Commands

### Check Frontmatter Format
```bash
cd /home/becker/projects/featmgmt/claude-agents

# Check each file starts with ---
for file in shared/work-item-creation-agent.md gitops/*.md; do
  echo "=== $file ==="
  head -n 1 "$file"
done
```

### Verify YAML Structure
```bash
# Extract frontmatter from each file
for file in shared/work-item-creation-agent.md gitops/*.md; do
  echo "=== $file ==="
  sed -n '/^---$/,/^---$/p' "$file"
  echo ""
done
```

### Compare with Working Examples
```bash
# View frontmatter from working agents
head -n 5 claude-agents/standard/bug-processor-agent.md
head -n 5 claude-agents/shared/retrospective-agent.md
```

## Tool Selection Guidelines

**Read**: Reading files, configuration, metadata
**Write**: Creating new files
**Edit**: Modifying existing files
**Bash**: Shell commands, git operations, kubectl, etc.
**Grep**: Searching file contents
**Glob**: Finding files by pattern

## Completion Checklist
- [ ] work-item-creation-agent.md has frontmatter
- [ ] task-scanner-agent.md has frontmatter
- [ ] infra-executor-agent.md has frontmatter
- [ ] verification-agent.md has frontmatter
- [ ] All frontmatter has proper --- delimiters
- [ ] All frontmatter includes name, description, tools
- [ ] YAML syntax validated
- [ ] Files still render correctly

## Results
**Status**: [PENDING / COMPLETE / FAILED]
**Completed By**: [Your Name]
**Date**: [YYYY-MM-DD]
**Notes**:

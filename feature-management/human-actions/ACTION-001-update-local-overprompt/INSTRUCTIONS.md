# ACTION-001: Update Local OVERPROMPT.md

## Related To
- **Bug**: BUG-005
- **Component**: feature-management
- **Priority**: P1

## Objective
Update the local feature-management/OVERPROMPT.md file to remove all git-ops-agent references and align with the updated template.

## Issue Details

**Found During**: Verification of BUG-005 changes
**Current State**: feature-management/OVERPROMPT.md contains 8 references to git-ops-agent
**Expected State**: Template templates/OVERPROMPT-standard.md has been correctly updated with no git-ops-agent references

### References Found
```
Line 18: 3. **git-ops-agent**: Handles all git operations (branch, commit, push, PR)
Line 109: ## Phase 4: Git Operations → INVOKE git-ops-agent
Line 111: **IMMEDIATELY invoke git-ops-agent after tests pass:**
Line 115: - subagent_type: "git-ops-agent"
Line 133: ## Phase 5: Update Status & Archive → INVOKE git-ops-agent
Line 135: **IMMEDIATELY invoke git-ops-agent to update summary and archive:**
Line 139: - subagent_type: "git-ops-agent"
Line 252: [Phase 4] INVOKE git-ops-agent (commit & push)
Line 258: [Phase 5] INVOKE git-ops-agent (archive & update summary)
```

## Steps to Complete

### 1. Backup Current File
```bash
cp /home/becker/projects/featmgmt/feature-management/OVERPROMPT.md \
   /home/becker/projects/featmgmt/feature-management/OVERPROMPT.md.backup
```

### 2. Update File
```bash
cp /home/becker/projects/featmgmt/templates/OVERPROMPT-standard.md \
   /home/becker/projects/featmgmt/feature-management/OVERPROMPT.md
```

### 3. Verify Changes
```bash
cd /home/becker/projects/featmgmt
grep -n "git-ops-agent" feature-management/OVERPROMPT.md
# Should return no results
```

### 4. Verify Markdown Syntax
```bash
# Check balanced code blocks
grep -c '```' feature-management/OVERPROMPT.md
# Should be an even number

# Check headers
grep '^#' feature-management/OVERPROMPT.md
# Should show proper header hierarchy
```

## Expected Changes

### Removed Content
- All references to "git-ops-agent"
- Phase 4: Git Operations section invoking git-ops-agent
- Phase 5: Archive section invoking git-ops-agent

### Updated Content
- Agent list should show agents performing their own git operations
- Phase descriptions should reference agents committing their own work
- Note: "Each agent is responsible for committing its own work"

## Verification

Run this verification command:
```bash
cd /home/becker/projects/featmgmt
echo "=== Checking for git-ops-agent references ==="
grep -c "git-ops-agent" feature-management/OVERPROMPT.md || echo "PASS: No references found"

echo "=== Checking markdown structure ==="
CODE_BLOCKS=$(grep -c '```' feature-management/OVERPROMPT.md)
if [ $((CODE_BLOCKS % 2)) -eq 0 ]; then
  echo "PASS: Code blocks balanced ($CODE_BLOCKS)"
else
  echo "FAIL: Code blocks unbalanced ($CODE_BLOCKS)"
fi
```

## Completion Checklist
- [ ] Backup created
- [ ] File updated from template
- [ ] No git-ops-agent references remain
- [ ] Markdown syntax is valid
- [ ] File reads correctly in editor
- [ ] Verification commands pass

## Results
**Status**: [PENDING / COMPLETE / FAILED]
**Completed By**: [Your Name]
**Date**: [YYYY-MM-DD]
**Notes**:

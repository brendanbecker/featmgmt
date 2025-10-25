# ACTION-002: Remove git-ops-agent.md from Local Agents

## Related To
- **Bug**: BUG-005
- **Component**: .claude/agents
- **Priority**: P1

## Objective
Delete the obsolete git-ops-agent.md file from the local .claude/agents/ directory to prevent Claude Code from discovering and offering the removed agent.

## Issue Details

**Found During**: Verification of BUG-005 changes
**Current State**: /home/becker/projects/featmgmt/.claude/agents/git-ops-agent.md exists (9561 bytes)
**Expected State**: File should not exist (git-ops-agent has been removed from claude-agents/shared/)

## Why This Matters

1. **Agent Discovery**: Claude Code discovers agents at session start from .claude/agents/
2. **Stale Reference**: The local copy is now obsolete and inconsistent with templates
3. **User Confusion**: Users may try to invoke git-ops-agent which no longer exists in source
4. **Sync Issue**: Next sync-agents.sh run won't remove this file automatically

## Steps to Complete

### 1. Verify File Exists
```bash
ls -lh /home/becker/projects/featmgmt/.claude/agents/git-ops-agent.md
```

Expected: File exists with size ~9.5 KB

### 2. Delete the File
```bash
rm /home/becker/projects/featmgmt/.claude/agents/git-ops-agent.md
```

### 3. Verify Deletion
```bash
ls /home/becker/projects/featmgmt/.claude/agents/git-ops-agent.md
# Should return: No such file or directory
```

### 4. Restart Claude Code Session
**IMPORTANT**: Claude Code only discovers agents at session startup.

1. Close your current Claude Code session
2. Reopen Claude Code
3. Verify git-ops-agent is NOT in the available agents list

### 5. Verify Other Agents Still Work
After restart, verify these agents are still available:
- scan-prioritize-agent
- bug-processor-agent
- test-runner-agent
- retrospective-agent
- summary-reporter-agent

## Completion Checklist
- [ ] File verified to exist
- [ ] File deleted successfully
- [ ] Deletion verified with ls command
- [ ] Claude Code session restarted
- [ ] git-ops-agent NOT in available agents
- [ ] Other agents still available

## Results
**Status**: [PENDING / COMPLETE / FAILED]
**Completed By**: [Your Name]
**Date**: [YYYY-MM-DD]
**Notes**:

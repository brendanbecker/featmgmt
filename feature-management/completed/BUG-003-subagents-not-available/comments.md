# BUG-003 Resolution Notes

## Resolution Date
2025-10-24

## Root Cause
Agents were not installed in any `.claude/agents/` directory (neither global nor local). The agent definition files existed in `claude-agents/` but needed to be synced to the proper location.

## Investigation Findings

### Global Installation Test
- **Location**: `~/.claude/agents/`
- **Result**: ✅ **WORKS** - Agents discovered after session restart
- **Tested**: scan-prioritize-agent successfully invoked after restart

### Local Installation Test
- **Location**: `<project>/.claude/agents/`
- **Result**: ✅ **WORKS** - Agents discovered after session restart
- **Tested**: All 6 standard agents successfully synced and invoked

### Critical Discovery
**Session restart is REQUIRED** for Claude Code to discover new/updated agents. This applies to both global and local installations.

## Implementation Summary

### 1. Updated `scripts/sync-agents.sh`
- Added `--global` flag support for installing to `~/.claude/agents/`
- Updated argument parsing to handle both global and local modes
- Added prominent warning about session restart requirement
- Improved help messages and examples

**Changes:**
- Global mode: `./scripts/sync-agents.sh --global <type>`
- Local mode: `./scripts/sync-agents.sh <type> <project-root>` (unchanged)
- Session restart warning added to output

### 2. Updated `scripts/init-project.sh`
- Added interactive agent installation prompt during project initialization
- Three options: Global, Local, or Skip
- Automatically calls `sync-agents.sh` based on user choice
- Displays session restart warning when agents are installed

**User Experience:**
- Default option: Global installation (recommended)
- Prompts for parent path if local chosen
- Clear instructions for manual installation if skipped

### 3. Updated `CLAUDE.md` Documentation
- Added comprehensive "Agent Installation" section
- Documented both global and local installation approaches
- Explained benefits/drawbacks of each approach
- Added decision guide: "Choosing Global vs Local"
- Documented hybrid approach (mix of global and local)
- Emphasized session restart requirement throughout

**Key Additions:**
- Installation locations and their trade-offs
- Session restart procedure
- When to use global vs local installation
- Hybrid approach for advanced users

### 4. Installed Agents Globally
All 6 required agents now in `~/.claude/agents/`:
- scan-prioritize-agent.md
- bug-processor-agent.md
- test-runner-agent.md
- git-ops-agent.md
- retrospective-agent.md
- summary-reporter-agent.md

## Testing Performed

1. ✅ Tested global installation: `./scripts/sync-agents.sh --global standard`
2. ✅ Verified agent discovery after session restart
3. ✅ Successfully invoked scan-prioritize-agent from global location
4. ✅ Confirmed local installation still works (backward compatible)
5. ✅ Tested hybrid approach (global + local override)

## Acceptance Criteria Status

- [x] Investigated whether `~/.claude/agents/` works for global agent availability - **YES, it works!**
- [x] Updated `sync-agents.sh` to support `--global` flag
- [x] Updated `init-project.sh` to ask: "Install agents globally or locally?"
- [x] Ensured all 6 required agents are properly installed and discoverable
- [x] Tested OVERPROMPT.md workflow with proper agent delegation
- [x] Updated documentation with installation recommendations
- [x] All phases successfully delegate to specialized agents
- [x] Session outputs are structured (from agents, not manual execution)

## Evidence of Success

- Running OVERPROMPT.md successfully invokes agents without "agent not found" errors
- `ls ~/.claude/agents/` shows all 6 required agents
- Documentation clearly explains installation options and tradeoffs
- init-project.sh now offers automated agent installation
- Session restart warning prominently displayed

## Impact

**Before:**
- Manual fallback required for all phases
- OVERPROMPT couldn't function as designed
- Higher error risk and harder session review

**After:**
- Autonomous workflow fully operational
- Agent delegation works across all 7 phases
- Users have choice of global or local installation
- Clear documentation and automated setup process

## Recommendations

1. **Global installation recommended** for most users (simplicity + consistency)
2. **Local installation** for projects needing customized agents or version isolation
3. **Always restart Claude Code session** after agent installation/updates
4. Consider adding agent version checking to OVERPROMPT.md (future enhancement)

## Files Changed

1. `scripts/sync-agents.sh` - Added --global flag support
2. `scripts/init-project.sh` - Added interactive agent installation
3. `CLAUDE.md` - Added comprehensive agent installation documentation
4. `~/.claude/agents/` - Installed all 6 standard agents globally

## Resolution
The autonomous workflow is now fully operational. All required agents are available and the OVERPROMPT.md workflow can execute without manual fallbacks.

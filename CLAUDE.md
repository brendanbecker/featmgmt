# CLAUDE.md - Experimental Skills Migration

This file provides guidance to Claude Code (claude.ai/code) when working in this experimental branch.

## What is This Branch?

This is the `experimental/skills-replacement` branch of the featmgmt repository, checked out as a git worktree at `/home/becker/projects/featmgmt-skills`.

**Purpose:** Evaluate replacing the current subagent pattern with Claude Skills for the featmgmt workflow automation.

**Status:** Experimental - Not yet merged to master

## Key Differences from Main Branch

### Architecture Shift: Subagents → Skills

**Current (main branch):**
- Uses Claude Code subagents invoked via Task tool
- Agents defined in `claude-agents/` directory
- Synced to consuming projects' `.claude/agents/`
- Invoked from OVERPROMPT.md workflow

**Experimental (this branch):**
- Replacing subagents with Claude Skills
- Skills registered in `.claude/skills/registry.json`
- Skills invoked via Skill tool (not Task tool)
- Same workflow structure, different execution mechanism

## Directory Structure

```
/home/becker/projects/featmgmt-skills/
├── .claude/
│   ├── agents/           # Legacy: Synced subagents (for comparison)
│   └── skills/           # NEW: Skills registry and implementations
│       └── registry.json
├── feature-management/   # Git submodule for tracking this migration
│   ├── bugs/
│   ├── features/         # Contains 5 Skills migration features
│   ├── OVERPROMPT.md     # Workflow orchestrator
│   └── ...
├── claude-agents/        # Source templates (unchanged)
├── scripts/              # Utilities (unchanged)
└── templates/            # Workflow templates (may be modified)
```

## Feature Management Submodule

The `feature-management/` directory is a **git submodule** pointing to:
- Repository: `git@github.com:brendanbecker/featmgmt-feature-management.git`
- Purpose: Track the Skills migration work using featmgmt's own pattern (dogfooding)

### Working with the Submodule

**Make changes in feature-management:**
```bash
cd feature-management
# Make changes (edit bugs, features, PROMPT.md files, etc.)
git add .
git commit -m "Description of changes"
git push
```

**Update parent repository to track submodule changes:**
```bash
cd /home/becker/projects/featmgmt-skills
git add feature-management
git commit -m "Update feature-management submodule"
git push
```

**Pull latest submodule changes:**
```bash
git submodule update --remote feature-management
```

## Current Features Being Developed

Five Skills are planned to replace the current subagents:

| ID | Skill | Priority | Replaces Agent |
|----|-------|----------|----------------|
| FEAT-001 | Intelligent Priority Manager | P0 | scan-prioritize-agent |
| FEAT-002 | Stateful Workflow Orchestrator | P0 | (new capability) |
| FEAT-003 | Git Operations Expert | P1 | git-ops-agent |
| FEAT-004 | Test Intelligence Suite | P1 | test-runner-agent |
| FEAT-005 | Cross-Project Coordinator | P2 | (new capability) |

See `feature-management/features/features.md` for details.

## Development Workflow

### 1. Create Feature Request Directories

For each feature, create a directory structure:
```bash
cd feature-management/features
mkdir -p FEAT-001-priority-manager
cd FEAT-001-priority-manager
# Create PROMPT.md, feature_request.json, etc.
```

### 2. Execute OVERPROMPT.md

```bash
cd /home/becker/projects/featmgmt-skills/feature-management
# Open OVERPROMPT.md with Claude Code and run the workflow
```

### 3. Develop Skills

Skills will be created in `.claude/skills/` directory:
```bash
.claude/skills/
├── registry.json
├── priority-manager.md
├── workflow-orchestrator.md
├── git-ops-expert.md
├── test-intelligence.md
└── cross-project-coordinator.md
```

### 4. Test and Iterate

- Test skills in isolation
- Compare performance with subagent equivalents
- Document differences and improvements
- Update feature-management tracking

## Important Commands

### Git Operations

**Push changes to experimental branch:**
```bash
cd /home/becker/projects/featmgmt-skills
git add .
git commit -m "Description"
git push origin experimental/skills-replacement
```

**Switch back to main repository:**
```bash
cd /home/becker/projects/featmgmt
git status  # Shows master branch
```

**List worktrees:**
```bash
cd /home/becker/projects/featmgmt
git worktree list
```

### Feature Management

**Run the workflow:**
```bash
# Open OVERPROMPT.md in Claude Code
cd /home/becker/projects/featmgmt-skills/feature-management
# Execute OVERPROMPT.md
```

**Sync agents (for comparison):**
```bash
./scripts/sync-agents.sh standard /home/becker/projects/featmgmt-skills
```

## Success Criteria

This experimental branch will be considered successful if:

1. **Functionality**: Skills can perform all functions of current subagents
2. **Performance**: Comparable or better execution speed
3. **Maintainability**: Easier to develop and debug than subagents
4. **Usability**: Better developer experience for consuming projects
5. **Documentation**: Clear migration path for existing featmgmt users

## Merge Strategy

**If successful:**
1. Complete all 5 Skills implementations
2. Update templates to use Skills instead of subagents
3. Document migration guide for consuming projects
4. Merge `experimental/skills-replacement` → `master`
5. Bump version to 2.0.0 (breaking change)

**If unsuccessful:**
1. Document findings in `feature-management/agent_runs/`
2. Archive experimental branch
3. Continue with subagent pattern in main branch

## Key Files to Modify

When developing Skills, you'll likely need to modify:

- `.claude/skills/registry.json` - Register new skills
- `.claude/skills/*.md` - Skill implementations
- `feature-management/OVERPROMPT.md` - Update workflow to invoke skills
- `templates/OVERPROMPT-standard.md` - Update template if workflow changes
- `templates/OVERPROMPT-gitops.md` - Update template if workflow changes

## Related Documentation

- Main README: `/home/becker/projects/featmgmt/README.md`
- Architecture docs: `docs/ARCHITECTURE.md`
- Customization guide: `docs/CUSTOMIZATION.md`
- Feature tracking: `feature-management/features/features.md`

## Questions or Issues?

This is experimental work. Document:
- Design decisions in feature PROMPT.md files
- Issues in `feature-management/bugs/`
- Session reports in `feature-management/agent_runs/`
- Retrospectives via retrospective-agent

---

**Remember:** This worktree is isolated from the main repository. Experiment freely!

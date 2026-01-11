# FEAT-019: Context Engineering Agent Role Prompts

**Priority**: P2
**Component**: agents
**Type**: new_feature
**Estimated Effort**: medium
**Business Value**: Medium - Defines specialized agent behaviors for CE pipeline

## Overview

Create specialized agent role prompts for Context Engineering workflows in the Gastown ecosystem. Defines Mayor, Polecat, and Witness prompts tailored to CE pipeline orchestration.

## Problem Statement

Gastown agents need role-specific prompts to effectively orchestrate Context Engineering workflows. Generic prompts don't encode CE-specific knowledge about:

- **Stages**: The 6-stage Context Engineering pipeline (Clarify, Research, Model, Plan, Execute, Complete)
- **Artifacts**: PROMPT.md format, PLAN.md, TASKS.md, feature_request.json
- **Quality Criteria**: Acceptance criteria, test requirements, documentation standards
- **Conventions**: featmgmt directory structure, status lifecycle, git commit patterns

Without CE-aware prompts, agents operate with generic behaviors that don't leverage the structured workflow, leading to:
- Missed stage transitions
- Inconsistent artifact generation
- No progress visibility for human oversight
- Recovery failures when agents get stuck

## Proposed Solution

Create role prompt templates for the three Gastown agent types:

### 1. Mayor (CE Orchestrator)

The Mayor oversees the entire Context Engineering pipeline:

**Responsibilities:**
- Understands CE stages 1-6 and their artifacts
- Tracks pipeline progression through stages
- Spawns polecats for Stage 6 implementation work
- Reports progress to human overseer
- Handles blocked work and dependency issues
- Coordinates convoy creation for batch operations

**Key Knowledge:**
- CE stage definitions and transitions
- How to read `bd ready` output and prioritize work
- When to spawn polecats vs handle work directly
- How to detect and report stuck polecats
- Pipeline completion criteria

### 2. Polecat (CE Implementer)

Polecats execute individual work items (beads):

**Responsibilities:**
- Understands PROMPT.md format and follows instructions
- Follows featmgmt conventions for file structure
- Creates proper commits with conventional commit format
- Signals completion correctly via `bd close`
- Reports blockers when unable to proceed

**Key Knowledge:**
- PROMPT.md section-by-section execution pattern
- TASKS.md checkbox completion pattern
- How to update status in JSON metadata files
- Git commit message conventions
- When and how to create follow-on work items

### 3. Witness (CE Quality Monitor)

Witnesses monitor implementation quality:

**Responsibilities:**
- Monitors implementation against acceptance criteria
- Detects stuck polecats (no progress, repeated failures)
- Validates artifacts against expected formats
- Triggers recovery actions when issues detected
- Reports quality metrics to Mayor

**Key Knowledge:**
- Acceptance criteria validation patterns
- Stuck detection heuristics (time, retry count, error patterns)
- Artifact format schemas (JSON, markdown)
- Recovery action options (retry, reassign, escalate)

## Implementation Tasks

### Section 1: Define Hook Content Format

- [ ] Document hook content structure for each role
- [ ] Define required context fields
- [ ] Define optional context fields
- [ ] Create JSON schema for hook validation
- [ ] Document hook content examples

**Hook Content Format:**
```toml
# In gastown rig configuration
[hooks.mayor]
content = """
{{role_prompt}}

## Current Pipeline State
- Stage: {{current_stage}}
- Ready beads: {{bd_ready_count}}
- In-progress: {{in_progress_count}}
- Completed today: {{completed_count}}

## Active Work
{{active_beads}}
"""
```

### Section 2: Create Mayor Prompt

- [ ] Write base Mayor role prompt
- [ ] Add CE stage awareness section
- [ ] Add pipeline orchestration commands
- [ ] Add progress reporting format
- [ ] Add error handling guidance
- [ ] Test with sample pipeline state

**Draft Mayor Prompt:**
```markdown
# Mayor: Context Engineering Orchestrator

You are managing a Context Engineering pipeline for {{project_name}}.

## Context Engineering Stages

1. **Clarify** - Problem definition and scope
2. **Research** - Deep research via AI tools
3. **Model** - Architecture and design decisions
4. **Plan** - Feature enumeration and dependency mapping
5. **Execute** - Implementation (your primary focus)
6. **Complete** - Testing, documentation, release

## Current State
- Pipeline stage: {{current_stage}}
- Ready beads: {{bd_ready_count}}
- In-progress beads: {{in_progress_count}}
- Blocked beads: {{blocked_count}}

## Your Responsibilities

1. **Monitor Progress**: Track which beads are ready, in-progress, blocked
2. **Dispatch Work**: Use `gt sling <bead-id>` to assign ready beads to polecats
3. **Handle Blocks**: Investigate blocked beads, resolve dependencies, escalate if needed
4. **Report Status**: Provide clear progress updates to the Overseer (human)
5. **Coordinate Batches**: Use `gt convoy create` for related work items

## Commands Available

| Command | Purpose |
|---------|---------|
| `bd ready` | Show unblocked work ready for execution |
| `bd list --status open` | Show all open beads |
| `bd show <bead-id>` | Show bead details |
| `gt sling <bead-id>` | Assign work to polecat |
| `gt convoy create` | Batch related work items |
| `bd close <bead-id>` | Mark work complete |
| `gt witness spawn` | Create quality monitor |

## Decision Framework

**When to sling work:**
- Bead appears in `bd ready` output
- Dependencies are truly satisfied (not just marked)
- Polecat capacity available

**When to create convoy:**
- Multiple related beads ready
- Shared context would help implementation
- Wave-based execution beneficial

**When to escalate to Overseer:**
- Circular dependencies detected
- Bead blocked for >30 minutes with no progress
- Test failures after 3 retry attempts
- Security or policy questions

## Progress Report Format

```
## Pipeline Progress Report

**Stage**: Execute (5/6)
**Session Duration**: {{duration}}

### Completed This Session
- FEAT-019-01: Created Mayor prompt [5 min]
- FEAT-019-02: Created Polecat prompt [8 min]

### In Progress
- FEAT-019-03: Creating Witness prompt (polecat-7)

### Blocked
- FEAT-019-04: Waiting on FEAT-014 completion

### Next Actions
1. Complete FEAT-019-03
2. Begin testing with sample pipeline
```
```

### Section 3: Create Polecat Prompt

- [ ] Write base Polecat role prompt
- [ ] Add PROMPT.md execution guidance
- [ ] Add featmgmt conventions section
- [ ] Add git commit guidance
- [ ] Add completion signaling
- [ ] Test with sample work item

**Draft Polecat Prompt:**
```markdown
# Polecat: Context Engineering Implementer

You are implementing a work item (bead) as part of a Context Engineering pipeline.

## Your Work Item
- Bead ID: {{bead_id}}
- Title: {{bead_title}}
- Type: {{bead_type}} (bug/feature/action)
- Priority: {{priority}}

## Implementation Pattern

Follow the PROMPT.md section-by-section:

1. **Read the entire PROMPT.md** first to understand scope
2. **Check PLAN.md** if present for architectural decisions
3. **Work through TASKS.md** checkboxes sequentially
4. **Update status** in metadata JSON as you progress
5. **Create commits** after meaningful units of work
6. **Signal completion** via `bd close`

## Featmgmt Conventions

### File Structure
```
{type}/{ID}-{slug}/
  PROMPT.md           # Required: Implementation instructions
  {type}_report.json  # Required: Metadata
  PLAN.md             # Optional: Architecture decisions
  TASKS.md            # Optional: Task breakdown
  comments.md         # Optional: Notes and updates
```

### Status Lifecycle
- `new` -> `in_progress` -> `resolved`
- Update `started_date` when beginning work
- Update `updated_date` after each commit

### Git Commits
Use conventional commit format:
```
<type>(<scope>): <description>

[optional body]

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: feat, fix, docs, style, refactor, test, chore

## Completion Checklist

Before signaling completion:
- [ ] All TASKS.md checkboxes completed
- [ ] All acceptance criteria from PROMPT.md met
- [ ] Tests passing (if applicable)
- [ ] Status updated to `resolved` in JSON
- [ ] Final commit pushed

## When You're Stuck

If blocked for more than 10 minutes:

1. **Document the blocker** in comments.md
2. **Check dependencies** - is something not actually ready?
3. **Signal the witness** - they monitor for stuck polecats
4. **Don't thrash** - repeated failures waste tokens

Blockers to report:
- Missing dependencies not marked in metadata
- Unclear requirements in PROMPT.md
- External system failures
- Permission or access issues
```

### Section 4: Create Witness Prompt

- [ ] Write base Witness role prompt
- [ ] Add quality monitoring rules
- [ ] Add stuck detection heuristics
- [ ] Add recovery action guidance
- [ ] Add artifact validation patterns
- [ ] Test with sample monitoring scenario

**Draft Witness Prompt:**
```markdown
# Witness: Context Engineering Quality Monitor

You monitor polecat work for quality and progress issues.

## Monitoring Scope
- Polecats: {{active_polecat_count}}
- Beads in progress: {{in_progress_beads}}
- Session duration: {{session_duration}}

## Quality Checks

### Acceptance Criteria Validation
For each completed bead, verify:
- [ ] All acceptance criteria from PROMPT.md addressed
- [ ] Tests exist and pass (for code changes)
- [ ] Documentation updated (if required)
- [ ] Status correctly updated to `resolved`

### Artifact Format Validation
Verify generated files match schemas:
- `*_report.json` - Valid JSON with required fields
- `PROMPT.md` - Has Implementation Tasks section
- `TASKS.md` - Has checkbox items
- Git commits - Follow conventional commit format

## Stuck Detection

### Time-Based Heuristics
- **Warning**: No commit for 15 minutes on active bead
- **Alert**: No commit for 30 minutes on active bead
- **Critical**: No progress for 1 hour

### Pattern-Based Heuristics
- Same error appearing 3+ times
- Repeated rollbacks on same file
- Test failures after 3 retry attempts
- Circular dependency detection

### Token Efficiency
- Excessive file re-reads (same file 5+ times)
- Large context window usage without progress
- Repetitive tool calls with same parameters

## Recovery Actions

### Level 1: Nudge
- Send reminder to polecat
- Suggest alternative approach
- Provide additional context

### Level 2: Reassign
- Mark bead as blocked
- Return to `bd ready` queue
- Note failure reason for next polecat

### Level 3: Escalate
- Notify Mayor of persistent issue
- Document failure pattern
- Recommend human intervention

## Metrics to Track

| Metric | Description |
|--------|-------------|
| Time to completion | From sling to close |
| First-attempt success rate | Beads completed without reassign |
| Test pass rate | Tests passing on first run |
| Commit frequency | Commits per hour of active work |

## Report Format

```
## Witness Report

**Monitoring Period**: {{start_time}} - {{end_time}}

### Health Summary
- Polecats active: 3
- Beads completed: 5
- Beads stuck: 1
- Avg completion time: 12 min

### Issues Detected
1. polecat-7 stuck on FEAT-019-03 (25 min no progress)
   - Last action: Reading same file repeatedly
   - Recommendation: Reassign with additional context

### Quality Metrics
- Acceptance criteria met: 5/5 (100%)
- Test pass rate: 4/5 (80%)
- Commit format compliance: 5/5 (100%)
```
```

### Section 5: Integration with gt sling

- [ ] Document hook content injection points
- [ ] Create sample rig configuration
- [ ] Test prompt injection via gt sling
- [ ] Document troubleshooting for prompt issues
- [ ] Verify prompts work with existing featmgmt agents

**Sample Rig Configuration:**
```toml
# .gastown/rig.toml

[project]
name = "myproject"
root = "."

[hooks]
# Mayor hook for pipeline orchestration
[hooks.mayor]
trigger = "session_start"
content_file = ".gastown/prompts/mayor-ce.md"

# Polecat hook for work execution
[hooks.polecat]
trigger = "sling"
content_file = ".gastown/prompts/polecat-ce.md"

# Witness hook for quality monitoring
[hooks.witness]
trigger = "witness_spawn"
content_file = ".gastown/prompts/witness-ce.md"
```

### Section 6: Testing and Validation

- [ ] Create test pipeline with sample beads
- [ ] Test Mayor prompt with pipeline orchestration
- [ ] Test Polecat prompt with work item execution
- [ ] Test Witness prompt with stuck detection
- [ ] Validate integration with FEAT-014 Stage 6 loop
- [ ] Document any prompt refinements needed

## Acceptance Criteria

- [ ] Mayor prompt created with CE orchestration knowledge
- [ ] Polecat prompt created with implementation guidance
- [ ] Witness prompt created with quality monitoring rules
- [ ] Hook content format documented
- [ ] Prompts integrate with gt sling workflow
- [ ] Tested with sample CE pipeline
- [ ] Documentation enables prompt customization

## Dependencies

- **FEAT-014**: Context Engineering to Beads/Gastown Integration (provides Stage 6 loop)
- **FEAT-016**: SYNTHESIS.md to Beads Bridge (Stage 6 implementation uses these prompts)
- **Gastown**: Must be installed and configured

## Notes

This feature extracts and expands Section 6 of FEAT-014. While FEAT-014 defines the overall beads/gastown integration, this feature focuses specifically on the detailed role prompts needed for effective CE pipeline orchestration.

The prompts should be:
- **Complete**: Contain all knowledge needed for the role
- **Contextual**: Accept template variables for dynamic state
- **Actionable**: Provide clear decision frameworks
- **Observable**: Define reporting formats for visibility

## References

- [Welcome to Gas Town](https://scribe.rip/welcome-to-gas-town-4f25ee16dd04) - Steve Yegge
- [The Future of Coding Agents](https://scribe.rip/the-future-of-coding-agents-e9451a84207c) - Steve Yegge
- FEAT-014 PROMPT.md - Parent feature with Stage 6 integration

# FEAT-021: Inquiry Orchestration Skill for Multi-Agent Deliberation

**Priority**: P1
**Component**: skills
**Type**: new_feature
**Estimated Effort**: large
**Business Value**: high

## Overview

Create a `/inquiry <ID>` skill that serves as the master orchestrator for featmgmt's Inquiry (INQ) workflow. This skill manages the complete lifecycle of structured deliberation processes, from spawning independent research agents through final consensus and FEAT generation.

## Problem Statement

The INQ work item type (defined in `docs/WORK-ITEM-TYPES.md`) provides a structured deliberation process for complex decisions requiring multi-perspective analysis. However, executing this process currently requires:

- Manual spawning of multiple research agents
- Manual tracking of which agent covers which research area
- Manual monitoring of agent completion
- Manual phase transitions (research -> synthesis -> debate -> consensus)
- Manual collection and organization of outputs

This manual orchestration is error-prone, tedious, and doesn't scale.

## Proposed Solution

Create the `/inquiry` skill that:

1. **Parses INQ configuration** from `inquiry_report.json` and `QUESTION.md`
2. **Spawns research agents** using ccmux MCP tools (when available)
3. **Tags sessions** with `["worker", "research", "<inquiry-id>"]` for routing
4. **Monitors progress** via watchdog integration or polling
5. **Handles phase transitions** automatically when conditions are met
6. **Delegates to companion skills** (FEAT-022, FEAT-023) for specialized work

## Key Capabilities

### 1. Inquiry Discovery and Validation

```bash
/inquiry INQ-001              # Launch or resume inquiry
/inquiry list                 # Show all inquiries with status
/inquiry INQ-001 --status     # Show detailed inquiry status
```

- Locate inquiry directory in any project's `feature-management/inquiries/`
- Validate required files exist (`inquiry_report.json`, `QUESTION.md`)
- Validate phase-specific files as needed

### 2. Research Agent Spawning (Phase 1)

When ccmux MCP tools are available:

```
ccmux_create_session(name="INQ-001-agent-1", tags=["worker", "research", "INQ-001"])
ccmux_create_session(name="INQ-001-agent-2", tags=["worker", "research", "INQ-001"])
...
```

- Read `research_agents` count from `inquiry_report.json`
- Create isolated sessions for each research agent
- Tag sessions for routing and monitoring
- Invoke FEAT-022 skill to generate agent prompts
- Send prompts to each agent session

### 3. Progress Monitoring

Integration options (in priority order):

1. **Watchdog integration**: If watchdog is running, receive completion notifications
2. **Polling via ccmux**: Periodically check session status via `ccmux_get_status`
3. **Manual checkpoint**: User triggers `/inquiry INQ-001 --check`

Track per-agent status:
- `pending` - Agent not yet started
- `working` - Agent is actively researching
- `completed` - Agent has finished and produced output
- `failed` - Agent encountered error

### 4. Phase Transition Logic

**Research -> Synthesis** (automatic when all agents complete):
- Verify all research agents have `completed` status
- Invoke FEAT-023 to collect outputs into `research/agent-N.md` files
- Update `inquiry_report.json` phase to `synthesis`
- Prompt user to run synthesis (or spawn synthesis agent)

**Synthesis -> Debate** (after SYNTHESIS.md created):
- Verify `SYNTHESIS.md` exists and is non-empty
- Update phase to `debate`
- Spawn debate agents if configured, or prompt user

**Debate -> Consensus** (after DEBATE.md created):
- Verify `DEBATE.md` exists with resolution sections
- Update phase to `consensus`
- Prompt user to formalize decisions

**Consensus -> Completed** (after CONSENSUS.md and FEAT created):
- Verify `CONSENSUS.md` exists
- Verify at least one FEAT was spawned (check `spawned_features` field)
- Update status to `completed`

### 5. Fallback Behavior (No ccmux)

When ccmux MCP tools are unavailable:

- Print instructions for manual agent spawning
- Generate prompts via FEAT-022 for user to copy/paste
- Track progress via file existence checks
- Still handle phase transitions based on file state

## Integration Points

| Component | Integration Method |
|-----------|-------------------|
| ccmux MCP | `ccmux_create_session`, `ccmux_get_status`, `ccmux_read_pane`, `ccmux_set_tags` |
| Watchdog | `ccmux_watchdog_*` tools for progress monitoring |
| FEAT-022 | Invoke skill to generate research prompts |
| FEAT-023 | Invoke skill to collect and organize outputs |
| beads (optional) | `bd update` to track inquiry status |

## Implementation Tasks

### Section 1: Skill Infrastructure

- [ ] Create skill definition file: `skills/inquiry/SKILL.md`
- [ ] Define command syntax and arguments
- [ ] Implement inquiry discovery (find `inquiries/` directory)
- [ ] Implement configuration parsing (`inquiry_report.json`, `QUESTION.md`)
- [ ] Validate inquiry structure and required files

### Section 2: Research Phase Orchestration

- [ ] Implement agent spawning via ccmux (when available)
- [ ] Implement session tagging for routing
- [ ] Integrate with FEAT-022 for prompt generation
- [ ] Implement prompt delivery to agent sessions
- [ ] Handle ccmux unavailable fallback (manual mode)

### Section 3: Progress Monitoring

- [ ] Implement watchdog integration for completion detection
- [ ] Implement polling-based status checking
- [ ] Implement `--check` command for manual status refresh
- [ ] Create status display formatting
- [ ] Track and persist agent states

### Section 4: Phase Transitions

- [ ] Implement research -> synthesis transition logic
- [ ] Implement synthesis -> debate transition logic
- [ ] Implement debate -> consensus transition logic
- [ ] Implement consensus -> completed transition logic
- [ ] Update `inquiry_report.json` on each transition

### Section 5: Output Coordination

- [ ] Integrate with FEAT-023 for output collection
- [ ] Verify file creation for each phase
- [ ] Handle partial completion scenarios
- [ ] Support resumption of interrupted inquiries

### Section 6: User Interface

- [ ] Implement `/inquiry list` command
- [ ] Implement `/inquiry <ID>` launch/resume command
- [ ] Implement `/inquiry <ID> --status` detailed view
- [ ] Implement `/inquiry <ID> --phase <phase>` manual override
- [ ] Create helpful error messages and recovery suggestions

### Section 7: Testing and Documentation

- [ ] Test with sample inquiry (create test INQ in this project)
- [ ] Test fallback mode (no ccmux)
- [ ] Test phase transitions
- [ ] Document skill usage in skill README
- [ ] Create example inquiry for demonstration

## Acceptance Criteria

- [ ] `/inquiry INQ-XXX` launches research phase with configured number of agents
- [ ] Sessions are properly tagged for routing and monitoring
- [ ] Progress can be monitored via watchdog or polling
- [ ] Phase transitions occur automatically when conditions are met
- [ ] Fallback mode provides useful manual instructions when ccmux unavailable
- [ ] `inquiry_report.json` is updated throughout lifecycle
- [ ] Skill works with any project's `feature-management/inquiries/` directory
- [ ] Integration with FEAT-022 and FEAT-023 is functional

## Error Handling

| Error | Recovery |
|-------|----------|
| Inquiry not found | List available inquiries, suggest checking path |
| Missing required files | List missing files, link to INQ documentation |
| ccmux unavailable | Fall back to manual mode with instructions |
| Agent spawn failure | Retry once, then report with diagnostic info |
| Phase transition blocked | Show what's missing, suggest next steps |
| Partial completion | Support resumption from last known state |

## Example Usage

```bash
# Start a new inquiry investigation
/inquiry INQ-001

# Check status of ongoing inquiry
/inquiry INQ-001 --status

# List all inquiries in current project
/inquiry list

# Manually advance phase (if auto-transition blocked)
/inquiry INQ-001 --phase synthesis

# Resume after interruption
/inquiry INQ-001 --resume
```

## Notes

- This skill orchestrates but does not replace human judgment in synthesis, debate, and consensus phases
- The skill should be conservative about auto-transitions - require human confirmation for later phases
- ccmux integration is optional but greatly enhances automation
- Skill should work standalone for projects not using ccmux

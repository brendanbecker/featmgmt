# Task Breakdown: FEAT-021

**Work Item**: [FEAT-021: Inquiry Orchestration Skill](PROMPT.md)
**Status**: Not Started
**Last Updated**: 2026-01-20

## Prerequisites

- [ ] Read and understand PROMPT.md
- [ ] Review PLAN.md and update if needed
- [ ] Review docs/WORK-ITEM-TYPES.md INQ specification
- [ ] Verify FEAT-022 and FEAT-023 are defined (can stub if not implemented)
- [ ] Test ccmux MCP tool availability

## Section 1: Skill Infrastructure

- [ ] Create `skills/inquiry/` directory structure
- [ ] Create `skills/inquiry/SKILL.md` with:
  - [ ] Skill metadata (name, description, triggers)
  - [ ] Command syntax documentation
  - [ ] Core orchestration instructions
- [ ] Implement inquiry discovery logic:
  - [ ] Find `feature-management/inquiries/` in current project
  - [ ] Locate specific inquiry by ID
  - [ ] Handle inquiry not found gracefully
- [ ] Implement configuration parsing:
  - [ ] Parse `inquiry_report.json` (validate required fields)
  - [ ] Parse `QUESTION.md` (extract problem statement, research areas)
  - [ ] Validate phase-specific files based on current phase

## Section 2: Research Phase Orchestration (ccmux mode)

- [ ] Implement ccmux availability detection
- [ ] Implement agent session spawning:
  - [ ] Create session with proper naming: `INQ-XXX-agent-N`
  - [ ] Apply tags: `["worker", "research", "<inquiry-id>"]`
  - [ ] Configure working directory
- [ ] Integrate with FEAT-022 for prompt generation:
  - [ ] Invoke prompt generator skill
  - [ ] Distribute research areas across agents
- [ ] Implement prompt delivery:
  - [ ] Send generated prompt to each agent session
  - [ ] Verify prompt was received
- [ ] Store session IDs in inquiry_report.json for tracking

## Section 3: Progress Monitoring

- [ ] Implement watchdog integration (if available):
  - [ ] Register for completion notifications
  - [ ] Handle watchdog callbacks
- [ ] Implement polling-based monitoring:
  - [ ] Check session status via `ccmux_get_status`
  - [ ] Parse Claude detection state
  - [ ] Determine agent completion
- [ ] Implement manual status check (`--check` flag):
  - [ ] Read pane output for completion indicators
  - [ ] Update tracked status
- [ ] Create status display formatting:
  - [ ] Show per-agent status
  - [ ] Show overall phase progress
  - [ ] Show next steps

## Section 4: Phase Transition Engine

- [ ] Implement transition condition checks:
  - [ ] Research -> Synthesis: all agents completed
  - [ ] Synthesis -> Debate: SYNTHESIS.md exists
  - [ ] Debate -> Consensus: DEBATE.md with resolutions exists
  - [ ] Consensus -> Completed: CONSENSUS.md + spawned FEAT exists
- [ ] Implement automatic research -> synthesis transition:
  - [ ] Detect all agents complete
  - [ ] Invoke FEAT-023 to collect outputs
  - [ ] Update inquiry_report.json phase
  - [ ] Notify user of transition
- [ ] Implement prompted transitions for later phases:
  - [ ] Check conditions
  - [ ] Prompt user to confirm
  - [ ] Execute transition on confirmation
- [ ] Update inquiry_report.json on each transition:
  - [ ] Set phase field
  - [ ] Add transition timestamp
  - [ ] Record any notes

## Section 5: Output Coordination

- [ ] Integrate with FEAT-023:
  - [ ] Invoke collector after research phase
  - [ ] Pass session IDs or output locations
  - [ ] Verify `research/agent-N.md` files created
- [ ] Verify phase file creation:
  - [ ] Check for SYNTHESIS.md after synthesis
  - [ ] Check for DEBATE.md after debate
  - [ ] Check for CONSENSUS.md after consensus
- [ ] Handle partial completion:
  - [ ] Track which agents completed
  - [ ] Allow retry of failed agents
  - [ ] Support manual completion marking

## Section 6: Fallback Mode (No ccmux)

- [ ] Detect ccmux unavailable
- [ ] Generate manual instructions:
  - [ ] List commands user should run
  - [ ] Provide prompts to copy/paste
- [ ] Invoke FEAT-022 for prompts even without ccmux
- [ ] Track progress via file existence:
  - [ ] Check for `research/agent-N.md` files
  - [ ] Infer completion from files present
- [ ] Support all phase transitions in manual mode

## Section 7: User Interface Commands

- [ ] Implement `/inquiry list`:
  - [ ] Scan inquiries directory
  - [ ] Show ID, title, phase, status for each
  - [ ] Format as table
- [ ] Implement `/inquiry <ID>`:
  - [ ] Load inquiry configuration
  - [ ] Determine current phase
  - [ ] Execute appropriate action (spawn, check, transition)
- [ ] Implement `/inquiry <ID> --status`:
  - [ ] Show detailed status
  - [ ] Show agent progress
  - [ ] Show phase history
- [ ] Implement `/inquiry <ID> --phase <phase>`:
  - [ ] Allow manual phase override
  - [ ] Require confirmation
  - [ ] Update inquiry_report.json
- [ ] Implement error handling:
  - [ ] Clear error messages
  - [ ] Recovery suggestions
  - [ ] Link to documentation

## Section 8: Testing

- [ ] Create test inquiry in this project:
  - [ ] `inquiries/INQ-TEST-001/`
  - [ ] Sample inquiry_report.json
  - [ ] Sample QUESTION.md with research areas
- [ ] Test with ccmux available:
  - [ ] Verify agent spawning
  - [ ] Verify tagging
  - [ ] Verify status tracking
  - [ ] Verify phase transitions
- [ ] Test fallback mode:
  - [ ] Verify instructions are useful
  - [ ] Verify manual completion works
  - [ ] Verify transitions work
- [ ] Test edge cases:
  - [ ] Partial completion
  - [ ] Agent failures
  - [ ] Interrupted inquiries
  - [ ] Resume after restart

## Section 9: Documentation

- [ ] Create `skills/inquiry/README.md`:
  - [ ] Overview and purpose
  - [ ] Command reference
  - [ ] Configuration options
  - [ ] Examples
- [ ] Add to skills index (if exists)
- [ ] Document integration with FEAT-022 and FEAT-023
- [ ] Create troubleshooting guide

## Completion Checklist

- [ ] Skill definition complete and discoverable
- [ ] Research phase orchestration works with ccmux
- [ ] Fallback mode provides useful manual workflow
- [ ] All phase transitions implemented
- [ ] Integration with FEAT-022 and FEAT-023 functional
- [ ] User interface commands implemented
- [ ] Tests pass
- [ ] Documentation complete

---
*Check off tasks as you complete them. Update status field above.*

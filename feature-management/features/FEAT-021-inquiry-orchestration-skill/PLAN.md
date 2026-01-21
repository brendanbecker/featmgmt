# Implementation Plan: FEAT-021

**Work Item**: [FEAT-021: Inquiry Orchestration Skill](PROMPT.md)
**Component**: skills
**Priority**: P1
**Created**: 2026-01-20

## Overview

This feature creates the master orchestration skill for INQ (Inquiry) work items. It coordinates multi-agent deliberation by spawning research agents, monitoring progress, and managing phase transitions through the complete INQ lifecycle.

## Architecture Decisions

### Decision 1: Skill-Based Architecture

**Choice**: Implement as a Claude Code skill in `skills/inquiry/SKILL.md`

**Rationale**:
- Skills are the standard extension mechanism in featmgmt
- Portable across projects - any featmgmt-enabled project can use it
- Follows established patterns from other featmgmt skills
- Can be invoked via `/inquiry` command

**Trade-offs**:
- (+) Consistent with featmgmt architecture
- (+) Portable and reusable
- (-) Skill execution context may have limitations
- (-) Depends on Claude Code skill discovery

### Decision 2: ccmux-First with Fallback

**Choice**: Use ccmux MCP tools when available, provide manual fallback when not

**Rationale**:
- ccmux provides powerful multi-session orchestration
- Not all users have ccmux configured
- Fallback ensures skill is useful in any environment
- Progressive enhancement pattern

**Trade-offs**:
- (+) Works everywhere
- (+) Full automation when ccmux available
- (-) Two code paths to maintain
- (-) Manual mode significantly less automated

### Decision 3: Modular Skill Composition

**Choice**: Delegate specialized work to FEAT-022 (prompt generation) and FEAT-023 (output collection)

**Rationale**:
- Single responsibility principle
- Each skill can be used independently
- Easier to test and maintain
- Reusable components

**Trade-offs**:
- (+) Modular and testable
- (+) Skills useful independently
- (-) Coordination complexity
- (-) Depends on multiple features

### Decision 4: Conservative Phase Transitions

**Choice**: Auto-transition research->synthesis only; require confirmation for later phases

**Rationale**:
- Research completion is deterministic (all agents done)
- Synthesis, debate, consensus require human judgment
- Prevents runaway automation
- Maintains human-in-the-loop for important decisions

**Trade-offs**:
- (+) Safer - humans verify key transitions
- (+) Allows human intervention
- (-) Less fully automated
- (-) Requires user engagement

## Affected Components

| Component | Type of Change | Risk Level |
|-----------|----------------|------------|
| skills/inquiry/ | New directory and files | Low |
| docs/WORK-ITEM-TYPES.md | Reference only (no changes) | None |
| ccmux MCP integration | New usage | Medium |
| FEAT-022, FEAT-023 | Dependency | Medium |

## Implementation Approach

### Phase 1: Core Skill Structure

1. Create skill directory structure
2. Implement inquiry discovery and validation
3. Parse `inquiry_report.json` configuration
4. Parse `QUESTION.md` for research context

### Phase 2: ccmux Integration

1. Detect ccmux availability via MCP tool presence
2. Implement session creation with proper tagging
3. Implement status polling
4. Implement watchdog integration (if available)

### Phase 3: Research Phase Orchestration

1. Integrate with FEAT-022 for prompt generation
2. Deliver prompts to spawned agents
3. Track agent progress
4. Detect research completion

### Phase 4: Phase Transition Engine

1. Implement transition condition checking
2. Update `inquiry_report.json` on transition
3. Integrate with FEAT-023 for output collection
4. Handle partial/interrupted states

### Phase 5: User Interface

1. Implement `/inquiry` command parsing
2. Create status display formatting
3. Implement list and detail views
4. Add error messages and recovery hints

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| FEAT-022 (Prompt Generator) | Required | Pending |
| FEAT-023 (Output Collector) | Required | Pending |
| ccmux MCP tools | Optional | Available |
| featmgmt INQ structure | Required | Defined |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ccmux unavailable in target env | Medium | Medium | Comprehensive fallback mode |
| FEAT-022/023 not ready | Medium | High | Can stub for initial testing |
| Complex state management | Medium | Medium | Persist state to inquiry_report.json |
| Agent failures during research | Low | Medium | Retry logic, partial completion handling |

## Rollback Strategy

Skill can be removed without affecting existing inquiries. The skill only orchestrates - all artifacts are standard INQ files that can be managed manually.

## Success Metrics

- Inquiry can be launched with single command
- Research agents spawn and receive correct prompts
- Phase transitions occur at appropriate times
- Status display provides clear progress visibility
- Works with and without ccmux

## Implementation Notes

### Skill File Location

```
skills/
  inquiry/
    SKILL.md          # Skill definition and instructions
    README.md         # Usage documentation
    examples/         # Example inquiries for testing
```

### ccmux Detection

Check for MCP tool availability:
```
if ccmux_list_sessions tool exists:
    use ccmux mode
else:
    use manual fallback mode
```

### State Persistence

All state persists in `inquiry_report.json`:
- Current phase
- Agent statuses (stored in custom field)
- Session IDs (when using ccmux)
- Timestamps for each transition

### Session Naming Convention

```
INQ-XXX-agent-1    # First research agent
INQ-XXX-agent-2    # Second research agent
INQ-XXX-synthesizer  # Synthesis agent (if automated)
INQ-XXX-debater-pro  # Debate agents (if automated)
INQ-XXX-debater-con
```

---
*This plan should be updated as implementation progresses.*

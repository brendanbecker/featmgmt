# Implementation Plan: FEAT-022

**Work Item**: [FEAT-022: Research Agent Prompt Generator](PROMPT.md)
**Component**: skills
**Priority**: P1
**Created**: 2026-01-20

## Overview

This feature creates a skill for generating focused, context-rich prompts for research agents in the inquiry workflow. It handles parsing `QUESTION.md`, distributing research areas, and producing ready-to-use prompts.

## Architecture Decisions

### Decision 1: Skill-Based Implementation

**Choice**: Implement as a standalone skill in `skills/inquiry-prompts/SKILL.md`

**Rationale**:
- Can be invoked by FEAT-021 orchestration
- Can also be used standalone for manual workflows
- Follows featmgmt skill patterns
- Portable across projects

**Trade-offs**:
- (+) Reusable and composable
- (+) Testable in isolation
- (-) Adds another skill to maintain
- (-) Coordination with FEAT-021 needed

### Decision 2: Multiple Parsing Formats

**Choice**: Support numbered lists, headed sections, and bulleted lists for research areas

**Rationale**:
- Users structure QUESTION.md differently
- Flexibility reduces friction
- Common markdown patterns
- Easy to detect format automatically

**Trade-offs**:
- (+) User-friendly, accepts various formats
- (+) No strict formatting requirements
- (-) More parsing logic to maintain
- (-) Edge cases possible

### Decision 3: Round-Robin Default Distribution

**Choice**: Use round-robin as default distribution, with balanced/grouped as options

**Rationale**:
- Round-robin is simplest and predictable
- Works well when areas are roughly equal
- Balanced mode available when needed
- Grouped mode for explicit dependencies

**Trade-offs**:
- (+) Simple default behavior
- (+) Advanced options available
- (-) May not be optimal for uneven areas
- (-) User must know to use balanced mode

### Decision 4: Self-Contained Prompts

**Choice**: Each agent prompt is completely self-contained with all necessary context

**Rationale**:
- Agents work independently (INQ Phase 1 requirement)
- No cross-agent communication needed
- Reduces coupling and complexity
- Enables true parallel research

**Trade-offs**:
- (+) True independence
- (+) Simpler agent implementation
- (-) Some context duplication
- (-) Larger prompt sizes

## Affected Components

| Component | Type of Change | Risk Level |
|-----------|----------------|------------|
| skills/inquiry-prompts/ | New directory | Low |
| QUESTION.md format | Documentation | Low |
| FEAT-021 integration | Consumer | Medium |

## Implementation Approach

### Phase 1: Parsing Infrastructure

1. Create skill directory structure
2. Implement QUESTION.md markdown parser
3. Implement research area extraction for all formats
4. Implement inquiry_report.json parser

### Phase 2: Distribution Engine

1. Implement round-robin distribution
2. Implement balanced distribution (complexity-aware)
3. Implement grouped distribution
4. Handle edge cases

### Phase 3: Prompt Generation

1. Create prompt template
2. Implement template variable substitution
3. Generate prompts for each agent
4. Format as clean markdown

### Phase 4: Output and Integration

1. Implement structured object return
2. Implement file output mode
3. Create CLI interface
4. Integrate with FEAT-021

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| featmgmt INQ structure | Required | Defined |
| FEAT-021 (consumer) | Soft | Pending |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| QUESTION.md format varies | High | Low | Support multiple formats |
| Areas unevenly sized | Medium | Low | Balanced distribution option |
| Parsing edge cases | Medium | Low | Graceful fallbacks, user hints |

## Rollback Strategy

Skill can be removed without affecting inquiries. Prompts can always be written manually.

## Success Metrics

- Correctly extracts research areas from various QUESTION.md formats
- Distributes areas fairly across agents
- Generated prompts are self-contained and clear
- Integration with FEAT-021 is seamless

## Implementation Notes

### Skill File Location

```
skills/
  inquiry-prompts/
    SKILL.md          # Skill definition
    README.md         # Usage documentation
    templates/        # Prompt templates
      default.md      # Default prompt template
```

### Research Area Detection Heuristics

1. Look for `## Research Areas` heading
2. If not found, look for numbered lists after problem statement
3. If not found, look for `## Research Area N:` pattern
4. If not found, look for bulleted lists
5. If still not found, treat entire document as single area

### Complexity Hint Parsing

Support inline hints in area descriptions:
- `(complexity: high|medium|low)`
- `(estimated: N hours)`
- `(priority: P0|P1|P2|P3)`

### Distribution Formulas

**Round-Robin:**
```
agent[i] gets areas where (area_index % num_agents) == i
```

**Balanced:**
```
Sort areas by complexity descending
For each area:
  Assign to agent with lowest current total complexity
```

**Grouped:**
```
Parse [group: X] annotations
Assign all areas in group to same agent
Balance remaining areas
```

---
*This plan should be updated as implementation progresses.*

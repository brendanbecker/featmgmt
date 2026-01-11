# Implementation Plan: FEAT-019

**Work Item**: [FEAT-019: Context Engineering Agent Role Prompts](PROMPT.md)
**Component**: agents
**Priority**: P2
**Created**: 2026-01-11

## Overview

Create specialized agent role prompts for Context Engineering workflows in the Gastown ecosystem. This defines Mayor, Polecat, and Witness prompts tailored to CE pipeline orchestration.

## Architecture Decisions

### Prompt Storage Strategy

**Decision**: Store prompts as standalone markdown files in `.gastown/prompts/`

**Rationale**:
- Prompts are version-controlled with the project
- Easy to customize per-project
- Can be referenced by rig.toml hook configuration
- Follows existing featmgmt pattern of markdown-based instructions

**Alternatives Considered**:
- Inline in rig.toml - Too verbose, hard to maintain
- Separate prompts repository - Overkill for role-specific content
- Embedded in agent code - Not customizable

### Template Variable Strategy

**Decision**: Use mustache-style `{{variable}}` placeholders

**Rationale**:
- Consistent with existing Gastown hook content format
- Simple string replacement, no complex templating engine
- Variables populated at runtime from pipeline state

**Variables Defined**:
| Variable | Source | Used By |
|----------|--------|---------|
| `{{project_name}}` | rig.toml | All roles |
| `{{current_stage}}` | bd list analysis | Mayor |
| `{{bd_ready_count}}` | bd ready | Mayor |
| `{{in_progress_count}}` | bd list --status in_progress | Mayor, Witness |
| `{{bead_id}}` | gt sling argument | Polecat |
| `{{bead_title}}` | bead metadata | Polecat |
| `{{bead_type}}` | bead metadata | Polecat |
| `{{active_polecat_count}}` | gt status | Witness |
| `{{session_duration}}` | computed | Witness |

### Role Responsibility Boundaries

**Mayor**:
- Does NOT implement work directly
- Does NOT run tests
- DOES monitor overall pipeline health
- DOES dispatch work to polecats
- DOES escalate issues to human

**Polecat**:
- Does NOT coordinate with other polecats
- Does NOT reassign work
- DOES implement assigned bead completely
- DOES signal completion or blockers
- DOES follow featmgmt conventions

**Witness**:
- Does NOT implement work
- Does NOT dispatch new work
- DOES monitor quality metrics
- DOES detect stuck polecats
- DOES trigger recovery actions

## Affected Components

| Component | Type of Change | Risk Level |
|-----------|----------------|------------|
| `.gastown/prompts/` | New directory | Low |
| `mayor-ce.md` | New file | Low |
| `polecat-ce.md` | New file | Low |
| `witness-ce.md` | New file | Low |
| rig.toml | Hook configuration | Medium |
| FEAT-014 Stage 6 | Integration point | Medium |

## Dependencies

- **FEAT-014**: Must define Stage 6 loop structure before prompts can integrate
- **Gastown**: Rig configuration and hook content injection
- **Beads**: Pipeline state commands (`bd ready`, `bd list`, etc.)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Prompts too verbose, exceed context | Medium | High | Use progressive disclosure, link to docs |
| Variable injection fails silently | Medium | Medium | Add validation, log injected values |
| Role boundaries unclear in practice | Low | Medium | Add explicit "NOT your job" sections |
| Gastown hook format changes | Low | High | Pin to specific Gastown version |

## Rollback Strategy

If prompts cause issues:
1. Remove hook configuration from rig.toml
2. Delete `.gastown/prompts/` directory
3. Gastown will use default prompts
4. Document what went wrong in comments.md

## Implementation Notes

### Prompt Size Considerations

Target prompt sizes (before variable injection):
- Mayor: ~1500 tokens - Needs comprehensive orchestration knowledge
- Polecat: ~1200 tokens - Focused on execution pattern
- Witness: ~1000 tokens - Monitoring rules and heuristics

### Testing Strategy

1. **Unit Tests**: Validate template variable substitution
2. **Integration Tests**: Verify prompts work with `gt sling`
3. **End-to-End**: Run sample CE pipeline with all three roles

### Documentation Updates

After implementation:
- Add "CE Role Prompts" section to FEAT-014 documentation
- Update Gastown rig.toml examples
- Create troubleshooting guide for prompt issues

---
*This plan should be updated as implementation progresses.*

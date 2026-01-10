# Implementation Plan: FEAT-013

**Work Item**: [FEAT-013: Formalize Architecture-to-WAVES Pipeline](PROMPT.md)
**Component**: methodology
**Priority**: P1
**Created**: 2026-01-09

## Overview

This feature formalizes the ad-hoc process of transforming architecture documentation into parallelizable development waves. The implementation focuses on documenting the methodology, creating templates, and providing worked examples rather than building automation tooling.

## Architecture Decisions

### Decision 1: Documentation-First Approach

**Choice**: Create documentation and templates rather than automated tooling

**Rationale**:
- Methodology needs to be understood before automation
- Documentation enables immediate use without development investment
- Templates provide structure while allowing flexibility
- Worked examples demonstrate application

**Trade-offs**:
- (+) Faster to implement
- (+) More flexible for edge cases
- (-) Requires manual execution
- (-) Less consistent than automation

### Decision 2: Three-Stage Pipeline

**Choice**: Separate Feature Enumeration, Dependency Analysis, and Wave Generation

**Rationale**:
- Clear separation of concerns
- Intermediate artifacts enable review
- Each stage can be refined independently
- Matches natural cognitive workflow

**Trade-offs**:
- (+) Debuggable - can trace decisions
- (+) Reviewable checkpoints
- (-) More artifacts to maintain
- (-) Potential for stage boundaries to be unclear

### Decision 3: Markdown-Based Artifacts

**Choice**: Use markdown tables for FEATURES.md and DEPENDENCIES.md

**Rationale**:
- Human-readable and editable
- Version-controllable
- Compatible with Obsidian, GitHub, etc.
- Consistent with existing featmgmt conventions

**Trade-offs**:
- (+) Universal format
- (+) Easy to review in PRs
- (-) Not machine-parseable without effort
- (-) Manual updates prone to drift

### Decision 4: Integration Point

**Choice**: Position as Stage 2.5 between Deep Research and Implementation Planning

**Rationale**:
- Consumes Deep Research outputs (ARCHITECTURE.md, PROJECT_SUMMARY.md)
- Produces Implementation Planning inputs (WAVES.md)
- Fills documented gap in methodology

**Trade-offs**:
- (+) Clear methodology fit
- (+) Leverages existing artifacts
- (-) Adds step to process
- (-) May seem heavyweight for small projects

## Affected Components

| Component | Type of Change | Risk Level |
|-----------|----------------|------------|
| methodology documentation | New content | Low |
| templates/ directory | New files | Low |
| WAVES.md convention | Enhancement | Low |
| context engineering workflow | Documentation update | Medium |

## Implementation Approach

### Phase 1: Core Documentation (Sections 1-3)

1. Document each stage in detail:
   - Feature Enumeration process and FEATURES.md format
   - Dependency Analysis process and DEPENDENCIES.md format
   - Wave Generation process and enhanced WAVES.md format

2. Create prompt templates for each stage that Claude can follow

3. Document heuristics and edge cases

### Phase 2: Templates (Section 5)

1. Create markdown templates for each artifact
2. Include section headers, example entries, and comments
3. Store in appropriate templates/ location

### Phase 3: Integration (Section 4)

1. Document how pipeline fits into broader methodology
2. Create diagram showing full flow
3. Document handoffs between stages

### Phase 4: Validation (Sections 6-7)

1. Apply pipeline to real project (featmgmt or another)
2. Create worked example showing all artifacts
3. Document lessons learned

## Dependencies

None - this is documentation/methodology work that does not depend on code changes.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pipeline too heavyweight | Medium | Medium | Document "quick mode" for small projects |
| Stages unclear | Low | Medium | Worked examples clarify boundaries |
| Dependency analysis hard | Medium | Low | Provide heuristics and common patterns |
| Templates not adopted | Medium | Low | Demonstrate value through examples |

## Rollback Strategy

Documentation can be revised or removed without impact on existing workflows. This is additive methodology documentation.

## Success Metrics

- Pipeline can be followed to produce valid WAVES.md
- Intermediate artifacts provide useful review checkpoints
- Process is repeatable across different projects
- Documentation is clear enough for independent use

## Implementation Notes

### Deliverables Location

Methodology documentation should go in:
- `docs/methodology/` if that exists, OR
- `templates/` for templates, OR
- Feature directory itself with links from main docs

### Template Naming Convention

- `FEATURES.template.md`
- `DEPENDENCIES.template.md`
- `WAVES.template.md` (enhanced version)

### Example Project

Use featmgmt itself as worked example:
- Already has ARCHITECTURE.md-like documentation in CLAUDE.md
- Has features that could demonstrate dependency relationships
- Results can be validated against existing knowledge

---
*This plan should be updated as implementation progresses.*

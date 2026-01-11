# Implementation Plan: FEAT-016

**Work Item**: [FEAT-016: SYNTHESIS.md to Beads Bridge](PROMPT.md)
**Component**: parsing
**Priority**: P3
**Created**: 2026-01-11

## Overview

Create a parser that extracts key decisions from SYNTHESIS.md and links them to beads, enabling traceability from research through to implementation.

## Architecture Decisions

### Parser Approach

- **Approach**: Markdown AST parsing with heuristic-based decision extraction
- **Rationale**: SYNTHESIS.md files have semi-structured content; AST parsing provides reliable section identification while heuristics handle varied content formats
- **Trade-offs**: Heuristics may need tuning per project; rigid parsing would miss valid decisions

### Decision Bead Format

- **Approach**: Extend existing bead metadata schema with `decision_type` and `source` fields
- **Rationale**: Leverages existing bead infrastructure; minimal new schema surface
- **Trade-offs**: Decisions become first-class beads rather than annotations; more storage but better queryability

### Linking Strategy

- **Approach**: Use `bd dep add` for explicit dependencies plus metadata cross-references
- **Rationale**: Integrates with existing bead dependency system; backward compatible
- **Trade-offs**: Dual linking mechanism adds complexity but provides flexibility

## Affected Components

| Component | Type of Change | Risk Level |
|-----------|----------------|------------|
| parsing module | New parser implementation | Low |
| bead schema | Schema extension | Low |
| bd CLI | New query commands | Low |
| Context Engineering docs | Documentation updates | Low |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| FEAT-014 (Stage 5 bead creation) | Feature | new |
| SYNTHESIS.md format | External | Defined in Context Engineering Stage 3 |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SYNTHESIS.md format varies widely | Medium | Medium | Support multiple common formats, document expected structure |
| Decision extraction misses important decisions | Medium | Low | Conservative extraction with manual override option |
| Circular dependencies in bead graph | Low | Medium | Validate DAG property during linking |

## Rollback Strategy

If implementation causes issues:
1. Decision beads are additive; can be deleted without affecting feature beads
2. Linking metadata can be stripped from existing beads
3. Parser can be disabled via configuration flag

## Implementation Notes

### SYNTHESIS.md Expected Structures

Common patterns to support:
1. `## Recommendations` sections with numbered items
2. Technology comparison tables with decision columns
3. `## Key Decisions` or `## Architecture Decisions` sections
4. Inline decision markers like `**Decision:**` or `> Decision:`
5. ADR (Architecture Decision Record) format sections

### Decision Types

- `technology`: Choice of library, framework, or tool
- `architecture`: Structural decisions (patterns, layers, interfaces)
- `approach`: Implementation strategy or methodology
- `tradeoff`: Explicit tradeoff analysis with chosen option
- `constraint`: External constraints that shaped decisions

### Query Interface

```bash
# What research led to this feature?
bd query --decisions-for FEAT-016

# What features implement this decision?
bd query --features-for DEC-001

# List all decisions from a SYNTHESIS.md
bd parse synthesis docs/SYNTHESIS.md
```

---
*This plan should be updated as implementation progresses.*

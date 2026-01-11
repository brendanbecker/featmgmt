# Implementation Plan: FEAT-018

**Work Item**: [FEAT-018: Stage 6 Gastown GUPP Loop Integration](PROMPT.md)
**Component**: automation
**Priority**: P1
**Created**: 2026-01-11

## Overview

Implement the Stage 6 implementation loop using Gastown's GUPP (Gas Town Universal Propulsion Principle). This creates the `bd ready` -> `gt sling` -> `gt convoy wait` -> `bd close` loop that runs until all beads are complete.

## Architecture Decisions

### Formula Structure

The formula will be implemented as a TOML file following Beads formula conventions:

```toml
[formula]
name = "ce-stage-6-implementation"
description = "Stage 6 GUPP loop for parallel bead execution"
version = "0.1.0"

[parameters]
concurrency = { type = "int", default = 3, description = "Max parallel polecats" }
wave_timeout = { type = "duration", default = "30m", description = "Max time per wave" }

[steps]
# Step definitions using Gastown primitives
```

### Convoy Strategy

- **Wave-based batching**: Each iteration creates a convoy for ready beads
- **Naming convention**: `Wave-{timestamp}` for traceability
- **Lifecycle**: Create -> Populate -> Wait -> Report

### Concurrency Model

- **Default**: 3 parallel polecats
- **Configurable**: Via formula parameter
- **Rationale**: Balance between throughput and resource usage

## Affected Components

| Component | Type of Change | Risk Level |
|-----------|----------------|------------|
| Beads (formulas) | New formula | Low |
| Gastown (gt CLI) | Integration | Low |
| Witness | Monitoring hooks | Low |

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| FEAT-014 | Required | Master formula + Stage 5 bead generator |
| Beads 0.44.0+ | Required | Formula support |
| Gastown | Required | Polecat and convoy support |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Stuck polecats block progress | Medium | High | Witness timeout + alerting |
| Resource exhaustion from over-concurrency | Low | Medium | Configurable concurrency limits |
| Dependency chain errors | Medium | Medium | Validate bd ready output |
| Convoy wait indefinite hang | Low | High | Wave timeout parameter |

## Rollback Strategy

If implementation causes issues:
1. Remove `ce-stage-6-implementation.formula.toml` from formula directory
2. Revert to manual Stage 6 execution
3. Document issues in comments.md

## Implementation Approach

### Phase 1: Basic Loop (MVP)

1. Create formula skeleton
2. Implement basic loop: ready -> sling -> wait -> close
3. Test with single bead
4. Test with multiple independent beads

### Phase 2: Concurrency Control

1. Add concurrency parameter
2. Implement polecat limit enforcement
3. Test with batched beads

### Phase 3: Error Handling

1. Add witness integration
2. Implement stuck detection
3. Add convoy failure handling
4. Test failure scenarios

### Phase 4: Polish

1. Add logging and progress reporting
2. Document parameters and usage
3. Integration test with full pipeline

## Implementation Notes

<!-- Add notes during implementation -->

---
*This plan should be updated as implementation progresses.*

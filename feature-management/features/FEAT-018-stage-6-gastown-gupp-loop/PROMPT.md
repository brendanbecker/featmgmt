# FEAT-018: Stage 6 Gastown GUPP Loop Integration

**Priority**: P1
**Component**: automation
**Type**: new_feature
**Estimated Effort**: medium
**Business Value**: High - Enables parallel agent execution for Stage 6 implementation

## Overview

Implement the Stage 6 implementation loop using Gastown's GUPP (Gas Town Universal Propulsion Principle). This creates the `bd ready` -> `gt sling` -> `gt convoy wait` -> `bd close` loop that runs until all beads are complete.

## Problem Statement

After Stage 5 generates beads with dependencies, Stage 6 execution is still manual. Need automated orchestration that:
- Queries for unblocked work (`bd ready`)
- Assigns work to polecats (`gt sling`)
- Monitors completion (`gt convoy wait`)
- Closes completed beads (`bd close`)
- Loops until done

## Proposed Solution

Create `ce-stage-6-implementation.formula.toml` that implements the GUPP loop:

```bash
while bd ready --count > 0; do
    convoy_id=$(gt convoy create "Wave $(date +%s)")
    bd ready --json | jq -r '.[].id' | while read bead_id; do
        gt sling $bead_id --convoy $convoy_id
    done
    gt convoy wait $convoy_id
    gt convoy show $convoy_id --json | jq -r '.completed[].bead_id' | while read id; do
        bd close $id
    done
done
```

## Key Capabilities

- Formula for Stage 6 loop
- Polecat spawning strategy (concurrency limits)
- Convoy creation for batch work
- Witness monitoring integration
- Completion detection and bead closing

## Dependencies

- FEAT-014 (master formula + Stage 5 bead generator)
- Beads 0.44.0+
- Gastown installed

## Implementation Tasks

### Section 1: Formula Design
- [ ] Define formula structure in TOML format
- [ ] Design convoy creation and naming strategy
- [ ] Determine concurrency limits for polecat spawning
- [ ] Plan error handling for failed polecats

### Section 2: Core Loop Implementation
- [ ] Implement `bd ready` query integration
- [ ] Implement `gt convoy create` for wave batching
- [ ] Implement `gt sling` for bead assignment to polecats
- [ ] Implement `gt convoy wait` for completion monitoring
- [ ] Implement `bd close` for completed beads

### Section 3: Witness Integration
- [ ] Add witness monitoring hooks
- [ ] Implement stuck polecat detection
- [ ] Add timeout handling for long-running polecats
- [ ] Create alerting for failed convoys

### Section 4: Testing
- [ ] Test with small bead sets (2-3 beads)
- [ ] Test with dependent bead chains
- [ ] Test concurrent execution limits
- [ ] Test error recovery and retry logic
- [ ] Test witness stuck detection

### Section 5: Documentation
- [ ] Document formula parameters
- [ ] Document concurrency configuration
- [ ] Document witness integration
- [ ] Add usage examples

## Acceptance Criteria

- [ ] `ce-stage-6-implementation.formula.toml` exists
- [ ] GUPP loop runs until `bd ready --count == 0`
- [ ] Polecats spawned with configurable concurrency
- [ ] Convoys track work batches
- [ ] Completed beads are closed automatically
- [ ] Witness can detect stuck polecats

## Technical Notes

### GUPP Loop Flow

```
┌─────────────────────────────────────────────────────┐
│                   GUPP Loop                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│   ┌──────────────┐                                  │
│   │  bd ready    │ ──> Check for unblocked beads    │
│   └──────┬───────┘                                  │
│          │ count > 0?                               │
│          ▼                                          │
│   ┌──────────────┐                                  │
│   │ gt convoy    │ ──> Create wave batch            │
│   │   create     │                                  │
│   └──────┬───────┘                                  │
│          │                                          │
│          ▼                                          │
│   ┌──────────────┐                                  │
│   │  gt sling    │ ──> Assign beads to polecats     │
│   │   (per bead) │                                  │
│   └──────┬───────┘                                  │
│          │                                          │
│          ▼                                          │
│   ┌──────────────┐                                  │
│   │  gt convoy   │ ──> Wait for completion          │
│   │    wait      │                                  │
│   └──────┬───────┘                                  │
│          │                                          │
│          ▼                                          │
│   ┌──────────────┐                                  │
│   │  bd close    │ ──> Mark beads complete          │
│   │ (per bead)   │                                  │
│   └──────┬───────┘                                  │
│          │                                          │
│          └──────────> Loop back to bd ready         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Concurrency Model

- Default concurrency: 3 polecats
- Configurable via formula parameter
- Witness monitors for stuck/failed polecats
- Convoy provides batch tracking

### Error Handling

- Failed polecat: Mark bead as failed, continue with others
- Stuck polecat: Witness timeout triggers alert
- All convoy failed: Report and exit with error code

## Notes

- This completes the automation of Stage 6 in the Context Engineering pipeline
- Integration with FEAT-014 provides the beads to execute
- Future enhancement: adaptive concurrency based on system load

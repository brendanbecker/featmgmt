# Task Breakdown: FEAT-018

**Work Item**: [FEAT-018: Stage 6 Gastown GUPP Loop Integration](PROMPT.md)
**Status**: Not Started
**Last Updated**: 2026-01-11

## Prerequisites

- [ ] Read and understand PROMPT.md
- [ ] Review PLAN.md and update if needed
- [ ] Verify FEAT-014 is complete or in progress
- [ ] Verify Beads 0.44.0+ is available
- [ ] Verify Gastown is installed and configured
- [ ] Understand convoy and polecat concepts

## Design Tasks

- [ ] Review existing formula examples in Beads
- [ ] Design formula TOML structure
- [ ] Define convoy naming convention
- [ ] Define concurrency limits and configuration
- [ ] Design error handling strategy
- [ ] Update PLAN.md with final approach

## Implementation Tasks

### Core Formula

- [ ] Create `ce-stage-6-implementation.formula.toml` skeleton
- [ ] Define formula metadata (name, version, description)
- [ ] Define parameters (concurrency, wave_timeout)
- [ ] Implement main loop condition (`bd ready --count > 0`)

### Loop Steps

- [ ] Implement Step 1: Query ready beads (`bd ready --json`)
- [ ] Implement Step 2: Create convoy (`gt convoy create`)
- [ ] Implement Step 3: Sling beads (`gt sling $bead_id --convoy $convoy_id`)
- [ ] Implement Step 4: Wait for convoy (`gt convoy wait $convoy_id`)
- [ ] Implement Step 5: Close completed beads (`bd close $id`)
- [ ] Implement loop continuation logic

### Error Handling

- [ ] Add polecat failure handling
- [ ] Add convoy timeout handling
- [ ] Add stuck polecat detection
- [ ] Add retry logic for transient failures
- [ ] Add cleanup on formula abort

### Witness Integration

- [ ] Add witness monitoring hooks
- [ ] Implement stuck detection thresholds
- [ ] Add alerting for failures
- [ ] Test witness integration

## Testing Tasks

- [ ] Test with single bead (no dependencies)
- [ ] Test with multiple independent beads
- [ ] Test with dependent bead chain (A -> B -> C)
- [ ] Test concurrency limits (spawn max N polecats)
- [ ] Test polecat failure scenario
- [ ] Test convoy timeout scenario
- [ ] Test stuck polecat detection
- [ ] Test full pipeline integration (Stage 5 -> Stage 6)
- [ ] Run full test suite

## Documentation Tasks

- [ ] Document formula parameters in PROMPT.md
- [ ] Document usage examples
- [ ] Document concurrency configuration
- [ ] Document witness integration
- [ ] Add troubleshooting section
- [ ] Update CHANGELOG if applicable

## Verification Tasks

- [ ] All acceptance criteria from PROMPT.md met
- [ ] Formula runs until `bd ready --count == 0`
- [ ] Polecats spawn with configured concurrency
- [ ] Convoys track work batches correctly
- [ ] Completed beads are closed automatically
- [ ] Witness detects stuck polecats
- [ ] Tests passing
- [ ] Update feature_request.json status
- [ ] Document completion in comments.md

## Completion Checklist

- [ ] All implementation tasks complete
- [ ] All tests passing
- [ ] Documentation updated
- [ ] PLAN.md reflects final implementation
- [ ] Ready for review/merge

---
*Check off tasks as you complete them. Update status field above.*

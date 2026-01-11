# FEAT-016: SYNTHESIS.md to Beads Bridge

**Priority**: P3
**Component**: parsing
**Type**: new_feature
**Estimated Effort**: small
**Business Value**: Low - Nice-to-have traceability from research to features

## Overview

Create a parser that extracts key decisions from SYNTHESIS.md and links them to beads, enabling traceability from research through to implementation.

## Problem Statement

SYNTHESIS.md contains key decisions and rationale from the research phase. Currently this context is lost when features are created. Linking decisions to their implementing beads would provide:
- Audit trail for "why was this built this way?"
- Traceability from research to code
- Context for future modifications

## Proposed Solution

Create a parser that:
1. Parses SYNTHESIS.md structure
2. Extracts decision points (recommendations, technology choices, tradeoffs)
3. Creates decision beads or annotations
4. Links decisions to feature beads via `bd dep add` or metadata

## Key Capabilities

- SYNTHESIS.md structure parser
- Decision extraction heuristics
- Bead annotation/linking
- Traceability queries

## Implementation Tasks

### Section 1: SYNTHESIS.md Parser
- [ ] Analyze common SYNTHESIS.md structures and formats
- [ ] Implement markdown section parser
- [ ] Extract decision points from recommendations sections
- [ ] Extract technology choices and rationale
- [ ] Extract tradeoffs and alternatives considered

### Section 2: Decision Bead Creation
- [ ] Define decision bead format/schema
- [ ] Implement decision-to-bead conversion
- [ ] Add metadata for decision type (technology, architecture, approach)
- [ ] Include source location (line numbers, section headers)

### Section 3: Bead Linking
- [ ] Implement linking via `bd dep add` for explicit dependencies
- [ ] Add metadata annotations for decision references
- [ ] Create bidirectional links (decision -> feature, feature -> decision)
- [ ] Handle updates when SYNTHESIS.md changes

### Section 4: Traceability Queries
- [ ] Implement "what research led to this feature?" query
- [ ] Implement "what features implement this decision?" query
- [ ] Add query results formatting for CLI output
- [ ] Consider integration with existing bead query tools

### Section 5: Testing
- [ ] Create sample SYNTHESIS.md files for testing
- [ ] Unit tests for parser
- [ ] Unit tests for decision extraction
- [ ] Integration tests for linking workflow
- [ ] Test traceability queries

### Section 6: Documentation
- [ ] Document SYNTHESIS.md expected format
- [ ] Document decision bead schema
- [ ] Add usage examples
- [ ] Update Context Engineering methodology docs

## Acceptance Criteria

- [ ] Parser extracts key decisions from SYNTHESIS.md
- [ ] Decisions linked to relevant feature beads
- [ ] Can query "what research led to this feature?"
- [ ] Can query "what features implement this decision?"

## Dependencies

- FEAT-014 (Stage 5 bead creation)
- SYNTHESIS.md format (from Context Engineering Stage 3)

## Notes

This feature bridges the gap between research artifacts and implementation artifacts, creating a complete audit trail from initial research through to shipped code. The traceability enables better decision-making for future changes by preserving the "why" behind technical choices.

Consider the following SYNTHESIS.md structures:
- Recommendations sections with numbered items
- Technology comparison tables
- Architecture decision records (ADRs) format
- Pros/cons lists
- Tradeoff analysis sections

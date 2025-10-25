# FEAT-004 Implementation Plan

## Overview
Add early-exit handling to OVERPROMPT workflows that automatically creates bugs/features when sessions fail unexpectedly. This ensures no knowledge is lost and failures become trackable work items.

## Objectives
1. Update both OVERPROMPT templates with early exit detection logic
2. Enhance .agent-state.json schema to track failures
3. Integrate with work-item-creation-agent (FEAT-003)
4. Ensure retrospective and summary still run on early exit
5. Provide comprehensive debugging context in created issues

## Approach

### Phase 1: Update OVERPROMPT Templates
- Add Early Exit Handling section after Phase 7
- Define exit conditions (3 consecutive failures, STOP command, critical errors)
- Implement early exit procedure with work-item-creation-agent invocation
- Provide specific case templates for different failure types

### Phase 2: Update State Schema
- Add failure tracking fields to .agent-state.json
- Update state management logic to track consecutive failures
- Reset failure count on success, increment on failure

### Phase 3: Update Safeguards Section
- Add Early Exit Protection to safeguards
- Document failure tracking and automatic bug creation

### Phase 4: Update Phase 6 (Retrospective)
- Ensure retrospective receives early exit context
- Pass early_exit_* fields to retrospective-agent

### Phase 5: Update Phase 7 (Summary Report)
- Ensure summary includes early-exit items created
- Document in "Issues Created" section

## Implementation Sections

### Section 1: Update OVERPROMPT Templates - Early Exit Detection
- Add comprehensive Early Exit Handling section
- Define all exit conditions
- Provide detailed procedure for each case

### Section 2: Update State Management
- Enhance .agent-state.json schema
- Add failure tracking fields
- Update state management documentation

### Section 3: Update Safeguards and Phase Contexts
- Add Early Exit Protection to safeguards
- Update Phase 6 to include early exit context
- Update Phase 7 to include early-exit items

## Success Criteria
- Both OVERPROMPT templates detect and handle early exits
- State tracking includes failure counts and exit reasons
- Retrospective and summary run even after early exit
- Created bugs include full debugging context
- All acceptance criteria from PROMPT.md met

## Dependencies
- FEAT-003: work-item-creation-agent must be available

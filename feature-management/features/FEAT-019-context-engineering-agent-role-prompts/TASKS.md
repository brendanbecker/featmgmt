# Task Breakdown: FEAT-019

**Work Item**: [FEAT-019: Context Engineering Agent Role Prompts](PROMPT.md)
**Status**: Not Started
**Last Updated**: 2026-01-11

## Prerequisites

- [ ] Read and understand PROMPT.md
- [ ] Review PLAN.md and update if needed
- [ ] Verify dependencies: FEAT-014 Stage 6 structure defined
- [ ] Confirm Gastown hook content format

## Section 1: Define Hook Content Format

- [ ] Document hook content structure for each role
- [ ] Define required context fields (project_name, stage, counts)
- [ ] Define optional context fields (custom metadata)
- [ ] Create JSON schema for hook validation
- [ ] Document hook content examples in PROMPT.md

## Section 2: Create Mayor Prompt

- [ ] Write base Mayor role prompt with identity
- [ ] Add CE stage awareness section (stages 1-6)
- [ ] Add pipeline orchestration commands table
- [ ] Add decision framework (when to sling, convoy, escalate)
- [ ] Add progress report format template
- [ ] Add error handling guidance
- [ ] Test with sample pipeline state injection

## Section 3: Create Polecat Prompt

- [ ] Write base Polecat role prompt with identity
- [ ] Add PROMPT.md execution guidance (section-by-section)
- [ ] Add featmgmt conventions section (file structure, status)
- [ ] Add git commit guidance (conventional commits)
- [ ] Add completion signaling checklist
- [ ] Add "when stuck" guidance
- [ ] Test with sample work item injection

## Section 4: Create Witness Prompt

- [ ] Write base Witness role prompt with identity
- [ ] Add quality monitoring rules (acceptance criteria, artifacts)
- [ ] Add stuck detection heuristics (time, pattern, token)
- [ ] Add recovery action levels (nudge, reassign, escalate)
- [ ] Add metrics tracking table
- [ ] Add report format template
- [ ] Test with sample monitoring scenario

## Section 5: Integration with gt sling

- [ ] Create `.gastown/prompts/` directory structure
- [ ] Write mayor-ce.md prompt file
- [ ] Write polecat-ce.md prompt file
- [ ] Write witness-ce.md prompt file
- [ ] Document rig.toml hook configuration
- [ ] Test prompt injection via gt sling
- [ ] Document troubleshooting for prompt issues

## Section 6: Testing and Validation

- [ ] Create test pipeline with sample beads
- [ ] Test Mayor prompt dispatches work correctly
- [ ] Test Polecat prompt executes work correctly
- [ ] Test Witness prompt detects stuck polecats
- [ ] Validate integration with FEAT-014 Stage 6 loop
- [ ] Document any prompt refinements needed
- [ ] Update PLAN.md with final implementation notes

## Verification Tasks

- [ ] All acceptance criteria from PROMPT.md met
- [ ] Prompts under target token counts
- [ ] Variable injection tested and working
- [ ] Update feature_request.json status to resolved
- [ ] Document completion in comments.md

## Completion Checklist

- [ ] All section tasks complete
- [ ] All tests passing
- [ ] PLAN.md updated with final approach
- [ ] Ready for review/merge

---
*Check off tasks as you complete them. Update status field above.*

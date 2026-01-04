# FEAT-012: Deprecate summary-reporter-agent and merge into retrospective-agent

**Priority**: P2
**Component**: agents
**Type**: improvement
**Estimated Effort**: medium
**Business Value**: medium

## Overview

The summary-reporter-agent generates 500+ line session reports that have ~70% overlap with retrospective-agent output. Analysis of actual session reports vs retrospective reports shows:

- Both contain: executive summary, component health, priority queue, failure analysis, next steps, recommendations
- Summary-reporter unique: git commit hashes, test duration stats, files modified list
- Retrospective unique: pattern recognition, dependency analysis, backlog mutations, priority accuracy assessment

The unique value from summary-reporter is marginal and easily absorbed by retrospective-agent.

## Rationale

1. **Never Used**: Session reports have never been reviewed - they exist but provide no value
2. **70% Redundancy**: Most content duplicates what retrospective already produces
3. **Workflow Simplification**: One comprehensive report is better than two overlapping reports
4. **Maintenance Burden**: Two report-generating agents means two things to maintain

## Implementation Tasks

### Section 1: Update retrospective-agent to include git operations summary
- [ ] Add "Git Operations Summary" section to retrospective report template
- [ ] Include commit hashes from the session
- [ ] Include files modified count
- [ ] Keep it concise (not the verbose 50-line version from summary-reporter)

### Section 2: Remove summary-reporter from OVERPROMPT templates
- [ ] Update OVERPROMPT-standard.md to remove Phase 6 (summary-reporter)
- [ ] Update OVERPROMPT-gitops.md to remove Phase 6 (summary-reporter)
- [ ] Renumber phases if needed or just remove the phase
- [ ] Update any cross-references to summary-reporter

### Section 3: Deprecate summary-reporter-agent definition
- [ ] Move summary-reporter-agent.md to deprecated/ or delete
- [ ] Update any agent documentation that references it
- [ ] Update CLAUDE.md if it mentions summary-reporter

### Section 4: Update consuming projects
- [ ] Document that projects using featmgmt should run update-project.sh
- [ ] Ensure sync-agents.sh no longer syncs summary-reporter-agent

### Section 5: Testing and verification
- [ ] Run OVERPROMPT workflow without summary-reporter
- [ ] Verify retrospective report contains git operations section
- [ ] Confirm no broken references remain

## Acceptance Criteria

- [ ] summary-reporter-agent is removed from OVERPROMPT workflow
- [ ] retrospective-agent includes git operations summary (commit hashes, files modified)
- [ ] No references to summary-reporter remain in templates
- [ ] Workflow completes successfully without summary-reporter phase

## Notes

Analysis performed 2026-01-04 comparing:
- `/home/becker/projects/tools/triager/feature-management/agent_runs/session-2025-11-01-111500.md` (522 lines)
- `/home/becker/projects/tools/triager/feature-management/agent_runs/retrospective-2025-11-01-113041.md` (559 lines)

Conclusion: The session report's unique value is marginal. Git commit hashes can be obtained from `git log`. Test duration (6.02s) is not actionable information.

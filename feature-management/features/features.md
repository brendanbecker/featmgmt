# Feature Tracking

**Last Updated**: 2025-10-23
**Repository**: featmgmt

## Summary Statistics

- **Total Features**: 4
- **By Priority**: P0: 0, P1: 1, P2: 1, P3: 0
- **By Status**:
  - New: 2
  - In Progress: 0
  - Completed: 2
  - Deprecated: 0

## Features by Priority

### P1 - High Priority (1)

| Feature ID | Title | Component | Priority | Status | Location |
|-----------|--------|-----------|----------|--------|----------|
| FEAT-003 | Create work-item-creation-agent for standardized issue creation | agents/shared | P1 | new | features/FEAT-003-work-item-creation-agent |

### Completed Features (2)

| Feature ID | Title | Component | Priority | Status | Location |
|-----------|--------|-----------|----------|--------|----------|
| FEAT-001 | Enable test-runner-agent to report encountered issues | agents/standard | P1 | completed | completed/FEAT-001-test-runner-issue-reporting |
| FEAT-002 | Empower retrospective-agent to create new bugs and features | agents/shared | P1 | completed | completed/FEAT-002-retrospective-issue-creation |

### P2 - Medium Priority (1)

| Feature ID | Title | Component | Priority | Status | Location |
|-----------|--------|-----------|----------|--------|----------|
| FEAT-004 | Early-exit bug/feature creation on session failures | workflow | P2 | new | features/FEAT-004-early-exit-bug-creation |

### P3 - Low Priority (0)

*No P3 features*

## Recent Activity

### 2025-10-23
- **FEAT-004** created: Early-exit bug/feature creation on session failures
  - Component: workflow
  - Type: enhancement
  - Dependency: FEAT-003
  - Automatically creates bugs/features when OVERPROMPT encounters early exit conditions
  - Prevents knowledge loss from failed sessions

- **FEAT-003** created: Create work-item-creation-agent for standardized issue creation
  - Component: agents/shared
  - Type: enhancement
  - Centralizes bug/feature/action creation logic for all agents
  - Enables DRY principle and consistent issue creation

- **FEAT-002** completed: Empower retrospective-agent to create new bugs and features
  - Component: agents/shared
  - Type: enhancement
  - Added pattern-based issue creation to retrospective-agent
  - Agent can now create bugs/features from recurring patterns, technical debt, and opportunities

- **FEAT-001** completed: Enable test-runner-agent to report encountered issues
  - Component: agents/standard
  - Type: enhancement
  - Added comprehensive issue detection and reporting to test-runner-agent
  - Agent can now automatically create bug/feature entries from test failures

### 2025-10-19
- **FEAT-001** created: Enable test-runner-agent to report encountered issues
  - Component: agents/standard
  - Type: enhancement
  - Enhances autonomous bug discovery and tracking

- **FEAT-002** created: Empower retrospective-agent to create new bugs and features
  - Component: agents/shared
  - Type: enhancement
  - Enables proactive backlog management through pattern analysis

## Feature Details

### FEAT-001: Test Runner Issue Reporting

**Description**: Extend test-runner-agent to automatically detect patterns in test failures that indicate bugs or missing features, and create draft bug/feature entries with structured issue reports.

**Business Value**: High - Improves autonomous bug discovery and tracking
**Technical Complexity**: Medium
**Estimated Effort**: Medium (2-3 hours)

**Key Capabilities**:
- Parse test failures and extract relevant information
- Identify failure patterns (bugs vs. features vs. environmental)
- Create well-structured bug/feature entries
- Include test output, stack traces, and context
- Link issues to test runs
- Update summary files automatically

**Tags**: agents, testing, automation, issue-tracking

**Files**:
- `features/FEAT-001-test-runner-issue-reporting/feature_request.json`
- `features/FEAT-001-test-runner-issue-reporting/PROMPT.md`
- `features/FEAT-001-test-runner-issue-reporting/PLAN.md`

---

### FEAT-002: Retrospective Issue Creation

**Description**: Extend retrospective-agent to analyze session patterns and create new bugs or features when identifying missing work items, technical debt, or improvement opportunities.

**Business Value**: High - Enables proactive issue identification and backlog health
**Technical Complexity**: Medium
**Estimated Effort**: Medium (3-4 hours)

**Key Capabilities**:
- Detect recurring failure patterns
- Identify automation opportunities
- Recognize technical debt accumulation
- Create bugs for systemic issues
- Create features for improvements
- Generate complete metadata and evidence
- Integrate with existing backlog workflow

**Tags**: agents, retrospective, automation, issue-tracking, backlog-management

**Files**:
- `features/FEAT-002-retrospective-issue-creation/feature_request.json`
- `features/FEAT-002-retrospective-issue-creation/PROMPT.md`
- `features/FEAT-002-retrospective-issue-creation/PLAN.md`

---

## Feature Workflow

### Lifecycle States

1. **New**: Feature proposal created, not yet started
2. **In Progress**: Implementation underway
3. **Completed**: Feature implemented and verified
4. **Deprecated**: No longer relevant or superseded

### Next Steps

To implement these features:

1. Review PROMPT.md files for detailed implementation instructions
2. Review PLAN.md files for technical design and integration points
3. Prioritize based on project needs and dependencies
4. Implement changes to agent definitions as specified
5. Test thoroughly using test scenarios outlined
6. Update status to "completed" when verified

## Dependencies

Both features are independent and can be implemented in any order. However:

- **FEAT-001** provides immediate value by detecting issues during test runs
- **FEAT-002** provides longer-term value by analyzing patterns across sessions

Recommended implementation order: FEAT-001 first, then FEAT-002

## Integration Notes

Both features enhance the featmgmt autonomous workflow:

- **FEAT-001** integrates into Phase 3 (Testing/Verification)
- **FEAT-002** integrates into Phase 6 (Retrospective)

Together, they create a closed feedback loop:
1. Tests run and detect issues (FEAT-001)
2. Retrospective analyzes patterns and creates strategic improvements (FEAT-002)
3. Both feed into the unified backlog for prioritization and execution

---

### FEAT-003: Work Item Creation Agent

**Description**: Centralized agent for creating bugs, features, and human actions with standardized format, duplicate detection, and automatic summary updates.

**Business Value**: High - Enables DRY principle and consistency
**Technical Complexity**: Medium
**Estimated Effort**: Medium (3-4 hours)

**Key Capabilities**:
- Create bugs, features, and human actions with proper structure
- Duplicate detection using configurable similarity threshold
- Automatic ID generation (next available)
- Metadata file generation (JSON + PROMPT.md/INSTRUCTIONS.md)
- Summary file updates (bugs.md, features.md, actions.md)
- Optional git operations (add, commit)
- Structured output for agent integration

**Integration Points**:
- test-runner-agent: Create bugs from test failures
- retrospective-agent: Create bugs/features from session analysis
- Any future agent needing to create work items

**Tags**: agents, automation, issue-tracking, shared

**Files**:
- `features/FEAT-003-work-item-creation-agent/feature_request.json`
- `features/FEAT-003-work-item-creation-agent/PROMPT.md`

---

### FEAT-004: Early Exit Bug Creation

**Description**: Automatically create bugs or features when OVERPROMPT encounters early exit conditions (failures, STOP commands, errors), preserving session context for debugging.

**Business Value**: Medium - Prevents knowledge loss from failed sessions
**Technical Complexity**: Low
**Estimated Effort**: Small (1-2 hours)
**Dependencies**: FEAT-003 (work-item-creation-agent)

**Key Capabilities**:
- Detect early exit conditions (3 failures, STOP, critical errors)
- Automatically invoke work-item-creation-agent
- Capture session state and debugging context
- Create P1 bugs with full evidence
- Allow retrospective to run despite early exit
- Include early-exit items in session summary

**Early Exit Triggers**:
- 3 consecutive item processing failures
- Explicit STOP command in comments.md
- Critical errors in workflow execution
- Subagent invocation failures

**Integration Points**:
- OVERPROMPT workflow: All phases
- work-item-creation-agent: Issue creation
- retrospective-agent: Pattern analysis
- summary-reporter-agent: Session reporting

**Tags**: overprompt, error-handling, automation

**Files**:
- `features/FEAT-004-early-exit-bug-creation/feature_request.json`
- `features/FEAT-004-early-exit-bug-creation/PROMPT.md`

---

**Note**: These features were created to enhance the autonomous capabilities of the featmgmt agent system. They represent strategic improvements to enable true self-improving autonomous workflows.

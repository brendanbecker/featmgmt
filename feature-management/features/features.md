# Feature Tracking

**Last Updated**: 2025-12-03
**Repository**: featmgmt

## Summary Statistics

- **Total Features**: 11
- **By Priority**: P0: 0, P1: 4, P2: 0, P3: 0
- **By Status**:
  - New: 4
  - In Progress: 0
  - Completed: 7
  - Deprecated: 0

## Features by Priority

### P1 - High Priority (4)

| Feature ID | Title | Component | Priority | Status | Location |
|-----------|--------|-----------|----------|--------|----------|
| FEAT-008 | Feature Management CRUD Skills | skills | P1 | new | features/FEAT-008-crud-skills |
| FEAT-009 | Feature Management Query Skills | skills | P1 | new | features/FEAT-009-query-skills |
| FEAT-010 | Semantic Search MCP Server | mcp-server | P1 | new | features/FEAT-010-semantic-search-mcp |
| FEAT-011 | Search Integration Skill | skills | P1 | new | features/FEAT-011-search-integration-skill |

### Completed Features (7)

| Feature ID | Title | Component | Priority | Status | Location |
|-----------|--------|-----------|----------|--------|----------|
| FEAT-007 | Add in_progress status tracking to bug-processor-agent and OVERPROMPT workflow | agents/standard | P1 | completed | completed/FEAT-007-status-tracking-workflow |
| FEAT-006 | Branch-based work item creation with human-in-the-loop PR review | agents/shared | P1 | completed | completed/FEAT-006-branch-based-item-creation |
| FEAT-001 | Enable test-runner-agent to report encountered issues | agents/standard | P1 | completed | completed/FEAT-001-test-runner-issue-reporting |
| FEAT-002 | Empower retrospective-agent to create new bugs and features | agents/shared | P1 | completed | completed/FEAT-002-retrospective-issue-creation |
| FEAT-003 | Create work-item-creation-agent for standardized issue creation | agents/shared | P1 | resolved | completed/FEAT-003-work-item-creation-agent |
| FEAT-004 | Early-exit bug/feature creation on session failures | workflow | P2 | resolved | completed/FEAT-004-early-exit-bug-creation |
| FEAT-005 | scan-prioritize-agent detects and recommends blocking human actions | agents/shared | P1 | resolved | completed/FEAT-005-scan-prioritize-blocking-actions |

### P2 - Medium Priority (0)

*No P2 features*

### P3 - Low Priority (0)

*No P3 features*

## Recent Activity

### 2025-12-03
- **FEAT-008** created: Feature Management CRUD Skills
  - Component: skills
  - Type: feature
  - Priority: P1
  - Business Value: High - Enables CRUD operations for bugs, features, and actions via skills
  - Estimated Effort: Medium
  - Technical Complexity: Medium
  - Skills: create-bug, create-feature, create-action, update-status, archive-item

- **FEAT-009** created: Feature Management Query Skills
  - Component: skills
  - Type: feature
  - Priority: P1
  - Business Value: High - Enables listing and querying work items
  - Estimated Effort: Small
  - Technical Complexity: Low
  - Skills: list-items (with filters), get-item

- **FEAT-010** created: Semantic Search MCP Server
  - Component: mcp-server
  - Type: feature
  - Priority: P1
  - Business Value: High - Enables semantic search across work items
  - Estimated Effort: Large
  - Technical Complexity: High
  - Features: ChromaDB with ONNX embeddings, per-project collections, on-demand indexing
  - MCP Tools: search, index, check_duplicates, get_similar, get_index_status

- **FEAT-011** created: Search Integration Skill
  - Component: skills
  - Type: feature
  - Priority: P1
  - Business Value: High - User-friendly interface to semantic search
  - Estimated Effort: Small
  - Technical Complexity: Low
  - Dependencies: FEAT-010
  - Skills: search-items, duplicate-check, find-similar

### 2025-10-25
- **FEAT-007** completed: Add in_progress status tracking to bug-processor-agent and OVERPROMPT workflow
  - Component: agents/standard
  - Type: enhancement
  - Priority: P1
  - Implemented by: bug-processor-agent
  - All 6 implementation tasks completed successfully
  - Modified 8 files (+176 insertions, -64 deletions)
  - Added Step 0 to bug-processor-agent for status tracking
  - Updated both OVERPROMPT variants (standard and gitops) Phase 4
  - Comprehensive documentation in CUSTOMIZATION.md and ARCHITECTURE.md
  - Changes committed: 5a4148afe954158689029749bcfb231bb48cf083
  - Verification passed with zero issues found
  - Key capabilities delivered:
    - Status lifecycle: new → in_progress → resolved
    - started_date tracking for time-to-completion metrics
    - Audit trail for complete work item timeline
    - Concurrent processing safety through in_progress lock
    - Foundation for abandonment detection

- **FEAT-007** created: Add in_progress status tracking to bug-processor-agent and OVERPROMPT workflow
  - Component: agents/standard
  - Type: enhancement
  - Priority: P1
  - Business Value: High - Improves visibility, enables audit trail, prevents concurrent processing conflicts
  - Estimated Effort: Small
  - Technical Complexity: Low

### 2025-10-24
- **FEAT-006** created: Branch-based work item creation with human-in-the-loop PR review
  - Component: agents/shared
  - Type: enhancement
  - Priority: P1
  - Business Value: High quality control checkpoint for auto-created work items
  - Enables human review of bulk/speculative items before entering master backlog
  - Prevents wasted processing cycles on duplicates and false positives
  - Dependencies: FEAT-003 (work-item-creation-agent)


- **FEAT-004** completed: Early-exit bug/feature creation on session failures
  - Component: workflow
  - Type: enhancement
  - Implemented by: bug-processor-agent
  - Enhanced OVERPROMPT templates with early-exit detection and bug creation
  - Integrated work-item-creation-agent for failure tracking
  - All acceptance criteria met

- **FEAT-005** completed: scan-prioritize-agent detects and recommends blocking human actions
  - Component: agents/shared
  - Type: enhancement
  - Implemented by: bug-processor-agent
  - Enhanced scan-prioritize-agent with blocking action detection
  - Added dependency analysis and user recommendations
  - All acceptance criteria met

- **FEAT-003** completed: Create work-item-creation-agent for standardized issue creation
  - Component: agents/shared
  - Type: enhancement
  - Implemented by: bug-processor-agent
  - Created comprehensive agent definition with full documentation
  - Updated test-runner-agent and retrospective-agent to delegate issue creation
  - All acceptance criteria met
  - Files created:
    - `claude-agents/shared/work-item-creation-agent.md` (comprehensive agent definition)
    - `TASKS.md` (implementation tracking)
  - Files modified:
    - `claude-agents/standard/test-runner-agent.md` (delegation workflow)
    - `claude-agents/shared/retrospective-agent.md` (delegation workflow)

### 2025-10-23
- **FEAT-005** created: scan-prioritize-agent detects and recommends blocking human actions
  - Component: agents/shared
  - Type: enhancement
  - Enhances scan-prioritize-agent to detect blocking dependencies
  - Surfaces human actions that block critical bugs/features in priority queue
  - Provides recommendations to unblock automated workflows

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

### FEAT-005: Scan-Prioritize Blocking Actions Detection

**Description**: Enhance scan-prioritize-agent to analyze human-actions/ directory, detect when human actions are blocking critical bugs or features, and surface these blocking actions in the priority queue with recommendations to the user.

**Business Value**: High - Improves workflow efficiency by preventing wasted cycles
**Technical Complexity**: Medium
**Estimated Effort**: Medium (3-4 hours)

**Key Capabilities**:
- Scan human-actions/ directory for pending actions
- Analyze blocking_items field to identify dependencies
- Calculate effective urgency based on highest blocked priority
- Mark blocked items in priority queue (blocked_by, status fields)
- Generate human_actions_required array with context
- Provide user recommendations for unblocking workflow
- Include summary statistics (blocking actions, blocked items counts)

**Problem Solved**:
Currently, agents may attempt to process bugs/features that are blocked by human prerequisites (e.g., "get database credentials"). This wastes agent cycles and creates failures. By detecting and surfacing these blocking human actions, users can complete prerequisites first, enabling successful automated processing.

**Enhanced Output**:
- Priority queue items marked with `blocked_by` and `status`
- `human_actions_required` array with blocking actions
- Recommendations: "⚠️ Complete ACTION-001 first - blocks BUG-003 (P0)"
- Summary statistics for visibility

**Integration Points**:
- scan-prioritize-agent: Core enhancement
- OVERPROMPT workflow: Display blocking action warnings
- work-item-creation-agent: Support blocking_items field
- Human actions directory: New dependency tracking

**Tags**: agents, prioritization, human-actions, workflow, dependencies

**Files**:
- `features/FEAT-005-scan-prioritize-blocking-actions/feature_request.json`
- `features/FEAT-005-scan-prioritize-blocking-actions/PROMPT.md`

**Related Work Items**:
- FEAT-003: work-item-creation-agent (should support blocking_items field)
- FEAT-004: Early-exit bug creation (may create human actions when blocked)

---

### FEAT-006: Branch-based Work Item Creation with Human-in-the-Loop PR Review

**Description**: Enhance work-item-creation-agent and git-ops-agent to support creating work items on a separate branch with automatic PR creation for human review. This creates an intelligent checkpoint where humans can review, consolidate, refine, or reject auto-created items before they enter the master backlog.

**Business Value**: High - Quality control checkpoint prevents wasted processing cycles
**Technical Complexity**: Medium
**Estimated Effort**: Medium (3-4 hours)
**Dependencies**: FEAT-003 (work-item-creation-agent)

**Problem Solved**:
Currently, agents create work items directly on master branch. This means:
- No quality control before items enter backlog
- Duplicate items waste processing cycles
- Multiple items sharing a root cause aren't consolidated
- Poorly-specified items cause agent failures
- No checkpoint to reject false positives

**Proposed Solution**:
1. Add optional `branch_name` parameter to work-item-creation-agent
2. Add `create-items-pr` operation to git-ops-agent
3. Agents create items on branch → create PR → human reviews → merge to master
4. Calling agents (retrospective, test-runner) optionally use branching for bulk/speculative items

**Workflow**:
```
Agent detects issues → Create on branch → Create PR → Human reviews →
Consolidate/refine/reject → Merge PR → Items enter master backlog
```

**Key Capabilities**:
- Create work items on separate branch
- Automatic PR creation with item summary
- PR includes links to all created items
- Human can consolidate duplicates before merging
- Easy rejection via PR closure
- Audit trail of what was created and why
- Backward compatible (direct-to-master still works)

**Integration Points**:
- work-item-creation-agent: Accept optional branch_name parameter
- git-ops-agent: Add create-items-pr operation
- retrospective-agent: Use branching for bulk pattern-based items
- test-runner-agent: Use branching for bulk test failures

**Acceptance Criteria**:
- work-item-creation-agent accepts optional branch_name parameter
- git-ops-agent supports create-items-pr mode
- PR includes summary with links to all items
- PR labeled "auto-created" for filtering
- Both workflows tested (direct and PR-based)
- Documentation updated with examples
- Backward compatibility maintained

**Tags**: agents, workflow, quality-control, human-in-the-loop, git-ops

**Files**:
- `features/FEAT-006-branch-based-item-creation/feature_request.json`
- `features/FEAT-006-branch-based-item-creation/PROMPT.md`

**Related Work Items**:
- FEAT-003: work-item-creation-agent (dependency - must exist)
- FEAT-004: Early-exit bug creation (could benefit from branching)
- FEAT-005: Blocking action detection (complementary quality gate)

---

**Note**: These features were created to enhance the autonomous capabilities of the featmgmt agent system. They represent strategic improvements to enable true self-improving autonomous workflows.

---

### FEAT-008: Feature Management CRUD Skills

**Description**: Create Claude Code skills for creating, updating, and archiving items in feature-management directories. Skills include: create-bug, create-feature, create-action, update-status, and archive-item. Skills encode best practices for interacting with feature-management repositories.

**Business Value**: High - Enables users to manage bugs, features, and human actions through natural language
**Technical Complexity**: Medium
**Estimated Effort**: Medium

**Key Capabilities**:
- create-bug: Create bug with metadata and PROMPT.md
- create-feature: Create feature request with metadata and PROMPT.md
- create-action: Create human action item with INSTRUCTIONS.md
- update-status: Transition item status with date tracking
- archive-item: Move completed items to completed/

**Tags**: skills, crud, bugs, features, human-actions, automation

**Files**:
- `features/FEAT-008-crud-skills/feature_request.json`
- `features/FEAT-008-crud-skills/PROMPT.md`

---

### FEAT-009: Feature Management Query Skills

**Description**: Create Claude Code skills for listing and retrieving items from feature-management directories. Skills include: list-items (with filtering by status, priority, component, tags) and get-item (retrieve full details of a specific item).

**Business Value**: High - Enables quick backlog queries and item retrieval
**Technical Complexity**: Low
**Estimated Effort**: Small

**Key Capabilities**:
- list-items: List with filters (status, priority, component, tags), sorting, pagination
- get-item: Retrieve full details including PROMPT.md, PLAN.md, TASKS.md content

**Tags**: skills, query, list, filter, bugs, features

**Files**:
- `features/FEAT-009-query-skills/feature_request.json`
- `features/FEAT-009-query-skills/PROMPT.md`

---

### FEAT-010: Semantic Search MCP Server

**Description**: Python MCP server providing semantic search for feature-management directories using ChromaDB with local ONNX embeddings. Per-project collections, on-demand indexing with staleness detection, duplicate detection.

**Business Value**: High - Enables finding related items and detecting duplicates
**Technical Complexity**: High
**Estimated Effort**: Large

**Key Capabilities**:
- search: Semantic search with filters and similarity scores
- index: Create/update ChromaDB collection for project
- check_duplicates: Find potential duplicates before item creation
- get_similar: Find items similar to existing item
- get_index_status: Report index health and staleness

**Architecture**:
- ChromaDB with ONNX embeddings (local, no API calls)
- Per-project collections at ~/.featmgmt/chromadb/{project_hash}/
- Indexes: titles, descriptions, PROMPT.md content
- On-demand re-indexing when files change

**Tags**: mcp, chromadb, semantic-search, embeddings, python

**Files**:
- `features/FEAT-010-semantic-search-mcp/feature_request.json`
- `features/FEAT-010-semantic-search-mcp/PROMPT.md`

---

### FEAT-011: Search Integration Skill

**Description**: Claude Code skills that leverage the semantic search MCP server (FEAT-010) to provide search-items and duplicate-check capabilities with best practices encoded.

**Business Value**: High - User-friendly interface to semantic search
**Technical Complexity**: Low
**Estimated Effort**: Small
**Dependencies**: FEAT-010 (Semantic Search MCP Server)

**Key Capabilities**:
- search-items: Natural language search with formatted results
- duplicate-check: Pre-creation duplicate detection with recommendations
- find-similar: Context gathering for related items

**Best Practices Encoded**:
- Always run duplicate-check before creating items
- Review resolved items for potential solutions
- Add related_items when creating similar-but-distinct items

**Tags**: skills, search, semantic-search, mcp, duplicates

**Files**:
- `features/FEAT-011-search-integration-skill/feature_request.json`
- `features/FEAT-011-search-integration-skill/PROMPT.md`

---

## Implementation Order

Recommended implementation order based on dependencies:

1. **FEAT-008** (CRUD Skills) - Foundational, no dependencies
2. **FEAT-009** (Query Skills) - Foundational, no dependencies
3. **FEAT-010** (Semantic Search MCP) - Foundational for search
4. **FEAT-011** (Search Integration Skill) - Depends on FEAT-010

FEAT-008 and FEAT-009 can be implemented in parallel.
FEAT-010 and FEAT-011 should be implemented sequentially.

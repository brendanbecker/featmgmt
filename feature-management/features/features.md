# Feature Tracking

**Last Updated**: 2026-01-11
**Repository**: featmgmt

## Summary Statistics

- **Total Features**: 17
- **By Priority**: P0: 0, P1: 7, P2: 2, P3: 1
- **By Status**:
  - New: 10
  - In Progress: 0
  - Completed: 7
  - Deprecated: 0

## Features by Priority

### P1 - High Priority (7)

| Feature ID | Title | Component | Priority | Status | Location |
|-----------|--------|-----------|----------|--------|----------|
| FEAT-008 | Feature Management CRUD Skills | skills | P1 | new | features/FEAT-008-crud-skills |
| FEAT-009 | Feature Management Query Skills | skills | P1 | new | features/FEAT-009-query-skills |
| FEAT-010 | Semantic Search MCP Server | mcp-server | P1 | new | features/FEAT-010-semantic-search-mcp |
| FEAT-011 | Search Integration Skill | skills | P1 | new | features/FEAT-011-search-integration-skill |
| FEAT-013 | Formalize Architecture-to-WAVES Pipeline | methodology | P1 | new | features/FEAT-013-architecture-to-waves-pipeline |
| FEAT-015 | Playwright-Automated Deep Research for Stage 2 | automation | P1 | new | features/FEAT-015-playwright-automated-deep-research |
| FEAT-018 | Stage 6 Gastown GUPP Loop Integration | automation | P1 | new | features/FEAT-018-stage-6-gastown-gupp-loop |

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

### P2 - Medium Priority (2)

| Feature ID | Title | Component | Priority | Status | Location |
|-----------|--------|-----------|----------|--------|----------|
| FEAT-017 | Migration Tool: featmgmt to Beads | tooling | P2 | new | features/FEAT-017-migration-tool-featmgmt-to-beads |
| FEAT-019 | Context Engineering Agent Role Prompts | agents | P2 | new | features/FEAT-019-context-engineering-agent-role-prompts |

### P3 - Low Priority (1)

| Feature ID | Title | Component | Priority | Status | Location |
|-----------|--------|-----------|----------|--------|----------|
| FEAT-016 | SYNTHESIS.md to Beads Bridge | parsing | P3 | new | features/FEAT-016-synthesis-md-to-beads-bridge |

## Recent Activity

### 2026-01-11
- **FEAT-019** created: Context Engineering Agent Role Prompts
  - Component: agents
  - Type: new_feature
  - Priority: P2
  - Business Value: Medium - Defines specialized agent behaviors for CE pipeline
  - Estimated Effort: Medium
  - Technical Complexity: Medium
  - Dependencies: FEAT-014 (master formula defines stages), FEAT-016 (Stage 6 loop uses these agents)
  - Key Capabilities:
    - Mayor prompt for CE orchestration (stage awareness, pipeline progression, polecat spawning)
    - Polecat prompt for implementation (PROMPT.md execution, featmgmt conventions, git commits)
    - Witness prompt for quality monitoring (stuck detection, acceptance criteria validation)
    - Hook content format definitions for Gastown integration
  - Requires Gastown installed

- **FEAT-018** created: Stage 6 Gastown GUPP Loop Integration
  - Component: automation
  - Type: new_feature
  - Priority: P1
  - Business Value: High - Enables parallel agent execution for Stage 6 implementation
  - Estimated Effort: Medium
  - Technical Complexity: Medium
  - Dependencies: FEAT-014 (master formula + Stage 5 bead generator)
  - Key Capabilities:
    - Formula for Stage 6 GUPP loop
    - Polecat spawning strategy (concurrency limits)
    - Convoy creation for batch work
    - Witness monitoring integration
    - Completion detection and bead closing
  - Implements: `bd ready` -> `gt sling` -> `gt convoy wait` -> `bd close` loop

- **FEAT-017** created: Migration Tool: featmgmt to Beads
  - Component: tooling
  - Type: new_feature
  - Priority: P2
  - Business Value: Medium - Enables existing projects to adopt beads workflow
  - Estimated Effort: Medium
  - Technical Complexity: Medium
  - Dependencies: FEAT-014 (Beads integration)
  - Key Capabilities:
    - Parse featmgmt directory structure (features/, bugs/)
    - Extract metadata from JSON files (priority, component, tags)
    - Infer dependencies from WAVES.md ordering
    - Generate `bd create` and `bd dep add` commands
    - Dry-run mode for preview without execution
    - Migration report generation
  - Enables migration without manual recreation of work items

- **FEAT-016** created: SYNTHESIS.md to Beads Bridge
  - Component: parsing
  - Type: new_feature
  - Priority: P3
  - Business Value: Low - Nice-to-have traceability from research to features
  - Estimated Effort: Small
  - Technical Complexity: Medium
  - Dependencies: FEAT-014 (Stage 5 bead creation)
  - Key Capabilities:
    - SYNTHESIS.md structure parser
    - Decision extraction heuristics
    - Bead annotation/linking
    - Traceability queries
  - Enables audit trail for "why was this built this way?" and context for future modifications

### 2026-01-10
- **FEAT-015** created: Playwright-Automated Deep Research for Stage 2
  - Component: automation
  - Type: new_feature
  - Priority: P1
  - Business Value: High - Eliminates manual browser work in Stage 2, completes the automation story for Context Engineering
  - Estimated Effort: Large
  - Technical Complexity: High
  - Dependencies: FEAT-014 (Beads formula integration)
  - Key Capabilities:
    - Session management (login state persistence)
    - Parallel execution across 3 browser tabs
    - Platform-specific UI navigation (Gemini, ChatGPT, Claude)
    - Completion detection and result extraction
    - Markdown conversion and automatic saving
  - Saves 15-30 minutes of human attention per research session

### 2026-01-09
- **FEAT-013** created: Formalize Architecture-to-WAVES Pipeline for Context Engineering
  - Component: methodology
  - Type: new_feature
  - Priority: P1
  - Business Value: High - Repeatable process for transforming architecture docs to implementation waves
  - Estimated Effort: Large
  - Technical Complexity: Medium
  - Pipeline Stages: Feature Enumeration -> Dependency Analysis -> Wave Generation
  - Artifacts: FEATURES.md, DEPENDENCIES.md, WAVES.md
  - Enables git worktree-based parallel development

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
    - Status lifecycle: new -> in_progress -> resolved
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
- retrospective-agent: Pattern analysis and session reporting

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
- Recommendations: "Warning: Complete ACTION-001 first - blocks BUG-003 (P0)"
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
3. Agents create items on branch -> create PR -> human reviews -> merge to master
4. Calling agents (retrospective, test-runner) optionally use branching for bulk/speculative items

**Workflow**:
```
Agent detects issues -> Create on branch -> Create PR -> Human reviews ->
Consolidate/refine/reject -> Merge PR -> Items enter master backlog
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

### FEAT-013: Formalize Architecture-to-WAVES Pipeline for Context Engineering

**Description**: Formalize a multi-stage pipeline to transform architecture documentation into an ordered feature list for parallel development. Creates a repeatable process with clear artifacts at each stage: Feature Enumeration (FEATURES.md), Dependency Analysis (DEPENDENCIES.md), and Wave Generation (WAVES.md).

**Business Value**: High - Repeatable process instead of ad-hoc prompting
**Technical Complexity**: Medium
**Estimated Effort**: Large

**Problem Solved**:
Currently the transformation from ARCHITECTURE.md + PROJECT_SUMMARY.md to WAVES.md is done ad-hoc. This creates:
- No structured feature extraction
- No explicit dependency analysis
- No intermediate artifacts for review
- Not reproducible or documentable

**Pipeline Stages**:
1. **Feature Enumeration**: Extract components, interfaces, capabilities, cross-cutting concerns -> FEATURES.md
2. **Dependency Analysis**: Map data, interface, runtime dependencies -> DEPENDENCIES.md
3. **Wave Generation**: Topological sort, depth grouping, critical path -> WAVES.md

**Key Capabilities**:
- Documented process for each stage with prompts and examples
- Templates for FEATURES.md and DEPENDENCIES.md
- Integration as Stage 2.5 in context engineering methodology
- Enables git worktree-based parallel development

**Tags**: methodology, context-engineering, automation, documentation

**Files**:
- `features/FEAT-013-architecture-to-waves-pipeline/feature_request.json`
- `features/FEAT-013-architecture-to-waves-pipeline/PROMPT.md`
- `features/FEAT-013-architecture-to-waves-pipeline/PLAN.md`
- `features/FEAT-013-architecture-to-waves-pipeline/TASKS.md`

---

### FEAT-015: Playwright-Automated Deep Research for Stage 2

**Description**: Automate Stage 2 (Deep Research) of the Context Engineering methodology using Playwright browser automation. Currently this stage requires manually copying the deep research prompt to three browser tabs (Gemini, ChatGPT, Claude), triggering their research features, waiting for completion, and saving results. This is the only manual stage in an otherwise automated pipeline.

**Business Value**: High - Eliminates manual browser work in Stage 2, completes the automation story for Context Engineering
**Technical Complexity**: High
**Estimated Effort**: Large
**Dependencies**: FEAT-014 (Beads formula integration)

**Problem Solved**:
Stage 2 is the weak link in Context Engineering automation:
- Manual copy/paste to 3 browser tabs
- Manual triggering of deep research features
- Manual waiting and polling for completion
- Manual extraction and saving of results
- Takes 15-30 minutes of human attention

**Proposed Solution**:
Create a Playwright-based automation that:
1. Takes a deep research prompt as input
2. Opens authenticated sessions to Gemini, ChatGPT, and Claude web UIs
3. Inputs the prompt and triggers each platform's research feature
4. Polls for completion (these can take 5-10 minutes each)
5. Extracts the results and converts to markdown
6. Saves to docs/research/{gemini,chatgpt,claude}_research.md

**Key Capabilities**:
- Session management (login state persistence)
- Parallel execution across 3 tabs
- Platform-specific UI navigation (Gemini Deep Research button, ChatGPT search, Claude web search)
- Completion detection for each platform
- Result extraction and markdown conversion
- Error handling and retry logic

**Integration Points**:
- Context Engineering Stage 2
- FEAT-014 (Beads formula) - could become a formula step
- MCP Playwright tools already available

**Tags**: automation, playwright, deep-research, context-engineering, stage-2

**Files**:
- `features/FEAT-015-playwright-automated-deep-research/feature_request.json`
- `features/FEAT-015-playwright-automated-deep-research/PROMPT.md`
- `features/FEAT-015-playwright-automated-deep-research/PLAN.md`
- `features/FEAT-015-playwright-automated-deep-research/TASKS.md`

---

### FEAT-016: SYNTHESIS.md to Beads Bridge

**Description**: Create a parser that extracts key decisions from SYNTHESIS.md and links them to beads, enabling traceability from research through to implementation.

**Business Value**: Low - Nice-to-have traceability from research to features
**Technical Complexity**: Medium
**Estimated Effort**: Small
**Dependencies**: FEAT-014 (Stage 5 bead creation)

**Problem Solved**:
SYNTHESIS.md contains key decisions and rationale from the research phase. Currently this context is lost when features are created. Linking decisions to their implementing beads would provide:
- Audit trail for "why was this built this way?"
- Traceability from research to code
- Context for future modifications

**Proposed Solution**:
Create a parser that:
1. Parses SYNTHESIS.md structure
2. Extracts decision points (recommendations, technology choices, tradeoffs)
3. Creates decision beads or annotations
4. Links decisions to feature beads via `bd dep add` or metadata

**Key Capabilities**:
- SYNTHESIS.md structure parser
- Decision extraction heuristics
- Bead annotation/linking
- Traceability queries

**Acceptance Criteria**:
- Parser extracts key decisions from SYNTHESIS.md
- Decisions linked to relevant feature beads
- Can query "what research led to this feature?"
- Can query "what features implement this decision?"

**Tags**: parsing, synthesis, traceability, beads

**Files**:
- `features/FEAT-016-synthesis-md-to-beads-bridge/feature_request.json`
- `features/FEAT-016-synthesis-md-to-beads-bridge/PROMPT.md`
- `features/FEAT-016-synthesis-md-to-beads-bridge/PLAN.md`
- `features/FEAT-016-synthesis-md-to-beads-bridge/TASKS.md`

---

### FEAT-017: Migration Tool: featmgmt to Beads

**Description**: Create a migration script that converts existing featmgmt feature-management directories into Beads. Parses PROMPT.md files, extracts implicit dependencies from WAVES.md if present, and generates `bd create` and `bd dep add` commands.

**Business Value**: Medium - Enables existing projects to adopt beads workflow
**Technical Complexity**: Medium
**Estimated Effort**: Medium
**Dependencies**: FEAT-014 (Beads integration)

**Problem Solved**:
Projects already using featmgmt have features defined in `features/*/PROMPT.md` format. To use beads/gastown, these need to be converted to beads with proper dependencies. Manual migration is tedious and error-prone.

**Proposed Solution**:
Create `scripts/migrate-featmgmt-to-beads.sh` that:
1. Scans `features/*/PROMPT.md` and `bugs/*/PROMPT.md`
2. Extracts metadata from `feature_request.json` / `bug_report.json`
3. Parses WAVES.md (if present) to infer dependencies
4. Generates `bd create` commands with `--body` containing PROMPT.md content
5. Generates `bd dep add` commands for all dependencies
6. Supports `--dry-run` to preview without executing
7. Creates migration report

**Key Capabilities**:
- Parse featmgmt directory structure (features/, bugs/)
- Extract metadata (priority, component, effort, tags)
- Infer dependencies from WAVES.md ordering
- Generate bd commands with proper escaping
- Dry-run mode for preview
- Migration report generation

**Tags**: migration, tooling, beads, featmgmt

**Files**:
- `features/FEAT-017-migration-tool-featmgmt-to-beads/feature_request.json`
- `features/FEAT-017-migration-tool-featmgmt-to-beads/PROMPT.md`
- `features/FEAT-017-migration-tool-featmgmt-to-beads/PLAN.md`
- `features/FEAT-017-migration-tool-featmgmt-to-beads/TASKS.md`

---

### FEAT-018: Stage 6 Gastown GUPP Loop Integration

**Description**: Implement the Stage 6 implementation loop using Gastown's GUPP (Gas Town Universal Propulsion Principle). This creates the `bd ready` -> `gt sling` -> `gt convoy wait` -> `bd close` loop that runs until all beads are complete.

**Business Value**: High - Enables parallel agent execution for Stage 6 implementation
**Technical Complexity**: Medium
**Estimated Effort**: Medium
**Dependencies**: FEAT-014 (master formula + Stage 5 bead generator)

**Problem Solved**:
After Stage 5 generates beads with dependencies, Stage 6 execution is still manual. Need automated orchestration that:
- Queries for unblocked work (`bd ready`)
- Assigns work to polecats (`gt sling`)
- Monitors completion (`gt convoy wait`)
- Closes completed beads (`bd close`)
- Loops until done

**Proposed Solution**:
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

**Key Capabilities**:
- Formula for Stage 6 GUPP loop
- Polecat spawning strategy (concurrency limits)
- Convoy creation for batch work
- Witness monitoring integration
- Completion detection and bead closing

**Tags**: gastown, beads, gupp, stage-6, implementation, formula

**Files**:
- `features/FEAT-018-stage-6-gastown-gupp-loop/feature_request.json`
- `features/FEAT-018-stage-6-gastown-gupp-loop/PROMPT.md`
- `features/FEAT-018-stage-6-gastown-gupp-loop/PLAN.md`
- `features/FEAT-018-stage-6-gastown-gupp-loop/TASKS.md`

---

### FEAT-019: Context Engineering Agent Role Prompts

**Description**: Create specialized agent role prompts for Context Engineering workflows in the Gastown ecosystem. Defines Mayor, Polecat, and Witness prompts tailored to CE pipeline orchestration.

**Business Value**: Medium - Defines specialized agent behaviors for CE pipeline
**Technical Complexity**: Medium
**Estimated Effort**: Medium
**Dependencies**: FEAT-014 (master formula defines stages), FEAT-016 (Stage 6 loop uses these agents)

**Problem Solved**:
Gastown agents need role-specific prompts to effectively orchestrate Context Engineering workflows. Generic prompts don't encode CE-specific knowledge about stages, artifacts, and quality criteria.

**Proposed Solution**:
Create role prompt templates:
1. **Mayor (CE Orchestrator)**: Understands CE stages 1-6, tracks pipeline progression, spawns polecats for Stage 6 implementation, reports progress to human overseer
2. **Polecat (CE Implementer)**: Understands PROMPT.md format, follows featmgmt conventions, creates proper commits, signals completion correctly
3. **Witness (CE Quality Monitor)**: Monitors implementation quality, detects stuck polecats, validates artifacts against acceptance criteria, triggers recovery actions

**Key Capabilities**:
- Role-specific system prompts with CE knowledge
- CE stage awareness (stages 1-6)
- Artifact format knowledge (PROMPT.md, TASKS.md, JSON metadata)
- Integration with existing featmgmt agents
- Hook content format definitions for Gastown

**Tags**: agents, prompts, gastown, mayor, polecat, witness, context-engineering

**Files**:
- `features/FEAT-019-context-engineering-agent-role-prompts/feature_request.json`
- `features/FEAT-019-context-engineering-agent-role-prompts/PROMPT.md`
- `features/FEAT-019-context-engineering-agent-role-prompts/PLAN.md`
- `features/FEAT-019-context-engineering-agent-role-prompts/TASKS.md`

---


## Implementation Order

Recommended implementation order based on dependencies:

1. **FEAT-008** (CRUD Skills) - Foundational, no dependencies
2. **FEAT-009** (Query Skills) - Foundational, no dependencies
3. **FEAT-010** (Semantic Search MCP) - Foundational for search
4. **FEAT-011** (Search Integration Skill) - Depends on FEAT-010
5. **FEAT-013** (Architecture-to-WAVES Pipeline) - Independent methodology work
6. **FEAT-015** (Playwright Deep Research) - Depends on FEAT-014, high impact for Context Engineering automation
7. **FEAT-018** (Stage 6 GUPP Loop) - Depends on FEAT-014, enables parallel implementation
8. **FEAT-017** (Migration Tool) - Depends on FEAT-014, enables adoption path for existing projects
9. **FEAT-019** (CE Agent Role Prompts) - Depends on FEAT-014 and FEAT-016, defines agent behaviors for CE pipeline
10. **FEAT-016** (SYNTHESIS.md to Beads Bridge) - Depends on FEAT-014, low priority traceability enhancement

FEAT-008 and FEAT-009 can be implemented in parallel.
FEAT-010 and FEAT-011 should be implemented sequentially.
FEAT-013, FEAT-015, FEAT-016, FEAT-017, FEAT-018, and FEAT-019 can be implemented independently (all after FEAT-014).

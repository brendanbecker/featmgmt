# Automated Bug/Feature Resolution Agent

You are an autonomous bug/feature resolution agent. **ALWAYS use specialized subagents for each phase.** Manual fallbacks are ONLY for debugging subagent failures.

## 🔧 Subagent Invocation Protocol

**CRITICAL**: Use the Task tool to invoke subagents. This is MANDATORY, not optional.

**Agent Discovery**: Claude Code automatically discovers agents from:
- Global: `~/.claude/agents/` (available to all projects)
- Local: `<project>/.claude/agents/` (project-specific)

Use `scripts/sync-agents.sh` to install agents. See CLAUDE.md for installation instructions.

Available subagents:
1. **scan-prioritize-agent**: Scans bugs/features, builds priority queue
2. **bug-processor-agent**: Executes PROMPT.md workflows section-by-section, commits changes
3. **test-runner-agent**: Runs tests, manages test database, creates human actions
4. **retrospective-agent**: Reviews session outcomes and reprioritizes backlog based on learnings, commits reprioritization
5. **summary-reporter-agent**: Generates comprehensive session reports

**Note on Git Operations**: Each agent is responsible for committing its own work. Git operations are intrinsic to each agent's responsibilities, not a separate concern.

## Phase 1: Scan & Prioritize → INVOKE scan-prioritize-agent

**IMMEDIATELY invoke scan-prioritize-agent using Task tool:**

```
Task tool parameters:
- subagent_type: "scan-prioritize-agent"
- description: "Scan and prioritize bugs/features"
- prompt: "Scan the feature-management repository at {{PROJECT_PATH}}/feature-management and build a priority queue of all unresolved bugs and features. Pull latest changes first with 'git pull origin master'. Read bugs/bugs.md and features/features.md. Scan human-actions/ directory for blocking actions. Sort by priority (P0>P1>P2>P3), then by number (oldest first). Bugs take precedence over features at same priority. Mark blocked items and surface human actions that block P0/P1 items. Return the complete priority queue with bug IDs, titles, priorities, components, blocking status, and human actions required."
```

**Expected output**: Priority queue of unresolved items with blocking status, human actions required, or "No items to process"

**Process scan-prioritize-agent output:**

1. **Check for blocking human actions:**
   - If `human_actions_required` is non-empty:
     - Display warnings prominently to user
     - Log blocking actions in session state
     - **Recommendation**: Complete human actions first before processing blocked items
     - **Decision point**: User can choose to skip blocked items or stop to complete actions

2. **Build working queue:**
   - Filter priority queue based on blocking status
   - **Option A (Recommended)**: Only process items with `status: "ready"`
   - **Option B**: Process all items (may fail on blocked items)
   - If all items are blocked, exit to Phase 6 (retrospective)

3. **Select next item:**
   - Choose highest priority item with `status: "ready"`
   - If no ready items exist, exit to Phase 6

**On subagent failure**: Only then execute manual fallback (see Manual Fallback section)

<details>
<summary>Manual Fallback Steps (ONLY if subagent fails)</summary>
1. Navigate to the feature-management directory
2. **Pull latest changes**: `git pull origin master` to ensure you have the latest items
3. **Read summary files**:
   - Read `bugs/bugs.md` for all bug summaries
   - Read `features/features.md` for all feature request summaries
4. Build a priority queue of unresolved items (status != "resolved" and status != "closed"):
   - Sort by priority (P0 > P1 > P2 > P3)
   - Within same priority, sort by bug/feature number (older first)
   - Bugs take precedence over features at the same priority level
5. If no unresolved items exist, report "No items to process" and exit
6. **Note**: After completing any item, you MUST update the status in both the summary file (bugs.md or features.md) AND the individual bug_report.json or feature_request.json
</details>

## Phase 2: Process Item (Bug or Feature) → INVOKE bug-processor-agent

**IMMEDIATELY invoke bug-processor-agent for the highest priority item:**

```
Task tool parameters:
- subagent_type: "bug-processor-agent"
- description: "Process {ITEM-ID} implementation"
- prompt: "Process item {ITEM-ID} at {{PROJECT_PATH}}/feature-management/{bugs|features}/{ITEM-ID}-[slug]/. Read PROMPT.md and execute all incomplete sections. Update TASKS.md with completion markers as you complete each section. Work in the appropriate component directory (orchestrator/classifier-worker/duplicate-worker/doc-generator-worker/git-manager-worker/shared). Follow all acceptance criteria. Return summary of changes made and sections completed."
```

**Expected output**: Implementation complete, TASKS.md updated, changes committed and pushed

**The bug-processor-agent will automatically**:
1. Read PROMPT.md, PLAN.md, and TASKS.md
2. Detect the next incomplete section
3. Execute all tasks in that section
4. Update TASKS.md with completion markers (`✅ COMPLETED - YYYY-MM-DD`)
5. Navigate to appropriate component directory (orchestrator/classifier-worker/duplicate-worker/doc-generator-worker/git-manager-worker/shared)
6. Follow acceptance criteria for each task
7. Commit changes with message: `fix({ITEM-ID}): [brief description]` or `feat({ITEM-ID}): [brief description]`
8. Push to origin master/main

**On subagent failure**: Mark item as "needs-review" and proceed to next item

<details>
<summary>Manual Fallback Steps (ONLY if subagent fails)</summary>
1. Select the highest priority unresolved item (bug or feature)
2. Read its `PROMPT.md` file completely
3. Navigate to the appropriate project directory based on component
4. Execute the instructions in PROMPT.md
5. Commit changes with message: `fix({ITEM-ID}): [brief description of changes]` or `feat({ITEM-ID}): [brief description of changes]`
</details>

## Phase 3: Test → INVOKE test-runner-agent

**IMMEDIATELY invoke test-runner-agent after implementation:**

```
Task tool parameters:
- subagent_type: "test-runner-agent"
- description: "Run tests for {ITEM-ID} changes"
- prompt: "Run all tests for components affected by {ITEM-ID}. Set up test database if needed using scripts/setup_test_db.sh. Run pytest with coverage. Work in component directory: [orchestrator/classifier-worker/duplicate-worker/doc-generator-worker/git-manager-worker/shared]. If tests fail, create human action items in feature-management/human_actions/. Return test results with pass/fail status and any issues found."
```

**Expected output**: Test results (all pass) or human action items for failures

**On test failure**: Invoke bug-processor-agent again to fix issues OR mark item as "test-failure"

<details>
<summary>Manual Fallback Steps (ONLY if subagent fails)</summary>
1. Navigate to component directory
2. Set up test database: `./scripts/setup_test_db.sh` (if backend)
3. Run tests: `pytest --cov=. --cov-report=xml`
4. If tests fail: Document failures and retry implementation
</details>

## Phase 4: Archive & Update Summary

**After bug-processor-agent completes and commits implementation:**

Execute archive operations directly:

1. **Update summary status**:
   - Update status in `bugs/bugs.md` or `features/features.md` to "resolved"
   - Update summary statistics at the bottom of the file

2. **Move to completed**:
   ```bash
   cd {{PROJECT_PATH}}/feature-management
   mv {bugs|features}/{ITEM-ID}-[slug] completed/
   ```

3. **Commit and push**:
   ```bash
   git add {bugs|features}/ completed/
   git commit -m "Archive {ITEM-ID}: Moved to completed after resolution"
   git push origin master
   ```

**Expected outcome**: Item archived, summary updated, changes committed

**Note**: This is a simple operation that doesn't require a separate agent. Each agent commits its own work - bug-processor-agent commits implementation, and you commit the archive operation.

## Phase 5: Retrospective → INVOKE retrospective-agent

**IMMEDIATELY invoke retrospective-agent after archiving (before final report):**

```
Task tool parameters:
- subagent_type: "retrospective-agent"
- description: "Conduct retrospective and reprioritize backlog"
- prompt: "Conduct retrospective analysis for current bug/feature resolution session. Analyze session outcomes from .agent-state.json (including early_exit_triggered and early_exit_reason fields if applicable), review ALL bugs and features in {{PROJECT_PATH}}/feature-management, identify items to deprecate/merge, reprioritize based on learnings (dependencies, component health, priority accuracy). Include any issues created during early exit in analysis. Update all bug_report.json and feature_request.json files, update bugs.md and features.md summary files. Commit all changes. Generate retrospective report to agent_runs/retrospective-[timestamp].md. Return backlog changes summary and top priority for next session."
```

**Expected output**: Retrospective report saved, backlog reprioritized, changes committed

**Context to provide:**
- Session summary (successful items, failed items)
- .agent-state.json (including early_exit_* fields if applicable)
- Created issues from early exit (if any)
- Overall patterns observed

**The retrospective-agent will automatically**:
1. Analyze session success/failure patterns
2. Review entire backlog (all bugs and features)
3. Identify items to deprecate (obsolete, superseded)
4. Merge duplicate/overlapping items
5. Reprioritize based on dependencies and learnings
6. Update all metadata files (JSON, summary files)
7. Commit changes with detailed explanation
8. Generate comprehensive retrospective report

**Note**: Retrospective runs even after early exit to ensure learnings are captured

**On subagent failure**: Skip retrospective and proceed to Phase 6

<details>
<summary>Manual Fallback Steps (ONLY if subagent fails)</summary>
1. Review session outcomes in `.agent-state.json`
2. Manually check for duplicate items to merge
3. Identify deprecated items and move to `deprecated/`
4. Update priority for items that proved more/less critical than expected
5. Commit changes: `git commit -m "Manual retrospective updates"`
6. Proceed to Phase 6
</details>

## Phase 6: Report → INVOKE summary-reporter-agent

**ALWAYS exit after completing 1 item:**
- Do NOT return to Phase 1
- Proceed directly to summary report
- User can re-run OVERPROMPT.md manually for next item

**INVOKE summary-reporter-agent to generate session report:**

```
Task tool parameters:
- subagent_type: "summary-reporter-agent"
- description: "Generate session report"
- prompt: "Generate comprehensive session report for bug/feature resolution session. Include: items processed, items completed, items failed, test results, git operations, total time, success rate. Include any early-exit items created during session in 'Issues Created' section. Save report to {{PROJECT_PATH}}/feature-management/agent_runs/session-[timestamp].md. Return report summary with key metrics and recommendations."
```

**Expected output**: Session report saved with statistics and recommendations

<details>
<summary>Manual Fallback Steps (ONLY if subagent fails)</summary>
1. Check if more unresolved items exist
2. If yes: Return to Phase 1 with next item
3. If no: Generate summary report:
   - List all items processed this session (now in `completed/`)
   - Note any items that failed or need human review
   - Include counts: resolved, failed, skipped
   - Commit report to `feature-management/agent_runs/run-[timestamp].md`
</details>

## PR-Based Work Item Creation (Optional)

### Overview

Agents can create work items on a separate branch for human review via PR before they enter the master backlog. This is useful when agents create multiple items that may need consolidation or refinement.

### When Agents Use PR Workflow

**retrospective-agent** (3+ items):
- Pattern analysis detects 3 or more issues to create
- Agent creates branch: `auto-items-YYYY-MM-DD-HHMMSS`
- Invokes work-item-creation-agent multiple times with `branch_name` and `auto_commit: false`
- Commits all items together
- Pushes branch and creates PR with `gh pr create`
- PR includes links to all PROMPT.md files and review guidelines

**test-runner-agent** (5+ failures):
- Test run detects 5 or more failures
- Creates branch for batch bug creation
- Same workflow as retrospective-agent
- PR includes test failure details and statistics

### Benefits

- **Quality Control**: Human can catch false positives before backlog entry
- **Consolidation**: "These 5 bugs share a root cause" → merge to 1 bug
- **Batch Review**: Review all auto-created items at once
- **Easy Rejection**: Close PR to discard all if agent misbehaved

### Human Review Workflow

1. **Agent creates PR** with auto-created items
2. **Human reviews** the PR:
   - Check for duplicates with existing backlog
   - Consolidate items that share root causes
   - Improve descriptions and acceptance criteria
   - Reject false positives
3. **Merge PR** → Items enter master backlog
4. **Next OVERPROMPT session** processes approved items

### Example

**retrospective-agent creates 5 bugs from pattern analysis:**
```
✅ Created 5 items on branch auto-items-2025-10-24-153045
✅ PR created: https://github.com/user/repo/pull/123
📋 Review and merge to add items to backlog
```

**Human reviews and consolidates:**
- Bugs #1-3 share OAuth root cause → consolidated to 1 bug
- Bug #4 is duplicate of existing BUG-015 → removed
- Bug #5 is valid → kept

**Result**: 2 items enter backlog instead of 5, better quality

### Requirements

- **GitHub CLI** (`gh`) must be installed for automatic PR creation
- If not available, agents provide manual instructions

## Early Exit Handling

### Exit Conditions

Monitor for these conditions throughout execution:

1. **3 Consecutive Failures**:
   - Track failure count in .agent-state.json
   - If 3 items fail in a row, trigger early exit

2. **Explicit STOP Command**:
   - Check comments.md for "STOP" marker
   - If found, trigger early exit

3. **Critical Errors**:
   - Subagent invocation failures (after 3 retries)
   - File system errors
   - Git operation failures
   - Trigger early exit

### Early Exit Procedure

When early exit is triggered:

1. **Capture Session State**:
   - Current item being processed
   - Failure count and error messages
   - Agent outputs (if any)
   - Git status (uncommitted changes)

2. **Create Issue via work-item-creation-agent**:

   Invoke work-item-creation-agent with:

   ```json
   {
     "item_type": "bug",
     "title": "Session failure: {reason}",
     "component": "{affected_component | workflow}",
     "priority": "P1",
     "evidence": [
       {
         "type": "file",
         "location": ".agent-state.json",
         "description": "Session state at failure"
       },
       {
         "type": "log",
         "location": "agent_runs/{timestamp}/",
         "description": "Session logs"
       },
       {
         "type": "output",
         "location": "error output text",
         "description": "Error messages"
       }
     ],
     "description": "OVERPROMPT session exited early due to: {reason}. This issue captures the context for debugging and resolution.",
     "metadata": {
       "severity": "high",
       "reproducibility": "{always | intermittent}",
       "steps_to_reproduce": [
         "Attempted to process item: {item_id}",
         "Failure occurred at phase: {phase}",
         "{specific_error_details}"
       ],
       "expected_behavior": "Session should complete successfully",
       "actual_behavior": "{what_happened}",
       "impact": "Blocked autonomous workflow execution"
     }
   }
   ```

3. **Proceed to Phase 6**: Run retrospective-agent despite early exit
4. **Proceed to Phase 7**: Run summary-reporter-agent
5. **Exit gracefully**

### Specific Cases

#### Case 1: 3 Consecutive Failures

```markdown
**Title**: "Session failure: 3 consecutive item processing failures"
**Component**: {last_item_component | workflow}
**Evidence**:
- All 3 failed items' directories
- Error outputs from bug-processor-agent or test-runner-agent
- .agent-state.json showing failure count
```

#### Case 2: Explicit STOP Command

```markdown
**Title**: "User-requested work: {work_description_from_comments}"
**Type**: feature (usually)
**Component**: {requested_component}
**Evidence**:
- comments.md with STOP marker and request details
```

#### Case 3: Critical Error

```markdown
**Title**: "Session failure: Critical error in {phase}"
**Component**: workflow
**Evidence**:
- Stack trace or error message
- Phase where error occurred
- Agent outputs if available
```

#### Case 4: Subagent Invocation Failures

```markdown
**Title**: "Session failure: Unable to invoke {agent_name}"
**Component**: agents/infrastructure
**Evidence**:
- Agent invocation attempts and errors
- Agent directory listing (.claude/agents/ or ~/.claude/agents/)
- Related to BUG-003
```

## Execution Flow (AUTOMATIC)

```
START
  ↓
[Phase 1] INVOKE scan-prioritize-agent
  ↓
  ├─→ Priority queue returned
  │
  └─→ IF no items in queue → [Phase 6] INVOKE retrospective-agent → [Phase 7] INVOKE summary-reporter-agent → END
  ↓
[Phase 2] INVOKE bug-processor-agent (highest priority item)
  ↓
  ├─→ Implementation successful
  │
  └─→ IF fails after 2 retries → Mark "needs-review" → Return to Phase 1
  ↓
[Phase 3] INVOKE test-runner-agent
  ↓
  ├─→ All tests pass
  │
  └─→ IF tests fail → Return to Phase 2 OR mark "test-failure" → Return to Phase 1
  ↓
[Phase 4] Archive & Update Summary (execute directly)
  ↓
  ├─→ Update summary file (bugs.md or features.md)
  ├─→ Move item directory to completed/
  ├─→ Commit with message 'Archive {ITEM-ID}: Moved to completed'
  └─→ Push to origin master
  ↓
[Phase 5] INVOKE retrospective-agent
  ↓
  ├─→ Analyze session outcomes
  ├─→ Review entire backlog
  ├─→ Deprecate obsolete items
  ├─→ Merge duplicates
  ├─→ Reprioritize based on learnings
  ├─→ Update metadata and summary files
  ├─→ Commit changes (owns its git operations)
  └─→ Generate retrospective report
  ↓
[Phase 6] INVOKE summary-reporter-agent
  ↓
  └─→ Generate session report → EXIT (session complete)
  ↓
User re-runs OVERPROMPT.md for next item
```

## Critical Rules

1. **ALWAYS invoke subagents first** - Manual steps are ONLY for debugging subagent failures
2. **Use Task tool with correct subagent_type** - Don't execute work yourself that subagents can do
3. **Pass complete context in prompts** - Include full paths, item IDs, component directories, requirements
4. **Check subagent output** - Verify tasks completed successfully before proceeding to next phase
5. **On subagent failure after 2 retries** - Mark item "needs-review", log the issue, and continue with next item
6. **Never skip phases** - Execute all 6 phases in order (including retrospective after session)
7. **Update state continuously** - Keep `.agent-state.json` current for recovery capability
8. **Git operations ownership** - Each agent commits its own work; don't delegate git operations unnecessarily

## Safeguards

- **Solo developer workflow**: Commit directly to master/main (no feature branches during build-out phase)
- **If an item's PROMPT.md execution fails 3 times**, mark it as "needs-review" and skip to next item
- **Maintain state in `.agent-state.json`** to track attempts and resume if interrupted
- **Before any destructive operations**, verify you're in the correct directory
- **If tests fail after implementation**, rollback changes and mark item as "test-failure"
- **Limit loop iterations** to prevent infinite loops (max 1 item per session - exits after first item)
- **Early Exit Protection**:
  - **Failure Tracking**: Count consecutive failures in .agent-state.json
  - **Automatic Bug Creation**: Create bugs for unresolved failures via work-item-creation-agent
  - **Knowledge Preservation**: Capture session state before exit (.agent-state.json, logs, error output)
  - **Graceful Shutdown**: Allow retrospective and summary to run even on early exit

## Exit Conditions

- **All items resolved** (queue empty) OR
- **Encountered 3 consecutive failures** OR
- **Max iterations reached** (1 item per session) OR
- **Explicit STOP command** in any item's comments.md

## State Management
Create/update `.agent-state.json`:
```json
{
  "session_id": "[uuid]",
  "started_at": "[timestamp]",
  "items_processed": [],
  "items_completed": [],
  "items_failed": [],
  "current_item": null,
  "attempt_count": {},
  "consecutive_failures": 0,
  "failure_count": 0,
  "last_failures": [],
  "early_exit_triggered": false,
  "early_exit_reason": null,
  "bugs_processed": [],
  "bugs_completed": [],
  "bugs_failed": [],
  "current_bug": null
}
```

**State Update Logic**:
- **On Success**: Set `failure_count` to 0, clear `last_failures` array
- **On Failure**: Increment `failure_count`, append failed item ID to `last_failures` array
- **On Early Exit**: Set `early_exit_triggered` to true, set `early_exit_reason` to description of exit condition

**Note**: `items_completed` contains items (bugs/features) that were successfully resolved and moved to `completed/` directory. Legacy fields (`bugs_*`, `current_bug`) are maintained for backward compatibility and should mirror the generic fields (`items_*`, `current_item`).

## Error Recovery
If interrupted and restarted:
1. Check for `.agent-state.json`
2. Resume from `current_item` if exists
3. Skip items in `items_processed` or `items_completed`
4. Respect attempt counts for failed items
5. Verify completed items are actually in `completed/` directory (may need to move if interrupted mid-completion)

## Logging
Log all actions to `feature-management/agent_runs/session-[uuid].log`:
- Timestamp each action
- Record decisions and reasoning
- Include error messages and stack traces
- Note any manual intervention required

## Maintaining Summary Files

The `bugs/bugs.md` and `features/features.md` files are THE source of truth for quick scanning.

**When to Update**:
- After changing any bug/feature status (new → in-progress → resolved → closed)
- After creating new bugs/features (should be handled by triage agent)
- After archiving completed items
- Whenever summary statistics change

**What to Update**:
1. **Status column**: Change status for the specific item
2. **Summary Statistics section**: Update counts (Total, P0/P1/P2/P3, status breakdown)
3. **Last updated date**: Update the timestamp at the top of the file
4. **Location column**: Update if item moved between directories

**Example Update Process**:
```bash
# 1. Edit bugs.md to change BUG-009 status from "new" to "resolved"
# 2. Update summary stats: New: 15→14, Resolved: 0→1
# 3. Update "Last updated" date
# 4. Commit changes
cd {{PROJECT_PATH}}/feature-management
git add bugs/bugs.md
git commit -m "Update BUG-009 status to resolved"
git push origin master
```

**Critical**: These files enable fast Phase 1 scanning. Keep them accurate!

## How to Start

**When you read this file, IMMEDIATELY begin execution:**

1. **Phase 1**: INVOKE scan-prioritize-agent (see Phase 1 section for exact Task tool parameters)
2. **Wait for output**: Review the priority queue returned
3. **IF items exist**: Proceed to Phase 2 with highest priority item
4. **IF no items**: INVOKE retrospective-agent, then summary-reporter-agent and report "No items to process"

**DO NOT ask the user for permission.** This is an autonomous workflow. Execute automatically.

**Example first message after reading this OVERPROMPT.md:**

> "Starting autonomous bug/feature resolution workflow. Invoking scan-prioritize-agent to build priority queue..."
>
> [INVOKE Task tool with scan-prioritize-agent parameters]

---

**START EXECUTION NOW WITH PHASE 1.**

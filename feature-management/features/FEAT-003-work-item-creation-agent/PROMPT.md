# FEAT-003: Create work-item-creation-agent for standardized issue creation

**Priority**: P1
**Component**: agents/shared
**Type**: enhancement
**Estimated Effort**: medium
**Business Value**: high

## Overview

Both test-runner-agent and retrospective-agent now need to create bugs, features, and human actions. This logic is duplicated and should be centralized in a dedicated work-item-creation-agent that handles:

- Bug creation (bug_report.json + PROMPT.md + bugs.md update)
- Feature creation (feature_request.json + PROMPT.md + features.md update)
- Human action creation (action_report.json + INSTRUCTIONS.md + actions.md update)
- Duplicate detection
- ID generation
- Summary file updates
- Git operations (add, commit)

## Benefits

- **DRY principle**: Single source of truth for issue creation
- **Consistency**: All created items follow same format
- **Maintainability**: Update templates in one place
- **Reusability**: Any agent can invoke for issue creation
- **Quality**: Centralized validation and duplicate detection

## Proposed Interface

### Input Parameters

The agent should accept the following structured input:

```json
{
  "item_type": "bug | feature | human_action",
  "title": "string",
  "component": "string",
  "priority": "P0 | P1 | P2 | P3",
  "evidence": [
    {
      "type": "file | log | output | link",
      "location": "path or URL",
      "description": "what this evidence shows"
    }
  ],
  "description": "string",
  "metadata": {
    // Type-specific fields:
    // For bugs: severity, reproducibility, steps_to_reproduce, etc.
    // For features: estimated_effort, business_value, user_impact, etc.
    // For human_actions: urgency, required_expertise, etc.
  }
}
```

### Output Format

The agent should return:

```json
{
  "success": true,
  "item_id": "BUG-XXX | FEAT-XXX | ACTION-XXX",
  "location": "bugs/BUG-XXX-slug/ | features/FEAT-XXX-slug/ | human-actions/ACTION-XXX-slug/",
  "files_created": [
    "bugs/BUG-XXX-slug/bug_report.json",
    "bugs/BUG-XXX-slug/PROMPT.md"
  ],
  "summary_updated": true,
  "commit_hash": "abc123... (if auto-commit enabled)",
  "duplicate_check": {
    "checked": true,
    "similar_items": [
      {
        "item_id": "BUG-001",
        "similarity": 0.85,
        "location": "bugs/BUG-001-slug/"
      }
    ],
    "is_duplicate": false
  }
}
```

## Implementation Tasks

### Task 1: Create Agent Definition File

**File**: `claude-agents/shared/work-item-creation-agent.md`

Create new agent with the following sections:

```markdown
# work-item-creation-agent

## Purpose

Standardized creation of bugs, features, and human action items in featmgmt repositories.

## Capabilities

1. **ID Generation**: Determine next available ID for item type
2. **Duplicate Detection**: Check for similar existing items
3. **Directory Creation**: Create proper directory structure
4. **Metadata Files**: Write JSON metadata (bug_report.json, feature_request.json, action_report.json)
5. **Instruction Files**: Write PROMPT.md or INSTRUCTIONS.md from templates
6. **Summary Updates**: Update bugs.md, features.md, or actions.md
7. **Git Operations**: Optionally commit created items

## Input Format

[Document the JSON input structure shown above]

## Processing Steps

1. Validate input parameters
2. Load .agent-config.json for duplicate threshold
3. Scan existing items of same type
4. Check for duplicates (title similarity, description similarity)
5. Generate next available ID
6. Create slug from title (lowercase, hyphens, max 50 chars)
7. Create directory: {type}/{ID}-{slug}/
8. Write metadata JSON file
9. Generate PROMPT.md or INSTRUCTIONS.md from template
10. Update summary file (bugs.md, features.md, actions.md)
11. Optionally: git add and commit

## Output Format

[Document the JSON output structure shown above]

## Error Handling

- **Duplicate Detected**: Return error with similar item details
- **Invalid Input**: Return validation errors
- **File Write Failure**: Return error with specific file/path
- **Git Operation Failure**: Return error but preserve created files

## Integration Points

- test-runner-agent: Create bugs from test failures
- retrospective-agent: Create bugs/features from session analysis
- Future agents: Any agent needing to create work items
```

### Task 2: Implement ID Generation Logic

The agent must:

1. Read the appropriate directory (bugs/, features/, human-actions/)
2. Parse existing item IDs (e.g., BUG-001, BUG-002)
3. Find the highest numeric ID
4. Increment by 1
5. Format as {TYPE}-{NUMBER} (e.g., BUG-003)

Handle edge cases:
- Empty directory (start at 001)
- Gaps in numbering (use max + 1, ignore gaps)
- Items in completed/ or deprecated/ (don't reuse those IDs)

### Task 3: Implement Duplicate Detection

The agent must:

1. Load `.agent-config.json` to get `duplicate_similarity_threshold` (default: 0.75)
2. Compare new item's title and description against existing items
3. Calculate similarity score (can use simple word overlap ratio)
4. If similarity >= threshold, flag as potential duplicate
5. Return list of similar items to user for review

### Task 4: Implement Metadata File Templates

#### Bug Template (bug_report.json)

```json
{
  "bug_id": "{ID}",
  "title": "{title}",
  "component": "{component}",
  "severity": "{severity}",
  "priority": "{priority}",
  "status": "new",
  "reported_date": "{date}",
  "updated_date": "{date}",
  "assigned_to": null,
  "tags": {tags_array},
  "affected_versions": ["{version}"],
  "environment": "{environment}",
  "reproducibility": "{reproducibility}",
  "description": "{description}",
  "steps_to_reproduce": {steps_array},
  "expected_behavior": "{expected}",
  "actual_behavior": "{actual}",
  "evidence": {evidence_object},
  "root_cause": "{root_cause}",
  "impact": "{impact}"
}
```

#### Feature Template (feature_request.json)

```json
{
  "feature_id": "{ID}",
  "title": "{title}",
  "component": "{component}",
  "priority": "{priority}",
  "status": "new",
  "type": "{type}",
  "created_date": "{date}",
  "updated_date": "{date}",
  "assigned_to": null,
  "tags": {tags_array},
  "estimated_effort": "{effort}",
  "dependencies": {dependencies_array},
  "description": "{description}",
  "business_value": "{value}",
  "technical_complexity": "{complexity}",
  "user_impact": "{impact}"
}
```

#### Human Action Template (action_report.json)

```json
{
  "action_id": "{ID}",
  "title": "{title}",
  "component": "{component}",
  "urgency": "{urgency}",
  "status": "pending",
  "created_date": "{date}",
  "updated_date": "{date}",
  "assigned_to": null,
  "tags": {tags_array},
  "required_expertise": "{expertise}",
  "estimated_time": "{time}",
  "description": "{description}",
  "reason": "{reason}",
  "blocking_items": {blocking_array},
  "evidence": {evidence_object}
}
```

### Task 5: Implement PROMPT.md/INSTRUCTIONS.md Generation

The agent must generate appropriate instruction files:

#### For Bugs (PROMPT.md)

```markdown
# {ID}: {title}

**Priority**: {priority}
**Component**: {component}
**Severity**: {severity}
**Status**: new

## Problem Statement

{description}

## Evidence

{evidence_section}

## Implementation Tasks

{tasks_section - generated from steps_to_reproduce or evidence}

## Acceptance Criteria

- [ ] Bug is reproducibly fixed
- [ ] Tests added to prevent regression
- [ ] All affected functionality tested

## Notes

{additional_context}
```

#### For Features (PROMPT.md)

```markdown
# {ID}: {title}

**Priority**: {priority}
**Component**: {component}
**Type**: {type}
**Estimated Effort**: {estimated_effort}
**Business Value**: {business_value}

## Overview

{description}

## Benefits

{benefits_section}

## Implementation Tasks

{tasks_section}

## Acceptance Criteria

{criteria_section}

## Notes

{additional_context}
```

#### For Human Actions (INSTRUCTIONS.md)

```markdown
# {ID}: {title}

**Urgency**: {urgency}
**Component**: {component}
**Required Expertise**: {required_expertise}
**Estimated Time**: {estimated_time}

## What Needs to Be Done

{description}

## Why Human Intervention Is Needed

{reason}

## Evidence/Context

{evidence_section}

## Blocking Items

{blocking_items_list}

## Next Steps

{next_steps}
```

### Task 6: Implement Summary File Updates

#### Update bugs.md

Add new row to the bug list table:

```markdown
| {ID} | {title} | {priority} | {status} | {component} | {location} |
```

Update statistics:
- Total Bugs: +1
- New: +1

#### Update features.md

Add new row to appropriate priority section:

```markdown
| {ID} | {title} | {component} | {priority} | {status} | {location} |
```

Update statistics:
- Total Features: +1
- By Priority: {priority}: +1
- By Status New: +1

Add to Recent Activity section with timestamp.

#### Update actions.md

Similar structure to bugs.md but for human actions.

### Task 7: Implement Optional Git Operations

The agent should optionally (based on input flag `auto_commit: true`):

```bash
git add {item_directory}
git add {summary_file}
git commit -m "Add {item_type} {ID}: {title}"
```

Return commit hash in output if successful.

### Task 8: Update test-runner-agent Integration

**File**: `claude-agents/standard/test-runner-agent.md`

Replace the issue creation section with:

```markdown
## Issue Creation (Delegated to work-item-creation-agent)

When test failures indicate bugs or missing features:

1. Classify the failure type (bug, feature, or environmental)
2. Prepare input for work-item-creation-agent:
   - Extract title from test name or error message
   - Determine component from test file path
   - Set priority based on failure severity
   - Collect evidence (test output, stack traces, logs)
   - Generate description with context
3. Invoke work-item-creation-agent via Task tool
4. Include created items in test report output

Example invocation:
[Provide detailed example of calling work-item-creation-agent]
```

### Task 9: Update retrospective-agent Integration

**File**: `claude-agents/shared/retrospective-agent.md`

Replace the issue creation section with:

```markdown
## Pattern-Based Issue Creation (Delegated to work-item-creation-agent)

When analyzing session patterns, create issues for:

1. **Recurring Failures**: Create bug with pattern evidence
2. **Missing Capabilities**: Create feature for enhancement
3. **Blocked Operations**: Create human action

For each identified issue:
1. Prepare structured input for work-item-creation-agent
2. Invoke via Task tool
3. Include created items in retrospective report

Example invocation:
[Provide detailed example of calling work-item-creation-agent]
```

### Task 10: Update sync-agents.sh

**File**: `scripts/sync-agents.sh`

Add work-item-creation-agent to the shared agents list:

```bash
SHARED_AGENTS=(
  "git-ops-agent"
  "retrospective-agent"
  "summary-reporter-agent"
  "work-item-creation-agent"  # NEW
)
```

## Acceptance Criteria

- [ ] Create `claude-agents/shared/work-item-creation-agent.md`
- [ ] Agent handles all three item types (bugs, features, human actions)
- [ ] Implements duplicate detection using `.agent-config.json` threshold
- [ ] Generates next available ID correctly
- [ ] Creates proper directory structure
- [ ] Writes metadata files (JSON) with all required fields
- [ ] Writes PROMPT.md/INSTRUCTIONS.md using templates
- [ ] Updates summary files (bugs.md, features.md, actions.md)
- [ ] Optional: Git add and commit created items
- [ ] Returns structured output with item details
- [ ] Update test-runner-agent.md to use work-item-creation-agent
- [ ] Update retrospective-agent.md to use work-item-creation-agent
- [ ] Add work-item-creation-agent to sync-agents.sh

## Testing Strategy

### Unit Tests (Manual Verification)

1. **Test bug creation:**
   - Input: Valid bug data
   - Expected: BUG-XXX created with all files
   - Verify: bug_report.json, PROMPT.md, bugs.md updated

2. **Test feature creation:**
   - Input: Valid feature data
   - Expected: FEAT-XXX created with all files
   - Verify: feature_request.json, PROMPT.md, features.md updated

3. **Test human action creation:**
   - Input: Valid action data
   - Expected: ACTION-XXX created with all files
   - Verify: action_report.json, INSTRUCTIONS.md, actions.md updated

4. **Test duplicate detection:**
   - Input: Bug similar to existing bug
   - Expected: Warning with similarity score
   - Verify: Duplicate check output is accurate

5. **Test ID generation:**
   - Input: Create multiple items
   - Expected: Sequential IDs (BUG-001, BUG-002, BUG-003)
   - Verify: No ID collisions

### Integration Tests

1. **Test from test-runner-agent:**
   - Run test-runner-agent on failing tests
   - Verify it invokes work-item-creation-agent
   - Check created bug items

2. **Test from retrospective-agent:**
   - Run retrospective-agent on session with patterns
   - Verify it invokes work-item-creation-agent
   - Check created bug/feature items

## Notes

This agent is a **key infrastructure component** that enables other agents to create work items autonomously. It should be robust, well-tested, and carefully documented since many other agents will depend on it.

## Dependencies

None - this is a foundational agent that other agents depend on.

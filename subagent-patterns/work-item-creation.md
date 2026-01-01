# Work Item Creation Pattern

## Purpose

Provides a standardized, centralized mechanism for creating work items (bugs, features, human action items) in a feature management repository. This pattern ensures consistency across all agents that need to create trackable work, eliminating duplication and maintaining data integrity.

## Problem Statement

Without a centralized work item creation pattern:

- **Inconsistent formatting**: Different agents create items with varying structures
- **ID collisions**: Without coordination, multiple agents may generate conflicting IDs
- **Duplicate work items**: Similar issues get created without detection
- **Missing metadata**: Required fields are omitted inconsistently
- **Summary drift**: Index files become out of sync with actual items
- **Lost discoveries**: Issues found during execution aren't tracked systematically

This pattern solves these problems by providing a single, well-defined interface for work item creation that all other agents delegate to.

## Responsibilities

- **ID Generation**: Determine the next available unique identifier for the item type
- **Duplicate Detection**: Check for semantically similar existing items before creation
- **Directory Structure**: Create properly formatted directory hierarchy
- **Metadata Files**: Write structured metadata (JSON) with all required fields
- **Instruction Files**: Generate actionable PROMPT.md or INSTRUCTIONS.md documents
- **Index Updates**: Update summary/index files with new entries
- **Branch Management**: Optionally create items on feature branches for review
- **Version Control**: Optionally commit created items atomically

## Workflow

### 1. Validate Input Parameters

Verify all required fields are present and correctly typed:
- Item type is valid (bug, feature, human_action)
- Priority format is valid
- Repository path exists
- Type-specific metadata is complete

### 2. Load Configuration

Read repository configuration to obtain:
- Duplicate similarity threshold
- Available tags and components
- Component detection keywords
- Severity classification rules

### 3. Scan Existing Items

Search the repository to:
- Enumerate all existing item IDs (active, completed, deprecated)
- Build a list of existing titles and descriptions for duplicate checking
- Identify the highest existing ID number

### 4. Check for Duplicates

Compare the proposed item against existing items:
- Calculate title similarity using word overlap
- Calculate description similarity
- Combine into overall similarity score
- Flag items exceeding the similarity threshold
- Continue with creation but include warnings

### 5. Generate Next Available ID

Using the scanned data:
- Find the maximum existing ID across all directories
- Increment by one
- Format according to type (BUG-XXX, FEAT-XXX, ACTION-XXX)

### 6. Create Slug from Title

Transform the title into a filesystem-safe identifier:
- Convert to lowercase
- Replace spaces and special characters with hyphens
- Remove consecutive hyphens
- Truncate to reasonable length

### 7. Handle Branch Creation (Optional)

If branch-based workflow is requested:
- Check if specified branch exists
- Create or checkout the branch
- All subsequent operations occur on this branch

### 8. Create Directory Structure

Create the item directory:
- Format: `{item_type}s/{ID}-{slug}/`
- Ensure parent directories exist

### 9. Write Metadata File

Create structured metadata appropriate to item type:

**For Bugs:**
- ID, title, component, severity, priority
- Status (new), dates (created, updated)
- Steps to reproduce, expected/actual behavior
- Evidence references, root cause analysis

**For Features:**
- ID, title, component, type, priority
- Business value, technical complexity, effort estimate
- Dependencies, user impact

**For Human Actions:**
- ID, title, urgency, required expertise
- Reason for human intervention
- Blocking items, estimated time

### 10. Generate Instruction Document

Create actionable documentation:

**For Bugs/Features (PROMPT.md):**
- Problem statement or feature overview
- Evidence and context
- Sectioned implementation tasks with checkboxes
- Acceptance criteria
- Notes and additional context

**For Human Actions (INSTRUCTIONS.md):**
- What needs to be done
- Why human intervention is needed
- Steps to complete
- Next steps after completion

### 11. Update Index/Summary File

Modify the appropriate summary file:
- Add new row to tracking table
- Update statistics counters
- Add entry to recent activity section

### 12. Commit Changes (Optional)

If auto-commit is enabled:
- Stage created files
- Commit with descriptive message
- Return commit hash

## Input Contract

### Required Inputs

| Field | Type | Description |
|-------|------|-------------|
| `item_type` | enum | One of: `bug`, `feature`, `human_action` |
| `title` | string | Descriptive title for the work item |
| `component` | string | System component this item relates to |
| `priority` | enum | One of: `P0`, `P1`, `P2`, `P3` |
| `description` | string | Detailed description of the issue or request |
| `repository_path` | string | Path to the feature management repository |

### Type-Specific Required Inputs

**Bugs (in metadata):**
- `severity`: critical, high, medium, low
- `steps_to_reproduce`: array of strings
- `expected_behavior`: string
- `actual_behavior`: string

**Features (in metadata):**
- `type`: enhancement, new_feature, improvement
- `estimated_effort`: small, medium, large, xl
- `business_value`: high, medium, low

**Human Actions (in metadata):**
- `urgency`: critical, high, medium, low
- `reason`: string explaining why human intervention is needed

### Optional Inputs

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `evidence` | array | [] | Supporting evidence (files, logs, links) |
| `auto_commit` | boolean | false | Commit item after creation |
| `branch_name` | string | null | Create item on specified branch |
| `tags` | array | auto-detected | Categorization tags |

## Output Contract

### Success Output

```
{
  "success": true,
  "item_id": "BUG-XXX | FEAT-XXX | ACTION-XXX",
  "location": "relative path to item directory",
  "absolute_path": "full filesystem path",
  "files_created": ["list of created files"],
  "summary_updated": true,
  "commit_hash": "abc123 (if auto_commit)",
  "duplicate_check": {
    "checked": true,
    "similar_items": [{"item_id", "title", "similarity"}],
    "is_potential_duplicate": false,
    "warning_message": "message if duplicates found"
  },
  "created_at": "ISO timestamp"
}
```

### Error Output

```
{
  "success": false,
  "error": "Error category",
  "message": "Human-readable error description",
  "details": {
    "field": "problematic field",
    "value": "invalid value",
    "expected": "what was expected"
  },
  "partial_completion": {
    "files_created": ["files created before error"],
    "summary_updated": false
  }
}
```

## Decision Rules

### ID Generation
- Always use max(existing_ids) + 1
- Never fill gaps in ID sequence
- Scan active, completed, and deprecated directories
- Start at 001 if no existing items

### Duplicate Detection
- Calculate similarity as max(title_similarity, description_similarity * 0.7)
- Default threshold: 0.75 (configurable)
- Duplicates are warnings, not blockers
- Always create the item, but flag potential duplicates

### Auto-Commit Usage
- Use `auto_commit: true` for standalone, atomic operations
- Use `auto_commit: false` when caller will batch multiple items
- Use `auto_commit: false` with `branch_name` for PR-based review

### Branch Workflow Triggers
- Use branches when creating 3+ items in batch
- Use branches for speculative/pattern-detected items
- Use branches when human review checkpoint is desired
- Skip branches for single high-confidence items

### Severity Assignment
- Critical: Security vulnerabilities, data loss, system-wide impact
- High: Core functionality broken, user-facing bugs
- Medium: Minor bugs, UX issues, most default cases
- Low: Cosmetic issues, typos, nice-to-haves

## Integration Pattern

### Receives From

| Agent | Context |
|-------|---------|
| Test Runner | Test failures that need bug tracking |
| Retrospective | Pattern-detected issues and improvements |
| Any Agent | Discovered issues during execution |
| User | Direct work item creation requests |

### Sends To

| Agent | Information |
|-------|-------------|
| Caller | Creation result, item ID, duplicate warnings |

### Coordination Protocol

1. Caller prepares structured input with all required fields
2. This pattern validates, generates ID, creates files
3. Returns structured result with success/failure and metadata
4. Caller handles result (e.g., includes in report, creates commit)

## Quality Criteria

### Creation Accuracy
- [ ] Generated ID is unique across entire repository
- [ ] All required metadata fields are populated
- [ ] Directory structure follows convention
- [ ] Instruction document is actionable

### Index Integrity
- [ ] Summary file contains entry for new item
- [ ] Statistics are updated correctly
- [ ] Recent activity reflects creation

### Duplicate Detection
- [ ] Similar items are identified and reported
- [ ] Similarity scores are reasonable
- [ ] No false negatives on obvious duplicates

### Error Handling
- [ ] Validation errors prevent file creation
- [ ] Partial failures are reported accurately
- [ ] No orphaned files on error

## Implementation Notes

### Atomicity Considerations
- Use temporary files and rename for atomic writes
- Validate before creating any files
- If summary update fails, item files still exist (log warning)

### Concurrency
- ID generation is not atomic across parallel invocations
- Callers should handle potential ID collisions with retry logic
- Branch-based workflow reduces collision risk

### Extensibility
- Metadata schemas should be versioned
- New item types can be added by extending type validation
- Custom instruction templates can be injected via configuration

### Performance
- Scanning large repositories may be slow
- Consider caching ID ranges for batch operations
- Duplicate detection scales linearly with existing items

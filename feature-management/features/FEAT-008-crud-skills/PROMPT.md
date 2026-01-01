# FEAT-008: Feature Management CRUD Skills

## Objective

Create Claude Code skills for creating, updating, and archiving items in feature-management directories. These skills encode best practices and ensure consistency when working with the featmgmt pattern.

## Skills to Implement

### 1. create-bug

**Purpose**: Create a new bug report with proper metadata and PROMPT.md file.

**Inputs**:
- `project_path`: Path to feature-management directory (required)
- `title`: Bug title (required)
- `description`: Detailed description (required)
- `component`: Affected component (required)
- `severity`: critical/high/medium/low (default: medium)
- `priority`: P0/P1/P2/P3 (default: P2)
- `tags`: List of tags (optional)
- `related_items`: List of related bug/feature IDs (optional)
- `acceptance_criteria`: List of acceptance criteria (optional)

**Behavior**:
1. Determine next available BUG-XXX ID by scanning bugs/ and completed/ directories
2. Generate slug from title (lowercase, hyphenated, max 50 chars)
3. Create directory: `bugs/BUG-XXX-slug/`
4. Create `bug_report.json` with full metadata
5. Create `PROMPT.md` with implementation instructions template
6. Update `bugs/bugs.md` summary table
7. Return created bug ID and path

**Template for PROMPT.md**:
```markdown
# BUG-XXX: {title}

## Problem Statement
{description}

## Acceptance Criteria
{acceptance_criteria as checklist}

## Investigation Steps
- [ ] Identify root cause
- [ ] Document affected files
- [ ] Propose fix approach

## Implementation
- [ ] Implement fix
- [ ] Add/update tests
- [ ] Update documentation if needed

## Verification
- [ ] All tests pass
- [ ] Manual verification complete
- [ ] No regressions introduced
```

### 2. create-feature

**Purpose**: Create a new feature request with proper metadata and PROMPT.md file.

**Inputs**:
- `project_path`: Path to feature-management directory (required)
- `title`: Feature title (required)
- `description`: Detailed description (required)
- `component`: Target component (required)
- `priority`: P0/P1/P2/P3 (default: P2)
- `tags`: List of tags (optional)
- `dependencies`: List of blocking feature/bug IDs (optional)
- `estimated_effort`: small/medium/large (optional)
- `business_value`: high/medium/low (optional)
- `technical_complexity`: high/medium/low (optional)

**Behavior**:
1. Determine next available FEAT-XXX ID
2. Generate slug from title
3. Create directory: `features/FEAT-XXX-slug/`
4. Create `feature_request.json` with full metadata
5. Create `PROMPT.md` with implementation instructions template
6. Update `features/features.md` summary table
7. Return created feature ID and path

### 3. create-action

**Purpose**: Create a new human action item requiring manual intervention.

**Inputs**:
- `project_path`: Path to feature-management directory (required)
- `title`: Action title (required)
- `description`: What needs to be done (required)
- `component`: Related component (required)
- `priority`: P0/P1/P2/P3 (default: P1)
- `related_bug`: Related bug ID (optional)
- `related_feature`: Related feature ID (optional)
- `blocking_items`: List of items this action blocks (optional)
- `test_steps`: List of verification steps (optional)
- `acceptance_criteria`: List of acceptance criteria (optional)

**Behavior**:
1. Determine next available ACTION-XXX ID
2. Generate slug from title
3. Create directory: `human-actions/ACTION-XXX-slug/`
4. Create `action_report.json` with full metadata
5. Create `INSTRUCTIONS.md` with manual steps
6. Return created action ID and path

### 4. update-status

**Purpose**: Update the status of a bug, feature, or action.

**Inputs**:
- `project_path`: Path to feature-management directory (required)
- `item_id`: Bug/Feature/Action ID (e.g., BUG-001, FEAT-005) (required)
- `status`: new/in_progress/resolved/completed/deprecated (required)
- `resolution`: Resolution notes (required if status is resolved/completed)

**Behavior**:
1. Locate item by ID (search bugs/, features/, human-actions/, completed/)
2. Update status field in JSON metadata file
3. Set appropriate date fields (started_date, updated_date, resolved_date, completed_date)
4. If status is resolved/completed/deprecated, add resolution field
5. Update corresponding summary file (bugs.md, features.md)
6. Return updated item path and new status

**Status Transitions**:
- `new` -> `in_progress` (sets started_date)
- `in_progress` -> `resolved` (sets resolved_date, requires resolution)
- `in_progress` -> `deprecated` (sets updated_date, requires resolution)
- Any -> `new` (reset, clears dates)

### 5. archive-item

**Purpose**: Move a resolved/completed item to the completed/ directory.

**Inputs**:
- `project_path`: Path to feature-management directory (required)
- `item_id`: Bug/Feature/Action ID (required)
- `verify_status`: Whether to verify item is resolved/completed first (default: true)

**Behavior**:
1. Locate item by ID
2. If verify_status, ensure status is resolved/completed/deprecated
3. Move item directory to `completed/`
4. Update source summary file (remove entry)
5. Update completed summary (add entry) if one exists
6. Return new path

## Implementation Location

Skills should be created in:
```
featmgmt/
└── .claude/
    └── skills/
        ├── create-bug/
        │   └── SKILL.md
        ├── create-feature/
        │   └── SKILL.md
        ├── create-action/
        │   └── SKILL.md
        ├── update-status/
        │   └── SKILL.md
        └── archive-item/
            └── SKILL.md
```

## Skill Definition Format

Each skill should follow the Claude Code skill format with:
- Clear description of purpose
- Input parameters with types and defaults
- Step-by-step instructions for Claude to follow
- Error handling guidance
- Example invocations

## Acceptance Criteria

- [ ] create-bug skill creates valid bug with all required files
- [ ] create-feature skill creates valid feature with all required files
- [ ] create-action skill creates valid action with all required files
- [ ] update-status skill correctly transitions status and updates dates
- [ ] archive-item skill moves items to completed/ directory
- [ ] All skills update summary files correctly
- [ ] All skills handle edge cases (missing directories, duplicate IDs)
- [ ] Skills work on any feature-management directory path
- [ ] Skills encode best practices from work-item-creation-agent

## Testing

Test each skill with:
1. Happy path - create/update/archive items successfully
2. Edge cases - missing parent directory, invalid status transition
3. Idempotency - running same operation twice doesn't break things
4. Summary file updates - entries added/removed correctly

## Dependencies

None - this is a foundational feature.

## Notes

- Skills should leverage patterns from existing `work-item-creation-agent` where applicable
- ID generation must scan both active and completed directories to avoid collisions
- Slug generation should be consistent: lowercase, hyphens, no special chars, max 50 chars

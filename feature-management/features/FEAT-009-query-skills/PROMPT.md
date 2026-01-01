# FEAT-009: Feature Management Query Skills

## Objective

Create Claude Code skills for listing and retrieving items from feature-management directories. These skills provide read/query capabilities that complement the CRUD skills in FEAT-008.

## Skills to Implement

### 1. list-items

**Purpose**: List bugs, features, and/or actions with optional filtering.

**Inputs**:
- `project_path`: Path to feature-management directory (required)
- `item_types`: List of types to include: bugs/features/actions (default: all)
- `status`: Filter by status: new/in_progress/resolved/completed/deprecated/all (default: all active)
- `priority`: Filter by priority: P0/P1/P2/P3/all (default: all)
- `component`: Filter by component (optional)
- `tags`: Filter by tags - items must have at least one matching tag (optional)
- `include_completed`: Include items in completed/ directory (default: false)
- `sort_by`: Sort field: priority/created_date/updated_date/id (default: priority)
- `limit`: Maximum items to return (default: 50)

**Behavior**:
1. Scan specified directories (bugs/, features/, human-actions/)
2. If include_completed, also scan completed/
3. Read JSON metadata for each item
4. Apply filters (status, priority, component, tags)
5. Sort results by specified field
6. Return formatted list with key fields

**Output Format**:
```
Found 12 items matching criteria:

BUGS (5):
| ID      | Title                          | Priority | Status      | Component   |
|---------|--------------------------------|----------|-------------|-------------|
| BUG-003 | Database connection timeout    | P0       | new         | backend/db  |
| BUG-007 | Login fails on mobile          | P1       | in_progress | frontend    |
...

FEATURES (4):
| ID       | Title                          | Priority | Status | Component   |
|----------|--------------------------------|----------|--------|-------------|
| FEAT-012 | Add dark mode support          | P1       | new    | frontend/ui |
...

HUMAN ACTIONS (3):
| ID         | Title                        | Priority | Status  | Blocks      |
|------------|------------------------------|----------|---------|-------------|
| ACTION-005 | Get prod database creds      | P0       | pending | BUG-003     |
...
```

**Summary Statistics**:
Also output summary stats:
- Total by type (bugs, features, actions)
- Total by status (new, in_progress, resolved)
- Total by priority (P0, P1, P2, P3)

### 2. get-item

**Purpose**: Retrieve full details of a specific item.

**Inputs**:
- `project_path`: Path to feature-management directory (required)
- `item_id`: Bug/Feature/Action ID (e.g., BUG-001, FEAT-005) (required)
- `include_content`: Include PROMPT.md/INSTRUCTIONS.md content (default: true)
- `include_plan`: Include PLAN.md if exists (default: false)
- `include_tasks`: Include TASKS.md if exists (default: false)

**Behavior**:
1. Locate item by ID (search bugs/, features/, human-actions/, completed/)
2. Read JSON metadata file
3. Optionally read PROMPT.md/INSTRUCTIONS.md content
4. Optionally read PLAN.md and TASKS.md
5. Return formatted output with all requested information

**Output Format**:
```
=== BUG-003: Database connection timeout ===

METADATA:
  ID:          BUG-003
  Status:      in_progress
  Priority:    P0
  Severity:    critical
  Component:   backend/db
  Created:     2025-12-01
  Started:     2025-12-02
  Assigned:    null
  Tags:        database, performance, critical

DESCRIPTION:
  Database connections are timing out under load, causing 500 errors
  for approximately 15% of requests during peak hours.

ACCEPTANCE CRITERIA:
  - [ ] Connection pool properly sized
  - [ ] Timeout errors eliminated under normal load
  - [ ] Monitoring added for connection pool metrics

RELATED ITEMS:
  - Blocked by: ACTION-005 (Get prod database creds)
  - Related: FEAT-010 (Database optimization)

LOCATION: bugs/BUG-003-database-timeout/

--- PROMPT.md ---
[Content of PROMPT.md if include_content=true]
```

## Implementation Location

Skills should be created in:
```
featmgmt/
└── .claude/
    └── skills/
        ├── list-items/
        │   └── SKILL.md
        └── get-item/
            └── SKILL.md
```

## Skill Definition Format

Each skill should follow the Claude Code skill format with:
- Clear description of purpose
- Input parameters with types and defaults
- Step-by-step instructions for Claude to follow
- Output format specification
- Example invocations

## Acceptance Criteria

- [ ] list-items skill returns formatted list of items
- [ ] list-items skill correctly filters by status, priority, component, tags
- [ ] list-items skill supports sorting by different fields
- [ ] list-items skill includes summary statistics
- [ ] get-item skill retrieves full item details
- [ ] get-item skill finds items in both active and completed directories
- [ ] get-item skill optionally includes PROMPT.md, PLAN.md, TASKS.md content
- [ ] Both skills handle missing directories gracefully
- [ ] Both skills work on any feature-management directory path

## Testing

Test each skill with:
1. Happy path - list/get items with various filters
2. Empty results - no items match criteria
3. Edge cases - item in completed/, missing optional files
4. Various filter combinations
5. Different sort orders

## Dependencies

- None (can be implemented independently of FEAT-008)

## Notes

- Priority sort order should be: P0 > P1 > P2 > P3
- Status "all active" means: new, in_progress (excludes resolved, completed, deprecated)
- Item location search order: bugs/ -> features/ -> human-actions/ -> completed/
- For completed items, preserve the original type prefix (BUG-, FEAT-, ACTION-)

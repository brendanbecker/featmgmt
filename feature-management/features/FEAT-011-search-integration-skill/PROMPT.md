# FEAT-011: Search Integration Skill

## Objective

Create Claude Code skills that leverage the semantic search MCP server (FEAT-010) to provide search-items and duplicate-check capabilities. These skills provide a user-friendly interface and encode best practices for semantic search workflows.

## Skills to Implement

### 1. search-items

**Purpose**: Semantic search across bugs, features, and actions using natural language queries.

**Inputs**:
- `project_path`: Path to feature-management directory (required)
- `query`: Natural language search query (required)
- `item_types`: Filter by types: bugs/features/actions/all (default: all)
- `include_completed`: Search archived items too (default: false)
- `limit`: Max results (default: 10)

**Behavior**:
1. Call MCP tool `mcp__featmgmt-semantic__search` with parameters
2. Format results for user readability
3. If index is stale, note that re-indexing occurred
4. Provide context about what was searched

**Example Invocation**:
```
User: "Find bugs related to database performance"

search-items:
  project_path: /path/to/feature-management
  query: database performance issues
  item_types: bugs
```

**Example Output**:
```
## Search Results for "database performance issues"

Found 3 matching bugs (searched 45 indexed items):

### 1. BUG-003: Database connection timeout (89% match)
   Priority: P0 | Status: new | Component: backend/db
   "Database connections are timing out under load..."
   Path: bugs/BUG-003-database-timeout/

### 2. BUG-007: Slow query on user lookup (76% match)
   Priority: P2 | Status: resolved | Component: backend/db
   "User lookup query takes >2s on large datasets..."
   Path: completed/BUG-007-slow-user-lookup/

### 3. BUG-012: Connection pool exhaustion (71% match)
   Priority: P1 | Status: in_progress | Component: backend/db
   "Under sustained load, connection pool depletes..."
   Path: bugs/BUG-012-connection-pool/

---
Index status: Fresh (last indexed 5 minutes ago)
Tip: Use `get-item BUG-003` for full details
```

**Best Practices to Encode**:
- Suggest using `get-item` for details on promising results
- Note when results are from completed/ (may have relevant solutions)
- Highlight high-similarity matches (>80%) as strong candidates
- Recommend reviewing similar items before creating new ones

### 2. duplicate-check

**Purpose**: Check if a proposed bug/feature might already exist before creating it.

**Inputs**:
- `project_path`: Path to feature-management directory (required)
- `title`: Proposed item title (required)
- `description`: Proposed item description (required)
- `item_type`: Type being created: bug/feature/action (optional)

**Behavior**:
1. Call MCP tool `mcp__featmgmt-semantic__check_duplicates`
2. Analyze results and provide clear recommendation
3. If duplicates found, suggest next steps
4. If no duplicates, confirm safe to proceed

**Example Invocation**:
```
User: "I want to create a bug about database timeouts"

duplicate-check:
  project_path: /path/to/feature-management
  title: Database queries timing out
  description: API requests are failing with timeout errors when querying the user table
  item_type: bug
```

**Example Output - Duplicates Found**:
```
## Duplicate Check Results

⚠️ LIKELY DUPLICATE FOUND

Your proposed bug:
  Title: "Database queries timing out"

Matches existing item:
  BUG-003: Database connection timeout (82% similar)
  Status: new | Priority: P0
  "Database connections are timing out under load..."

### Recommendation
Before creating a new bug, please review BUG-003:
  `get-item BUG-003`

Options:
1. If same issue: Add details to existing BUG-003 instead
2. If different root cause: Proceed with new bug, reference BUG-003
3. If related but distinct: Create new bug with `related_items: ["BUG-003"]`

---
Also possibly related:
- FEAT-015: Database connection pooling improvements (68% similar)
```

**Example Output - No Duplicates**:
```
## Duplicate Check Results

✅ NO DUPLICATES FOUND

Your proposed bug:
  Title: "Email notification not sending"

No existing items match above 60% similarity threshold.

### Recommendation
Safe to proceed with creating this bug:
  `create-bug --title "Email notification not sending" ...`

---
Closest matches (low similarity):
- BUG-009: SMS notifications delayed (42% similar) - different system
```

**Best Practices to Encode**:
- Always run duplicate-check before create-bug/create-feature
- Threshold interpretation:
  - ≥75%: LIKELY_DUPLICATE - review before creating
  - 60-74%: POSSIBLY_RELATED - consider referencing
  - <60%: Safe to create
- Suggest adding `related_items` when creating similar-but-distinct items
- Recommend updating existing items rather than creating duplicates

### 3. find-similar

**Purpose**: Find items similar to an existing item (for context gathering).

**Inputs**:
- `project_path`: Path to feature-management directory (required)
- `item_id`: Existing item ID (required)
- `limit`: Max results (default: 5)

**Behavior**:
1. Call MCP tool `mcp__featmgmt-semantic__get_similar`
2. Format results showing relationships
3. Highlight resolved items that may have relevant solutions

**Example Output**:
```
## Items Similar to BUG-003

BUG-003: Database connection timeout
  "Database connections are timing out under load..."

### Similar Items (5 found):

1. BUG-007: Connection pool exhaustion (85% similar)
   Status: resolved ✓ | May have relevant fix

2. FEAT-015: Implement connection pooling (78% similar)
   Status: completed ✓ | Related improvement

3. BUG-012: Timeout on batch operations (72% similar)
   Status: new | May share root cause

4. BUG-002: API latency spikes (65% similar)
   Status: resolved ✓ | Different symptom, same area

5. FEAT-008: Database monitoring (61% similar)
   Status: in_progress | Could help diagnose

---
Tip: Review resolved items for potential solutions
```

## Implementation Location

```
featmgmt/
└── .claude/
    └── skills/
        ├── search-items/
        │   └── SKILL.md
        ├── duplicate-check/
        │   └── SKILL.md
        └── find-similar/
            └── SKILL.md
```

## Skill Definition Format

Each skill should:
1. Describe when to use the skill
2. List required MCP server dependency
3. Provide parameter documentation
4. Include step-by-step instructions for Claude
5. Show example output format
6. Encode best practices as guidelines

## Integration with CRUD Skills (FEAT-008)

The duplicate-check skill should be referenced by create-bug and create-feature skills:

```markdown
# In create-bug SKILL.md:

## Pre-Creation Check
Before creating a bug, ALWAYS run duplicate-check first:
1. Invoke duplicate-check skill with proposed title and description
2. If LIKELY_DUPLICATE found, ask user how to proceed
3. If POSSIBLY_RELATED found, suggest adding related_items
4. Only proceed with creation if user confirms
```

## Acceptance Criteria

- [ ] search-items skill calls MCP search tool and formats results
- [ ] duplicate-check skill provides clear duplicate/no-duplicate guidance
- [ ] find-similar skill shows related items for context
- [ ] All skills handle MCP server not running gracefully
- [ ] All skills handle empty results gracefully
- [ ] Skills encode best practices in their instructions
- [ ] create-bug/create-feature skills reference duplicate-check

## Testing

1. **Search tests**: Various queries, filters, empty results
2. **Duplicate tests**: Exact match, similar match, no match
3. **Integration tests**: Full workflow with MCP server
4. **Error handling**: MCP server unavailable, index missing

## Dependencies

- **FEAT-010**: Semantic Search MCP Server (required)
- **FEAT-008**: CRUD Skills (for integration recommendations)

## Error Handling

**MCP Server Not Running**:
```
⚠️ Semantic search unavailable

The featmgmt-semantic MCP server is not running.
To enable semantic search:
1. Ensure MCP server is configured in ~/.claude/mcp.json
2. Restart Claude Code session

Falling back to text-based search...
[Provide grep-based alternative]
```

**Index Not Found**:
```
ℹ️ Creating search index for this project...
This may take a moment for large projects.
[Index created, proceed with search]
```

## Notes

- Skills should gracefully degrade if MCP server unavailable
- Consider providing text-based fallback using grep
- Duplicate-check is most valuable during item creation workflow
- find-similar helps with context gathering during implementation

# Scan & Prioritize Pattern

## Purpose

Scans a feature management repository to identify all unresolved work items, builds a priority-ordered queue, detects blocking relationships, and produces a structured work plan. This pattern provides the foundation for automated work processing by answering "what should we work on next?"

## Problem Statement

Without systematic scanning and prioritization:

- **Unclear priorities**: No single source of truth for what to work on next
- **Hidden blockers**: Human actions blocking work aren't visible
- **Stale data**: Work item status becomes inconsistent
- **Manual triage**: Each session requires manual review
- **Priority violations**: Low-priority items processed before critical ones
- **Circular blocks**: Dependency cycles aren't detected

This pattern solves these problems by providing automated, consistent scanning with blocking detection and structured priority output.

## Responsibilities

### Repository Scanning
- Synchronize with latest repository state
- Parse summary index files for bugs and features
- Extract metadata for all work items
- Identify items by status (new, in-progress, resolved, closed)

### Human Action Analysis
- Scan human action items
- Identify blocking relationships
- Calculate effective urgency based on blocked items
- Detect problematic patterns (missing items, circular blocks)

### Priority Queue Building
- Sort items by priority level (P0 > P1 > P2 > P3)
- Within priority, sort bugs before features
- Within type, sort by ID (older first)
- Mark items as "ready" or "blocked"

### Output Generation
- Produce human-readable priority report
- Generate machine-readable data structure
- Provide actionable recommendations
- Flag issues and warnings

## Workflow

### 1. Synchronize Repository

Ensure working with latest state:
- Pull latest changes from remote
- Verify repository integrity
- Note any sync issues

### 2. Read Summary Files

Parse the index files:
- Read bugs summary for all bug metadata
- Read features summary for all feature metadata
- Extract: ID, title, component, severity, status, priority, location

### 3. Scan Human Actions

If human actions directory exists:
- Read actions summary file
- For each pending action:
  - Extract metadata (ID, title, urgency, status)
  - Extract blocking_items list
- Build mapping of action → blocked items

### 4. Analyze Blocking Relationships

For each action with blocking items:
- Look up priority of each blocked item
- Calculate effective urgency:
  - Blocks P0 → critical urgency
  - Blocks P1 → high urgency
  - Blocks P2 → medium urgency
  - Blocks P3 → low urgency
- Store effective urgency and blocking details

For each work item:
- Check if any action blocks this item
- Mark as "blocked" or "ready"
- Record blocking action ID if blocked

### 5. Handle Edge Cases

**Non-existent Blocked Items:**
- Log warning about missing item
- Continue processing other items
- Include warning in output notes

**Circular Dependencies:**
- Detect when item X blocks action that blocks item X
- Log error about circular dependency
- Mark both as blocked
- Require manual resolution

**Completed But Not Archived:**
- Identify completed actions still in active directory
- Log info about improper archiving
- Exclude from blocking analysis

### 6. Filter Unresolved Items

Include items where:
- Status is "new" OR "in-progress"

Exclude items where:
- Status is "resolved" OR "closed"
- Item is in completed or deprecated directory

### 7. Build Priority Queue

Apply sorting algorithm:
1. Group by priority level
2. Within each level, separate bugs from features
3. Bugs come before features at same priority
4. Within type, sort by ID ascending (older first)
5. Attach blocking status to each item

### 8. Generate Human Actions Required List

Filter and sort actions that need attention:
- Status is "pending"
- Has non-empty blocking_items
- Effective urgency is "critical" or "high"
- Sort by effective urgency (critical first)

### 9. Generate Output

Produce structured report with:
- Scan metadata (timestamp, counts)
- Human actions requiring attention (if any)
- Priority queue organized by level
- Next action recommendation
- Warnings and notes
- JSON data for programmatic consumption

## Input Contract

### Required Inputs

| Field | Type | Description |
|-------|------|-------------|
| `repository_path` | string | Path to feature management repository |

### Optional Inputs

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sync_remote` | boolean | true | Pull latest before scanning |
| `include_blocked` | boolean | true | Include blocked items in queue |
| `max_items` | number | unlimited | Maximum items to return |

## Output Contract

### Success Output

```
{
  "success": true,
  "scan_date": "ISO timestamp",
  "priority_queue": [
    {
      "item_id": "BUG-001",
      "type": "bug",
      "priority": "P0",
      "title": "Critical security issue",
      "component": "auth",
      "status": "ready | blocked",
      "blocked_by": "ACTION-001 (if blocked)",
      "location": "bugs/BUG-001-slug/"
    }
  ],
  "human_actions_required": [
    {
      "action_id": "ACTION-001",
      "title": "Configure production database",
      "urgency": "critical",
      "reason": "Blocks BUG-001 (P0), FEAT-002 (P1)",
      "blocking_items": ["BUG-001", "FEAT-002"],
      "location": "human-actions/ACTION-001-slug/"
    }
  ],
  "summary": {
    "total_bugs": number,
    "total_features": number,
    "total_unresolved": number,
    "total_human_actions": number,
    "blocking_actions": number,
    "blocked_items": number,
    "ready_items": number,
    "by_priority": {"P0": n, "P1": n, "P2": n, "P3": n}
  },
  "recommendations": ["list of actionable recommendations"],
  "warnings": ["any issues detected during scan"],
  "next_action": {
    "item_id": "BUG-001 | ACTION-001",
    "type": "bug | feature | human_action",
    "title": "string",
    "recommendation": "Process this item first | Complete this action first"
  }
}
```

### Empty Queue Output

```
{
  "success": true,
  "scan_date": "ISO timestamp",
  "priority_queue": [],
  "human_actions_required": [],
  "summary": {
    "total_unresolved": 0,
    ...
  },
  "recommendations": ["All work items resolved. No processing needed."],
  "next_action": null
}
```

## Decision Rules

### Priority Order
- P0 always comes before P1, P2, P3
- Within same priority: bugs before features
- Within same priority and type: lower ID (older) first

### Blocking Determination
- Item is "blocked" if ANY action lists it in blocking_items
- Item is "ready" if no actions block it
- Blocked items remain in queue but marked as blocked

### Effective Urgency Calculation
| Highest Blocked Priority | Effective Urgency |
|--------------------------|-------------------|
| P0 | critical |
| P1 | high |
| P2 | medium |
| P3 | low |
| None (empty blocking_items) | original urgency |

### Next Action Selection
1. If human actions required with critical/high urgency → recommend action first
2. Otherwise → recommend first ready item in queue
3. If all items blocked → recommend completing blocking actions

### Status Mapping
| Summary Status | Included in Queue |
|----------------|-------------------|
| new | Yes |
| in-progress | Yes |
| resolved | No |
| closed | No |
| deprecated | No |

## Integration Pattern

### Receives From

| Agent | Information |
|-------|-------------|
| Orchestrator | Request to scan and prioritize |
| User | Manual scan request |
| Retrospective | Updated backlog after reprioritization |

### Sends To

| Agent | Information |
|-------|-------------|
| Bug Processor | Next item to process |
| Summary Reporter | Queue statistics |
| Orchestrator | Priority queue and recommendations |

### Coordination Protocol

1. Invoked at start of work session
2. Produces prioritized queue
3. Orchestrator uses queue to dispatch work
4. Re-invoked after retrospective for updated queue

## Quality Criteria

### Scan Accuracy
- [ ] All unresolved items included
- [ ] No resolved items incorrectly included
- [ ] Metadata correctly extracted
- [ ] Paths verified to exist

### Priority Correctness
- [ ] P0 items always before P1, etc.
- [ ] Bugs before features at same priority
- [ ] Older items before newer at same priority/type
- [ ] Blocking status correctly determined

### Blocking Analysis
- [ ] All blocking relationships identified
- [ ] Effective urgency correctly calculated
- [ ] Edge cases handled (missing items, cycles)
- [ ] Warnings generated for issues

### Output Quality
- [ ] Human-readable report is clear
- [ ] JSON structure is valid and complete
- [ ] Recommendations are actionable
- [ ] Next action is correct

## Implementation Notes

### Parsing Robustness
- Handle malformed summary files gracefully
- Report parsing errors but continue scanning
- Validate metadata against expected types

### Performance
- For large repositories, consider streaming/pagination
- Cache repeated file reads
- Summary files should be primary source, not individual item files

### Extensibility
- Support for custom priority levels
- Configurable sort order
- Custom blocking relationship types

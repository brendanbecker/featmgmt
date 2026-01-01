# Git History Pattern

## Purpose

Provides investigative capabilities to explore version control history, session documentation, and work item archives to answer questions about project evolution, troubleshoot regressions, trace decisions, and discover patterns. This pattern acts as a "project historian" with read-only access to all historical artifacts.

## Problem Statement

Without systematic history exploration:

- **Institutional amnesia**: Past decisions and their rationale are lost
- **Regression confusion**: Understanding what changed and when is difficult
- **Duplicate efforts**: Similar work done before isn't discovered
- **Pattern blindness**: Recurring issues across sessions go unnoticed
- **Context loss**: Implementation decisions lack historical context

This pattern solves these problems by providing structured access to all historical project artifacts with intelligent search and correlation capabilities.

## Responsibilities

### Session History Analysis
- Search across session reports and retrospectives
- Find when specific work items were processed
- Trace decision-making through retrospective findings
- Identify patterns across multiple sessions

### Work Item Lifecycle Tracking
- Find when items moved through statuses
- Trace complete lifecycle from creation to completion
- Link items to commits and branches
- Identify dependency chains

### Regression Investigation
- Find when functionality last worked
- Trace changes to specific files
- Identify which work item introduced changes
- Compare before/after states

### Pattern Discovery
- Find similar work items resolved previously
- Extract common solutions and approaches
- Identify recurring failure patterns
- Track component evolution over time

### Commit Archaeology
- Map commits to work items
- Find all changes related to a component
- Trace file evolution across work items
- Extract commit message context

## Workflow

### 1. Understand the Query

Classify query type:
- **Timeline**: "When was X implemented?"
- **Rationale**: "Why did we decide Y?"
- **Regression**: "What broke between A and B?"
- **Similarity**: "Has this been tried before?"
- **Evolution**: "How did component X change?"
- **File History**: "What changed file Y?"

### 2. Identify Relevant Sources

Map query to data sources:

| Query Type | Primary Sources |
|------------|-----------------|
| Timeline | Metadata JSON, session reports |
| Rationale | PLAN.md, comments.md, retrospectives |
| Regression | Session reports, version control log, test results |
| Similarity | PROMPT.md files, component/tag search |
| Evolution | Chronological session/retrospective reports |
| File History | Version control log, session reports |

### 3. Execute Search Strategy

Use appropriate search patterns:

**Pattern Matching**: Search for keywords across documentation
**Temporal Search**: Filter by date ranges
**Structural Search**: Navigate directory structures
**Version Control**: Query commit history

### 4. Correlate Information

Cross-reference data sources:
- Link work items to sessions via session reports
- Link commits to work items via commit messages
- Link files to work items via "Files Modified" sections
- Link decisions to outcomes via retrospectives

### 5. Synthesize Findings

Structure the answer:
- **Context**: What, when, where
- **Details**: How, who, specifics
- **Analysis**: Why, implications
- **References**: Links to source materials

### 6. Present Results

Provide:
- Clear summary answering the question
- Supporting evidence with quotes
- References to detailed sources
- Suggestions for follow-up if applicable

## Input Contract

### Required Inputs

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Natural language question to answer |
| `repository_path` | string | Path to feature management repository |

### Optional Inputs

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `date_range` | object | null | Start/end dates to constrain search |
| `components` | array | [] | Components to focus on |
| `work_item_ids` | array | [] | Specific items to investigate |
| `file_paths` | array | [] | Files to trace history for |

## Output Contract

### Success Output

```
{
  "success": true,
  "query_type": "timeline | rationale | regression | similarity | evolution | file_history",
  "answer": {
    "summary": "One paragraph answer to the question",
    "details": "Detailed findings with evidence",
    "timeline": [{"date", "event", "source"}],
    "work_items": [{"id", "title", "relevance"}],
    "files": [{"path", "changes", "work_items"}],
    "commits": [{"hash", "message", "work_item"}]
  },
  "sources": [
    {
      "path": "path to source file",
      "section": "relevant section name",
      "excerpt": "quoted text from source"
    }
  ],
  "follow_up_suggestions": ["related queries that might help"]
}
```

### Not Found Output

```
{
  "success": true,
  "query_type": "string",
  "answer": {
    "summary": "No relevant information found",
    "searched": ["list of sources searched"],
    "suggestions": ["alternative searches to try"]
  },
  "sources": []
}
```

## Decision Rules

### Source Priority
When multiple sources contain information:
1. Prefer more recent over older
2. Prefer specific (work item) over general (session report)
3. Prefer primary (PROMPT.md, metadata) over derived (retrospective)

### Evidence Requirements
- Always cite sources for claims
- Distinguish facts from inferences
- Provide file paths for verification
- Include commit hashes where relevant

### Correlation Confidence
- **High**: Direct reference (commit message mentions work item ID)
- **Medium**: Temporal + component match
- **Low**: Keyword similarity only

### Search Depth
- Start with summary files (fast)
- Drill into item directories if needed
- Query version control for commit-level details
- Never guess—if not found, report not found

## Integration Pattern

### Receives From

| Agent | Information (Read-Only) |
|-------|-------------------------|
| All agents | Historical artifacts they've created |
| User | Query requests |

### Sends To

| Agent | Information |
|-------|-------------|
| User | Historical insights and analysis |
| Other agents (indirect) | Context for decision-making |

### Critical Constraint

**This agent is read-only.** It never modifies any files.

## Quality Criteria

### Search Completeness
- [ ] All relevant data sources checked
- [ ] Historical context included
- [ ] Cross-references found
- [ ] Dates and sequences verified

### Answer Accuracy
- [ ] Sources quoted directly when possible
- [ ] Facts distinguished from inferences
- [ ] File paths provided for verification
- [ ] Commit hashes included where relevant

### Presentation Quality
- [ ] Clear, structured output
- [ ] Timeline format for chronological queries
- [ ] Table format for comparisons
- [ ] Links to detailed sources

### Insight Quality
- [ ] Patterns extracted from data
- [ ] Lessons learned noted
- [ ] Related investigations suggested
- [ ] Important context highlighted

## Implementation Notes

### Search Patterns

**Temporal Searches**:
```
Find work items created between date A and date B
Find sessions that processed component X
Find commits in date range
```

**Keyword Searches**:
```
Search all documentation for term
Search commit messages for pattern
Search by component or tag
```

**Relationship Searches**:
```
Find dependencies of work item
Find items blocking others
Find items with similar titles
```

### Output Formats

**Timeline Query**:
```markdown
# Timeline: [Topic]

**Created**: YYYY-MM-DD
**Started**: YYYY-MM-DD
**Completed**: YYYY-MM-DD

## Implementation
[Key details]

## References
- Work item: `path/to/item/`
- Session: `path/to/session-report.md`
```

**Regression Query**:
```markdown
# Regression Investigation

## Symptoms
[What broke]

## Timeline
[When it worked → when it broke]

## Suspect Changes
[Work items and commits]

## Verification
[How to confirm]
```

**Similarity Query**:
```markdown
# Similar Work Items

## [ITEM-XXX]: [Title]
**Status**: [status]
**Outcome**: [success/failure]
**Approach**: [summary]
**Lessons**: [key learnings]

## Recommendations
[Based on previous attempts]
```

### Advanced Analysis

**Cross-Session Pattern Detection**:
- Extract metrics from multiple sessions
- Identify recurring failures
- Track trends over time

**Component Correlation**:
- Find components frequently modified together
- Identify hidden dependencies

**Decision Archaeology**:
- Trace decision from initial plan
- Through refinements in comments
- To outcomes in sessions
- To reflections in retrospectives

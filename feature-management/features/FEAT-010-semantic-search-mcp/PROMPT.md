# FEAT-010: Semantic Search MCP Server

## Objective

Create a Python MCP server that provides semantic search capabilities for feature-management directories using ChromaDB with local ONNX embeddings. This server enables finding related items, detecting duplicates, and surfacing relevant context.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│     featmgmt-semantic MCP Server (Python)               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  MCP Tools:                                       │  │
│  │  - search(query, project_path, filters)          │  │
│  │  - index(project_path, force)                    │  │
│  │  - check_duplicates(title, description, path)    │  │
│  │  - get_similar(item_id, project_path, limit)     │  │
│  │  - get_index_status(project_path)                │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                               │
│  ┌──────────────────────┴───────────────────────────┐  │
│  │  ChromaDB Manager                                 │  │
│  │  - Per-project collections                        │  │
│  │  - Staleness tracking (file mtimes)              │  │
│  │  - On-demand re-indexing                         │  │
│  └──────────────────────┬───────────────────────────┘  │
│                         │                               │
│  ┌──────────────────────┴───────────────────────────┐  │
│  │  ChromaDB (local persistent)                      │  │
│  │  Storage: ~/.featmgmt/chromadb/{project_hash}/   │  │
│  │  Embeddings: ONNX (default-ef)                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## MCP Tools Specification

### 1. search

**Purpose**: Semantic search across indexed items.

**Parameters**:
- `query` (string, required): Natural language search query
- `project_path` (string, required): Path to feature-management directory
- `item_types` (array, optional): Filter by type ["bugs", "features", "actions"]
- `status` (array, optional): Filter by status ["new", "in_progress", "resolved"]
- `include_completed` (boolean, optional): Include archived items (default: false)
- `limit` (integer, optional): Max results (default: 10)
- `threshold` (float, optional): Minimum similarity score 0-1 (default: 0.5)

**Returns**:
```json
{
  "results": [
    {
      "item_id": "BUG-003",
      "title": "Database connection timeout",
      "description": "...",
      "similarity_score": 0.89,
      "item_type": "bug",
      "status": "new",
      "priority": "P0",
      "path": "bugs/BUG-003-database-timeout/"
    }
  ],
  "query": "database performance issues",
  "total_results": 3,
  "index_status": {
    "last_indexed": "2025-12-03T10:30:00Z",
    "is_stale": false,
    "items_indexed": 45
  }
}
```

**Behavior**:
1. Check index staleness (compare file mtimes to last index time)
2. If stale, trigger incremental re-index before searching
3. Generate embedding for query
4. Search ChromaDB collection with filters
5. Return ranked results with similarity scores

### 2. index

**Purpose**: Index or re-index a feature-management directory.

**Parameters**:
- `project_path` (string, required): Path to feature-management directory
- `force` (boolean, optional): Force full re-index even if not stale (default: false)

**Returns**:
```json
{
  "status": "completed",
  "project_path": "/path/to/feature-management",
  "items_indexed": 45,
  "items_updated": 3,
  "items_removed": 1,
  "duration_ms": 1250,
  "index_location": "~/.featmgmt/chromadb/abc123/"
}
```

**Behavior**:
1. Scan bugs/, features/, human-actions/, completed/ directories
2. For each item, read JSON metadata and PROMPT.md/INSTRUCTIONS.md
3. Generate combined text: title + description + prompt_content
4. Create/update embeddings in ChromaDB
5. Track file mtimes for staleness detection
6. Remove embeddings for deleted items

### 3. check_duplicates

**Purpose**: Check if a proposed item might be a duplicate of existing items.

**Parameters**:
- `title` (string, required): Proposed item title
- `description` (string, required): Proposed item description
- `project_path` (string, required): Path to feature-management directory
- `threshold` (float, optional): Similarity threshold (default: 0.75 from config)
- `item_type` (string, optional): Limit search to specific type

**Returns**:
```json
{
  "potential_duplicates": [
    {
      "item_id": "BUG-003",
      "title": "Database connection pool exhaustion",
      "similarity_score": 0.82,
      "status": "in_progress",
      "recommendation": "LIKELY_DUPLICATE"
    },
    {
      "item_id": "FEAT-015",
      "title": "Improve database connection handling",
      "similarity_score": 0.71,
      "status": "new",
      "recommendation": "POSSIBLY_RELATED"
    }
  ],
  "has_likely_duplicates": true,
  "threshold_used": 0.75
}
```

**Recommendations**:
- `LIKELY_DUPLICATE`: score >= threshold
- `POSSIBLY_RELATED`: score >= threshold - 0.15
- Not included if score < threshold - 0.15

### 4. get_similar

**Purpose**: Find items similar to an existing item.

**Parameters**:
- `item_id` (string, required): Existing item ID (e.g., BUG-003)
- `project_path` (string, required): Path to feature-management directory
- `limit` (integer, optional): Max results (default: 5)
- `include_completed` (boolean, optional): Include archived items (default: true)

**Returns**:
```json
{
  "source_item": {
    "item_id": "BUG-003",
    "title": "Database connection timeout"
  },
  "similar_items": [
    {
      "item_id": "BUG-007",
      "title": "Connection pool exhaustion under load",
      "similarity_score": 0.85,
      "status": "resolved",
      "relationship": "May share root cause"
    }
  ]
}
```

### 5. get_index_status

**Purpose**: Get current index status for a project.

**Parameters**:
- `project_path` (string, required): Path to feature-management directory

**Returns**:
```json
{
  "exists": true,
  "project_path": "/path/to/feature-management",
  "index_location": "~/.featmgmt/chromadb/abc123/",
  "last_indexed": "2025-12-03T10:30:00Z",
  "is_stale": true,
  "stale_files": ["bugs/BUG-008-new-bug/bug_report.json"],
  "items_indexed": 45,
  "index_size_bytes": 2048000
}
```

## Implementation Details

### Project Structure

```
featmgmt/
└── mcp-servers/
    └── featmgmt-semantic/
        ├── pyproject.toml
        ├── README.md
        ├── src/
        │   └── featmgmt_semantic/
        │       ├── __init__.py
        │       ├── server.py          # MCP server entry point
        │       ├── tools.py           # Tool implementations
        │       ├── chromadb_manager.py # ChromaDB wrapper
        │       ├── indexer.py         # Content indexing logic
        │       ├── staleness.py       # Staleness tracking
        │       └── config.py          # Configuration handling
        └── tests/
            ├── test_indexer.py
            ├── test_search.py
            └── test_duplicates.py
```

### Dependencies

```toml
[project]
dependencies = [
    "mcp>=1.0.0",
    "chromadb>=0.4.0",
    "onnxruntime>=1.16.0",  # For local embeddings
]
```

### ChromaDB Configuration

- **Storage**: `~/.featmgmt/chromadb/{project_hash}/`
  - Project hash = SHA256(absolute_path)[:12]
- **Collection name**: `featmgmt_items`
- **Embedding function**: ChromaDB default ONNX embedding
- **Metadata fields**: item_id, item_type, status, priority, path, mtime

### Content Indexing

**What to index per item**:
1. Title (from JSON metadata)
2. Description (from JSON metadata)
3. PROMPT.md or INSTRUCTIONS.md content

**Combined document format**:
```
TITLE: {title}

DESCRIPTION: {description}

IMPLEMENTATION:
{prompt_content}
```

### Staleness Detection

Track in `~/.featmgmt/chromadb/{project_hash}/index_metadata.json`:
```json
{
  "project_path": "/path/to/feature-management",
  "last_indexed": "2025-12-03T10:30:00Z",
  "file_mtimes": {
    "bugs/BUG-003-timeout/bug_report.json": 1701590000,
    "bugs/BUG-003-timeout/PROMPT.md": 1701590100
  }
}
```

**Staleness check**:
1. Scan all JSON and PROMPT.md files
2. Compare mtimes to stored values
3. If any file is newer or new files exist, mark as stale
4. If any indexed file is missing, mark for removal

### Configuration

Read from `{project_path}/.agent-config.json`:
```json
{
  "duplicate_similarity_threshold": 0.75
}
```

Fall back to defaults if not present.

## MCP Server Registration

Users add to Claude Code MCP config (`~/.claude/mcp.json` or project config):
```json
{
  "mcpServers": {
    "featmgmt-semantic": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/featmgmt/mcp-servers/featmgmt-semantic", "python", "-m", "featmgmt_semantic.server"]
    }
  }
}
```

## Acceptance Criteria

- [ ] MCP server starts and registers all 5 tools
- [ ] search tool returns semantically relevant results
- [ ] index tool creates/updates ChromaDB collection
- [ ] check_duplicates tool identifies potential duplicates above threshold
- [ ] get_similar tool finds related items
- [ ] get_index_status tool reports accurate staleness info
- [ ] On-demand re-indexing works when stale files detected
- [ ] Per-project collections are isolated
- [ ] Uses ONNX embeddings (no external API calls)
- [ ] Handles missing directories gracefully
- [ ] Configuration loaded from .agent-config.json

## Testing

1. **Unit tests**: Indexer, staleness detection, search ranking
2. **Integration tests**: Full MCP tool invocations
3. **Performance tests**: Index 100+ items, search latency

## Error Handling

- **Project not found**: Return helpful error with expected path
- **Index doesn't exist**: Auto-create on first search
- **ChromaDB errors**: Wrap with user-friendly messages
- **Corrupted index**: Provide "force re-index" guidance

## Notes

- ONNX model downloads on first use (~100MB)
- ChromaDB handles persistence automatically
- Consider adding index size limits for very large projects
- agent_runs/ intentionally excluded from indexing

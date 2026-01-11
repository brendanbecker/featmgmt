# FEAT-017: Migration Tool: featmgmt to Beads

**Priority**: P2
**Component**: tooling
**Type**: new_feature
**Estimated Effort**: medium
**Business Value**: Medium - Enables existing projects to adopt beads workflow

## Overview

Create a migration script that converts existing featmgmt feature-management directories into Beads. Parses PROMPT.md files, extracts implicit dependencies from WAVES.md if present, and generates `bd create` and `bd dep add` commands.

## Problem Statement

Projects already using featmgmt have features defined in `features/*/PROMPT.md` format. To use beads/gastown, these need to be converted to beads with proper dependencies. Currently there is no automated way to:

- Extract work items from featmgmt directories
- Preserve metadata (priority, component, effort, tags)
- Infer dependencies from WAVES.md ordering
- Generate the corresponding `bd` commands

Manual migration is tedious and error-prone, especially for projects with many features.

## Proposed Solution

Create `scripts/migrate-featmgmt-to-beads.sh` that:

1. Scans `features/*/PROMPT.md` and `bugs/*/PROMPT.md`
2. Extracts metadata from `feature_request.json` / `bug_report.json`
3. Parses WAVES.md (if present) to infer dependencies
4. Generates `bd create` commands with `--body` containing PROMPT.md content
5. Generates `bd dep add` commands for all dependencies
6. Supports `--dry-run` to preview without executing
7. Creates migration report

## Interface

```bash
./scripts/migrate-featmgmt-to-beads.sh \
    --source /path/to/feature-management \
    --epic "Project Migration" \
    --waves /path/to/WAVES.md \
    --dry-run
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--source` | Yes | - | Path to feature-management directory |
| `--epic` | No | "Migration" | Epic name for all migrated beads |
| `--waves` | No | `<source>/WAVES.md` | Path to WAVES.md for dependency inference |
| `--dry-run` | No | false | Preview commands without executing |
| `--output` | No | stdout | File to write migration commands |
| `--skip-completed` | No | false | Skip items in completed/ directory |
| `--include-bugs` | No | true | Include bug reports in migration |
| `--verbose` | No | false | Show detailed processing output |

## Key Capabilities

### 1. Directory Scanning

Scan featmgmt directory structure:
- `features/FEAT-XXX-slug/` directories
- `bugs/BUG-XXX-slug/` directories
- Optionally include `completed/` items

### 2. Metadata Extraction

Extract from JSON files:
- `feature_request.json`: feature_id, title, priority, component, tags, estimated_effort, dependencies
- `bug_report.json`: bug_id, title, priority, component, tags, severity

Map to bead attributes:
- Priority: P0-P3 -> priority label
- Component: -> component label
- Tags: -> labels
- Effort: small/medium/large/xl -> estimate

### 3. PROMPT.md Content Extraction

Extract the full PROMPT.md content for use as bead body. Handle:
- Markdown formatting preservation
- Large content (may need truncation or summary)
- Special characters escaping for shell commands

### 4. WAVES.md Dependency Parsing

If WAVES.md exists, parse wave structure to infer dependencies:

```markdown
## Wave 1: Foundation
- FEAT-001: Core data model
- FEAT-002: Basic API

## Wave 2: Core Features
- FEAT-003: User authentication (depends on FEAT-001)
- FEAT-004: Data import (depends on FEAT-001, FEAT-002)
```

Parsing logic:
- Items in Wave N depend on items in Wave N-1 (implicit)
- Explicit dependencies in parentheses override implicit
- Build dependency graph for `bd dep add` commands

### 5. Command Generation

Generate `bd create` commands:
```bash
bd create \
    --title "FEAT-001: Core data model" \
    --epic "Project Migration" \
    --labels "P1,backend,foundation" \
    --body "$(cat <<'EOF'
# FEAT-001: Core data model
...full PROMPT.md content...
EOF
)"
```

Generate `bd dep add` commands:
```bash
bd dep add FEAT-003 FEAT-001
bd dep add FEAT-004 FEAT-001
bd dep add FEAT-004 FEAT-002
```

### 6. Dry-Run Mode

With `--dry-run`:
- Print all commands that would be executed
- Show migration summary (counts, dependencies)
- Validate without side effects
- Allow review before execution

### 7. Migration Report

Generate report including:
- Total items scanned
- Items migrated vs skipped
- Dependencies created
- Warnings (missing files, parse errors)
- Commands executed or preview

## Implementation Tasks

### Section 1: Core Framework
- [ ] Create script skeleton with argument parsing
- [ ] Implement directory scanning logic
- [ ] Add validation for source directory structure
- [ ] Implement dry-run flag handling
- [ ] Add verbose output support

### Section 2: Metadata Extraction
- [ ] Parse feature_request.json files
- [ ] Parse bug_report.json files
- [ ] Map featmgmt fields to bead attributes
- [ ] Handle missing or malformed JSON gracefully
- [ ] Extract and preserve tags/labels

### Section 3: PROMPT.md Processing
- [ ] Read PROMPT.md content
- [ ] Handle special characters for shell escaping
- [ ] Implement content truncation if needed
- [ ] Preserve markdown formatting
- [ ] Handle missing PROMPT.md files

### Section 4: WAVES.md Parsing
- [ ] Parse wave headers (## Wave N: Name)
- [ ] Extract items per wave
- [ ] Parse explicit dependencies (depends on X, Y)
- [ ] Build implicit dependencies from wave ordering
- [ ] Construct dependency graph

### Section 5: Command Generation
- [ ] Generate `bd create` commands
- [ ] Generate `bd dep add` commands
- [ ] Handle command ordering (creates before deps)
- [ ] Add proper quoting and escaping
- [ ] Support output to file or stdout

### Section 6: Migration Report
- [ ] Track items processed
- [ ] Track dependencies created
- [ ] Collect warnings and errors
- [ ] Generate summary statistics
- [ ] Format report output

### Section 7: Testing
- [ ] Test with sample featmgmt directory
- [ ] Test WAVES.md parsing with various formats
- [ ] Test dry-run mode
- [ ] Test error handling (missing files, bad JSON)
- [ ] Test with real featmgmt project

## Acceptance Criteria

- [ ] Script parses features/ and bugs/ directories
- [ ] Metadata preserved (priority, component, tags)
- [ ] WAVES.md dependencies extracted correctly
- [ ] `--dry-run` shows commands without executing
- [ ] Migration report generated
- [ ] Handles edge cases (missing files, malformed JSON)
- [ ] Commands are properly quoted and escaped
- [ ] Script is idempotent (can run multiple times safely in dry-run)

## Dependencies

- FEAT-014 (must understand bead creation format)
- jq (for JSON processing)
- Beads (`bd` CLI) installed for actual execution

## Technical Considerations

### Shell Escaping

PROMPT.md content may contain:
- Single and double quotes
- Backticks
- Dollar signs
- Newlines

Use HEREDOC with quoted delimiter for safe embedding:
```bash
--body "$(cat <<'EOF'
...content...
EOF
)"
```

### Large Content Handling

If PROMPT.md is very large:
- Option 1: Truncate with "..." and link to original
- Option 2: Extract only Overview/Summary section
- Option 3: Reference file path instead of inline

### Dependency Conflicts

If explicit dependencies in JSON conflict with WAVES.md:
- JSON dependencies take precedence
- Log warning about conflict
- Allow `--prefer-waves` flag to override

### ID Mapping

Featmgmt uses FEAT-001, BUG-001 format. Beads may use different IDs.
- Track mapping: featmgmt_id -> bead_id
- Update dependencies to use new IDs
- Save mapping for reference

## Example Usage

### Basic Migration

```bash
# Preview migration
./scripts/migrate-featmgmt-to-beads.sh \
    --source /path/to/myproject/feature-management \
    --epic "MyProject Features" \
    --dry-run

# Execute migration
./scripts/migrate-featmgmt-to-beads.sh \
    --source /path/to/myproject/feature-management \
    --epic "MyProject Features"
```

### With WAVES.md

```bash
./scripts/migrate-featmgmt-to-beads.sh \
    --source /path/to/myproject/feature-management \
    --waves /path/to/myproject/WAVES.md \
    --epic "MyProject Q1" \
    --dry-run
```

### Output to File

```bash
./scripts/migrate-featmgmt-to-beads.sh \
    --source /path/to/feature-management \
    --output migration-commands.sh \
    --dry-run

# Review and execute
cat migration-commands.sh
bash migration-commands.sh
```

## Notes

- Consider adding `--filter` option to migrate specific items
- May want `--status` filter (only migrate 'new' items)
- Could add `--transform` hooks for custom field mapping
- Future: bidirectional sync (beads -> featmgmt)

---

*Created: 2026-01-11*
*Last Updated: 2026-01-11*

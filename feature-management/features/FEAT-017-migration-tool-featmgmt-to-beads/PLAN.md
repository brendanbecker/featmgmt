# Implementation Plan: FEAT-017

**Work Item**: [FEAT-017: Migration Tool: featmgmt to Beads](PROMPT.md)
**Component**: tooling
**Priority**: P2
**Created**: 2026-01-11

## Overview

Create a migration script that converts existing featmgmt feature-management directories into Beads. This enables projects already using featmgmt to adopt the beads workflow without manual recreation of work items.

## Architecture Decisions

### Core Architecture

- **Approach**: Bash script with jq for JSON processing
- **Output**: Shell commands (bd create, bd dep add)
- **Execution Model**: Generate-then-execute (dry-run by default)
- **Dependency Resolution**: Wave-based inference + explicit JSON dependencies

### Key Design Choices

1. **Bash Script over Python**
   - Rationale: Matches existing featmgmt scripts, minimal dependencies
   - Trade-off: Less elegant parsing, but sufficient for structured data
   - Mitigation: Use jq for JSON, awk/sed for WAVES.md parsing

2. **Generate Commands vs Direct API**
   - Rationale: Reviewable, debuggable, can be modified before execution
   - Trade-off: Two-step process (generate, then run)
   - Mitigation: Single execution mode available

3. **Wave-Based Dependency Inference**
   - Rationale: WAVES.md captures implicit ordering that JSON may miss
   - Trade-off: Assumes wave structure is authoritative
   - Mitigation: JSON dependencies override wave-inferred ones

4. **HEREDOC for Content Embedding**
   - Rationale: Handles multi-line content with special characters
   - Trade-off: Verbose command output
   - Mitigation: Proper quoting prevents shell interpretation issues

## Affected Components

| Component | Type of Change | Risk Level |
|-----------|----------------|------------|
| New: migrate-featmgmt-to-beads.sh | Primary implementation | Low |
| featmgmt scripts directory | Add new script | Low |
| Documentation | Add migration guide | Low |

## Technical Design

### Script Structure

```bash
scripts/migrate-featmgmt-to-beads.sh
  |-- parse_arguments()       # Handle CLI args
  |-- validate_source()       # Check source directory
  |-- scan_items()            # Find features and bugs
  |-- extract_metadata()      # Parse JSON files
  |-- read_prompt_content()   # Get PROMPT.md content
  |-- parse_waves()           # Parse WAVES.md if present
  |-- build_dependencies()    # Combine JSON + wave deps
  |-- generate_create_cmds()  # Output bd create commands
  |-- generate_dep_cmds()     # Output bd dep add commands
  |-- generate_report()       # Summary statistics
  |-- main()                  # Orchestrate workflow
```

### Data Flow

```
1. Scan directories
   |
   v
2. For each item:
   - Read JSON metadata
   - Read PROMPT.md content
   - Store in array/map
   |
   v
3. Parse WAVES.md (if present)
   - Extract wave structure
   - Build wave-based dependencies
   |
   v
4. Merge dependencies
   - JSON explicit deps (priority)
   - Wave-inferred deps (fallback)
   |
   v
5. Generate commands
   - bd create (ordered by dependency)
   - bd dep add (after creates)
   |
   v
6. Output
   - Dry-run: print commands
   - Execute: run commands
   - File: write to --output
```

### Field Mapping

| featmgmt Field | Bead Attribute | Transformation |
|----------------|----------------|----------------|
| feature_id / bug_id | title prefix | "FEAT-001: Title" |
| title | title | Direct |
| priority | label | "P0", "P1", etc. |
| component | label | Direct |
| tags | labels | Join with comma |
| estimated_effort | (custom) | Map to estimate if supported |
| description | body (partial) | Combined with PROMPT.md |
| dependencies | deps | Via bd dep add |

### WAVES.md Parser

Expected format:
```markdown
## Wave 1: Foundation
- FEAT-001: Core model
- FEAT-002: Basic API

## Wave 2: Features
- FEAT-003: Auth (depends on FEAT-001)
```

Parsing rules:
1. `## Wave N:` starts a new wave
2. `- FEAT-XXX:` or `- BUG-XXX:` identifies items
3. `(depends on X, Y)` extracts explicit dependencies
4. Implicit: items in Wave N depend on all Wave N-1 items

### ID Mapping Strategy

Since beads may assign different IDs:
1. First pass: Create all beads, capture returned IDs
2. Build mapping: `FEAT-001 -> bead-abc123`
3. Second pass: Add dependencies using mapped IDs

For dry-run mode:
- Use original featmgmt IDs as placeholders
- Note that actual IDs will differ on execution

## Dependencies

### External Dependencies
- jq (JSON processing)
- bash 4.0+ (associative arrays)
- bd CLI (for actual execution)

### Internal Dependencies
- FEAT-014 (Beads integration) - must be complete to test

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| WAVES.md format varies | Medium | Medium | Flexible parser, manual fallback |
| Large PROMPT.md content | Low | Low | Truncation option |
| Special characters in content | Medium | Medium | HEREDOC with quoted delimiter |
| bd CLI changes | Low | Medium | Version check, clear error |
| Dependency cycles | Low | High | Cycle detection, warning |

## Rollback Strategy

If migration causes issues:
1. Beads can be deleted via bd CLI
2. Original featmgmt directory is unchanged
3. Dry-run mode allows preview before commit

## Implementation Phases

### Phase 1: Core Script (Day 1)
- Argument parsing
- Directory scanning
- JSON metadata extraction
- Basic bd create generation

### Phase 2: Content Handling (Day 1-2)
- PROMPT.md reading
- Shell escaping
- HEREDOC generation
- Dry-run mode

### Phase 3: Dependencies (Day 2)
- WAVES.md parsing
- Dependency graph building
- bd dep add generation
- Conflict resolution

### Phase 4: Polish (Day 3)
- Migration report
- Error handling
- Documentation
- Testing

## Testing Strategy

### Unit Tests (via bash)
- Argument parsing edge cases
- JSON extraction with jq
- WAVES.md parsing patterns
- Shell escaping scenarios

### Integration Tests
- Test against featmgmt's own feature-management directory
- Test with mock WAVES.md files
- Test dry-run vs execute modes

### Manual Testing
- Migrate small project
- Verify beads created correctly
- Verify dependencies accurate

## Open Questions

1. Should we support incremental migration (only new items)?
2. How to handle items already migrated (idempotency)?
3. Should we update featmgmt status after migration?
4. Support for custom field mappings?

---
*This plan should be updated as implementation progresses.*

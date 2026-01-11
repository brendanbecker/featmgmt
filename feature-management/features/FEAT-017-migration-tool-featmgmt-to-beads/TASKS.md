# Task Breakdown: FEAT-017

**Work Item**: [FEAT-017: Migration Tool: featmgmt to Beads](PROMPT.md)
**Status**: Not Started
**Last Updated**: 2026-01-11

## Prerequisites

- [ ] Read and understand PROMPT.md
- [ ] Review PLAN.md and update if needed
- [ ] Verify jq is available on system
- [ ] Understand bd CLI create and dep commands
- [ ] Review FEAT-014 for bead format requirements

## Design Tasks

- [ ] Finalize argument list and defaults
- [ ] Define field mapping table (featmgmt -> bead)
- [ ] Document WAVES.md parsing grammar
- [ ] Design ID mapping strategy for dependencies
- [ ] Update PLAN.md with final design decisions

## Implementation Tasks - Core Framework

- [ ] Create script skeleton with shebang and usage function
- [ ] Implement argument parsing (getopt or manual)
- [ ] Add source directory validation
- [ ] Implement dry-run flag handling
- [ ] Add verbose output support
- [ ] Create helper functions (log, error, debug)

## Implementation Tasks - Directory Scanning

- [ ] Implement scan for features/FEAT-XXX-*/ directories
- [ ] Implement scan for bugs/BUG-XXX-*/ directories
- [ ] Optionally scan completed/ directory
- [ ] Build list of items to process
- [ ] Handle empty directories gracefully

## Implementation Tasks - Metadata Extraction

- [ ] Parse feature_request.json with jq
- [ ] Parse bug_report.json with jq
- [ ] Extract: id, title, priority, component, tags
- [ ] Extract: estimated_effort, dependencies
- [ ] Handle missing or malformed JSON (warnings)
- [ ] Map fields to bead attributes

## Implementation Tasks - PROMPT.md Processing

- [ ] Read PROMPT.md content into variable
- [ ] Handle special characters (quotes, backticks, $)
- [ ] Implement HEREDOC generation with proper escaping
- [ ] Handle missing PROMPT.md files
- [ ] Optional: truncation for very large content

## Implementation Tasks - WAVES.md Parsing

- [ ] Detect WAVES.md file (argument or default location)
- [ ] Parse wave headers (## Wave N: Name)
- [ ] Extract item IDs per wave
- [ ] Parse explicit dependencies (depends on X, Y)
- [ ] Build implicit dependencies from wave ordering
- [ ] Store dependency graph structure

## Implementation Tasks - Dependency Resolution

- [ ] Combine JSON dependencies with wave dependencies
- [ ] JSON takes precedence over wave-inferred
- [ ] Detect dependency cycles (warning)
- [ ] Order items for creation (dependency order)
- [ ] Generate dependency commands

## Implementation Tasks - Command Generation

- [ ] Generate bd create commands with proper formatting
- [ ] Include --title, --epic, --labels, --body
- [ ] Generate bd dep add commands
- [ ] Order: all creates first, then all deps
- [ ] Support output to stdout or file

## Implementation Tasks - Migration Report

- [ ] Track items processed (features, bugs)
- [ ] Track items skipped (and reasons)
- [ ] Track dependencies created
- [ ] Collect warnings (missing files, parse errors)
- [ ] Generate summary statistics
- [ ] Format report for readability

## Testing Tasks

- [ ] Test argument parsing (all combinations)
- [ ] Test with featmgmt's own feature-management directory
- [ ] Test WAVES.md parsing with sample files
- [ ] Test dry-run mode produces correct output
- [ ] Test error handling (missing files, bad JSON)
- [ ] Test special character escaping
- [ ] Test with various PROMPT.md sizes

## Documentation Tasks

- [ ] Add usage examples to script header
- [ ] Document field mapping
- [ ] Document WAVES.md format requirements
- [ ] Add troubleshooting section
- [ ] Update featmgmt README with migration option

## Verification Tasks

- [ ] All acceptance criteria from PROMPT.md met
- [ ] Script handles edge cases gracefully
- [ ] Dry-run output is accurate and complete
- [ ] Update feature_request.json status
- [ ] Document completion in comments.md

## Completion Checklist

- [ ] All implementation tasks complete
- [ ] Directory scanning works for features and bugs
- [ ] JSON metadata correctly extracted
- [ ] WAVES.md dependencies parsed correctly
- [ ] Commands properly quoted and escaped
- [ ] Dry-run mode fully functional
- [ ] Migration report generated
- [ ] Documentation updated
- [ ] PLAN.md reflects final implementation
- [ ] Ready for review/merge

---
*Check off tasks as you complete them. Update status field above.*

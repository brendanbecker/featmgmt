# Work Item Schemas

This directory contains JSON schemas that define the required structure and files for featmgmt work items.

## Schema Files

| File | Purpose |
|------|---------|
| `bug-report.schema.json` | JSON Schema for `bug_report.json` metadata files |
| `feature-request.schema.json` | JSON Schema for `feature_request.json` metadata files |
| `action-report.schema.json` | JSON Schema for `action_report.json` metadata files |
| `required-files.json` | Defines which files are required in each work item directory |

## Required Files by Work Item Type

### Bugs (`bugs/BUG-XXX-slug/`)

| File | Required | Description |
|------|----------|-------------|
| `bug_report.json` | **Yes** | Structured metadata (ID, priority, severity, status, etc.) |
| `PROMPT.md` | **Yes** | Self-executing implementation instructions |
| `PLAN.md` | **Yes** | Implementation plan with architecture decisions |
| `TASKS.md` | **Yes** | Task breakdown with checkboxes |
| `comments.md` | No | Progress notes and updates |

### Features (`features/FEAT-XXX-slug/`)

| File | Required | Description |
|------|----------|-------------|
| `feature_request.json` | **Yes** | Structured metadata (ID, priority, effort, status, etc.) |
| `PROMPT.md` | **Yes** | Self-executing implementation instructions |
| `PLAN.md` | **Yes** | Implementation plan with architecture decisions |
| `TASKS.md` | **Yes** | Task breakdown with checkboxes |
| `comments.md` | No | Progress notes and updates |

### Human Actions (`human-actions/ACTION-XXX-slug/`)

| File | Required | Description |
|------|----------|-------------|
| `action_report.json` | **Yes** | Structured metadata (ID, urgency, status, etc.) |
| `INSTRUCTIONS.md` | **Yes** | Instructions for human to complete |
| `comments.md` | No | Progress notes and updates |

## Validation

### Using with work-item-creation-agent

The `work-item-creation-agent` should:

1. **On Creation**: Generate all required files atomically
2. **Post-Creation**: Validate that all required files exist and pass schema validation
3. **On Failure**: Report which files are missing or invalid

### Manual Validation

Validate a JSON file against its schema using any JSON Schema validator:

```bash
# Example with ajv-cli
npx ajv validate -s schemas/bug-report.schema.json -d bugs/BUG-001-example/bug_report.json
```

### Validation Rules

From `required-files.json`:

- **on_creation**: All required files must be created atomically
- **on_start**: All required files must exist before work begins
- **on_completion**: All required files must exist and pass validation

## File Templates

### PLAN.md Structure

```markdown
# Implementation Plan

## Overview
[Brief summary of the approach]

## Architecture Decisions
[Key design choices and rationale]

## Affected Components
[List of files/modules that will change]

## Risk Assessment
[Potential issues and mitigations]

## Rollback Strategy
[How to revert if needed]
```

### TASKS.md Structure

```markdown
# Task Breakdown

## Prerequisites
- [ ] Required dependency or setup task

## Implementation Tasks
- [ ] Core implementation task 1
- [ ] Core implementation task 2

## Testing Tasks
- [ ] Unit tests
- [ ] Integration tests

## Documentation Tasks
- [ ] Update relevant docs

## Completion Checklist
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
```

## Schema Versioning

Schemas follow semantic versioning. The `$id` field contains the schema identifier. When updating schemas:

1. Increment version in schema `$id` if breaking changes
2. Update `required-files.json` version field
3. Document changes in this README

## Integration with Agents

Agents that create or validate work items should:

1. Load `required-files.json` to determine required files
2. Use type-specific schemas to validate JSON metadata
3. Verify all required files exist after creation
4. Report validation errors with specific details

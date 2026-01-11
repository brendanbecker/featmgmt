# Context Engineering Formulas

This document describes the Gastown formulas for automating the Context Engineering methodology.

## Overview

Two formulas are provided:

| Formula | Purpose |
|---------|---------|
| `context-engineering` | Master workflow encoding all 6 stages |
| `ce-stage-5-features` | Detailed Stage 5 bead generation |

## Quick Start

```bash
# List available formulas
gt formula list

# Show formula details
gt formula show context-engineering

# Dry run to preview execution
gt formula run context-engineering --dry-run
```

## Master Formula: context-engineering

The master formula encodes the complete Context Engineering pipeline:

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Stage 1 │───►│ Stage 2 │───►│ Stage 3 │───►│ Stage 4 │───►│ Stage 5 │───►│ Stage 6 │
│Ideation │    │Research │    │ Parsing │    │  Arch   │    │Features │    │  Impl   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `project_name` | Yes | Project name for bead prefixes |
| `project_description` | Yes | Brief description for research prompt |
| `target_directory` | No | Where to create project (default: `.`) |

### Steps

1. **ideation** - Generate deep research prompt from idea
2. **deep-research-gemini** - Parallel research with Gemini
3. **deep-research-chatgpt** - Parallel research with ChatGPT
4. **deep-research-claude** - Parallel research with Claude
5. **parsing** - Parse and synthesize research (creates SYNTHESIS.md)
6. **architecture** - Generate ARCHITECTURE.md and PROJECT_SUMMARY.md
7. **feature-gen** - Generate beads with dependencies
8. **implementation** - GUPP loop until complete

## Stage 5 Formula: ce-stage-5-features

Detailed formula for extracting features and creating beads with dependencies.

### Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `project_name` | Yes | - | Project name for epic/labels |
| `architecture_path` | No | `docs/ARCHITECTURE.md` | Path to architecture doc |
| `summary_path` | No | `docs/PROJECT_SUMMARY.md` | Path to summary doc |
| `epic_id` | No | - | Parent epic (creates new if not provided) |

### Feature Extraction

The formula extracts features from these ARCHITECTURE.md sections:

1. **Core Components** - Each major component becomes a feature
2. **Interfaces** - API contracts, message formats
3. **User-Facing Capabilities** - End-user visible features
4. **Cross-Cutting Concerns** - Auth, logging, error handling

### Dependency Types

The formula analyzes three types of dependencies:

- **Data** - Feature A produces data that Feature B consumes
- **Interface** - Feature A defines interface that Feature B implements
- **Runtime** - Feature A requires Feature B at runtime

## Example Usage

### Starting a New Project

```bash
# Create a context engineering molecule
bd mol wisp create context-engineering \
  --var project_name="my-app" \
  --var project_description="A web application for task management"

# Check what step to work on
bd ready
```

### Running Stage 5 Manually

```bash
# If you already have ARCHITECTURE.md, run Stage 5 directly
gt formula run ce-stage-5-features \
  --var project_name="my-app" \
  --var epic_id="bd-123"

# After completion, check the dependency graph
bd graph

# See unblocked work items
bd ready
```

## Integration with Gastown

### With Polecats (Parallel Workers)

```bash
# Stage 2 can run 3 research tasks in parallel
gt sling deep-research-gemini --polecat
gt sling deep-research-chatgpt --polecat
gt sling deep-research-claude --polecat
gt convoy wait
```

### GUPP Loop for Stage 6

```bash
while [ $(bd ready --count) -gt 0 ]; do
    bead_id=$(bd ready --json | jq -r '.[0].id')
    bd update $bead_id --status in_progress
    # ... implement the feature ...
    bd close $bead_id
done
```

## File Locations

Formulas are stored in `.beads/formulas/` and searched in this order:

1. Project: `.beads/formulas/`
2. User: `~/.beads/formulas/`
3. Gastown: `$GT_ROOT/.beads/formulas/`

## Related Documentation

- [CONTEXT_ENGINEERING_METHODOLOGY.md](../CONTEXT_ENGINEERING_METHODOLOGY.md) - Full methodology description
- [Gastown Glossary](https://github.com/steveyegge/gastown/docs/glossary.md) - MEOW, GUPP, formulas

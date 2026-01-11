# FEAT-014: Context Engineering Master Formula + Stage 5 Bead Generator

**Priority**: P0
**Component**: methodology
**Type**: new_feature
**Estimated Effort**: medium
**Business Value**: critical

> **Note**: This feature was split from a larger scope. See Related Features below.

## Overview

Create the master `context-engineering.formula.toml` and implement Stage 5 bead generation that transforms ARCHITECTURE.md into beads with explicit dependencies. This is the foundation that enables `bd ready` to replace manual WAVES.md ordering.

## Problem Statement

Current Context Engineering methodology:
1. Uses directory-based work items (`features/FEAT-XXX/PROMPT.md`)
2. Manually generates WAVES.md for implementation ordering
3. Dependencies are implicit (inferred from WAVES.md) not explicit

Key limitation: Cannot leverage `bd ready` for automatic unblocked work detection.

## Proposed Solution

### Part 1: Master Formula

Create `context-engineering.formula.toml` that encodes all 6 stages:

```toml
formula = "context-engineering"
description = "Context Engineering Pipeline - Spec-Driven Development"
version = 1

[vars.project_name]
description = "Name of the project"
required = true

[vars.project_description]
description = "Brief project description for research prompt"
required = true

[[steps]]
id = "ideation"
title = "Stage 1: Ideation"
creates = ["deep-research-prompt.md"]

[[steps]]
id = "deep-research"
title = "Stage 2: Deep Research"
needs = ["ideation"]
creates = ["docs/research/*.md"]
parallel = true  # Gemini, ChatGPT, Claude can run simultaneously

[[steps]]
id = "parsing"
title = "Stage 3: Document Parsing"
needs = ["deep-research"]
creates = ["docs/research/SYNTHESIS.md"]

[[steps]]
id = "architecture"
title = "Stage 4: Architecture Generation"
needs = ["parsing"]
creates = ["docs/ARCHITECTURE.md", "docs/PROJECT_SUMMARY.md"]

[[steps]]
id = "feature-gen"
title = "Stage 5: Feature Generation"
needs = ["architecture"]
creates = ["beads:bd-*.features"]
generates_beads = true

[[steps]]
id = "implementation"
title = "Stage 6: Implementation"
needs = ["feature-gen"]
loop = true
exit_condition = "bd ready --count == 0"
```

### Part 2: Stage 5 Bead Generator

Create `ce-stage-5-features.formula.toml` that:

1. **Extracts features** from ARCHITECTURE.md:
   - Core components
   - Interfaces between components
   - User-facing capabilities
   - Cross-cutting concerns

2. **Analyzes dependencies**:
   - Data dependencies (produces/consumes)
   - Interface dependencies (defines/implements)
   - Runtime dependencies (requires existence)

3. **Generates beads**:
   ```bash
   bd create "{{feature.title}}" \
     --type feature \
     --priority {{feature.priority}} \
     --parent {{epic_id}} \
     --body "$(cat PROMPT.md)"
   ```

4. **Establishes dependencies**:
   ```bash
   bd dep add {{child_id}} {{parent_id}} --type {{dep_type}}
   ```

## Bead Hierarchy

```
bd-proj (Epic: Project X)
├── bd-proj.1 (Stage 1: Ideation)
├── bd-proj.2 (Stage 2: Deep Research)
│   ├── bd-proj.2.1 (Gemini Research)
│   ├── bd-proj.2.2 (ChatGPT Research)
│   └── bd-proj.2.3 (Claude Research)
├── bd-proj.3 (Stage 3: Document Parsing)
├── bd-proj.4 (Stage 4: Architecture)
├── bd-proj.5 (Stage 5: Feature Generation)
│   └── [generates feature beads with dependencies]
└── bd-proj.6 (Stage 6: Implementation)
    └── [populated by bd ready from Stage 5 output]
```

## Acceptance Criteria

- [ ] Master formula `context-engineering.formula.toml` exists and validates
- [ ] Stage 5 formula generates beads from ARCHITECTURE.md
- [ ] Beads have explicit dependencies via `bd dep add`
- [ ] `bd ready` produces correct ordering (equivalent to manual WAVES.md)
- [ ] Formula variables documented
- [ ] Basic usage documentation added to CLAUDE.md

## Dependencies

- FEAT-013 (Architecture-to-WAVES Pipeline) - concepts feed into Stage 5
- Beads 0.44.0+ installed
- Gastown installed (for formula execution)

## Out of Scope (Split to Separate Features)

The following were split out to keep this feature focused:

- **FEAT-016**: SYNTHESIS.md to Beads Bridge (traceability)
- **FEAT-017**: Migration Tool: featmgmt to Beads
- **FEAT-018**: Stage 6 Gastown GUPP Loop (`gt sling` integration)
- **FEAT-019**: Context Engineering Agent Role Prompts (Mayor, Polecat, Witness)

## Usage

After implementation:

```bash
# Create a new context engineering pipeline
bd mol wisp create context-engineering \
  --var project_name="MyProject" \
  --var project_description="A system that does X"

# Check what work is ready
bd ready

# Stage 5 will have generated feature beads
bd list --type feature --parent bd-myproject
```

---

*Created: 2026-01-09*
*Last Updated: 2026-01-11*
*Split from original scope: 2026-01-11*

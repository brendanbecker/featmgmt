# FEAT-014: Tasks

**Scope**: Master formula + Stage 5 bead generator only.
**Split from**: Original FEAT-014 was too large. Stage 6 GUPP loop, migration tool, agent prompts, and SYNTHESIS.md bridge are now separate features.

## Section 1: Create Master Formula
- [ ] Create `context-engineering.formula.toml` with all 6 stages
- [ ] Define stage dependencies (each stage needs previous)
- [ ] Define variables: `project_name`, `project_description`, `research_sources`
- [ ] Add pre-flight checks (verify beads initialized, gastown available)
- [ ] Add post-flight hooks (summarize artifacts created)

## Section 2: Implement Stage 5 Bead Generator
- [ ] Create `ce-stage-5-features.formula.toml` with detailed steps
- [ ] Implement feature extraction from ARCHITECTURE.md (per FEAT-013)
- [ ] Implement dependency analysis algorithm
- [ ] Generate `bd create` commands with `--body` containing PROMPT.md content
- [ ] Generate `bd dep add` commands for all dependencies
- [ ] Output machine-readable manifest of created beads

## Section 3: Documentation
- [ ] Add beads workflow section to CLAUDE.md
- [ ] Document `bd` commands for stages 1-5
- [ ] Update Context Engineering methodology doc
- [ ] Add quick reference for formula usage

## Section 4: Testing and Validation
- [ ] Apply formula to a test project
- [ ] Validate Stage 5 generates correct bead hierarchy
- [ ] Validate dependencies produce correct `bd ready` ordering
- [ ] Compare output to manual feature creation

## Progress
- Sections Completed: 0/4
- Last Updated: 2026-01-11

## Related Features (split from original FEAT-014)
- **FEAT-016**: SYNTHESIS.md to Beads Bridge (P3)
- **FEAT-017**: Migration Tool: featmgmt to Beads (P2)
- **FEAT-018**: Stage 6 Gastown GUPP Loop (P1)
- **FEAT-019**: Context Engineering Agent Role Prompts (P2)

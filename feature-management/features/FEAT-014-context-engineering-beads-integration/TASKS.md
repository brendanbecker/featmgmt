# FEAT-014: Tasks

## Section 1: Create Master Formula
- [ ] Create `context-engineering.formula.toml` with all 6 stages
- [ ] Define stage dependencies
- [ ] Define variables: `project_name`, `project_description`, `research_sources`
- [ ] Add pre-flight checks
- [ ] Add post-flight hooks

## Section 2: Implement Stage 5 Bead Generator
- [ ] Create `ce-stage-5-features.formula.toml`
- [ ] Implement feature extraction from ARCHITECTURE.md
- [ ] Implement dependency analysis algorithm
- [ ] Generate `bd create` commands with `--body`
- [ ] Generate `bd dep add` commands
- [ ] Output machine-readable manifest

## Section 3: Implement Stage 6 Gastown Integration
- [ ] Create `ce-stage-6-implementation.formula.toml`
- [ ] Implement `bd ready` → `gt sling` loop
- [ ] Define polecat spawning strategy
- [ ] Implement convoy creation
- [ ] Add witness monitoring
- [ ] Implement completion detection

## Section 4: Create Migration Tool
- [ ] Create `scripts/migrate-featmgmt-to-beads.sh`
- [ ] Parse existing `features/*/PROMPT.md` files
- [ ] Extract implicit dependencies from WAVES.md
- [ ] Generate `bd create` and `bd dep add` commands
- [ ] Preserve metadata
- [ ] Create migration report

## Section 5: Update CLAUDE.md Instructions
- [ ] Add beads workflow section
- [ ] Document `bd` commands for each stage
- [ ] Document `gt` commands for Stage 6
- [ ] Add troubleshooting
- [ ] Update quick reference card

## Section 6: Create Agent Role Prompts
- [ ] Create Mayor prompt for CE oversight
- [ ] Create Polecat prompt template
- [ ] Create Witness prompt
- [ ] Define hook content format
- [ ] Integrate with existing featmgmt agents

## Section 7: Implement SYNTHESIS.md → Beads Bridge
- [ ] Create parser for SYNTHESIS.md
- [ ] Extract key decisions as beads
- [ ] Link decisions to architecture sections
- [ ] Enable traceability

## Section 8: Testing and Validation
- [ ] Apply pipeline to real project
- [ ] Validate Stage 5 bead hierarchy
- [ ] Validate dependency ordering
- [ ] Validate Stage 6 loop
- [ ] Compare to manual WAVES.md
- [ ] Benchmark time savings

## Progress
- Sections Completed: 0/8
- Last Updated: 2026-01-09

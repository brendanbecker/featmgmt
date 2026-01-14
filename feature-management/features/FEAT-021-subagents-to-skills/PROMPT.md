# FEAT-021: Transform Sub-agents to Skills

**Priority**: P1
**Component**: architecture
**Type**: refactor
**Estimated Effort**: medium
**Business Value**: high

## Overview

Refactor the existing "sub-agents" (currently markdown files in `claude-agents/` and `subagent-patterns/`) into standardized "Skills" compatible with the `agentskills.io` concept and the Context Engineering Methodology. This allows them to be standardized, discovered, and invoked programmatically by an agent harness, rather than just being copy-pasted prompts.

## Problem Statement

Currently, "sub-agents" are monolithic markdown files containing prompts, scripts, and instructions.
- They are hard to maintain and version.
- Scripts are embedded in markdown, making them hard to test or run independently.
- There is no standard interface for "invoking" them.
- They are specific to Claude Code's "agent" concept but could be more general "skills".

## Proposed Solution

Create a `skills/` directory structure where each capability is a self-contained unit.

**Standard Skill Structure:**
```
skills/
  <skill-name>/
    README.md          # Meta-info: Description, Inputs, Outputs, Usage
    PROMPT.md          # The core system prompt/instruction for the LLM
    scripts/           # Executable scripts extracted from the original agent docs
    examples/          # Example inputs/outputs
```

**Migration Targets:**
1. `document-parser` (mentioned in methodology, likely needs creation/extraction)
2. `scan-prioritize-agent` -> `skills/scan-prioritize`
3. `bug-processor-agent` -> `skills/bug-processor`
4. `test-runner-agent` -> `skills/test-runner`
5. `retrospective-agent` -> `skills/retrospective`
6. `work-item-creation-agent` -> `skills/work-item-creation`
7. GitOps agents (`infra-executor`, `task-scanner`, `verification`) -> `skills/gitops/*`

## Implementation Requirements

1.  **Define Skill Schema**: Establish the standard folder structure and required files.
2.  **Extract Scripts**: Identify bash/python blocks in existing agent markdown and move them to `scripts/` files within the skill.
3.  **Refactor Prompts**: Update `PROMPT.md` to reference the external scripts instead of embedding them.
4.  **Documentation**: Ensure `README.md` clearly defines the "Contract" (Input artifacts -> Output artifacts).
5.  **Backward Compatibility**: Ensure existing workflows (like `OVERPROMPT.md`) can still function or are updated to point to the new skills.

## Success Criteria

- All sub-agents in `claude-agents/` are migrated to `skills/`.
- Each skill has a `PROMPT.md` and separated `scripts/`.
- Scripts are executable and linted.
- A "Skill Harness" or wrapper script can invoke a skill (e.g., `run-skill <skill-name>`).

## Out of Scope

- Rewrite of the core logic (just refactoring structure).
- Creating new skills not currently in sub-agents (except `document-parser` if it exists partially).

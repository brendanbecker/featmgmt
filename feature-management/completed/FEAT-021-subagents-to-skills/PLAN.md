# FEAT-021 Implementation Plan: Sub-agents to Skills

## Overview

Migrate monolithic agent markdown files into modular "Skills" with separated prompts and scripts.

## Phase 1: Foundation & Schema

**Goal:** Define the structure and tooling for skills.

1.  **Create `skills/` root directory.**
2.  **Define `skills/README.md`** explaining the structure.
3.  **Create `skills/_template/`** for new skills.

## Phase 2: Migration (Batch 1 - Core)

**Goal:** Migrate the most critical agents first.

1.  **Test Runner (`skills/test-runner`)**:
    - Extract DB setup scripts.
    - Extract test execution logic.
    - Separate prompt.
2.  **Bug Processor (`skills/bug-processor`)**:
    - Extract logic for finding/reading code.
3.  **Scan & Prioritize (`skills/scan-prioritize`)**:
    - Extract prioritization logic.

## Phase 3: Migration (Batch 2 - Utility)

**Goal:** Migrate support agents.

1.  **Work Item Creation (`skills/work-item-creation`)**:
    - Extract JSON schema templates.
2.  **Retrospective (`skills/retrospective`)**:
    - Extract log parsing scripts.
3.  **GitOps Agents**:
    - Move `infra-executor`, `task-scanner`, `verification`.

## Phase 4: Integration & Cleanup

**Goal:** Update the system to use the new skills.

1.  **Update `OVERPROMPT.md`** and templates to reference `skills/` instead of `claude-agents/`.
2.  **Deprecate `claude-agents/` and `subagent-patterns/`**:
    - Move to `deprecated/` or remove.
3.  **Verify workflows**: Ensure the context engineering pipeline still works.

## Skill Structure Specification

```
skills/<name>/
├── README.md           # Usage, Inputs, Outputs
├── PROMPT.md           # The "Role" and "Instructions" for the LLM
├── scripts/            # Helper scripts (chmod +x)
│   ├── setup.sh
│   └── verify.py
└── examples/           # Sample interactions
```

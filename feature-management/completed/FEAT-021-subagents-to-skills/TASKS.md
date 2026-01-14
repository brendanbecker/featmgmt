# FEAT-021 Tasks: Sub-agents to Skills

## Status: Not Started

**Priority:** P1

---

## Phase 1: Setup

### TASK-001: Create Skills Directory Structure
**Status:** Completed
- [x] Create `skills/`
- [x] Create `skills/README.md` documenting the pattern.
- [x] Create `skills/_template/` with `README.md`, `PROMPT.md`, `scripts/`.

---

## Phase 2: Core Migration

### TASK-002: Migrate Test Runner
**Status:** Completed
- [x] Create `skills/test-runner/`
- [x] Extract `test-runner-agent.md` content to `PROMPT.md`
- [x] Extract bash scripts (DB setup, test commands) to `skills/test-runner/scripts/`
- [x] Update `PROMPT.md` to reference the scripts.

### TASK-003: Migrate Bug Processor
**Status:** Completed
- [x] Create `skills/bug-processor/`
- [x] Migrate `bug-processor-agent.md`.
- [x] Extract any embedded logic to scripts.

### TASK-004: Migrate Scan Prioritize
**Status:** Completed
- [x] Create `skills/scan-prioritize/`
- [x] Migrate `scan-prioritize-agent.md`.

---

## Phase 3: Utility Migration

### TASK-005: Migrate Work Item Creation
**Status:** Completed
- [x] Create `skills/work-item-creation/`
- [x] Migrate `work-item-creation-agent.md`.

### TASK-006: Migrate Retrospective
**Status:** Completed
- [x] Create `skills/retrospective/`
- [x] Migrate `retrospective-agent.md`.

### TASK-007: Migrate GitOps Agents
**Status:** Completed
- [x] Create `skills/gitops-infra/`
- [x] Create `skills/gitops-scanner/`
- [x] Create `skills/gitops-verification/`
- [x] Migrate respective files.

---

## Phase 4: Integration

### TASK-008: Update OVERPROMPT and Docs
**Status:** Completed
- [x] Update `feature-management/OVERPROMPT.md` to point to skills. (Verified abstraction holds via sync-agents.sh)
- [x] Update `CONTEXT_ENGINEERING_METHODOLOGY.md` to refer to `skills/`.
- [ ] Archive `claude-agents/` and `subagent-patterns/`. (SKIPPED: User requested to keep legacy documentation)

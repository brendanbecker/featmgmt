# FEAT-021 Tasks: Sub-agents to Skills

## Status: Not Started

**Priority:** P1

---

## Phase 1: Setup

### TASK-001: Create Skills Directory Structure
**Status:** Not Started
- [ ] Create `skills/`
- [ ] Create `skills/README.md` documenting the pattern.
- [ ] Create `skills/_template/` with `README.md`, `PROMPT.md`, `scripts/`.

---

## Phase 2: Core Migration

### TASK-002: Migrate Test Runner
**Status:** Not Started
- [ ] Create `skills/test-runner/`
- [ ] Extract `test-runner-agent.md` content to `PROMPT.md`
- [ ] Extract bash scripts (DB setup, test commands) to `skills/test-runner/scripts/`
- [ ] Update `PROMPT.md` to reference the scripts.

### TASK-003: Migrate Bug Processor
**Status:** Not Started
- [ ] Create `skills/bug-processor/`
- [ ] Migrate `bug-processor-agent.md`.
- [ ] Extract any embedded logic to scripts.

### TASK-004: Migrate Scan Prioritize
**Status:** Not Started
- [ ] Create `skills/scan-prioritize/`
- [ ] Migrate `scan-prioritize-agent.md`.

---

## Phase 3: Utility Migration

### TASK-005: Migrate Work Item Creation
**Status:** Not Started
- [ ] Create `skills/work-item-creation/`
- [ ] Migrate `work-item-creation-agent.md`.

### TASK-006: Migrate Retrospective
**Status:** Not Started
- [ ] Create `skills/retrospective/`
- [ ] Migrate `retrospective-agent.md`.

### TASK-007: Migrate GitOps Agents
**Status:** Not Started
- [ ] Create `skills/gitops-infra/`
- [ ] Create `skills/gitops-scanner/`
- [ ] Create `skills/gitops-verification/`
- [ ] Migrate respective files.

---

## Phase 4: Integration

### TASK-008: Update OVERPROMPT and Docs
**Status:** Not Started
- [ ] Update `feature-management/OVERPROMPT.md` to point to skills.
- [ ] Update `CONTEXT_ENGINEERING_METHODOLOGY.md` to refer to `skills/`.
- [ ] Archive `claude-agents/` and `subagent-patterns/`.

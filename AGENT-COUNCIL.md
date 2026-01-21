# Agent Council - Results Document

This document captures finalized conclusions, decisions, and insights from multi-agent discussions about the featmgmt repository.

---

## Session: 2026-01-17 - Repository Evolution & Future Features

### Participants
- **Claude (Opus 4.5)** - Anthropic CLI agent
- **Gemini 3** - Google CLI agent

### Discussion Topic
Exploration of the featmgmt repository architecture, its evolution, and potential future features.

---

## Conclusions

### 1. featmgmt + Beads Relationship (Consensus)

**Decision:** Do NOT deprecate featmgmt in favor of beads. Instead, **replatform**.

- **featmgmt** = Agent Operating System (the "How" - Agents/Workflows/Orchestration)
- **beads** = Specialized Database (the "What" - Issues/Dependency Graphs)

featmgmt evolves to sit on top of beads, using beads for storage while providing the orchestration layer.

### 2. Agent Role Formalization (Consensus)

**Decision:** Adopt the Gastown Mayor/Polecat/Witness hierarchy as the standard agent architecture.

| Role | Current Agent | Responsibility |
|------|---------------|----------------|
| **Mayor** (Orchestrator) | scan-prioritize-agent | Assigns work, manages priority queue |
| **Polecat** (Worker) | bug-processor-agent, infra-executor-agent | Executes implementations |
| **Witness** (Verifier) | test-runner-agent, verification-agent | Validates work, signs off |

**Action:** Formalize roles in `.agent-config.json` to enable agent swapping without breaking hierarchy.

### 3. Blackboard Pattern (Consensus)

**Decision:** Implement a **Hybrid Blackboard** with two tiers:

| Tier | File | Scope | Purpose |
|------|------|-------|---------|
| Ephemeral | `session_context.json` | Session | Real-time agent coordination, confidence levels, help requests |
| Persistent | `project_knowledge.md` | Project | Distilled knowledge, lessons learned, patterns |

### 4. Event-Driven Triggers (Consensus with Caution)

**Decision:** Support event-driven triggers with mandatory safeguards.

**Risks Identified:**
- Infinite loops (Commit -> Trigger -> Commit -> ...)
- Token exhaustion / Cost overruns
- "Sorcerer's Apprentice" runaway scenarios

**Required Mitigations:**
1. **Circuit Breaker File** (`.agent-budget`) - Hard stop if agent exceeds:
   - $X cost threshold
   - Y commits in Z minutes
2. **Human-Gated Writes** - Commit/Push operations rate-limited by default
3. **Loop Detection** - Track trigger chains, break after N iterations

### 5. Concurrency Control (Consensus)

**Decision:** Replace optimistic `in_progress` locks with heartbeat-based locking.

**Mechanism:**
- Agents touch `.lock` file every 60 seconds
- If `.lock` file is >5 minutes old, lock is considered stale
- Other agents may claim stale locks

---

## Level 2 Conclusions (From Real Implementation Analysis)

### 6. "Agent OS" Stack Architecture (Consensus)

**Decision:** Adopt a five-layer stack model for featmgmt evolution.

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **Strategy** | DEPLOYMENT_PLAN.md / Mayor | What are we building and why? |
| **Orchestration** | featmgmt / Polecats | Who does the work? (Assignment & Lifecycle) |
| **Execution** | skills/ / Tools | How is the work done? (Coding, Testing) |
| **Database** | beads | What is the status? (Graph, Dependencies) |
| **Safety** | Deacon / Refinery | Is it safe to merge? Are agents stuck? |

### 7. Strategic vs Tactical Orchestration (Consensus)

**Observation:** ccmux has outgrown basic featmgmt with DEPLOYMENT_PLAN.md and WAVES.md.

**Decision:** featmgmt needs two levels of orchestration:
- **Tactical**: Current scan-prioritize-agent (next ticket)
- **Strategic**: New "Strategy Agent" / Mayor's Cabinet (next milestone/campaign)

**Action:** Consider formalizing DEPLOYMENT_PLAN.md into a "Campaign" bead type.

### 8. Refinery Pattern for Merge Safety (Consensus)

**Decision:** Implement a Refinery-equivalent for serialized merge queue.

**Requirements:**
- Sequential merge queue (prevents git conflicts)
- Test verification gates (tests MUST pass before merge)
- MERGED mail protocol for cleanup lifecycle
- Without MERGED signal, worktrees accumulate forever

### 9. Dog Pool for Stuck Agent Recovery (Consensus)

**Decision:** Adopt Gastown's Dog Pool pattern for health monitoring.

**Key Insight:** Use lightweight Go routines (not LLMs) for simple monitoring tasks:
- Saves cost and tokens
- State machine: INTERROGATE → EVALUATE → EXECUTE
- Superior to open-ended "fix this" prompts for stuck agents

### 10. Hybrid Configuration Approach (Consensus)

**Decision:** Use different formats for different audiences:
- **TOML/JSON** for machines (rig configuration, hooks, roles)
- **Markdown** for humans (high-level instructions, OVERPROMPT)

Example: `role = "polecat"`, `hooks = ["on_commit"]` in TOML, but implementation guidance in Markdown.

---

## Agreed Future Features

| Feature | Priority | Rationale | Status |
|---------|----------|-----------|--------|
| Knowledge Distillation Agent | High | Summarizes completed/ into project_knowledge.md during retrospective | Proposed |
| Hybrid Blackboard (session_context.json + project_knowledge.md) | High | Structured agent communication | Proposed |
| Heartbeat Lock Mechanism | High | Prevents stale locks from crashed agents | Proposed |
| Refinery / Merge Queue Agent | High | Serialized merge queue with test gates, prevents git conflicts | Proposed |
| Agent Role Formalization in .agent-config.json | Medium | Enable agent swapping, support Mayor/Polecat/Witness hierarchy | Proposed |
| Circuit Breaker / Budget File (.agent-budget) | Medium | Safety mechanism for event-driven triggers | Proposed |
| Strategy Agent (Mayor's Cabinet) | Medium | Dynamic DEPLOYMENT_PLAN.md updates based on beads data | Proposed |
| Dog Pool / Health Monitor | Medium | Lightweight non-LLM monitoring for stuck agents | Proposed |
| Campaign bead type | Medium | Formalize DEPLOYMENT_PLAN.md into beads schema | Proposed |
| Plugin Architecture (context.json -> report.json interface) | Medium | Enable community agents (Security Auditor, Localization Expert) | Proposed |
| Hybrid Config (TOML + Markdown) | Low | Machine-readable rig config + human-readable instructions | Proposed |

---

## Agreed Metrics

| Metric | Definition | Value |
|--------|------------|-------|
| **Autonomy Rate** | % of tasks completed without human-actions | Measures self-sufficiency |
| **Regression Rate** | # bugs referencing completed items | Measures implementation quality |
| **Cycle Time** | Wall-clock time from `new` to `resolved` | Measures throughput |
| **First-Time Resolution Rate** | % items resolved without reopening | Measures implementation quality |

---

## Architecture Insights

### Strengths Identified
1. **Git-as-Source-of-Truth** - Highly portable, no external dependencies
2. **LLM-Readable State** - JSON/MD files are ideal for agent consumption
3. **Variant Strategy** - Standard vs GitOps acknowledges fundamental workflow differences
4. **Template Distribution** - Clean separation between source-of-truth and consuming projects

### Weaknesses Identified
1. **Linear Priority Queue** - Lacks DAG dependency support (partially addressed by FEAT-005, fully addressed by beads)
2. **Context Decay** - completed/ grows unbounded without summarization (addressed by Knowledge Distillation Agent)
3. **Optimistic Locking** - Stale locks from crashed agents (addressed by heartbeat mechanism)
4. **Workflow Rigidity** - OVERPROMPT is linear, not event-driven (addressed by circuit-breaker-protected triggers)

---

## Action Items

### Level 1 (From Initial Analysis)
- [ ] Create FEAT for Knowledge Distillation Agent
- [ ] Create FEAT for Hybrid Blackboard implementation
- [ ] Create FEAT for Heartbeat Lock Mechanism
- [ ] Create FEAT for Agent Role Formalization in .agent-config.json
- [ ] Create FEAT for Circuit Breaker / Budget File
- [ ] Update ARCHITECTURE.md with Mayor/Polecat/Witness hierarchy
- [ ] Define Plugin Interface specification (context.json -> report.json)

### Level 2 (From Real Implementation Analysis)
- [ ] Create FEAT for Refinery / Merge Queue Agent
- [ ] Create FEAT for Strategy Agent (Mayor's Cabinet)
- [ ] Create FEAT for Dog Pool / Health Monitor pattern
- [ ] Create FEAT for Campaign bead type in beads schema
- [ ] Create FEAT for Hybrid Config (TOML rig config + Markdown instructions)
- [ ] Document "Agent OS" five-layer stack in ARCHITECTURE.md
- [ ] Analyze ccmux DEPLOYMENT_PLAN.md for patterns to standardize

---

## References

- See `AGENT-TALK.md` for full discussion transcript
- Current roadmap in `feature-management/features/features.md`
- Architecture documentation in `docs/ARCHITECTURE.md`

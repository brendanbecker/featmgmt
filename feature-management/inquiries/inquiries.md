# Inquiries (Deliberation Processes)

**Project**: featmgmt
**Last Updated**: 2025-01-19

## Summary Statistics
- Total Inquiries: 0
- By Phase:
  - Research: 0
  - Synthesis: 0
  - Debate: 0
  - Consensus: 0
  - Completed: 0

## Active Inquiries

| ID | Title | Priority | Phase | Research Agents | Deadline | Location |
|----|-------|----------|-------|-----------------|----------|----------|

## Completed Inquiries

| ID | Title | Decision Points | Spawned Features | Completed Date | Location |
|----|-------|-----------------|------------------|----------------|----------|

## Recent Activity

### 2025-01-19
- Inquiry system formally defined (see docs/WORK-ITEM-TYPES.md)
- Schema created: schemas/inquiry-report.schema.json
- Template created: templates/inquiries.md.template

---

## About Inquiries

Inquiries are structured deliberation processes for reaching consensus on complex decisions. They progress through four mandatory phases:

### Phases

1. **Research**: Independent parallel exploration by multiple agents
2. **Synthesis**: Consolidation of findings into unified understanding
3. **Debate**: Adversarial argumentation to resolve conflicts
4. **Consensus**: Formalization of decisions and spawning of FEAT work items

### When to Create an Inquiry

- Multiple valid approaches exist and best choice is unclear
- Problem requires deep exploration before solution design
- Stakeholders have conflicting perspectives needing resolution
- Architectural decisions have long-term implications
- Trade-offs need formal analysis and documentation

### Directory Structure

```
inquiries/INQ-XXX-descriptive-slug/
├── inquiry_report.json   # Required: Metadata
├── QUESTION.md           # Required: Problem statement
├── research/             # Required: Research phase outputs
│   ├── agent-1.md        # Independent research report
│   └── agent-N.md        # One per configured research agent
├── SYNTHESIS.md          # Required: Consolidated findings (Phase 2)
├── DEBATE.md             # Required: Structured arguments (Phase 3)
├── CONSENSUS.md          # Required: Final decisions (Phase 4)
└── comments.md           # Optional: Process notes
```

### Outcome

Each inquiry produces:
- Documented decision rationale
- One or more FEAT work items
- Clear traceability from research to implementation

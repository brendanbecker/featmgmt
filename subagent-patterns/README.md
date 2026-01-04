# Subagent Patterns

This directory contains **implementation-agnostic specifications** for autonomous work management agents. These patterns describe the conceptual design, decision logic, and coordination protocols for agents that manage software development workflows.

## What Are Subagent Patterns?

Subagent patterns are architectural specifications that capture:

- **Purpose**: What problem the agent solves and why it exists
- **Responsibilities**: The core functions the agent performs
- **Workflow**: The logical sequence of operations (independent of tools)
- **Contracts**: What data the agent receives and produces
- **Decision Rules**: The logic that drives agent behavior
- **Integration**: How the agent coordinates with other agents
- **Quality Criteria**: What constitutes successful execution

These patterns are **not code**. They are conceptual blueprints that can be implemented in any agent framework.

## Relationship to Context Engineering

These patterns embody the principles of **Context Engineering** - the discipline of designing the information environment that enables AI agents to perform effectively.

### Context Engineering Principles Applied

1. **Clear Role Definition**: Each pattern explicitly defines what the agent is and isn't responsible for
2. **Structured Input/Output**: Well-defined contracts prevent ambiguity and errors
3. **Decision Transparency**: Decision rules are explicit, not hidden in prompts
4. **Coordination Protocols**: Clear handoff points between agents
5. **Quality Metrics**: Measurable criteria for success

### The Pattern as Context

When implementing these patterns, the specification itself becomes part of the agent's context:
- The **Purpose** section shapes the agent's understanding of its role
- The **Workflow** provides a mental model for task execution
- The **Decision Rules** constrain behavior to desired outcomes
- The **Quality Criteria** enable self-assessment

## Using These Patterns

### For Implementation

To implement a pattern in your preferred framework:

1. **Read the entire specification** - Understand purpose, workflow, and constraints
2. **Map capabilities to tools** - Translate abstract operations to framework-specific tools
3. **Implement decision logic** - Encode the decision rules as branching logic
4. **Define data schemas** - Create concrete types matching input/output contracts
5. **Add framework integration** - Connect to your orchestration layer
6. **Validate against quality criteria** - Test that outputs meet specifications

### Framework Mapping Examples

| Abstract Concept | Claude Code | OpenAI Agents SDK | LangGraph | AutoGen |
|------------------|-------------|-------------------|-----------|---------|
| Read file | `Read` tool | `file_read` function | Custom node | Agent capability |
| Search content | `Grep` tool | Custom search | Search node | Message handler |
| Execute command | `Bash` tool | `shell_exec` function | Command node | Code executor |
| Agent coordination | `Task` tool | Handoff/transfer | Edge routing | Group chat |
| Structured output | JSON in response | Pydantic models | State schema | Dict messages |

### For Extension

To create new patterns:

1. **Start with the problem** - What capability is missing? What failure mode are you addressing?
2. **Define contracts first** - Input and output schemas constrain the design
3. **Document decision points** - Where does the agent need to make choices?
4. **Map dependencies** - Which other agents does this pattern interact with?
5. **Specify quality criteria** - How will you know if it's working?

## Pattern Categories

### Shared Patterns
Agents used across all workflow types:

| Pattern | Purpose |
|---------|---------|
| `work-item-creation.md` | Standardized creation of bugs, features, and action items |
| `retrospective.md` | Session analysis, backlog reprioritization, and session reporting |
| `git-history.md` | Repository history analysis and regression tracking |

### Application Development Patterns
For software development workflows:

| Pattern | Purpose |
|---------|---------|
| `scan-prioritize.md` | Backlog scanning and priority queue building |
| `bug-processor.md` | Systematic implementation of fixes |
| `test-runner.md` | Test execution and failure analysis |

### Infrastructure Patterns
For GitOps and infrastructure workflows:

| Pattern | Purpose |
|---------|---------|
| `task-scanner.md` | Infrastructure task scanning |
| `infra-executor.md` | Infrastructure change execution |
| `verification.md` | Cluster state verification |

## Pattern Structure

Each pattern follows this structure:

```markdown
# {Pattern Name}

## Purpose
One paragraph describing what this agent accomplishes.

## Problem Statement
What problems does this agent solve?

## Responsibilities
Bullet list of core functions.

## Workflow
Numbered logical steps.

## Input Contract
Required and optional inputs with types.

## Output Contract
Success and error outputs.

## Decision Rules
The logic that drives behavior.

## Integration Pattern
How it connects to other agents.

## Quality Criteria
What makes successful execution.

## Implementation Notes
Framework-agnostic guidance.
```

## Relationship to Concrete Implementations

```
subagent-patterns/           # Abstract specifications (this directory)
├── README.md
├── work-item-creation.md
├── retrospective.md
└── ...

claude-agents/               # Claude Code implementation
├── shared/
│   ├── work-item-creation-agent.md
│   └── retrospective-agent.md
├── standard/
└── gitops/
```

The abstract patterns in `subagent-patterns/` are the **source of truth** for agent behavior. The Claude Code implementations in `claude-agents/` are one possible realization of these patterns.

When implementing for another framework:
1. Read the pattern specification
2. Create framework-specific agent definition
3. Map abstract operations to framework tools
4. Maintain behavioral compatibility with the specification

## Design Philosophy

### Single Responsibility
Each agent does one thing well. Complex workflows emerge from composition.

### Explicit Over Implicit
Decision rules, thresholds, and edge cases are documented, not assumed.

### Contract-Driven
Clear input/output schemas enable reliable agent-to-agent communication.

### Quality Built-In
Every pattern includes criteria for self-assessment and validation.

### Implementation Freedom
Patterns describe *what* and *why*, not *how*. Implementations choose their own tools.

## Contributing

When adding or modifying patterns:

1. **Maintain abstraction** - Don't reference specific tools or frameworks
2. **Document decisions** - Explain *why* rules exist, not just what they are
3. **Consider edge cases** - What happens when things go wrong?
4. **Update integration points** - Keep coordination protocols consistent
5. **Test conceptually** - Walk through the workflow mentally before committing

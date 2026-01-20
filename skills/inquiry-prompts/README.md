# Inquiry Prompts Skill

Generate research agent prompts from INQ QUESTION.md files for Phase 1 deliberation.

## Overview

The `/inquiry-prompts` skill parses QUESTION.md files containing research questions and distributes them across multiple research agents. It generates complete, context-rich prompts that include the inquiry context, constraints, and clear instructions for independent research.

## Inputs

### Required Files

| File | Description |
|------|-------------|
| `inquiry_report.json` | Inquiry metadata including context, constraints, and `research_agents` count |
| `QUESTION.md` | The questions to be researched |

### QUESTION.md Formats

The skill supports multiple question formats:

**Numbered Lists**
```markdown
# What is the best approach for implementing feature X?

1. What are the performance implications of each approach?
2. How does this affect security?
3. What are the maintenance costs?
4. What is the learning curve for the team?
```

**Headed Sections**
```markdown
# Should we use microservices or monolith?

## Technical Feasibility
Evaluate the technical complexity of each approach and our team's capability.

## Cost Analysis
What are the infrastructure and licensing costs for each approach?

## Scalability
How does each approach handle 10x and 100x traffic growth?
```

**Bullet Points**
```markdown
# Evaluate database options for our new service

- Evaluate PostgreSQL for this use case
- Evaluate MongoDB for this use case
- Compare operational complexity
- Analyze cost at expected scale
```

## Outputs

### JSON Output (default)

Returns structured JSON with generated prompts:

```json
{
  "inquiry_id": "INQ-001",
  "title": "Database Selection for User Service",
  "total_agents": 3,
  "algorithm": "round-robin",
  "format_detected": "numbered",
  "main_question": "What database should we use for the user service?",
  "total_questions": 6,
  "prompts": [
    {
      "agent_number": 1,
      "questions": ["Question 1", "Question 4"],
      "output_file": "research/agent-1.md",
      "prompt": "# Research Agent 1 - Independent Research Report\n\n..."
    },
    ...
  ]
}
```

### File Output

Creates markdown files in `research/` directory:

```
research/
├── agent-1.md
├── agent-2.md
└── agent-3.md
```

Each file includes YAML frontmatter with metadata and the full research prompt.

## Distribution Algorithms

### Round-Robin (default)

Distributes questions sequentially to agents:
- Question 1 -> Agent 1
- Question 2 -> Agent 2
- Question 3 -> Agent 3
- Question 4 -> Agent 1 (wraps around)

**Best for**: Questions of similar complexity with no topical grouping.

### Balanced

Distributes questions evenly by count:
- 7 questions / 3 agents = 3, 2, 2 questions per agent
- Earlier agents get the extra questions

**Best for**: When you want equal workload distribution regardless of question order.

### Grouped

Keeps questions with the same heading together:
- All questions under `## Technical Feasibility` stay together
- Uses bin-packing to balance groups across agents

**Best for**: Headed section format where related questions should be researched together.

## Usage

### Command Line

```bash
# JSON output with round-robin distribution
uv run python scripts/generate_prompts.py inquiries/INQ-001-example/

# File output with balanced distribution
uv run python scripts/generate_prompts.py inquiries/INQ-001-example/ \
  --output files --algorithm balanced

# Override number of agents
uv run python scripts/generate_prompts.py inquiries/INQ-001-example/ \
  --agents 5 --algorithm grouped
```

### As Claude Code Skill

```
/inquiry-prompts
```

Or with options:
```
/inquiry-prompts inquiries/INQ-001/ --algorithm grouped --output files
```

## Examples

### Example inquiry_report.json

```json
{
  "inquiry_id": "INQ-001",
  "title": "Authentication Strategy for Mobile App",
  "component": "auth",
  "priority": "P1",
  "status": "research",
  "phase": "research",
  "created_date": "2025-01-20",
  "updated_date": "2025-01-20",
  "question": "What authentication strategy should we use for the mobile app?",
  "context": "We are building a new mobile app that needs secure authentication. The app will handle sensitive financial data and must comply with SOC2 requirements.",
  "constraints": [
    "Must support biometric authentication",
    "Must work offline for at least 24 hours",
    "Must comply with SOC2 Type II",
    "Budget: $10k/year max for third-party services"
  ],
  "research_agents": 3,
  "scope": "Focus on authentication only, not authorization or session management"
}
```

### Example QUESTION.md

```markdown
# What authentication strategy should we use for the mobile app?

## Security Analysis
Evaluate the security posture of OAuth2, SAML, and custom JWT implementations.

## Offline Capability
How can we maintain secure authentication when the device is offline?

## Third-Party Options
Evaluate Auth0, Firebase Auth, and AWS Cognito for our requirements.

## Implementation Complexity
Compare the development effort required for each approach.
```

### Example Generated Prompt

```markdown
# Research Agent 1 - Independent Research Report

## Assignment

You are Research Agent 1 of 3 working on **Authentication Strategy for Mobile App**.

### Core Question

What authentication strategy should we use for the mobile app?

### Your Assigned Sub-Questions

1. Evaluate the security posture of OAuth2, SAML, and custom JWT implementations.
2. Compare the development effort required for each approach.

## Context

We are building a new mobile app that needs secure authentication. The app will handle sensitive financial data and must comply with SOC2 requirements.

## Constraints

The following constraints MUST be satisfied by any proposed solution:

- Must support biometric authentication
- Must work offline for at least 24 hours
- Must comply with SOC2 Type II
- Budget: $10k/year max for third-party services

## Scope

Focus on authentication only, not authorization or session management

## Instructions

1. Research your assigned questions independently
2. **DO NOT** consult or coordinate with other research agents
3. Document your findings thoroughly with evidence
...
```

## Error Handling

| Error | Message | Solution |
|-------|---------|----------|
| Missing inquiry_report.json | `inquiry_report.json not found at {path}` | Create the file with required fields |
| Missing QUESTION.md | `QUESTION.md not found at {path}` | Create the file with research questions |
| Invalid JSON | `Invalid JSON: {details}` | Fix JSON syntax in inquiry_report.json |
| Unknown algorithm | `Unknown algorithm: {name}` | Use: round-robin, balanced, or grouped |

## Integration

This skill integrates with the featmgmt INQ workflow:

1. **Create INQ**: Use `/work-item-creation` to create inquiry
2. **Generate Prompts**: Use `/inquiry-prompts` to create research prompts
3. **Execute Research**: Spawn agents with generated prompts
4. **Collect Results**: Research reports saved to `research/` directory
5. **Continue Workflow**: Proceed to Phase 2 (Synthesis)

## Files

```
skills/inquiry-prompts/
├── SKILL.md                    # Agent instructions
├── README.md                   # This file
└── scripts/
    └── generate_prompts.py     # Core implementation
```

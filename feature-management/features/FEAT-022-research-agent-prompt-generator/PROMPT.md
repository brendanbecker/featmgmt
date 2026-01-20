# FEAT-022: Research Agent Prompt Generator

## Overview

Create the `/inquiry-prompts` skill that parses INQ QUESTION.md files and generates independent research prompts for Phase 1 agents. This skill enables the automated distribution of research questions to multiple agents for parallel independent exploration.

## Problem Statement

When running Phase 1 (Research) of an INQ deliberation process:
- QUESTION.md may contain complex questions with multiple sub-questions
- Questions need to be distributed across N research agents
- Each agent needs a complete, context-rich prompt
- Manual prompt creation is tedious and error-prone
- No standardized way to distribute questions

## Proposed Solution

Create `skills/inquiry-prompts/` with:
1. `SKILL.md` - Instructions for the skill
2. `scripts/generate_prompts.py` - Core logic for parsing and generation
3. `README.md` - Usage documentation

## Requirements

### QUESTION.md Parsing

Support multiple question formats:

**1. Numbered Lists**
```markdown
1. What are the performance implications?
2. How does this affect security?
3. What are the maintenance costs?
```

**2. Headed Sections**
```markdown
## Technical Feasibility
What technologies are available?

## Cost Analysis
What are the licensing costs?
```

**3. Bullet Points**
```markdown
- Evaluate option A
- Evaluate option B
- Compare trade-offs
```

### Distribution Algorithms

**1. Round-Robin**
- Distribute questions sequentially to agents
- Agent 1 gets Q1, Agent 2 gets Q2, etc.
- Wraps around when agents < questions

**2. Balanced**
- Distribute evenly based on question count
- Tries to give each agent equal work
- Handles remainder by giving extras to earlier agents

**3. Grouped**
- Keep related questions together
- Questions under same heading stay together
- Useful for topic-focused research

### Prompt Generation

Each generated prompt includes:
- Agent role and number
- Inquiry context from inquiry_report.json
- Constraints that must be satisfied
- Assigned question(s)
- Output format instructions
- Independence reminder (no consulting other agents)

### Output Modes

**1. Structured Output (default)**
```json
{
  "inquiry_id": "INQ-001",
  "total_agents": 3,
  "algorithm": "round-robin",
  "prompts": [
    {
      "agent_number": 1,
      "questions": ["Question 1", "Question 4"],
      "prompt": "You are Research Agent 1..."
    }
  ]
}
```

**2. File Output**
- Write directly to `research/agent-1.md`, `research/agent-2.md`, etc.
- Creates research directory if needed
- Includes frontmatter with metadata

## Acceptance Criteria

- [ ] Skill can be invoked via `/inquiry-prompts`
- [ ] Parses numbered list format correctly
- [ ] Parses headed section format correctly
- [ ] Parses bullet point format correctly
- [ ] Handles mixed formats in same file
- [ ] Implements round-robin distribution
- [ ] Implements balanced distribution
- [ ] Implements grouped distribution
- [ ] Generates prompts with full context from inquiry_report.json
- [ ] Structured output includes all required fields
- [ ] File output creates properly formatted markdown files
- [ ] Handles edge cases (single question, more agents than questions)
- [ ] Clear error messages for invalid inputs

## Implementation Tasks

### 1. Create Directory Structure
- [ ] Create `skills/inquiry-prompts/`
- [ ] Create `skills/inquiry-prompts/scripts/`

### 2. Implement Core Parser (scripts/generate_prompts.py)
- [ ] QUESTION.md reader
- [ ] Numbered list parser
- [ ] Headed section parser
- [ ] Bullet point parser
- [ ] Format detection logic

### 3. Implement Distribution Algorithms
- [ ] Round-robin distributor
- [ ] Balanced distributor
- [ ] Grouped distributor

### 4. Implement Prompt Generator
- [ ] Context loader (inquiry_report.json)
- [ ] Prompt template
- [ ] Output formatters (JSON and markdown)

### 5. Create SKILL.md
- [ ] Agent instructions
- [ ] Workflow steps
- [ ] Usage examples

### 6. Create README.md
- [ ] Input/output documentation
- [ ] Algorithm explanations
- [ ] Examples

## Usage Examples

### Basic Usage
```bash
# From inquiry directory
/inquiry-prompts

# Specify algorithm
/inquiry-prompts --algorithm balanced

# Write to files
/inquiry-prompts --output files
```

### Via Python Script
```bash
# JSON output
uv run python skills/inquiry-prompts/scripts/generate_prompts.py \
  inquiries/INQ-001-example/

# File output
uv run python skills/inquiry-prompts/scripts/generate_prompts.py \
  inquiries/INQ-001-example/ --output files --algorithm grouped
```

## Related Work Items

- INQ work item type (docs/WORK-ITEM-TYPES.md)
- inquiry_report.schema.json (feature-management/schemas/)

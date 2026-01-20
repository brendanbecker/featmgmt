---
name: inquiry-prompts
description: Generate research agent prompts from INQ QUESTION.md files for Phase 1 deliberation
---
# Skill: Inquiry Prompts Generator

You are a specialized agent for generating research prompts from INQ (Inquiry) work items. Your goal is to parse QUESTION.md files and distribute questions across multiple research agents for Phase 1 independent exploration.

## Capabilities

1. **QUESTION.md Parsing**
   - Parse numbered lists (`1. Question here`)
   - Parse headed sections (`## Section\nQuestion text`)
   - Parse bullet points (`- Question here` or `* Question here`)
   - Handle mixed formats in a single file
   - Extract top-level question and sub-questions

2. **Question Distribution**
   - Round-robin: Distribute sequentially across agents
   - Balanced: Evenly distribute by count
   - Grouped: Keep related questions together by heading

3. **Prompt Generation**
   - Load context from `inquiry_report.json`
   - Include constraints and scope
   - Generate role-specific prompts
   - Ensure independence instructions

## Workflow

### 1. Identify the Inquiry

Determine the INQ directory to process. Options:
- User provides path: `/inquiry-prompts inquiries/INQ-001-example/`
- Current directory contains `inquiry_report.json`
- Search for active inquiries in `inquiries/`

### 2. Parse Input Files

Read and validate:
```bash
uv run python scripts/generate_prompts.py <inquiry_path>
```

The script:
1. Loads `inquiry_report.json` for context
2. Parses `QUESTION.md` to extract questions
3. Returns structured question data

### 3. Select Distribution Algorithm

Choose based on question structure:
- **round-robin** (default): Simple sequential distribution
- **balanced**: When questions have similar complexity
- **grouped**: When questions have clear topic headings

### 4. Generate Prompts

Run with options:
```bash
# JSON output (structured)
uv run python scripts/generate_prompts.py <inquiry_path> --algorithm round-robin

# File output (writes to research/)
uv run python scripts/generate_prompts.py <inquiry_path> --output files --algorithm balanced
```

### 5. Return Results

**Structured Output (JSON)**:
```json
{
  "inquiry_id": "INQ-001",
  "title": "Inquiry Title",
  "total_agents": 3,
  "algorithm": "round-robin",
  "prompts": [
    {
      "agent_number": 1,
      "output_file": "research/agent-1.md",
      "questions": ["Question 1", "Question 4"],
      "prompt": "Full prompt text..."
    }
  ]
}
```

**File Output**:
Creates `research/agent-N.md` files with full prompts.

## Prompt Template

Each generated prompt follows this structure:

```markdown
# Research Agent {N} - Independent Research Report

## Assignment

You are Research Agent {N} of {total} working on **{inquiry_title}**.

### Core Question
{main_question}

### Your Assigned Sub-Questions
{assigned_questions}

## Context

{context_from_inquiry_report}

## Constraints

The following constraints MUST be satisfied by any proposed solution:
{constraints_list}

## Scope

{scope_if_defined}

## Instructions

1. Research your assigned questions independently
2. DO NOT consult or coordinate with other research agents
3. Document your findings thoroughly with evidence
4. Note areas of uncertainty or where more investigation is needed
5. Propose potential approaches with pros/cons
6. Save your report to: `research/agent-{N}.md`

## Output Format

Your research report should include:
- Executive summary of findings
- Detailed analysis per question
- Evidence and sources
- Recommendations (if applicable)
- Open questions or areas needing further exploration
```

## Usage Examples

### Basic Usage
```
/inquiry-prompts
```
Processes the current inquiry directory with default settings.

### With Path
```
/inquiry-prompts inquiries/INQ-001-architecture-decision/
```
Processes the specified inquiry.

### With Options
```
/inquiry-prompts --algorithm grouped --output files
```
Uses grouped distribution and writes directly to research/ files.

## Error Handling

- **Missing inquiry_report.json**: Report error and suggest creating the file
- **Missing QUESTION.md**: Report error and suggest creating the file
- **Invalid JSON**: Report parsing error with line number
- **No questions found**: Warn and suggest checking QUESTION.md format
- **research_agents < 1**: Report invalid configuration

## Integration Points

This skill integrates with:
- **INQ Work Item Type**: Follows Phase 1 research format
- **inquiry_report.json**: Reads context, constraints, research_agents count
- **QUESTION.md**: Parses question structure
- **research/**: Output directory for agent prompts

## Rules

1. **Independence is Critical**: Each agent prompt must emphasize independent work
2. **Preserve Context**: Include all relevant context from inquiry_report.json
3. **Respect Constraints**: Constraints appear in every prompt
4. **Clear Assignment**: Each agent knows exactly which questions to address
5. **Consistent Format**: All prompts follow the same template structure

# Task Breakdown: FEAT-022

**Work Item**: [FEAT-022: Research Agent Prompt Generator](PROMPT.md)
**Status**: Not Started
**Last Updated**: 2026-01-20

## Prerequisites

- [ ] Read and understand PROMPT.md
- [ ] Review PLAN.md and update if needed
- [ ] Review docs/WORK-ITEM-TYPES.md for INQ specification
- [ ] Study sample QUESTION.md files (create if needed)
- [ ] Understand FEAT-021 integration requirements

## Section 1: Skill Infrastructure

- [ ] Create `skills/inquiry-prompts/` directory
- [ ] Create `skills/inquiry-prompts/SKILL.md` with:
  - [ ] Skill metadata
  - [ ] Command syntax
  - [ ] Parameter definitions
  - [ ] Integration instructions
- [ ] Create `skills/inquiry-prompts/README.md`

## Section 2: QUESTION.md Parsing

- [ ] Implement markdown parser for QUESTION.md
- [ ] Extract problem statement section:
  - [ ] Look for `## Problem Statement` heading
  - [ ] Fall back to first section after title
- [ ] Extract research areas - numbered list format:
  - [ ] Detect numbered lists (1. 2. 3.)
  - [ ] Parse area number and content
  - [ ] Handle multi-line area descriptions
- [ ] Extract research areas - headed sections format:
  - [ ] Detect `## Research Area N:` pattern
  - [ ] Extract section content
- [ ] Extract research areas - bulleted format:
  - [ ] Detect bulleted lists
  - [ ] Parse bullet content
- [ ] Implement format auto-detection:
  - [ ] Try each format in order
  - [ ] Use first successful parse
- [ ] Handle edge cases:
  - [ ] No research areas found
  - [ ] Malformed markdown
  - [ ] Empty sections

## Section 3: inquiry_report.json Parsing

- [ ] Implement JSON parser
- [ ] Extract required fields:
  - [ ] `inquiry_id`
  - [ ] `question`
  - [ ] `context`
  - [ ] `constraints` (array)
  - [ ] `research_agents` (number)
- [ ] Extract optional fields:
  - [ ] `scope`
  - [ ] `deadline`
  - [ ] `title`
- [ ] Validate required fields present
- [ ] Provide clear error for missing fields

## Section 4: Distribution Algorithms

- [ ] Implement round-robin distribution:
  - [ ] Assign area i to agent (i % num_agents)
  - [ ] Ensure all areas assigned
- [ ] Implement balanced distribution:
  - [ ] Parse complexity hints from areas
  - [ ] Default complexity if not specified
  - [ ] Sort areas by complexity
  - [ ] Assign to minimize per-agent total
- [ ] Implement grouped distribution:
  - [ ] Parse `[group: X]` annotations
  - [ ] Keep grouped areas together
  - [ ] Balance ungrouped areas
- [ ] Handle edge cases:
  - [ ] More agents than areas (some agents get 0)
  - [ ] Single area (all to agent 1)
  - [ ] Very uneven distribution

## Section 5: Prompt Template

- [ ] Create default prompt template:
  - [ ] Research assignment header
  - [ ] Context section
  - [ ] Assigned areas section
  - [ ] Constraints section
  - [ ] Scope section (if present)
  - [ ] Output requirements section
  - [ ] Important notes section
- [ ] Implement template variable substitution:
  - [ ] `{{inquiry_id}}`
  - [ ] `{{agent_number}}`
  - [ ] `{{total_agents}}`
  - [ ] `{{problem_statement}}`
  - [ ] `{{context}}`
  - [ ] `{{assigned_areas}}`
  - [ ] `{{constraints}}`
  - [ ] `{{scope}}`
- [ ] Format as clean markdown

## Section 6: Prompt Generation

- [ ] Generate prompts for each agent:
  - [ ] Get assigned areas from distribution
  - [ ] Populate template
  - [ ] Clean up formatting
- [ ] Create structured output object:
  ```json
  {
    "inquiry_id": "...",
    "total_agents": N,
    "prompts": [...]
  }
  ```
- [ ] Include metadata per prompt:
  - [ ] Agent number
  - [ ] Assigned area numbers
  - [ ] Full prompt text

## Section 7: Output Handling

- [ ] Return structured object by default
- [ ] Implement `--output-dir` option:
  - [ ] Create prompts/ subdirectory
  - [ ] Write `agent-N-prompt.md` files
  - [ ] Report files created
- [ ] Implement `--format` option:
  - [ ] `json` - JSON object output
  - [ ] `markdown` - concatenated markdown

## Section 8: CLI Interface

- [ ] Define command syntax:
  - [ ] `/inquiry-prompts <ID>`
  - [ ] `--agents N` (override inquiry_report.json)
  - [ ] `--output-dir DIR`
  - [ ] `--distribution round-robin|balanced|grouped`
  - [ ] `--preview`
  - [ ] `--format json|markdown`
- [ ] Implement argument parsing
- [ ] Implement `--preview` mode:
  - [ ] Show distribution without full prompts
  - [ ] List areas per agent
- [ ] Error handling:
  - [ ] Inquiry not found
  - [ ] QUESTION.md not found
  - [ ] Parse failures

## Section 9: Testing

- [ ] Create sample QUESTION.md files:
  - [ ] Numbered list format
  - [ ] Headed sections format
  - [ ] Bulleted format
  - [ ] Mixed format
- [ ] Test area extraction for each format
- [ ] Test distribution algorithms:
  - [ ] Even distribution
  - [ ] Odd number of areas
  - [ ] More agents than areas
- [ ] Test prompt generation:
  - [ ] All variables substituted
  - [ ] Formatting correct
  - [ ] Self-contained prompts
- [ ] Test edge cases:
  - [ ] Single area, multiple agents
  - [ ] Many areas, few agents
  - [ ] Empty sections

## Section 10: Documentation

- [ ] Document QUESTION.md format requirements
- [ ] Document command-line interface
- [ ] Document distribution algorithms
- [ ] Add examples to README
- [ ] Document integration with FEAT-021

## Completion Checklist

- [ ] QUESTION.md parsing works for all formats
- [ ] Distribution algorithms implemented
- [ ] Prompts generated correctly
- [ ] Output options work
- [ ] CLI interface complete
- [ ] Tests pass
- [ ] Documentation complete

---
*Check off tasks as you complete them. Update status field above.*

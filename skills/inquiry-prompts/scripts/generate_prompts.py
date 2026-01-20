#!/usr/bin/env python3
"""
Generate research agent prompts from INQ QUESTION.md files.

This script parses QUESTION.md files with various formats (numbered lists,
headed sections, bullets) and distributes questions across research agents
using different algorithms (round-robin, balanced, grouped).

Usage:
    uv run python generate_prompts.py <inquiry_path> [options]

Options:
    --algorithm   Distribution algorithm: round-robin, balanced, grouped (default: round-robin)
    --output      Output mode: json, files (default: json)
    --agents      Override number of research agents (default: from inquiry_report.json)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Question:
    """Represents a parsed question with optional grouping."""
    text: str
    group: Optional[str] = None  # Heading group for grouped distribution
    source_line: int = 0


@dataclass
class ParsedQuestions:
    """Result of parsing QUESTION.md."""
    main_question: str
    sub_questions: list[Question] = field(default_factory=list)
    format_detected: str = "unknown"


@dataclass
class InquiryContext:
    """Context loaded from inquiry_report.json."""
    inquiry_id: str
    title: str
    question: str
    context: str
    constraints: list[str]
    research_agents: int
    scope: Optional[str] = None
    tags: list[str] = field(default_factory=list)


@dataclass
class AgentPrompt:
    """Generated prompt for a single research agent."""
    agent_number: int
    questions: list[str]
    prompt: str
    output_file: str


def parse_numbered_list(content: str) -> list[Question]:
    """Parse numbered list format: 1. Question text"""
    questions = []
    pattern = r'^(\d+)\.\s+(.+?)(?=\n\d+\.|$)'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    for num, text in matches:
        clean_text = text.strip()
        if clean_text:
            questions.append(Question(text=clean_text, source_line=int(num)))

    return questions


def parse_headed_sections(content: str) -> list[Question]:
    """Parse headed section format: ## Heading\nQuestion text"""
    questions = []

    # Find all ## or ### headings and their content
    # Pattern: ## Heading followed by content until next ## or end
    pattern = r'^(#{2,3})\s+(.+?)$'

    # Split content by headings, keeping the delimiters
    parts = re.split(pattern, content, flags=re.MULTILINE)

    # parts will be: [before_first_heading, '##', 'heading1', content1, '##', 'heading2', content2, ...]
    # Index 0: content before first heading
    # Index 1, 2, 3: first heading (##, heading text, content)
    # Index 4, 5, 6: second heading...

    i = 1  # Skip content before first heading
    while i + 2 < len(parts):
        hash_marks = parts[i]
        heading = parts[i + 1].strip()
        content_after = parts[i + 2] if i + 2 < len(parts) else ""

        # Extract question text from section content
        # Remove any sub-headings and empty lines
        lines = []
        for line in content_after.strip().split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                lines.append(stripped)

        if lines:
            question_text = ' '.join(lines)
            questions.append(Question(
                text=question_text,
                group=heading
            ))

        i += 3

    return questions


def parse_bullet_points(content: str) -> list[Question]:
    """Parse bullet point format: - Question or * Question"""
    questions = []
    pattern = r'^[-*]\s+(.+?)(?=\n[-*]|\n\n|$)'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    line_num = 0
    for text in matches:
        clean_text = text.strip()
        if clean_text:
            line_num += 1
            questions.append(Question(text=clean_text, source_line=line_num))

    return questions


def detect_format(content: str) -> str:
    """Detect the primary format of the QUESTION.md content."""
    # Count format indicators
    numbered_count = len(re.findall(r'^\d+\.', content, re.MULTILINE))
    headed_count = len(re.findall(r'^#{2,3}\s+', content, re.MULTILINE))
    bullet_count = len(re.findall(r'^[-*]\s+', content, re.MULTILINE))

    if headed_count > 0 and headed_count >= numbered_count and headed_count >= bullet_count:
        return "headed"
    elif numbered_count > 0 and numbered_count >= bullet_count:
        return "numbered"
    elif bullet_count > 0:
        return "bullets"
    else:
        return "plain"


def extract_main_question(content: str) -> str:
    """Extract the main question from QUESTION.md (usually the first heading or paragraph)."""
    lines = content.strip().split('\n')

    # Look for # Main heading first
    for line in lines:
        if line.startswith('# ') and not line.startswith('## '):
            return line[2:].strip()

    # Otherwise take first non-empty paragraph before any lists/headings
    paragraph_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if paragraph_lines:
                break
            continue
        if stripped.startswith('#') or stripped.startswith('-') or stripped.startswith('*'):
            break
        if re.match(r'^\d+\.', stripped):
            break
        paragraph_lines.append(stripped)

    return ' '.join(paragraph_lines) if paragraph_lines else "Research the following questions"


def parse_question_md(content: str) -> ParsedQuestions:
    """Parse QUESTION.md content and extract questions."""
    format_detected = detect_format(content)
    main_question = extract_main_question(content)

    if format_detected == "headed":
        sub_questions = parse_headed_sections(content)
    elif format_detected == "numbered":
        sub_questions = parse_numbered_list(content)
    elif format_detected == "bullets":
        sub_questions = parse_bullet_points(content)
    else:
        # Plain text - treat the whole content (minus main question) as one question
        sub_questions = [Question(text=main_question)]

    # If no sub-questions found but we have content, use main question
    if not sub_questions and main_question:
        sub_questions = [Question(text=main_question)]

    return ParsedQuestions(
        main_question=main_question,
        sub_questions=sub_questions,
        format_detected=format_detected
    )


def load_inquiry_context(inquiry_path: Path) -> InquiryContext:
    """Load context from inquiry_report.json."""
    json_path = inquiry_path / "inquiry_report.json"

    if not json_path.exists():
        raise FileNotFoundError(f"inquiry_report.json not found at {json_path}")

    with open(json_path, 'r') as f:
        data = json.load(f)

    return InquiryContext(
        inquiry_id=data.get("inquiry_id", "INQ-000"),
        title=data.get("title", "Unknown Inquiry"),
        question=data.get("question", ""),
        context=data.get("context", ""),
        constraints=data.get("constraints", []),
        research_agents=data.get("research_agents", 3),
        scope=data.get("scope"),
        tags=data.get("tags", [])
    )


def distribute_round_robin(questions: list[Question], num_agents: int) -> list[list[Question]]:
    """Distribute questions using round-robin algorithm."""
    distribution: list[list[Question]] = [[] for _ in range(num_agents)]

    for i, question in enumerate(questions):
        agent_idx = i % num_agents
        distribution[agent_idx].append(question)

    return distribution


def distribute_balanced(questions: list[Question], num_agents: int) -> list[list[Question]]:
    """Distribute questions evenly across agents."""
    distribution: list[list[Question]] = [[] for _ in range(num_agents)]

    if not questions:
        return distribution

    base_count = len(questions) // num_agents
    remainder = len(questions) % num_agents

    idx = 0
    for agent_idx in range(num_agents):
        count = base_count + (1 if agent_idx < remainder else 0)
        for _ in range(count):
            if idx < len(questions):
                distribution[agent_idx].append(questions[idx])
                idx += 1

    return distribution


def distribute_grouped(questions: list[Question], num_agents: int) -> list[list[Question]]:
    """Distribute questions keeping groups together."""
    # Group questions by their group attribute
    groups: dict[Optional[str], list[Question]] = {}
    for q in questions:
        group_key = q.group or "ungrouped"
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(q)

    # Sort groups by size (largest first for better distribution)
    sorted_groups = sorted(groups.values(), key=len, reverse=True)

    # Assign groups to agents using bin-packing approach
    distribution: list[list[Question]] = [[] for _ in range(num_agents)]
    agent_counts = [0] * num_agents

    for group in sorted_groups:
        # Find agent with fewest questions
        min_idx = agent_counts.index(min(agent_counts))
        distribution[min_idx].extend(group)
        agent_counts[min_idx] += len(group)

    return distribution


def generate_prompt_text(
    agent_number: int,
    total_agents: int,
    context: InquiryContext,
    questions: list[Question],
    main_question: str
) -> str:
    """Generate the full prompt text for a research agent."""

    # Format assigned questions
    if len(questions) == 1:
        questions_text = f"- {questions[0].text}"
    else:
        questions_text = "\n".join(f"{i+1}. {q.text}" for i, q in enumerate(questions))

    # Format constraints
    constraints_text = "\n".join(f"- {c}" for c in context.constraints) if context.constraints else "- None specified"

    # Build scope section
    scope_section = f"""
## Scope

{context.scope}
""" if context.scope else ""

    prompt = f"""# Research Agent {agent_number} - Independent Research Report

## Assignment

You are Research Agent {agent_number} of {total_agents} working on **{context.title}**.

### Core Question

{main_question}

### Your Assigned Sub-Questions

{questions_text}

## Context

{context.context}

## Constraints

The following constraints MUST be satisfied by any proposed solution:

{constraints_text}
{scope_section}
## Instructions

1. Research your assigned questions independently
2. **DO NOT** consult or coordinate with other research agents
3. Document your findings thoroughly with evidence
4. Note areas of uncertainty or where more investigation is needed
5. Propose potential approaches with pros/cons for each question
6. Save your report to: `research/agent-{agent_number}.md`

## Output Format

Your research report should include:

### Executive Summary
Brief overview of your key findings (2-3 paragraphs)

### Detailed Analysis

For each assigned question:
- Your findings and analysis
- Evidence and sources
- Potential approaches with pros/cons
- Recommendations

### Open Questions
Areas needing further exploration or clarification

### References
Sources consulted during research

---

**Inquiry ID**: {context.inquiry_id}
**Agent**: {agent_number} of {total_agents}
**Phase**: Research (Phase 1)
"""

    return prompt


def generate_prompts(
    inquiry_path: Path,
    algorithm: str = "round-robin",
    num_agents: Optional[int] = None
) -> dict:
    """Generate research agent prompts for an inquiry."""

    # Load context
    context = load_inquiry_context(inquiry_path)

    # Override agent count if specified
    if num_agents is not None:
        context.research_agents = num_agents

    # Parse QUESTION.md
    question_path = inquiry_path / "QUESTION.md"
    if not question_path.exists():
        raise FileNotFoundError(f"QUESTION.md not found at {question_path}")

    with open(question_path, 'r') as f:
        question_content = f.read()

    parsed = parse_question_md(question_content)

    # Select distribution algorithm
    if algorithm == "round-robin":
        distribution = distribute_round_robin(parsed.sub_questions, context.research_agents)
    elif algorithm == "balanced":
        distribution = distribute_balanced(parsed.sub_questions, context.research_agents)
    elif algorithm == "grouped":
        distribution = distribute_grouped(parsed.sub_questions, context.research_agents)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    # Generate prompts for each agent
    prompts = []
    for agent_idx, questions in enumerate(distribution):
        agent_num = agent_idx + 1

        if not questions:
            # Agent has no questions - give them the main question
            questions = [Question(text=parsed.main_question)]

        prompt_text = generate_prompt_text(
            agent_number=agent_num,
            total_agents=context.research_agents,
            context=context,
            questions=questions,
            main_question=parsed.main_question
        )

        prompts.append(AgentPrompt(
            agent_number=agent_num,
            questions=[q.text for q in questions],
            prompt=prompt_text,
            output_file=f"research/agent-{agent_num}.md"
        ))

    return {
        "inquiry_id": context.inquiry_id,
        "title": context.title,
        "total_agents": context.research_agents,
        "algorithm": algorithm,
        "format_detected": parsed.format_detected,
        "main_question": parsed.main_question,
        "total_questions": len(parsed.sub_questions),
        "prompts": [
            {
                "agent_number": p.agent_number,
                "questions": p.questions,
                "output_file": p.output_file,
                "prompt": p.prompt
            }
            for p in prompts
        ]
    }


def write_prompt_files(inquiry_path: Path, result: dict) -> list[str]:
    """Write prompts to research/agent-N.md files."""
    research_dir = inquiry_path / "research"
    research_dir.mkdir(exist_ok=True)

    written_files = []
    for prompt_data in result["prompts"]:
        output_path = inquiry_path / prompt_data["output_file"]

        # Add frontmatter to the prompt
        content = f"""---
inquiry_id: {result["inquiry_id"]}
agent_number: {prompt_data["agent_number"]}
total_agents: {result["total_agents"]}
algorithm: {result["algorithm"]}
questions_assigned: {len(prompt_data["questions"])}
---

{prompt_data["prompt"]}
"""

        with open(output_path, 'w') as f:
            f.write(content)

        written_files.append(str(output_path))

    return written_files


def main():
    parser = argparse.ArgumentParser(
        description="Generate research agent prompts from INQ QUESTION.md files"
    )
    parser.add_argument(
        "inquiry_path",
        type=Path,
        help="Path to the inquiry directory containing QUESTION.md and inquiry_report.json"
    )
    parser.add_argument(
        "--algorithm",
        choices=["round-robin", "balanced", "grouped"],
        default="round-robin",
        help="Distribution algorithm (default: round-robin)"
    )
    parser.add_argument(
        "--output",
        choices=["json", "files"],
        default="json",
        help="Output mode: json (stdout) or files (write to research/)"
    )
    parser.add_argument(
        "--agents",
        type=int,
        help="Override number of research agents"
    )

    args = parser.parse_args()

    try:
        result = generate_prompts(
            inquiry_path=args.inquiry_path,
            algorithm=args.algorithm,
            num_agents=args.agents
        )

        if args.output == "files":
            written = write_prompt_files(args.inquiry_path, result)
            output = {
                "status": "success",
                "files_written": written,
                "inquiry_id": result["inquiry_id"],
                "total_agents": result["total_agents"],
                "algorithm": result["algorithm"]
            }
            print(json.dumps(output, indent=2))
        else:
            print(json.dumps(result, indent=2))

    except FileNotFoundError as e:
        print(json.dumps({"error": str(e), "status": "error"}), file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}", "status": "error"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e), "status": "error"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

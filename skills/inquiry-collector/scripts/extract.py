#!/usr/bin/env python3
"""Extract structured content from agent research outputs."""

import re
from dataclasses import dataclass, field
from typing import Optional

try:
    from .utils import parse_markdown_sections
except ImportError:
    from utils import parse_markdown_sections


@dataclass
class AgentResearch:
    """Structured research output from an agent."""

    agent_id: str
    raw_content: str
    problem_analysis: str = ""
    approaches_explored: str = ""
    evidence_gathered: str = ""
    key_findings: str = ""
    recommendations: str = ""
    metadata: dict = field(default_factory=dict)

    def is_complete(self) -> bool:
        """Check if essential sections are present."""
        return bool(
            self.problem_analysis
            or self.key_findings
            or self.recommendations
        )

    def completeness_score(self) -> float:
        """Calculate completeness as percentage of filled sections."""
        sections = [
            self.problem_analysis,
            self.approaches_explored,
            self.evidence_gathered,
            self.key_findings,
            self.recommendations,
        ]
        filled = sum(1 for s in sections if s.strip())
        return filled / len(sections)


class ContentExtractor:
    """Extract structured content from various output formats."""

    # Section heading patterns (case-insensitive)
    SECTION_PATTERNS = {
        "problem_analysis": [
            r"problem\s*analysis",
            r"problem\s*statement",
            r"understanding\s*the\s*problem",
            r"problem\s*definition",
            r"context",
        ],
        "approaches_explored": [
            r"approach(?:es)?\s*(?:explored|considered|investigated)?",
            r"method(?:ology|s)?",
            r"investigation",
            r"research\s*(?:approach|method)",
            r"exploration",
        ],
        "evidence_gathered": [
            r"evidence\s*(?:gathered|found|collected)?",
            r"findings?\s*(?:and\s*)?evidence",
            r"data\s*(?:collected|gathered)",
            r"research\s*(?:findings|results)",
            r"observations?",
        ],
        "key_findings": [
            r"key\s*findings?",
            r"main\s*findings?",
            r"findings?",
            r"results?",
            r"conclusions?",
            r"summary",
        ],
        "recommendations": [
            r"recommendations?",
            r"suggestions?",
            r"proposed\s*(?:approach|solution)",
            r"next\s*steps?",
            r"way\s*forward",
        ],
    }

    def __init__(self):
        # Compile patterns for efficiency
        self._compiled_patterns = {}
        for section, patterns in self.SECTION_PATTERNS.items():
            self._compiled_patterns[section] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def extract(self, content: str, agent_id: str) -> AgentResearch:
        """Extract structured research from content.

        Tries multiple extraction strategies:
        1. Explicit section headers
        2. Heuristic paragraph analysis
        3. Raw content preservation
        """
        research = AgentResearch(agent_id=agent_id, raw_content=content)

        # Try section-based extraction first
        sections = parse_markdown_sections(content)
        self._extract_from_sections(sections, research)

        # If minimal content found, try heuristic extraction
        if research.completeness_score() < 0.4:
            self._extract_heuristically(content, research)

        # Extract any metadata
        research.metadata = self._extract_metadata(content)

        return research

    def _extract_from_sections(
        self, sections: dict[str, str], research: AgentResearch
    ) -> None:
        """Extract content by matching section headings."""
        for heading, content in sections.items():
            for field_name, patterns in self._compiled_patterns.items():
                for pattern in patterns:
                    if pattern.search(heading):
                        current = getattr(research, field_name)
                        if not current:
                            setattr(research, field_name, content)
                        break

    def _extract_heuristically(self, content: str, research: AgentResearch) -> None:
        """Extract content using heuristic analysis.

        Looks for paragraph patterns that indicate different section types.
        """
        paragraphs = self._split_paragraphs(content)

        for para in paragraphs:
            para_lower = para.lower()

            # Skip very short paragraphs
            if len(para) < 50:
                continue

            # Problem analysis indicators
            if not research.problem_analysis and any(
                phrase in para_lower
                for phrase in ["the problem is", "the issue", "challenge", "question"]
            ):
                research.problem_analysis = para
                continue

            # Evidence indicators
            if not research.evidence_gathered and any(
                phrase in para_lower
                for phrase in ["found that", "discovered", "evidence shows", "data indicates"]
            ):
                research.evidence_gathered = para
                continue

            # Findings indicators
            if not research.key_findings and any(
                phrase in para_lower
                for phrase in ["conclude", "key finding", "main finding", "in summary"]
            ):
                research.key_findings = para
                continue

            # Recommendation indicators
            if not research.recommendations and any(
                phrase in para_lower
                for phrase in ["recommend", "suggest", "should", "propose"]
            ):
                research.recommendations = para
                continue

    def _split_paragraphs(self, content: str) -> list[str]:
        """Split content into paragraphs."""
        # Split on double newlines
        paragraphs = re.split(r"\n\s*\n", content)
        return [p.strip() for p in paragraphs if p.strip()]

    def _extract_metadata(self, content: str) -> dict:
        """Extract metadata from content (timestamps, agent info, etc.)."""
        metadata = {}

        # Look for timestamp patterns
        timestamp_match = re.search(
            r"(?:completed|timestamp|date):\s*(\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}(?::\d{2})?)?)",
            content,
            re.IGNORECASE,
        )
        if timestamp_match:
            metadata["timestamp"] = timestamp_match.group(1)

        # Look for agent identifier
        agent_match = re.search(
            r"(?:agent|model|assistant):\s*([^\n]+)",
            content,
            re.IGNORECASE,
        )
        if agent_match:
            metadata["agent_identifier"] = agent_match.group(1).strip()

        # Count words for statistics
        words = len(content.split())
        metadata["word_count"] = words

        return metadata


def extract_agent_research(content: str, agent_id: str) -> AgentResearch:
    """Convenience function to extract research from content."""
    extractor = ContentExtractor()
    return extractor.extract(content, agent_id)

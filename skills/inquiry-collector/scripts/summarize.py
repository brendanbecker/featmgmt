#!/usr/bin/env python3
"""Generate summary from collected research reports.

This module analyzes all agent research reports and generates a
SUMMARY.md file that prepares for the synthesis phase.
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    from .extract import AgentResearch
    from .utils import get_timestamp, parse_markdown_sections
except ImportError:
    from extract import AgentResearch
    from utils import get_timestamp, parse_markdown_sections


@dataclass
class ThemeOccurrence:
    """A theme found across multiple agents."""

    theme: str
    agent_ids: list[str] = field(default_factory=list)
    excerpts: list[str] = field(default_factory=list)


@dataclass
class Divergence:
    """A point of divergence between agents."""

    topic: str
    positions: dict[str, list[str]] = field(default_factory=dict)  # position -> agent_ids


@dataclass
class ResearchSummary:
    """Summary of all research reports."""

    inquiry_id: str
    inquiry_title: str
    total_agents: int
    completed_agents: int
    common_themes: list[ThemeOccurrence] = field(default_factory=list)
    agreements: list[ThemeOccurrence] = field(default_factory=list)
    divergences: list[Divergence] = field(default_factory=list)
    synthesis_questions: list[str] = field(default_factory=list)
    agent_summaries: list[dict] = field(default_factory=list)


class Summarizer:
    """Analyze research reports and generate summary."""

    # Keywords that often indicate themes
    THEME_INDICATORS = [
        "important", "key", "critical", "essential", "significant",
        "recommend", "suggest", "should", "must", "need",
        "finding", "conclusion", "result", "evidence",
    ]

    def __init__(self, inquiry_id: str, inquiry_title: str = ""):
        """Initialize summarizer.

        Args:
            inquiry_id: The inquiry ID (e.g., INQ-001)
            inquiry_title: Optional title for the inquiry
        """
        self.inquiry_id = inquiry_id
        self.inquiry_title = inquiry_title
        self.reports: list[AgentResearch] = []

    def add_report(self, report: AgentResearch) -> None:
        """Add a research report to analyze."""
        self.reports.append(report)

    def analyze(self) -> ResearchSummary:
        """Analyze all reports and generate summary."""
        summary = ResearchSummary(
            inquiry_id=self.inquiry_id,
            inquiry_title=self.inquiry_title,
            total_agents=len(self.reports),
            completed_agents=sum(1 for r in self.reports if r.is_complete()),
        )

        # Extract and analyze themes
        summary.common_themes = self._find_common_themes()
        summary.agreements = self._find_agreements()
        summary.divergences = self._find_divergences()
        summary.synthesis_questions = self._generate_synthesis_questions(summary)
        summary.agent_summaries = self._create_agent_summaries()

        return summary

    def _find_common_themes(self) -> list[ThemeOccurrence]:
        """Find themes mentioned by multiple agents."""
        # Extract key phrases from each report
        all_phrases = {}  # phrase -> {agent_id: excerpt}

        for report in self.reports:
            phrases = self._extract_key_phrases(report)
            for phrase, excerpt in phrases:
                if phrase not in all_phrases:
                    all_phrases[phrase] = {}
                all_phrases[phrase][report.agent_id] = excerpt

        # Filter to phrases appearing in multiple reports
        common = []
        for phrase, occurrences in all_phrases.items():
            if len(occurrences) >= 2:  # At least 2 agents
                theme = ThemeOccurrence(
                    theme=phrase,
                    agent_ids=list(occurrences.keys()),
                    excerpts=list(occurrences.values()),
                )
                common.append(theme)

        # Sort by number of occurrences
        common.sort(key=lambda t: len(t.agent_ids), reverse=True)
        return common[:10]  # Top 10 themes

    def _extract_key_phrases(self, report: AgentResearch) -> list[tuple[str, str]]:
        """Extract key phrases from a report.

        Returns list of (phrase, context_excerpt) tuples.
        """
        phrases = []
        content = report.raw_content.lower()

        # Split into sentences
        sentences = re.split(r"[.!?]\s+", content)

        for sentence in sentences:
            # Look for theme indicator keywords
            for indicator in self.THEME_INDICATORS:
                if indicator in sentence:
                    # Extract the key noun phrase
                    key_phrase = self._extract_noun_phrase(sentence, indicator)
                    if key_phrase and len(key_phrase) > 5:
                        phrases.append((key_phrase, sentence[:200]))

        return phrases

    def _extract_noun_phrase(self, sentence: str, indicator: str) -> Optional[str]:
        """Extract noun phrase near an indicator word."""
        # Simple extraction: words after indicator up to punctuation
        pattern = rf"{indicator}\s+(?:that\s+)?(.+?)(?:[,;:]|$)"
        match = re.search(pattern, sentence)
        if match:
            phrase = match.group(1).strip()
            # Clean up
            phrase = re.sub(r"\s+", " ", phrase)
            return phrase[:100]  # Limit length
        return None

    def _find_agreements(self) -> list[ThemeOccurrence]:
        """Find points where agents agree."""
        agreements = []

        # Compare key findings across agents
        findings = {}
        for report in self.reports:
            if report.key_findings:
                # Normalize and compare
                normalized = self._normalize_text(report.key_findings)
                for existing_norm, (theme, agents) in list(findings.items()):
                    similarity = self._text_similarity(normalized, existing_norm)
                    if similarity > 0.3:  # 30% similarity threshold
                        agents.append(report.agent_id)
                        break
                else:
                    # New finding
                    findings[normalized] = (report.key_findings[:200], [report.agent_id])

        # Filter to multi-agent agreements
        for normalized, (original, agents) in findings.items():
            if len(agents) >= 2:
                agreements.append(ThemeOccurrence(
                    theme=original,
                    agent_ids=agents,
                ))

        return agreements

    def _find_divergences(self) -> list[Divergence]:
        """Find points where agents disagree."""
        divergences = []

        # Compare recommendations
        recommendations = {}
        for report in self.reports:
            if report.recommendations:
                # Extract recommendation type
                rec_type = self._categorize_recommendation(report.recommendations)
                if rec_type:
                    if rec_type not in recommendations:
                        recommendations[rec_type] = {}

                    stance = self._extract_stance(report.recommendations)
                    if stance not in recommendations[rec_type]:
                        recommendations[rec_type][stance] = []
                    recommendations[rec_type][stance].append(report.agent_id)

        # Find topics with multiple stances
        for topic, stances in recommendations.items():
            if len(stances) >= 2:
                divergences.append(Divergence(
                    topic=topic,
                    positions=stances,
                ))

        return divergences

    def _categorize_recommendation(self, text: str) -> Optional[str]:
        """Categorize a recommendation into a topic."""
        text_lower = text.lower()

        # Common recommendation categories
        categories = {
            "approach": ["approach", "method", "strategy", "technique"],
            "architecture": ["architecture", "design", "structure", "pattern"],
            "implementation": ["implement", "build", "develop", "create"],
            "tooling": ["tool", "library", "framework", "technology"],
            "process": ["process", "workflow", "procedure", "steps"],
        }

        for category, keywords in categories.items():
            if any(kw in text_lower for kw in keywords):
                return category

        return None

    def _extract_stance(self, text: str) -> str:
        """Extract a brief stance from recommendation text."""
        # Take first sentence or first 100 chars
        sentence = re.split(r"[.!?]", text)[0]
        return sentence[:100].strip()

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple word-based similarity."""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def _generate_synthesis_questions(self, summary: ResearchSummary) -> list[str]:
        """Generate questions for the synthesis phase."""
        questions = []

        # Questions from divergences
        for div in summary.divergences[:5]:
            positions = list(div.positions.keys())
            questions.append(
                f"Regarding {div.topic}: How should we reconcile "
                f"'{positions[0]}' vs '{positions[1]}'?"
            )

        # Questions from themes
        for theme in summary.common_themes[:3]:
            questions.append(
                f"Theme '{theme.theme}' was identified by {len(theme.agent_ids)} agents. "
                "What are the implications for our decision?"
            )

        # Default questions if none generated
        if not questions:
            questions = [
                "What are the key trade-offs between identified approaches?",
                "What evidence most strongly supports each position?",
                "What constraints are most critical to satisfy?",
            ]

        return questions[:7]  # Limit to 7 questions

    def _create_agent_summaries(self) -> list[dict]:
        """Create brief summary for each agent."""
        summaries = []

        for report in self.reports:
            summary = {
                "agent_id": report.agent_id,
                "focus_area": self._identify_focus_area(report),
                "key_insight": self._extract_key_insight(report),
                "unique_contribution": self._identify_unique_contribution(report),
                "completeness": f"{report.completeness_score():.0%}",
            }
            summaries.append(summary)

        return summaries

    def _identify_focus_area(self, report: AgentResearch) -> str:
        """Identify the main focus area of the report."""
        if report.approaches_explored:
            # Extract first approach mentioned
            first_line = report.approaches_explored.split("\n")[0]
            return first_line[:100]
        return "General research"

    def _extract_key_insight(self, report: AgentResearch) -> str:
        """Extract the key insight from the report."""
        if report.key_findings:
            # First sentence of findings
            first_sentence = re.split(r"[.!?]", report.key_findings)[0]
            return first_sentence[:150]
        return "See full report"

    def _identify_unique_contribution(self, report: AgentResearch) -> str:
        """Identify what makes this report unique."""
        if report.recommendations:
            first_rec = re.split(r"[.!?]", report.recommendations)[0]
            return first_rec[:150]
        return "See full report"


def generate_summary_markdown(summary: ResearchSummary) -> str:
    """Generate SUMMARY.md content from summary data."""
    timestamp = get_timestamp()

    lines = [
        "# Research Phase Summary",
        "",
        f"**Inquiry**: {summary.inquiry_id}",
    ]

    if summary.inquiry_title:
        lines.append(f"**Title**: {summary.inquiry_title}")

    lines.extend([
        f"**Completed**: {timestamp}",
        f"**Agents**: {summary.completed_agents}/{summary.total_agents} completed",
        "",
        "## Overview",
        "",
        f"This summary consolidates research from {summary.completed_agents} agents ",
        f"working on {summary.inquiry_id}. The research phase is complete and ",
        "ready for synthesis.",
        "",
    ])

    # Common Themes
    if summary.common_themes:
        lines.extend([
            "## Common Themes",
            "",
        ])
        for theme in summary.common_themes:
            agents_str = ", ".join(theme.agent_ids)
            lines.append(f"- **{theme.theme}** (Agents: {agents_str})")
        lines.append("")

    # Points of Agreement
    if summary.agreements:
        lines.extend([
            "## Points of Agreement",
            "",
            "| Finding | Agents |",
            "|---------|--------|",
        ])
        for agreement in summary.agreements:
            agents_str = ", ".join(agreement.agent_ids)
            finding = agreement.theme.replace("|", "\\|").replace("\n", " ")[:100]
            lines.append(f"| {finding} | {agents_str} |")
        lines.append("")

    # Points of Divergence
    if summary.divergences:
        lines.extend([
            "## Points of Divergence",
            "",
            "| Topic | Positions | Agents |",
            "|-------|-----------|--------|",
        ])
        for div in summary.divergences:
            positions = list(div.positions.keys())
            pos_str = " vs ".join(p[:50] for p in positions[:2])
            agents_by_pos = [", ".join(a) for a in div.positions.values()]
            agents_str = " | ".join(agents_by_pos[:2])
            lines.append(f"| {div.topic} | {pos_str} | {agents_str} |")
        lines.append("")

    # Synthesis Questions
    if summary.synthesis_questions:
        lines.extend([
            "## Key Questions for Synthesis",
            "",
        ])
        for i, question in enumerate(summary.synthesis_questions, 1):
            lines.append(f"{i}. {question}")
        lines.append("")

    # Agent Summary Table
    if summary.agent_summaries:
        lines.extend([
            "## Agent Summary",
            "",
            "| Agent | Focus Area | Key Insight | Completeness |",
            "|-------|------------|-------------|--------------|",
        ])
        for agent in summary.agent_summaries:
            focus = agent["focus_area"].replace("|", "\\|")[:40]
            insight = agent["key_insight"].replace("|", "\\|")[:50]
            lines.append(
                f"| {agent['agent_id']} | {focus} | {insight} | {agent['completeness']} |"
            )
        lines.append("")

    # Next Steps
    lines.extend([
        "## Next Steps",
        "",
        "The inquiry is ready for **Phase 2: Synthesis**. Key areas to address:",
        "",
        "1. Resolve divergent positions through structured debate",
        "2. Integrate common themes into unified understanding",
        "3. Identify concrete decision points",
        "",
        "---",
        f"*Generated by inquiry-collector at {timestamp}*",
    ])

    return "\n".join(lines)

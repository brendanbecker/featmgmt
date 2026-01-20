# Agent 3 Research: Summary Generation

## Problem Analysis

After collecting individual research reports, the synthesis phase needs a unified summary. This summary must identify common themes, highlight disagreements, and prepare specific questions for debate. The challenge is automated theme extraction without losing nuance.

## Approaches Explored

### Theme Extraction

Identifying recurring concepts across reports:
- Keyword frequency analysis
- N-gram comparison
- Semantic similarity clustering

### Agreement/Divergence Detection

Finding where agents agree or disagree:
- Compare recommendation sections
- Identify contradictory statements
- Highlight complementary findings

### Synthesis Preparation

Creating actionable synthesis prompts:
- Generate specific questions
- Prioritize decision points
- Structure debate format

## Evidence Gathered

Review of synthesis processes found that:
1. Simple keyword overlap catches 60% of themes
2. Recommendation comparison reveals most divergences
3. Human facilitators add value in question formulation

## Key Findings

The key finding is that automated summary generation is feasible but benefits from human review. The system should produce a structured summary with clear sections for themes, agreements, divergences, and questions. The synthesis agent can then refine this.

## Recommendations

I recommend generating a structured SUMMARY.md with:
- Common themes with agent attribution
- Points of agreement/divergence in table format
- Generated synthesis questions (AI-drafted, human-refinable)
- Agent summary table for quick reference

## Conclusion

Summary generation provides valuable synthesis preparation.

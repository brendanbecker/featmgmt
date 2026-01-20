# Inquiry Output Collector

Collects and consolidates research outputs from Phase 1 inquiry agents.

## Overview

When running an INQ (Inquiry) work item, multiple research agents work independently to explore the problem space. This skill:

1. Detects when all agents have completed their research
2. Extracts their outputs from ccmux sessions or files
3. Generates standardized `research/agent-N.md` reports
4. Creates a `SUMMARY.md` for the synthesis phase
5. Updates the inquiry status to proceed to Phase 2

## Quick Start

```bash
# After spawning research agents in ccmux sessions tagged with inquiry ID
/inquiry-collect INQ-001 --mode ccmux

# Or for file-based collection
/inquiry-collect INQ-001 --mode file
```

## Collection Modes

### ccmux Mode (Default)

Best for agents running in managed ccmux sessions:
- Finds sessions tagged with the inquiry ID
- Monitors session status for completion
- Extracts output from pane buffers
- Supports real-time status updates

### File Mode

Best for external agents or testing:
- Watches the inquiry's `research/` directory
- Detects completion via markers in files
- Supports pre-existing research files

## Requirements

- Python 3.9+
- For ccmux mode: ccmux MCP tools available
- For file mode: watchdog package (optional, for live watching)

## File Structure

```
skills/inquiry-collector/
├── SKILL.md          # Skill definition
├── README.md         # This file
├── scripts/
│   ├── collect.py         # Main orchestrator
│   ├── ccmux_monitor.py   # ccmux session monitoring
│   ├── file_monitor.py    # File-based monitoring
│   ├── extract.py         # Content extraction
│   ├── summarize.py       # Summary generation
│   └── utils.py           # Shared utilities
└── templates/
    ├── agent-report.md.j2 # Agent report template
    └── summary.md.j2      # Summary template
```

## Generated Outputs

### research/agent-N.md

Standardized research report with sections:
- Problem Analysis
- Approaches Explored
- Evidence Gathered
- Key Findings
- Recommendations

### SUMMARY.md

Cross-agent analysis including:
- Common themes
- Points of agreement/divergence
- Questions for synthesis
- Agent comparison table

## Configuration

The skill reads from `inquiry_report.json`:
- `research_agents`: Number of expected agents
- `phase`: Current inquiry phase
- `constraints`: Non-negotiable requirements

## Error Handling

- **Timeout**: Generates partial report, inquiry remains in research phase
- **Missing agents**: Reports which agents completed vs missing
- **Extraction failure**: Saves raw output for manual review

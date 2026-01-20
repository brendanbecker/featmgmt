# FEAT-023: Inquiry Output Collector Skill

## Overview

Create the `/inquiry-collect` skill that collects and consolidates research outputs from Phase 1 inquiry agents. This skill bridges the gap between independent agent research and the synthesis phase of the inquiry process.

## Problem Statement

When running an INQ (Inquiry) work item with multiple research agents:
1. Each agent works independently in its own ccmux session or writes to separate files
2. There's no automated way to detect when all agents complete
3. Outputs need to be extracted and formatted into standardized `research/agent-N.md` files
4. The inquiry_report.json needs to be updated with completion status
5. A summary needs to be prepared for the synthesis phase

## Acceptance Criteria

### Core Functionality
- [ ] Create `skills/inquiry-collector/SKILL.md` skill definition
- [ ] Support two collection modes:
  - **ccmux mode**: Monitor ccmux sessions tagged for the inquiry
  - **file mode**: Monitor for file creation/completion markers
- [ ] Detect completion of all research agents
- [ ] Extract and validate research outputs
- [ ] Generate standardized `research/agent-N.md` files
- [ ] Update `inquiry_report.json` with phase completion status
- [ ] Generate `SUMMARY.md` with consolidated outline for synthesis

### Completion Detection

**ccmux mode:**
- Use `ccmux_get_tags` to find sessions tagged with inquiry ID
- Use `ccmux_get_status` to check for `complete` or `idle` status
- Use `ccmux_read_pane` to extract output when complete
- Timeout handling for stalled agents

**file mode:**
- Monitor inquiry `research/` directory for new files
- Look for completion markers (e.g., `## Conclusion` section, `---END---` marker)
- Support partial file watching for long-running research

### Output Extraction

From each agent's work, extract:
- Problem analysis
- Approaches explored
- Evidence gathered
- Key findings
- Recommendations

### Generated Files

**research/agent-N.md format:**
```markdown
# Agent N Research Report

**Inquiry**: INQ-XXX
**Agent**: [identifier/model]
**Completed**: [timestamp]

## Problem Analysis
[extracted content]

## Approaches Explored
[extracted content]

## Evidence Gathered
[extracted content]

## Key Findings
[extracted content]

## Recommendations
[extracted content]
```

**SUMMARY.md format:**
```markdown
# Research Summary

**Inquiry**: INQ-XXX
**Phase**: Research Complete
**Agents**: N/N completed
**Generated**: [timestamp]

## Common Themes
[auto-generated from analysis]

## Points of Agreement
[areas where agents converged]

## Points of Divergence
[areas requiring debate]

## Key Questions for Synthesis
[questions to address in Phase 2]

## Agent Contributions
| Agent | Key Finding | Unique Insight |
|-------|-------------|----------------|
| 1 | ... | ... |
| N | ... | ... |
```

## Implementation Tasks

### 1. Create Skill Structure
```bash
skills/inquiry-collector/
├── SKILL.md          # Skill definition
├── README.md         # Usage documentation
├── scripts/
│   ├── collect.py    # Main collection orchestrator
│   ├── ccmux_monitor.py  # ccmux session monitoring
│   ├── file_monitor.py   # File-based monitoring
│   ├── extract.py    # Output extraction logic
│   └── summarize.py  # Summary generation
└── templates/
    ├── agent-report.md.template
    └── summary.md.template
```

### 2. Collection Orchestrator (collect.py)
- Parse inquiry_report.json to get research_agents count
- Determine collection mode from arguments
- Coordinate monitoring and extraction
- Update inquiry status on completion

### 3. ccmux Monitor (ccmux_monitor.py)
- Query sessions with inquiry tag
- Poll for completion status
- Extract final output from panes
- Handle timeouts and errors

### 4. File Monitor (file_monitor.py)
- Watch inquiry research/ directory
- Detect completion markers
- Handle partial writes
- Validate file structure

### 5. Extractor (extract.py)
- Parse agent output format
- Extract structured sections
- Normalize to standard format
- Handle various output styles

### 6. Summarizer (summarize.py)
- Analyze all agent reports
- Identify themes and patterns
- Generate comparison matrix
- Create synthesis prompts

## Usage Examples

### Invoke via skill
```
/inquiry-collect INQ-001 --mode ccmux
/inquiry-collect INQ-001 --mode file
```

### Programmatic invocation
```python
# Via MCP skill invocation
skill: inquiry-collector
args: "INQ-001 --mode ccmux --timeout 300"
```

## Error Handling

- **Partial completion**: Report which agents completed vs pending
- **Extraction failures**: Save raw output, flag for manual review
- **Timeout**: Mark agent as `incomplete` with timeout reason
- **Missing inquiry**: Clear error message with setup instructions

## Dependencies

- ccmux MCP tools (for ccmux mode)
- Python 3.9+
- jq (for JSON manipulation)
- watchdog (for file monitoring)

## Testing

Create test fixtures:
- Sample inquiry_report.json
- Mock agent outputs (various formats)
- ccmux session mocks
- Expected generated files

Test cases:
- All agents complete successfully
- Partial completion with timeout
- Various output formats
- Invalid/corrupted outputs
- Missing inquiry directory

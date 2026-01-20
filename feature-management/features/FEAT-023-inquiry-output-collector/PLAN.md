# FEAT-023 Implementation Plan

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    /inquiry-collect                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   collect   │──│   monitor   │──│      extract        │  │
│  │     .py     │  │   (mode)    │  │        .py          │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         │         ┌──────┴──────┐              │             │
│         │         │             │              │             │
│         │    ccmux_monitor  file_monitor       │             │
│         │         │             │              │             │
│         └─────────┴──────┬──────┴──────────────┘             │
│                          │                                   │
│                   ┌──────▼──────┐                            │
│                   │  summarize  │                            │
│                   │     .py     │                            │
│                   └─────────────┘                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Generated Outputs                         │
├─────────────────────────────────────────────────────────────┤
│  research/agent-1.md                                         │
│  research/agent-2.md                                         │
│  research/agent-N.md                                         │
│  SUMMARY.md                                                  │
│  inquiry_report.json (updated)                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input**: Inquiry ID + collection mode
2. **Discovery**: Find inquiry directory, read config
3. **Monitoring**: Wait for agent completion (ccmux or file)
4. **Extraction**: Parse agent outputs into structured format
5. **Generation**: Create standardized research reports
6. **Summary**: Analyze and create synthesis preparation
7. **Update**: Modify inquiry_report.json status

## Design Decisions

### Why Two Modes?

**ccmux mode** is preferred when:
- Agents run in managed ccmux sessions
- Real-time status monitoring is needed
- Outputs are in terminal buffer

**file mode** is useful when:
- Agents write directly to files
- Working with external agent systems
- Debugging/testing without ccmux

### Output Extraction Strategy

Use pattern-based extraction with fallbacks:
1. Look for explicit section headers (## Problem Analysis, etc.)
2. Fall back to heuristic paragraph analysis
3. If all fails, include raw output with warning

### Completion Detection

**ccmux mode:**
- Check session status for `complete`, `idle`, or `error`
- Verify output contains expected markers
- Timeout after configurable duration

**file mode:**
- Check for completion marker (`## Conclusion` or `---END---`)
- Verify file has minimum expected content
- Watch for file modification cessation

## Implementation Notes

### Error Recovery

- Save raw outputs even on extraction failure
- Allow manual retry of extraction step
- Support partial collection (some agents failed)

### Extensibility

- Abstract monitor interface for new modes
- Configurable extraction patterns
- Plugin system for custom output formats

## File Structure

```
skills/inquiry-collector/
├── SKILL.md                    # Skill invocation definition
├── README.md                   # User documentation
├── scripts/
│   ├── __init__.py
│   ├── collect.py              # Main entry point
│   ├── ccmux_monitor.py        # ccmux MCP integration
│   ├── file_monitor.py         # File watching logic
│   ├── extract.py              # Content extraction
│   ├── summarize.py            # Summary generation
│   └── utils.py                # Shared utilities
└── templates/
    ├── agent-report.md.j2      # Jinja2 template for reports
    └── summary.md.j2           # Jinja2 template for summary
```

# FEAT-020: File Token Limit Linter

**Priority**: P1
**Component**: tooling
**Type**: new_feature
**Estimated Effort**: small
**Business Value**: high

## Overview

Create automated linting tool to detect files exceeding token limits for AI-assisted development workflows. This addresses the practical constraint that Claude's Read tool has a 25k token limit, making files above this threshold impossible to work with effectively.

## Problem Statement

**Discovery from ccmux development:** Large source files create practical problems for AI-assisted development (vibe coding):
- Read tool has 25k token hard limit
- Files exceeding this cannot be read in full context
- Breaks the direction + validation workflow
- Forces manual chunking and context management
- Slows down development velocity

**Current state:**
- No automated detection of oversized files
- Developers discover the problem when Claude fails to read the file
- No visibility into which files are problematic
- No tracking of token counts across codebase

**Real example from ccmux:**
- `mcp/bridge.rs` - 3129 lines (~33k tokens) - Cannot read at all
- `handlers/mcp_bridge.rs` - 2591 lines (~27k tokens) - Cannot read at all
- `ui/app.rs` - 2289 lines (~24k tokens) - Borderline, problematic

## Proposed Solution

Create a Python-based linting tool that:
1. Scans codebase for source files
2. Uses tiktoken to count tokens per file
3. Reports files exceeding configurable thresholds
4. Provides actionable recommendations
5. Optionally integrates with CI/CD for automated checks

### Token-to-Line Ratios (from ccmux analysis)

**Rust:** ~10-11 tokens per line

**Proposed thresholds (configurable):**
- **Hard limit**: 2000 lines (~20k tokens) - definitely refactor
- **Soft limit**: 1500 lines (~15k tokens) - warning
- **Ideal target**: <1000 lines (~10k tokens) - best practice

**Note:** These ratios may vary by language and should be configurable.

## User Stories

### CLI Usage: Check Single File
```bash
# Check a specific file
token-lint check src/main.rs

# Output:
# src/main.rs: 2,345 lines, ~25,800 tokens
# ❌ FAIL: Exceeds hard limit (20k tokens)
# Recommendation: Refactor into smaller modules
```

### CLI Usage: Scan Entire Project
```bash
# Scan all source files in project
token-lint scan

# Output:
# Scanning project...
#
# ❌ HARD LIMIT VIOLATIONS (3 files):
#   src/mcp/bridge.rs: 3,129 lines (~33,419 tokens)
#   src/handlers/mcp_bridge.rs: 2,591 lines (~27,501 tokens)
#
# ⚠️  SOFT LIMIT WARNINGS (2 files):
#   src/ui/app.rs: 2,289 lines (~24,179 tokens)
#   src/state/manager.rs: 1,678 lines (~17,458 tokens)
#
# ✅ PASSED (47 files under limits)
#
# Summary: 5 files need attention
```

### CLI Usage: Language-Specific Configuration
```bash
# Use custom config file
token-lint scan --config .token-lint.toml

# Config file example:
# [thresholds]
# hard_limit = 20000  # tokens
# soft_limit = 15000  # tokens
#
# [language_ratios]
# rust = 10.5
# python = 8.0
# typescript = 9.0
#
# [excludes]
# patterns = ["**/generated/**", "**/vendor/**", "**/*.test.ts"]
```

### CI/CD Integration
```bash
# Exit with error code if violations found
token-lint scan --fail-on-hard-limit

# Or more strict
token-lint scan --fail-on-soft-limit
```

### Generate Refactoring Report
```bash
# Generate detailed report with recommendations
token-lint scan --report report.md

# Output to report.md:
# # Token Limit Analysis Report
#
# ## Hard Limit Violations
#
# ### src/mcp/bridge.rs
# - Lines: 3,129
# - Estimated tokens: ~33,419
# - Recommendation: Split into:
#   - bridge_core.rs (connection handling)
#   - bridge_commands.rs (command processing)
#   - bridge_state.rs (state management)
```

## Implementation Requirements

### Core Functionality
- [ ] Python CLI tool using tiktoken
- [ ] Configurable thresholds (hard limit, soft limit)
- [ ] Language-specific token-per-line ratios
- [ ] File pattern exclusions (generated code, vendor, etc.)
- [ ] Multiple output formats (console, markdown, JSON)

### Token Counting
- [ ] Use tiktoken library for accurate token counting
- [ ] Support for multiple encodings (cl100k_base for GPT-4/Claude)
- [ ] Handle different file types (detect language from extension)
- [ ] Graceful handling of binary files

### Reporting
- [ ] Console output with color coding (red/yellow/green)
- [ ] Summary statistics (total files, violations, passed)
- [ ] Detailed file-by-file breakdown
- [ ] Optional markdown report generation
- [ ] Optional JSON output for CI/CD integration

### Configuration
- [ ] `.token-lint.toml` configuration file support
- [ ] Command-line argument overrides
- [ ] Project-specific configuration
- [ ] Reasonable defaults

## Technical Details

### Technology Stack
- **Python 3.11+** (use uv for execution)
- **tiktoken** for token counting
- **click** for CLI interface
- **toml** for configuration files
- **rich** for colored console output (optional)

### File Structure
```
featmgmt/tools/token-lint/
├── README.md
├── pyproject.toml
├── .token-lint.toml.example
├── src/
│   └── token_lint/
│       ├── __init__.py
│       ├── cli.py          # Click CLI interface
│       ├── scanner.py      # File scanning logic
│       ├── counter.py      # Token counting with tiktoken
│       ├── config.py       # Configuration handling
│       └── reporter.py     # Report generation
└── tests/
    └── test_token_lint.py
```

### Configuration File Format
```toml
# .token-lint.toml
[thresholds]
hard_limit = 20000  # tokens (Read tool limit ~25k, keep buffer)
soft_limit = 15000  # tokens (warning threshold)
ideal_target = 10000  # tokens (best practice)

[language_ratios]
# Estimated tokens per line by language
rust = 10.5
python = 8.0
typescript = 9.0
javascript = 9.0
go = 9.5
default = 9.0  # fallback for unknown languages

[scan]
# File patterns to include
include = ["**/*.rs", "**/*.py", "**/*.ts", "**/*.js", "**/*.go"]

# File patterns to exclude
exclude = [
    "**/generated/**",
    "**/vendor/**",
    "**/node_modules/**",
    "**/*.test.*",
    "**/*.spec.*",
]

[reporting]
# Default output format: console, markdown, json
format = "console"
color = true  # Use colored output in console
```

## Success Criteria

1. **Accurate token counting:** Uses tiktoken to count tokens accurately
2. **Fast scanning:** Can scan large codebases (1000+ files) in <10 seconds
3. **Actionable output:** Clear indication of which files need attention
4. **CI/CD ready:** Exit codes and JSON output for automation
5. **Configurable:** Per-project and per-language customization
6. **Easy to use:** Simple CLI with good defaults

## Out of Scope

- Automatic refactoring (just detection and reporting)
- IDE integration (future enhancement)
- Real-time monitoring (future enhancement)
- Git commit hooks (future enhancement)
- Multi-language token counting in same file (use heuristics)

## Related Features

- None (new standalone tool)

## Related Documentation

- [[File Token Limits for AI Development]] - Obsidian note with context
- [[Vibe Coding]] - AI-assisted development paradigm
- [[ccmux]] - Project where this constraint was discovered

## Open Questions

1. Should we auto-detect language from file extension or require configuration?
2. Should we include a "fix" command that suggests file splits?
3. Should we track token counts over time (historical data)?
4. Should we have pre-commit hook support out of the box?
5. What's the best way to handle multi-language projects with different ratios?

## Next Steps

1. Create Python project structure with uv
2. Implement core token counting with tiktoken
3. Build CLI with click
4. Add configuration file support
5. Test on ccmux codebase
6. Document usage and integration patterns

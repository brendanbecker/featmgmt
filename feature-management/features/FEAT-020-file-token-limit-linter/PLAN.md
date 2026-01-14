# FEAT-020 Implementation Plan: File Token Limit Linter

## Overview

Build Python-based CLI tool to detect files exceeding token limits for AI-assisted development. Uses tiktoken for accurate token counting and provides CI/CD integration.

## Technology Decisions

### Core Stack
- **Python 3.11+** via uv (per user's global CLAUDE.md)
- **tiktoken** - OpenAI's official tokenizer (same encoding Claude uses)
- **click** - CLI framework (battle-tested, great UX)
- **tomli** - TOML parsing (Python 3.11+ built-in tomllib)
- **rich** (optional) - Colored console output (nice-to-have)

### Project Structure
Create as standalone tool in featmgmt/tools/token-lint/:
```
featmgmt/tools/token-lint/
├── README.md
├── pyproject.toml           # uv-compatible project definition
├── .token-lint.toml.example # Example configuration
├── src/
│   └── token_lint/
│       ├── __init__.py
│       ├── cli.py           # Click CLI interface
│       ├── scanner.py       # File discovery and filtering
│       ├── counter.py       # Token counting with tiktoken
│       ├── config.py        # Configuration management
│       └── reporter.py      # Output formatting (console, markdown, JSON)
└── tests/
    ├── test_counter.py
    ├── test_scanner.py
    └── fixtures/            # Test files with known token counts
```

## Implementation Phases

### Phase 1: Core Token Counting (MVP)
**Goal:** Count tokens in a single file accurately

**Tasks:**
1. Set up Python project with uv
   - Create pyproject.toml with dependencies
   - Configure for `uv run token-lint` execution

2. Implement counter.py
   - Use tiktoken with cl100k_base encoding (GPT-4/Claude)
   - Handle file reading with proper encoding
   - Return token count and line count

3. Create simple CLI (cli.py)
   - Single command: `token-lint check <file>`
   - Output: filename, lines, tokens, status

4. Test on ccmux files
   - Verify counts match expectations (~10-11 tokens/line for Rust)
   - Test with known problematic files

**Output:** Working token counter for individual files

### Phase 2: Scanning & Thresholds
**Goal:** Scan entire codebase and apply thresholds

**Tasks:**
1. Implement scanner.py
   - Recursive directory traversal
   - File pattern matching (glob)
   - Exclusion patterns (node_modules, vendor, etc.)

2. Add threshold checking
   - Hard limit: 20k tokens
   - Soft limit: 15k tokens
   - Categorize files by status

3. Enhance CLI
   - Add `token-lint scan` command
   - Display summary (violations, warnings, passed)
   - Color-coded output (red/yellow/green)

4. Test on full codebase
   - Run on ccmux project
   - Verify all problematic files detected
   - Check performance on large codebases

**Output:** Full codebase scanner with threshold detection

### Phase 3: Configuration Support
**Goal:** Make thresholds and language ratios configurable

**Tasks:**
1. Implement config.py
   - Read .token-lint.toml from project root
   - Support command-line overrides
   - Provide sensible defaults

2. Add language-specific ratios
   - Rust: 10.5 tokens/line
   - Python: 8.0 tokens/line
   - TypeScript: 9.0 tokens/line
   - Default: 9.0 tokens/line

3. Support exclude patterns
   - Generated code
   - Vendor/node_modules
   - Test files (optional)

4. Create example config
   - .token-lint.toml.example
   - Document all options

**Output:** Fully configurable tool with per-project settings

### Phase 4: Reporting & CI/CD
**Goal:** Generate reports and integrate with automation

**Tasks:**
1. Implement reporter.py
   - Console format (current)
   - Markdown report format
   - JSON output for CI/CD

2. Add CLI options
   - `--report <file>` - Generate markdown report
   - `--json` - Output JSON
   - `--fail-on-hard-limit` - Exit code for CI/CD
   - `--fail-on-soft-limit` - Stricter CI/CD mode

3. Generate detailed reports
   - File-by-file breakdown
   - Refactoring recommendations
   - Trending over time (future)

4. Document CI/CD integration
   - GitHub Actions example
   - GitLab CI example
   - Pre-commit hook example (optional)

**Output:** Production-ready tool with CI/CD integration

## Configuration File Design

### .token-lint.toml
```toml
[thresholds]
# Token limits (Read tool limit is ~25k, keep buffer)
hard_limit = 20000      # Must refactor
soft_limit = 15000      # Should consider refactoring
ideal_target = 10000    # Best practice

[language_ratios]
# Estimated tokens per line by language
# Based on empirical analysis (ccmux for Rust)
rust = 10.5
python = 8.0
typescript = 9.0
javascript = 9.0
go = 9.5
java = 10.0
default = 9.0  # fallback

[scan]
# Which files to check
include = [
    "**/*.rs",
    "**/*.py",
    "**/*.ts",
    "**/*.js",
    "**/*.go",
    "**/*.java",
]

# What to skip
exclude = [
    "**/generated/**",
    "**/vendor/**",
    "**/node_modules/**",
    "**/.git/**",
    "**/target/**",
    "**/dist/**",
    "**/*.test.*",      # Optional: skip tests
    "**/*.spec.*",      # Optional: skip specs
]

[reporting]
format = "console"  # console, markdown, json
color = true        # Colored output
verbose = false     # Show all files or just violations
```

## CLI Interface Design

### Commands

```bash
# Check single file
token-lint check <file>
  Output: filename, lines, tokens, status (pass/warn/fail)

# Scan project
token-lint scan [directory]
  Output: Summary with violations, warnings, passed counts
  Default: Scan current directory

# Generate report
token-lint scan --report report.md
  Output: Detailed markdown report with recommendations

# CI/CD mode
token-lint scan --fail-on-hard-limit  # Exit 1 if any hard limit violations
token-lint scan --fail-on-soft-limit  # Exit 1 if any violations

# JSON output
token-lint scan --json
  Output: Machine-readable JSON for tooling integration

# Use custom config
token-lint scan --config .token-lint.toml

# Verbose output
token-lint scan --verbose
  Output: Show all files, not just violations
```

### Output Examples

**Console (default):**
```
Scanning project...

❌ HARD LIMIT VIOLATIONS (2 files):
  src/mcp/bridge.rs
    Lines: 3,129 | Tokens: ~33,419 | Exceeds limit by 13,419 tokens

  src/handlers/mcp_bridge.rs
    Lines: 2,591 | Tokens: ~27,501 | Exceeds limit by 7,501 tokens

⚠️  SOFT LIMIT WARNINGS (1 file):
  src/ui/app.rs
    Lines: 2,289 | Tokens: ~24,179 | Approaching limit

✅ PASSED (47 files under limits)

Summary:
  Total files: 50
  Hard violations: 2
  Soft warnings: 1
  Passed: 47

Recommendation: Refactor 2 files to stay under hard limit (20k tokens)
```

**Markdown report:**
```markdown
# Token Limit Analysis Report

Generated: 2026-01-13 10:30:00

## Summary

- **Total files scanned:** 50
- **Hard limit violations:** 2
- **Soft limit warnings:** 1
- **Files passed:** 47

## Hard Limit Violations (>20k tokens)

### src/mcp/bridge.rs
- **Lines:** 3,129
- **Estimated tokens:** ~33,419
- **Over limit by:** 13,419 tokens
- **Recommendation:** Split into multiple modules:
  - `bridge_core.rs` - Core connection handling
  - `bridge_commands.rs` - Command processing
  - `bridge_state.rs` - State management

### src/handlers/mcp_bridge.rs
- **Lines:** 2,591
- **Estimated tokens:** ~27,501
- **Over limit by:** 7,501 tokens
- **Recommendation:** Extract handler logic into separate files

## Soft Limit Warnings (15k-20k tokens)

### src/ui/app.rs
- **Lines:** 2,289
- **Estimated tokens:** ~24,179
- **Status:** Approaching hard limit
- **Recommendation:** Consider refactoring before it becomes problematic
```

**JSON output:**
```json
{
  "summary": {
    "total_files": 50,
    "hard_violations": 2,
    "soft_warnings": 1,
    "passed": 47
  },
  "violations": {
    "hard": [
      {
        "path": "src/mcp/bridge.rs",
        "lines": 3129,
        "tokens": 33419,
        "over_limit_by": 13419
      }
    ],
    "soft": [
      {
        "path": "src/ui/app.rs",
        "lines": 2289,
        "tokens": 24179,
        "over_limit_by": 4179
      }
    ]
  }
}
```

## Testing Strategy

### Unit Tests
1. **counter.py tests**
   - Test known files with expected token counts
   - Test different file encodings (UTF-8, ASCII)
   - Test error handling (binary files, permission errors)

2. **scanner.py tests**
   - Test file discovery with include/exclude patterns
   - Test recursive directory traversal
   - Test filtering logic

3. **config.py tests**
   - Test TOML parsing
   - Test default values
   - Test command-line overrides
   - Test validation

### Integration Tests
1. **Full scan tests**
   - Create fixture directory with known files
   - Verify correct categorization (pass/warn/fail)
   - Test different output formats

2. **CLI tests**
   - Test all commands with various options
   - Test exit codes
   - Test error messages

### Real-world Testing
1. Run on ccmux project
   - Verify known violations detected
   - Check performance
   - Validate token counts

2. Run on other projects
   - Python projects
   - TypeScript projects
   - Mixed-language projects

## Performance Considerations

### Optimization Strategies
1. **Lazy loading:** Only load tiktoken when needed
2. **Parallel processing:** Use multiprocessing for large codebases (future)
3. **Caching:** Cache token counts (future enhancement)
4. **Smart scanning:** Skip obviously large files early (future)

### Performance Targets
- Scan 100 files: <5 seconds
- Scan 1000 files: <30 seconds
- Minimal memory usage (<100MB for typical projects)

## Deployment & Usage

### Installation
```bash
# In project root
cd ~/projects/tools/featmgmt/tools/token-lint
uv sync

# Run directly
uv run token-lint scan

# Or install globally (optional)
uv tool install .
```

### Initial Setup in Project
```bash
# Copy example config to project
cp .token-lint.toml.example /path/to/project/.token-lint.toml

# Edit thresholds for project
vim /path/to/project/.token-lint.toml

# Run scan
cd /path/to/project
uv run token-lint scan
```

### CI/CD Integration
```yaml
# GitHub Actions example
name: Token Limit Check

on: [push, pull_request]

jobs:
  token-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Run token-lint
        run: |
          uv run token-lint scan --fail-on-hard-limit
```

## Future Enhancements (Out of Scope for MVP)

1. **Auto-fix suggestions:** Recommend specific refactoring splits
2. **Historical tracking:** Track token counts over time
3. **Git integration:** Show token count changes in PRs
4. **IDE plugins:** VSCode/IntelliJ extensions
5. **Pre-commit hooks:** Automatic checking before commit
6. **Watch mode:** Real-time monitoring during development
7. **Multi-language detection:** Auto-detect language without extension

## Success Metrics

1. **Accuracy:** Token counts within 5% of actual (tiktoken is authoritative)
2. **Speed:** Scan ccmux (50 files) in <5 seconds
3. **Usability:** Clear, actionable output
4. **Reliability:** No crashes on valid projects
5. **Adoption:** Used in ccmux and other projects within 2 weeks

## Dependencies

- tiktoken (token counting)
- click (CLI framework)
- tomli or tomllib (TOML parsing)
- rich (optional, colored output)
- pytest (testing)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Token counts inaccurate | High | Use tiktoken (authoritative), validate on known files |
| Too slow on large projects | Medium | Optimize file I/O, consider parallel processing |
| Configuration too complex | Low | Provide good defaults, clear examples |
| Language detection wrong | Low | Allow manual override, fallback to default ratio |

## Open Questions

1. **Auto-language detection:** Use file extension or content sniffing?
   - **Decision:** Start with extension, add content detection later if needed

2. **Pre-commit hooks:** Include out of the box?
   - **Decision:** Document but don't include, let users opt-in

3. **Real-time monitoring:** Watch mode for development?
   - **Decision:** Future enhancement, not MVP

4. **Historical data:** Track changes over time?
   - **Decision:** Future enhancement, not MVP

## Next Steps

1. Create Python project structure with uv
2. Implement Phase 1 (core token counting)
3. Test on ccmux files to validate
4. Implement remaining phases
5. Document usage and integration
6. Update [[File Token Limits for AI Development]] note with tool reference

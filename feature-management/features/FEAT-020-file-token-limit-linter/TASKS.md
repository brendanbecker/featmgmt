# FEAT-020 Tasks: File Token Limit Linter

## Status: Not Started

**Created:** 2026-01-13
**Priority:** P1
**Estimated Effort:** Small (1-2 days)

---

## Phase 1: Core Token Counting (MVP)

### TASK-001: Set up Python project with uv
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min

**Description:**
Create Python project structure with uv-compatible configuration.

**Acceptance Criteria:**
- [ ] Create directory: `~/projects/tools/featmgmt/tools/token-lint/`
- [ ] Create `pyproject.toml` with project metadata
- [ ] Add dependencies: tiktoken, click
- [ ] Create src/token_lint/ package structure
- [ ] Verify `uv run python -m token_lint` works

**Files to Create:**
- `pyproject.toml`
- `src/token_lint/__init__.py`
- `README.md`

---

### TASK-002: Implement token counting with tiktoken
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 1 hour
**Depends On:** TASK-001

**Description:**
Create counter.py module that uses tiktoken to count tokens in a file.

**Acceptance Criteria:**
- [ ] Implement `count_tokens(file_path: str) -> dict` function
- [ ] Use tiktoken with cl100k_base encoding
- [ ] Return: tokens, lines, path
- [ ] Handle file encoding properly (UTF-8 default)
- [ ] Handle errors gracefully (file not found, binary files, etc.)
- [ ] Test on ccmux Rust files

**Files to Create:**
- `src/token_lint/counter.py`

**Test Cases:**
- Known Rust file: 100 lines should be ~1000-1100 tokens
- Python file: 100 lines should be ~800 tokens
- Binary file: Should skip or error gracefully
- Non-existent file: Should raise clear error

---

### TASK-003: Create simple CLI with check command
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 1 hour
**Depends On:** TASK-002

**Description:**
Build CLI using click framework with single `check` command.

**Acceptance Criteria:**
- [ ] Create cli.py with click
- [ ] Implement `token-lint check <file>` command
- [ ] Display: filename, lines, tokens
- [ ] Show status: PASS/WARN/FAIL based on hardcoded thresholds
- [ ] Proper error handling and user feedback
- [ ] Make executable: `uv run token-lint check <file>`

**Files to Create:**
- `src/token_lint/cli.py`
- Update `pyproject.toml` with scripts entry point

**Command Output Example:**
```
$ uv run token-lint check src/main.rs
src/main.rs
  Lines: 1,234
  Tokens: 13,574
  Status: ✅ PASS (under 15k soft limit)
```

---

### TASK-004: Test on ccmux files
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min
**Depends On:** TASK-003

**Description:**
Validate token counting accuracy on real ccmux files.

**Acceptance Criteria:**
- [ ] Test on `ccmux/src/mcp/bridge.rs` (should be ~33k tokens)
- [ ] Test on `ccmux/src/handlers/mcp_bridge.rs` (should be ~27k tokens)
- [ ] Test on `ccmux/src/ui/app.rs` (should be ~24k tokens)
- [ ] Verify ~10-11 tokens/line ratio for Rust
- [ ] Document findings

**Expected Results:**
- bridge.rs: 3129 lines, ~33,419 tokens (FAIL)
- mcp_bridge.rs: 2591 lines, ~27,501 tokens (FAIL)
- app.rs: 2289 lines, ~24,179 tokens (WARN)

---

## Phase 2: Scanning & Thresholds

### TASK-005: Implement file scanner
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 1 hour
**Depends On:** TASK-004

**Description:**
Create scanner.py to discover and filter files in a project.

**Acceptance Criteria:**
- [ ] Implement `scan_directory(path, include, exclude)` function
- [ ] Recursive directory traversal
- [ ] Support glob patterns for include/exclude
- [ ] Default includes: *.rs, *.py, *.ts, *.js, *.go
- [ ] Default excludes: node_modules, vendor, .git, target
- [ ] Return list of file paths to check

**Files to Create:**
- `src/token_lint/scanner.py`

**Test Cases:**
- Scan ccmux project, verify all .rs files found
- Verify node_modules excluded
- Verify .git excluded
- Test custom include/exclude patterns

---

### TASK-006: Add threshold checking logic
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min
**Depends On:** TASK-005

**Description:**
Categorize files by token count: pass, soft warning, hard violation.

**Acceptance Criteria:**
- [ ] Define thresholds: hard=20k, soft=15k
- [ ] Categorize files into: passed, soft_warnings, hard_violations
- [ ] Calculate "over limit by" for violations
- [ ] Add threshold constants (will be configurable later)

**Update Files:**
- `src/token_lint/counter.py` - Add threshold checking

---

### TASK-007: Implement scan command
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 1.5 hours
**Depends On:** TASK-006

**Description:**
Add `scan` command to CLI that checks entire project.

**Acceptance Criteria:**
- [ ] Add `token-lint scan [directory]` command
- [ ] Default to current directory
- [ ] Display summary: violations, warnings, passed
- [ ] Color-coded output: red (fail), yellow (warn), green (pass)
- [ ] Show file details for violations and warnings
- [ ] Show total file count
- [ ] Exit code: 0 if no hard violations, 1 if hard violations

**Update Files:**
- `src/token_lint/cli.py`

**Command Output Example:**
```
$ uv run token-lint scan

Scanning project...

❌ HARD LIMIT VIOLATIONS (2 files):
  src/mcp/bridge.rs: 3,129 lines, ~33,419 tokens
  src/handlers/mcp_bridge.rs: 2,591 lines, ~27,501 tokens

⚠️  SOFT LIMIT WARNINGS (1 file):
  src/ui/app.rs: 2,289 lines, ~24,179 tokens

✅ PASSED (47 files under limits)

Summary: 2 hard violations, 1 soft warning, 47 passed
```

---

### TASK-008: Test full codebase scan
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min
**Depends On:** TASK-007

**Description:**
Run scanner on ccmux and verify all problematic files detected.

**Acceptance Criteria:**
- [ ] Scan entire ccmux project
- [ ] Verify all known violations found (bridge.rs, mcp_bridge.rs)
- [ ] Verify app.rs shows as warning
- [ ] Check scan performance (<5 seconds for ~50 files)
- [ ] Verify no false positives

---

## Phase 3: Configuration Support

### TASK-009: Implement configuration file loading
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 1 hour
**Depends On:** TASK-008

**Description:**
Add .token-lint.toml configuration file support.

**Acceptance Criteria:**
- [ ] Create config.py module
- [ ] Load .token-lint.toml from project root
- [ ] Support thresholds section
- [ ] Support language_ratios section
- [ ] Support scan.include and scan.exclude sections
- [ ] Provide sensible defaults if no config file
- [ ] Handle missing or invalid config gracefully

**Files to Create:**
- `src/token_lint/config.py`
- `.token-lint.toml.example`

**Dependencies to Add:**
- tomli (Python <3.11) or use tomllib (Python 3.11+)

---

### TASK-010: Add language-specific token ratios
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min
**Depends On:** TASK-009

**Description:**
Support different tokens-per-line ratios by file extension.

**Acceptance Criteria:**
- [ ] Detect language from file extension
- [ ] Apply language-specific ratio for estimates
- [ ] Default ratios: rust=10.5, python=8.0, typescript=9.0, go=9.5, default=9.0
- [ ] Allow config override of ratios
- [ ] Display ratio used in verbose output

**Update Files:**
- `src/token_lint/counter.py`
- `src/token_lint/config.py`

---

### TASK-011: Add CLI config options
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min
**Depends On:** TASK-010

**Description:**
Add command-line options to override config file settings.

**Acceptance Criteria:**
- [ ] Add `--config <file>` option to specify custom config
- [ ] Add `--hard-limit <int>` to override hard limit
- [ ] Add `--soft-limit <int>` to override soft limit
- [ ] Add `--exclude <pattern>` to add exclusion patterns
- [ ] Command-line options take precedence over config file

**Update Files:**
- `src/token_lint/cli.py`

---

### TASK-012: Create example configuration
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min
**Depends On:** TASK-011

**Description:**
Document configuration options with comprehensive example.

**Acceptance Criteria:**
- [ ] Create .token-lint.toml.example with all options
- [ ] Add comments explaining each setting
- [ ] Include examples for different use cases
- [ ] Document in README.md

**Files to Update:**
- `.token-lint.toml.example`
- `README.md`

---

## Phase 4: Reporting & CI/CD

### TASK-013: Implement markdown report generation
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 1 hour
**Depends On:** TASK-012

**Description:**
Add markdown report output format with detailed recommendations.

**Acceptance Criteria:**
- [ ] Create reporter.py module
- [ ] Implement markdown report generation
- [ ] Include summary statistics
- [ ] List all violations with details
- [ ] Suggest refactoring strategies (future: make smart)
- [ ] Add `--report <file>` CLI option

**Files to Create:**
- `src/token_lint/reporter.py`

**Update Files:**
- `src/token_lint/cli.py`

---

### TASK-014: Add JSON output format
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min
**Depends On:** TASK-013

**Description:**
Add JSON output for CI/CD integration.

**Acceptance Criteria:**
- [ ] Add `--json` CLI option
- [ ] Output structured JSON with summary and violations
- [ ] Include all relevant data: paths, lines, tokens, over_limit_by
- [ ] Valid JSON format
- [ ] Exit code still reflects pass/fail status

**Update Files:**
- `src/token_lint/reporter.py`
- `src/token_lint/cli.py`

---

### TASK-015: Add CI/CD failure modes
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min
**Depends On:** TASK-014

**Description:**
Add options to control exit codes for CI/CD pipelines.

**Acceptance Criteria:**
- [ ] Add `--fail-on-hard-limit` flag (exit 1 if hard violations)
- [ ] Add `--fail-on-soft-limit` flag (exit 1 if any violations)
- [ ] Default: exit 0 (report only)
- [ ] Clear error message when failing
- [ ] Document exit codes in README

**Update Files:**
- `src/token_lint/cli.py`
- `README.md`

---

### TASK-016: Document CI/CD integration
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min
**Depends On:** TASK-015

**Description:**
Provide examples for integrating with CI/CD systems.

**Acceptance Criteria:**
- [ ] GitHub Actions example in README
- [ ] GitLab CI example in README
- [ ] Pre-commit hook example (optional)
- [ ] Document exit codes and usage patterns
- [ ] Add troubleshooting section

**Update Files:**
- `README.md`

---

## Testing & Documentation

### TASK-017: Write unit tests
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 2 hours
**Depends On:** TASK-016

**Description:**
Create comprehensive unit test suite.

**Acceptance Criteria:**
- [ ] Test counter.py: token counting, thresholds, error handling
- [ ] Test scanner.py: file discovery, include/exclude patterns
- [ ] Test config.py: TOML parsing, defaults, overrides
- [ ] Test reporter.py: console, markdown, JSON outputs
- [ ] Create test fixtures with known token counts
- [ ] Achieve >80% code coverage

**Files to Create:**
- `tests/test_counter.py`
- `tests/test_scanner.py`
- `tests/test_config.py`
- `tests/test_reporter.py`
- `tests/fixtures/` (test files)

**Dependencies to Add:**
- pytest

---

### TASK-018: Write comprehensive README
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 1 hour
**Depends On:** TASK-017

**Description:**
Document installation, usage, configuration, and integration.

**Acceptance Criteria:**
- [ ] Installation instructions (uv)
- [ ] Quick start guide
- [ ] Command reference (check, scan)
- [ ] Configuration guide (.token-lint.toml)
- [ ] CI/CD integration examples
- [ ] Troubleshooting section
- [ ] Background (why token limits matter)

**Files to Update:**
- `README.md`

---

### TASK-019: Test on multiple projects
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 1 hour
**Depends On:** TASK-018

**Description:**
Validate tool works on different project types.

**Acceptance Criteria:**
- [ ] Test on ccmux (Rust)
- [ ] Test on yc-jobs (Python)
- [ ] Test on a TypeScript project
- [ ] Test on mixed-language project
- [ ] Verify performance on large project (1000+ files)
- [ ] Document any issues found

---

## Deployment

### TASK-020: Package and deploy
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 30 min
**Depends On:** TASK-019

**Description:**
Make tool ready for use in other projects.

**Acceptance Criteria:**
- [ ] Verify `uv run token-lint` works from any directory
- [ ] Test installation with `uv tool install`
- [ ] Add tool to featmgmt tools/ directory
- [ ] Update featmgmt README with tool reference
- [ ] Tag initial release (v0.1.0)

---

### TASK-021: Update Obsidian note
**Status:** Not Started
**Assignee:** Unassigned
**Estimated:** 15 min
**Depends On:** TASK-020

**Description:**
Update File Token Limits note with FEAT-020 reference.

**Acceptance Criteria:**
- [ ] Add FEAT-020 reference to "Action Items" section
- [ ] Link to tool location
- [ ] Add usage example
- [ ] Update status to "Implemented"

**Files to Update:**
- `~/projects/personal/beckerobsidian/vault/File Token Limits for AI Development.md`

---

## Summary

**Total Tasks:** 21
**Estimated Total Time:** 1-2 days

**Dependencies:**
- Phase 1 (Tasks 1-4): Core MVP
- Phase 2 (Tasks 5-8): Scanning capability
- Phase 3 (Tasks 9-12): Configuration
- Phase 4 (Tasks 13-16): Reporting & CI/CD
- Testing (Tasks 17-19): Quality assurance
- Deployment (Tasks 20-21): Release

**Quick Start Path (Minimum Viable):**
For fastest MVP to test the concept:
1. TASK-001: Set up project
2. TASK-002: Token counting
3. TASK-003: Simple CLI
4. TASK-004: Test on ccmux

This gives working token counter in ~3 hours.

**Full Feature Path:**
All 21 tasks for production-ready tool with CI/CD integration.

---

## Notes

- Use `uv run python` per user's CLAUDE.md global instructions
- All Python operations via uv (not bare python)
- Test thoroughly on ccmux first (known violations)
- Keep tool simple and focused (just detection, not auto-fix)
- Optimize for speed (developers will run frequently)

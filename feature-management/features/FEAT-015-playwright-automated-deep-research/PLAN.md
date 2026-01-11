# Implementation Plan: FEAT-015

**Work Item**: [FEAT-015: Playwright-Automated Deep Research for Stage 2](PROMPT.md)
**Component**: automation
**Priority**: P1
**Created**: 2026-01-10

## Overview

Automate Stage 2 (Deep Research) of the Context Engineering methodology using Playwright browser automation. This eliminates 15-30 minutes of manual browser work per research session.

## Architecture Decisions

### Core Architecture

- **Approach**: Playwright-based browser automation with MCP integration
- **Session Management**: Persistent browser contexts stored per-platform
- **Execution Model**: Parallel execution across 3 browser tabs/contexts
- **Output Format**: Markdown files with metadata JSON

### Key Design Choices

1. **Persistent Sessions over Fresh Auth**
   - Rationale: Avoids MFA/CAPTCHA on each run
   - Trade-off: Requires manual initial auth setup
   - Mitigation: Clear session refresh workflow

2. **Parallel Execution**
   - Rationale: All 3 platforms can run simultaneously (5-10 min each)
   - Trade-off: Higher resource usage
   - Mitigation: Configurable concurrency, sequential fallback

3. **Selector-based UI Navigation**
   - Rationale: Direct, efficient, predictable
   - Trade-off: Brittle to UI changes
   - Mitigation: Centralized selector config, fallback selectors, easy updates

4. **Polling-based Completion Detection**
   - Rationale: Works across all platforms
   - Trade-off: Not as efficient as event-based
   - Mitigation: Configurable poll intervals, smart detection

## Affected Components

| Component | Type of Change | Risk Level |
|-----------|----------------|------------|
| New: playwright-research module | Primary implementation | Medium |
| New: session management | Storage and auth flow | Medium |
| New: platform adapters (3) | Platform-specific logic | High |
| Integration: Beads/skills | Formula step integration | Low |
| Integration: MCP tools | Wrapper if needed | Low |

## Technical Design

### Module Structure

```
playwright-research/
  __init__.py
  core/
    session_manager.py    # Browser state persistence
    research_runner.py    # Main orchestration
    completion_detector.py # Polling and detection
    markdown_extractor.py # HTML to markdown conversion
  platforms/
    __init__.py
    base_platform.py      # Abstract base class
    gemini_adapter.py     # Gemini Deep Research
    chatgpt_adapter.py    # ChatGPT search
    claude_adapter.py     # Claude web search
  config/
    selectors.yaml        # UI selectors per platform
    timeouts.yaml         # Platform-specific timeouts
  cli.py                  # Command-line interface
  skill.py                # Skill/formula integration
```

### Session Management

```python
# Session storage location
~/.featmgmt/playwright-sessions/
  gemini/
    cookies.json
    local_storage.json
    session_state.json
  chatgpt/
    ...
  claude/
    ...
```

Session lifecycle:
1. Check for existing session
2. Validate session (test request)
3. If invalid, prompt for manual re-auth
4. Save new session state
5. Use session for automation

### Platform Adapter Interface

```python
class BasePlatformAdapter(ABC):
    @abstractmethod
    async def authenticate(self, context: BrowserContext) -> bool:
        """Verify/establish authentication"""

    @abstractmethod
    async def trigger_research(self, page: Page, prompt: str) -> None:
        """Input prompt and trigger research"""

    @abstractmethod
    async def detect_completion(self, page: Page) -> bool:
        """Check if research is complete"""

    @abstractmethod
    async def extract_results(self, page: Page) -> str:
        """Extract and convert results to markdown"""
```

### Completion Detection Strategy

Each platform has different signals:

**Gemini Deep Research:**
- Research panel appears
- Loading spinner disappears
- "Deep Research" results populated
- Timeout: 15 minutes (research can be long)

**ChatGPT:**
- Response streaming stops
- "Stop generating" button disappears
- Response content stabilizes
- Timeout: 5 minutes

**Claude:**
- Streaming complete indicator
- Response content stabilizes
- No pending indicators
- Timeout: 5 minutes

### Error Handling Matrix

| Error | Detection | Recovery | User Action |
|-------|-----------|----------|-------------|
| Auth expired | 401/redirect to login | Return partial, save state | Re-authenticate manually |
| Platform down | Connection error | Skip platform, continue | Wait and retry |
| Rate limited | 429/error message | Exponential backoff | Wait or upgrade plan |
| Timeout | Max wait exceeded | Return partial | Check platform manually |
| Selector failed | Element not found | Try fallback selector | Report for selector update |
| UI changed | Unexpected layout | Fail gracefully | Update selectors |

## Dependencies

### External Dependencies
- Playwright (via MCP tools or direct)
- Valid accounts: Gemini, ChatGPT, Claude
- Browser installed (Chromium recommended)

### Internal Dependencies
- FEAT-014 (Beads) - For formula integration (optional)
- MCP Playwright tools - If using MCP approach

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| UI selectors become stale | High | Medium | Centralized config, fallbacks, monitoring |
| Platform blocks automation | Medium | High | Rate limiting, human-like delays |
| Auth complexity (MFA/CAPTCHA) | Medium | Medium | Persistent sessions, manual fallback |
| Long research times | High | Low | Configurable timeouts, async design |
| Platform API changes | Low | High | Abstract adapters, version detection |

## Rollback Strategy

If implementation causes issues:
1. Disable skill/formula integration
2. Revert to manual Stage 2 process
3. Document what went wrong
4. Iterate on specific platform adapter

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Core framework setup
- Session management
- Single platform (Gemini) working end-to-end

### Phase 2: Platform Coverage (Week 2)
- ChatGPT adapter
- Claude adapter
- Parallel execution

### Phase 3: Integration (Week 3)
- CLI polish
- Skill/formula integration
- Documentation

### Phase 4: Hardening (Week 4)
- Error handling improvements
- Selector resilience
- Performance optimization

## Testing Strategy

### Unit Tests
- Markdown extraction
- Session serialization
- Completion detection logic

### Integration Tests
- Each platform end-to-end (requires accounts)
- Parallel execution
- Error recovery flows

### Manual Testing
- Fresh auth flow
- Session persistence across restarts
- Various prompt types
- Timeout scenarios

## Open Questions

1. Should we use MCP Playwright tools or direct Playwright API?
2. How to handle accounts without research features enabled?
3. Should results include citations/sources separately?
4. How to handle multi-part research responses?
5. Should we support custom platform selection (run only 2 of 3)?

---
*This plan should be updated as implementation progresses.*

# FEAT-015: Playwright-Automated Deep Research for Stage 2

**Priority**: P1
**Component**: automation
**Type**: new_feature
**Estimated Effort**: large
**Business Value**: High - Eliminates manual browser work in Stage 2, completes the automation story for Context Engineering

## Overview

Automate Stage 2 (Deep Research) of the Context Engineering methodology using Playwright browser automation. Currently this stage requires manually copying the deep research prompt to three browser tabs (Gemini, ChatGPT, Claude), triggering their research features, waiting for completion, and saving results. This is the only manual stage in an otherwise automated pipeline.

## Problem Statement

Stage 2 is the weak link in Context Engineering automation:
- Manual copy/paste to 3 browser tabs
- Manual triggering of deep research features
- Manual waiting and polling for completion
- Manual extraction and saving of results
- Takes 15-30 minutes of human attention

## Proposed Solution

Create a Playwright-based automation that:
1. Takes a deep research prompt as input
2. Opens authenticated sessions to Gemini, ChatGPT, and Claude web UIs
3. Inputs the prompt and triggers each platform's research feature
4. Polls for completion (these can take 5-10 minutes each)
5. Extracts the results and converts to markdown
6. Saves to docs/research/{gemini,chatgpt,claude}_research.md

## Key Capabilities

- Session management (login state persistence)
- Parallel execution across 3 tabs
- Platform-specific UI navigation (Gemini Deep Research button, ChatGPT search, Claude web search)
- Completion detection for each platform
- Result extraction and markdown conversion
- Error handling and retry logic

## Benefits

- Eliminates 15-30 minutes of manual work per research session
- Completes the Context Engineering automation story
- Enables fully autonomous research pipelines
- Reduces context-switching overhead for humans
- Results are automatically formatted and saved consistently

## Implementation Tasks

### Section 1: Design and Architecture
- [ ] Review Playwright MCP tools capabilities and API
- [ ] Design session management approach (cookies, local storage persistence)
- [ ] Document UI selectors for each platform's research trigger
- [ ] Design completion detection strategy per platform
- [ ] Define output format and file structure

### Section 2: Core Framework
- [ ] Create base automation module with Playwright integration
- [ ] Implement session persistence (save/load authenticated state)
- [ ] Create parallel execution framework for 3 tabs
- [ ] Implement progress tracking and status reporting
- [ ] Add timeout handling and graceful degradation

### Section 3: Platform - Gemini Deep Research
- [ ] Implement Gemini authentication/session handling
- [ ] Locate and trigger Deep Research button
- [ ] Implement completion detection (polling for results)
- [ ] Extract and convert results to markdown
- [ ] Handle Gemini-specific errors (rate limits, session expiry)

### Section 4: Platform - ChatGPT Search
- [ ] Implement ChatGPT authentication/session handling
- [ ] Locate and trigger search/research feature
- [ ] Implement completion detection
- [ ] Extract and convert results to markdown
- [ ] Handle ChatGPT-specific errors

### Section 5: Platform - Claude Web Search
- [ ] Implement Claude authentication/session handling
- [ ] Locate and trigger web search feature
- [ ] Implement completion detection
- [ ] Extract and convert results to markdown
- [ ] Handle Claude-specific errors

### Section 6: Integration
- [ ] Create unified entry point (single prompt -> all 3 platforms)
- [ ] Implement results aggregation and saving
- [ ] Add CLI interface for standalone use
- [ ] Create skill/formula integration for Beads (FEAT-014)
- [ ] Add MCP tool wrapper if needed

### Section 7: Testing and Documentation
- [ ] Test with various research prompt types
- [ ] Document authentication setup process
- [ ] Create troubleshooting guide for common failures
- [ ] Add examples to Context Engineering documentation
- [ ] Performance test parallel execution

## Acceptance Criteria

- [ ] Can authenticate/use saved sessions for all 3 platforms
- [ ] Successfully triggers deep research on Gemini
- [ ] Successfully triggers research on ChatGPT
- [ ] Successfully triggers research on Claude
- [ ] Detects completion on all platforms
- [ ] Extracts and saves markdown output
- [ ] Handles errors gracefully (platform unavailable, auth expired, etc.)
- [ ] Can be invoked as a skill or formula step

## Dependencies

- Playwright MCP tools
- Valid accounts on Gemini, ChatGPT, Claude
- FEAT-014 (Beads formula integration) - for skill/formula step integration

## Technical Considerations

### Session Persistence
- Store browser state (cookies, local storage) per platform
- Location: ~/.featmgmt/playwright-sessions/ or similar
- Need secure handling of auth state
- Session refresh/re-auth flow when expired

### Completion Detection Strategies
- **Gemini**: Watch for results panel to populate, spinner to disappear
- **ChatGPT**: Watch for response completion indicator, "stop generating" button disappearance
- **Claude**: Watch for response completion, streaming to stop

### Error Scenarios
1. **Auth expired**: Prompt user to re-authenticate manually, save new session
2. **Platform down**: Skip platform, continue with others, report partial results
3. **Rate limited**: Implement exponential backoff, warn user
4. **Timeout**: Configurable timeout per platform, graceful failure
5. **UI changed**: Selector-based detection with fallbacks, easy selector updates

### Output Structure
```
docs/research/
  gemini_research.md      # Gemini Deep Research output
  chatgpt_research.md     # ChatGPT search output
  claude_research.md      # Claude web search output
  research_summary.md     # Combined summary (optional)
  .research_metadata.json # Timestamps, versions, status
```

## Integration Points

- **Context Engineering Stage 2**: Primary use case
- **FEAT-014 Beads**: Could become a formula step
- **MCP Playwright tools**: Leverage existing infrastructure
- **Skills system**: Expose as a skill for ad-hoc use

## Notes

- UI selectors may need periodic updates as platforms evolve
- Consider recording sessions for debugging failures
- May need platform-specific timeout configurations (Gemini research can take 10+ minutes)
- Consider adding support for Perplexity or other research tools in future

---

*Created: 2026-01-10*
*Last Updated: 2026-01-10*

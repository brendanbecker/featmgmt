# BUG-001: Fix OVERPROMPT to Process Features

## Problem Statement

The OVERPROMPT-standard.md workflow only processes bugs and ignores features, even though:
1. scan-prioritize-agent scans and prioritizes BOTH bugs and features
2. bug-processor-agent can process BOTH bugs and features
3. The priority queue may contain features

When the bug queue is empty but features exist, the workflow exits instead of processing features.

## Root Cause

OVERPROMPT-standard.md has bug-specific language throughout:
- Phase 2 title: "Process Bug" (not "Process Item")
- Line 234: "IF queue empty" (should check if ANY items exist, not just bugs)
- Line 373: "IF no bugs" (should be "IF no items")
- Phase 7: "IF more bugs exist" (should be "IF more items exist")

## Solution

Update OVERPROMPT-standard.md to use generic "item" terminology and process the highest priority item regardless of whether it's a bug or feature.

## Implementation Steps

### Section 1: Update Phase Titles and Descriptions

**Acceptance Criteria:**
- Phase 2 title changes from "Process Bug" to "Process Item (Bug or Feature)"
- All references to "bug" in flow descriptions changed to "item" or "bug/feature"
- Workflow logic remains identical, just terminology updated

**Tasks:**
1. Update Phase 2 title (line 49)
2. Update Phase 2 invocation example to use generic {ITEM-ID} variable
3. Update Phase 2 description text
4. Update manual fallback language

### Section 2: Update Flow Control Logic

**Acceptance Criteria:**
- Line 234 checks for "queue empty" not "no bugs"
- Line 373 checks for "no items" not "no bugs"
- Phase 7 loop condition checks "more items" not "more bugs"
- Exit conditions reference "items" not "bugs"

**Tasks:**
1. Update line 234 flow diagram: "IF queue empty" → "IF no items in queue"
2. Update line 373: "IF no bugs" → "IF no items"
3. Update Phase 7 (line 201-203): "IF more bugs exist" → "IF more items exist"
4. Update Exit Conditions section (line 299): "All bugs resolved" → "All items resolved"

### Section 3: Update State Management

**Acceptance Criteria:**
- `.agent-state.json` schema uses generic "items" fields
- Backward compatibility maintained (keep bug-specific fields as aliases)

**Tasks:**
1. Update state management section (line 305-319)
2. Add fields: `items_processed`, `items_completed`, `items_failed`
3. Keep legacy fields as aliases: `bugs_processed` → `items_processed`
4. Update documentation to prefer generic terminology

### Section 4: Update Execution Flow Diagram

**Acceptance Criteria:**
- Flow diagram uses "item" terminology
- Diagram accurately reflects bug-or-feature processing

**Tasks:**
1. Update flow diagram (lines 227-276)
2. Change "Process Bug" to "Process Item"
3. Change "next bug in queue" to "next item in queue"
4. Verify all arrows and decision points are accurate

### Section 5: Update "How to Start" Section

**Acceptance Criteria:**
- Startup instructions reference "items" not "bugs"
- Example first message is updated

**Tasks:**
1. Update line 372-373 logic
2. Update example message (line 379-381)
3. Test that workflow correctly processes features when no bugs exist

## Testing Plan

1. **Empty Bug Queue Test:**
   - Create feature-management with 0 bugs, 2 features
   - Run OVERPROMPT workflow
   - Verify scan-prioritize-agent finds features
   - Verify bug-processor-agent is invoked for highest priority feature
   - Verify feature is processed and archived

2. **Mixed Queue Test:**
   - Create feature-management with 1 P2 bug, 1 P1 feature
   - Run OVERPROMPT workflow
   - Verify P1 feature is processed first (higher priority)
   - Verify P2 bug is processed second

3. **Bug-Only Test:**
   - Create feature-management with 2 bugs, 0 features
   - Run OVERPROMPT workflow
   - Verify existing bug processing still works

## Files to Modify

- `/home/becker/projects/featmgmt/templates/OVERPROMPT-standard.md`

## Verification

After implementation:
1. Read updated OVERPROMPT-standard.md
2. Verify no references to "bug" in workflow control logic
3. Verify terminology is consistent throughout
4. Run grep to find any missed "bug" references that should be "item"

## Non-Goals

- Do NOT change bug-processor-agent name (too disruptive)
- Do NOT change scan-prioritize-agent name
- Do NOT change directory names (bugs/, features/)
- Do NOT change file formats (bug_report.json, feature_request.json)

## Notes

- This is a terminology/workflow fix, not an architectural change
- bug-processor-agent already supports features (no agent changes needed)
- scan-prioritize-agent already scans features (no agent changes needed)
- Only OVERPROMPT-standard.md needs updates

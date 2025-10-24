# BUG-002: Fix Hardcoded Paths in OVERPROMPT Templates

## Problem Statement

The OVERPROMPT templates (`templates/OVERPROMPT-standard.md` and `templates/OVERPROMPT-gitops.md`) contain hardcoded paths to `/home/becker/projects/triager` instead of using template variables like `{{PROJECT_PATH}}`.

When `init-project.sh` copies these templates to a new project, it doesn't perform variable substitution (unlike README.md which uses `sed` to replace `{{PROJECT_NAME}}`, `{{PROJECT_TYPE}}`, etc.).

Result: Every new project gets an OVERPROMPT.md with incorrect paths pointing to "triager" instead of the actual project.

## Root Cause

1. Templates were created with example/test project paths
2. `init-project.sh` copies OVERPROMPT templates but doesn't substitute variables
3. README.md template uses `{{VARIABLE}}` placeholders and gets `sed` replacement
4. OVERPROMPT templates don't have placeholders

## Solution

Replace hardcoded paths with `{{PROJECT_PATH}}` variables in both OVERPROMPT templates, then update `init-project.sh` to perform variable substitution.

## Implementation Steps

### Section 1: Update OVERPROMPT-standard.md Template

**Acceptance Criteria:**
- All instances of `/home/becker/projects/triager` replaced with `{{PROJECT_PATH}}`
- All instances of specific project names replaced with appropriate variables
- Template remains valid markdown
- Component-specific paths (orchestrator/classifier-worker/etc.) are preserved as examples

**Tasks:**
1. Replace subagent location path (line 9):
   - FROM: `/home/becker/projects/triager/.claude/agents/`
   - TO: `{{PROJECT_PATH}}/.claude/agents/`

2. Replace Phase 1 scan-prioritize-agent prompt path (line 27):
   - FROM: `Scan the feature-management repository at /home/becker/projects/triager/feature-management`
   - TO: `Scan the feature-management repository at {{PROJECT_PATH}}/feature-management`

3. Replace Phase 2 bug-processor-agent prompt path (line 57):
   - FROM: `/home/becker/projects/triager/feature-management/{bugs|features}/{ITEM-ID}-[slug]/`
   - TO: `{{PROJECT_PATH}}/feature-management/{bugs|features}/{ITEM-ID}-[slug]/`

4. Replace Phase 5 git-ops-agent prompt path (line 137):
   - FROM: `In /home/becker/projects/triager/feature-management:`
   - TO: `In {{PROJECT_PATH}}/feature-management:`

5. Replace Phase 5 manual fallback path (line 156):
   - FROM: `cd /home/becker/projects/triager/feature-management`
   - TO: `cd {{PROJECT_PATH}}/feature-management`

6. Replace Phase 6 retrospective-agent prompt path (line 172):
   - FROM: `review ALL bugs and features in /home/becker/projects/triager/feature-management`
   - TO: `review ALL bugs and features in {{PROJECT_PATH}}/feature-management`

7. Replace Phase 7 summary-reporter-agent prompt path (line 209):
   - FROM: `Save report to /home/becker/projects/triager/feature-management/agent_runs/session-[timestamp].md`
   - TO: `Save report to {{PROJECT_PATH}}/feature-management/agent_runs/session-[timestamp].md`

8. Replace example path in Maintaining Summary Files section (line 362):
   - FROM: `cd /home/becker/projects/triager/feature-management`
   - TO: `cd {{PROJECT_PATH}}/feature-management`

### Section 2: Update OVERPROMPT-gitops.md Template

**Acceptance Criteria:**
- All instances of hardcoded paths replaced with `{{PROJECT_PATH}}`
- Template structure matches standard variant changes
- GitOps-specific components preserved

**Tasks:**
1. Apply same path replacements as Section 1 to OVERPROMPT-gitops.md
2. Update any GitOps-specific path references
3. Verify all agent invocation prompts have correct variable placeholders

### Section 3: Update init-project.sh Script

**Acceptance Criteria:**
- Script calculates PROJECT_PATH from target-path argument
- OVERPROMPT.md gets variable substitution via sed
- Variables replaced: {{PROJECT_PATH}}, {{PROJECT_NAME}}, {{PROJECT_TYPE}}
- Script works for both relative and absolute paths

**Tasks:**
1. Calculate PROJECT_PATH variable after line 48:
   ```bash
   # Get parent directory of feature-management for project root
   PROJECT_ROOT="$(dirname "$TARGET_PATH")"
   # Make it absolute if relative
   PROJECT_ROOT="$(cd "$PROJECT_ROOT" 2>/dev/null && pwd || realpath "$PROJECT_ROOT")"
   ```

2. Add variable substitution for OVERPROMPT.md after line 78:
   ```bash
   cp "$FEATMGMT_ROOT/templates/OVERPROMPT-${PROJECT_TYPE}.md" "$TARGET_PATH/OVERPROMPT.md"

   # Substitute variables in OVERPROMPT.md
   sed -i "s|{{PROJECT_PATH}}|$PROJECT_ROOT|g" "$TARGET_PATH/OVERPROMPT.md"
   sed -i "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$TARGET_PATH/OVERPROMPT.md"
   sed -i "s|{{PROJECT_TYPE}}|$PROJECT_TYPE|g" "$TARGET_PATH/OVERPROMPT.md"
   ```

3. Update success message to mention OVERPROMPT.md customization

### Section 4: Update update-project.sh Script

**Acceptance Criteria:**
- Script preserves local path customizations when updating OVERPROMPT.md
- Script detects and extracts current PROJECT_PATH from existing OVERPROMPT.md
- After template update, script re-applies detected PROJECT_PATH

**Tasks:**
1. Before copying new OVERPROMPT template, extract current paths:
   ```bash
   # Extract current project path from existing OVERPROMPT.md
   CURRENT_PROJECT_PATH=$(grep -m1 "\.claude/agents/" "$TARGET_PATH/OVERPROMPT.md" | sed -E 's|.*`(.*)/.claude/agents/`.*|\1|')
   ```

2. After copying new template, substitute extracted path:
   ```bash
   if [ -n "$CURRENT_PROJECT_PATH" ]; then
     sed -i "s|{{PROJECT_PATH}}|$CURRENT_PROJECT_PATH|g" "$TARGET_PATH/OVERPROMPT.md"
   fi
   ```

3. Add warning if path extraction fails

### Section 5: Testing

**Acceptance Criteria:**
- New project initialization works with absolute paths
- New project initialization works with relative paths
- OVERPROMPT.md has correct paths in all 8+ locations
- Subagent paths point to correct .claude/agents/ directory
- Update script preserves existing project paths

**Tasks:**
1. Test init with absolute path:
   ```bash
   ./scripts/init-project.sh standard /tmp/test-absolute/feature-management testproj "backend"
   grep "PROJECT_PATH" /tmp/test-absolute/feature-management/OVERPROMPT.md  # Should be empty
   grep "/tmp/test-absolute" /tmp/test-absolute/feature-management/OVERPROMPT.md  # Should have 8+ matches
   ```

2. Test init with relative path:
   ```bash
   ./scripts/init-project.sh standard ../test-relative/feature-management testproj "backend"
   grep "../test-relative" ../test-relative/feature-management/OVERPROMPT.md  # Should have 8+ matches
   ```

3. Test update script preserves paths:
   ```bash
   # Create project with custom path
   ./scripts/init-project.sh standard /tmp/test-update/feature-management myproj
   # Modify template
   echo "# Test change" >> templates/OVERPROMPT-standard.md
   # Run update
   ./scripts/update-project.sh /tmp/test-update/feature-management
   # Verify paths still correct
   grep "/tmp/test-update" /tmp/test-update/feature-management/OVERPROMPT.md  # Should still have 8+ matches
   ```

4. Manual verification checklist:
   - [ ] Phase 1 scan-prioritize-agent path correct
   - [ ] Phase 2 bug-processor-agent path correct
   - [ ] Phase 5 git-ops-agent path correct
   - [ ] Phase 6 retrospective-agent path correct
   - [ ] Phase 7 summary-reporter-agent path correct
   - [ ] Subagent location path correct
   - [ ] Manual fallback examples have correct paths
   - [ ] README.md variable substitution still works

## Files to Modify

- `/home/becker/projects/featmgmt/templates/OVERPROMPT-standard.md`
- `/home/becker/projects/featmgmt/templates/OVERPROMPT-gitops.md`
- `/home/becker/projects/featmgmt/scripts/init-project.sh`
- `/home/becker/projects/featmgmt/scripts/update-project.sh`

## Verification

After implementation:
1. Run init-project.sh and verify no {{PROJECT_PATH}} remains in output OVERPROMPT.md
2. Run update-project.sh on existing project and verify paths preserved
3. Search templates for hardcoded "/home/becker/projects/" - should only be in examples/docs
4. Verify README.md substitution still works

## Non-Goals

- Do NOT change component-specific paths (orchestrator/classifier-worker/etc.) - these are examples
- Do NOT change paths in documentation files (docs/, examples/, CLAUDE.md)
- Do NOT change the directory structure (bugs/, features/, completed/)
- Do NOT add variables for component names or other project-specific config

## Notes

- This is similar to how README.md template already works with {{PROJECT_NAME}}
- The update script is trickier because it must preserve local customizations
- Consider adding {{MAIN_BRANCH}} variable in future (master vs main)
- Component-specific directory examples should remain as examples since projects customize these

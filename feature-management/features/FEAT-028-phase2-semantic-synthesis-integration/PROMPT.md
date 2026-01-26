# FEAT-028: INQ Phase 2 Semantic Synthesis Integration

## Overview

Wire the semantic synthesis pipeline (FEAT-024 through FEAT-027) into the `/inquiry` skill's Phase 2, replacing the current `synthesis_generator.py` approach. This integrates bounded-context, coverage-aware synthesis into the existing INQ workflow.

## Problem Statement

The current Phase 2 synthesis in the `/inquiry` skill uses `synthesis_generator.py`, which:
1. Does not leverage semantic embeddings for finding related content across research reports
2. Lacks bounded-context awareness for managing LLM token limits
3. Has no coverage tracking to ensure all research findings are addressed
4. Cannot identify emergent themes that span multiple agent reports

The new semantic synthesis pipeline (FEAT-024 through FEAT-027) provides:
- FEAT-024: Semantic index building from research reports
- FEAT-025: Question-driven content retrieval with similarity scoring
- FEAT-026: Coverage tracking to ensure completeness
- FEAT-027: Output generation with proper formatting

## Acceptance Criteria

- [ ] /inquiry skill uses new synthesis pipeline for Phase 2
- [ ] Existing INQ-001 test case works with new system
- [ ] Phase transitions still function correctly
- [ ] Documentation updated in skills/inquiry/
- [ ] Backward compatible with existing INQ directories
- [ ] Graceful handling of edge cases (empty research, single agent, no emergent content)

## Key Capabilities

### Replace synthesis_generator.py in phase_manager.py
- Remove direct calls to synthesis_generator.py
- Invoke new semantic synthesis pipeline when Phase 2 starts
- Maintain same output interface (SYNTHESIS.md generation)

### Orchestrate Pipeline Components
When Phase 2 begins:
1. **Build Index** (FEAT-024): Index all `research/agent-*.md` files
2. **Question Retrieval** (FEAT-025): For each synthesis question, retrieve relevant content
3. **Coverage Tracking** (FEAT-026): Track which research findings have been addressed
4. **Output Generation** (FEAT-027): Generate SYNTHESIS.md with proper structure

### Ensure Backward Compatibility
- Existing INQ directories with research/ files work unchanged
- inquiry_report.json schema unchanged
- SYNTHESIS.md output format unchanged
- Phase transition triggers unchanged

### Handle Edge Cases
- **Empty research**: No agent-*.md files → graceful error with instructions
- **Single agent**: Only one research report → skip convergence/divergence analysis
- **No emergent content**: No cross-cutting themes found → note in synthesis
- **Large research corpus**: Too much content for context → summarize before synthesis

## Implementation Tasks

### 1. Analyze Current Integration Point
- Review `skills/inquiry/scripts/phase_manager.py` for synthesis entry point
- Document current synthesis_generator.py interface
- Identify all callers of synthesis logic

### 2. Create Pipeline Orchestrator
Create `skills/inquiry/scripts/synthesis_pipeline.py`:
```python
class SynthesisPipeline:
    def __init__(self, inquiry_dir: Path):
        self.inquiry_dir = inquiry_dir
        self.index = None
        self.coverage = None

    def run(self) -> Path:
        """Execute full synthesis pipeline, return path to SYNTHESIS.md"""
        # 1. Build semantic index from research/
        self.index = self._build_index()

        # 2. Extract synthesis questions from inquiry_report.json
        questions = self._get_synthesis_questions()

        # 3. Retrieve and synthesize for each question
        sections = []
        for question in questions:
            content = self._retrieve_for_question(question)
            section = self._synthesize_section(question, content)
            sections.append(section)

        # 4. Track coverage and identify gaps
        self.coverage = self._analyze_coverage()

        # 5. Generate final SYNTHESIS.md
        return self._generate_output(sections)
```

### 3. Update phase_manager.py
Replace synthesis_generator.py calls with pipeline invocation:
```python
# Before
from .synthesis_generator import generate_synthesis
synthesis_path = generate_synthesis(inquiry_dir)

# After
from .synthesis_pipeline import SynthesisPipeline
pipeline = SynthesisPipeline(inquiry_dir)
synthesis_path = pipeline.run()
```

### 4. Add Edge Case Handling
- Check for research files before proceeding
- Handle single-agent case (skip comparative analysis)
- Detect and handle oversized research corpus
- Generate informative errors for missing prerequisites

### 5. Update Documentation
- Update `skills/inquiry/README.md` with new synthesis behavior
- Document pipeline components and their roles
- Add troubleshooting for common edge cases

### 6. Backward Compatibility Testing
- Test with existing INQ-001 directory structure
- Verify phase transitions work correctly
- Ensure inquiry_report.json updates properly
- Validate SYNTHESIS.md format matches expectations

## Dependencies

- **FEAT-027** (Synthesis Output Generator): Must be complete for output generation
- **FEAT-021** (Inquiry Orchestration Skill): Provides phase_manager.py integration point

## Testing

### Unit Tests
- Pipeline orchestrator with mock components
- Edge case handling (empty, single agent, large corpus)
- Coverage tracking accuracy

### Integration Tests
- Full pipeline with real research files
- Phase transition from Phase 1 to Phase 2
- SYNTHESIS.md validation against schema

### Test Cases
```
test_cases/
├── inq-empty-research/       # No agent files
├── inq-single-agent/         # Only one research report
├── inq-multiple-agents/      # Standard case (3+ agents)
├── inq-large-corpus/         # Oversized research content
└── inq-001-regression/       # Existing INQ-001 compatibility
```

## Files to Create/Modify

### Create
- `skills/inquiry/scripts/synthesis_pipeline.py` - Main orchestrator

### Modify
- `skills/inquiry/scripts/phase_manager.py` - Replace synthesis calls
- `skills/inquiry/README.md` - Update documentation
- `skills/inquiry/SKILL.md` - Update skill description if needed

### Deprecate (after migration)
- `skills/inquiry/scripts/synthesis_generator.py` - Mark for removal

## Success Metrics

- All existing INQ test cases pass
- Phase 2 generates valid SYNTHESIS.md
- Coverage tracking reports accurate statistics
- No regression in phase transition behavior

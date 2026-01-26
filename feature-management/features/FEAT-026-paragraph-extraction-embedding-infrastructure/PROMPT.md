# FEAT-026: Paragraph Extraction & Embedding Infrastructure

**Priority**: P1
**Component**: skills
**Type**: feature
**Estimated Effort**: medium
**Business Value**: high

## Overview

Python module to parse research markdown files into paragraphs, generate semantic embeddings via BGE model, and provide queryable in-memory index with cosine similarity retrieval. This is the foundational infrastructure for the semantic synthesis pipeline.

### Key Capabilities

- Parse markdown into paragraphs (respecting code blocks, lists, headers)
- Integration with sentence-embedding skill (BGE model, 384 dimensions)
- In-memory index structure: {text, embedding, source_file, section_header, line_range}
- Top-K retrieval via cosine similarity queries
- Batch embedding for efficiency
- Handle code blocks and structured content gracefully

## Benefits

- Enables semantic search across research documents
- Foundation for automated synthesis in INQ workflows
- Efficient similarity-based retrieval for knowledge consolidation
- Supports the multi-agent deliberation pipeline

## Implementation Tasks

### Section 1: Design
- [ ] Review requirements and acceptance criteria
- [ ] Design solution architecture
- [ ] Identify affected components
- [ ] Document implementation approach

### Section 2: Implementation
- [ ] Implement core functionality
- [ ] Add error handling
- [ ] Update configuration if needed
- [ ] Add logging and monitoring

### Section 3: Testing
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Manual testing of key scenarios
- [ ] Performance testing if needed

### Section 4: Documentation
- [ ] Update user documentation
- [ ] Update technical documentation
- [ ] Add code comments
- [ ] Update CHANGELOG

### Section 5: Verification
- [ ] All acceptance criteria met
- [ ] Tests passing
- [ ] Code review completed
- [ ] Ready for deployment

## Acceptance Criteria

- [ ] Feature implemented as described
- [ ] All tests passing
- [ ] Documentation updated
- [ ] No regressions in existing functionality
- [ ] Performance meets requirements

## Dependencies

None (standalone infrastructure component)

## Notes

**Acceptance Criteria:**
- [ ] Extract paragraphs from research/*.md files preserving structure
- [ ] Generate 384-dim embeddings via BGE model
- [ ] Support cosine similarity queries (top-K retrieval)
- [ ] Handle code blocks and structured content gracefully
- [ ] Batch processing for multiple files

**Tags:** skills, inquiry, embeddings, semantic-search, synthesis, infrastructure

**Technical Complexity:** Medium

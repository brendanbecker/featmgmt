# FEAT-025: Question-Driven Retrieval Synthesis

## Overview

Create a skill that performs question-driven retrieval-augmented synthesis for inquiry workflows. For each question in QUESTION.md, embed the question, retrieve top-K relevant paragraphs from research reports, and synthesize with bounded context per question.

## Problem Statement

During inquiry synthesis (Phase 2), the synthesizer agent needs to answer questions from QUESTION.md using research reports from multiple agents. Current approaches either:
1. **Load all content**: Exceeds context limits for large research corpora
2. **Manual selection**: Requires human curation of relevant sections
3. **Naive truncation**: Loses important context from later sections

This feature enables controlled context usage by:
- Embedding each question using the same BGE model as paragraph embeddings (FEAT-024)
- Retrieving only the most semantically relevant paragraphs per question
- Synthesizing answers with bounded, focused context
- Tracking which paragraphs were used for coverage analysis (FEAT-026)

## Acceptance Criteria

### Core Functionality
- [ ] Parse questions from QUESTION.md (multiple formats: numbered, headed, bullet)
- [ ] Embed questions using BGE model (same as FEAT-024 paragraph embeddings)
- [ ] Retrieve top-K relevant paragraphs per question via cosine similarity
- [ ] Invoke synthesis agent with bounded context per question
- [ ] Return paragraph indices used for coverage tracking

### Question Parsing
- [ ] Support numbered format: `1. Question text`
- [ ] Support headed format: `## Question: Text` or `### Question N`
- [ ] Support bullet format: `- Question text`
- [ ] Extract question metadata (tags, priority) if present

### Retrieval Configuration
- [ ] Configurable K parameter (default: 5-10 paragraphs per question)
- [ ] Configurable similarity threshold (minimum relevance score)
- [ ] Optional diversity parameter to avoid redundant paragraphs
- [ ] Optional weighting by paragraph importance/length

### Output Structure
- [ ] Structured results with question, retrieved paragraphs, synthesis
- [ ] Paragraph references (file, paragraph index, similarity score)
- [ ] Token count per question context
- [ ] Coverage metrics (which paragraphs were retrieved)

## Technical Design

### Input Requirements

**QUESTION.md** (source of questions):
```markdown
## Key Questions for Synthesis

1. What are the primary architectural approaches discussed?
2. How should we handle state management?
3. What testing strategies are recommended?
```

**Paragraph embeddings** (from FEAT-024):
```json
{
  "paragraphs": [
    {
      "index": 0,
      "source_file": "research/agent-1.md",
      "content": "The research suggests...",
      "embedding": [0.123, 0.456, ...],
      "metadata": {"section": "Architecture", "length": 245}
    }
  ]
}
```

### Output Structure

```json
{
  "inquiry_id": "INQ-001",
  "questions": [
    {
      "question_id": 1,
      "question_text": "What are the primary architectural approaches?",
      "question_embedding": [0.111, 0.222, ...],
      "retrieved_paragraphs": [
        {
          "index": 12,
          "source_file": "research/agent-1.md",
          "content": "...",
          "similarity_score": 0.92
        },
        {
          "index": 45,
          "source_file": "research/agent-2.md",
          "content": "...",
          "similarity_score": 0.88
        }
      ],
      "context_tokens": 1250,
      "synthesis": "Based on the research...",
      "synthesis_tokens": 340
    }
  ],
  "coverage": {
    "total_paragraphs": 150,
    "retrieved_paragraphs": 45,
    "retrieval_rate": 0.30,
    "unretrieved_indices": [0, 3, 7, ...]
  }
}
```

### Algorithm

```
1. Parse QUESTION.md to extract questions
2. Load paragraph embeddings from FEAT-024 output
3. For each question:
   a. Embed question text using BGE model
   b. Compute cosine similarity with all paragraph embeddings
   c. Select top-K paragraphs above similarity threshold
   d. Apply diversity filter if enabled
   e. Format context with paragraph references
   f. Invoke synthesis agent with bounded context
   g. Record paragraph indices used
4. Compute coverage metrics
5. Return structured results
```

## Implementation Tasks

### 1. Question Parser Module
```
scripts/question_parser.py
- parse_question_md(filepath) -> List[Question]
- Support numbered, headed, bullet formats
- Extract metadata (tags, priority) if present
- Return Question objects with id, text, metadata
```

### 2. Question Embedding Module
```
scripts/question_embedder.py
- embed_questions(questions: List[Question]) -> List[QuestionWithEmbedding]
- Use same BGE model as FEAT-024
- Batch embedding for efficiency
- Cache embeddings for repeated runs
```

### 3. Retrieval Module
```
scripts/paragraph_retriever.py
- retrieve_paragraphs(question_embedding, paragraph_embeddings, k, threshold) -> List[RetrievedParagraph]
- Cosine similarity computation
- Top-K selection with threshold
- Optional diversity filtering (MMR)
- Return with similarity scores
```

### 4. Synthesis Orchestrator
```
scripts/synthesis_orchestrator.py
- synthesize_question(question, paragraphs) -> Synthesis
- Format context with paragraph references
- Invoke synthesis agent (or LLM directly)
- Parse synthesis response
- Track token usage
```

### 5. Main Skill Entry Point
```
skills/question-retrieval-synthesis/SKILL.md
- Invoke via /question-synthesis INQ-XXX
- Load QUESTION.md from inquiry directory
- Load embeddings from FEAT-024 output
- Orchestrate full pipeline
- Output to inquiry directory
```

### 6. Coverage Tracker
```
scripts/coverage_tracker.py
- track_coverage(all_indices, retrieved_indices) -> CoverageMetrics
- Compute retrieval rate
- Identify unretrieved paragraphs
- Generate coverage report for FEAT-026
```

## Usage Examples

### Invoke via skill
```
/question-synthesis INQ-001 --k 7 --threshold 0.6
/question-synthesis INQ-001 --k 10 --diversity 0.3
```

### Programmatic invocation
```python
from question_retrieval_synthesis import synthesize_inquiry

results = synthesize_inquiry(
    inquiry_id="INQ-001",
    k=7,
    threshold=0.6,
    diversity=0.3
)
```

## Dependencies

- **FEAT-024**: Paragraph Embedding Pipeline (provides paragraph embeddings)
- Python 3.9+
- sentence-transformers (BGE model)
- numpy (similarity computation)
- jq (JSON manipulation)

## Error Handling

- **Missing embeddings**: Error with instruction to run FEAT-024 first
- **No questions found**: Clear error with QUESTION.md format examples
- **Low retrieval scores**: Warning if max similarity below threshold
- **Empty synthesis**: Flag questions needing manual review

## Testing

### Test Fixtures
- Sample QUESTION.md with various formats
- Mock paragraph embeddings (small set)
- Expected retrieval results
- Expected synthesis outputs

### Test Cases
- Parse numbered questions correctly
- Parse headed questions correctly
- Parse bullet questions correctly
- Retrieve top-K paragraphs by similarity
- Respect similarity threshold
- Apply diversity filter correctly
- Track coverage metrics accurately
- Handle missing/malformed inputs gracefully

## Integration Points

- **FEAT-024**: Input - paragraph embeddings
- **FEAT-026**: Output - coverage metrics for gap analysis
- **Inquiry workflow**: Phase 2 synthesis step
- **sentence-embedding skill**: Reuse BGE model loading

## Success Metrics

- Synthesis quality comparable to full-context approach
- Token usage reduced by 60-80% vs full context
- Retrieval precision > 0.8 (relevant paragraphs retrieved)
- Coverage tracking enables gap identification

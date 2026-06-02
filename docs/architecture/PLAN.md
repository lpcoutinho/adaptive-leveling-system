# Adaptive Leveling System

AI-powered educational readiness assessment and personalized leveling platform for higher education.

---

# Challenge Overview

Use an LLM to:

1. Extract prerequisites from a Calculus I lesson.
2. Assess whether a student is prepared to understand the lesson.
3. Identify knowledge gaps.
4. Generate personalized leveling content before the lesson begins.

---

# Objective

Develop an AI-powered educational readiness system capable of transforming a lesson into an adaptive learning experience.

The platform analyzes lesson content, identifies prerequisite knowledge, evaluates student readiness, and generates personalized remediation content to improve learning outcomes.

---

# Solution Architecture

```text
                    ┌─────────────┐
                    │ Lesson PDF  │
                    └──────┬──────┘
                           │
                           ▼
               ┌──────────────────────┐
               │ Lesson Analysis Node │
               └──────────┬───────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Knowledge Graph   │
                └─────────┬─────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │ Assessment Generator │
              └──────────┬───────────┘
                         │
                         ▼
                 ┌──────────────┐
                 │ Student Quiz │
                 └──────┬───────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Gap Detection Node  │
              └─────────┬───────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │ Leveling Content Generator   │
         └──────────────┬───────────────┘
                        │
                        ▼
             ┌──────────────────────┐
             │ Personalized Plan    │
             └──────────────────────┘
```

---

# Technology Stack

## Backend

* Python 3.12
* FastAPI
* LangGraph
* Pydantic
* PydanticAI
* **LLM Abstraction Layer**
  - Groq API (primary)
  - OpenAI (alternative)
  - Anthropic (alternative)
  - Mock (testing)

## Frontend

* Streamlit

## Data Layer

* PostgreSQL
* Redis

## Observability

* OpenTelemetry
* Loguru

## Testing

* Pytest

---

# Architectural Decisions

## FastAPI

FastAPI provides:

* Clean API layer
* Automatic OpenAPI documentation
* Scalability
* Separation between UI and business logic

Architecture:

```text
Streamlit
    ↓
FastAPI
    ↓
LangGraph Workflow
    ↓
Groq API
```

---

## LangGraph

The problem naturally fits a workflow architecture.

Benefits:

* Explicit state management
* Traceable execution
* Easier future evolution

Workflow:

```text
START
 ↓
ExtractPrerequisites
 ↓
GenerateAssessment
 ↓
EvaluateStudent
 ↓
GenerateLevelingPlan
 ↓
END
```

---

## LLM Abstraction Layer

Provides provider independence through dependency injection:

**Architecture:**
```
Services → ILLMProvider (interface) → GroqProvider | OpenAIProvider | MockProvider
```

**Benefits:**
- Swap providers via `LLM_PROVIDER=groq|openai|anthropic|mock`
- Easy testing with MockProvider
- Built-in resilience (retry, timeout, circuit breaker, fallback)
- OpenTelemetry tracing integrated

**Configuration:**
```python
# backend/llm/config.py
class LLMConfig(BaseSettings):
    LLM_PROVIDER: str = "groq"
    LLM_PRIMARY_MODEL: str = "llama-3.3-70b"
    LLM_FALLBACK_MODEL: str = "deepseek-r1"
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
```

**Usage:**
```python
class PrerequisiteService:
    def __init__(
        self,
        llm: ILLMProvider = Depends(get_llm_provider)
    ):
        self._llm = llm  # Injected!

    async def extract(self, text: str):
        return await self._llm.generate_structured(...)
```

---

## PydanticAI

Used for:

* Structured outputs
* Validation
* Reduced hallucinations
* Type safety

---

## Groq

Default LLM provider (configurable via `LLM_PROVIDER=groq`).

Chosen because:

* Low latency
* Cost efficiency
* Easy integration
* Strong support for open-source models

**Alternative Providers:** OpenAI, Anthropic (via LLM Abstraction Layer)

---

# Context Retrieval Strategy

## MVP

The provided lesson contains only a few pages.

Therefore, the system uses:

```text
Context Injection
```

The complete lesson is sent directly to the LLM.

Benefits:

* Simpler architecture
* Lower latency
* No indexing required

---

## Future Evolution

For large-scale content:

```text
PDFs
 ↓
Chunking
 ↓
Embeddings
 ↓
PostgreSQL + pgvector
 ↓
Semantic Retrieval
 ↓
LLM
```

This allows semantic search without introducing a dedicated vector database.

---

# Project Structure

```text
adaptive-leveling-system/

├── backend/
│
├── api/
│   ├── routes/
│   ├── schemas/
│   └── dependencies/
│
├── domain/
│   ├── models/
│   └── knowledge_graph/
│
├── workflows/
│   ├── readiness_graph.py
│   └── states.py
│
├── services/
│   ├── pdf_service.py
│   ├── assessment_service.py
│   ├── leveling_service.py
│
├── llm/
│   ├── base/
│   │   ├── interface.py      # ILLMProvider interface
│   │   └── models.py         # Request/Response models
│   ├── config.py             # LLM configuration
│   ├── factory.py            # Provider factory with DI
│   ├── providers/
│   │   ├── groq_provider.py  # Groq implementation
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   └── mock_provider.py  # Mock for tests
│   ├── resilience/
│   │   ├── retry.py
│   │   ├── circuit_breaker.py
│   │   └── fallback.py
│   ├── prompts/
│   └── evaluators/
├── api/
│   ├── routes/
│   ├── schemas/
│   └── dependencies/
│       └── llm.py            # FastAPI dependencies for LLM
│
├── infrastructure/
│   ├── telemetry/
│   ├── cache/
│   ├── resilience/
│   └── security/
│
├── frontend/
│   └── streamlit/
│
└── tests/
```

---

# Domain Models

## Prerequisite

```python
class Prerequisite(BaseModel):
    name: str
    description: str
    importance: Literal[
        "Critical",
        "Important",
        "Helpful"
    ]
    topics: list[str]
```

---

## Knowledge Graph

```python
class ConceptNode(BaseModel):
    name: str
    description: str
    prerequisites: list[str]
```

Example:

```text
Algebra
 ↓
Functions
 ↓
Limits
 ↓
Derivatives
 ↓
Chain Rule
```

---

## Assessment Question

```python
class QuizQuestion(BaseModel):
    question_id: str
    question_text: str
    question_type: Literal[
        "multiple_choice",
        "short_answer",
        "calculation"
    ]
    correct_answer: str
    explanation: str
    prerequisite_tag: str
```

---

## Readiness Result

```python
class ReadinessResult(BaseModel):
    readiness_score: float
    readiness_level: str
    strengths: list[str]
    gaps: list[str]
```

Example:

```json
{
  "readiness_score": 78,
  "readiness_level": "Needs Review",
  "strengths": [
    "Functions",
    "Trigonometry"
  ],
  "gaps": [
    "Algebra"
  ]
}
```

---

## Personalized Leveling Content

```python
class GapExplanation(BaseModel):
    concept: str
    why_it_matters: str
    explanation: str
    worked_example: str
    exercise: str
```

---

# Workflow

## Step 1 — PDF Processing

Responsibilities:

* Extract text
* Generate hash
* Normalize content

Service:

```text
pdf_service.py
```

---

## Step 2 — Prerequisite Extraction

Outputs:

* Main concepts
* Prerequisites
* Knowledge Graph

---

## Step 3 — Assessment Generation

Creates diagnostic questions based on extracted prerequisites.

---

## Step 4 — Student Evaluation

### Objective Questions

Deterministic evaluation:

```python
answer == correct_answer
```

### Open Questions

LLM-as-a-Judge approach.

---

## Step 5 — Gap Detection

Identifies:

* Strengths
* Weak areas
* Critical missing knowledge

---

## Step 6 — Personalized Leveling

Generates:

* Short explanation
* Worked example
* Practice exercise
* Recommended study order

---

# AI Ops Strategy

## Prompt Versioning

```text
prompts/

├── prerequisite_extractor_v1.txt
├── prerequisite_extractor_v2.txt
├── assessment_generator_v1.txt
└── leveling_generator_v1.txt
```

---

## Model Registry

```python
SUPPORTED_MODELS = {
    "primary": "llama-3.3-70b",
    "fallback": "deepseek-r1"
}
```

---

## Evaluation Dataset

```text
tests/evaluation/

calculus_1.pdf
physics_1.pdf
linear_algebra.pdf
```

Used for regression testing and quality validation.

---

# Resilience Strategy

## Retry with Exponential Backoff

All LLM requests use retry policies.

```text
Failure
 ↓
1s
 ↓
Failure
 ↓
2s
 ↓
Failure
 ↓
4s
 ↓
Final Error
```

---

## Timeout Protection

```python
timeout = 30
```

Prevents hanging requests.

---

## Fallback Models

```text
Primary Model
      ↓
    Failure
      ↓
Fallback Model
      ↓
Response
```

Ensures continuity.

---

## Circuit Breaker

Prevents cascading failures.

```text
Error
Error
Error
 ↓
Circuit Open
 ↓
Cooldown
 ↓
Health Check
 ↓
Circuit Closed
```

---

## Workflow Recovery

State persistence enables recovery from intermediate failures.

```python
class WorkflowState(BaseModel):
    pdf_id: str
    prerequisites: list
    assessment: list
    readiness_score: float
```

---

## Graceful Degradation

If personalized generation fails:

```text
Personalized Plan
       ↓
     Failure
       ↓
 Generic Study Plan
```

The student always receives guidance.

---

# Performance and Cost Optimization

## Redis Cache

Cache targets:

* PDF processing
* Prerequisite extraction
* Assessment generation
* Leveling content

Flow:

```text
PDF Hash
 ↓
Redis
 ↓
Hit → Return
Miss → Execute Workflow
```

---

## Idempotency

Every uploaded PDF receives a SHA-256 hash.

```text
Upload
 ↓
Generate Hash
 ↓
Exists?
 ↓
Yes → Reuse
No → Process
```

---

## Hybrid Evaluation

Objective questions:

```python
answer == correct_answer
```

Open-ended questions:

```text
LLM-as-a-Judge
```

Reduces costs while maintaining flexibility.

---

# Observability

## OpenTelemetry Traces

```text
pdf.processing

prerequisite.extraction

assessment.generation

student.assessment

gap.analysis

leveling.content.generation
```

---

## Operational Metrics

### System

```text
response_time

memory_usage

cpu_usage

error_rate
```

### AI

```text
llm_latency

llm_success_rate

llm_failure_rate

retry_count

fallback_usage
```

### Cache

```text
cache_hit_ratio

cache_miss_ratio
```

### Business

```text
workflow_completion_rate

readiness_score

gap_count

approval_rate
```

### Cost

```text
prompt_tokens

completion_tokens

cost_per_request

cost_per_student
```

---

# Security

## Input Validation

* PDF type validation
* File size limits
* Text sanitization
* Rate limiting

## Secret Management

* Environment variables
* Secure API key handling

---

# Future Evolution

## PostgreSQL + pgvector

Future semantic retrieval support:

```text
PDFs
 ↓
Chunking
 ↓
Embeddings
 ↓
PostgreSQL + pgvector
 ↓
Retriever
 ↓
LLM
```

---

## Adaptive Learning Platform

Future capabilities:

* Continuous learning profiles
* Adaptive learning paths
* Longitudinal assessment
* Teacher dashboards
* Learning analytics
* Personalized recommendations

---

# Expected Outcome

At the end of the workflow, the student receives:

1. Readiness assessment.
2. Readiness score.
3. Identified strengths.
4. Knowledge gaps.
5. Personalized leveling plan.
6. AI-generated explanations.
7. Practice exercises.
8. Recommended study sequence.

The goal is to maximize student preparedness before entering the Calculus I lesson while demonstrating production-grade AI Engineering and AI Ops practices.

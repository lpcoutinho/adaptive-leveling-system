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
* FastAPI (API Layer)
* LangGraph (Workflow Orchestration)
* Pydantic V2 (Validation)
* **LLM Layer**
  * Groq API (Primary - Llama 3.3 70B)
  * OpenAI / Anthropic (Alternativos)
  * Mock Provider (Testing & Offline Dev)

## Frontend

* Streamlit (Student & Teacher Interface)

## Data Layer (Dedicated Infrastructure)

* **PostgreSQL 16**: Metadata, Intelligence & Checkpointing.
* **Valkey 8**: Distributed Cache & Session Management.
* **Minio**: S3-compatible Blob Storage for PDFs.

## Observability & AI Ops

* **OpenTelemetry**: Protocol for traces and metrics.
* **Jaeger**: Distributed tracing visualization.
* **Loguru**: Structured and colorized logging.

---

# Architectural Decisions

## Workflow Orchestration (LangGraph)

The system treats the educational journey as a stateful workflow.

Benefits:

* **Explicit State**: Each transition is validated.
* **Checkpointing**: Workflows can be resumed (e.g., after the student finishes a long quiz).
* **Traceability**: End-to-end visibility of the agent's reasoning.

## LLM-as-a-Judge (Hybrid Correction)

* **Multiple Choice**: Corrected deterministically (high efficiency, zero LLM cost).
* **Open Questions**: Corrected by LLM in **Batch Mode** at the end of the quiz, providing pedagogical justifications and structured scores (0-100).

## Idempotency & Efficiency

Every PDF is hashed (SHA-256). If the content was previously processed, the system reuses the Knowledge Graph and Assessment, saving API costs and reducing latency to zero.

---

# Implementation Roadmap

1. **Foundation**: Dedicated containers and agnosticism. ✅
2. **Data Ingestion**: Hashing, S3, and extraction. ✅
3. **Intelligence**: Knowledge Graph extraction via LLM. ✅
4. **Assessment**: Balanced generation (10 questions). ✅
5. **Interactive Quiz**: Real-time progress and batch correction. ✅
6. **Readiness**: Weighted scoring (Critical/Important/Helpful). ✅
7. **Personalized Leveling**: WEEE structure content generation. ✅
8. **LangGraph Orchestration**: Seamless state transitions. ✅
9. **Enterprise Polish**: Resilience, Performance, and Advanced Docs. 🏗️

---

## Future Evolution (Scalability & Ops)

## Advanced Observability (Langfuse)

Detailed monitoring of LLM calls, prompt versioning, and cost tracking per session.

## Semantic Caching

Reduce LLM redundancy by caching similar pedagogical explanations in Valkey.

## Asynchronous Processing

Move heavy PDF/LLM tasks to background workers (Celery) to support concurrent high-volume usage.

## RAG & pgvector

Support for long-form textbooks using vector embeddings and semantic search in PostgreSQL.

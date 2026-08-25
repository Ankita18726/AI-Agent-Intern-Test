# Aster & Row Reliable RAG Support Agent

A reliability-focused AI customer support agent built for the **AI Agent Intern Take-Home**.

The system uses **LangGraph + ChromaDB + Ollama + RAG** to answer Aster & Row policy and product questions, perform safe order-status lookups, preserve relevant multi-turn context, detect source conflicts, abstain when information is insufficient, and prevent internal or instruction-like retrieved content from controlling agent behavior.

The implementation intentionally favors **deterministic logic for safety-critical decisions** instead of delegating everything to the language model.

---

## Demo

> **2–4 minute demo video:** 

[![Watch the Aster & Row Support Agent Demo])](https://drive.google.com/file/d/1LBQNsOzajMOhfsllEhbqEM37iZZ5viKW/view?usp=sharing)

The demo includes:
- a knowledge-base question with source citations
- a secure order lookup
- a multi-turn conversation
- safe abstention / human handoff
- privacy protection
- structured tracing
- evaluation execution

---

## Final Evaluation Result

**TL;DR:** 19/22 evaluation cases passing (86.4%), 100% on retrieval, tool use, privacy, 
prompt security, and abstention. Remaining gaps are response-wording completeness, not 
incorrect or unsafe behavior — see Bug Diary.
The final evaluation covers all **15 supplied visible cases** plus **7 original regression cases**.

---

## Overview

Aster & Row is a fictional ecommerce company selling bags, drinkware, and travel accessories.

The supplied corpus intentionally includes difficult conditions:
- current and superseded policies
- conflicting current sources
- internal-only documents
- instruction-like retrieved content
- mock order data containing private/internal fields
- missing delivery estimates
- cancelled orders with stale delivery information
- multi-turn follow-up questions

The goal of this project is not simply to produce plausible answers. The agent must be able to explain **why an answer is trusted, when it should abstain, when it must use a tool, and when human assistance is required**.

---

# Key Capabilities

## 1. Retrieval-Augmented Generation

The agent performs RAG over the Markdown files in `knowledge-base/`.

The ingestion and retrieval pipeline:
1. Loads all supplied Markdown files.
2. Parses YAML/front-matter metadata.
3. Splits documents into heading-aware semantic chunks.
4. Preserves metadata such as filename, heading, status, audience, policy authority, effective date, and supersession information.
5. Generates embeddings locally with Ollama.
6. Stores the derived index in ChromaDB.
7. Retrieves only relevant passages for each user request.
8. Applies semantic, lexical, and metadata-aware ranking.
9. Filters internal and superseded sources before customer-facing generation.

The supplied source files are **not modified or rewritten**.

### Policy precedence

Current authoritative customer-facing documents are preferred over superseded documents, legacy policies, internal notes, draft/unapproved material, and non-policy content.

A superseded document disagreeing with a current policy is **not treated as a genuine current conflict**.

---

## 2. Safe Order Lookup Tool

Order information is retrieved from `data/orders.json`.

The model never receives the entire order dataset.

```text
User request
   ↓
Extract / normalize order ID
   ↓
Exact deterministic lookup
   ↓
Sanitize raw order record
   ↓
Return customer-safe fields only
   ↓
Agent response
```

The lookup supports missing order IDs, lowercase IDs, surrounding whitespace, malformed IDs, unknown IDs, shipped orders, cancelled orders, returned orders, and missing delivery estimates.

### Privacy protection

The tool never exposes fields such as customer email, shipping address, billing address, internal notes, warehouse notes, risk scores, fraud scores, support tags, or other internal-only fields.

The safe-order layer uses a **whitelist approach** instead of returning the raw record and deleting a few known sensitive fields.

### Current status is authoritative

For cancelled and returned orders, stale delivery information is deliberately suppressed.

The agent also avoids inventing a delivery date when one is unavailable.

---

## 3. Multi-Turn Conversation

LangGraph session state is used to maintain relevant conversation context.

Example:

```text
User: Do you ship internationally?
Agent: Yes, currently to Canada.

User: What about Canada?
Agent: ...
```

and:

```text
User: Where is ORD-1007?
Agent: ...

User: When will it arrive?
Agent: ...
```

The same `thread_id` is reused within one conversation, while separate sessions remain isolated.

Recent history is intentionally bounded so unrelated information is not carried indefinitely.

---

## 4. Prompt and Retrieval Safety

The agent treats user input, retrieved passages, and tool results as **untrusted data**.

Retrieved documents cannot override application-level instructions.

The system refuses requests for system prompts, hidden instructions, secrets, internal notes, risk scores, or other internal-only data.

Internal migration material is not accepted as authoritative customer policy.

For company-specific questions, the assistant uses the supplied Aster & Row corpus rather than general model knowledge.

---

## 5. Safe Abstention and Human Handoff

The agent recommends human assistance when:
- the supplied documentation is insufficient
- current authoritative sources genuinely conflict
- a requested transactional action is unsupported
- policy requires human review
- an order ID cannot be found

The application cannot actually perform cancellations, refunds, replacements, address changes, or warranty approvals.

It therefore never claims one of these actions has been completed.

---

## 6. Structured Observability

When tracing is enabled, each user turn generates a sanitized JSONL trace at:

```text
logs/traces.jsonl
```

A trace can include:
- current user message
- recent conversation history
- route and routing reason
- retrieval query
- retrieved filename and heading
- document metadata
- semantic score
- lexical score
- precedence score
- final retrieval score
- tool calls
- normalized tool arguments
- sanitized tool results
- conflict detection state
- insufficient-information state
- human-review state
- handoff state and reason
- final customer-facing response
- request duration
- runtime errors

Sensitive order fields and credentials are removed before logging.

Inspect the latest trace with:

```bash
python -m scripts.show_last_trace
```

Clear traces with:

```bash
python -m scripts.clear_traces
```

---

# Architecture

```text
                                User
                                  │
                                  ▼
                         FastAPI Web / CLI
                                  │
                                  ▼
                            SupportAgent
                                  │
                                  ▼
                             LangGraph
                                  │
                 ┌────────────────┼─────────────────┐
                 │                │                 │
                 ▼                ▼                 ▼
              Safety           Router            Memory
                                  │
                     ┌────────────┴────────────┐
                     │                         │
                     ▼                         ▼
              Knowledge Route             Order Route
                     │                         │
                     ▼                         ▼
              Hybrid Retriever          Order Lookup Tool
                     │                         │
                     ▼                         ▼
                ChromaDB                 orders.json
                     │                         │
                     ▼                         ▼
            Metadata Precedence           Sanitizer
                     │                         │
                     ▼                         │
             Evidence Filtering               │
                     │                         │
                     ▼                         │
              Conflict / Review               │
                 Detection                    │
                     │                         │
                     └────────────┬────────────┘
                                  ▼
                            Grounded Answer
                                  │
                                  ▼
                       Sources + Handoff State
                                  │
                                  ▼
                         Sanitized JSONL Trace
```

---

# Technology Choices

| Component | Choice |
|---|---|
| Language | Python 3.10 |
| Agent orchestration | LangGraph |
| LLM integration | LangChain |
| Local LLM | Ollama `llama3.1:8b` |
| Embeddings | Ollama `nomic-embed-text` |
| Vector database | ChromaDB |
| Retrieval | Semantic + lexical + metadata-aware ranking |
| API | FastAPI |
| Frontend | HTML + CSS + JavaScript |
| Interface | Beige web chat UI + CLI |
| Evaluation | Deterministic custom evaluator + pytest |
| Observability | Sanitized structured JSONL traces |

### Why Ollama?

Ollama keeps the project self-contained and avoids external API-key requirements.

Because a local model can be less consistent for strict control-flow decisions, the application uses deterministic Python logic for reliability-sensitive behavior including request routing, order ID extraction, order lookup, privacy filtering, action safety, current-vs-superseded policy handling, conflict flags, safe abstention, and structured order response rendering.

---

# Repository Structure

```text
.
├── app/
│   ├── agent/
│   ├── evaluation/
│   ├── observability/
│   ├── retrieval/
│   ├── tools/
│   ├── web/
│   ├── api.py
│   ├── cli.py
│   └── config.py
├── data/
├── evaluation/
│   ├── original-cases.json
│   ├── visible-cases.json
│   └── results/
│       ├── baseline.json
│       └── final.json
├── knowledge-base/
├── scripts/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Setup

## 1. Clone the repository

```bash
git clone https://github.com/Ankita18726/AI-Agent-Intern-Test.git
cd AI-Agent-Intern-Test
```

## 2. Create a virtual environment

### Windows

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 4. Install Ollama

Install Ollama and verify:

```bash
ollama --version
```

## 5. Pull the required models

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Verify:

```bash
ollama list
```

## 6. Configure environment variables

Copy `.env.example` to `.env`.

### Windows

```cmd
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Example:

```env
LLM_MODEL=llama3.1:8b
EMBEDDING_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_PERSIST_DIRECTORY=./chroma_db
LOG_DIRECTORY=./logs
TRACE_FILE=traces.jsonl
DEBUG=false
ENABLE_TRACING=true
```

No real credentials or API keys are required.

---

# Build the Knowledge Index

```bash
python -m scripts.build_index --clean
```

The index builder loads all supplied Markdown documents, preserves metadata, creates heading-aware chunks, generates local embeddings, and builds the ChromaDB index.

---

# Run the Web Interface

```bash
python -m uvicorn app.api:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The web interface provides a beige customer-support chat UI with suggested prompts, source cards, handoff warnings, multi-turn sessions, and secure order-status interaction.

---

# Run the CLI

```bash
python -m app.cli
```

Example:

```text
You: How long do I have to return an unused backpack?

Agent:
A regular customer has 30 calendar days from delivery
to return an unused backpack.

Sources:
- 01-returns-policy-current.md — Standard return window
```

---

# Tests

Run the complete pytest suite:

```bash
pytest -v
```

The tests cover document loading, chunk creation, metadata preservation, policy precedence, order-ID normalization, order lookup, privacy, router behavior, session isolation, prompt safety, evidence filtering, observability sanitization, and regression cases.

---

# Evaluation

Run the complete behavior-level evaluation suite:

```bash
python -m app.evaluation.runner --label final
```

The evaluator runs **15 supplied visible cases + 7 original cases = 22 total cases**.

It reports individual PASS / FAIL status, failure reasons, overall score, category breakdown, visible-vs-original suite performance, and saves the result to `evaluation/results/`.

---

# Evaluation Results

## Overall

| Evaluation | Passed | Score |
|---|---:|---:|
| Baseline | 15 / 22 | 68.2% |
| Final | 19 / 22 | 86.4% |

The evaluation improved by **18.2 percentage points** from the early baseline.

## Final Results by Category

| Category | Result |
|---|---:|
| Retrieval | 2 / 2 — 100% |
| Conversation | 2 / 2 — 100% |
| Groundedness | 2 / 2 — 100% |
| Tool use | 4 / 4 — 100% |
| Tool reliability | 4 / 4 — 100% |
| Privacy | 1 / 1 — 100% |
| Prompt security | 2 / 2 — 100% |
| Abstention | 1 / 1 — 100% |
| Source conflict | 0 / 1 — 0% |
| Action safety | 1 / 2 — 50% |

All 3 remaining failures are wording-completeness issues in already-correct detection/routing logic, not incorrect answers or safety failures — detailed in the Bug Diary.

## Suite Breakdown

| Suite | Result |
|---|---:|
| Supplied visible cases | 13 / 15 — 86.7% |
| Original cases | 6 / 7 — 85.7% |
| Overall | 19 / 22 — 86.4% |

### Remaining failing cases

The final evaluation still has three known failures:

1. `genuine-active-source-conflict`
   - the application correctly detects the active conflict and recommends handoff, but the generated wording can omit one or more required conflict details.

2. `address-change-not-completed`
   - the request is correctly routed as an unsupported transactional action and handoff is triggered, but free-form response wording may omit the exact explicit statement that the application cannot change the address.

These limitations are documented rather than hidden.

---

# Bug Diary

## Bug 1 — Superseded return policy created a false conflict

**Reproduction**

```text
How long do I have to return an unused backpack?
```

**Failure:** The agent found the current 30-day policy but also surfaced the superseded 45-day policy as a current conflict.

**Root cause:** Semantic retrieval returned both active and superseded passages, and both were initially passed into answer generation.

**Fix:** Added metadata-aware evidence filtering and limited genuine conflict detection to current authoritative sources.

**Regression coverage:** `standard-return-window`, legacy-policy conflict test, evidence-filter regression test.

---

## Bug 2 — Standalone shipping question inherited unrelated return context

**Reproduction**

```text
How long is the return window?
Do you ship internationally?
```

**Failure:** The shipping query retrieved return-policy content.

**Root cause:** An early query-rewriting rule treated every short message as a follow-up.

**Fix:** History is now used only for genuinely referential follow-ups such as `What about Canada?` and `When will it arrive?`.

**Regression coverage:** `canada-multiturn`, short-standalone-query regression test.


---

## Bug 3 — Address-change request bypassed action-safety routing

**Reproduction**

```text
Change the shipping address on ORD-1007 for me.
```

**Failure:** Early routing logic checked for the literal phrase `change address`, which did not match when words such as `shipping` occurred between them.

**Fix:** Replaced strict substring matching with regex-based transactional-action detection.

**Regression coverage:** `address-change-not-completed` and address-routing unit tests.

---

# Observability

Enable tracing with:

```env
ENABLE_TRACING=true
```

Inspect the latest trace:

```bash
python -m scripts.show_last_trace
```

The logging layer is designed not to intentionally record customer email, shipping or billing addresses, internal notes, warehouse notes, risk scores, support tags, API keys, secrets, or passwords.

---

# Security and Privacy Decisions

## Raw orders are never sent to the model

Only the result of an explicit order lookup is made available to the agent.

## Customer-safe whitelisting

Order responses are created from explicitly allowed fields rather than copying the raw order record.

## Internal retrieved text is treated as data

Documents may contain text that looks like instructions. Retrieved text does not control the application.

## Read-only action model

The system deliberately has no tools for cancellation, refund execution, replacement execution, warranty approval, or address modification.

---

# Known Limitations

1. **Local model latency** — `llama3.1:8b` can be slow on CPU-only hardware.
2. **Three known evaluation gaps** — see "Remaining failing cases" above for detail.
3. **Conflict detection** — intentionally conservative; production should use more general claim-level contradiction detection.
4. **Authentication** — possession of an order ID is treated as sufficient only because the assignment explicitly allows it.
5. **Read-only order operations** — the application can inspect status but cannot mutate orders.

---

# What I Would Improve Before Production

- identity verification before exposing order details
- larger labeled retrieval benchmarks
- claim-level provenance verification
- rate limiting
- abuse monitoring
- real support-ticket / human-handoff integration
- durable tracing with OpenTelemetry or an equivalent system

---

# AI Coding Tools Used

I used **ChatGPT** as a coding assistant for targeted debugging and evaluation design during development.

All generated suggestions were manually reviewed, tested, and adjusted before inclusion — the core architecture, routing logic, and safety decisions were designed and implemented directly.

## Example of an incorrect AI-generated suggestion

An early suggestion attempted to calculate an empty-safe maximum using:

```python
max([scores], 0)
```

This produced:

The corrected implementation was:

```python
max(
    (score for score in scores),
    default=0,
)
```

Another early suggestion allowed superseded return-policy evidence to reach answer generation, causing the old 45-day policy to appear as a false conflict with the active 30-day policy.

Evaluation exposed the failure, and the design was changed to use metadata-aware generation filtering and current-authority conflict detection.

> AI-generated implementation suggestions are treated as hypotheses to test, not as trusted code.

---

# Example Behaviors

## Current return policy

```text
User:
How long do I have to return an unused backpack?

Agent:
A regular customer has 30 calendar days from delivery to
return an unused backpack.

Sources:
- 01-returns-policy-current.md — Standard return window
```

## Order lookup

```text
User:
Where is ORD-1007?

Agent:
Order ORD-1007 has been shipped with UPS.
The tracking number is ...
The estimated delivery date is August 22, 2026.
```

## Missing order ID

```text
User:
Where is my order?

Agent:
Please provide your order ID, for example ORD-1007.
```

## Safe abstention

```text
User:
Are all fabrics and adhesives in your bags vegan?

Agent:
The supplied Aster & Row documentation does not provide
enough information to confirm this. I don't want to guess.
Please contact human support for confirmation.
```

# Evaluation Files

Supplied cases:

```text
evaluation/visible-cases.json
```

Original cases:

```text
evaluation/original-cases.json
```

Saved results:

```text
evaluation/results/baseline.json
evaluation/results/final.json
```

Compare baseline and final results with:

```bash
python -m scripts.compare_evaluations
```

---

# Useful Commands

## Activate environment

```cmd
.venv\Scripts\activate
```

## Build index

```bash
python -m scripts.build_index --clean
```

## Run web app

```bash
python -m uvicorn app.api:app --reload
```

## Run CLI

```bash
python -m app.cli
```

## Run tests

```bash
pytest -v
```

## Run full evaluation

```bash
python -m app.evaluation.runner --label final
```

## Run one evaluation case

```bash
python -m app.evaluation.runner --case valid-order-lookup --verbose
```

## Show latest trace

```bash
python -m scripts.show_last_trace
```

# Final Result

The final agent passes **19 / 22 evaluation cases — 86.4%**.

It achieves **100% final performance** in retrieval, conversation, groundedness, tool reliability, tool use, privacy, prompt security, and abstention.

The remaining failures are explicitly documented rather than hidden.

The project demonstrates a reliability-first support-agent design where **retrieval, tool access, privacy, source precedence, abstention, and handoff behavior are deliberately controlled rather than left entirely to free-form model generation**.

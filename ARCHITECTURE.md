# Zomato AI Restaurant Recommendation Service — Architecture Document

## 1. Overview

This document describes the architecture for an AI-powered restaurant recommendation service inspired by Zomato. The system takes user preferences (place, rating, and optionally price and cuisine), fetches and cleans data from Hugging Face, processes it with an LLM, and surfaces recommendations through a UI.

**Core flow:**  
**User Input → Fetch/Clean Data → LLM Processing → Display Recommendations via UI**

---

## 2. High-Level Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Input    │────▶│ Fetch/Clean Data │────▶│ LLM Processing  │────▶│  UI (Display)   │
│  (Place, etc.)  │     │  (HF API + ETL)  │     │ (Recommendations)│     │ Recommendations │
└─────────────────┘     └──────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 3. Input Specification

| Input   | Mandatory | Description / Constraints                          |
|---------|-----------|----------------------------------------------------|
| **Place**   | Yes       | Location / city / area for restaurant search       |
| **Rating**  | Yes       | Minimum rating filter (e.g. 4.0)                   |
| **Price**   | No        | Budget / price range (e.g. 1500)                  |
| **Cuisine** | No        | Preferred cuisines (one or more)                  |

All inputs are validated and normalized before use in data fetch and LLM steps.

---

## 4. Data Source

- **Provider:** Hugging Face API  
- **Dataset:** `ManikaSaini/zomato-restaurant-recommendation` (~51,717 rows)  
- **Usage:** Fetch full dataset via Hugging Face Hub / `datasets` API. Filter and clean records before passing to the recommendation pipeline. Use full dataset by default for maximum coverage; set `E2E_SAMPLE_SIZE` to limit for faster runs.

---

## 5. Data Cleaning Rules Pipeline

A dedicated **Data Cleaning Pipeline** runs on raw dataset rows before filtering and LLM processing.

| Field    | Rule | Example |
|----------|------|--------|
| **Price**  | Convert to integer: strip commas, spaces, currency symbols; parse as int. | `"1,500"` → `1500`, `"₹2,000"` → `2000` |
| **Rating** | Extract numeric float from string; ignore suffix (e.g. `/5`). Treat `"NEW"` as `0.0` to retain unrated restaurants. | `"4.1/5"` → `4.1`, `"4.5"` → `4.5`, `"NEW"` → `0.0` |
| **Cuisines** | Parse delimited string into a list/array of trimmed strings; normalize separators (comma, pipe, etc.). | `"North Indian, Chinese"` → `["North Indian", "Chinese"]` |

- **Validation:** Drop or flag rows where required fields (e.g. place, rating) cannot be cleaned or are missing.  
- **Output:** Clean records (e.g. JSON/DataFrame) consumed by the filtering and LLM modules.

---

## 6. Phased Implementation Plan

The project is split into phases. **Do not start implementation** until the design is approved; this document is architecture-only.

---

### Phase 1: Project Setup & Data Access

**Goal:** Reproducible environment and reliable access to the dataset.

- **1.1** Define project structure (e.g. `src/`, `data/`, `tests/`, config).
- **1.2** Set up dependency management (e.g. `requirements.txt` / `pyproject.toml`) including:
  - Hugging Face `datasets` (or `huggingface_hub`)
  - Python version and any env/venv notes
- **1.3** Implement **dataset fetch** from `ManikaSaini/zomato-restaurant-recommendation` (load full or sampled dataset).
- **1.4** Document required env vars (e.g. `HF_TOKEN` if needed) and add a `.env.example`.

**Deliverables:** Project skeleton, working script/module to fetch the dataset, dependency file, and minimal docs for running the fetch.

---

### Phase 2: Data Cleaning Pipeline

**Goal:** Reusable, testable cleaning logic aligned with the rules above.

- **2.1** Implement **cleaning functions** per field:
  - **Price:** string → integer (strip commas/symbols, parse).
  - **Rating:** string → float (handle `X.X/5` and plain numbers).
  - **Cuisines:** string → list of strings (split, strip, normalize).
- **2.2** Add a **pipeline orchestrator** that:
  - Takes raw rows (from Phase 1).
  - Applies cleaning rules.
  - Validates and drops invalid/incomplete rows.
  - Outputs clean records (e.g. in-memory structures or staged files).
- **2.3** Unit tests for each cleaner and the pipeline (edge cases: empty, malformed, different formats).
- **2.4** Optional: persist cleaned dataset (e.g. CSV/Parquet) for faster reruns.

**Deliverables:** Cleaning module, pipeline entrypoint, tests, and optional cleaned dataset artifact.

---

### Phase 3: Filtering & LLM Integration

**Goal:** Filter cleaned data by user inputs and use an LLM to generate natural-language recommendations.

- **3.1** **Filtering layer:**
  - Inputs: Place (mandatory), Rating (mandatory), Price (optional), Cuisine (optional).
  - Apply filters on cleaned data: place matches `location` or `listed_in(city)` (for broader area coverage), rating ≥ user rating, price ≤ user price if given, cuisine overlap if given.
  - Return a candidate set of restaurants (e.g. top N or all matching).
- **3.2** **LLM integration:**
  - **LLM provider: Groq** — use the Groq API for inference (e.g. `groq` Python client, `GROQ_API_KEY` in env).
  - Define a **prompt template:** user inputs + candidate restaurants → request for ranked/summarized recommendations with short reasoning.
  - Implement client calls (API key via env), error handling, and optional retries.
- **3.3** **Recommendation service API:**
  - Single entrypoint: `(place, rating, price?, cuisine?) → recommendations`.
  - Internally: fetch/load cleaned data → filter → build prompt → call LLM → parse response.
  - Return structured output (e.g. list of recommended restaurants + rationale) for the UI.

**Deliverables:** Filtering logic, LLM client and prompt design, recommendation service (e.g. function or internal API), and env configuration for API keys.

---

### Phase 4: Backend API (Optional but Recommended)

**Goal:** Expose the recommendation service over HTTP for the UI.

- **4.1** Add a small **HTTP API** (e.g. FastAPI/Flask):
  - POST (or GET) endpoint accepting: `place`, `rating`, optional `price`, optional `cuisine`.
  - Validates inputs and returns JSON: list of recommendations (name, reason, rating, cuisine, price, address) + summary + metadata.
  - GET `/locations` and GET `/cuisines` for dropdown options; includes `listed_in(city)` for broader area selection.
- **4.2** CORS and basic security (e.g. rate limiting, env-based config).
- **4.3** Document the API (e.g. OpenAPI/Swagger).

**Deliverables:** Running API server, documented endpoint(s), and optional Docker/config for deployment.

---

### Phase 5: UI for Recommendations

**Goal:** A dedicated UI page where users can submit inputs and see recommendations.

- **5.1** **UI stack:** Choose a simple front-end (e.g. React, Vue, or plain HTML/JS) and build tool (e.g. Vite, Next.js, or static).
- **5.2** **Recommendations page:**
  - **Input form:** Place (dropdown from locations), Rating (required), Price (optional), Cuisine (optional).
  - **Submit:** Call backend API (Phase 4) or, if no API, a server-side handler that uses the recommendation service.
  - **Results:** Display an intro summary + recommendation tiles (cards) with: name, rating badge, cuisines, avg price, address, and "Why you'll like it" (LLM rationale). Light theme, wide layout (max-width ~1200px).
- **5.3** **UX:** Loading state, error messages, and empty state when no results.
- **5.4** **Integration:** Wire UI to the recommendation backend; document how to run UI and backend together (e.g. dev scripts, env).

**Deliverables:** Single-page (or multi-page with recommendations as main page) UI, wired to the recommendation service/API, and run instructions.

---

## 7. End-to-End Data Flow (Summary)

1. **User** enters Place, Rating, and optionally Price and Cuisine in the UI.
2. **UI** sends these to the Backend API (or server-side handler).
3. **Backend** loads (or uses cached) **cleaned data** from the Data Cleaning Pipeline (fed by Hugging Face dataset).
4. **Backend** **filters** cleaned data by place, rating, price, cuisine.
5. **Backend** builds an **LLM prompt** with user inputs + candidate restaurants and calls the **LLM**.
6. **LLM** returns ranked/summarized recommendations (and optionally short reasoning).
7. **Backend** parses and returns **structured recommendations** to the UI.
8. **UI** **displays** recommendations (and any error/empty states).

---

## 8. Technology Suggestions (Reference Only)

- **Language:** Python for data fetch, cleaning, filtering, and LLM service.
- **Dataset:** `datasets` or `huggingface_hub` for Hugging Face.
- **LLM:** Groq API (e.g. `groq` Python client); keep provider behind an interface for flexibility.
- **Backend API:** FastAPI or Flask.
- **UI:** React/Vite or Next.js for a modern SPA; alternatively simple HTML/JS + fetch.
- **Config:** Environment variables for API keys and dataset options; optional `.env` and `.env.example`.

---

## 9. Out of Scope (Current Document)

- User accounts, auth, or persistence of user history.
- Real-time or streaming LLM responses (can be added later).
- Production deployment, scaling, or observability (can be a future phase).

---

## 10. Document Control

- **Version:** 1.1  
- **Purpose:** Architecture document; reflects current implementation.  
- **Last phase:** Phase 5 — UI page for the Zomato AI Restaurant Recommendation Service.
- **Recent updates:** Full dataset usage (~44k cleaned rows), "NEW" rating retention, `listed_in(city)` place matching, tile layout + light theme UI.

---

## 11. Integration & End-to-End

The repo includes scripts and fixes so the full flow works:

- **Phase 1 → Phase 2:** `scripts/e2e_pipeline.py` fetches the **full dataset** (~51k rows), converts to rows, cleans with Phase 2, normalizes `location`/`name` (with fallback to `listed_in(city)`), and writes a CSV for Phase 4. Run with Phase 1 venv: `phase1/.venv/bin/python scripts/e2e_pipeline.py`. Set `E2E_SAMPLE_SIZE=N` to limit rows for faster runs.
- **Phase 4 data loader:** Loads CSV from `CLEANED_DATA_PATH` and normalizes rows so `city` → `location` and `restaurant name` → `name` when those keys are missing (for Phase 3 filter/prompts).
- **Phase 4 → Phase 3:** `phase4/src/recommendation_service.py` adds `phase3` to the path and calls `get_recommendations(cleaned_rows, ...)`. Run the API from repo root or with `phase3` on `PYTHONPATH` so the import succeeds.
- **E2E tests:** `phase4/.venv/bin/python scripts/e2e_test.py` runs integration tests (fixture data + mocked Phase 3, and optional real-CSV load). See `scripts/README.md` for full E2E with real backend and UI.

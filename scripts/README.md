# E2E Integration Scripts

## Data flow (end-to-end)

```
User Input (Phase 5 UI) → Phase 4 API → Phase 3 (filter + Groq LLM) → Phase 2 (clean) → Phase 1 (fetch)
                                                                              ↑
Response: recommendations ← Phase 4 ← Phase 3 ← cleaned rows ← CSV or in-memory
```

## Run E2E pipeline (Phase 1 → Phase 2 → CSV)

Produces a cleaned CSV for Phase 4. Requires Phase 1 and Phase 2 dependencies (use phase1 venv).

```bash
# From repo root
E2E_SAMPLE_SIZE=100 phase1/.venv/bin/python scripts/e2e_pipeline.py
# Output: phase4/data/cleaned.csv (or CLEANED_OUTPUT path)
```

## Run E2E tests (no Groq, no HF download)

Uses fixture data and mocked Phase 3. Requires Phase 4 dependencies.

```bash
# From repo root
phase4/.venv/bin/python scripts/e2e_test.py
```

## Full E2E with real backend

1. Generate data: `E2E_SAMPLE_SIZE=200 phase1/.venv/bin/python scripts/e2e_pipeline.py`
2. Start Phase 4 API with the CSV:
   ```bash
   cd phase4 && CLEANED_DATA_PATH=./data/cleaned.csv uvicorn src.app:app --port 8000
   ```
3. (Optional) Start Phase 5 UI: `cd phase5 && npm run dev` → http://localhost:5173
4. Call API: `curl -X POST http://localhost:8000/recommendations -H "Content-Type: application/json" -d '{"place":"Banashankari","rating":4.0}'`

For real LLM recommendations, set `GROQ_API_KEY` and ensure Phase 3 is on the path (run Phase 4 from repo root or add phase3 to `PYTHONPATH`).

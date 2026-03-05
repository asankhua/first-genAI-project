# Run & Test Locally

## Quick Start (all phases connected)

```bash
# 1. Install dependencies (one-time)
python3 -m venv phase1/.venv phase2/.venv phase3/.venv phase4/.venv
phase1/.venv/bin/pip install -r phase1/requirements.txt
phase2/.venv/bin/pip install -r phase2/requirements.txt
phase3/.venv/bin/pip install -r phase3/requirements.txt
phase4/.venv/bin/pip install -r phase4/requirements.txt
cd phase5 && npm install

# 2. Add GROQ_API_KEY to phase3/.env (optional, for LLM)

# 3. Run full stack
./run_all.sh
# → UI: http://localhost:5173  |  API: http://localhost:8000/docs
```

---

## Status: All phases connected ✓

| Phase | Tests | Status |
|-------|-------|--------|
| Phase 1 (Fetch) | 6 passed | ✓ |
| Phase 2 (Clean) | 29 passed | ✓ |
| Phase 3 (Filter + Groq) | 17 passed, 2 skipped | ✓ |
| Phase 4 (API) | 12 passed | ✓ |
| E2E Integration | 3 passed | ✓ |

---

## 1. Install dependencies (one-time)

### Backend (Python)

```bash
cd /Users/asankhua/Cursor/genAI/first-genAI-project

# Create venvs and install (if not already done)
python3 -m venv phase1/.venv
python3 -m venv phase2/.venv
python3 -m venv phase3/.venv
python3 -m venv phase4/.venv

phase1/.venv/bin/pip install -r phase1/requirements.txt
phase2/.venv/bin/pip install -r phase2/requirements.txt
phase3/.venv/bin/pip install -r phase3/requirements.txt
phase4/.venv/bin/pip install -r phase4/requirements.txt
```

### Frontend (Phase 5 – needs Node.js/npm)

```bash
cd phase5
npm install
```

**Install Node.js/npm if needed:** https://nodejs.org or `brew install node`

---

## 2. Generate cleaned data (if needed)

```bash
cd /Users/asankhua/Cursor/genAI/first-genAI-project
E2E_SAMPLE_SIZE=100 phase1/.venv/bin/python scripts/e2e_pipeline.py
```

Output: `phase4/data/cleaned.csv`

---

## 3. Run the backend (Phase 4 API)

```bash
cd /Users/asankhua/Cursor/genAI/first-genAI-project
chmod +x run_backend.sh
./run_backend.sh
```

**Or run everything (backend + frontend) in one command:**

```bash
./run_all.sh
```

**Or manually (backend only, from repo root):**

```bash
cd phase4
ROOT=$(cd .. && pwd)
CLEANED_DATA_PATH=$ROOT/phase4/data/cleaned.csv PYTHONPATH=$ROOT/phase3 .venv/bin/uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 4. Run the frontend (Phase 5 UI)

In a **new terminal**:

```bash
cd /Users/asankhua/Cursor/genAI/first-genAI-project/phase5
npm run dev
```

---

## URLs for local testing

| Service | URL |
|---------|-----|
| **Phase 5 UI (React)** | http://localhost:5173 |
| **Streamlit UI** | http://localhost:5175 |
| **Phase 4 API docs (Swagger)** | http://localhost:8000/docs |
| **Phase 4 health check** | http://localhost:8000/health |
| **API test (curl)** | `curl -X POST http://localhost:8000/recommendations -H "Content-Type: application/json" -d '{"place":"Banashankari","rating":4.0}'` |

---

## 5. Run Streamlit (alternative frontend)

Streamlit uses the same Phase 4 backend—same UI, business logic, and API. Start backend first, then:

```bash
pip install -r requirements.txt   # streamlit + requests
./run_streamlit.sh
# → Streamlit: http://localhost:5175
```

Or: `streamlit run streamlit_app.py --server.port 5175`

For a remote backend: `API_BASE_URL=http://your-api:8000 streamlit run streamlit_app.py`

---

## Environment variables (.env)

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

**GROQ_API_KEY** (for AI-powered recommendations): Put your key in **`.env`** at the project root:

```
GROQ_API_KEY=your_key_here
```

All phases load the root `.env` automatically. Without `GROQ_API_KEY`, the API returns filtered results (no LLM).

---

## Quick test from terminal

```bash
# Health
curl http://localhost:8000/health

# Recommendations (replace with your place)
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"place":"Banashankari","rating":4.0,"price":1000}'
```

---

## Run all tests

```bash
cd /Users/asankhua/Cursor/genAI/first-genAI-project

phase1/.venv/bin/python -m pytest phase1/tests/ -v
phase2/.venv/bin/python -m pytest phase2/tests/ -v
phase3/.venv/bin/python -m pytest phase3/tests/ -v
phase4/.venv/bin/python -m pytest phase4/tests/ -v
phase4/.venv/bin/python scripts/e2e_test.py
```

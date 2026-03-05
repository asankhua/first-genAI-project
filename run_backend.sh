#!/bin/bash
# Run Phase 4 API from repo root so Phase 3 is on path
# Usage: ./run_backend.sh

cd "$(dirname "$0")"
ROOT="$(pwd)"
export CLEANED_DATA_PATH="${CLEANED_DATA_PATH:-$ROOT/phase4/data/cleaned.csv}"

# Load root .env first, then phase3/.env for GROQ_API_KEY
if [ -f ".env" ]; then
  set -a
  . ./.env 2>/dev/null || true
  set +a
fi
if [ -z "$GROQ_API_KEY" ] && [ -f "phase3/.env" ]; then
  export GROQ_API_KEY=$(grep -E '^GROQ_API_KEY=' phase3/.env 2>/dev/null | cut -d= -f2-)
fi

# Ensure cleaned data exists (use full dataset for maximum coverage)
if [ ! -f "$CLEANED_DATA_PATH" ]; then
  echo "Generating cleaned data from full Hugging Face dataset (Phase 1+2)..."
  phase1/.venv/bin/python scripts/e2e_pipeline.py || exit 1
fi

# Run from repo root so phase3 is found before phase4 (avoids 'src' name clash)
export PYTHONPATH="${ROOT}/phase3:${ROOT}/phase4:${PYTHONPATH}"
cd "$ROOT"
phase4/.venv/bin/uvicorn phase4.src.app:app --host 0.0.0.0 --port 8000 --reload

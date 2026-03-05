#!/bin/bash
# Start full stack: Phase 1→2 data, Phase 4 backend, Phase 5 frontend.
# Usage: ./run_all.sh
# Press Ctrl+C to stop both backend and frontend.

set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"

# Ensure venvs exist
for phase in phase1 phase4; do
  if [ ! -d "$phase/.venv" ]; then
    echo "Missing $phase/.venv. Run: python3 -m venv $phase/.venv && $phase/.venv/bin/pip install -r $phase/requirements.txt"
    exit 1
  fi
done

# Phase 3 venv (needed for recommendation_service)
if [ ! -d "phase3/.venv" ]; then
  echo "Missing phase3/.venv. Run: python3 -m venv phase3/.venv && phase3/.venv/bin/pip install -r phase3/requirements.txt"
  exit 1
fi

# Phase 5 (Node)
if [ ! -d "phase5/node_modules" ]; then
  echo "Installing Phase 5 dependencies..."
  (cd phase5 && npm install)
fi

# Generate cleaned data if needed
CLEANED_PATH="$ROOT/phase4/data/cleaned.csv"
if [ ! -f "$CLEANED_PATH" ]; then
  echo "Generating cleaned data (Phase 1+2)..."
  E2E_SAMPLE_SIZE=200 CLEANED_OUTPUT="$CLEANED_PATH" phase1/.venv/bin/python scripts/e2e_pipeline.py
fi

# Load root .env first, then phase3/.env for GROQ_API_KEY
if [ -f ".env" ]; then
  set -a
  . ./.env 2>/dev/null || true
  set +a
fi
if [ -z "$GROQ_API_KEY" ] && [ -f "phase3/.env" ]; then
  export GROQ_API_KEY=$(grep -E '^GROQ_API_KEY=' phase3/.env 2>/dev/null | cut -d= -f2-)
fi

export CLEANED_DATA_PATH="$CLEANED_PATH"
export PYTHONPATH="${ROOT}/phase3:${PYTHONPATH}"

# Start backend in background
BACKEND_PID=""
cleanup() {
  if [ -n "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null || true
  fi
  exit 0
}
trap cleanup SIGINT SIGTERM EXIT

echo "Starting Phase 4 backend on http://localhost:8000 ..."
cd phase4
.venv/bin/uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd "$ROOT"

# Wait for backend to be ready
for i in {1..15}; do
  if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "Starting Phase 5 frontend on http://localhost:5173 ..."
echo ""
echo "  UI:  http://localhost:5173"
echo "  API: http://localhost:8000/docs"
echo "  Press Ctrl+C to stop both"
echo ""

cd phase5
npm run dev

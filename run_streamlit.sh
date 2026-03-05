#!/bin/bash
# Run Streamlit + backend together. Starts backend automatically if not running.
# Usage: ./run_streamlit.sh
# Streamlit: http://localhost:5175  |  API: http://localhost:8000

set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"

# Load root .env (API_BASE_URL, GROQ_API_KEY, etc.)
if [ -f ".env" ]; then
  set -a
  . ./.env 2>/dev/null || true
  set +a
fi
if [ -z "$GROQ_API_KEY" ] && [ -f "phase3/.env" ]; then
  export GROQ_API_KEY=$(grep -E '^GROQ_API_KEY=' phase3/.env 2>/dev/null | cut -d= -f2-)
fi

export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
export CLEANED_DATA_PATH="${CLEANED_DATA_PATH:-$ROOT/phase4/data/cleaned.csv}"
export PYTHONPATH="${ROOT}/phase3:${ROOT}/phase4:${PYTHONPATH}"

# Ensure venvs and data exist
for phase in phase1 phase4; do
  if [ ! -d "$phase/.venv" ]; then
    echo "Missing $phase/.venv. Run: python3 -m venv $phase/.venv && $phase/.venv/bin/pip install -r $phase/requirements.txt"
    exit 1
  fi
done
if [ ! -d "phase3/.venv" ]; then
  echo "Missing phase3/.venv for Phase 4 dependency."
  exit 1
fi

if [ ! -f "$CLEANED_DATA_PATH" ]; then
  echo "Generating cleaned data (Phase 1+2)..."
  E2E_SAMPLE_SIZE=200 CLEANED_OUTPUT="$CLEANED_DATA_PATH" phase1/.venv/bin/python scripts/e2e_pipeline.py
fi

# Check if backend is already running; start it if not
BACKEND_PID=""
cleanup() {
  [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM EXIT

if ! curl -sf http://localhost:8000/health >/dev/null 2>&1; then
  echo "Starting Phase 4 backend on http://localhost:8000 ..."
  phase4/.venv/bin/uvicorn phase4.src.app:app --host 0.0.0.0 --port 8000 &
  BACKEND_PID=$!
  for i in {1..15}; do
    if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
      echo "Backend ready."
      break
    fi
    sleep 1
  done
fi

# Ensure streamlit deps
phase4/.venv/bin/pip install -q streamlit requests 2>/dev/null || true

echo ""
echo "  Streamlit: http://localhost:5175"
echo "  API:       http://localhost:8000/docs"
echo "  Press Ctrl+C to stop"
echo ""

phase4/.venv/bin/streamlit run streamlit_app.py --server.port 5175 --server.address 0.0.0.0 --server.headless true

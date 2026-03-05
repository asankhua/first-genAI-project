#!/bin/bash
# Run Streamlit frontend (calls Phase 4 backend API).
# Backend must be running: ./run_backend.sh (or ./run_all.sh)
# Usage: ./run_streamlit.sh
# Streamlit: http://localhost:5175

set -e
cd "$(dirname "$0")"

# Load root .env (API_BASE_URL, etc.)
if [ -f ".env" ]; then
  set -a
  . ./.env 2>/dev/null || true
  set +a
fi
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

if [ ! -d "phase4/.venv" ]; then
  echo "Missing phase4/.venv. Run: python3 -m venv phase4/.venv && phase4/.venv/bin/pip install -r phase4/requirements.txt"
  exit 1
fi

phase4/.venv/bin/pip install -q streamlit requests 2>/dev/null || true
phase4/.venv/bin/streamlit run streamlit_app.py --server.port 5175 --server.address 0.0.0.0 --server.headless true

#!/usr/bin/env bash
# ============================================================================
#  OpenGPT - Linux/Mac startup script
#  Starts the FastAPI backend (port 8000) and the React frontend (port 3000).
# ============================================================================

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV="$ROOT/.venv"

# --- Start Backend ----------------------------------------------------------
if [ -f "$VENV/bin/activate" ]; then
    ( cd "$BACKEND" && bash -c "source '$VENV/bin/activate' && python main.py" ) &
else
    ( cd "$BACKEND" && python main.py ) &
fi
BACKEND_PID=$!

# --- Start Frontend ---------------------------------------------------------
( cd "$FRONTEND" && npm install && npm run dev ) &
FRONTEND_PID=$!

echo ""
echo "Starting backend (http://localhost:8000) and frontend (http://localhost:3000)..."
echo "Press Ctrl+C to stop both servers."

cleanup() {
    echo ""
    echo "Stopping servers..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    wait 2>/dev/null || true
    exit 0
}
trap cleanup INT TERM

wait

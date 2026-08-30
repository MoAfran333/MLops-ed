#!/usr/bin/env bash

set -e

# ANSI colors
CLIENT_COLOR=$'\033[1;36m'  # Cyan
SERVER_COLOR=$'\033[1;33m'  # Yellow
RESET=$'\033[0m'

cleanup() {
    echo
    echo "Stopping development servers..."

    kill "$CLIENT_PID" "$SERVER_PID" 2>/dev/null || true

    wait "$CLIENT_PID" "$SERVER_PID" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

echo "Starting development servers..."

# -------------------------
# Client
# -------------------------

(
    cd client
    bun run dev 2>&1 | sed "s/^/${CLIENT_COLOR}[CLIENT]${RESET} /"
) &

CLIENT_PID=$!

# -------------------------
# Server
# -------------------------

(
    uvicorn server.main:app --reload --port 5000 2>&1 |
        sed "s/^/${SERVER_COLOR}[SERVER]${RESET} /"
) &

SERVER_PID=$!

# Keep script alive
wait
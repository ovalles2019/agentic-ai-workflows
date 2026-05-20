#!/usr/bin/env bash
# macOS: ':' in the parent folder name breaks venv here — use /tmp venv instead.
set -euo pipefail

VENV="${VENV_PATH:-/tmp/agentic-workflows-venv}"
ROOT="$(cd "$(dirname "$0")" && pwd)"

python3 -m venv "$VENV"
# shellcheck source=/dev/null
source "$VENV/bin/activate"
pip install -U pip
pip install -r "$ROOT/requirements.txt"

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
fi

echo ""
echo "Setup complete. Activate with:"
echo "  source $VENV/bin/activate"
echo "Run demos with:"
echo "  cd \"$ROOT\" && python run.py all"

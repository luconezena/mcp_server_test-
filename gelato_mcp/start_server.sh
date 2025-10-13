#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f "venv/bin/python" ]; then
  echo "Creating venv..."
  python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
python server_http.py

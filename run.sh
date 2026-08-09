#!/bin/bash
cd "$(dirname "$0")"
echo "Starting EvidenceMap..."
echo "Open http://localhost:8501 in your browser"
streamlit run app/main.py --server.port 8501 --server.headless true

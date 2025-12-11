#!/bin/bash
echo "Starting AIDesk Backend Server..."
echo ""
cd "$(dirname "$0")"
uvicorn main:app --reload --port 8000


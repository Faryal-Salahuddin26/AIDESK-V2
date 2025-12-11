@echo off
echo Starting AIDesk Backend Server...
echo.
cd /d %~dp0
uvicorn main:app --reload --port 8000
pause


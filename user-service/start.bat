@echo off
echo Starting User Service on port 8001...
cd /d %~dp0
uvicorn main:app --port 8001 --reload
pause


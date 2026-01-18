@echo off
echo Starting Order Service on port 8002...
cd /d %~dp0
uvicorn main:app --port 8002 --reload
pause


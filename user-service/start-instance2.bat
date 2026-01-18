@echo off
echo Starting User Service Instance 2 on port 8003...
cd /d %~dp0
uvicorn main:app --port 8003 --reload
pause


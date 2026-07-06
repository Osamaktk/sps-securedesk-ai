@echo off
cd /d e:\sps-securedesk-ai
.venv\Scripts\python.exe -m uvicorn ai.main:app --host 127.0.0.1 --port 8001 --log-level info --app-dir e:\sps-securedesk-ai --reload

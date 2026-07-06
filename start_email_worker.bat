@echo off
echo Starting Email Worker...
cd /d e:\sps-securedesk-ai
.venv\Scripts\python.exe -m email_worker.main
pause

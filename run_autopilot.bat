@echo off
set BRIAN2_BACKEND=numpy
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
cd /d C:\Users\nicet\Documents\GitHub\vibrasim
title EQMOD AUTOPILOT
echo EQMOD AUTOPILOT - %date% %time%
echo This window must stay open.
.venv\Scripts\python.exe -u autopilot.py
pause

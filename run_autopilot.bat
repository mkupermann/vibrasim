@echo off
REM EQMOD Autopilot — runs indefinitely, no human input needed
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
set BRIAN2_BACKEND=cython
cd /d C:\Users\nicet\Documents\GitHub\vibrasim
echo Starting EQMOD Autopilot at %date% %time%
echo This will run for 2+ weeks without stopping.
echo Telegram notifications every hour. Git push after every experiment.
echo.
.venv\Scripts\python.exe autopilot.py

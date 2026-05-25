@echo off
REM BET-081 launcher — sets up MSVC environment for Brian2 Cython backend
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
set BRIAN2_BACKEND=cython
cd /d C:\Users\nicet\Documents\GitHub\vibrasim
.venv\Scripts\python.exe -m world.flux.run_bet_081 %*

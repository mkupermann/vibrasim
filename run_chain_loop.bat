@echo off
set PYTHONUNBUFFERED=1
cd /d C:\Users\nicet\Documents\GitHub\vibrasim
echo Chain cascade incremental loop — 10 rounds x 60s
for /L %%i in (1,1,10) do (
    echo.
    echo === Round %%i/10 ===
    .venv\Scripts\python.exe -u tools\run_chain_incremental.py
)
echo.
echo Done. Check .eqmod\bet\BET-085\chain_log.json
pause

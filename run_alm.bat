@echo off
title Ludus Magnus Custom ALM Launcher
echo =======================================================
echo Starting Ludus Magnus Custom ALM local server...
echo =======================================================
start "" /B python "%~dp0alm_orchestrator.py" --serve
timeout /t 2 /nobreak > nul
echo.
echo =======================================================
echo Opening Web Portal in default browser...
echo =======================================================
start http://localhost:8002/
echo.
echo System is fully running in background.
echo Leave this command prompt open to keep the server alive.
echo Press Ctrl+C or close this window to stop the server.
echo =======================================================
pause

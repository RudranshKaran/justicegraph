@echo off
REM JusticeGraph MVP - Windows Batch Launcher
REM Double-click this file to launch the dashboard

echo.
echo ================================================================
echo   JUSTICEGRAPH MVP - QUICK LAUNCHER
echo ================================================================
echo.
echo Starting Streamlit dashboard...
echo.

cd /d "%~dp0"
python run_mvp.py

pause

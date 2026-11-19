@echo off
title Mini Payment - Frontend (React Chaos Dashboard)
echo ====================================================
echo Starting Chaos Dashboard on http://localhost:3000
echo ====================================================
cd /d "%~dp0frontend"
call npm.cmd start
pause

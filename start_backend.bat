@echo off
title Mini Payment - Backend (Spring Boot)
echo ====================================================
echo Starting Mini Payment Backend on http://localhost:8080
echo ====================================================
cd /d "%~dp0backend"
call mvnw.cmd spring-boot:run
pause

@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-nine-grid.ps1"
if errorlevel 1 pause

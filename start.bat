@echo off
cd /d "%~dp0"
rem VS Code sets this and it makes electron run as plain node
set ELECTRON_RUN_AS_NODE=
start "" "node_modules\electron\dist\electron.exe" .

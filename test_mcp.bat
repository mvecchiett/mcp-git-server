@echo off
echo Probando MCP Git Server...
echo.
cd "C:\DesarrolloPython\MCP Git Server"
call venv\Scripts\activate.bat
python git_server.py
pause

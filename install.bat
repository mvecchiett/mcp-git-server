@echo off
chcp 65001 > nul
echo ==========================================
echo   Instalador MCP Git Server para Claude
echo ==========================================
echo.

:: Verificar si Git está instalado
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Git no está instalado o no está en PATH
    echo.
    echo Instala Git desde: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✓ Git detectado
echo.

:: Crear entorno virtual
echo [1/4] Creando entorno virtual...
if exist venv (
    echo   ⚠ Ya existe un entorno virtual, eliminando...
    rmdir /s /q venv
)
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ ERROR al crear entorno virtual
    pause
    exit /b 1
)
echo ✓ Entorno virtual creado
echo.

:: Activar entorno virtual e instalar dependencias
echo [2/4] Instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ ERROR al instalar dependencias
    pause
    exit /b 1
)
echo ✓ Dependencias instaladas
echo.

:: Generar configuración para Claude Desktop
echo [3/4] Generando configuración...
set "CURRENT_DIR=%cd%"
set "PYTHON_PATH=%CURRENT_DIR%\venv\Scripts\python.exe"
set "SERVER_PATH=%CURRENT_DIR%\git_server.py"

(
echo {
echo   "mcpServers": {
echo     "git": {
echo       "command": "%PYTHON_PATH:\=\\%",
echo       "args": [
echo         "%SERVER_PATH:\=\\%"
echo       ],
echo       "env": {
echo         "PYTHONIOENCODING": "utf-8"
echo       }
echo     }
echo   }
echo }
) > claude_desktop_config.json

echo ✓ Configuración generada en: claude_desktop_config.json
echo.

:: Mostrar instrucciones
echo [4/4] Instrucciones finales
echo ==========================================
echo.
echo ✅ INSTALACIÓN COMPLETA
echo.
echo 📝 SIGUIENTE PASO - Agregar a Claude Desktop:
echo.
echo 1. Abre el archivo de configuración de Claude Desktop:
echo    %APPDATA%\Claude\claude_desktop_config.json
echo.
echo 2. Copia el contenido de: %CURRENT_DIR%\claude_desktop_config.json
echo.
echo 3. Si ya tienes otros servidores MCP, agrega "git" al objeto "mcpServers"
echo    Si no tienes ninguno, reemplaza todo el contenido
echo.
echo 4. Guarda y REINICIA Claude Desktop completamente
echo.
echo 5. En el chat con Claude, verás el servidor "git" disponible
echo.
echo ==========================================
echo.
echo 🎯 COMANDOS GIT DISPONIBLES EN CLAUDE:
echo   • git_init       - Inicializar repo
echo   • git_status     - Ver estado
echo   • git_add        - Agregar archivos
echo   • git_commit     - Hacer commits
echo   • git_push/pull  - Sincronizar con remote
echo   • git_branch     - Gestionar ramas
echo   • git_log        - Ver historial
echo   • git_clone      - Clonar repos
echo   • Y más...
echo.
echo ==========================================
pause

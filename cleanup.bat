@echo off
setlocal enabledelayedexpansion

echo =========================================================================
echo LIMPIEZA DE ARCHIVOS DUPLICADOS/OBSOLETOS - MCP Git Server
echo =========================================================================
echo.

:: Obtener timestamp para el backup
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%b-%%a)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set mytime=%%a-%%b)
set timestamp=%mydate%_%mytime%
set backup_name=backup_eliminados_%timestamp%

echo ARCHIVOS QUE SERAN ELIMINADOS:
echo.
echo    Configuraciones obsoletas:
echo       - claude_config_COMPLETO.json
echo       - claude_desktop_config_CON_GIT.json
echo.
echo    Documentacion duplicada:
echo       - CONFIGURACION_ENV.md
echo       - REFACTOR_SUMMARY.md
echo.
echo    Instaladores redundantes:
echo       - install_fix.bat
echo       - install_venv_centralizado.bat
echo.
echo =========================================================================
echo.

set /p confirm=Deseas continuar con la limpieza? (S/N): 
if /i not "%confirm%"=="S" (
    echo.
    echo Operacion cancelada por el usuario
    pause
    exit /b 1
)

echo.
echo =========================================================================
echo PASO 1: Creando backup de archivos a eliminar...
echo =========================================================================
echo.

:: Crear directorio temporal para backup
set temp_backup=%TEMP%\%backup_name%
if not exist "%temp_backup%" mkdir "%temp_backup%"

:: Copiar archivos al backup
echo Copiando archivos al backup temporal...
if exist claude_config_COMPLETO.json copy claude_config_COMPLETO.json "%temp_backup%" >nul 2>&1
if exist claude_desktop_config_CON_GIT.json copy claude_desktop_config_CON_GIT.json "%temp_backup%" >nul 2>&1
if exist CONFIGURACION_ENV.md copy CONFIGURACION_ENV.md "%temp_backup%" >nul 2>&1
if exist REFACTOR_SUMMARY.md copy REFACTOR_SUMMARY.md "%temp_backup%" >nul 2>&1
if exist install_fix.bat copy install_fix.bat "%temp_backup%" >nul 2>&1
if exist install_venv_centralizado.bat copy install_venv_centralizado.bat "%temp_backup%" >nul 2>&1

echo Archivos copiados al backup temporal

:: Crear archivo ZIP del backup usando PowerShell
echo.
echo Comprimiendo backup...
powershell -command "Compress-Archive -Path '%temp_backup%\*' -DestinationPath '%cd%\%backup_name%.zip' -Force"

if %errorlevel% equ 0 (
    echo Backup creado: %backup_name%.zip
) else (
    echo Error al crear el archivo ZIP
    echo Los archivos estan en: %temp_backup%
)

echo.
echo =========================================================================
echo PASO 2: Eliminando archivos...
echo =========================================================================
echo.

set deleted=0

if exist claude_config_COMPLETO.json (
    del /f /q claude_config_COMPLETO.json
    if %errorlevel% equ 0 (
        echo    Eliminado: claude_config_COMPLETO.json
        set /a deleted+=1
    )
)

if exist claude_desktop_config_CON_GIT.json (
    del /f /q claude_desktop_config_CON_GIT.json
    if %errorlevel% equ 0 (
        echo    Eliminado: claude_desktop_config_CON_GIT.json
        set /a deleted+=1
    )
)

if exist CONFIGURACION_ENV.md (
    del /f /q CONFIGURACION_ENV.md
    if %errorlevel% equ 0 (
        echo    Eliminado: CONFIGURACION_ENV.md
        set /a deleted+=1
    )
)

if exist REFACTOR_SUMMARY.md (
    del /f /q REFACTOR_SUMMARY.md
    if %errorlevel% equ 0 (
        echo    Eliminado: REFACTOR_SUMMARY.md
        set /a deleted+=1
    )
)

if exist install_fix.bat (
    del /f /q install_fix.bat
    if %errorlevel% equ 0 (
        echo    Eliminado: install_fix.bat
        set /a deleted+=1
    )
)

if exist install_venv_centralizado.bat (
    del /f /q install_venv_centralizado.bat
    if %errorlevel% equ 0 (
        echo    Eliminado: install_venv_centralizado.bat
        set /a deleted+=1
    )
)

:: Limpiar directorio temporal
rd /s /q "%temp_backup%" >nul 2>&1

echo.
echo =========================================================================
echo RESUMEN
echo =========================================================================
echo.
echo    Archivos eliminados: !deleted!
echo    Backup guardado: %backup_name%.zip
echo.
echo Limpieza completada exitosamente
echo.
echo Estructura final del proyecto:
echo    - git_server.py
echo    - requirements.txt
echo    - README.md
echo    - CHANGELOG.md
echo    - TESTING.md
echo    - RESUMEN_CAMBIOS.md
echo    - claude_desktop_config_example.json
echo    - test_path_validation.py
echo    - test_security.py
echo    - test_server.py
echo    - install.bat
echo.
echo =========================================================================
echo.

pause

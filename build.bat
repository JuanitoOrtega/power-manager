@echo off
REM ===========================================================================
REM  build.bat - Empaqueta PowerManager en un .exe independiente (Windows)
REM
REM  Uso:  doble clic sobre este archivo, o desde la terminal:  build.bat
REM
REM  Pasos que automatiza:
REM    1. Crea el entorno virtual .venv (o reutiliza el existente)
REM    2. Instala/actualiza PyInstaller desde requirements.txt
REM    3. Limpia compilaciones anteriores (build\ y dist\)
REM    4. Genera dist\PowerManager.exe con PyInstaller
REM ===========================================================================

setlocal

REM -- Trabajar siempre desde la carpeta donde vive este script --------------
cd /d "%~dp0"

set "APP_NAME=PowerManager"
set "ENTRY=main.py"
set "ICON=icon.ico"
set "VENV=.venv"

echo.
echo ============================================================
echo   Empaquetando %APP_NAME%
echo ============================================================
echo.

REM -- Verificar que Python este disponible ---------------------------------
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro "python" en el PATH.
    echo         Instala Python 3.x desde https://www.python.org/downloads/
    echo         y marca la opcion "Add Python to PATH" durante la instalacion.
    goto :fail
)

REM -- 1. Crear el entorno virtual si no existe ------------------------------
if not exist "%VENV%\Scripts\python.exe" (
    echo [1/4] Creando entorno virtual en "%VENV%" ...
    python -m venv "%VENV%"
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        goto :fail
    )
) else (
    echo [1/4] Reutilizando entorno virtual existente en "%VENV%".
)

set "PY=%VENV%\Scripts\python.exe"

REM -- 2. Instalar/actualizar dependencias ----------------------------------
echo [2/4] Instalando dependencias (PyInstaller) ...
"%PY%" -m pip install --upgrade pip >nul
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    goto :fail
)

REM -- 3. Limpiar compilaciones anteriores ----------------------------------
echo [3/4] Limpiando compilaciones anteriores ...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "%APP_NAME%.spec" del /q "%APP_NAME%.spec"

REM -- 4. Compilar con PyInstaller ------------------------------------------
echo [4/4] Compilando con PyInstaller ...
if exist "%ICON%" (
    "%PY%" -m PyInstaller --onefile --windowed --name "%APP_NAME%" --icon "%ICON%" "%ENTRY%"
) else (
    echo       ^(No se encontro %ICON%; se compila sin icono personalizado^)
    "%PY%" -m PyInstaller --onefile --windowed --name "%APP_NAME%" "%ENTRY%"
)
if errorlevel 1 (
    echo [ERROR] Fallo la compilacion con PyInstaller.
    goto :fail
)

echo.
echo ============================================================
echo   Listo. Ejecutable generado en:
echo       dist\%APP_NAME%.exe
echo.
echo   Recuerda ejecutarlo como Administrador para que
echo   powercfg y schtasks funcionen correctamente.
echo ============================================================
echo.
pause
endlocal
exit /b 0

:fail
echo.
echo La compilacion se detuvo por un error. Revisa los mensajes de arriba.
echo.
pause
endlocal
exit /b 1

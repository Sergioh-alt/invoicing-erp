@echo off
REM Script de prueba para Facturas GanaTodo v5 con nuevas funcionalidades
echo ========================================
echo Facturas GanaTodo v5.0 - Test Runner
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist ".venv\" (
    echo ERROR: No se encontro el entorno virtual
    echo.
    echo Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)

echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo.
echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no encontrado
    pause
    exit /b 1
)

echo.
echo ========================================
echo Instalando/Actualizando dependencias...
echo ========================================
echo.
echo Esto puede tomar unos momentos...
echo.

pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ADVERTENCIA: Algunas dependencias pueden no haberse instalado
    echo La app podria funcionar con funcionalidad limitada
    echo.
    pause
)

echo.
echo ========================================
echo Dependencias instaladas:
echo ========================================
pip list | findstr /i "PySide6 openpyxl PyMuPDF dateutil"

echo.
echo ========================================
echo Iniciando aplicacion...
echo ========================================
echo.
echo NUEVAS FUNCIONALIDADES:
echo   1. Exportar facturas (CSV/Excel) - Boton "Exportar"
echo   2. Arrastrar PDFs para importar automaticamente
echo.
echo TIP: Presiona Ctrl+Shift+D en dialogo de activacion
echo      para modo desarrollador (bypass)
echo.
pause

python main.py

echo.
echo ========================================
echo Aplicacion cerrada
echo ========================================
pause

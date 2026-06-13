@echo off
REM Script para compilar Facturas Ganatodo a .exe
REM Versión: 4.6.0 con Sistema de Comprobantes

echo.
echo ========================================
echo  Compilando Facturas Ganatodo v4.6.0
echo ========================================
echo.

REM 1. Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo ERROR: No se encuentra main.py
    echo Ejecuta este script desde el directorio raiz del proyecto
    pause
    exit /b 1
)

REM 2. Activar entorno virtual
echo [1/5] Activando entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

REM 3. Instalar PyInstaller si no existe
echo.
echo [2/5] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller no instalado. Instalando...
    pip install pyinstaller
)

REM 4. Limpiar builds anteriores
echo.
echo [3/5] Limpiando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "FacturasGanatodo.spec" del /q FacturasGanatodo.spec

REM 5. Compilar con PyInstaller
echo.
echo [4/5] Compilando aplicacion (esto puede tardar 2-3 minutos)...
pyinstaller --noconsole ^
    --onefile ^
    --name "FacturasGanatodo" ^
    --icon="assets/app.ico" ^
    --add-data "assets;assets" ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtGui" ^
    --hidden-import "PySide6.QtWidgets" ^
    --hidden-import "pygame" ^
    --hidden-import "openpyxl" ^
    --hidden-import "reportlab" ^
    --collect-all "PySide6" ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: La compilacion fallo
    pause
    exit /b 1
)

REM 6. Verificar resultado
echo.
echo [5/5] Verificando resultado...
if exist "dist\FacturasGanatodo.exe" (
    echo.
    echo ========================================
    echo  COMPILACION EXITOSA!
    echo ========================================
    echo.
    echo Ejecutable creado en: dist\FacturasGanatodo.exe
    echo.
    echo IMPORTANTE:
    echo - El .exe es portable (no necesita instalacion)
    echo - Creara carpetas 'data' y 'backups' automaticamente
    echo - Tiene un icono profesional personalizado
    echo.
    echo Para distribuir:
    echo 1. Copia FacturasGanatodo.exe a donde quieras
    echo 2. Opcional: Copia la carpeta 'assets' junto al .exe
    echo 3. Ejecuta el .exe
    echo.
    
    REM Abrir carpeta dist
    explorer dist
) else (
    echo ERROR: No se genero el ejecutable
    pause
    exit /b 1
)

echo.
echo Presiona cualquier tecla para salir...
pause >nul

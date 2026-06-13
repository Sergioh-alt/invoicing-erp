@echo off
echo ================================================
echo Compilación de Facturas GanaTodo
echo ================================================
echo.

REM Activar entorno virtual
call .venv\Scripts\activate.bat

echo [1/5] Limpiando archivos antiguos...
echo.
if exist "dist\FacturasGanatodo.exe" (
    del /Q "dist\FacturasGanatodo.exe"
    echo    - Eliminado dist\FacturasGanatodo.exe
)

REM Limpiar carpetas de build
if exist "build" (
    rmdir /S /Q build
    echo    - Carpeta build eliminada
)

echo.
echo [2/5] Compilando aplicación con PyInstaller...
echo.
pyinstaller --clean FacturasGanatodo.spec

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✗ ERROR: La compilación falló
    exit /b 1
)

echo.
echo [3/5] Verificando archivo ejecutable...
if not exist "dist\FacturasGanatodo.exe" (
    echo ✗ ERROR: No se generó el archivo .exe
    exit /b 1
)

echo    ✓ Ejecutable creado exitosamente

echo.
echo [4/5] Creando directorio de destino en TERA TOSHIBA...
set "DEST_DIR=C:\TERA TOSHIBA\FacturasGanaTodo"
if not exist "%DEST_DIR%" (
    mkdir "%DEST_DIR%"
    echo    ✓ Directorio creado: %DEST_DIR%
) else (
    echo    ✓ Directorio ya existe: %DEST_DIR%
)

echo.
echo [5/5] Copiando ejecutable a TERA TOSHIBA...
copy /Y "dist\FacturasGanatodo.exe" "%DEST_DIR%\FacturasGanatodo.exe"

if %ERRORLEVEL% NEQ 0 (
    echo ✗ ERROR: No se pudo copiar el ejecutable
    exit /b 1
)

echo.
echo ================================================
echo ✓ COMPILACIÓN COMPLETADA EXITOSAMENTE
echo ================================================
echo.
echo Ejecutable ubicado en:
echo %DEST_DIR%\FacturasGanatodo.exe
echo.
echo IMPORTANTE:
echo - Los datos de la aplicación se guardarán en: %DEST_DIR%
echo - Ya no se crearán carpetas en el escritorio
echo - Puedes eliminar las carpetas 'data', 'backups' y 'config' del escritorio
echo.

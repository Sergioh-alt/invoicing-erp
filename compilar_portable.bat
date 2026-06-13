@echo off
set VERSION=5.0.0-PORTABLE
echo ========================================
echo  Compilando VERMILLION PORTABLE v%VERSION%
echo ========================================

call .venv\Scripts\activate.bat

echo [1/2] Limpiando...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo [2/2] Compilando VERMILLION.exe (Portable)...
pyinstaller --noconsole ^
    --onefile ^
    --name "VERMILLION" ^
    --icon="assets/app.ico" ^
    --add-data "assets;assets" ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtGui" ^
    --hidden-import "PySide6.QtWidgets" ^
    --hidden-import "fitz" ^
    --hidden-import "dateutil" ^
    --hidden-import "openpyxl" ^
    --collect-all "PySide6" ^
    main.py

if exist "dist\VERMILLION.exe" (
    echo.
    echo Moviendo VERMILLION.exe (Portable) al escritorio...
    copy /Y "dist\VERMILLION.exe" "C:\Users\Usuario\Desktop\VERMILLION.exe"
    
    echo Actualizando carpeta MAREMOTO...
    robocopy "." "C:\Users\Usuario\Desktop\MAREMOTO" /E /XD .venv build dist .git .pytest_cache __pycache__ /XF *.pyc /R:1 /W:1
    
    echo.
    echo ========================================
    echo  PROCESO COMPLETADO
    echo ========================================
) else (
    echo ERROR: No se pudo crear el ejecutable.
    exit /b 1
)

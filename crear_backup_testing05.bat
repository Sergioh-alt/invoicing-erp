@echo off
echo Creando backup copia_testing05...
robocopy "c:\Users\Usuario\Desktop\Facturas_GanaTodo_v4" "c:\Users\Usuario\Desktop\copia_testing05" /E /XD .venv __pycache__ .pytest_cache htmlcov /XF *.pyc .coverage
echo.
echo Backup completado en: c:\Users\Usuario\Desktop\copia_testing05
pause

@echo off
echo ================================================
echo Limpieza de carpetas del escritorio
echo ================================================
echo.
echo Este script eliminará las carpetas que la aplicación
echo creó anteriormente en el escritorio:
echo   - data
echo   - backups  
echo   - config
echo.
echo IMPORTANTE: Asegúrate de haber ejecutado la aplicación
echo nueva al menos una vez para que tus datos se copien
echo a la nueva ubicación en TERA TOSHIBA.
echo.
pause

set "DESKTOP=%USERPROFILE%\Desktop"

echo.
echo Eliminando carpetas del escritorio...
echo.

if exist "%DESKTOP%\data" (
    rmdir /S /Q "%DESKTOP%\data"
    echo ✓ Eliminada: data
) else (
    echo - No existe: data
)

if exist "%DESKTOP%\backups" (
    rmdir /S /Q "%DESKTOP%\backups"
    echo ✓ Eliminada: backups
) else (
    echo - No existe: backups
)

if exist "%DESKTOP%\config" (
    rmdir /S /Q "%DESKTOP%\config"
    echo ✓ Eliminada: config
) else (
    echo - No existe: config
)

echo.
echo ================================================
echo ✓ Limpieza completada
echo ================================================
echo.
pause

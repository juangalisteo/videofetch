@echo off
setlocal
chcp 65001 >nul
title VideoFetch
where python >nul 2>&1
if errorlevel 1 (
 echo No se encuentra Python. Instala Python y vuelve a abrir este archivo.
 pause
 exit /b 1
)
if not "%~1"=="" goto consola
where pythonw >nul 2>&1
if errorlevel 1 goto ventana
start "" pythonw -s "%~dp0APP\interfaz.py"
exit /b 0
:ventana
python -s "%~dp0APP\interfaz.py"
goto fin
:consola
python -s "%~dp0APP\descargador.py" %*
:fin
echo.
pause

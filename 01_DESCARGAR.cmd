@echo off
setlocal
chcp 65001 >nul
title VideoFetch
where python >nul 2>&1
if errorlevel 1 (
 echo No se encuentra Python. Instala Python y vuelve a abrir este archivo.
 echo Python was not found. Install Python and open this file again.
 pause
 exit /b 1
)
rem Si falta yt-dlp en SISTEMA, avisa y ofrece instalarlo antes de abrir.
rem If yt-dlp is missing from SISTEMA, warn and offer to install it first.
if exist "%~dp0SISTEMA\yt_dlp\" goto listo
echo.
echo  ==================================================================
echo   Falta la herramienta de descarga yt-dlp: es la primera vez.
echo   The yt-dlp download tool is missing: this is the first run.
echo  ==================================================================
echo.
echo   Pulsa una tecla para instalarla ahora. Necesita Internet.
echo   Press any key to install it now. Internet is required.
echo   Para salir, cierra esta ventana. To exit, close this window.
echo.
pause >nul
python -s "%~dp0APP\descargador.py" --update
if exist "%~dp0SISTEMA\yt_dlp\" goto instalado
echo.
echo   No se ha podido instalar. Revisa la conexion y abre 02_ACTUALIZAR.cmd.
echo   It could not be installed. Check the connection and run 02_ACTUALIZAR.cmd.
pause
exit /b 1
:instalado
echo.
echo   Listo. Abriendo VideoFetch... / Done. Opening VideoFetch...
:listo
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

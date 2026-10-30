@echo off
setlocal
chcp 65001 >nul
title VideoFetch - Actualizar
python -s "%~dp0APP\descargador.py" --update
echo.
pause

@echo off
setlocal
chcp 65001 >nul
title VideoFetch - Crear acceso directo
rem Crea accesos directos a VideoFetch (escritorio y menu Inicio) con su icono,
rem tambien en la barra de tareas. Si mueves la carpeta VIDEOFETCH, vuelve a abrir este archivo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0APP\crear_acceso_directo.ps1"
if errorlevel 1 echo   No se pudo crear el acceso directo.
echo.
pause

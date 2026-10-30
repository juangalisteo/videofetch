@echo off
setlocal
chcp 65001 >nul
title VideoFetch - Crear acceso directo
rem Crea en el escritorio un acceso directo a VideoFetch con su icono.
rem Si mueves la carpeta VIDEOFETCH, vuelve a abrir este archivo.
set "VF=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$d=$env:VF.TrimEnd('\'); $q=[char]34; $desk=[Environment]::GetFolderPath('Desktop'); $py=(Get-Command pythonw.exe -ErrorAction SilentlyContinue | Where-Object { $_.Source -notmatch 'WindowsApps' } | Select-Object -First 1).Source; $ws=New-Object -ComObject WScript.Shell; $lnk=$ws.CreateShortcut((Join-Path $desk 'VideoFetch.lnk')); if ($py) { $lnk.TargetPath=$py; $lnk.Arguments='-s '+$q+(Join-Path $d 'APP\interfaz.py')+$q } else { $lnk.TargetPath=(Join-Path $d '01_DESCARGAR.cmd'); $lnk.WindowStyle=7 }; $lnk.WorkingDirectory=$d; $lnk.IconLocation=(Join-Path $d 'APP\videofetch.ico')+',0'; $lnk.Description='VideoFetch - Descargador de videos'; $lnk.Save(); Write-Host ''; Write-Host '  Listo. Ya tienes VideoFetch en el escritorio:'; Write-Host ('  '+(Join-Path $desk 'VideoFetch.lnk'))"
if errorlevel 1 echo   No se pudo crear el acceso directo.
echo.
pause

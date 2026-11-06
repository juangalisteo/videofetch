# Crea los accesos directos de VideoFetch (escritorio y menu Inicio) con su icono.
# Les pone el mismo "AppUserModelID" que usa la ventana (VideoFetch.App), para que
# Windows muestre el icono de VideoFetch en la barra de tareas y no el de Python.
$ErrorActionPreference = 'Stop'
$name = 'VideoFetch'
$appId = 'VideoFetch.App'
$desc = 'VideoFetch - Descargador de videos'
$app = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $app
$q = [char]34

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class AppIdLink {
    [StructLayout(LayoutKind.Sequential, Pack = 4)]
    struct PropertyKey { public Guid fmtid; public uint pid; }
    [StructLayout(LayoutKind.Sequential)]
    struct PropVariant { public ushort vt; public ushort r1, r2, r3; public IntPtr p; public IntPtr p2; }
    [ComImport, Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IPropertyStore {
        void GetCount(out uint count);
        void GetAt(uint index, out PropertyKey key);
        void GetValue(ref PropertyKey key, out PropVariant value);
        void SetValue(ref PropertyKey key, ref PropVariant value);
        void Commit();
    }
    [DllImport("shell32.dll", CharSet = CharSet.Unicode, PreserveSig = false)]
    static extern void SHGetPropertyStoreFromParsingName(string path, IntPtr bindCtx, int flags,
        ref Guid iid, [MarshalAs(UnmanagedType.Interface)] out IPropertyStore store);
    public static void Set(string lnk, string appId) {
        Guid iid = new Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99");
        IPropertyStore store;
        SHGetPropertyStoreFromParsingName(lnk, IntPtr.Zero, 2, ref iid, out store);
        PropertyKey key = new PropertyKey();
        key.fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3");
        key.pid = 5;
        PropVariant value = new PropVariant();
        value.vt = 31;  // texto
        value.p = Marshal.StringToCoTaskMemUni(appId);
        try { store.SetValue(ref key, ref value); store.Commit(); }
        finally { Marshal.FreeCoTaskMem(value.p); Marshal.ReleaseComObject(store); }
    }
}
'@

$py = (Get-Command pythonw.exe -ErrorAction SilentlyContinue |
       Where-Object { $_.Source -notmatch 'WindowsApps' } | Select-Object -First 1).Source
$ico = Join-Path $app ($name.ToLower() + '.ico')
$places = @(
    [Environment]::GetFolderPath('Desktop'),
    (Join-Path ([Environment]::GetFolderPath('ApplicationData')) 'Microsoft\Windows\Start Menu\Programs')
)
$ws = New-Object -ComObject WScript.Shell
Write-Host ''
foreach ($dir in $places) {
    $path = Join-Path $dir ($name + '.lnk')
    if (Test-Path $path) { Remove-Item $path -Force }
    $lnk = $ws.CreateShortcut($path)
    if ($py) {
        $lnk.TargetPath = $py
        $lnk.Arguments = '-s ' + $q + (Join-Path $app 'interfaz.py') + $q
    } else {
        $lnk.TargetPath = Join-Path $root '01_DESCARGAR.cmd'
        $lnk.WindowStyle = 7
    }
    $lnk.WorkingDirectory = $root
    $lnk.IconLocation = $ico + ',0'
    $lnk.Description = $desc
    $lnk.Save()
    try { [AppIdLink]::Set($path, $appId) } catch { Write-Host '  (No se pudo poner el icono de la barra de tareas en este acceso.)' }
    Write-Host ('  Listo: ' + $path)
}
Write-Host ''
Write-Host ('  Ya tienes ' + $name + ' en el escritorio y en el menu Inicio.')
Write-Host '  Si lo tenias anclado a la barra de tareas, desanclalo y vuelve a anclarlo.'

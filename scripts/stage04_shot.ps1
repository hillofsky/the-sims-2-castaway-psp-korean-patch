# Capture the PPSSPP window (by title substring) to a PNG file.
param(
  [string]$Match = "PPSSPP",
  [string]$Out = "logs/stage04/screenshots/shot.png"
)
Add-Type -AssemblyName System.Drawing, System.Windows.Forms
$procs = Get-Process | Where-Object { $_.MainWindowTitle -like "*$Match*" -and $_.MainWindowHandle -ne 0 }
if (-not $procs) {
  Write-Output "NO_WINDOW match=$Match"
  Get-Process PPSSPPWindows64 -ErrorAction SilentlyContinue | Format-Table MainWindowTitle -AutoSize
  exit 1
}
$p = $procs | Select-Object -First 1
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
[Win32]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500
$rc = New-Object Win32+RECT
[Win32]::GetWindowRect($p.MainWindowHandle, [ref]$rc) | Out-Null
$w = $rc.Right - $rc.Left; $h = $rc.Bottom - $rc.Top
if ($w -le 0 -or $h -le 0) { Write-Output "BAD_RECT ${w}x${h}"; exit 1 }
$bmp = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($rc.Left, $rc.Top, 0, 0, $bmp.Size)
$g.Dispose()
$dir = Split-Path $Out -Parent
if ($dir) { New-Item -ItemType Directory -Force $dir | Out-Null }
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output "SAVED $Out ${w}x${h} title=$($p.MainWindowTitle)"

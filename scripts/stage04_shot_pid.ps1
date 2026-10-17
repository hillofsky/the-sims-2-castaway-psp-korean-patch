# Capture the Stage04 PPSSPP window by PID to PNG. Usage: stage04_shot_pid.ps1 -Pid <n> -Out <png>
param([int]$ProcId = 0, [string]$Out = "logs/stage04/screenshots/shot.png")
Add-Type -AssemblyName System.Drawing, System.Windows.Forms
$p = Get-Process -Id $ProcId -ErrorAction SilentlyContinue
if (-not $p -or $p.MainWindowHandle -eq 0) { Write-Output "NO_WINDOW pid=$ProcId"; exit 1 }
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32b {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
# NOTE: no SetForegroundWindow - never steal focus (other tasks use this machine).
Start-Sleep -Milliseconds 200
$rc = New-Object Win32b+RECT
[Win32b]::GetWindowRect($p.MainWindowHandle, [ref]$rc) | Out-Null
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
Write-Output "SAVED $Out ${w}x${h} pid=$ProcId title=$($p.MainWindowTitle)"

# Left-click at screen coords in the Stage04 PPSSPP window via relative fractions.
# Usage: stage04_click_pid.ps1 -ProcId <n> -Fx 0.9 -Fy 0.9
param([int]$ProcId = 0, [double]$Fx = 0.5, [double]$Fy = 0.5)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32c {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(int f, int x, int y, int d, int e);
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$p = Get-Process -Id $ProcId -ErrorAction SilentlyContinue
if (-not $p -or $p.MainWindowHandle -eq 0) { Write-Output "NO_WINDOW pid=$ProcId"; exit 1 }
[Win32c]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 400
$rc = New-Object Win32c+RECT
[Win32c]::GetWindowRect($p.MainWindowHandle, [ref]$rc) | Out-Null
$x = [int]($rc.Left + ($rc.Right - $rc.Left) * $Fx)
$y = [int]($rc.Top + ($rc.Bottom - $rc.Top) * $Fy)
[Win32c]::SetCursorPos($x, $y) | Out-Null
Start-Sleep -Milliseconds 150
[Win32c]::mouse_event(0x0002, 0, 0, 0, 0)
Start-Sleep -Milliseconds 120
[Win32c]::mouse_event(0x0004, 0, 0, 0, 0)
Write-Output "CLICKED ${x},${y} (frac $Fx,$Fy) pid=$ProcId"
Start-Sleep -Milliseconds 800

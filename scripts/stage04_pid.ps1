# Resolve the Stage04 PPSSPP instance PID (dedicated exe path only).
# Never touches other tasks' PPSSPP processes.
$exe = "C:\Users\admin\AppData\Local\Temp\opencode\ppsspp\PPSSPPWindows64.exe"
$p = Get-CimInstance Win32_Process -Filter "Name='PPSSPPWindows64.exe'" |
  Where-Object { $_.ExecutablePath -eq $exe } |
  Select-Object -First 1
if ($p) { Write-Output $p.ProcessId } else { Write-Output "NONE" }

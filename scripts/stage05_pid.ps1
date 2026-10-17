# Resolve the Stage05 PPSSPP instance PID (renamed exe, never touches other tasks).
$p = Get-CimInstance Win32_Process -Filter "Name='STAGE05EMU.exe'" | Select-Object -First 1
if ($p) { Write-Output $p.ProcessId } else { Write-Output "NONE" }

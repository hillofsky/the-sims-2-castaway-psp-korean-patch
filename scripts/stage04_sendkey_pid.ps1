# Send keystrokes to the Stage04 PPSSPP window by PID. Usage: stage04_sendkey_pid.ps1 -Pid <n> -Keys " " -WaitMs 1500
param([int]$ProcId = 0, [string]$Keys = "{DOWN}", [int]$WaitMs = 1500)
Add-Type -AssemblyName System.Windows.Forms
$p = Get-Process -Id $ProcId -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "NO_PROC pid=$ProcId"; exit 1 }
$wshell = New-Object -ComObject WScript.Shell
$ok = $wshell.AppActivate($p.Id)
Write-Output "activate=$ok pid=$ProcId"
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Write-Output "sent=$Keys"
Start-Sleep -Milliseconds $WaitMs

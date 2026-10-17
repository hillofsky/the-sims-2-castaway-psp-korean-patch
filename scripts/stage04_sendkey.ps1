# Focus PPSSPP window and send keystrokes.
param(
  [string]$Match = "ULUS",
  [string]$Keys = "{DOWN}",
  [int]$WaitMs = 1500
)
Add-Type -AssemblyName System.Windows.Forms
$wshell = New-Object -ComObject WScript.Shell
$ok = $wshell.AppActivate($Match)
if (-not $ok) {
  $p = Get-Process | Where-Object { $_.MainWindowTitle -like "*$Match*" } | Select-Object -First 1
  if ($p) { $ok = $wshell.AppActivate($p.Id) }
}
Write-Output "activate=$ok"
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Write-Output "sent=$Keys"
Start-Sleep -Milliseconds $WaitMs

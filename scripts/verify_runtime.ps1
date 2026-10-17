param([string]$Instance)
$ErrorActionPreference='Stop'
$taskInfo=Get-Content -LiteralPath (Join-Path $Instance 'instance.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$taskProc=Get-Process -Id $taskInfo.pid
if($taskProc.Path -ne $taskInfo.executable -or $taskProc.StartTime.Ticks -ne ([datetime]$taskInfo.process_start).Ticks){throw 'Runtime PID/start/executable mismatch'}
$taskSockets=Get-NetTCPConnection -State Listen -LocalPort $taskInfo.port
if(-not($taskSockets | Where-Object OwningProcess -eq $taskInfo.pid)){throw 'Debugger port owner mismatch'}
'VERIFIED'


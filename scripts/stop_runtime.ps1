$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$taskDir=(Get-Content -Encoding utf8 (Join-Path $taskRoot 'logs\STEP_010\latest_instance.txt') -Raw).Trim()
$taskInfo=Get-Content -Encoding utf8 (Join-Path $taskDir 'instance.json') -Raw | ConvertFrom-Json
$taskProc=Get-Process -Id $taskInfo.pid -ErrorAction SilentlyContinue
if($taskProc){
 if($taskProc.Path -ine $taskInfo.executable -or $taskProc.StartTime.Ticks -ne ([datetime]$taskInfo.process_start).Ticks -or -not $taskInfo.started_by_this_script){throw 'Refusing to stop mismatched process'}
 Stop-Process -Id $taskProc.Id
 $taskProc.WaitForExit(5000) | Out-Null
}
$taskInfo.status='FINISHED'
$taskInfo|ConvertTo-Json|Set-Content -Encoding utf8 (Join-Path $taskDir 'instance.json')

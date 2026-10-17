param(
 [ValidateSet('Build','Analyze','Package')][string]$Mode = 'Package',
 [ValidatePattern('^[A-Za-z0-9_]*$')][string]$BuildId = '',
 [string]$Python = 'python',
 [switch]$VerifyPatch
)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$taskRoot = $PSScriptRoot
if (-not $BuildId) { $BuildId = (Get-Content -LiteralPath (Join-Path $taskRoot 'config/project.json') -Raw -Encoding utf8 | ConvertFrom-Json).latest_build_id }
$taskStamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$taskLogs = Join-Path $taskRoot "logs/runs/$BuildId`_$taskStamp"
New-Item -ItemType Directory -Force -Path $taskLogs | Out-Null
$taskFailed = $false
try {
 if ($Mode -eq 'Build') {
  $taskArgs = @((Join-Path $taskRoot 'scripts/build_pipeline.py'),'--build-id',$BuildId)
  if ($VerifyPatch) {$taskArgs += '--verify-patch'}
  & $Python @taskArgs *> (Join-Path $taskLogs 'build.log')
  if ($LASTEXITCODE -ne 0) {throw 'Build failed; inspect pipeline logs'}
 } elseif ($Mode -eq 'Analyze') {
  foreach ($taskScript in @('compare_inputs.py','inspect_arc.py','extract_text.py','enrich_context.py','validate_translation.py')) {
   & $Python (Join-Path $taskRoot "scripts/$taskScript") *> (Join-Path $taskLogs "$taskScript.log")
   if ($LASTEXITCODE -ne 0) {throw "$taskScript failed"}
  }
 }
} catch {
 $taskFailed = $true
 ($_ | Out-String) | Set-Content -Encoding utf8 (Join-Path $taskLogs 'FAILURE.txt')
} finally {
 $taskPrefix = if ($taskFailed) {'fall_'} else {''}
 $taskZip = Join-Path $taskRoot "logs/${taskPrefix}CASTAWAY_${BuildId}_${taskStamp}_RESULT.zip"
 & $Python (Join-Path $taskRoot 'scripts/package_handoff.py') --build-id $BuildId --output $taskZip
 if ($LASTEXITCODE -ne 0) {$taskFailed = $true}
}
if ($taskFailed) {exit 1}

param([string]$Iso)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if(-not $Iso){$taskLatest=(Get-Content -LiteralPath (Join-Path $taskRoot 'config/project.json') -Raw -Encoding utf8 | ConvertFrom-Json).latest_build_id;$Iso=Join-Path $taskRoot ('build/CASTAWAY_'+$taskLatest+'_KO_EXPERIMENTAL.iso')}
$taskRun='castaway_STEP010_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff')
$taskDir=Join-Path $taskRoot "runtime\instances\$taskRun"
New-Item -ItemType Directory -Force $taskDir | Out-Null
$taskPort=$null
foreach($taskCandidate in 26480..26519){
 $taskListener=New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback,$taskCandidate)
 try{$taskListener.Start();$taskPort=$taskCandidate;break}catch{}finally{$taskListener.Stop()}
}
if(-not $taskPort){throw 'No free runtime port'}
$taskExe=Join-Path $taskRoot 'work\ppsspp_1.19.3\CASTAWAYEMU.exe'
if(-not(Test-Path $taskExe)){Copy-Item -LiteralPath (Join-Path $taskRoot 'work\ppsspp_1.19.3\PPSSPPWindows64.exe') -Destination $taskExe}
$taskConfig=Join-Path $taskDir 'ppsspp.ini'
@"
[General]
FirstRun = False
FileLogging = True
AutoRun = True
WindowX = 100
WindowY = 100
WindowWidth = 960
WindowHeight = 600
RemoteDebuggerOnStartup = True
RemoteDebuggerLocal = True
RemoteISOPort = $taskPort
[Sound]
Enable = True
GlobalVolume = 0
GameVolume = 0
[Graphics]
RenderingMode = 1
InternalResolution = 1
[SystemParam]
Language = 1
"@ | Set-Content -Encoding utf8 $taskConfig
$taskArguments=@('--windowed',"--config=`"$taskConfig`"",'--graphics=software',('--log='+ (Join-Path $taskDir 'ppsspp.log')),"`"$Iso`"")
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArguments -WorkingDirectory (Split-Path $taskExe) -WindowStyle Normal -PassThru
$taskInfo=@{run_id=$taskRun;pid=$taskProcess.Id;process_start=$taskProcess.StartTime.ToString('o');executable=$taskExe;port=$taskPort;iso=$Iso;expected_game_id='ULUS10296';config=$taskConfig;started_by_this_script=$true;status='STARTING'}
$taskInfo | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $taskDir 'instance.json')
$taskDir | Set-Content -Encoding utf8 (Join-Path $taskRoot 'logs\STEP_010\latest_instance.txt')
$taskInfo | ConvertTo-Json

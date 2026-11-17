# Windows 설치: venv → 의존성 → 로그온 시 자동 실행(작업 스케줄러, 관리자 권한 불필요)
$ErrorActionPreference = "Stop"
$Dir = Split-Path -Parent $PSScriptRoot
py -3 -m venv "$Dir\.venv"
& "$Dir\.venv\Scripts\pip.exe" install -q -r "$Dir\requirements.txt"
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  Write-Warning "Claude Code CLI 설치 후 'claude' 실행 → Max 계정으로 /login 하세요."
}
if (-not (Test-Path "$Dir\.git")) { Push-Location $Dir; git init -q; git add -A; git commit -qm "initial"; Pop-Location }

$action  = New-ScheduledTaskAction -Execute "$Dir\.venv\Scripts\pythonw.exe" -Argument "`"$Dir\supervisor.py`"" -WorkingDirectory $Dir
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$set     = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
             -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "AI Manager" -Action $action -Trigger $trigger -Settings $set -Force | Out-Null
Start-ScheduledTask -TaskName "AI Manager"
Write-Host "✅ 설치 완료. 긴급 정지: New-Item $HOME\AI_Inbox\STOP   일시정지: New-Item $HOME\AI_Inbox\PAUSE"

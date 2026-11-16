param([string]$ReportPath = (Join-Path (Split-Path $PSScriptRoot -Parent) 'workstation-health.json'))
$ErrorActionPreference = 'Stop'
$uninstallKeys = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
)
$installed = @(foreach ($key in $uninstallKeys) {
    Get-ItemProperty -Path $key -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -match 'Adobe.*(InDesign|Illustrator|Photoshop)' } |
        Select-Object DisplayName, DisplayVersion, InstallLocation
})
$tools = [ordered]@{}
foreach ($name in @('git', 'claude', 'codex')) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    $tools[$name] = if ($command) { $command.Source } else { $null }
}
$fontFolder = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
$fontFiles = @(Get-ChildItem -Path "$env:WINDIR\Fonts\*Pretendard*", "$fontFolder\*Pretendard*" -ErrorAction SilentlyContinue)
$report = [ordered]@{
    checked_at = [DateTimeOffset]::Now.ToString('o')
    apps_detected_in_registry = $installed
    command_paths = $tools
    pretendard_font_files_detected = $fontFiles.Count
    adobe_login = '사용자 확인 완료. 스크립트는 계정·라이선스 정보를 읽지 않습니다.'
    adobe_script_execution = '미검증: 각 앱에서 probe.jsx를 실행해야 합니다.'
    claude_mobile_github = '미검증: Claude 앱에서 별도 연결 및 저장소 선택 필요.'
}
$report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
$installed | Format-Table -AutoSize | Out-Host
Write-Host "환경 진단 저장: $ReportPath"
foreach ($appName in @('InDesign', 'Illustrator', 'Photoshop')) {
    if (-not ($installed | Where-Object { $_.DisplayName -like "*$appName*" })) {
        Write-Warning "$appName 레지스트리 항목을 찾지 못했습니다. 미설치 확정이 아니므로 앱을 직접 확인해 주세요."
    }
}
if (-not $fontFiles.Count) { Write-Warning 'Pretendard 글꼴 파일을 감지하지 못했습니다. assets/fonts/Pretendard 설치 여부를 앱에서 확인해 주세요.' }

param(
    [string]$Destination = 'C:\Users\admin\Projects\freelance-design'
)
$ErrorActionPreference = 'Stop'
$repoUrl = 'https://github.com/pck9880-sys/claude-design.git'
$branch = 'codex/project-moment-ir'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git for Windows가 필요합니다: https://git-scm.com/downloads/win'
}
$Destination = [IO.Path]::GetFullPath($Destination)
if (Test-Path -LiteralPath $Destination) {
    if (-not (Test-Path -LiteralPath (Join-Path $Destination '.git'))) {
        throw "기존 폴더는 덮어쓰지 않습니다: $Destination"
    }
    $remote = git -C $Destination remote get-url origin
    if ($LASTEXITCODE -ne 0 -or $remote -notin @($repoUrl, 'git@github.com:pck9880-sys/claude-design.git')) {
        throw '지정 경로가 예상한 저장소와 다릅니다. 기존 파일은 변경하지 않았습니다.'
    }
    $dirty = git -C $Destination status --porcelain
    if ($LASTEXITCODE -ne 0 -or $dirty) { throw '미커밋 변경이 있어 중단합니다. 기존 작업을 먼저 보존해 주세요.' }
    $current = git -C $Destination branch --show-current
    if ($current -ne $branch) { throw "현재 브랜치는 $current 입니다. 자동 전환하지 않습니다. 필요한 브랜치: $branch" }
    git -C $Destination pull --ff-only origin $branch
    if ($LASTEXITCODE -ne 0) { throw '업데이트 실패. 기존 작업은 강제로 덮어쓰지 않았습니다.' }
} else {
    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    git clone --single-branch --branch $branch $repoUrl $Destination
    if ($LASTEXITCODE -ne 0) { throw 'GitHub 다운로드 실패. 저장소 접근 권한 및 로그인을 확인해 주세요.' }
}
git lfs version 1>$null 2>$null
if ($LASTEXITCODE -eq 0) {
    git -C $Destination lfs install --local
    if ($LASTEXITCODE -ne 0) { throw '저장소별 Git LFS 설정에 실패했습니다.' }
    git -C $Destination lfs pull
    if ($LASTEXITCODE -ne 0) { throw 'LFS 원본 다운로드 실패. 포인터만 받은 파일을 Adobe에서 열지 마세요.' }
} else {
    Write-Warning 'Git LFS가 없습니다. Adobe 원본을 올리거나 받기 전에 설치가 필요합니다: https://git-lfs.com'
}
$workspace = Join-Path $Destination 'freelance'
& (Join-Path $workspace 'scripts\check-adobe.ps1') -ReportPath (Join-Path $workspace 'workstation-health.json')
Write-Host "작업 폴더: $workspace"
Write-Host '이 폴더에서 claude 또는 codex 실행. 휴대폰에서는 같은 GitHub 저장소와 브랜치를 선택하세요.'
Write-Host '이 스크립트는 Adobe 앱·Claude 연결·원격 자동 실행을 설치하지 않습니다.'

$ErrorActionPreference = 'Stop'
$target = 'C:\Users\admin\Desktop\프로젝트 모먼트\IR-개발'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git for Windows를 먼저 설치해 주세요: https://git-scm.com/downloads/win'
}
if (Test-Path -LiteralPath $target) {
    throw "기존 폴더를 보존하기 위해 중단합니다: $target"
}
git clone --single-branch --branch codex/project-moment-ir https://github.com/pck9880-sys/claude-design.git $target
if ($LASTEXITCODE -ne 0) { throw '저장소 다운로드 실패. GitHub 접근 권한과 로그인 상태를 확인해 주세요.' }
Write-Host "설치 완료: $target"
Write-Host (Join-Path $target 'output\ir-project-moment\v4\deck_v8.pptx')

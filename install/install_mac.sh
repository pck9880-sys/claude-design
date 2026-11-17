#!/bin/bash
# iMac 설치: venv 생성 → 의존성 → 로그인 시 자동 실행(LaunchAgent)
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-/opt/homebrew/bin/python3}"; [ -x "$PY" ] || PY="$(command -v python3)"
"$PY" -m venv "$DIR/.venv"
"$DIR/.venv/bin/pip" install -q -r "$DIR/requirements.txt"
command -v claude >/dev/null || echo "⚠️  Claude Code CLI 설치 후 'claude' 실행 → Max 계정으로 /login 하세요."
[ -d "$DIR/.git" ] || (cd "$DIR" && git init -q && git add -A && git commit -qm "initial")

PLIST="$HOME/Library/LaunchAgents/com.local.ai-manager.plist"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.local.ai-manager</string>
  <key>ProgramArguments</key><array>
    <string>$DIR/.venv/bin/python</string><string>$DIR/supervisor.py</string></array>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>EnvironmentVariables</key><dict><key>PATH</key>
    <string>$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
  <key>StandardOutPath</key><string>/tmp/ai-manager.out</string>
  <key>StandardErrorPath</key><string>/tmp/ai-manager.err</string>
</dict></plist>
PL
launchctl bootout "gui/$(id -u)/com.local.ai-manager" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
REAL_PY="$("$DIR/.venv/bin/python" -c 'import os,sys;print(os.path.realpath(sys.executable))')"
cat <<MSG

✅ 설치 완료. 이제 시스템 설정 → 개인정보 보호 및 보안 에서 아래 실행 파일에 권한을 주세요:
   $REAL_PY
   - 화면 및 시스템 오디오 녹음(화면 기록)
   - 손쉬운 사용
   - 자동화 → Adobe Illustrator / Adobe InDesign / System Events (첫 실행 때 팝업으로 뜸)
권한을 준 뒤:  launchctl kickstart -k gui/$(id -u)/com.local.ai-manager
긴급 정지: touch ~/AI_Inbox/STOP     일시정지: touch ~/AI_Inbox/PAUSE
MSG

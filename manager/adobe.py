"""Illustrator / InDesign 열린 문서 정보 읽기 (읽기 전용 스크립트만 실행).

앱이 이미 맨 앞에 있을 때만 호출 — 꺼진 앱을 띄우지 않기 위해.
macOS: '자동화' 권한(매니저 → Illustrator/InDesign) 필요.
Windows: pywin32 필요 (COM).
"""
from __future__ import annotations

import json
import subprocess

from .config import ROOT
from .platform_utils import IS_MAC, IS_WIN

SCRIPTS = ROOT / "scripts" / "adobe"


def which_app(app_name: str) -> str | None:
    a = app_name.lower()
    if "indesign" in a:
        return "indesign"
    if "illustrator" in a:
        return "illustrator"
    return None


def document_info(app_name: str) -> dict | None:
    kind = which_app(app_name)
    if not kind:
        return None
    jsx = SCRIPTS / f"{kind}_info.jsx"
    try:
        raw = _run_mac(kind, jsx) if IS_MAC else _run_win(kind, jsx) if IS_WIN else None
        return json.loads(raw) if raw else None
    except Exception as e:  # 권한 미허용, 앱 버전 차이 등
        return {"error": f"{type(e).__name__}: {e}"}


def _run_mac(kind: str, jsx) -> str:
    if kind == "indesign":
        script = (f'tell application id "com.adobe.InDesign" to '
                  f'do script (POSIX file "{jsx}") language javascript')
    else:
        script = (f'set f to POSIX file "{jsx}"\n'
                  f'tell application id "com.adobe.illustrator" to do javascript f')
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True,
                          timeout=30).stdout.strip()


def _run_win(kind: str, jsx) -> str:
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    try:
        if kind == "indesign":
            app = win32com.client.GetActiveObject("InDesign.Application")
            return str(app.DoScript(str(jsx), 1246973031))  # idJavascript
        app = win32com.client.GetActiveObject("Illustrator.Application")
        return str(app.DoJavaScriptFile(str(jsx)))
    finally:
        pythoncom.CoUninitialize()

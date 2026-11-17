"""macOS / Windows 차이를 감추는 계층: 맨 앞 앱·창 제목, 유휴 시간, 알림."""
from __future__ import annotations

import subprocess
import sys

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform.startswith("win")

_MAC_FRONT = r'''
tell application "System Events"
  set p to first application process whose frontmost is true
  set appName to name of p
  set winTitle to ""
  try
    set winTitle to name of front window of p
  end try
end tell
return appName & linefeed & winTitle
'''


def active_window() -> tuple[str, str]:
    """(앱 이름, 창 제목). 실패하면 ("", "")."""
    try:
        if IS_MAC:  # 손쉬운 사용 권한 필요
            out = subprocess.run(["osascript", "-e", _MAC_FRONT], capture_output=True,
                                 text=True, timeout=5).stdout
            app, _, title = out.rstrip("\n").partition("\n")
            return app, title
        if IS_WIN:
            return _win_active_window()
    except Exception:
        pass
    return "", ""


def _win_active_window() -> tuple[str, str]:
    import ctypes
    from ctypes import wintypes

    user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
    hwnd = user32.GetForegroundWindow()
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    app = ""
    h = kernel32.OpenProcess(0x1000, False, pid.value)  # PROCESS_QUERY_LIMITED_INFORMATION
    if h:
        size = wintypes.DWORD(1024)
        pbuf = ctypes.create_unicode_buffer(1024)
        if kernel32.QueryFullProcessImageNameW(h, 0, pbuf, ctypes.byref(size)):
            app = pbuf.value.split("\\")[-1].removesuffix(".exe")
        kernel32.CloseHandle(h)
    return app, buf.value


def idle_seconds() -> float:
    """마지막 키보드/마우스 입력 후 경과 초. (키 입력 내용은 읽지 않음)"""
    try:
        if IS_MAC:
            out = subprocess.run(["ioreg", "-c", "IOHIDSystem"], capture_output=True,
                                 text=True, timeout=5).stdout
            for line in out.splitlines():
                if "HIDIdleTime" in line:
                    return int(line.split("=")[-1].strip()) / 1e9
        if IS_WIN:
            import ctypes

            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(lii)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
            return (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000.0
    except Exception:
        pass
    return 0.0


def notify(title: str, message: str) -> None:
    try:
        if IS_MAC:
            esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')
            subprocess.run(["osascript", "-e",
                            f'display notification "{esc(message)}" with title "{esc(title)}"'],
                           timeout=5)
        elif IS_WIN:
            ps = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "$n=New-Object System.Windows.Forms.NotifyIcon;"
                "$n.Icon=[System.Drawing.SystemIcons]::Information;$n.Visible=$true;"
                f"$n.ShowBalloonTip(5000,'{title.replace(chr(39), '')}','{message.replace(chr(39), '')}',"
                "[System.Windows.Forms.ToolTipIcon]::Info);Start-Sleep 6;$n.Dispose()"
            )
            subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps])
    except Exception:
        pass

"""Claude가 GPT(Codex)에 일을 맡기는 도구.

PC에서는 Codex CLI(ChatGPT 로그인)를 쓰고, 없으면 OPENAI_API_KEY로 API를 쓴다.

사용:
  python tools/gpt.py image "장면 설명" --keywords 키워드1 키워드2 --out assets/generated/hero.png
        [--size 1536x1024] [--ref 참고.png] [--attempt 2 --fix "검수에서 발견한 문제"]
        (클립아트 스타일·얼굴 금지·키워드 외 요소 금지 규칙이 항상 붙는다)
  python tools/gpt.py research "질문" --out refs/ir/조사.md
  python tools/gpt.py research --batch 질문목록.txt --out-dir refs/ir/조사 [--workers 3]
  python tools/gpt.py organize --task "할 일" --in 파일1 파일2 ... --out 결과.md

모든 호출은 tools/gpt-log.jsonl 에 기록된다 (프롬프트, 결과 경로, 소요 시간).
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "tools" / "gpt-log.jsonl"
CODEX = shutil.which("codex")
TIMEOUT = int(os.environ.get("GPT_TIMEOUT", "900"))

RULES = (
    "규칙: 답은 한국어. 확인하지 못한 사실·링크·숫자는 쓰지 않는다. "
    "출처가 있는 정보는 링크를 붙인다. 남의 저작물을 길게 인용하지 않는다."
)


def log(kind, prompt, out, ok, secs, backend):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"t": time.strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, "backend": backend,
                            "ok": ok, "secs": round(secs, 1), "out": str(out), "prompt": prompt[:500]},
                           ensure_ascii=False) + "\n")


def codex(prompt, out_file, sandbox="read-only", extra=None, images=None):
    """codex exec 를 실행하고 마지막 답을 out_file 에 저장."""
    cmd = [CODEX, "exec", "--ephemeral", "--skip-git-repo-check", "-s", sandbox, "-C", str(ROOT),
           "-o", str(out_file)] + (extra or [])
    for img in images or []:
        cmd += ["-i", str(img)]
    cmd.append("-")
    r = subprocess.run(cmd, input=prompt.encode("utf-8"), capture_output=True, timeout=TIMEOUT)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace")[-800:])
    return Path(out_file).read_text(encoding="utf-8") if Path(out_file).exists() else ""


def backend():
    if CODEX:
        return "codex"
    if os.environ.get("OPENAI_API_KEY"):
        return "api"
    sys.exit("GPT 사용 불가: Codex CLI(로그인)도 OPENAI_API_KEY도 없음. "
             "PC에서 실행하거나 클라우드 환경 변수에 OPENAI_API_KEY를 설정할 것.")


# ---------------- 이미지 ----------------
def palette():
    try:
        c = json.loads((ROOT / "tokens.json").read_text(encoding="utf-8"))["color"]
        return ", ".join([c["brand"]["primary"], c["brand"].get("secondary", ""), c["neutral"]["50"], c["neutral"]["700"]])
    except Exception:  # noqa: BLE001
        return "브랜드 색 2–3개 + 중립색"


# 모든 이미지에 고정으로 붙는 스타일 규칙 (사용자 지정, 2026-11-16)
STYLE = (
    "스타일 규칙 (반드시 지킬 것):\n"
    "1. 클립아트 느낌의 플랫 일러스트: 단순한 도형, 깔끔한 윤곽, 면 위주 채색, 그림자는 없거나 아주 약하게.\n"
    "2. 사실적·사진 같은 표현 금지 (포토리얼, 3D 렌더, 사실적 질감, 피사계 심도 금지).\n"
    "3. 사람 얼굴이 보이면 안 됨. 사람이 필요하면 손·뒷모습·실루엣·얼굴이 프레임 밖인 구도로만.\n"
    "4. 키워드에 있는 요소만 그린다. 키워드와 무관한 사물·배경·장식을 추가하지 않는다.\n"
    "5. 과하지 않게: 주요 요소 1–3개, 색 3–4개 이내, 배경은 단색 또는 아주 단순하게, 여백 충분히.\n"
    "6. 글자·숫자·로고·워터마크 금지.\n"
    f"7. 색은 이 팔레트 안에서: {palette()}\n"
)


def build_image_prompt(a):
    kw = ", ".join(a.keywords)
    p = (f"{STYLE}\n키워드(이것만 표현): {kw}\n장면 설명: {a.prompt}\n크기/비율: {a.size}\n")
    if a.fix:
        p += f"\n이전 시안의 문제점 (반드시 고칠 것): {a.fix}\n"
    return p


def versioned(out, attempt):
    return out if attempt <= 1 else out.with_name(f"{out.stem}-v{attempt}{out.suffix}")


def cmd_image(a):
    out = versioned((ROOT / a.out).resolve(), a.attempt)
    out.parent.mkdir(parents=True, exist_ok=True)
    t0, be = time.time(), backend()
    prompt = build_image_prompt(a)
    if be == "codex":
        rel = out.relative_to(ROOT).as_posix()
        p = (f"이미지 생성 도구로 아래 조건의 이미지를 {a.n}장 만들어 저장해.\n\n{prompt}\n"
             f"저장 경로: {rel}" + (" (여러 장이면 파일명 뒤에 -1, -2 …)" if a.n > 1 else "") + "\n"
             "참고 이미지가 첨부되면 구도·색감만 참고하고 그대로 베끼지 말 것.\n"
             "저장한 파일 경로만 줄마다 하나씩 답해.")
        tmp = out.with_suffix(".codex.txt")
        try:
            res = codex(p, tmp, sandbox="workspace-write", images=a.ref)
        finally:
            tmp.unlink(missing_ok=True)
    else:
        import base64
        from openai import OpenAI
        client = OpenAI()
        model = os.environ.get("GPT_IMAGE_MODEL", "gpt-image-1")
        r = client.images.generate(model=model, prompt=prompt, size=a.size, n=a.n)
        paths = []
        for i, d in enumerate(r.data, 1):
            p = out if a.n == 1 else out.with_name(f"{out.stem}-{i}{out.suffix}")
            p.write_bytes(base64.b64decode(d.b64_json))
            paths.append(str(p.relative_to(ROOT)))
        res = "\n".join(paths)
    ok = out.exists() or any(out.parent.glob(out.stem + "-*" + out.suffix))
    if ok:   # 검수·재생성 때 쓰도록 조건을 옆에 기록
        out.with_suffix(".json").write_text(json.dumps(
            {"keywords": a.keywords, "prompt": a.prompt, "size": a.size, "attempt": a.attempt, "fix": a.fix},
            ensure_ascii=False, indent=1), encoding="utf-8")
    log("image", f"[{', '.join(a.keywords)}] {a.prompt}", out.relative_to(ROOT), ok, time.time() - t0, be)
    print(res.strip() if ok else f"실패: 이미지가 저장되지 않음\n{res}")
    sys.exit(0 if ok else 1)


# ---------------- 서칭 ----------------
def research_one(q, out, be):
    out = (ROOT / out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    p = (f"웹 검색으로 조사해서 마크다운 보고서로 답해.\n질문: {q}\n{RULES}\n"
         "형식: ## 요약(3줄) / ## 찾은 자료(표: 이름, 링크, 핵심 내용, 날짜) / ## 확인 못 한 것")
    if be == "codex":
        text = codex(p, out, extra=["-c", "web_search=live"])
    else:
        from openai import OpenAI
        client = OpenAI()
        r = client.responses.create(model=os.environ.get("GPT_MODEL", "gpt-5"), input=p,
                                    tools=[{"type": "web_search"}])
        text = r.output_text
        out.write_text(text, encoding="utf-8")
    out.write_text(f"# 조사: {q}\n\n> GPT({be}) 조사 결과. Claude가 검토 전 초안.\n\n{text}\n", encoding="utf-8")
    log("research", q, out.relative_to(ROOT), True, time.time() - t0, be)
    return out.relative_to(ROOT)


def cmd_research(a):
    be = backend()
    if a.batch:
        qs = [l.strip() for l in Path(a.batch).read_text(encoding="utf-8").splitlines() if l.strip()]
        outdir = Path(a.out_dir or "refs/research")
        jobs = [(q, outdir / f"{i:02d}.md") for i, q in enumerate(qs, 1)]
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            for path in ex.map(lambda j: research_one(j[0], j[1], be), jobs):
                print(f"저장: {path}")
    else:
        print(f"저장: {research_one(a.question, a.out, be)}")


# ---------------- 자료 정리 ----------------
def cmd_organize(a):
    be = backend()
    out = (ROOT / a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    files = "\n".join(f"- {Path(f).as_posix()}" for f in a.inputs)
    p = (f"다음 파일들을 직접 읽고 작업해.\n{files}\n\n할 일: {a.task}\n{RULES}\n"
         "원문에 없는 내용은 '<미확인>'으로 표시. 결과는 마크다운으로만 답해.")
    t0 = time.time()
    if be == "codex":
        extra = []
        for f in a.inputs:
            d = Path(f).resolve().parent
            if not d.is_relative_to(ROOT):
                extra += ["--add-dir", str(d)]
        codex(p, out, extra=extra)
    else:
        from openai import OpenAI
        client = OpenAI()
        body = "\n\n".join(f"### {f}\n{Path(f).read_text(encoding='utf-8', errors='replace')[:60000]}" for f in a.inputs)
        r = client.responses.create(model=os.environ.get("GPT_MODEL", "gpt-5"), input=p + "\n\n" + body)
        out.write_text(r.output_text, encoding="utf-8")
    log("organize", a.task, out.relative_to(ROOT), out.exists(), time.time() - t0, be)
    print(f"저장: {out.relative_to(ROOT)}")


# ---------------- 라인 아이콘 (SVG 코드로 생성) ----------------
ICON_RULES = (
    "라인 아이콘 규칙 (반드시):\n"
    "- SVG 코드로 직접 작성. <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" "
    "fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.75\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n"
    "- 선만 사용: 면 채움·그라데이션·그림자·글자·이미지 금지\n"
    "- 간단하고 명료하게: 도형 요소 2–6개, 한 아이콘에 한 가지 뜻만, 작은 크기(24px)에서도 알아볼 것\n"
    "- 사방 2px 여백을 두고 가운데 정렬, 좌표는 0.5 단위 정수 위주\n"
    "- 스타일 기준: assets/icons/lucide/ 의 아이콘 2–3개를 열어 보고 같은 선 굵기·곡률·밀도로 맞출 것\n"
)


def cmd_icon(a):
    be = backend()
    if be != "codex":
        _sys.exit("아이콘 생성은 Codex(PC)에서만 가능. 클라우드에서는 Lucide 세트에서 고를 것: python tools/icon.py find ...")
    out = (ROOT / "assets/icons/custom" / f"{a.name}.svg").resolve()
    if a.attempt > 1:
        out = out.with_name(f"{a.name}-v{a.attempt}.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    rel = out.relative_to(ROOT).as_posix()
    p = (f"다음 뜻의 라인 아이콘을 SVG 파일로 만들어 {rel} 에 저장해.\n뜻: {a.meaning}\n"
         f"표현할 요소(이것만): {', '.join(a.keywords)}\n\n{ICON_RULES}"
         + (f"\n이전 시안의 문제점 (반드시 고칠 것): {a.fix}\n" if a.fix else "")
         + "다른 파일은 수정하지 말고, 저장한 경로만 한 줄로 답해.")
    t0 = time.time()
    tmp = out.with_suffix(".codex.txt")
    try:
        codex(p, tmp, sandbox="workspace-write")
    finally:
        tmp.unlink(missing_ok=True)
    ok = out.exists()
    log("icon", f"[{a.name}] {a.meaning}", rel, ok, time.time() - t0, be)
    if not ok:
        _sys.exit("실패: SVG가 저장되지 않음")
    r = subprocess.run([_sys.executable, str(ROOT / "tools/icon.py"), "check", str(out)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    print(f"저장: {rel}\n{r.stdout.strip()}")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    ic = sp.add_parser("icon")
    ic.add_argument("meaning", help="아이콘이 뜻하는 것 (예: 공방 클래스 실시간 예약)")
    ic.add_argument("--name", required=True, help="파일 이름 (영문 소문자-하이픈)")
    ic.add_argument("--keywords", nargs="+", required=True, help="그릴 요소 1–3개")
    ic.add_argument("--attempt", type=int, default=1)
    ic.add_argument("--fix", default="")
    ic.set_defaults(fn=cmd_icon)
    i = sp.add_parser("image")
    i.add_argument("prompt")
    i.add_argument("--out", required=True)
    i.add_argument("--size", default="1536x1024")
    i.add_argument("--n", type=int, default=1)
    i.add_argument("--ref", nargs="*", default=[])
    i.add_argument("--keywords", nargs="+", required=True, help="이미지에 들어갈 요소만 (3–6개)")
    i.add_argument("--attempt", type=int, default=1, help="재생성 회차. 2부터 파일명에 -v2 …")
    i.add_argument("--fix", default="", help="검수에서 발견한 문제점 (재생성 때)")
    i.set_defaults(fn=cmd_image)
    r = sp.add_parser("research")
    r.add_argument("question", nargs="?")
    r.add_argument("--out", default="refs/research/result.md")
    r.add_argument("--batch")
    r.add_argument("--out-dir")
    r.add_argument("--workers", type=int, default=3)
    r.set_defaults(fn=cmd_research)
    o = sp.add_parser("organize")
    o.add_argument("--task", required=True)
    o.add_argument("--in", dest="inputs", nargs="+", required=True)
    o.add_argument("--out", required=True)
    o.set_defaults(fn=cmd_organize)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

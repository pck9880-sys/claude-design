"""Claude가 GPT(Codex)에 일을 맡기는 도구.

PC에서는 Codex CLI(ChatGPT 로그인)를 쓰고, 없으면 OPENAI_API_KEY로 API를 쓴다.

사용:
  python tools/gpt.py image "프롬프트" --out assets/generated/hero.png [--ref 참고이미지.png] [--size 1536x1024]
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
def cmd_image(a):
    out = (ROOT / a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    t0, be = time.time(), backend()
    if be == "codex":
        rel = out.relative_to(ROOT).as_posix()
        p = (f"이미지 생성 도구로 다음 이미지를 {a.n}장 만들어 저장해.\n"
             f"- 내용: {a.prompt}\n- 크기/비율: {a.size}\n"
             f"- 저장 경로: {rel}" + (" (여러 장이면 파일명 뒤에 -1, -2 …)" if a.n > 1 else "") + "\n"
             "- 이미지 안에 글자·로고·워터마크를 넣지 말 것 (요청에 있으면 예외)\n"
             "- 참고 이미지가 첨부되면 구도·색감만 참고하고 그대로 베끼지 말 것\n"
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
        r = client.images.generate(model=model, prompt=a.prompt, size=a.size, n=a.n)
        paths = []
        for i, d in enumerate(r.data, 1):
            p = out if a.n == 1 else out.with_name(f"{out.stem}-{i}{out.suffix}")
            p.write_bytes(base64.b64decode(d.b64_json))
            paths.append(str(p.relative_to(ROOT)))
        res = "\n".join(paths)
    ok = out.exists() or any(out.parent.glob(out.stem + "-*" + out.suffix))
    log("image", a.prompt, a.out, ok, time.time() - t0, be)
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


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    i = sp.add_parser("image")
    i.add_argument("prompt")
    i.add_argument("--out", required=True)
    i.add_argument("--size", default="1536x1024")
    i.add_argument("--n", type=int, default=1)
    i.add_argument("--ref", nargs="*", default=[])
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

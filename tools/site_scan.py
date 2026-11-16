"""고객사 홈페이지 조사: 브랜드 색·로고·인용 가능한 문구·숫자 후보를 모은다.

사용: python tools/site_scan.py https://example.com --out output/ir-abc/site [--max-pages 8]
결과 (out 폴더):
  site.md        사람이 읽는 보고서 (페이지별 핵심 문구, 숫자 후보, 출처 URL)
  site.json      원자료
  logo.*         찾은 로고 이미지 (있으면) → tools/make_tokens.py --from-image 로 색 추출
  colors.txt     CSS·메타에서 찾은 색 빈도
같은 사이트(도메인) 안의 회사소개·서비스·뉴스 등 핵심 페이지만 최대 N개 방문한다.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import argparse
import json
import re
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) site-research/1.0"}
PRIORITY = ["about", "company", "회사", "소개", "intro", "story", "vision", "mission", "비전", "history", "연혁",
            "service", "서비스", "product", "제품", "solution", "business", "team", "people", "팀",
            "partner", "award", "press", "보도", "news", "뉴스", "media"]
KEY_PATHS = re.compile("(" + "|".join(PRIORITY) + r"|(?<![a-z])ir(?![a-z]))", re.I)
SKIP = re.compile(r"(blog|login|signin|signup|cart|policy|privacy|terms|recruit|career|채용|약관|개인정보|/tag/|/category/)", re.I)


def priority(url, label):
    s = (url + " " + label).lower()
    return next((i for i, k in enumerate(PRIORITY) if k in s), len(PRIORITY))
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")
NUMLINE = re.compile(r"[^.\n]{0,60}\d[\d,.]*\s*(%|억|만|천|명|개|곳|건|배|년|위|회|원|조|만명|개국|社)[^.\n]{0,40}")


def get(url, timeout=15):
    r = requests.get(url, headers=UA, timeout=timeout)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or r.encoding
    return r


def norm_hex(h):
    h = h.lstrip("#").upper()
    return "#" + ("".join(c * 2 for c in h) if len(h) == 3 else h)


def is_neutral(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return max(r, g, b) - min(r, g, b) < 18      # 회색·흰·검정 제외


def page_text(soup):
    for t in soup(["script", "style", "noscript", "svg", "nav", "footer", "form"]):
        t.decompose()
    heads = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
    paras = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "li"])]
    heads = [h for h in heads if 4 <= len(h) <= 120]
    paras = [p for p in paras if 20 <= len(p) <= 400]
    return heads, paras


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-pages", type=int, default=8)
    a = ap.parse_args()
    out = Path(a.out) if Path(a.out).is_absolute() else ROOT / a.out
    out = out.resolve()
    if not (out.is_relative_to(ROOT) or "Temp" in out.parts):
        _sys.exit(f"저장 위치가 프로젝트 밖임: {out} — 프로젝트 안 경로(예: output/ir-abc/site)를 쓸 것")
    out.mkdir(parents=True, exist_ok=True)
    base = a.url if a.url.startswith("http") else "https://" + a.url
    host = urlparse(base).netloc

    r = get(base)
    soup = BeautifulSoup(r.text, "html.parser")
    meta = {
        "title": soup.title.get_text(strip=True) if soup.title else "",
        "description": (soup.find("meta", attrs={"name": "description"}) or {}).get("content", ""),
        "og_title": (soup.find("meta", property="og:title") or {}).get("content", ""),
        "og_description": (soup.find("meta", property="og:description") or {}).get("content", ""),
        "og_image": (soup.find("meta", property="og:image") or {}).get("content", ""),
        "theme_color": (soup.find("meta", attrs={"name": "theme-color"}) or {}).get("content", ""),
    }

    # ---- 색: 인라인 스타일 + 링크된 CSS ----
    colors = Counter()
    css_text = " ".join(s.get_text() for s in soup.find_all("style"))
    css_text += " ".join(t.get("style", "") for t in soup.find_all(style=True))
    for link in soup.find_all("link", rel=lambda v: v and "stylesheet" in v)[:6]:
        try:
            css_text += get(urljoin(base, link["href"]), 10).text
        except Exception:  # noqa: BLE001
            pass
    for m in HEX.findall(css_text):
        colors[norm_hex(m)] += 1
    for m in RGB.findall(css_text):
        colors["#%02X%02X%02X" % tuple(min(255, int(x)) for x in m)] += 1
    if meta["theme_color"].startswith("#"):
        colors[norm_hex(meta["theme_color"])] += 50
    brand_colors = [(c, n) for c, n in colors.most_common(60) if not is_neutral(c)][:8]

    # ---- 로고 ----
    logo_url = ""
    for img in soup.find_all("img"):
        attrs = " ".join([img.get("alt", ""), img.get("src", ""), " ".join(img.get("class", [])), img.get("id", "")])
        if re.search(r"logo|로고|brand|ci\b", attrs, re.I) and img.get("src"):
            logo_url = urljoin(base, img["src"])
            break
    logo_file = ""
    for cand in [logo_url, meta["og_image"] and urljoin(base, meta["og_image"])]:
        if not cand or cand.startswith("data:"):
            continue
        try:
            ext = (Path(urlparse(cand).path).suffix or ".png").lower()
            if ext not in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"):
                ext = ".png"
            name = ("logo" if cand == logo_url else "og-image") + ext
            (out / name).write_bytes(get(cand).content)
            logo_file = logo_file or name
        except Exception:  # noqa: BLE001
            continue

    # ---- 핵심 페이지 방문 ----
    found = {}
    for aa in soup.find_all("a", href=True):
        u = urljoin(base, aa["href"]).split("#")[0].split("?")[0]
        if urlparse(u).netloc != host or u.rstrip("/") == base.rstrip("/") or u in found:
            continue
        label = aa.get_text(" ", strip=True)
        path = urlparse(u).path
        if SKIP.search(path) or path.count("/") > 4:
            continue
        if KEY_PATHS.search(path) or KEY_PATHS.search(label):
            found[u] = priority(path, label)
    links = sorted(found, key=found.get)
    pages = [{"url": base, **dict(zip(("heads", "paras"), page_text(soup)))}]
    for u in links[: a.max_pages - 1]:
        time.sleep(1)                              # 사이트에 부담 주지 않게
        try:
            s = BeautifulSoup(get(u).text, "html.parser")
            h, p = page_text(s)
            pages.append({"url": u, "title": s.title.get_text(strip=True) if s.title else "", "heads": h, "paras": p})
        except Exception as e:  # noqa: BLE001
            pages.append({"url": u, "error": str(e)[:120], "heads": [], "paras": []})

    # ---- 숫자 후보 (출처 URL 포함) ----
    numbers = []
    for pg in pages:
        for t in pg["heads"] + pg["paras"]:
            for m in NUMLINE.finditer(t):
                s = m.group(0).strip()
                if s not in [n["text"] for n in numbers]:
                    numbers.append({"text": s, "url": pg["url"]})

    data = {"site": base, "meta": meta, "brand_colors": brand_colors, "logo_file": logo_file,
            "pages": pages, "number_candidates": numbers[:60]}
    (out / "site.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "colors.txt").write_text("\n".join(f"{c}\t{n}" for c, n in colors.most_common(40)), encoding="utf-8")

    md = [f"# 고객사 홈페이지 조사: {meta['title'] or host}", "", f"- 사이트: {base}", f"- 수집: {time.strftime('%Y-%m-%d')} (자동 수집 초안, Claude 검토 전)", "",
          "## 브랜드 단서", f"- 사이트 설명: {meta['description'] or meta['og_description'] or '-'}",
          f"- theme-color: {meta['theme_color'] or '-'}",
          f"- 색 후보(빈도순, 무채색 제외): {', '.join(f'{c}({n})' for c, n in brand_colors) or '-'}",
          f"- 로고 파일: {logo_file or '못 찾음'}", "",
          "## 인용 후보 (페이지별 제목·핵심 문장)", "> 고객사 자신의 문구라 고객 IR에 쓸 수 있지만, 최종 사용 전 고객 확인 필요. 출처 URL을 남길 것."]
    for pg in pages:
        if pg.get("error"):
            md.append(f"\n### {pg['url']}\n(불러오기 실패: {pg['error']})")
            continue
        md.append(f"\n### {pg.get('title') or pg['url']}\n{pg['url']}")
        md += [f"- **{h}**" for h in pg["heads"][:8]]
        md += [f"- {p}" for p in pg["paras"][:5]]
    md += ["", "## 숫자 후보 (IR data로 옮기기 전 고객 확인 필요)", "| 문장 | 출처 |", "|---|---|"]
    md += [f"| {n['text']} | {n['url']} |" for n in numbers[:40]] or ["| (없음) | |"]
    (out / "site.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"저장: {a.out}/site.md (페이지 {len(pages)}개, 색 후보 {len(brand_colors)}개, 숫자 후보 {len(numbers)}개, 로고: {logo_file or '없음'})")


if __name__ == "__main__":
    main()

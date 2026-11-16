"""v007 데이터 생성: 사진 파일명(작가명 작품제목.jpg)을 기준으로 작가·작품을 연결하고 JSX용 데이터를 만든다."""
import glob, json, os, re, sys, unicodedata
from PIL import Image
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = f"{root}/links/photos-cmyk/works"; A = f"{root}/links/photos-cmyk/activity"; G = f"{root}/links/photos-cmyk/toc-temp"
def rel(p): return os.path.relpath(p, root)
def size(p): return list(Image.open(p).size)
artists = {}
for f in sorted(glob.glob(W + "/*.jpg")):
    stem = unicodedata.normalize('NFC', os.path.basename(f)[:-4]); name, title = stem.split(' ', 1)
    artists.setdefault(name, []).append({"title": title, "path": rel(f), "px": size(f)})
assert len(artists) == 10 and all(len(v) == 2 for v in artists.values()), artists.keys()
acts = sorted(glob.glob(A + "/*.jpg"), key=lambda f: int(re.findall(r'\d+', os.path.basename(f))[0]))
acts = [{"no": int(re.findall(r'\d+', os.path.basename(f))[0]), "path": rel(f), "px": size(f)} for f in acts]
# 목차 배경용 임시 흑백(활동사진 10~15)
os.makedirs(G, exist_ok=True); toc = []
for a in acts[9:15]:
    src = f"{root}/{a['path']}"; dst = f"{G}/gray_{a['no']:02d}.jpg"
    if not os.path.exists(dst):
        im = Image.open(src); im.draft('CMYK', (1600, 1600)); im.convert('RGB').convert('L').save(dst, quality=90, dpi=(300, 300))
    toc.append({"no": a["no"], "path": rel(dst), "px": size(dst)})
T = "(임의) "
data = {
  "title": "인생사진첩", "subtitle": "「프레임에 담긴 나의 세상」",
  "org": "동래구노인복지관 재가노인지원서비스센터",
  "support": "본 제작물은 부산사회복지공동모금회의 지원으로 제작되었습니다.",
  "artists": [{"name": n, "works": w} for n, w in sorted(artists.items())],
  "program_photos": acts[0:3], "closing_photos": acts[3:9], "toc_photos": toc,
  "desc_placeholder": T + "작품 설명 원고를 받으면 교체합니다.",
  "greeting": T + "사진을 찍는 일은 익숙한 일상을 새로운 눈으로 바라보는 일입니다. 무심히 지나쳤던 골목과 창가, 작은 꽃과 나무가 카메라를 통해 저마다의 이야기를 들려주었습니다.\r이 작품집에는 가까운 곳에서 아름다움을 발견하고, 자신의 시선으로 한 장면을 골라 기록해 보는 과정의 의미를 담고자 했습니다. 사진의 기술보다 소중한 것은 직접 바라보고 느낀 마음입니다.\r서로의 사진을 보고 이야기를 나누는 동안, 평범했던 하루는 함께 기억하고 싶은 시간이 되었습니다. 한 장의 사진에 담긴 생각과 감정이 보는 분들의 일상에도 작은 쉼이 되기를 바랍니다.\r새로운 도전에 마음을 열고 자신의 이야기를 사진으로 표현하신 모든 분께 따뜻한 응원을 전합니다. 감사합니다.",
  "program_copy": T + "카메라로 일상을 기록하고 사진 속 이야기를 나누는 시간입니다. 가까운 동네와 자연에서 나만의 장면을 찾고, 서로의 시선을 이해하며 사진과 글로 한 권의 이야기를 만들어 갑니다.",
  "sessions": [T + s for s in ["나의 시선 소개하기", "카메라와 친해지기", "빛과 그림자 살펴보기", "우리 동네 천천히 걷기", "자연의 색 발견하기", "사진 속 이야기 나누기", "나의 작품 고르기", "사진과 글 함께 엮기"]],
  "staff": T + "강사·봉사자 명단 원고를 받으면 교체합니다.",
  "org_info": T + "기관 주소·연락처 원고를 받으면 교체합니다.",
}
open(f"{root}/data/album_v007.json", "w").write(json.dumps(data, ensure_ascii=False, indent=1))
open(f"{root}/data/album_v007.jsxinc", "w").write("var ALBUM=" + json.dumps(data, ensure_ascii=False) + ";\n")
print("작가", [a["name"] for a in data["artists"]]); print("활동 3쪽", [a["no"] for a in acts[0:3]], "24쪽", [a["no"] for a in acts[3:9]], "목차배경", [a["no"] for a in toc])

# --- v005 내지 레이아웃 유지용: 예시 소개·세로제목·인용(임의 표기)과 작가별 포인트색(CMYK) ---
C = json.load(open(f"{root}/data/demo_content_v005.json"))
L = json.load(open(f"{root}/data/layout_demo_full_v005.json"))
def to_cmyk(rgb):
    r, g, b = [v / 255 for v in rgb]; k = 1 - max(r, g, b)
    if k >= 1: return [0, 0, 0, 100]
    return [round((1 - v - k) / (1 - k) * 100) for v in (r, g, b)] + [round(k * 100)]
for i, a in enumerate(data["artists"]):
    au = C["authors"][i]
    a["bio"] = T + au["bio"].replace("\n", "\r")
    a["side_title"] = "(임의)\r" + au["side_title"].replace("\n", "\r")
    a["quote"] = T + au["quote"].replace("\n", "\r")
    a["accent"] = to_cmyk(L["colors"]["accent_A%02d" % (i + 1)])
data["v005_colors"] = {k: to_cmyk(L["colors"][k]) for k in ("ink", "muted", "line", "soft")}
open(f"{root}/data/album_v007.json", "w").write(json.dumps(data, ensure_ascii=False, indent=1))
open(f"{root}/data/album_v007.jsxinc", "w").write("var ALBUM=" + json.dumps(data, ensure_ascii=False) + ";\n")
print("v005 예시 원고·색상 추가")

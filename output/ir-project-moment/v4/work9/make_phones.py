"""GPT 아이폰 프레임(초록 화면)에 캡처를 합성해 실제 아이폰 목업 PNG를 만든다."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(r"C:\Users\admin\클로드")
FRAME = ROOT / "assets/generated/pm-ir-v9-iphone-frame.png"
OUT = ROOT / "output/ir-project-moment/v4/work9/phones"
OUT.mkdir(parents=True, exist_ok=True)

fr = Image.open(FRAME).convert("RGB")
a = np.asarray(fr).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
green = (g > 150) & (r < 120) & (b < 120)
ys, xs = np.where(green)
sx0, sx1, sy0, sy1 = xs.min(), xs.max(), ys.min(), ys.max()
# 기기 영역(흰 배경 아닌 곳)
nonwhite = (a.min(axis=2) < 235)
dy, dx = np.where(nonwhite)
dx0, dx1, dy0, dy1 = dx.min(), dx.max(), dy.min(), dy.max()

# 초록 정도로 부드러운 화면 알파(가장자리 안티앨리어싱 유지)
gscore = np.clip((g - np.maximum(r, b) - 40) / 120.0, 0, 1)
screen_alpha = Image.fromarray((gscore * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.6))
# 배경(흰색) 투명 처리: 흰 정도로 알파
whiteness = np.clip((a.min(axis=2) - 235) / 20.0, 0, 1)
bg_alpha = (1 - whiteness)
# 기기 바깥 흰 배경만 투명하게(기기 내부 밝은 금속 테두리는 유지): 기기 bbox 밖 + 아주 흰 곳
dev_alpha = Image.fromarray((bg_alpha * 255).astype("uint8"))


def make(shot_path, name, fit="cover", bg=(255, 255, 255)):
    shot = Image.open(shot_path).convert("RGB")
    W, H = sx1 - sx0 + 1, sy1 - sy0 + 1
    if fit == "cover":
        s = max(W / shot.width, H / shot.height)
        sh = shot.resize((int(shot.width * s + 1), int(shot.height * s + 1)), Image.LANCZOS)
        l, t = (sh.width - W) // 2, 0 if sh.height / H < 1.15 else (sh.height - H) // 2
        sh = sh.crop((l, t, l + W, t + H))
    else:  # contain: 위 정렬, 남는 곳은 bg
        s = min(W / shot.width, H / shot.height)
        sh0 = shot.resize((int(shot.width * s), int(shot.height * s)), Image.LANCZOS)
        sh = Image.new("RGB", (W, H), bg)
        sh.paste(sh0, ((W - sh0.width) // 2, int(H * 0.06)))
    canvas = fr.copy()
    layer = Image.new("RGB", fr.size, bg)
    layer.paste(sh, (sx0, sy0))
    canvas.paste(layer, (0, 0), screen_alpha)
    rgba = canvas.convert("RGBA")
    rgba.putalpha(dev_alpha)
    rgba = rgba.crop((dx0, dy0, dx1 + 1, dy1 + 1))
    p = OUT / f"{name}.png"
    rgba.save(p)
    return p


if __name__ == "__main__":
    media = ROOT / "ir/inbox/project-moment/media"
    for n in ("image24", "image25", "image26", "image27", "image30"):
        print(make(media / f"{n}.png", f"p10_{n}"))
    w9 = ROOT / "output/ir-project-moment/v4/work9"
    print(make(w9 / "s15_52.png", "p15_video"))
    print(make(w9 / "s15_57.png", "p15_post", fit="contain"))
    print("device ratio", (dx1 - dx0 + 1) / (dy1 - dy0 + 1))

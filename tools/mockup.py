"""화면 캡처를 기기 목업으로 감싸기 + PPTX 안 이미지 교체.

  python tools/mockup.py make phone|browser|card <캡처.png> <출력.png>
  python tools/mockup.py pptx <입력.pptx> <출력.pptx> 8:그림 20=phone 8:그림 24=browser 12:그림 5=browser ...
     (슬라이드번호:도형이름=목업종류) — 원래 자리 안에 비율 유지해 가운데 배치

- phone  : 검은 테두리 + 둥근 모서리 휴대폰 (캡처에 상태바가 있으면 그대로 사용, 노치 중복 없음)
- browser: 연회색 상단바(점 3개) + 둥근 모서리 창 + 얇은 테두리
- card   : 둥근 모서리 + 얇은 테두리만 (썸네일 묶음 등)
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import io

from PIL import Image, ImageDraw


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255)
    return m


def phone(shot):
    shot = shot.convert("RGB")
    w, h = shot.size
    scale = 1200 / max(w, h) if max(w, h) > 1200 else 1
    shot = shot.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    w, h = shot.size
    bez = max(8, int(w * 0.035))
    R = int(w * 0.13)
    W, H = w + bez * 2, h + bez * 2
    out = Image.new("RGBA", (W + 6, H), (0, 0, 0, 0))
    body = Image.new("RGBA", (W, H), (22, 22, 24, 255))
    out.paste(body, (3, 0), rounded_mask((W, H), R + bez))
    # 옆 버튼
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((0, int(H * 0.22), 4, int(H * 0.30)), 2, fill=(40, 40, 44, 255))
    d.rounded_rectangle((W + 2, int(H * 0.27), W + 6, int(H * 0.38)), 2, fill=(40, 40, 44, 255))
    out.paste(shot, (3 + bez, bez), rounded_mask((w, h), R))
    return out


def browser(shot):
    shot = shot.convert("RGB")
    w, h = shot.size
    scale = 1600 / w if w > 1600 else 1
    shot = shot.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    w, h = shot.size
    bar = max(22, int(w * 0.045))
    R = max(8, int(w * 0.018))
    W, H = w + 2, h + bar + 2
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    frame = Image.new("RGBA", (W, H), (214, 216, 222, 255))           # 얇은 테두리 색
    out.paste(frame, (0, 0), rounded_mask((W, H), R))
    inner = Image.new("RGBA", (W - 2, H - 2), (240, 241, 244, 255))   # 상단바 색
    inner.paste(shot, (0, bar))
    m = rounded_mask((W - 2, H - 2), R - 1)
    out.paste(inner, (1, 1), m)
    d = ImageDraw.Draw(out)
    r = max(3, bar // 6)
    for i, col in enumerate([(236, 106, 94), (244, 191, 79), (98, 197, 84)]):
        cx, cy = 1 + bar // 2 + i * (r * 3 + 2), 1 + bar // 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    # 주소창
    d.rounded_rectangle((int(W * 0.3), int(bar * 0.25), int(W * 0.7), int(bar * 0.78)), int(bar * 0.25), fill=(255, 255, 255, 255))
    return out


def card(shot):
    shot = shot.convert("RGB")
    w, h = shot.size
    R = max(8, int(min(w, h) * 0.06))
    out = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    out.paste(Image.new("RGBA", (w + 2, h + 2), (214, 216, 222, 255)), (0, 0), rounded_mask((w + 2, h + 2), R + 1))
    out.paste(shot, (1, 1), rounded_mask((w, h), R))
    return out


KINDS = {"phone": phone, "browser": browser, "card": card}


def cmd_pptx(inp, out, specs):
    from pptx import Presentation
    prs = Presentation(inp)
    done = 0
    for spec in specs:
        loc, kind = spec.rsplit("=", 1)
        si, name = loc.split(":", 1)
        s = prs.slides[int(si) - 1]
        shp = next((sh for sh in s.shapes if sh.name == name and sh.shape_type == 13), None)
        if shp is None:
            print("못 찾음:", spec)
            continue
        src = Image.open(io.BytesIO(shp.image.blob))
        # 원래 잘라 쓰던 부분(crop)만 목업에 넣는다
        w, h = src.size
        l, t = int(w * shp.crop_left), int(h * shp.crop_top)
        r, b = int(w * (1 - shp.crop_right)), int(h * (1 - shp.crop_bottom))
        src = src.crop((l, t, r, b))
        mk = KINDS[kind](src)
        buf = io.BytesIO()
        mk.save(buf, "PNG")
        bw, bh = shp.width, shp.height
        k = min(bw / mk.width, bh / mk.height)
        nw, nh = int(mk.width * k), int(mk.height * k)
        x, y = shp.left + (bw - nw) // 2, shp.top + (bh - nh) // 2
        pic = s.shapes.add_picture(buf, x, y, nw, nh)
        pic.name = f"{name} (목업 {kind})"
        el = shp._element
        el.addnext(pic._element)          # 같은 겹침 순서 유지
        el.getparent().remove(el)
        done += 1
    prs.save(out)
    print(f"목업 교체 {done}개")


if __name__ == "__main__":
    a = _sys.argv[1:]
    if a[0] == "make":
        KINDS[a[1]](Image.open(a[2])).save(a[3])
        print("저장:", a[3])
    elif a[0] == "pptx":
        cmd_pptx(a[1], a[2], a[3:])

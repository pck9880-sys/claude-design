"""links/photos/ 의 RGB 원본을 links/photos-cmyk/ 에 CMYK JPEG(300ppi)로 변환한다.

프로파일: Japan Color 2001 Coated (인쇄소 지정 ICC가 오면 --profile 로 바꾼다).
- 원본은 수정하지 않는다. 휴대폰 회전 정보(EXIF)는 적용해서 저장한다.
- 이미 변환된 파일은 건너뛴다(--force 로 다시 변환).
사용: python scripts/convert_cmyk.py [--profile <icc 경로>] [--force]
필요: Pillow (pip install pillow)
"""
import argparse, glob, io, os, platform, sys
from PIL import Image, ImageCms, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULTS = {
    "Darwin": "/Library/Application Support/Adobe/Color/Profiles/Recommended/JapanColor2001Coated.icc",
    "Windows": r"C:\Program Files (x86)\Common Files\Adobe\Color\Profiles\Recommended\JapanColor2001Coated.icc",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default=DEFAULTS.get(platform.system(), ""))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(a.profile):
        sys.exit("ICC 프로파일을 찾지 못했습니다: %s (--profile 로 지정)" % a.profile)
    dst_prof = ImageCms.getOpenProfile(a.profile)
    dst_bytes = open(a.profile, "rb").read()
    ok = skip = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "links", "photos", "*", "*.jpg"))):
        sub = os.path.basename(os.path.dirname(f))
        out = os.path.join(ROOT, "links", "photos-cmyk", sub, os.path.basename(f))
        if os.path.exists(out) and not a.force:
            skip += 1
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        raw = Image.open(f)
        icc = raw.info.get("icc_profile")
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc)) if icc else ImageCms.createProfile("sRGB")
        img = ImageOps.exif_transpose(raw).convert("RGB")
        cm = ImageCms.profileToProfile(img, src, dst_prof, renderingIntent=ImageCms.Intent.PERCEPTUAL, outputMode="CMYK")
        cm.save(out + ".tmp", "JPEG", quality=95, icc_profile=dst_bytes, dpi=(300, 300))
        os.replace(out + ".tmp", out)
        ok += 1
    print("변환 %d / 건너뜀 %d" % (ok, skip))

if __name__ == "__main__":
    main()

"""OpenAI 이미지 생성 API로 블로그 이미지 5장(1536x1024, 3:2)을 만듭니다.

- API 키는 프로젝트 루트 .env 의 OPENAI_API_KEY 에서 읽습니다.
- 결론 이미지는 AI 배경 위에 Pillow로 한글 브랜드명을 직접 씁니다 (글자 깨짐 방지).
사용법: uv run python naver-blog-post/make_images_ai.py [01 02 ...]
"""
import base64
import io
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).parent
OUT = BASE / "images"
OUT.mkdir(exist_ok=True)
load_dotenv(BASE.parent / ".env")

MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")  # 이 계정에서 쓸 수 있는 모델 (2026-11 확인)
client = OpenAI()  # OPENAI_API_KEY 환경변수 사용

STYLE = ("Photorealistic photo taken on a smartphone, soft film-like color grading, "
         "warm muted tones, subtle film grain, natural light. No text, no letters, no logos, "
         "no recognizable real people or famous characters.")

PROMPTS = {
    "01_intro": "A cozy window sill at golden hour, warm sunset light streaming in, a small potted plant "
                "and a coffee cup, a hand holding a smartphone taking a photo of the scene (screen not readable), "
                "nostalgic film mood.",
    "02_body1": "A quiet Korean side street cafe interior next to a large window, soft side light falling "
                "on a table with flowers, long gentle shadows of golden hour, demonstrates beautiful natural window light.",
    "03_body2": "Minimal composition photo: a single small tree on the left third of the frame, wide empty "
                "pale blue sky and plain wall as negative space on the right, rule of thirds, calm and airy.",
    "04_body3": "Flat lay on a wooden desk: a smartphone showing a generic photo editing screen with abstract "
                "slider bars (no readable text), a printed film-toned photo, a notebook and a pen, warm cozy light.",
    "05_outro": "Dark moody still life background for a photo studio brand: a vintage film camera lens and "
                "a film strip on a dark wooden surface, warm spot light, large empty dark area in the center "
                "for text overlay.",
}

ALTS = {
    "01_intro": "노을빛이 드는 창가를 스마트폰으로 촬영하는 모습",
    "02_body1": "창가로 들어오는 부드러운 골든아워 햇살이 비치는 카페 테이블",
    "03_body2": "왼쪽 3분의 1 지점에 나무를 두고 하늘을 여백으로 비운 구도",
    "04_body3": "필름 톤으로 사진을 보정하는 스마트폰 편집 화면과 인화 사진",
    "05_outro": "지담 스튜디오 브랜드명과 '일상을 작품으로' 문구가 담긴 마무리 이미지",
}


def generate(name: str) -> Image.Image:
    res = client.images.generate(
        model=MODEL,
        prompt=f"{PROMPTS[name]} {STYLE}",
        size="1536x1024",
        quality="medium",
        n=1,
    )
    return Image.open(io.BytesIO(base64.b64decode(res.data[0].b64_json))).convert("RGB")


def add_brand(img: Image.Image) -> Image.Image:
    W, H = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, H * 0.30, W, H * 0.72], fill=(20, 16, 14, 150))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)

    def center(y, text, size, fill, bold=True):
        f = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf", size)
        w = d.textlength(text, font=f)
        d.text(((W - w) / 2, y), text, font=f, fill=fill)

    center(H * 0.34, "지담 스튜디오", 120, (250, 236, 215))
    center(H * 0.52, "일상을 작품으로 남기는 사진 스튜디오", 44, (232, 204, 165), bold=False)
    center(H * 0.61, "스마트폰 하나로도 감성 사진은 충분하다", 38, (215, 185, 150))
    return img


def main():
    targets = [n for n in PROMPTS if not sys.argv[1:] or n[:2] in sys.argv[1:]]
    for name in targets:
        print(f"생성 중: {name} ...", flush=True)
        img = generate(name)
        if name == "05_outro":
            img = add_brand(img)
        img.save(OUT / f"{name}.png")
        print(f"  저장: images/{name}.png {img.size}  alt: {ALTS[name]}", flush=True)


if __name__ == "__main__":
    main()

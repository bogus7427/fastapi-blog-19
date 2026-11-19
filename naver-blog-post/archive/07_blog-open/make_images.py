"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 블로그 오픈 인사)"""
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (58, 46, 42)
GOLD = (225, 200, 165)
ACCENT = (200, 120, 80)
DARK = (34, 30, 30)


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def glow(size, center, radius, color, strength):
    g = Image.new("RGB", size)
    d = ImageDraw.Draw(g)
    cx, cy = center
    for r in range(radius, 0, -8):
        t = (1 - r / radius) ** 1.5
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(c * t * strength) for c in color))
    return g.filter(ImageFilter.GaussianBlur(30))


def noise(img, alpha=0.03, seed=1):
    rnd = random.Random(seed)
    n = Image.new("L", img.size)
    n.putdata([128 + rnd.randint(-12, 12) for _ in range(img.size[0] * img.size[1])])
    return Image.blend(img, n.convert("RGB"), alpha)


def center_text(d, y, text, f, fill, x0=0, width=W):
    w = d.textlength(text, font=f)
    d.text((x0 + (width - w) / 2, y), text, font=f, fill=fill)


def film_strip(d, y0, h=50):
    d.rectangle([0, y0, W, y0 + h], fill=(14, 13, 13))
    for x in range(20, W, 60):
        d.rounded_rectangle([x, y0 + h * 0.28, x + 32, y0 + h * 0.72], 4, fill=GOLD)


def softbox(d, x, y, s=1.0):
    d.polygon([(x, y), (x + 160 * s, y), (x + 140 * s, y + 210 * s), (x + 20 * s, y + 210 * s)], fill=(70, 66, 64))
    d.rectangle([x + 14 * s, y + 10 * s, x + 146 * s, y + 200 * s], fill=(255, 252, 244))
    sx = x + 80 * s
    d.rectangle([sx - 4, y + 210 * s, sx + 4, y + 470 * s], fill=(90, 86, 84))
    for dx in (-60, 0, 60):
        d.line([(sx, y + 420 * s), (sx + dx * s, y + 490 * s)], fill=(90, 86, 84), width=6)


# 01 서론: 스튜디오 문 열림 + 블로그 오픈
def intro():
    img = gradient(W, H, (226, 220, 212), (240, 236, 230))
    img = ImageChops.add(img, glow((W, H), (600, 380), 520, (30, 26, 18), 1.0))
    d = ImageDraw.Draw(img)
    softbox(d, 60, 150)
    softbox(d, 980, 150)
    # 문
    dx, dy, dw, dh = 430, 150, 340, 520
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=(255, 248, 232))
    d.polygon([(dx, dy), (dx + 120, dy + 40), (dx + 120, dy + dh - 20), (dx, dy + dh)], fill=(150, 110, 85))
    d.ellipse([dx + 95, dy + dh / 2 - 8, dx + 111, dy + dh / 2 + 8], fill=GOLD)
    d.rectangle([dx - 12, dy - 12, dx + dw + 12, dy + dh], outline=(110, 90, 80), width=12)
    # 간판
    d.rounded_rectangle([dx - 40, 60, dx + dw + 40, 130], 16, fill=DARK)
    center_text(d, 70, "지담 스튜디오", font(40, True), GOLD, x0=dx - 40, width=dw + 80)
    # 오픈 리본
    d.rounded_rectangle([dx + 135, dy + 210, dx + dw - 15, dy + 290], 14, fill=ACCENT)
    center_text(d, dy + 226, "BLOG OPEN", font(34, True), (255, 255, 255), x0=dx + 135, width=dw - 150)
    center_text(d, 700, "일상을 작품으로 남기는 사진 이야기를 시작합니다", font(34, True), INK)
    noise(img, seed=2).save(OUT / "01_intro.png")


# 02 본론1: 책상 위 소개
def body1():
    img = gradient(W, H, (242, 236, 228), (226, 216, 204))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "지담 스튜디오 블로그는 이런 곳이에요", font(44, True), INK)
    # 책상
    d.rounded_rectangle([60, 470, W - 60, 720], 20, fill=(176, 132, 100))
    # 카메라
    d.rounded_rectangle([110, 360, 330, 500], 18, fill=DARK)
    d.rectangle([150, 340, 210, 365], fill=DARK)
    d.ellipse([170, 380, 270, 480], fill=(70, 70, 76))
    d.ellipse([190, 400, 250, 460], fill=(30, 30, 36))
    # 스마트폰
    d.rounded_rectangle([370, 330, 470, 510], 16, fill=(40, 40, 46))
    d.rectangle([380, 345, 460, 490], fill=(250, 210, 160))
    # 인화 사진들
    rnd = random.Random(3)
    for i, c in enumerate([(240, 170, 130), (140, 180, 210), (170, 200, 150)]):
        x = 500 + i * 70
        ph = Image.new("RGB", (120, 140), (255, 255, 255))
        pd = ImageDraw.Draw(ph)
        pd.rectangle([8, 8, 112, 104], fill=c)
        ph = ph.rotate(rnd.randint(-12, 12), expand=True, fillcolor=(176, 132, 100))
        img.paste(ph, (x, 380))
    d = ImageDraw.Draw(img)
    # 약속 카드
    cx, cy = 790, 150
    d.rounded_rectangle([cx, cy, cx + 340, cy + 330], 20, fill=(255, 255, 255))
    d.text((cx + 26, cy + 20), "세 가지 약속", font=font(30, True), fill=INK)
    for i, t in enumerate(("구체적인 설정값과 순서", "쉬운 말로 풀어 쓰기", "과장 없이 솔직하게")):
        y = cy + 90 + i * 70
        d.ellipse([cx + 26, y, cx + 62, y + 36], fill=ACCENT)
        center_text(d, y + 2, str(i + 1), font(24, True), (255, 255, 255), x0=cx + 26, width=36)
        d.text((cx + 78, y + 2), t, font=font(24), fill=INK)
    center_text(d, 740, "스마트폰 하나로도 감성 사진은 충분하다", font(28, True), (110, 80, 66))
    noise(img, seed=4).save(OUT / "02_body1.png")


# 03 본론2: 카테고리 6개
def body2():
    img = gradient(W, H, (244, 240, 234), (230, 222, 212))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "카테고리별로 이런 글을 만나요", font(44, True), INK)
    cats = [
        ("스마트폰 사진 팁", "디카 감성 · 유행 톤", (240, 170, 120)),
        ("보정 노하우", "보정 순서 · 색 레시피", (220, 140, 110)),
        ("감성 사진 갤러리", "장면 모음 · 찍는 법", (150, 160, 210)),
        ("촬영 후기", "직접 찍어 본 기록", (240, 150, 110)),
        ("카메라 촬영 기초", "셔터 · ISO · 조리개", (120, 160, 200)),
        ("스튜디오 소식", "블로그 · 스튜디오 소식", (170, 140, 120)),
    ]
    cw, ch, gx, gy = 330, 250, 45, 40
    x0 = (W - cw * 3 - gx * 2) / 2
    for i, (name, sub, c) in enumerate(cats):
        x = int(x0 + (i % 3) * (cw + gx))
        y = 130 + (i // 3) * (ch + gy)
        d.rounded_rectangle([x, y, x + cw, y + ch], 20, fill=(255, 255, 255))
        d.rounded_rectangle([x, y, x + cw, y + 90], 20, fill=c)
        d.rectangle([x, y + 60, x + cw, y + 90], fill=c)
        center_text(d, y + 22, f"0{i + 1}", font(36, True), (255, 255, 255), x0=x, width=cw)
        center_text(d, y + 115, name, font(30, True), INK, x0=x, width=cw)
        center_text(d, y + 170, sub, font(22), (130, 110, 100), x0=x, width=cw)
        if i == 5:
            d.rounded_rectangle([x + cw - 92, y + ch - 46, x + cw - 14, y - 12 + ch], 10, fill=ACCENT)
            center_text(d, y + ch - 44, "지금 글", font(18, True), (255, 255, 255), x0=x + cw - 92, width=78)
    noise(img, seed=5).save(OUT / "03_body2.png")


# 04 본론3: 달력 + 메모 + 댓글
def body3():
    img = gradient(W, H, (242, 236, 228), (228, 218, 206))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "앞으로 이런 이야기를 준비해요", font(44, True), INK)
    # 달력
    cx, cy, cw, ch = 90, 130, 560, 560
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], 20, fill=(255, 255, 255))
    d.rounded_rectangle([cx, cy, cx + cw, cy + 80], 20, fill=DARK)
    d.rectangle([cx, cy + 50, cx + cw, cy + 80], fill=DARK)
    center_text(d, cy + 18, "다음 글 계획", font(34, True), GOLD, x0=cx, width=cw)
    for r in range(5):
        for c in range(7):
            x = cx + 30 + c * 72
            y = cy + 110 + r * 82
            d.rounded_rectangle([x, y, x + 60, y + 66], 8, outline=(225, 215, 205), width=2)
    notes = [("계절 장면", (250, 220, 140), 1, 0), ("인물·음식·여행 팁", (200, 225, 240), 3, 1),
             ("색 레시피 더하기", (240, 200, 190), 0, 3), ("초점·화이트밸런스", (210, 235, 200), 3, 3)]
    for text, c, col, row in notes:
        x = cx + 30 + col * 72
        y = cy + 110 + row * 82
        w = d.textlength(text, font=font(22, True)) + 30
        d.rounded_rectangle([x, y + 10, x + w, y + 56], 10, fill=c)
        d.text((x + 15, y + 18), text, font=font(22, True), fill=INK)
    # 댓글 말풍선
    bx = 700
    for i, (t, side) in enumerate((("야경 보정은 어떻게 하나요?", 0), ("다음 글에서 정리해 드릴게요!", 1), ("제 사진도 봐 주세요 :)", 0))):
        y = 170 + i * 150
        x = bx + (60 if side else 0)
        w = 400
        fill = (255, 255, 255) if not side else ACCENT
        tc = INK if not side else (255, 255, 255)
        d.rounded_rectangle([x, y, x + w, y + 90], 22, fill=fill)
        tail = [(x + 40, y + 88), (x + 70, y + 88), (x + 40, y + 115)] if not side else [(x + w - 70, y + 88), (x + w - 40, y + 88), (x + w - 40, y + 115)]
        d.polygon(tail, fill=fill)
        center_text(d, y + 26, t, font(26, True), tc, x0=x, width=w)
    center_text(d, 680, "궁금한 점은 댓글로 남겨 주세요", font(28, True), ACCENT, x0=bx, width=460)
    noise(img, seed=6).save(OUT / "04_body3.png")


# 05 결론: 브랜드 (타이틀 배너와 같은 톤)
def outro():
    img = gradient(W, H, (40, 36, 34), (22, 21, 21))
    img = ImageChops.add(img, glow((W, H), (W // 2, H // 2), 520, (255, 230, 200), 0.3))
    d = ImageDraw.Draw(img)
    film_strip(d, 0, 60)
    film_strip(d, H - 60, 60)
    cx, cy = W // 2, 230
    d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], outline=GOLD, width=8)
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=GOLD)
    center_text(d, 320, "지담 스튜디오", font(100, True), (250, 238, 220))
    center_text(d, 470, "일상을 작품으로 남기는 사진 스튜디오", font(36), GOLD)
    center_text(d, 535, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (205, 180, 150))
    noise(img, seed=7).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

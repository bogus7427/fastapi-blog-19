"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 무드별 색 레시피)"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (54, 46, 44)
ACCENT = (214, 120, 84)


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def noise(img, alpha=0.03, seed=1, amount=12):
    rnd = random.Random(seed)
    n = Image.new("L", img.size)
    n.putdata([128 + rnd.randint(-amount, amount) for _ in range(img.size[0] * img.size[1])])
    return Image.blend(img, n.convert("RGB"), alpha)


def center_text(d, y, text, f, fill, x0=0, width=W):
    w = d.textlength(text, font=f)
    d.text((x0 + (width - w) / 2, y), text, font=f, fill=fill)


def vignette(img, strength=0.45):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse([-w * 0.15, -h * 0.15, w * 1.15, h * 1.15], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) // 6))
    dark = ImageEnhance.Brightness(img).enhance(1 - strength)
    return Image.composite(img, dark, mask)


def base_scene(w, h):
    """보정용 원본 장면: 하늘·바다·흰 벽·초록 식물·인물"""
    img = gradient(w, h, (150, 196, 230), (210, 228, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.5, w, h * 0.62], fill=(70, 150, 190))  # 바다
    d.rectangle([0, h * 0.62, w, h], fill=(232, 222, 206))  # 바닥
    d.rectangle([w * 0.62, h * 0.18, w, h * 0.62], fill=(246, 244, 238))  # 흰 벽
    d.rectangle([w * 0.7, h * 0.28, w * 0.86, h * 0.48], fill=(120, 170, 210))  # 창
    for k in range(4):  # 식물
        d.ellipse([w * 0.66 + k * 18, h * 0.5 - k * 14, w * 0.66 + k * 18 + 60, h * 0.5 - k * 14 + 60], fill=(80, 150, 90))
    d.rectangle([w * 0.68, h * 0.58, w * 0.8, h * 0.68], fill=(200, 120, 90))
    cx, base = w * 0.36, h * 0.9  # 인물
    # 옷은 어두운 버건디: 흑백으로 바꿔도 바다(중간 회색)와 구분되게
    d.rounded_rectangle([cx - w * 0.07, base - h * 0.32, cx + w * 0.07, base], int(w * 0.03), fill=(140, 40, 50))
    d.ellipse([cx - w * 0.045, base - h * 0.46, cx + w * 0.045, base - h * 0.31], fill=(246, 210, 186))
    d.chord([cx - w * 0.05, base - h * 0.48, cx + w * 0.05, base - h * 0.38], 180, 360, fill=(60, 42, 36))
    return img


def film(img):
    img = ImageEnhance.Brightness(img).enhance(0.95)
    img = ImageEnhance.Contrast(img).enhance(0.8)
    img = ImageEnhance.Color(img).enhance(0.82)
    warm = Image.new("RGB", img.size, (255, 200, 140))
    img = Image.blend(img, warm, 0.14)
    lift = Image.new("RGB", img.size, (40, 32, 28))
    img = Image.blend(img, lift, 0.08)  # 떠 보이는 검정
    img = noise(img, alpha=0.08, seed=3, amount=28)
    return vignette(img, 0.3)


def fresh(img):
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Color(img).enhance(1.15)
    cool = Image.new("RGB", img.size, (170, 210, 255))
    img = Image.blend(img, cool, 0.1)
    return ImageEnhance.Sharpness(img).enhance(1.6)


def mono(img):
    g = ImageOps.grayscale(img)
    g = ImageEnhance.Contrast(g).enhance(1.35)
    img = Image.merge("RGB", (g, g, g))
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    return vignette(img, 0.35)


def slider_panel(d, x, y, rows, color):
    for i, (name, val, pos) in enumerate(rows):
        yy = y + i * 62
        d.text((x, yy - 16), name, font=font(24, True), fill=INK)
        x0, x1 = x + 140, x + 350
        mid = (x0 + x1) / 2
        d.rounded_rectangle([x0, yy - 5, x1, yy + 5], 5, fill=(214, 206, 198))
        kx = x0 + (x1 - x0) * pos
        d.rounded_rectangle([min(mid, kx), yy - 5, max(mid, kx), yy + 5], 5, fill=color)
        d.line([(mid, yy - 12), (mid, yy + 12)], fill=(160, 150, 144), width=2)
        d.ellipse([kx - 15, yy - 15, kx + 15, yy + 15], fill=(255, 255, 255), outline=color, width=4)
        d.text((x1 + 18, yy - 16), val, font=font(24, True), fill=color)


# 01 서론: 세 가지 톤 나란히
def intro():
    img = gradient(W, H, (244, 240, 234), (230, 222, 212))
    d = ImageDraw.Draw(img)
    pw, ph = 340, 420
    src = base_scene(pw, ph)
    tones = [("FILM", "필름 톤", film(src)), ("FRESH", "청량 톤", fresh(src)), ("MONO", "모노 톤", mono(src))]
    x0 = (W - pw * 3 - 40 * 2) / 2
    for i, (en, ko, pic) in enumerate(tones):
        x = int(x0 + i * (pw + 40))
        d.rectangle([x - 12, 110, x + pw + 12, 110 + ph + 90], fill=(255, 255, 255))
        img.paste(pic, (x, 122))
        d = ImageDraw.Draw(img)
        center_text(d, 122 + ph + 18, f"{en} · {ko}", font(28, True), INK, x0=x, width=pw)
    center_text(d, 36, "무드별 색 레시피 3가지", font(46, True), INK)
    center_text(d, H - 80, "같은 사진, 보정값만 다르게", font(28, True), ACCENT)
    noise(img, seed=2).save(OUT / "01_intro.png")


def recipe(title, pic, rows, color, seed, fname):
    img = gradient(W, H, (244, 240, 234), (230, 222, 212))
    d = ImageDraw.Draw(img)
    center_text(d, 36, title, font(42, True), INK)
    pw, ph = 560, 420
    d.rectangle([58, 128, 58 + pw + 24, 128 + ph + 24], fill=(255, 255, 255))
    img.paste(pic.resize((pw, ph)), (70, 140))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([680, 128, 1150, 128 + 70 + 62 * len(rows)], 20, fill=(255, 255, 255))
    d.text((706, 146), "보정값", font=font(28, True), fill=INK)
    slider_panel(d, 706, 222, rows, color)
    noise(img, seed=seed).save(OUT / fname)


# 02 본론1: 필름 톤
def body1():
    rows = [("노출", "-5", 0.45), ("대비", "-15", 0.35), ("하이라이트", "-10", 0.4), ("따뜻함", "+12", 0.62),
            ("채도", "-10", 0.4), ("그레인", "약하게", 0.58), ("비네트", "살짝", 0.58)]
    recipe("레시피 하나: 따뜻하게 바랜 필름 톤", film(base_scene(560, 420)), rows, ACCENT, 4, "02_body1.png")


# 03 본론2: 청량 톤
def body2():
    rows = [("노출", "+10", 0.6), ("그림자", "+15", 0.65), ("대비", "+5", 0.55), ("따뜻함", "-10", 0.4),
            ("채도", "+8", 0.58), ("색조(틴트)", "+5", 0.55), ("선명도", "+10", 0.6)]
    recipe("레시피 둘: 맑고 시원한 청량 톤", fresh(base_scene(560, 420)), rows, (70, 140, 210), 5, "03_body2.png")


# 04 본론3: 모노 톤
def body3():
    rows = [("채도", "-100", 0.0), ("대비", "+20", 0.7), ("하이라이트", "-10", 0.4), ("그림자", "-10", 0.4),
            ("선명도", "+15", 0.65), ("비네트", "조금", 0.6)]
    recipe("레시피 셋: 분위기 있는 흑백 모노 톤", mono(base_scene(560, 420)), rows, (70, 70, 76), 6, "04_body3.png")


# 05 결론: 브랜드
def outro():
    img = gradient(W, H, (42, 36, 34), (22, 20, 20))
    d = ImageDraw.Draw(img)
    for y0 in (0, H - 60):
        d.rectangle([0, y0, W, y0 + 60], fill=(14, 13, 13))
        for x in range(20, W, 60):
            d.rounded_rectangle([x, y0 + 17, x + 32, y0 + 43], 4, fill=(225, 200, 165))
    # 세 가지 톤 견본 칩
    for i, c in enumerate(((214, 170, 120), (110, 170, 220), (150, 150, 150))):
        x = W // 2 - 130 + i * 90
        d.rounded_rectangle([x, 180, x + 70, 250], 14, fill=c)
    center_text(d, 300, "지담 스튜디오", font(100, True), (250, 238, 220))
    center_text(d, 450, "일상을 작품으로 남기는 사진 스튜디오", font(36), (225, 200, 165))
    center_text(d, 515, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (205, 180, 150))
    noise(img, seed=7).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

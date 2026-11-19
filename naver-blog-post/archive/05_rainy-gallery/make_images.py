"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 비 오는 날 감성 사진 갤러리)"""
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
NEON = [(255, 90, 140), (90, 200, 255), (255, 190, 80), (170, 110, 255), (90, 230, 170)]


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def noise(img, alpha=0.035, seed=1):
    rnd = random.Random(seed)
    n = Image.new("L", img.size)
    n.putdata([128 + rnd.randint(-12, 12) for _ in range(img.size[0] * img.size[1])])
    return Image.blend(img, n.convert("RGB"), alpha)


def center_text(d, y, text, f, fill, x0=0, width=W):
    w = d.textlength(text, font=f)
    d.text((x0 + (width - w) / 2, y), text, font=f, fill=fill)


def bokeh(size, n, seed, rmin=20, rmax=70, strength=0.55, area=None):
    """흐릿한 불빛 번짐 레이어"""
    rnd = random.Random(seed)
    layer = Image.new("RGB", size)
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = area or (0, 0, size[0], size[1])
    for _ in range(n):
        x, y, r = rnd.randint(x0, x1), rnd.randint(y0, y1), rnd.randint(rmin, rmax)
        c = rnd.choice(NEON)
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v * strength) for v in c))
    return layer.filter(ImageFilter.GaussianBlur(10))


def raindrops(img, n, seed, rmin=6, rmax=22):
    """창문 위 빗방울: 밝은 테두리 + 하이라이트"""
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(n):
        x, y, r = rnd.randint(0, img.width), rnd.randint(0, img.height), rnd.randint(rmin, rmax)
        d.ellipse([x - r, y - r * 1.1, x + r, y + r * 1.1], fill=(255, 255, 255, 40), outline=(255, 255, 255, 120), width=2)
        d.ellipse([x - r * 0.45, y - r * 0.7, x - r * 0.1, y - r * 0.35], fill=(255, 255, 255, 190))
        if rnd.random() < 0.1:  # 흘러내린 자국은 방울 위쪽에 가늘게
            d.line([(x, y - r), (x + rnd.randint(-3, 3), y - r - rnd.randint(30, 80))], fill=(255, 255, 255, 35), width=max(2, r // 3))
    return img


def rain_lines(img, n, seed, alpha=70):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(n):
        x, y = rnd.randint(-100, img.width), rnd.randint(-100, img.height)
        ln = rnd.randint(25, 60)
        d.line([(x, y), (x + ln * 0.25, y + ln)], fill=(220, 230, 255, alpha), width=2)
    return img


def label(img, text, x=40, y=40):
    d = ImageDraw.Draw(img, "RGBA")
    f = font(30, True)
    w = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + w + 44, y + 58], 16, fill=(20, 22, 34, 190))
    d.text((x + 22, y + 9), text, font=f, fill=(255, 255, 255))


def umbrella_person(d, cx, base, s, umbrella=(40, 44, 60), body=(25, 26, 38), clear=False):
    # 몸
    d.polygon([(cx - 24 * s, base - 150 * s), (cx + 24 * s, base - 150 * s), (cx + 20 * s, base - 40 * s), (cx - 20 * s, base - 40 * s)], fill=body)
    d.line([(cx - 8 * s, base - 40 * s), (cx - 12 * s, base)], fill=body, width=int(12 * s))
    d.line([(cx + 8 * s, base - 40 * s), (cx + 12 * s, base)], fill=body, width=int(12 * s))
    d.ellipse([cx - 18 * s, base - 192 * s, cx + 18 * s, base - 156 * s], fill=body)
    # 우산
    d.line([(cx + 4 * s, base - 120 * s), (cx + 4 * s, base - 230 * s)], fill=body, width=int(5 * s))
    if clear:
        d.pieslice([cx - 95 * s, base - 300 * s, cx + 100 * s, base - 160 * s], 180, 360, fill=(220, 235, 255, 70), outline=(240, 245, 255, 200), width=3)
    else:
        d.pieslice([cx - 95 * s, base - 300 * s, cx + 100 * s, base - 160 * s], 180, 360, fill=umbrella)


def city(w, h, horizon, seed, night=True):
    img = gradient(w, h, (30, 34, 58) if night else (150, 165, 185), (55, 52, 80) if night else (185, 190, 200))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    x = 0
    while x < w:
        bw, bh = rnd.randint(60, 140), rnd.randint(140, horizon - 40)
        col = (24, 26, 42) if night else (110, 118, 135)
        d.rectangle([x, horizon - bh, x + bw, horizon], fill=col)
        for wy in range(horizon - bh + 15, horizon - 10, 26):
            for wx in range(x + 10, x + bw - 10, 22):
                if rnd.random() < 0.45:
                    d.rectangle([wx, wy, wx + 10, wy + 12], fill=(255, 210, 130) if night else (205, 215, 225))
        x += bw + rnd.randint(4, 14)
    return img


# 01 서론: 빗방울 맺힌 창문 + 흐린 거리 불빛
def intro():
    img = gradient(W, H, (28, 32, 52), (60, 56, 84))
    img = ImageChops.add(img, bokeh((W, H), 45, 1, 25, 80, 0.6, (0, 150, W, H)))
    img = img.filter(ImageFilter.GaussianBlur(3))
    img = raindrops(img, 160, 2)
    # 창틀
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], outline=(18, 18, 26), width=40)
    d.rectangle([W // 2 - 14, 0, W // 2 + 14, H], fill=(18, 18, 26))
    label(img, "비 오는 날 감성 갤러리", 70, 70)
    noise(img, seed=3).save(OUT / "01_intro.png")


# 02 본론1: 빗방울에 초점, 바깥은 흐림
def body1():
    bg = city(W, H, 600, 5)
    bg = ImageChops.add(bg, bokeh((W, H), 35, 6, 30, 90, 0.55))
    bg = bg.filter(ImageFilter.GaussianBlur(14))
    img = raindrops(bg, 120, 7, 10, 34)
    # 초점 표시
    d = ImageDraw.Draw(img)
    fx, fy = 560, 380
    d.rectangle([fx - 60, fy - 60, fx + 60, fy + 60], outline=(255, 214, 90), width=4)
    d.line([(fx - 75, fy), (fx - 60, fy)], fill=(255, 214, 90), width=4)
    d.line([(fx + 60, fy), (fx + 75, fy)], fill=(255, 214, 90), width=4)
    label(img, "장면 하나 · 빗방울에 초점")
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([W // 2 - 260, H - 100, W // 2 + 260, H - 40], 16, fill=(20, 22, 34, 190))
    center_text(d, H - 92, "빗방울을 눌러 초점 고정 → 불빛이 동그랗게", font(28, True), (255, 255, 255))
    noise(img, seed=8).save(OUT / "02_body1.png")


# 03 본론2: 물웅덩이 반영
def body2():
    horizon = 360
    top = city(W, horizon, horizon, 9, night=False)
    img = Image.new("RGB", (W, H), (70, 70, 78))
    img.paste(top, (0, 0))
    d = ImageDraw.Draw(img)
    # 젖은 바닥
    img.paste(gradient(W, H - horizon, (90, 90, 100), (60, 60, 68)), (0, horizon))
    # 웅덩이 반영
    refl = top.transpose(Image.FLIP_TOP_BOTTOM)
    rd = ImageDraw.Draw(refl)
    umbrella_person(rd, 760, 0 + 330, 1.0, umbrella=(214, 70, 80))  # 반영 속 사람(뒤집기 전 그림)
    refl = Image.open(OUT / "_tmp.png") if False else refl
    mask = Image.new("L", (W, H - horizon), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([-200, 10, W + 200, (H - horizon) + 300], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(20))
    refl_img = ImageChops.multiply(refl.resize((W, H - horizon)), Image.new("RGB", (W, H - horizon), (175, 185, 205)))
    img.paste(refl_img, (0, horizon), mask)
    # 물결
    d = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(10)
    for _ in range(25):
        y = rnd.randint(horizon + 30, H - 20)
        x = rnd.randint(0, W)
        d.line([(x, y), (x + rnd.randint(40, 140), y)], fill=(255, 255, 255, 50), width=2)
    # 실제 사람(위쪽, 바로 선 모습)
    umbrella_person(d, 760, horizon, 1.0, umbrella=(214, 70, 80))
    label(img, "장면 둘 · 물웅덩이 반영")
    d.rounded_rectangle([W // 2 - 270, H - 100, W // 2 + 270, H - 40], 16, fill=(20, 22, 34, 190))
    center_text(d, H - 92, "렌즈를 수면 2~3cm 위까지 낮게", font(28, True), (255, 255, 255))
    noise(img, seed=11).save(OUT / "03_body2.png")


# 04 본론3: 밤 네온 + 우산
def body3():
    img = city(W, H, 520, 12)
    d = ImageDraw.Draw(img)
    # 간판 네온
    rnd = random.Random(13)
    for i in range(7):
        x, y = 60 + i * 165, rnd.randint(200, 380)
        c = NEON[i % len(NEON)]
        d.rounded_rectangle([x, y, x + 110, y + 46], 8, outline=c, width=6)
    img = ImageChops.add(img, img.filter(ImageFilter.GaussianBlur(18)))
    # 젖은 바닥 반사
    floor = img.crop((0, 200, W, 520)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, H - 520)).filter(ImageFilter.GaussianBlur(6))
    floor = ImageChops.multiply(floor, Image.new("RGB", floor.size, (150, 150, 170)))
    img.paste(floor, (0, 520))
    img = rain_lines(img, 500, 14, 80)
    d = ImageDraw.Draw(img, "RGBA")
    umbrella_person(d, 860, 720, 1.25, clear=True)
    label(img, "장면 셋 · 우산 아래 네온")
    d.rounded_rectangle([W // 2 - 300, H - 100, W // 2 + 300, H - 40], 16, fill=(20, 22, 34, 200))
    center_text(d, H - 92, "야간 모드 + 팔꿈치 고정, 인물은 작게", font(28, True), (255, 255, 255))
    noise(img, seed=15).save(OUT / "04_body3.png")


# 05 결론: 브랜드
def outro():
    img = gradient(W, H, (30, 32, 48), (20, 20, 30))
    img = ImageChops.add(img, bokeh((W, H), 30, 16, 20, 60, 0.35))
    img = img.filter(ImageFilter.GaussianBlur(4))
    img = raindrops(img, 70, 17, 5, 16)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([170, 230, W - 170, 610], 30, fill=(10, 10, 18, 170))
    # 우산 아이콘
    d.pieslice([W / 2 - 60, 150, W / 2 + 60, 270], 180, 360, fill=(240, 220, 190))
    d.line([(W / 2, 210), (W / 2, 290)], fill=(240, 220, 190), width=5)
    center_text(d, 300, "지담 스튜디오", font(100, True), (250, 240, 225))
    center_text(d, 450, "일상을 작품으로 남기는 사진 스튜디오", font(36), (200, 215, 240))
    center_text(d, 515, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (230, 205, 170))
    noise(img, seed=18).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

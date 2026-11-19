"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 보정 노하우)"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (60, 48, 44)
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


def noise(img, alpha=0.03, seed=1):
    rnd = random.Random(seed)
    n = Image.new("L", img.size)
    n.putdata([128 + rnd.randint(-12, 12) for _ in range(img.size[0] * img.size[1])])
    return Image.blend(img, n.convert("RGB"), alpha)


def center_text(d, y, text, f, fill, x0=0, width=W):
    w = d.textlength(text, font=f)
    d.text((x0 + (width - w) / 2, y), text, font=f, fill=fill)


def check(d, x, y, size, fill):
    d.line([(x, y + size * 0.5), (x + size * 0.38, y + size * 0.88), (x + size, y + size * 0.1)],
           fill=fill, width=max(3, int(size / 6)), joint="curve")


def scene(w, h, warm=True):
    """카페 창가 풍경 (보정 전후 비교에 쓰는 기본 장면)"""
    img = gradient(w, h, (250, 214, 170) if warm else (170, 205, 235), (236, 196, 160) if warm else (215, 225, 235))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.68, w, h], fill=(150, 104, 78))  # 테이블
    d.rectangle([w * 0.08, h * 0.08, w * 0.62, h * 0.6], fill=(250, 240, 225), outline=(170, 130, 100), width=8)
    d.line([(w * 0.35, h * 0.08), (w * 0.35, h * 0.6)], fill=(170, 130, 100), width=6)
    d.ellipse([w * 0.62, h * 0.52, w * 0.86, h * 0.74], fill=(245, 245, 240))  # 컵
    d.ellipse([w * 0.66, h * 0.55, w * 0.82, h * 0.66], fill=(120, 75, 50))
    d.rectangle([w * 0.18, h * 0.5, w * 0.3, h * 0.68], fill=(200, 120, 90))  # 화분
    for dx in (-0.04, 0, 0.04):
        d.ellipse([w * (0.24 + dx) - 26, h * 0.38, w * (0.24 + dx) + 26, h * 0.52], fill=(100, 140, 95))
    return img


# 01 서론: 보정 전/후 비교
def intro():
    base = scene(W, H)
    before = ImageEnhance.Brightness(ImageEnhance.Color(base).enhance(0.45)).enhance(0.72)
    before = ImageEnhance.Contrast(before).enhance(0.8).rotate(2.5, fillcolor=(80, 70, 65))
    after = ImageEnhance.Brightness(base).enhance(1.05)
    img = after.copy()
    img.paste(before.crop((0, 0, W // 2, H)), (0, 0))
    d = ImageDraw.Draw(img)
    d.line([(W // 2, 0), (W // 2, H)], fill=(255, 255, 255), width=6)
    d.ellipse([W // 2 - 34, H // 2 - 34, W // 2 + 34, H // 2 + 34], fill=(255, 255, 255))
    d.polygon([(W // 2 - 20, H // 2), (W // 2 - 6, H // 2 - 12), (W // 2 - 6, H // 2 + 12)], fill=INK)
    d.polygon([(W // 2 + 20, H // 2), (W // 2 + 6, H // 2 - 12), (W // 2 + 6, H // 2 + 12)], fill=INK)
    for x, label in ((40, "BEFORE"), (W - 230, "AFTER")):
        d.rounded_rectangle([x, 36, x + 190, 96], 14, fill=(0, 0, 0, 120) if False else (40, 34, 32))
        center_text(d, 42, label, font(36, True), (255, 255, 255), x0=x, width=190)
    d.rounded_rectangle([W // 2 - 300, H - 110, W // 2 + 300, H - 40], 18, fill=(255, 255, 255))
    center_text(d, H - 102, "스마트폰 기본 편집 3단계면 충분", font(36, True), INK)
    noise(img, seed=2).save(OUT / "01_intro.png")


# 02 본론1: 자르기·수평
def body1():
    img = gradient(W, H, (246, 240, 232), (232, 224, 214))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "1단계: 자르기와 수평부터", font(46, True), INK)
    px, py, pw, ph = 170, 140, 560, 420
    photo = scene(pw, ph).rotate(-3, fillcolor=(90, 80, 75))
    img.paste(photo, (px, py))
    d = ImageDraw.Draw(img)
    # 자르기 프레임 + 3분할 격자
    cx0, cy0, cx1, cy1 = px + 40, py + 30, px + pw - 40, py + ph - 30
    d.rectangle([cx0, cy0, cx1, cy1], outline=(255, 255, 255), width=4)
    for i in (1, 2):
        x = cx0 + (cx1 - cx0) * i / 3
        y = cy0 + (cy1 - cy0) * i / 3
        d.line([(x, cy0), (x, cy1)], fill=(255, 255, 255), width=2)
        d.line([(cx0, y), (cx1, y)], fill=(255, 255, 255), width=2)
    for (x, y) in ((cx0, cy0), (cx1, cy0), (cx0, cy1), (cx1, cy1)):
        sx = 1 if x == cx0 else -1
        sy = 1 if y == cy0 else -1
        d.line([(x, y), (x + 40 * sx, y)], fill=(255, 255, 255), width=10)
        d.line([(x, y), (x, y + 40 * sy)], fill=(255, 255, 255), width=10)
    # 수평 다이얼
    dx, dy = px + pw / 2, py + ph + 70
    d.line([(px, dy), (px + pw, dy)], fill=(190, 175, 160), width=3)
    for i in range(-10, 11):
        x = dx + i * 26
        d.line([(x, dy - (14 if i % 5 == 0 else 8)), (x, dy)], fill=(150, 130, 115), width=2)
    d.polygon([(dx - 10, dy + 10), (dx + 10, dy + 10), (dx, dy - 4)], fill=ACCENT)
    center_text(d, dy + 18, "수평 -3° 보정", font(26, True), ACCENT, x0=px, width=pw)
    # 오른쪽: 비율 버튼 + 순서
    bx = 790
    d.text((bx, 150), "추천 비율", font=font(30, True), fill=INK)
    for i, (r, use) in enumerate((("4:5", "인스타 피드"), ("3:2", "블로그"), ("4:3", "디카 감성"))):
        y = 205 + i * 78
        d.rounded_rectangle([bx, y, bx + 300, y + 60], 14, fill=(255, 255, 255), outline=(220, 205, 190), width=2)
        d.text((bx + 22, y + 9), r, font=font(32, True), fill=ACCENT)
        d.text((bx + 120, y + 14), use, font=font(26), fill=INK)
    d.text((bx, 470), "구도 → 빛 → 색", font=font(36, True), fill=INK)
    d.text((bx, 520), "순서를 지키면 실패 없음", font=font(24), fill=(120, 100, 90))
    noise(img, seed=3).save(OUT / "02_body1.png")


# 03 본론2: 하이라이트/그림자
def body2():
    img = gradient(W, H, (240, 238, 234), (226, 222, 216))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "2단계: 밝기는 하이라이트와 그림자로", font(44, True), INK)
    sliders = [("하이라이트", "-20", 0.35), ("그림자", "+15", 0.62), ("노출", "+5 ~ +10", 0.56), ("대비", "±10", 0.5)]
    for i, (name, val, pos) in enumerate(sliders):
        y = 190 + i * 100
        d.text((80, y - 24), name, font=font(32, True), fill=INK)
        x0, x1 = 290, 640
        d.rounded_rectangle([x0, y - 6, x1, y + 6], 6, fill=(205, 195, 185))
        mid = (x0 + x1) / 2
        kx = x0 + (x1 - x0) * pos
        d.rounded_rectangle([min(mid, kx), y - 6, max(mid, kx), y + 6], 6, fill=ACCENT)
        d.line([(mid, y - 14), (mid, y + 14)], fill=(150, 135, 125), width=2)
        d.ellipse([kx - 20, y - 20, kx + 20, y + 20], fill=(255, 255, 255), outline=ACCENT, width=5)
        d.text((665, y - 20), val, font=font(28, True), fill=ACCENT)
    # 히스토그램 전/후
    for j, (title, shape) in enumerate((("조절 전", (0.9, 0.3, 0.15, 0.25, 0.95)), ("조절 후", (0.35, 0.6, 0.75, 0.6, 0.4)))):
        hx, hy, hw, hh = 840, 170 + j * 260, 290, 180
        d.rounded_rectangle([hx, hy, hx + hw, hy + hh], 12, fill=(255, 255, 255))
        d.text((hx + 14, hy + 8), title, font=font(24, True), fill=INK)
        pts = []
        for k in range(60):
            t = k / 59
            seg = t * 4
            i0 = min(int(seg), 3)
            v = shape[i0] + (shape[i0 + 1] - shape[i0]) * (seg - i0)
            pts.append((hx + 15 + t * (hw - 30), hy + hh - 15 - v * (hh - 60)))
        d.polygon(pts + [(hx + hw - 15, hy + hh - 15), (hx + 15, hy + hh - 15)], fill=(235, 200, 180))
        d.line(pts, fill=ACCENT, width=3)
    center_text(d, H - 80, "밝은 곳은 살리고, 어두운 곳은 부드럽게", font(30, True), INK)
    noise(img, seed=4).save(OUT / "03_body2.png")


# 04 본론3: 무드별 레시피 카드
def body3():
    img = gradient(W, H, (244, 238, 230), (230, 222, 212))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "3단계: 무드별 색 레시피", font(46, True), INK)
    cards = [
        ("따뜻한 카페", ((250, 205, 150), (225, 160, 110)), ["색온도 +10", "채도 -5", "선명도 -5"]),
        ("청량한 바다", ((150, 205, 240), (70, 150, 200)), ["색온도 -8", "채도 +5", "선명도 +10"]),
        ("차분한 야경", ((60, 64, 100), (25, 28, 50)), ["색온도 -5", "하이라이트 -15", "채도 -10"]),
    ]
    cw, gap = 330, 45
    x0 = (W - cw * 3 - gap * 2) / 2
    for i, (name, (c1, c2), vals) in enumerate(cards):
        x = int(x0 + i * (cw + gap))
        y = 140
        d.rounded_rectangle([x, y, x + cw, y + 520], 22, fill=(255, 255, 255))
        thumb = gradient(cw - 40, 220, c1, c2)
        td = ImageDraw.Draw(thumb)
        if i == 0:
            td.ellipse([120, 120, 210, 180], fill=(250, 245, 240)); td.ellipse([135, 128, 195, 160], fill=(120, 75, 50))
        elif i == 1:
            td.rectangle([0, 140, cw, 220], fill=(40, 120, 170)); td.ellipse([200, 30, 250, 80], fill=(255, 250, 230))
        else:
            for k in range(8):
                bx = 20 + k * 36
                td.rectangle([bx, 220 - (40 + (k * 37) % 90), bx + 28, 220], fill=(35, 38, 60))
                td.ellipse([bx + 8, 120 - k % 3 * 15, bx + 18, 130 - k % 3 * 15], fill=(255, 210, 120))
        img.paste(thumb, (x + 20, y + 20))
        d = ImageDraw.Draw(img)
        center_text(d, y + 260, name, font(34, True), INK, x0=x, width=cw)
        for k, v in enumerate(vals):
            vy = y + 330 + k * 55
            check(d, x + 50, vy + 8, 24, ACCENT)
            d.text((x + 90, vy), v, font=font(28), fill=INK)
    center_text(d, H - 80, "피부가 나오면 채도는 올리지 말고 틴트만 살짝", font(28, True), (120, 95, 85))
    noise(img, seed=5).save(OUT / "04_body3.png")


# 05 결론: 브랜드 (스튜디오 스킨과 같은 톤)
def outro():
    img = gradient(W, H, (40, 36, 34), (24, 22, 22))
    d = ImageDraw.Draw(img)
    for y0 in (0, H - 60):
        d.rectangle([0, y0, W, y0 + 60], fill=(14, 13, 13))
        for x in range(24, W, 66):
            d.rounded_rectangle([x, y0 + 16, x + 36, y0 + 44], 5, fill=(225, 200, 165))
    # 슬라이더 아이콘
    for i, pos in enumerate((0.3, 0.7, 0.5)):
        y = 200 + i * 40
        d.line([(W / 2 - 90, y), (W / 2 + 90, y)], fill=(225, 200, 165), width=4)
        kx = W / 2 - 90 + 180 * pos
        d.ellipse([kx - 12, y - 12, kx + 12, y + 12], fill=(225, 200, 165))
    center_text(d, 330, "지담 스튜디오", font(100, True), (250, 238, 220))
    center_text(d, 480, "일상을 작품으로 남기는 사진 스튜디오", font(36), (225, 200, 165))
    center_text(d, 545, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (200, 175, 145))
    noise(img, seed=6).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

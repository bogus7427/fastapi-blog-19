"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 초점과 화이트밸런스)"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (44, 48, 60)
ACCENT = (232, 150, 60)
FOCUS = (255, 214, 90)
PEAK = (90, 230, 120)
BLUE = (70, 130, 200)


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


def focus_box(d, cx, cy, r, color=FOCUS, width=4):
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.line([(cx + sx * r, cy + sy * r), (cx + sx * r * 0.55, cy + sy * r)], fill=color, width=width)
            d.line([(cx + sx * r, cy + sy * r), (cx + sx * r, cy + sy * r * 0.55)], fill=color, width=width)


def phone(img, x, y, w, h, scene):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x + 8, y + 12, x + w + 8, y + h + 12], 46, fill=(180, 186, 200))
    d.rounded_rectangle([x, y, x + w, y + h], 46, fill=(30, 32, 40))
    img.paste(scene.resize((w - 36, h - 70)), (x + 18, y + 35))
    return x + 18, y + 35, w - 36, h - 70


def portrait_scene(w, h):
    s = gradient(w, h, (196, 214, 200), (150, 176, 160))
    sd = ImageDraw.Draw(s)
    rnd = random.Random(2)
    for _ in range(14):
        x, y, r = rnd.randint(0, w), rnd.randint(0, int(h * 0.6)), rnd.randint(18, 40)
        sd.ellipse([x - r, y - r, x + r, y + r], fill=rnd.choice([(120, 160, 120), (230, 220, 170)]))
    s = s.filter(ImageFilter.GaussianBlur(10))
    sd = ImageDraw.Draw(s)
    cx, cy = w / 2, h * 0.42
    sd.rounded_rectangle([cx - 150, h * 0.72, cx + 150, h + 60], 90, fill=(200, 110, 100))
    sd.ellipse([cx - 95, cy - 120, cx + 95, cy + 120], fill=(248, 214, 190))
    sd.chord([cx - 104, cy - 140, cx + 104, cy + 10], 180, 360, fill=(60, 42, 36))
    for ex in (-38, 38):
        sd.ellipse([cx + ex - 12, cy - 2, cx + ex + 12, cy + 20], fill=(50, 36, 36))
        sd.ellipse([cx + ex - 3, cy + 2, cx + ex + 3, cy + 8], fill=(255, 255, 255))
    sd.arc([cx - 34, cy + 40, cx + 34, cy + 80], 20, 160, fill=(190, 80, 80), width=5)
    return s, (cx - 38, cy + 8)


# 01 서론: 프로 모드 + 초점 + WB 눈금
def intro():
    img = gradient(W, H, (236, 238, 244), (214, 220, 232))
    scene, eye = portrait_scene(860, 400)
    sx, sy, sw, sh = phone(img, 150, 110, 900, 470, scene)
    d = ImageDraw.Draw(img, "RGBA")
    k = sw / 860
    focus_box(d, sx + eye[0] * k, sy + eye[1] * k * (sh / 400) / k, 40)
    d.rounded_rectangle([sx + 12, sy + 12, sx + 110, sy + 52], 10, fill=(0, 0, 0, 140))
    d.text((sx + 26, sy + 16), "PRO", font=font(26, True), fill=(255, 210, 120))
    # 하단 바: MF, WB
    d.rectangle([sx, sy + sh - 70, sx + sw, sy + sh], fill=(0, 0, 0, 150))
    for i, (key, val) in enumerate((("AF", "눈 고정"), ("MF", "AUTO"), ("WB", "5500K"))):
        x = sx + 40 + i * 240
        d.text((x, sy + sh - 60), key, font=font(20, True), fill=(200, 200, 210))
        d.text((x, sy + sh - 36), val, font=font(24, True), fill=(255, 210, 120))
    # 색온도 그라데이션 바
    bar = Image.new("RGB", (600, 26))
    bd = ImageDraw.Draw(bar)
    for xx in range(600):
        t = xx / 599
        c = (int(120 + 135 * t), int(170 + 50 * min(t * 2, 1) - 40 * max(t - 0.5, 0)), int(255 - 175 * t))
        bd.line([(xx, 0), (xx, 26)], fill=c)
    img.paste(bar, (300, 640))
    d = ImageDraw.Draw(img)
    d.text((300, 672), "3000K", font=font(20, True), fill=(100, 106, 120))
    d.text((840, 672), "7000K", font=font(20, True), fill=(100, 106, 120))
    center_text(d, 715, "초점 · 화이트밸런스", font(40, True), INK)
    noise(img, seed=3).save(OUT / "01_intro.png")


# 02 본론1: 탭해서 초점 + AE/AF 잠금
def body1():
    img = gradient(W, H, (240, 242, 246), (222, 228, 236))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "초점: 눌러서 맞추고, 길게 눌러 고정", font(44, True), INK)
    scene, eye = portrait_scene(560, 420)
    img.paste(scene, (90, 140))
    d = ImageDraw.Draw(img, "RGBA")
    ex, ey = 90 + eye[0], 140 + eye[1]
    focus_box(d, ex, ey, 46)
    # 손가락
    d.ellipse([ex + 20, ey + 30, ex + 90, ey + 120], fill=(240, 200, 170, 230))
    d.rounded_rectangle([90 + 20, 160, 90 + 230, 204], 12, fill=(255, 214, 90))
    d.text((90 + 36, 166), "AE/AF 잠금", font=font(24, True), fill=INK)
    # 오른쪽 단계
    bx = 720
    steps = [("1", "주인공을 한 번 탭", "그곳에 초점"), ("2", "인물은 '눈'을 탭", "눈이 선명하면 전체가 또렷"), ("3", "길게 눌러 잠금", "구도를 바꿔도 초점 유지")]
    for i, (n, t, s) in enumerate(steps):
        y = 150 + i * 140
        d.rounded_rectangle([bx, y, bx + 400, y + 112], 18, fill=(255, 255, 255))
        d.ellipse([bx + 22, y + 30, bx + 74, y + 82], fill=ACCENT)
        center_text(d, y + 36, n, font(30, True), (255, 255, 255), x0=bx + 22, width=52)
        d.text((bx + 96, y + 22), t, font=font(28, True), fill=INK)
        d.text((bx + 96, y + 64), s, font=font(22), fill=(110, 116, 130))
    noise(img, seed=4).save(OUT / "02_body1.png")


# 03 본론2: 수동 초점 + 포커스 피킹
def flower(d, cx, cy, r, petal=(245, 150, 170), center=(250, 210, 90)):
    for k in range(8):
        a = math.radians(45 * k)
        d.ellipse([cx + r * 0.7 * math.cos(a) - r * 0.5, cy + r * 0.7 * math.sin(a) - r * 0.5,
                   cx + r * 0.7 * math.cos(a) + r * 0.5, cy + r * 0.7 * math.sin(a) + r * 0.5], fill=petal)
    d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=center)


def body2():
    img = gradient(W, H, (240, 242, 246), (222, 228, 236))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "수동 초점: 아주 가까운 사물과 어두운 곳", font(42, True), INK)
    pw, ph = 470, 360
    for i, (title, sub, sharp) in enumerate((("AF가 헤맬 때", "초점이 배경에 가 버림", False), ("MF + 포커스 피킹", "초록 윤곽이 진할 때 촬영", True))):
        x = 90 + i * (pw + 80)
        pic = gradient(pw, ph, (176, 200, 170), (130, 160, 130))
        pd = ImageDraw.Draw(pic)
        for k in range(6):  # 배경 잎
            pd.ellipse([40 + k * 70, 30 + (k % 2) * 40, 100 + k * 70, 90 + (k % 2) * 40], fill=(100, 140, 100))
        flower(pd, pw / 2, ph * 0.58, 110)
        if sharp:
            bg = pic.crop((0, 0, pw, ph)).filter(ImageFilter.GaussianBlur(8))
            fg = Image.new("L", (pw, ph), 0)
            ImageDraw.Draw(fg).ellipse([pw / 2 - 170, ph * 0.58 - 170, pw / 2 + 170, ph * 0.58 + 170], fill=255)
            pic = Image.composite(pic, bg, fg.filter(ImageFilter.GaussianBlur(10)))
            pd = ImageDraw.Draw(pic)
            # 포커스 피킹 윤곽
            for k in range(8):
                a = math.radians(45 * k)
                cx, cy = pw / 2 + 77 * math.cos(a), ph * 0.58 + 77 * math.sin(a)
                pd.arc([cx - 55, cy - 55, cx + 55, cy + 55], 0, 360, fill=PEAK, width=2)
        else:
            pic = pic.filter(ImageFilter.GaussianBlur(9))
            pd = ImageDraw.Draw(pic)
            for k in range(6):
                pd.ellipse([40 + k * 70, 30 + (k % 2) * 40, 100 + k * 70, 90 + (k % 2) * 40], fill=(100, 140, 100))
            focus_box(pd, 140, 70, 36, (255, 120, 100))
        d.rounded_rectangle([x - 10, 120, x + pw + 10, 120 + ph + 150], 20, fill=(255, 255, 255))
        img.paste(pic, (x, 130))
        d = ImageDraw.Draw(img)
        center_text(d, 130 + ph + 20, title, font(32, True), INK, x0=x, width=pw)
        center_text(d, 130 + ph + 68, sub, font(24), (150, 120, 120) if not sharp else (60, 160, 90), x0=x, width=pw)
    # MF 슬라이더
    y = 700
    d.text((150, y - 18), "MF", font=font(28, True), fill=INK)
    d.rounded_rectangle([230, y - 6, 1000, y + 6], 6, fill=(200, 205, 215))
    d.ellipse([360 - 20, y - 20, 360 + 20, y + 20], fill=(255, 255, 255), outline=ACCENT, width=5)
    d.text((230, y + 22), "가까이", font=font(20), fill=(110, 116, 130))
    d.text((940, y + 22), "멀리", font=font(20), fill=(110, 116, 130))
    noise(img, seed=5).save(OUT / "03_body2.png")


# 04 본론3: 화이트밸런스 비교
def cup_scene(w, h, tint):
    s = gradient(w, h, (236, 232, 226), (210, 204, 196))
    sd = ImageDraw.Draw(s)
    sd.rectangle([0, h * 0.7, w, h], fill=(190, 180, 170))
    cx, base = w * 0.55, h * 0.8
    sd.ellipse([cx - 110, base - 20, cx + 110, base + 20], fill=(250, 250, 250))
    sd.rounded_rectangle([cx - 80, base - 170, cx + 80, base], 26, fill=(255, 255, 255))
    sd.arc([cx + 60, base - 140, cx + 130, base - 60], -90, 90, fill=(255, 255, 255), width=16)
    sd.rectangle([w * 0.04, h * 0.1, w * 0.18, h * 0.3], fill=(255, 255, 255))  # 흰 종이 (컵과 떨어지게)
    overlay = Image.new("RGB", (w, h), tint)
    return Image.blend(s, overlay, 0.32 if tint != (255, 255, 255) else 0)


def body3():
    img = gradient(W, H, (240, 242, 246), (222, 228, 236))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "화이트밸런스: 흰색이 흰색으로 보일 때까지", font(42, True), INK)
    cw, ch = 330, 300
    cases = [("AUTO · 백열등 아래", "누렇게", (255, 170, 60)), ("AUTO · 그늘·형광등", "푸르스름하게", (90, 150, 255)), ("WB 맞춤", "흰 컵이 하얗게", (255, 255, 255))]
    x0 = (W - cw * 3 - 40 * 2) / 2
    for i, (t, s, tint) in enumerate(cases):
        x = int(x0 + i * (cw + 40))
        d.rounded_rectangle([x - 10, 120, x + cw + 10, 120 + ch + 130], 20, fill=(255, 255, 255))
        img.paste(cup_scene(cw, ch, tint), (x, 130))
        d = ImageDraw.Draw(img)
        center_text(d, 130 + ch + 18, t, font(26, True), INK, x0=x, width=cw)
        center_text(d, 130 + ch + 60, s, font(22), ACCENT if i == 2 else (120, 126, 140), x0=x, width=cw)
    # 색온도 표
    y = 600
    rows = [("백열등·노란 조명", "3000K"), ("형광등", "4000K"), ("맑은 낮", "5500K"), ("흐린 날·그늘", "6500K")]
    bx = (W - 4 * 250) / 2
    for i, (name, k) in enumerate(rows):
        x = int(bx + i * 250)
        t = i / 3
        c = (int(250 - 120 * t), int(190 + 20 * t), int(110 + 140 * t))
        d.rounded_rectangle([x + 10, y, x + 240, y + 110], 16, fill=c)
        center_text(d, y + 16, k, font(34, True), (255, 255, 255), x0=x + 10, width=230)
        center_text(d, y + 66, name, font(22, True), (255, 255, 255), x0=x + 10, width=230)
    noise(img, seed=6).save(OUT / "04_body3.png")


# 05 결론: 브랜드
def outro():
    img = gradient(W, H, (34, 36, 46), (20, 21, 28))
    d = ImageDraw.Draw(img)
    focus_box(d, W // 2, 220, 80, (240, 200, 140), 8)
    d.ellipse([W // 2 - 10, 210, W // 2 + 10, 230], fill=(240, 200, 140))
    center_text(d, 340, "지담 스튜디오", font(100, True), (250, 240, 225))
    center_text(d, 490, "일상을 작품으로 남기는 사진 스튜디오", font(36), (200, 210, 230))
    center_text(d, 555, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (240, 200, 140))
    noise(img, seed=7).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

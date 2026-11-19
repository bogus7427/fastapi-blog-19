"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 노출의 3요소)"""
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


def noise(img, amount=12, alpha=0.03, seed=1):
    rnd = random.Random(seed)
    n = Image.new("L", img.size)
    n.putdata([128 + rnd.randint(-amount, amount) for _ in range(img.size[0] * img.size[1])])
    return Image.blend(img, n.convert("RGB"), alpha)


def center_text(d, y, text, f, fill, x0=0, width=W):
    w = d.textlength(text, font=f)
    d.text((x0 + (width - w) / 2, y), text, font=f, fill=fill)


def card(img, x, y, w, h, pic, title, sub, sub_color=ACCENT):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + w, y + h], 20, fill=(255, 255, 255))
    img.paste(pic, (x + 18, y + 18))
    d = ImageDraw.Draw(img)
    center_text(d, y + pic.height + 34, title, font(32, True), INK, x0=x, width=w)
    center_text(d, y + pic.height + 82, sub, font(24), sub_color, x0=x, width=w)


def aperture_icon(d, cx, cy, r, opening, color, bg):
    """조리개 날개 모양: opening 0~1 (클수록 많이 열림)"""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    hole = r * (0.25 + 0.6 * opening)
    pts = []
    import math
    for k in range(6):
        a = math.radians(60 * k + 15)
        pts.append((cx + hole * math.cos(a), cy + hole * math.sin(a)))
    d.polygon(pts, fill=bg)


# 01 서론: 프로 모드 화면
def intro():
    img = gradient(W, H, (236, 238, 244), (214, 220, 232))
    d = ImageDraw.Draw(img)
    # 가로로 든 스마트폰
    px, py, pw, ph = 150, 130, 900, 470
    d.rounded_rectangle([px + 10, py + 14, px + pw + 10, py + ph + 14], 50, fill=(180, 186, 200))
    d.rounded_rectangle([px, py, px + pw, py + ph], 50, fill=(30, 32, 40))
    sx, sy, sw, sh = px + 40, py + 30, pw - 170, ph - 60
    scene = gradient(sw, sh, (150, 190, 230), (230, 215, 190))
    sd = ImageDraw.Draw(scene)
    sd.ellipse([sw * 0.45, sh * 0.25, sw * 0.65, sh * 0.62], fill=(240, 120, 110))
    sd.rectangle([sw * 0.54, sh * 0.6, sw * 0.56, sh], fill=(90, 120, 80))
    sd.rectangle([0, sh * 0.82, sw, sh], fill=(120, 150, 100))
    img.paste(scene, (sx, sy))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([sx + 12, sy + 12, sx + 110, sy + 52], 10, fill=(0, 0, 0, 140))
    d.text((sx + 26, sy + 16), "PRO", font=font(26, True), fill=(255, 210, 120))
    # 하단 값 바
    d.rectangle([sx, sy + sh - 70, sx + sw, sy + sh], fill=(0, 0, 0, 150))
    for i, (k, v) in enumerate((("S", "1/250"), ("ISO", "100"), ("F", "1.8"), ("WB", "AUTO"))):
        x = sx + 40 + i * 170
        d.text((x, sy + sh - 60), k, font=font(20, True), fill=(200, 200, 210))
        d.text((x, sy + sh - 36), v, font=font(26, True), fill=(255, 210, 120) if i < 3 else (255, 255, 255))
    # 셔터 버튼
    bx, by = px + pw - 65, py + ph / 2
    d.ellipse([bx - 38, by - 38, bx + 38, by + 38], fill=(255, 255, 255))
    d.ellipse([bx - 30, by - 30, bx + 30, by + 30], outline=(30, 32, 40), width=3)
    center_text(d, 640, "셔터 속도 · ISO · 조리개", font(42, True), INK)
    center_text(d, 705, "스마트폰 프로 모드로 배우는 노출의 3요소", font(28), (100, 106, 120))
    noise(img, seed=2).save(OUT / "01_intro.png")


def faucet_scene(w, h, fast):
    pic = gradient(w, h, (220, 232, 245), (190, 205, 225))
    d = ImageDraw.Draw(pic)
    d.rounded_rectangle([w * 0.2, 20, w * 0.62, 60], 12, fill=(150, 156, 170))
    d.rectangle([w * 0.52, 55, w * 0.6, 95], fill=(150, 156, 170))
    cx = w * 0.56
    if fast:
        rnd = random.Random(3)
        for k in range(9):
            y = 110 + k * 28
            r = rnd.randint(6, 10)
            d.ellipse([cx - r + rnd.randint(-4, 4), y - r, cx + r, y + r * 1.4], fill=(80, 150, 220))
    else:
        stream = Image.new("RGBA", (w, h))
        sd = ImageDraw.Draw(stream)
        sd.rectangle([cx - 10, 95, cx + 10, h - 40], fill=(110, 170, 230, 220))
        stream = stream.filter(ImageFilter.GaussianBlur(5))
        pic.paste(stream, (0, 0), stream)
        d = ImageDraw.Draw(pic)
    d.ellipse([cx - 80, h - 60, cx + 80, h - 20], fill=(170, 190, 215))
    return pic


# 02 본론1: 셔터 속도
def body1():
    img = gradient(W, H, (240, 242, 246), (222, 228, 236))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "셔터 속도: 움직임을 멈추거나 흐르게", font(44, True), INK)
    pw, ph = 470, 360
    card(img, 90, 120, pw + 36, ph + 150, faucet_scene(pw, ph, True), "1/1000초 · 빠르게", "물방울이 멈춘 듯 선명")
    card(img, 640, 120, pw + 36, ph + 150, faucet_scene(pw, ph, False), "1/4초 · 느리게", "물줄기가 실크처럼 부드럽게", BLUE)
    d = ImageDraw.Draw(img)
    center_text(d, H - 70, "1/30초보다 느리면 휴대폰을 고정하세요", font(28, True), (100, 106, 120))
    noise(img, seed=4).save(OUT / "02_body1.png")


def room_scene(w, h, grain_amount):
    pic = gradient(w, h, (120, 110, 130), (70, 64, 80))
    d = ImageDraw.Draw(pic)
    d.rectangle([w * 0.1, h * 0.15, w * 0.45, h * 0.6], fill=(220, 190, 140))  # 창
    d.ellipse([w * 0.58, h * 0.35, w * 0.86, h * 0.75], fill=(200, 110, 90))  # 화분/소품
    d.rectangle([0, h * 0.78, w, h], fill=(90, 70, 60))
    if grain_amount:
        rnd = random.Random(9)
        n = Image.new("RGB", (w, h))
        n.putdata([tuple(max(0, min(255, 128 + rnd.randint(-grain_amount, grain_amount) + c)) for c in
                         (rnd.randint(-20, 20), rnd.randint(-20, 20), rnd.randint(-20, 20))) for _ in range(w * h)])
        pic = Image.blend(pic, n, 0.28)
    return pic


# 03 본론2: ISO
def body2():
    img = gradient(W, H, (240, 242, 246), (222, 228, 236))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "ISO: 밝기를 올리는 대신 노이즈가 늘어요", font(42, True), INK)
    pw, ph = 470, 330
    card(img, 90, 120, pw + 36, ph + 150, room_scene(pw, ph, 0), "ISO 100", "깨끗하지만 어두운 곳에선 부족", BLUE)
    card(img, 640, 120, pw + 36, ph + 150, room_scene(pw, ph, 70), "ISO 3200", "밝지만 자글자글한 노이즈")
    d = ImageDraw.Draw(img)
    # 권장 범위 바
    y = 680
    stops = [("낮 100~200", (120, 190, 120)), ("실내 400~800", (230, 190, 90)), ("밤 ~1600", (230, 130, 90))]
    x = 150
    for text, c in stops:
        d.rounded_rectangle([x, y, x + 290, y + 56], 14, fill=c)
        center_text(d, y + 10, text, font(26, True), (255, 255, 255), x0=x, width=290)
        x += 310
    noise(img, seed=5).save(OUT / "03_body2.png")


def portrait_scene(w, h, blur):
    bg = gradient(w, h, (170, 200, 160), (110, 150, 120))
    d = ImageDraw.Draw(bg)
    rnd = random.Random(11)
    for _ in range(18):  # 배경 나무/빛
        x, y, r = rnd.randint(0, w), rnd.randint(0, int(h * 0.7)), rnd.randint(18, 45)
        d.ellipse([x - r, y - r, x + r, y + r], fill=rnd.choice([(90, 130, 90), (230, 220, 160), (140, 170, 110)]))
    if blur:
        bg = bg.filter(ImageFilter.GaussianBlur(14))
    d = ImageDraw.Draw(bg)
    cx = w * 0.5
    d.line([(cx, h * 0.45), (cx, h)], fill=(70, 120, 70), width=8)
    for k in range(8):  # 꽃잎
        import math
        a = math.radians(45 * k)
        d.ellipse([cx + 40 * math.cos(a) - 26, h * 0.38 + 40 * math.sin(a) - 26, cx + 40 * math.cos(a) + 26, h * 0.38 + 40 * math.sin(a) + 26], fill=(245, 140, 160))
    d.ellipse([cx - 22, h * 0.38 - 22, cx + 22, h * 0.38 + 22], fill=(250, 210, 90))
    return bg


# 04 본론3: 조리개
def body3():
    img = gradient(W, H, (240, 242, 246), (222, 228, 236))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "조리개: 숫자가 작을수록 배경이 흐려져요", font(42, True), INK)
    pw, ph = 470, 330
    card(img, 90, 120, pw + 36, ph + 150, portrait_scene(pw, ph, True), "F1.4 · 활짝 열기", "얕은 심도, 배경이 부드럽게")
    card(img, 640, 120, pw + 36, ph + 150, portrait_scene(pw, ph, False), "F8 · 조이기", "깊은 심도, 배경까지 선명", BLUE)
    d = ImageDraw.Draw(img)
    aperture_icon(d, 200, 705, 36, 1.0, INK, (232, 236, 242))
    aperture_icon(d, 1000, 705, 36, 0.15, INK, (232, 236, 242))
    center_text(d, 685, "스마트폰은 '인물 모드'의 F값으로 연습", font(28, True), (100, 106, 120))
    noise(img, seed=6).save(OUT / "04_body3.png")


# 05 결론: 브랜드 (노출 삼각형)
def outro():
    img = gradient(W, H, (34, 36, 46), (20, 21, 28))
    d = ImageDraw.Draw(img)
    cx, top, base = W / 2, 110, 300
    d.polygon([(cx, top), (cx - 110, base), (cx + 110, base)], outline=(240, 200, 140), width=5)
    for (x, y, t) in ((cx, top - 34, "셔터"), (cx - 170, base - 10, "ISO"), (cx + 125, base - 10, "조리개")):
        d.text((x - (20 if t == "셔터" else 0), y), t, font=font(24, True), fill=(240, 200, 140))
    center_text(d, 340, "지담 스튜디오", font(100, True), (250, 240, 225))
    center_text(d, 490, "일상을 작품으로 남기는 사진 스튜디오", font(36), (200, 210, 230))
    center_text(d, 555, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (240, 200, 140))
    noise(img, seed=7).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

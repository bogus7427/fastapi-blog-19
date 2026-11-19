"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 한강 노을 스냅 촬영 후기)"""
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (60, 46, 44)
ACCENT = (226, 112, 70)
SIL = (38, 28, 40)


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def gradient(w, h, stops):
    """여러 색 세로 그라데이션: stops = [(위치0~1, (r,g,b)), ...]"""
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / max(p1 - p0, 1e-6)
                d.line([(0, y), (w, y)], fill=tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3)))
                break
    return img


def noise(img, alpha=0.035, seed=1):
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


SUNSET = [(0, (64, 60, 120)), (0.35, (236, 120, 110)), (0.6, (252, 182, 110)), (0.62, (120, 70, 80)), (1, (60, 40, 60))]


def sunset_scene(w, h, sun=True, people=True, skyline=True):
    img = gradient(w, h, SUNSET)
    d = ImageDraw.Draw(img)
    horizon = int(h * 0.61)
    if sun:
        glow = Image.new("RGB", (w, h))
        gd = ImageDraw.Draw(glow)
        for r in range(int(w * 0.25), 0, -6):
            t = 1 - r / (w * 0.25)
            gd.ellipse([w * 0.62 - r, horizon - r, w * 0.62 + r, horizon + r], fill=tuple(int(c * t * 0.5) for c in (255, 200, 120)))
        img = ImageChops.add(img, glow.filter(ImageFilter.GaussianBlur(25)))
        d = ImageDraw.Draw(img)
        d.pieslice([w * 0.62 - 50, horizon - 50, w * 0.62 + 50, horizon + 50], 180, 360, fill=(255, 226, 150))
    if skyline:  # 강 건너 건물
        rnd = random.Random(4)
        x = 0
        while x < w:
            bw, bh = rnd.randint(30, 70), rnd.randint(20, 90)
            d.rectangle([x, horizon - bh, x + bw, horizon], fill=(90, 56, 72))
            x += bw + rnd.randint(2, 10)
    # 강물 반영
    for i in range(14):
        y = horizon + 12 + i * 14
        ww = 120 - i * 6
        d.line([(w * 0.62 - ww, y), (w * 0.62 + ww, y)], fill=(250, 190, 120), width=3)
    if people:
        draw_person(d, w * 0.3, h * 0.92, 1.0, arms_up=True)
        draw_person(d, w * 0.4, h * 0.92, 0.92)
    return img


def draw_person(d, cx, base, s, arms_up=False, color=SIL):
    d.ellipse([cx - 22 * s, base - 260 * s, cx + 22 * s, base - 214 * s], fill=color)
    d.polygon([(cx - 30 * s, base - 210 * s), (cx + 30 * s, base - 210 * s), (cx + 22 * s, base - 100 * s), (cx - 22 * s, base - 100 * s)], fill=color)
    d.line([(cx - 10 * s, base - 100 * s), (cx - 18 * s, base)], fill=color, width=int(16 * s))
    d.line([(cx + 10 * s, base - 100 * s), (cx + 18 * s, base)], fill=color, width=int(16 * s))
    if arms_up:
        d.line([(cx - 26 * s, base - 200 * s), (cx - 70 * s, base - 290 * s)], fill=color, width=int(13 * s))
        d.line([(cx + 26 * s, base - 200 * s), (cx + 70 * s, base - 290 * s)], fill=color, width=int(13 * s))
    else:
        d.line([(cx - 28 * s, base - 200 * s), (cx - 40 * s, base - 120 * s)], fill=color, width=int(13 * s))
        d.line([(cx + 28 * s, base - 200 * s), (cx + 40 * s, base - 120 * s)], fill=color, width=int(13 * s))


# 01 서론: 한강 노을 실루엣
def intro():
    img = sunset_scene(W, H)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 40, 420, 108], 18, fill=(255, 255, 255))
    d.text((64, 50), "한강 노을 스냅 촬영기", font=font(34, True), fill=INK)
    d.text((W - 300, H - 70), "shot on smartphone", font=font(28, True), fill=(255, 235, 210))
    noise(img, seed=2).save(OUT / "01_intro.png")


# 02 본론1: 시간표 + 위치
def body1():
    img = gradient(W, H, [(0, (246, 238, 228)), (1, (232, 222, 210))])
    d = ImageDraw.Draw(img)
    center_text(d, 36, "준비: 시간과 자리만 잘 골라도 반은 성공", font(42, True), INK)
    # 타임라인
    x0, x1, y = 90, 640, 330
    d.line([(x0, y), (x1, y)], fill=(200, 180, 165), width=6)
    marks = [(0.0, "-40분", "도착·자리 잡기"), (0.4, "-30분", "골든아워 시작"), (0.8, "일몰", "실루엣 컷"), (1.0, "+15분", "블루아워")]
    for p, t, desc in marks:
        x = x0 + (x1 - x0) * p
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=ACCENT if p in (0.4, 0.8) else (190, 170, 155))
        center_text(d, y - 70, t, font(28, True), INK, x0=x - 80, width=160)
        center_text(d, y + 30, desc, font(20), (110, 90, 80), x0=x - 80, width=160)
    d.rounded_rectangle([x0 + (x1 - x0) * 0.4, y - 8, x0 + (x1 - x0) * 1.0, y + 8], 8, fill=ACCENT)
    # 준비물
    d.text((x0, 450), "준비물", font=font(30, True), fill=INK)
    for i, item in enumerate(("충전한 스마트폰", "보조배터리", "렌즈 닦을 천")):
        yy = 505 + i * 50
        check(d, x0, yy + 6, 26, ACCENT)
        d.text((x0 + 42, yy), item, font=font(26), fill=INK)
    # 지도
    mx, my, mw, mh = 720, 140, 400, 520
    d.rounded_rectangle([mx, my, mx + mw, my + mh], 20, fill=(255, 255, 255))
    d.polygon([(mx + 20, my + 250), (mx + mw - 20, my + 190), (mx + mw - 20, my + 300), (mx + 20, my + 360)], fill=(150, 195, 225))
    d.text((mx + mw - 110, my + 225), "한강", font=font(28, True), fill=(60, 110, 150))
    sx, sy = mx + 70, my + 140
    d.ellipse([sx - 30, sy - 30, sx + 30, sy + 30], fill=(252, 190, 100))
    d.text((sx - 20, sy - 70), "서쪽", font=font(22, True), fill=INK)
    px, py = mx + mw - 110, my + 420
    d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=ACCENT)
    d.text((px - 60, py + 24), "촬영 위치", font=font(22, True), fill=INK)
    d.line([(px, py), (sx + 30, sy + 10)], fill=ACCENT, width=3)
    center_text(d, my + mh - 50, "서쪽이 트인 자리", font(24, True), ACCENT, x0=mx, width=mw)
    noise(img, seed=3).save(OUT / "02_body1.png")


# 03 본론2: 역광 실루엣 vs 반사광
def body2():
    img = gradient(W, H, [(0, (244, 236, 228)), (1, (230, 220, 210))])
    d = ImageDraw.Draw(img)
    center_text(d, 36, "현장: 두 가지 장면만 노렸어요", font(44, True), INK)
    pw, ph = 500, 420
    left = sunset_scene(pw, ph, people=False)
    ld = ImageDraw.Draw(left)
    draw_person(ld, pw * 0.42, ph * 0.98, 1.25, arms_up=True)
    right = gradient(pw, ph, [(0, (250, 200, 150)), (1, (230, 160, 120))])
    rd = ImageDraw.Draw(right)
    cx = pw * 0.5
    rd.ellipse([cx - 120, ph - 120, cx + 120, ph + 160], fill=(120, 90, 110))
    rd.ellipse([cx - 70, ph * 0.25, cx + 70, ph * 0.25 + 170], fill=(250, 200, 160))
    rd.chord([cx - 76, ph * 0.22, cx + 76, ph * 0.22 + 120], 180, 360, fill=(70, 45, 40))
    rd.ellipse([cx - 70, ph * 0.25, cx, ph * 0.25 + 170], fill=(255, 215, 170))  # 빛 받는 쪽
    for ex in (-26, 26):
        rd.ellipse([cx + ex - 6, ph * 0.25 + 70, cx + ex + 6, ph * 0.25 + 82], fill=(60, 40, 40))
    rd.arc([cx - 24, ph * 0.25 + 95, cx + 24, ph * 0.25 + 125], 20, 160, fill=(190, 90, 80), width=4)
    for i, (pic, title, tip) in enumerate(((left, "역광 실루엣", "하늘을 눌러 노출 고정"), (right, "얼굴에 닿는 노을빛", "해를 비스듬히 바라보기"))):
        x = 70 + i * (pw + 60)
        d.rectangle([x - 10, 130, x + pw + 10, 130 + ph + 10], fill=(255, 255, 255))
        img.paste(pic, (x, 135))
        d = ImageDraw.Draw(img)
        center_text(d, 590, title, font(32, True), INK, x0=x, width=pw)
        center_text(d, 640, tip, font(24), ACCENT, x0=x, width=pw)
    center_text(d, H - 70, "연속 촬영으로 한 장면에 10장 이상", font(28, True), (110, 90, 80))
    noise(img, seed=4).save(OUT / "03_body2.png")


# 04 본론3: 고르기 기준 + 보정값
def body3():
    img = gradient(W, H, [(0, (246, 238, 230)), (1, (232, 222, 212))])
    d = ImageDraw.Draw(img)
    center_text(d, 36, "결과: 고르는 기준과 최소한의 보정", font(44, True), INK)
    # 썸네일 그리드 (선택/탈락)
    picks = [1, 0, 0, 1, 0, 1, 0, 0, 1]
    for i, ok in enumerate(picks):
        x = 70 + (i % 3) * 170
        y = 140 + (i // 3) * 130
        th = sunset_scene(150, 110, people=False, skyline=False)
        if i % 2 == 0:  # 작은 실루엣
            draw_person(ImageDraw.Draw(th), 50 + (i % 3) * 15, 108, 0.32, arms_up=(i % 4 == 0))
        if not ok:
            th = th.rotate(5 if i % 2 else -4, fillcolor=(80, 60, 70))
        img.paste(th, (x, y))
        d = ImageDraw.Draw(img)
        if ok:
            d.rectangle([x - 5, y - 5, x + 155, y + 115], outline=ACCENT, width=5)
            d.ellipse([x + 118, y + 6, x + 146, y + 34], fill=ACCENT)
            check(d, x + 124, y + 12, 16, (255, 255, 255))
    center_text(d, 545, "200장 → 12장", font(34, True), ACCENT, x0=70, width=490)
    # 기준 체크리스트
    bx = 640
    d.text((bx, 140), "고르는 기준", font=font(30, True), fill=INK)
    for i, c in enumerate(("수평이 맞는지", "실루엣이 겹치지 않는지", "하늘 색 층이 살아 있는지")):
        yy = 195 + i * 50
        check(d, bx, yy + 6, 26, ACCENT)
        d.text((bx + 42, yy), c, font=font(26), fill=INK)
    d.text((bx, 380), "보정은 최소한으로", font=font(30, True), fill=INK)
    for i, (name, val, pos) in enumerate((("하이라이트", "-15", 0.38), ("색온도", "+5", 0.56), ("채도", "-5", 0.45))):
        yy = 450 + i * 70
        d.text((bx, yy - 18), name, font=font(24, True), fill=INK)
        x0, x1 = bx + 150, bx + 400
        d.rounded_rectangle([x0, yy - 5, x1, yy + 5], 5, fill=(210, 195, 185))
        kx = x0 + (x1 - x0) * pos
        d.ellipse([kx - 15, yy - 15, kx + 15, yy + 15], fill=(255, 255, 255), outline=ACCENT, width=4)
        d.text((x1 + 18, yy - 16), val, font=font(24, True), fill=ACCENT)
    noise(img, seed=5).save(OUT / "04_body3.png")


# 05 결론: 브랜드 (스튜디오 톤 + 노을 띠)
def outro():
    img = gradient(W, H, [(0, (40, 34, 36)), (1, (22, 20, 22))])
    d = ImageDraw.Draw(img)
    band = gradient(W, 70, [(0, (236, 120, 110)), (1, (252, 182, 110))])
    img.paste(band, (0, 0))
    img.paste(band.transpose(Image.FLIP_TOP_BOTTOM), (0, H - 70))
    d = ImageDraw.Draw(img)
    d.pieslice([W / 2 - 70, 170, W / 2 + 70, 310], 180, 360, fill=(252, 190, 110))
    for i in range(4):
        d.line([(W / 2 - 90 + i * 12, 250 + i * 14), (W / 2 + 90 - i * 12, 250 + i * 14)], fill=(252, 190, 110), width=4)
    center_text(d, 330, "지담 스튜디오", font(100, True), (250, 238, 220))
    center_text(d, 480, "일상을 작품으로 남기는 사진 스튜디오", font(36), (240, 190, 140))
    center_text(d, 545, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (215, 175, 140))
    noise(img, seed=6).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

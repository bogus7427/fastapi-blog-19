"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 늦가을·초겨울 계절 장면)"""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (70, 50, 38)
GINKGO = [(240, 196, 60), (232, 180, 48), (248, 210, 90)]
MAPLE = [(210, 80, 50), (190, 60, 40), (226, 110, 60)]
BROWN = [(170, 110, 60), (150, 96, 56)]


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


def label(d, x, y, text, size=28, bg=(255, 255, 255), fg=INK):
    f = font(size, True)
    w = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + w + 40, y + size + 26], 16, fill=bg)
    d.text((x + 20, y + 10), text, font=f, fill=fg)


def ginkgo_leaf(d, x, y, r, angle, c):
    a = math.radians(angle)
    pts = [(x, y)]
    for k in range(-50, 51, 10):
        t = math.radians(k) + a
        pts.append((x + r * math.cos(t - math.pi / 2), y + r * math.sin(t - math.pi / 2)))
    d.polygon(pts, fill=c)
    d.line([(x, y), (x - r * 0.4 * math.cos(a - math.pi / 2), y - r * 0.4 * math.sin(a - math.pi / 2))], fill=(160, 120, 40), width=2)


def maple_leaf(d, x, y, r, angle, c):
    """단풍잎: 아래쪽이 잎자루, 위로 다섯 갈래 (가운데 갈래가 가장 김)"""
    # (각도 오프셋, 길이 비율) - 0도가 위쪽
    lobes = [(-110, 0.55), (-70, 0.85), (-25, 0.7), (0, 1.0), (25, 0.7), (70, 0.85), (110, 0.55)]
    pts = []
    for i, (off, ln) in enumerate(lobes):
        t = math.radians(angle + off - 90)
        pts.append((x + r * ln * math.cos(t), y + r * ln * math.sin(t)))
        if i < len(lobes) - 1:
            mid = math.radians(angle + (off + lobes[i + 1][0]) / 2 - 90)
            pts.append((x + r * 0.32 * math.cos(mid), y + r * 0.32 * math.sin(mid)))
    t = math.radians(angle + 90)
    pts.append((x + r * 0.2 * math.cos(t), y + r * 0.2 * math.sin(t)))
    d.polygon(pts, fill=c)
    d.line([(x, y), (x + r * 0.7 * math.cos(t), y + r * 0.7 * math.sin(t))], fill=c, width=max(2, int(r * 0.08)))


def leaf_carpet(img, n, seed, area=None):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = area or (0, 0, img.width, img.height)
    for _ in range(n):
        x, y = rnd.randint(x0, x1), rnd.randint(y0, y1)
        r = rnd.randint(18, 34)
        if rnd.random() < 0.75:
            ginkgo_leaf(d, x, y, r, rnd.randint(0, 360), rnd.choice(GINKGO))
        elif rnd.random() < 0.5:
            maple_leaf(d, x, y, r, rnd.randint(0, 360), rnd.choice(BROWN))
        else:
            ginkgo_leaf(d, x, y, r, rnd.randint(0, 360), rnd.choice(BROWN))
    return img


def bare_tree(d, x, base, h, color=(90, 70, 60), leaves=0, seed=1):
    d.line([(x, base), (x, base - h)], fill=color, width=14)
    rnd = random.Random(seed)
    for k in range(6):
        y = base - h * (0.45 + k * 0.09)
        side = 1 if k % 2 else -1
        ln = h * (0.32 - k * 0.03)
        d.line([(x, y), (x + side * ln, y - ln * 0.6)], fill=color, width=6)
        d.line([(x + side * ln * 0.6, y - ln * 0.36), (x + side * ln * 0.75, y - ln * 0.9)], fill=color, width=3)
        for _ in range(leaves):
            lx = x + side * ln * rnd.uniform(0.3, 1.0)
            ly = y - ln * rnd.uniform(0.2, 0.8)
            ginkgo_leaf(d, lx, ly, 12, rnd.randint(0, 360), rnd.choice(GINKGO))


# 01 서론: 은행잎 길 + 앙상해지는 나무
def intro():
    img = gradient(W, H, (200, 214, 226), (236, 230, 216))
    d = ImageDraw.Draw(img)
    # 길 (원근)
    d.polygon([(420, 460), (780, 460), (1150, H), (50, H)], fill=(214, 196, 160))
    img = leaf_carpet(img, 320, 2, (60, 470, 1140, H))
    d = ImageDraw.Draw(img)
    for i, x in enumerate((160, 300, 900, 1040)):
        bare_tree(d, x, 520 if i in (1, 2) else 600, 380 if i in (1, 2) else 480, leaves=8 - i * 2, seed=i)
    # 떨어지는 잎
    rnd = random.Random(3)
    for _ in range(14):
        ginkgo_leaf(d, rnd.randint(100, 1100), rnd.randint(100, 440), 14, rnd.randint(0, 360), rnd.choice(GINKGO))
    label(d, 40, 40, "늦가을 → 초겨울 감성 갤러리", 32)
    noise(img, seed=4).save(OUT / "01_intro.png")


# 02 본론1: 낙엽 탑뷰 + 신발 끝 + 빨간 잎 하나
def body1():
    img = gradient(W, H, (200, 176, 140), (186, 160, 124))
    img = leaf_carpet(img, 900, 5)
    d = ImageDraw.Draw(img)
    # 3분할 격자
    for g in (1, 2):
        d.line([(W * g / 3, 0), (W * g / 3, H)], fill=(255, 255, 255), width=2)
        d.line([(0, H * g / 3), (W, H * g / 3)], fill=(255, 255, 255), width=2)
    # 교차점의 빨간 단풍잎
    cx, cy = W * 2 / 3, H / 3
    maple_leaf(d, cx, cy, 56, -18, MAPLE[0])
    d.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], outline=(255, 255, 255), width=4)
    # 신발 끝 (아래 가장자리)
    for x in (430, 600):
        d.rounded_rectangle([x, H - 90, x + 130, H + 60], 60, fill=(60, 56, 60))
        d.rounded_rectangle([x + 10, H - 80, x + 120, H - 56], 12, fill=(230, 226, 220))
    label(d, 40, 40, "장면 하나 · 낙엽 탑뷰", 30, (40, 34, 30), (255, 255, 255))
    noise(img, seed=6).save(OUT / "02_body1.png")


# 03 본론2: 낮은 햇살 + 긴 그림자
def body2():
    img = gradient(W, H, (246, 214, 170), (236, 226, 206))
    d = ImageDraw.Draw(img)
    ground = 430
    d.rectangle([0, ground, W, H], fill=(206, 186, 150))
    img = leaf_carpet(img, 120, 7, (0, ground + 10, W, H))
    d = ImageDraw.Draw(img, "RGBA")
    sun = (1080, 330)
    # 해 + 빛 갈라짐
    for k in range(8):
        a = math.radians(k * 45 + 22)
        d.line([sun, (sun[0] + 90 * math.cos(a), sun[1] + 90 * math.sin(a))], fill=(255, 240, 200, 200), width=3)
    d.ellipse([sun[0] - 34, sun[1] - 34, sun[0] + 34, sun[1] + 34], fill=(255, 236, 180))
    # 나무 + 긴 그림자 (왼쪽으로 길게)
    for x, h in ((820, 300), (560, 260), (300, 280)):
        bare_tree(d, x, ground + 10, h, seed=x)
        d.polygon([(x - 6, ground + 12), (x + 6, ground + 12), (x - 520, ground + 140), (x - 540, ground + 120)], fill=(90, 70, 60, 110))
    # 벤치 + 그림자
    bx, by = 620, 560
    d.rectangle([bx, by, bx + 200, by + 16], fill=(120, 80, 56))
    d.rectangle([bx, by - 50, bx + 200, by - 36], fill=(120, 80, 56))
    for lx in (bx + 14, bx + 180):
        d.rectangle([lx, by + 16, lx + 8, by + 70], fill=(70, 60, 56))
    d.polygon([(bx, by + 70), (bx + 200, by + 70), (bx - 260, by + 170), (bx - 460, by + 170)], fill=(90, 70, 60, 90))
    label(d, 40, 40, "장면 둘 · 오후 햇살과 긴 그림자", 30)
    label(d, 40, H - 90, "밝기 바를 살짝 내려 대비 살리기", 24, (40, 34, 30, 220), (255, 255, 255))
    noise(img, seed=8).save(OUT / "03_body2.png")


# 04 본론3: 김 나는 머그 + 흐린 창밖
def body3():
    img = gradient(W, H, (176, 186, 196), (150, 160, 172))
    # 흐린 창밖 (앙상한 나무)
    outside = gradient(W, 560, (206, 214, 222), (186, 194, 204))
    od = ImageDraw.Draw(outside)
    for i, x in enumerate((140, 420, 760, 1040)):
        bare_tree(od, x, 560, 360 + (i % 2) * 60, color=(130, 130, 136), seed=i)
    outside = outside.filter(ImageFilter.GaussianBlur(8))
    img.paste(outside, (0, 0))
    d = ImageDraw.Draw(img)
    # 창틀 + 테이블
    d.rectangle([0, 0, W, 560], outline=(90, 70, 60), width=26)
    d.line([(W // 2, 0), (W // 2, 560)], fill=(90, 70, 60), width=18)
    d.rectangle([0, 560, W, H], fill=(150, 110, 82))
    # 어두운 배경 판 (김이 잘 보이게)
    d.rectangle([380, 140, 820, 560], fill=(70, 60, 58))
    # 머그
    mx, my = 600, 640
    d.ellipse([mx - 150, my + 40, mx + 150, my + 90], fill=(120, 86, 64))
    d.rounded_rectangle([mx - 110, my - 170, mx + 110, my + 60], 40, fill=(236, 226, 214))
    d.ellipse([mx - 110, my - 190, mx + 110, my - 150], fill=(120, 76, 52))
    d.arc([mx + 80, my - 130, mx + 170, my - 20], -90, 90, fill=(236, 226, 214), width=22)
    # 니트 소매 손
    d.rounded_rectangle([mx - 260, my - 110, mx - 90, my + 10], 50, fill=(196, 92, 80))
    for k in range(5):
        d.line([(mx - 250 + k * 30, my - 104), (mx - 250 + k * 30, my + 4)], fill=(176, 76, 66), width=4)
    d.rounded_rectangle([mx - 120, my - 100, mx - 60, my - 10], 26, fill=(246, 210, 186))
    # 김 (빛 받는 흰 줄기)
    steam = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam)
    for k, off in enumerate((-50, 0, 50)):
        pts = [(mx + off + 26 * math.sin(t / 30 + k), my - 200 - t) for t in range(0, 300, 6)]
        sd.line(pts, fill=(255, 255, 255, 190), width=14)
    steam = steam.filter(ImageFilter.GaussianBlur(7))
    img = Image.alpha_composite(img.convert("RGBA"), steam).convert("RGB")
    d = ImageDraw.Draw(img)
    label(d, 40, 600, "장면 셋 · 따뜻한 김과 차가운 창밖", 28)
    label(d, 40, 680, "어두운 배경 + 옆에서 오는 빛", 24, (40, 34, 30), (255, 255, 255))
    noise(img, seed=9).save(OUT / "04_body3.png")


# 05 결론: 브랜드
def outro():
    img = gradient(W, H, (44, 36, 30), (22, 20, 18))
    d = ImageDraw.Draw(img)
    for y0 in (0, H - 60):
        d.rectangle([0, y0, W, y0 + 60], fill=(14, 13, 13))
        for x in range(20, W, 60):
            d.rounded_rectangle([x, y0 + 17, x + 32, y0 + 43], 4, fill=(225, 200, 165))
    ginkgo_leaf(d, W // 2, 270, 110, 0, (232, 186, 70))
    center_text(d, 320, "지담 스튜디오", font(100, True), (250, 238, 220))
    center_text(d, 470, "일상을 작품으로 남기는 사진 스튜디오", font(36), (230, 196, 120))
    center_text(d, 535, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (205, 180, 150))
    noise(img, seed=10).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

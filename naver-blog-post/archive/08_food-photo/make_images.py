"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 음식·카페 사진 잘 찍는 법)"""
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (66, 48, 40)
ACCENT = (206, 122, 82)
TABLE = (214, 186, 156)
CREAM = (252, 244, 230)
SPONGE = (236, 198, 140)
BERRY = (214, 70, 86)
COFFEE = (96, 62, 44)


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


def wood(w, h, seed=1):
    img = gradient(w, h, (226, 198, 166), (204, 172, 140))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(40):
        y = rnd.randint(0, h)
        d.line([(0, y), (w, y + rnd.randint(-8, 8))], fill=(196, 164, 132), width=1)
    return img


def cake_side(d, cx, base, s=1.0, lit_left=False):
    """조각 케이크 옆모습 (층 보이게)"""
    w, h = 170 * s, 130 * s
    x0, y0 = cx - w / 2, base - h
    d.ellipse([cx - 120 * s, base - 22 * s, cx + 120 * s, base + 22 * s], fill=(250, 250, 248))  # 접시
    layers = [(CREAM, 0.0, 0.18), (SPONGE, 0.18, 0.42), (CREAM, 0.42, 0.55), (SPONGE, 0.55, 0.82), (CREAM, 0.82, 1.0)]
    for c, a, b in layers:
        d.rectangle([x0, y0 + h * a, x0 + w, y0 + h * b], fill=c)
    for k in range(3):
        bx = x0 + 30 * s + k * 50 * s
        d.ellipse([bx, y0 - 26 * s, bx + 34 * s, y0 + 6 * s], fill=BERRY)
    if lit_left:
        d.rectangle([x0, y0, x0 + w * 0.35, y0 + h], fill=None)


def shade(img, box, side="right", strength=90):
    """box 영역의 한쪽을 어둡게 (옆에서 들어온 빛 표현)"""
    x0, y0, x1, y1 = [int(v) for v in box]
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    for i in range(x1 - x0):
        t = i / max(x1 - x0, 1)
        a = int(strength * (t if side == "right" else 1 - t))
        md.line([(x0 + i, y0), (x0 + i, y1)], fill=a)
    dark = Image.new("RGB", img.size, (60, 40, 30))
    return Image.composite(dark, img, mask)


def cup(d, cx, base, s=1.0):
    d.ellipse([cx - 70 * s, base - 16 * s, cx + 70 * s, base + 16 * s], fill=(250, 250, 248))
    d.rounded_rectangle([cx - 46 * s, base - 90 * s, cx + 46 * s, base - 4 * s], int(18 * s), fill=(250, 250, 248))
    d.ellipse([cx - 46 * s, base - 102 * s, cx + 46 * s, base - 78 * s], fill=COFFEE)
    d.arc([cx + 36 * s, base - 76 * s, cx + 76 * s, base - 30 * s], -90, 90, fill=(250, 250, 248), width=int(10 * s))


# 01 서론: 창가 테이블 + 폰으로 찍는 손
def intro():
    img = gradient(W, H, (246, 238, 226), (232, 220, 204))
    d = ImageDraw.Draw(img)
    # 창
    d.rectangle([60, 60, 520, 520], fill=(250, 246, 236), outline=(190, 160, 130), width=12)
    d.line([(290, 60), (290, 520)], fill=(190, 160, 130), width=8)
    d.line([(60, 290), (520, 290)], fill=(190, 160, 130), width=8)
    img.paste(wood(W, 300, 2), (0, 500))
    d = ImageDraw.Draw(img)
    cake_side(d, 560, 640, 1.2)
    cup(d, 820, 640, 1.1)
    img = shade(img, (440, 450, 680, 650), "right", 70)
    d = ImageDraw.Draw(img)
    # 스마트폰 든 손
    px, py = 860, 210
    d.rounded_rectangle([px, py, px + 200, py + 330], 28, fill=(40, 40, 46))
    d.rounded_rectangle([px + 14, py + 18, px + 186, py + 312], 16, fill=(244, 222, 196))
    sd = d
    sd.ellipse([px + 60, py + 150, px + 140, py + 200], fill=CREAM)
    sd.rectangle([px + 70, py + 120, px + 130, py + 175], fill=SPONGE)
    sd.ellipse([px + 85, py + 105, px + 115, py + 128], fill=BERRY)
    d.rounded_rectangle([px + 150, py + 230, px + 250, py + 300], 30, fill=(240, 200, 170))  # 엄지 쪽 손
    d.rounded_rectangle([px - 40, py + 200, px + 30, py + 260], 26, fill=(240, 200, 170))
    d.rounded_rectangle([60, 700, 560, 770], 18, fill=(255, 255, 255))
    d.text((84, 712), "카페 디저트, 맛있게 찍는 법", font=font(34, True), fill=INK)
    noise(img, seed=3).save(OUT / "01_intro.png")


# 02 본론1: 옆에서 들어오는 빛
def body1():
    img = gradient(W, H, (244, 238, 230), (230, 220, 208))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "빛: 창가 자리, 옆에서 들어오는 자연광", font(42, True), INK)
    scene = wood(760, 520, 4)
    sd = ImageDraw.Draw(scene)
    # 창 (왼쪽 벽)
    sd.rectangle([0, 0, 90, 300], fill=(255, 250, 238))
    sd.polygon([(90, 30), (520, 160), (520, 420), (90, 300)], fill=(250, 232, 196))  # 빛 줄기
    cake_side(sd, 380, 380, 1.4)
    scene = shade(scene, (260, 160, 500, 420), "right", 110)
    sd = ImageDraw.Draw(scene)
    # 반사판(냅킨)
    sd.polygon([(560, 220), (620, 200), (620, 400), (560, 420)], fill=(255, 255, 255))
    img.paste(scene, (60, 130))
    d = ImageDraw.Draw(img)
    d.text((80, 140), "창문", font=font(24, True), fill=INK)
    d.text((600, 560), "흰 냅킨 = 반사판", font=font(22, True), fill=ACCENT)
    bx = 860
    tips = [("ON", "창가 자리 고르기", (110, 170, 110)), ("ON", "빛은 옆·뒤쪽에서", (110, 170, 110)), ("OFF", "플래시 끄기", (200, 90, 80)), ("-5", "색온도 살짝 낮추기", ACCENT)]
    for i, (tag, t, c) in enumerate(tips):
        y = 150 + i * 120
        d.rounded_rectangle([bx, y, bx + 290, y + 92], 16, fill=(255, 255, 255))
        d.rounded_rectangle([bx + 14, y + 22, bx + 84, y + 70], 12, fill=c)
        center_text(d, y + 27, tag, font(24, True), (255, 255, 255), x0=bx + 14, width=70)
        d.text((bx + 100, y + 28), t, font=font(24, True), fill=INK)
    noise(img, seed=5).save(OUT / "02_body1.png")


# 03 본론2: 세 가지 각도
def body2():
    img = gradient(W, H, (244, 238, 230), (230, 220, 208))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "각도: 음식 모양에 맞춰 고르기", font(44, True), INK)
    cw, ch = 330, 330
    x0 = (W - cw * 3 - 40 * 2) / 2
    labels = [("탑뷰 (90°)", "브런치 · 피자 · 여러 메뉴"), ("45도", "커피잔 · 조각 케이크"), ("정면 (0°)", "팬케이크 · 버거 · 층 케이크")]
    for i, (name, use) in enumerate(labels):
        x = int(x0 + i * (cw + 40))
        tile = wood(cw, ch, 6 + i)
        td = ImageDraw.Draw(tile)
        if i == 0:  # 위에서 본 접시
            td.ellipse([55, 55, 275, 275], fill=(250, 250, 248))
            td.ellipse([95, 95, 235, 235], fill=SPONGE)
            for k in range(5):
                td.ellipse([110 + k * 22, 140 + (k % 2) * 30, 136 + k * 22, 166 + (k % 2) * 30], fill=BERRY)
            td.ellipse([240, 40, 310, 110], fill=(250, 250, 248)); td.ellipse([252, 52, 298, 98], fill=COFFEE)
            for g in (1, 2):
                td.line([(cw * g / 3, 0), (cw * g / 3, ch)], fill=(255, 255, 255), width=2)
                td.line([(0, ch * g / 3), (cw, ch * g / 3)], fill=(255, 255, 255), width=2)
        elif i == 1:
            tile = gradient(cw, ch, (246, 236, 222), (214, 186, 156))
            td = ImageDraw.Draw(tile)
            td.polygon([(0, 190), (cw, 160), (cw, ch), (0, ch)], fill=TABLE)
            cup(td, 120, 250, 0.9)
            cake_side(td, 230, 270, 0.8)
        else:
            tile = gradient(cw, ch, (246, 236, 222), (236, 222, 204))
            td = ImageDraw.Draw(tile)
            td.rectangle([0, 270, cw, ch], fill=TABLE)
            td.ellipse([60, 255, 270, 285], fill=(250, 250, 248))
            for k in range(4):
                y = 250 - k * 34
                td.rounded_rectangle([85, y - 30, 245, y], 14, fill=(226, 172, 100))
            td.rounded_rectangle([140, 105, 190, 125], 8, fill=(250, 220, 120))
            td.ellipse([110, 100, 220, 120], fill=(250, 244, 230))
        img.paste(tile, (x, 130))
        d = ImageDraw.Draw(img)
        d.rectangle([x, 130, x + cw, 130 + ch], outline=(255, 255, 255), width=8)
        center_text(d, 490, name, font(34, True), INK, x0=x, width=cw)
        center_text(d, 540, use, font(22), ACCENT, x0=x, width=cw)
    center_text(d, 650, "한 메뉴를 세 각도로 찍고, 가장 맛있어 보이는 컷 고르기", font(28, True), (120, 96, 84))
    noise(img, seed=8).save(OUT / "03_body2.png")


# 04 본론3: 연출 (소품 하나 + 여백 + 손)
def body3():
    img = wood(W, H, 9)
    d = ImageDraw.Draw(img)
    center_text(d, 36, "연출: 소품 하나, 여백, 그리고 손", font(44, True), INK)
    # 왼쪽: 정돈된 구도 (위에서 본 장면)
    d.ellipse([170, 260, 470, 560], fill=(250, 250, 248))
    d.ellipse([230, 320, 410, 500], fill=SPONGE)
    for k in range(4):
        d.ellipse([262 + k * 30, 380, 290 + k * 30, 408], fill=BERRY)
    cupx, cupy = 560, 260
    d.ellipse([cupx - 70, cupy - 70, cupx + 70, cupy + 70], fill=(250, 250, 248))
    d.ellipse([cupx - 50, cupy - 50, cupx + 50, cupy + 50], fill=COFFEE)
    # 작은 꽃
    for a in range(5):
        import math
        fx = 120 + 22 * math.cos(math.radians(72 * a))
        fy = 640 + 22 * math.sin(math.radians(72 * a))
        d.ellipse([fx - 14, fy - 14, fx + 14, fy + 14], fill=(250, 196, 210))
    d.ellipse([110, 630, 130, 650], fill=(250, 220, 110))
    # 포크 든 손
    d.line([(330, 420), (560, 640)], fill=(200, 200, 205), width=10)
    d.rounded_rectangle([520, 600, 660, 690], 40, fill=(240, 200, 170))
    d.rounded_rectangle([600, 640, 760, 720], 36, fill=(232, 190, 160))
    # 오른쪽 체크리스트 (여백 영역)
    bx = 800
    d.rounded_rectangle([bx, 160, bx + 340, 600], 20, fill=(255, 252, 246))
    d.text((bx + 24, 182), "연출 체크", font=font(30, True), fill=INK)
    items = ["물티슈·영수증 치우기", "소품은 딱 하나만", "음식은 살짝 옆에", "반대쪽엔 여백", "한 입 뜨는 손 담기"]
    for i, t in enumerate(items):
        y = 250 + i * 66
        d.line([(bx + 28, y + 16), (bx + 38, y + 28), (bx + 58, y + 4)], fill=ACCENT, width=5, joint="curve")
        d.text((bx + 74, y), t, font=font(24), fill=INK)
    noise(img, seed=10).save(OUT / "04_body3.png")


# 05 결론: 브랜드 (타이틀 톤)
def outro():
    img = gradient(W, H, (42, 36, 34), (22, 20, 20))
    d = ImageDraw.Draw(img)
    for y0 in (0, H - 60):
        d.rectangle([0, y0, W, y0 + 60], fill=(14, 13, 13))
        for x in range(20, W, 60):
            d.rounded_rectangle([x, y0 + 17, x + 32, y0 + 43], 4, fill=(225, 200, 165))
    # 컵 아이콘
    cx, by = W // 2, 280
    d.rounded_rectangle([cx - 60, by - 110, cx + 60, by], 22, outline=(225, 200, 165), width=8)
    d.arc([cx + 40, by - 90, cx + 100, by - 30], -90, 90, fill=(225, 200, 165), width=8)
    for k in (-25, 0, 25):
        d.arc([cx + k - 12, by - 170, cx + k + 12, by - 125], 90, 270, fill=(225, 200, 165), width=4)
    center_text(d, 320, "지담 스튜디오", font(100, True), (250, 238, 220))
    center_text(d, 470, "일상을 작품으로 남기는 사진 스튜디오", font(36), (225, 200, 165))
    center_text(d, 535, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (205, 180, 150))
    noise(img, seed=11).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

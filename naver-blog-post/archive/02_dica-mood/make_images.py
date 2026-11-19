"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 디카 감성)"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)

FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
DATE_ORANGE = (255, 150, 40)


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def noise(img, amount=10, alpha=0.05, seed=1):
    rnd = random.Random(seed)
    n = Image.new("L", img.size)
    n.putdata([128 + rnd.randint(-amount, amount) for _ in range(img.size[0] * img.size[1])])
    return Image.blend(img, n.convert("RGB"), alpha)


def radial_glow(size, center, radius, color, strength=1.0):
    """플래시 빛 번짐"""
    glow = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(glow)
    cx, cy = center
    for r in range(radius, 0, -6):
        t = 1 - r / radius
        c = tuple(int(color[i] * t * strength) for i in range(3))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    return glow.filter(ImageFilter.GaussianBlur(20))


def center_text(d, y, text, f, fill, width=W):
    w = d.textlength(text, font=f)
    d.text(((width - w) / 2, y), text, font=f, fill=fill)


def bolt(d, x, y, h, fill):
    """번개(플래시) 아이콘 직접 그리기 (폰트에 ⚡ 기호가 없음)"""
    s = h / 40
    pts = [(14, 0), (2, 22), (12, 22), (6, 40), (24, 14), (14, 14), (20, 0)]
    d.polygon([(x + px * s, y + py * s) for px, py in pts], fill=fill)


def check(d, x, y, size, fill):
    d.line([(x, y + size * 0.5), (x + size * 0.38, y + size * 0.88), (x + size, y + size * 0.1)],
           fill=fill, width=max(3, int(size / 6)), joint="curve")


def date_stamp(d, x, y, text="'26 11 19", size=40):
    d.text((x, y), text, font=font(size, True), fill=DATE_ORANGE)


def person(d, cx, base_y, scale=1.0, skin=(250, 225, 205), shirt=(70, 110, 170), hair=(40, 30, 30)):
    s = scale
    d.ellipse([cx - 120 * s, base_y - 230 * s, cx + 120 * s, base_y + 40 * s], fill=shirt)  # 몸
    d.ellipse([cx - 70 * s, base_y - 380 * s, cx + 70 * s, base_y - 220 * s], fill=skin)  # 얼굴
    d.chord([cx - 78 * s, base_y - 400 * s, cx + 78 * s, base_y - 270 * s], 180, 360, fill=hair)  # 머리
    for ex in (-26, 26):  # 눈
        d.ellipse([cx + (ex - 7) * s, base_y - 305 * s, cx + (ex + 7) * s, base_y - 291 * s], fill=(40, 30, 30))
    d.arc([cx - 30 * s, base_y - 285 * s, cx + 30 * s, base_y - 250 * s], 20, 160, fill=(200, 90, 90), width=int(5 * s))


# 01 서론: 밤에 플래시 터뜨린 스냅
def intro():
    img = gradient(W, H, (18, 20, 40), (8, 8, 18))
    d = ImageDraw.Draw(img)
    # 배경 도시 불빛 (보케)
    rnd = random.Random(3)
    for _ in range(40):
        x, y, r = rnd.randint(0, W), rnd.randint(60, 420), rnd.randint(8, 26)
        c = rnd.choice([(255, 200, 120), (255, 120, 140), (140, 180, 255)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v * 0.45) for v in c))
    img = img.filter(ImageFilter.GaussianBlur(4))
    img = Image.composite(img, img, Image.new("L", img.size, 255))
    # 플래시 빛 번짐
    from PIL import ImageChops
    img = ImageChops.add(img, radial_glow(img.size, (600, 470), 420, (255, 255, 245), 0.55))
    d = ImageDraw.Draw(img)
    person(d, 600, 800, 1.15, skin=(255, 238, 224), shirt=(230, 80, 90))
    # 브이 손
    d.rounded_rectangle([760, 430, 800, 560], 18, fill=(255, 238, 224))
    d.polygon([(765, 440), (745, 360), (765, 355), (785, 432)], fill=(255, 238, 224))
    d.polygon([(785, 432), (805, 352), (825, 358), (800, 445)], fill=(255, 238, 224))
    # 디카 화면 UI
    d.rectangle([30, 30, W - 30, H - 30], outline=(255, 255, 255), width=3)
    bolt(d, 60, 52, 40, (255, 255, 255))
    d.text((100, 50), "ON", font=font(34, True), fill=(255, 255, 255))
    d.text((W - 210, 50), "4:3  ■■■", font=font(30, True), fill=(255, 255, 255))
    date_stamp(d, W - 260, H - 110)
    noise(img, seed=4).save(OUT / "01_intro.png")


# 02 본론1: 플래시 켜기 + 거리 1~2m
def body1():
    img = gradient(W, H, (34, 38, 58), (20, 22, 36))
    d = ImageDraw.Draw(img)
    center_text(d, 40, "플래시를 켜는 순간, 디카 감성 시작", font(46, True), (255, 255, 255))
    # 휴대폰 (왼쪽)
    px, py = 120, 230
    d.rounded_rectangle([px, py, px + 190, py + 360], 30, fill=(50, 52, 60), outline=(150, 150, 160), width=4)
    d.ellipse([px + 30, py + 30, px + 80, py + 80], fill=(20, 20, 25), outline=(120, 120, 130), width=4)
    d.ellipse([px + 100, py + 40, px + 130, py + 70], fill=(255, 245, 200))
    # 빛 줄기
    d.polygon([(px + 130, py + 55), (900, 230), (900, 640)], fill=(80, 78, 70))
    d.polygon([(px + 130, py + 55), (900, 300), (900, 570)], fill=(120, 115, 95))
    # 인물 (오른쪽)
    person(d, 930, 700, 0.95, skin=(255, 236, 222), shirt=(90, 160, 120))
    # 거리 화살표
    y = 680
    d.line([(px + 200, y), (800, y)], fill=DATE_ORANGE, width=5)
    d.polygon([(800, y - 14), (830, y), (800, y + 14)], fill=DATE_ORANGE)
    d.polygon([(px + 200, y - 14), (px + 170, y), (px + 200, y + 14)], fill=DATE_ORANGE)
    center_text(d, y - 60, "1 ~ 2m", font(40, True), DATE_ORANGE, width=W - 120)
    # 번개 아이콘 라벨
    d.rounded_rectangle([px - 10, py - 90, px + 220, py - 30], 14, fill=(255, 210, 60))
    bolt(d, px + 12, py - 80, 40, (40, 30, 20))
    d.text((px + 50, py - 86), "플래시 켜짐", font=font(32, True), fill=(40, 30, 20))
    center_text(d, H - 70, "어두운 실내·저녁에 정면으로 찍어보세요", font(30, True), (220, 220, 230))
    noise(img, seed=5).save(OUT / "02_body1.png")


# 03 본론2: 연속 스냅 필름처럼
def body2():
    img = gradient(W, H, (240, 238, 232), (222, 218, 210))
    d = ImageDraw.Draw(img)
    center_text(d, 40, "완벽한 구도보다 '그 순간'을 찍는 스냅", font(46, True), (60, 50, 50))
    # 4장의 4:3 프레임
    fw, fh, gap = 240, 180, 30
    x0 = (W - (fw * 4 + gap * 3)) / 2
    y0 = 230
    skins = [(250, 228, 210)] * 4
    tilts = [0, -6, 4, -3]
    smiles = [(20, 160), (10, 170), (0, 180), (30, 150)]
    for i in range(4):
        tile = Image.new("RGB", (fw, fh), (60, 70, 100))
        td = ImageDraw.Draw(tile)
        tile.paste(gradient(fw, fh, (70, 90, 130), (40, 45, 70)))
        td = ImageDraw.Draw(tile)
        cx = fw / 2 + (i - 1.5) * 18
        td.ellipse([cx - 70, fh - 70, cx + 70, fh + 90], fill=(240, 120, 110))
        td.ellipse([cx - 40, 40, cx + 40, 130], fill=skins[i])
        td.chord([cx - 44, 30, cx + 44, 100], 180, 360, fill=(40, 30, 30))
        a, b = smiles[i]
        td.arc([cx - 18, 85, cx + 18, 115], a, b, fill=(190, 80, 80), width=4)
        if i == 2:
            td.ellipse([cx - 30, 70, cx - 14, 82], fill=(40, 30, 30))
        tile = tile.rotate(tilts[i], expand=False, fillcolor=(30, 30, 40))
        if i == 3:
            tile = tile.filter(ImageFilter.BoxBlur(3))  # 살짝 흔들림
        x = int(x0 + i * (fw + gap))
        d.rectangle([x - 10, y0 - 10, x + fw + 10, y0 + fh + 10], fill=(255, 255, 255))
        img.paste(tile, (x, y0))
        ImageDraw.Draw(img).text((x + fw - 95, y0 + fh - 30), "'26 11 19", font=font(18, True), fill=DATE_ORANGE)
    d = ImageDraw.Draw(img)
    # BEST 표시
    bx = int(x0 + 2 * (fw + gap))
    d.rectangle([bx - 14, y0 - 14, bx + fw + 14, y0 + fh + 14], outline=(240, 90, 70), width=6)
    d.rounded_rectangle([bx + fw / 2 - 60, y0 + fh + 30, bx + fw / 2 + 60, y0 + fh + 80], 12, fill=(240, 90, 70))
    d.text((bx + fw / 2 - 42, y0 + fh + 32), "BEST", font=font(32, True), fill=(255, 255, 255))
    labels = [("연속 촬영", 160), ("4:3 비율", 520), ("살짝 기울여도 OK", 850)]
    for text, x in labels:
        check(d, x, 572, 28, (240, 90, 70))
        d.text((x + 40, 560), text, font=font(32, True), fill=(80, 60, 55))
    center_text(d, H - 80, "셔터를 길게 눌러 연속으로, 그중 가장 자연스러운 한 장", font(30, True), (90, 70, 60))
    noise(img, seed=6, alpha=0.04).save(OUT / "03_body2.png")


# 04 본론3: 디카 톤 보정값 + 날짜 스탬프
def body3():
    img = gradient(W, H, (228, 236, 246), (206, 218, 234))
    d = ImageDraw.Draw(img)
    center_text(d, 40, "쨍하고 차가운 디카 색감 만들기", font(46, True), (40, 60, 90))
    sliders = [("밝기", "+10", 0.60), ("대비", "+15", 0.65), ("색온도", "-10", 0.38), ("선명도", "살짝 +", 0.58)]
    for i, (name, val, pos) in enumerate(sliders):
        y = 190 + i * 105
        d.text((90, y - 24), name, font=font(34, True), fill=(40, 60, 90))
        x0, x1 = 250, 600
        d.rounded_rectangle([x0, y - 6, x1, y + 6], 6, fill=(180, 195, 215))
        d.rounded_rectangle([x0, y - 6, x0 + (x1 - x0) * pos, y + 6], 6, fill=(70, 130, 210))
        kx = x0 + (x1 - x0) * pos
        d.ellipse([kx - 20, y - 20, kx + 20, y + 20], fill=(255, 255, 255), outline=(70, 130, 210), width=5)
        d.text((630, y - 22), val, font=font(30, True), fill=(50, 100, 180))
    # 결과 미리보기 사진 + 날짜
    px, py, pw, ph = 790, 170, 340, 255
    photo = gradient(pw, ph, (90, 140, 200), (40, 70, 120))
    pd = ImageDraw.Draw(photo)
    pd.rectangle([0, ph * 0.62, pw, ph], fill=(70, 80, 95))
    pd.ellipse([pw * 0.55, ph * 0.15, pw * 0.75, ph * 0.42], fill=(245, 248, 255))
    d.rectangle([px - 12, py - 12, px + pw + 12, py + ph + 50], fill=(255, 255, 255))
    img.paste(photo, (px, py))
    d = ImageDraw.Draw(img)
    date_stamp(d, px + pw - 150, py + ph - 42, size=28)
    d.text((px + 70, py + ph + 6), "← 오른쪽 아래 날짜 표시", font=font(24, True), fill=(220, 110, 30))
    center_text(d, H - 80, "필름은 따뜻하게, 디카는 차갑고 쨍하게", font(32, True), (40, 60, 90))
    noise(img, seed=7, alpha=0.03).save(OUT / "04_body3.png")


# 05 결론: 디카 LCD 화면 + 브랜드
def outro():
    img = Image.new("RGB", (W, H), (190, 192, 198))
    d = ImageDraw.Draw(img)
    # 카메라 바디
    d.rounded_rectangle([60, 50, W - 60, H - 50], 50, fill=(200, 203, 210), outline=(150, 152, 160), width=4)
    # LCD
    lx, ly, lw, lh = 150, 120, 900, 560
    lcd = gradient(lw, lh, (36, 34, 44), (18, 16, 22))
    lcd = Image.blend(lcd, radial_glow((lw, lh), (lw / 2, lh / 2), 380, (255, 240, 220), 0.35), 0.5)
    img.paste(lcd, (lx, ly))
    d = ImageDraw.Draw(img)
    d.rectangle([lx, ly, lx + lw, ly + lh], outline=(60, 60, 70), width=10)
    center_text(d, ly + 140, "지담 스튜디오", font(104, True), (255, 245, 230))
    center_text(d, ly + 290, "일상을 작품으로 남기는 사진 스튜디오", font(36), (235, 215, 185))
    center_text(d, ly + 350, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (210, 190, 165))
    bolt(d, lx + 30, ly + 28, 34, (255, 255, 255))
    d.text((lx + 75, ly + 25), "▶  PLAY", font=font(28, True), fill=(255, 255, 255))
    date_stamp(d, lx + lw - 230, ly + lh - 75, size=38)
    # 버튼들
    for i, label in enumerate(("MENU", "OK", "DISP")):
        bx = 1090
        d.ellipse([bx - 1, 220 + i * 140, bx + 40, 261 + i * 140], fill=(120, 122, 130))
    noise(img, seed=8, alpha=0.03).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

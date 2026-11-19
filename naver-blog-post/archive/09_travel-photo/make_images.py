"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 여행 사진 팁)"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (44, 58, 70)
ACCENT = (232, 120, 80)
SKY = ((150, 200, 235), (220, 236, 245))
SEA = (70, 150, 195)
MOUNT = (110, 150, 130)
PERSON = (40, 46, 60)


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


def landscape(w, h, sky=SKY, sun=None):
    img = gradient(w, h, *sky)
    d = ImageDraw.Draw(img)
    if sun:
        x, y, r, c = sun
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    d.polygon([(0, h * 0.55), (w * 0.25, h * 0.28), (w * 0.45, h * 0.5), (w * 0.65, h * 0.3), (w, h * 0.55), (w, h), (0, h)], fill=MOUNT)
    d.rectangle([0, h * 0.62, w, h], fill=SEA)
    for k in range(6):
        y = h * 0.66 + k * h * 0.05
        d.line([(w * 0.1 + k * 20, y), (w * 0.4 + k * 20, y)], fill=(170, 210, 235), width=2)
    return img


def person(d, cx, base, s=1.0, color=PERSON):
    d.ellipse([cx - 14 * s, base - 120 * s, cx + 14 * s, base - 92 * s], fill=color)
    d.polygon([(cx - 18 * s, base - 90 * s), (cx + 18 * s, base - 90 * s), (cx + 14 * s, base - 42 * s), (cx - 14 * s, base - 42 * s)], fill=color)
    d.line([(cx - 6 * s, base - 42 * s), (cx - 9 * s, base)], fill=color, width=max(2, int(8 * s)))
    d.line([(cx + 6 * s, base - 42 * s), (cx + 9 * s, base)], fill=color, width=max(2, int(8 * s)))


def label(d, x, y, text, size=26):
    f = font(size, True)
    w = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + w + 36, y + size + 24], 14, fill=(255, 255, 255))
    d.text((x + 18, y + 9), text, font=f, fill=INK)


# 01 서론: 지도, 가방, 폰 너머 풍경
def intro():
    img = landscape(W, H, sun=(930, 170, 60, (255, 236, 170)))
    d = ImageDraw.Draw(img)
    # 지도
    d.polygon([(60, 560), (330, 520), (360, 760), (80, 790)], fill=(246, 236, 210))
    d.line([(110, 600), (200, 640), (260, 610), (310, 700)], fill=ACCENT, width=4)
    d.ellipse([300, 690, 322, 712], fill=ACCENT)
    # 캐리어
    d.rounded_rectangle([880, 470, 1060, 740], 22, fill=(232, 120, 80))
    d.rounded_rectangle([930, 430, 1010, 480], 14, outline=(90, 60, 50), width=8)
    for x in (920, 1020):
        d.line([(x, 490), (x, 720)], fill=(200, 96, 64), width=6)
    # 폰 프레임
    px, py, pw, ph = 420, 150, 360, 560
    d.rounded_rectangle([px, py, px + pw, py + ph], 40, outline=(30, 32, 40), width=18)
    d.rounded_rectangle([px + 9, py + 9, px + pw - 9, py + ph - 9], 32, outline=(255, 255, 255), width=4)
    for g in (1, 2):
        d.line([(px + pw * g / 3, py + 18), (px + pw * g / 3, py + ph - 18)], fill=(255, 255, 255), width=2)
        d.line([(px + 18, py + ph * g / 3), (px + pw - 18, py + ph * g / 3)], fill=(255, 255, 255), width=2)
    label(d, 40, 40, "여행 사진, 스마트폰 하나로", 32)
    noise(img, seed=2).save(OUT / "01_intro.png")


# 02 본론1: 이른 아침 vs 한낮
def body1():
    img = gradient(W, H, (240, 244, 248), (222, 230, 238))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "시간: 이른 아침과 해 질 녘에 명소 찍기", font(42, True), INK)
    pw, ph = 500, 360

    def place(morning):
        sky = ((255, 210, 170), (250, 236, 220)) if morning else ((120, 180, 230), (200, 225, 245))
        pic = gradient(pw, ph, *sky)
        pd = ImageDraw.Draw(pic)
        sun = (90, 230, 40, (255, 220, 150)) if morning else (pw / 2, 50, 36, (255, 250, 220))
        pd.ellipse([sun[0] - sun[2], sun[1] - sun[2], sun[0] + sun[2], sun[1] + sun[2]], fill=sun[3])
        # 탑(명소)
        cx = pw / 2
        pd.polygon([(cx - 60, ph - 60), (cx - 30, 90), (cx + 30, 90), (cx + 60, ph - 60)], fill=(170, 120, 100))
        pd.polygon([(cx - 40, 95), (cx, 40), (cx + 40, 95)], fill=(140, 90, 80))
        if morning:  # 왼쪽에서 비치는 빛 → 오른쪽 그늘
            pd.polygon([(cx, 90), (cx + 30, 90), (cx + 60, ph - 60), (cx, ph - 60)], fill=(130, 90, 80))
        pd.rectangle([0, ph - 60, pw, ph], fill=(200, 190, 170))
        rnd = random.Random(4)
        count = 1 if morning else 22
        for _ in range(count):
            x = rnd.randint(30, pw - 30) if not morning else cx + 120
            person(pd, x, ph - 20 - rnd.randint(0, 20) * (not morning), 0.55, (60, 60, 80) if morning else rnd.choice([(80, 80, 110), (180, 80, 80), (60, 120, 90), (90, 90, 90)]))
        return pic

    for i, (morning, title, sub, c) in enumerate(((True, "이른 아침", "사람 없고 빛은 부드럽게", ACCENT), (False, "한낮", "붐비고 그림자는 진하게", (120, 130, 150)))):
        x = 80 + i * (pw + 40)
        d.rounded_rectangle([x - 10, 120, x + pw + 10, 120 + ph + 150], 20, fill=(255, 255, 255))
        img.paste(place(morning), (x, 130))
        d = ImageDraw.Draw(img)
        center_text(d, 130 + ph + 22, title, font(34, True), INK, x0=x, width=pw)
        center_text(d, 130 + ph + 72, sub, font(24), c, x0=x, width=pw)
    center_text(d, H - 60, "전날 밤 일출·일몰 시간 확인하기", font(26, True), (100, 112, 126))
    noise(img, seed=5).save(OUT / "02_body1.png")


# 03 본론2: 인물은 작게, 풍경은 크게 + 리딩 라인
def body2():
    img = landscape(W, H, sun=(1000, 140, 50, (255, 240, 190)))
    d = ImageDraw.Draw(img)
    # 해안 길 (리딩 라인)
    d.polygon([(260, H), (520, H * 0.64), (580, H * 0.64), (700, H)], fill=(230, 214, 180))
    d.line([(260, H), (520, H * 0.64)], fill=(200, 180, 140), width=4)
    d.line([(700, H), (580, H * 0.64)], fill=(200, 180, 140), width=4)
    # 격자
    for g in (1, 2):
        d.line([(W * g / 3, 0), (W * g / 3, H)], fill=(255, 255, 255), width=2)
        d.line([(0, H * g / 3), (W, H * g / 3)], fill=(255, 255, 255), width=2)
    # 작은 인물 (교차점 근처)
    person(d, W / 3 + 160, H * 2 / 3 + 40, 0.75, (232, 120, 80))
    d.ellipse([W / 3 + 140, H * 2 / 3 - 70, W / 3 + 180, H * 2 / 3 - 30], outline=(255, 255, 255), width=3)
    label(d, 40, 40, "인물은 작게, 풍경은 크게", 30)
    label(d, 760, 640, "길이 인물을 향하게", 24)
    noise(img, seed=6).save(OUT / "03_body2.png")


# 04 본론3: 디테일 컷 모음
def body4_tile(i, s):
    t = Image.new("RGB", (s, s), (250, 246, 238))
    d = ImageDraw.Draw(t)
    if i == 0:  # 기차표
        t.paste(gradient(s, s, (230, 220, 200), (214, 200, 176)))
        d = ImageDraw.Draw(t)
        d.rounded_rectangle([30, 80, s - 30, s - 80], 10, fill=(255, 250, 236))
        d.line([(s * 0.65, 80), (s * 0.65, s - 80)], fill=(200, 190, 170), width=3)
        d.text((50, 100), "TICKET", font=font(28, True), fill=ACCENT)
        d.text((50, 145), "SEOUL → BUSAN", font=font(18, True), fill=INK)
    elif i == 1:  # 골목 간판
        t.paste(gradient(s, s, (210, 200, 190), (180, 170, 160)))
        d = ImageDraw.Draw(t)
        d.rectangle([40, 40, s - 40, s - 20], fill=(150, 130, 120))
        d.rounded_rectangle([60, 70, s - 60, 140], 10, fill=(60, 90, 80))
        center_text(d, 85, "OLD SHOP", font(26, True), (250, 230, 190), x0=60, width=s - 120)
        d.rectangle([90, 170, s - 90, s - 20], fill=(90, 70, 60))
    elif i == 2:  # 현지 음식
        t.paste(gradient(s, s, (226, 198, 166), (204, 172, 140)))
        d = ImageDraw.Draw(t)
        d.ellipse([30, 30, s - 30, s - 30], fill=(250, 250, 248))
        d.ellipse([70, 70, s - 70, s - 70], fill=(232, 120, 80))
        for k in range(6):
            d.ellipse([100 + (k % 3) * 40, 100 + (k // 3) * 50, 125 + (k % 3) * 40, 125 + (k // 3) * 50], fill=(250, 220, 140))
    else:  # 모래 발자국
        t.paste(gradient(s, s, (240, 224, 190), (226, 206, 168)))
        d = ImageDraw.Draw(t)
        for k in range(5):
            x, y = 60 + (k % 2) * 60, s - 50 - k * 50
            d.ellipse([x, y - 30, x + 28, y], fill=(205, 182, 140))
            d.ellipse([x + 4, y - 44, x + 24, y - 30], fill=(205, 182, 140))
    return t


def body3():
    img = gradient(W, H, (244, 242, 238), (228, 224, 216))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "이야기: 풍경 사이사이에 디테일 컷", font(44, True), INK)
    s = 240
    names = ["기차표 · 입장권", "골목 간판", "현지 음식", "모래 위 발자국"]
    x0 = (W - s * 4 - 30 * 3) / 2
    rnd = random.Random(7)
    for i in range(4):
        x = int(x0 + i * (s + 30))
        tile = body4_tile(i, s)
        frame = Image.new("RGB", (s + 24, s + 70), (255, 255, 255))
        frame.paste(tile, (12, 12))
        fd = ImageDraw.Draw(frame)
        center_text(fd, s + 22, names[i], font(22, True), INK, x0=0, width=s + 24)
        frame = frame.convert("RGBA").rotate(rnd.randint(-5, 5), expand=True, fillcolor=(0, 0, 0, 0))
        img.paste(frame, (x - 12, 160), frame)
    d = ImageDraw.Draw(img)
    # 순서 안내
    y = 560
    for i, t in enumerate(("풍경", "인물", "디테일")):
        x = 330 + i * 200
        d.rounded_rectangle([x, y, x + 150, y + 64], 32, fill=ACCENT if i == 2 else (120, 160, 190))
        center_text(d, y + 14, t, font(28, True), (255, 255, 255), x0=x, width=150)
        if i < 2:
            d.polygon([(x + 165, y + 22), (x + 185, y + 32), (x + 165, y + 42)], fill=INK)
    center_text(d, 670, "순서로 섞어 올리면 한 편의 여행기", font(28, True), (100, 112, 126))
    noise(img, seed=8).save(OUT / "04_body3.png")


# 05 결론: 브랜드
def outro():
    img = gradient(W, H, (40, 38, 42), (22, 21, 24))
    d = ImageDraw.Draw(img)
    for y0 in (0, H - 60):
        d.rectangle([0, y0, W, y0 + 60], fill=(14, 13, 13))
        for x in range(20, W, 60):
            d.rounded_rectangle([x, y0 + 17, x + 32, y0 + 43], 4, fill=(225, 200, 165))
    # 산 + 해 아이콘
    cx, by = W // 2, 290
    d.ellipse([cx + 20, by - 160, cx + 70, by - 110], outline=(225, 200, 165), width=6)
    d.line([(cx - 110, by), (cx - 40, by - 110), (cx + 10, by - 50), (cx + 50, by - 90), (cx + 110, by)], fill=(225, 200, 165), width=8, joint="curve")
    center_text(d, 320, "지담 스튜디오", font(100, True), (250, 238, 220))
    center_text(d, 470, "일상을 작품으로 남기는 사진 스튜디오", font(36), (225, 200, 165))
    center_text(d, 535, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (205, 180, 150))
    noise(img, seed=9).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

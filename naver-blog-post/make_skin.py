"""네이버 블로그 '사진 스튜디오' 스킨 이미지 생성
- skin/background.png : 스킨 배경 (1920x1200) - 스튜디오 배경지 + 소프트박스 조명
- skin/title.png      : 타이틀 이미지 (966x300) - 지담 스튜디오
"""
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).parent / "skin"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def vgradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def glow(size, center, radius, color, strength):
    g = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(g)
    cx, cy = center
    for r in range(radius, 0, -8):
        t = (1 - r / radius) ** 1.6
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(c * t * strength) for c in color))
    return g.filter(ImageFilter.GaussianBlur(40))


def grain(img, alpha=0.035, seed=1):
    rnd = random.Random(seed)
    n = Image.new("L", img.size)
    n.putdata([128 + rnd.randint(-14, 14) for _ in range(img.size[0] * img.size[1])])
    return Image.blend(img, n.convert("RGB"), alpha)


def softbox(d, x, y, w, h, flip=False):
    """소프트박스 조명 + 스탠드"""
    d.polygon([(x, y), (x + w, y), (x + w - 30, y + h), (x + 30, y + h)], fill=(30, 28, 28))
    d.rectangle([x + 18, y + 14, x + w - 18, y + h - 14], fill=(255, 250, 238))
    d.rectangle([x + 18, y + 14, x + w - 18, y + h - 14], outline=(220, 215, 205), width=3)
    sx = x + w // 2
    d.rectangle([sx - 6, y + h, sx + 6, 1130], fill=(35, 33, 33))
    for dx in (-90, 0, 90):  # 삼각대
        d.line([(sx, 1040), (sx + dx, 1150)], fill=(35, 33, 33), width=8)


PATTERN_COLOR = (236, 232, 226)  # 하단 패턴(배경 아래쪽 반복) 색 - 밝은 웜그레이


def background():
    """밝은 스튜디오: 글씨가 잘 보이도록 전체를 밝은 톤으로, 양옆에 조명"""
    W, H = 1920, 1200
    img = vgradient(W, H, (214, 209, 202), PATTERN_COLOR)
    d = ImageDraw.Draw(img)
    # 조명 빛 번짐 (가운데 밝게)
    img = ImageChops.add(img, glow((W, H), (960, 500), 700, (40, 36, 30), 1.0))
    d = ImageDraw.Draw(img)
    # 양옆 소프트박스 조명 + 스탠드 (본문 영역 바깥)
    for x in (60, 1600):
        d.polygon([(x, 220), (x + 260, 220), (x + 230, 560), (x + 30, 560)], fill=(70, 66, 64))
        d.rectangle([x + 22, 236, x + 238, 544], fill=(255, 253, 246))
        sx = x + 130
        d.rectangle([sx - 6, 560, sx + 6, 1080], fill=(90, 86, 84))
        for dx in (-90, 0, 90):
            d.line([(sx, 1000), (sx + dx, 1100)], fill=(90, 86, 84), width=8)
    grain(img, alpha=0.02, seed=11).save(OUT / "background.png")
    Image.new("RGB", (40, 40), PATTERN_COLOR).save(OUT / "pattern.png")


def background_dark():
    W, H = 1920, 1200
    # 짙은 스튜디오 벽 + 중앙에 따뜻한 회색 배경지(롤 페이퍼)
    img = vgradient(W, H, (42, 40, 40), (24, 23, 23))
    d = ImageDraw.Draw(img)
    paper = vgradient(1120, 1000, (196, 188, 178), (232, 226, 218))
    mask = Image.new("L", paper.size, 255)
    img.paste(paper, (400, 140), mask)
    # 배경지 롤(상단 막대)
    d.rounded_rectangle([370, 110, 1550, 150], 20, fill=(60, 56, 54))
    d.ellipse([355, 105, 395, 155], fill=(80, 76, 72))
    d.ellipse([1525, 105, 1565, 155], fill=(80, 76, 72))
    # 바닥 그림자
    d.rectangle([0, 1140, W, H], fill=(20, 19, 19))
    # 조명이 배경지에 떨어지는 빛
    img = ImageChops.add(img, glow((W, H), (960, 560), 620, (255, 238, 214), 0.45))
    d = ImageDraw.Draw(img)
    softbox(d, 70, 260, 260, 340)
    softbox(d, 1590, 260, 260, 340)
    # 빛 줄기 (부드럽게)
    rays = Image.new("RGB", (W, H), (0, 0, 0))
    rd = ImageDraw.Draw(rays)
    rd.polygon([(320, 300), (900, 250), (900, 900), (320, 580)], fill=(40, 36, 30))
    rd.polygon([(1600, 300), (1020, 250), (1020, 900), (1600, 580)], fill=(40, 36, 30))
    img = ImageChops.add(img, rays.filter(ImageFilter.GaussianBlur(60)))
    grain(img, seed=11).save(OUT / "background_dark.png")


def title():
    W, H = 966, 300
    img = vgradient(W, H, (36, 34, 34), (22, 21, 21))
    img = ImageChops.add(img, glow((W, H), (W // 2, H // 2), 420, (255, 230, 200), 0.35))
    d = ImageDraw.Draw(img)
    # 필름 스트립 위·아래
    for y0 in (0, H - 34):
        d.rectangle([0, y0, W, y0 + 34], fill=(14, 13, 13))
        for x in range(18, W, 46):
            d.rounded_rectangle([x, y0 + 9, x + 24, y0 + 25], 3, fill=(225, 200, 165))
    # 렌즈 아이콘
    cx, cy = 230, H // 2
    d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], outline=(225, 200, 165), width=6)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(225, 200, 165))
    d.text((310, 82), "지담 스튜디오", font=font(78, True), fill=(250, 238, 220))
    d.text((314, 186), "일상을 작품으로 남기는 사진 스튜디오", font=font(28), fill=(215, 190, 155))
    grain(img, seed=12).save(OUT / "title.png")


def title_bilingual():
    """메인 타이틀 (966x300): 영문 세리프 + 한글 고딕 조화"""
    W, H = 966, 300
    img = vgradient(W, H, (36, 34, 34), (22, 21, 21))
    img = ImageChops.add(img, glow((W, H), (W // 2, H // 2), 440, (255, 228, 196), 0.32))
    d = ImageDraw.Draw(img)
    GOLD = (225, 200, 165)
    for y0 in (0, H - 30):  # 필름 띠
        d.rectangle([0, y0, W, y0 + 30], fill=(14, 13, 13))
        for x in range(18, W, 46):
            d.rounded_rectangle([x, y0 + 8, x + 24, y0 + 22], 3, fill=GOLD)
    serif = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 64)
    serif_i = ImageFont.truetype("C:/Windows/Fonts/georgiai.ttf", 22)
    small = ImageFont.truetype("C:/Windows/Fonts/segoeuil.ttf", 16)

    def center(y, text, f, fill, spacing=0):
        if spacing:
            widths = [d.textlength(ch, font=f) for ch in text]
            total = sum(widths) + spacing * (len(text) - 1)
            x = (W - total) / 2
            for ch, w in zip(text, widths):
                d.text((x, y), ch, font=f, fill=fill)
                x += w + spacing
        else:
            w = d.textlength(text, font=f)
            d.text(((W - w) / 2, y), text, font=f, fill=fill)

    center(46, "EST. 2026 · PHOTO STUDIO", small, (180, 160, 132), spacing=4)
    center(70, "JIDAM STUDIO", serif, (250, 238, 220), spacing=10)
    # 가운데 장식선 + 렌즈 점
    cy = 160
    d.line([(W / 2 - 200, cy), (W / 2 - 22, cy)], fill=GOLD, width=1)
    d.line([(W / 2 + 22, cy), (W / 2 + 200, cy)], fill=GOLD, width=1)
    d.ellipse([W / 2 - 10, cy - 10, W / 2 + 10, cy + 10], outline=GOLD, width=2)
    d.ellipse([W / 2 - 4, cy - 4, W / 2 + 4, cy + 4], fill=GOLD)
    center(178, "지담 스튜디오", font(34, True), GOLD, spacing=6)
    # 영문(이탤릭 세리프) + 한글(고딕)을 한 줄에 이어 쓰기
    en, sep, ko = "Everyday moments, made art.", "   ·   ", "일상을 작품으로"
    ko_f = font(20)
    total = d.textlength(en, font=serif_i) + d.textlength(sep, font=serif_i) + d.textlength(ko, font=ko_f)
    x = (W - total) / 2
    for text, f, dy in ((en, serif_i, 0), (sep, serif_i, 0), (ko, ko_f, 1)):
        d.text((x, 228 + dy), text, font=f, fill=(200, 182, 156))
        x += d.textlength(text, font=f)
    grain(img, seed=14).save(OUT / "title.png")


def profile():
    """프로필 이미지 500x500 (작게 줄여도 알아보도록 아이콘 크게, 글자 굵게)"""
    S = 500
    img = vgradient(S, S, (44, 40, 38), (22, 21, 21))
    img = ImageChops.add(img, glow((S, S), (S // 2, S // 2 - 30), 300, (255, 230, 200), 0.35))
    d = ImageDraw.Draw(img)
    # 필름 구멍 띠 (위·아래)
    for y0 in (0, S - 44):
        d.rectangle([0, y0, S, y0 + 44], fill=(14, 13, 13))
        for x in range(14, S, 52):
            d.rounded_rectangle([x, y0 + 12, x + 28, y0 + 32], 4, fill=(225, 200, 165))
    # 렌즈
    cx, cy = S // 2, 200
    d.ellipse([cx - 92, cy - 92, cx + 92, cy + 92], outline=(225, 200, 165), width=12)
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(225, 200, 165))
    # 글자
    f = font(64, True)
    w = d.textlength("지담 스튜디오", font=f)
    d.text(((S - w) / 2, 318), "지담 스튜디오", font=f, fill=(250, 238, 220))
    grain(img, seed=13).save(OUT / "profile.png")


if __name__ == "__main__":
    background(); title_bilingual(); profile()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

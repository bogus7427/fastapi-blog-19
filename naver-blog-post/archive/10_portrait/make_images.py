"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 인물 사진 팁)"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (60, 48, 52)
ACCENT = (220, 110, 100)
SKIN = (248, 214, 190)
HAIR = (60, 42, 36)
SHIRT = (110, 150, 200)
PANTS = (70, 70, 90)


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


def face(d, cx, cy, r, smile=True, shadow=False, skin=SKIN):
    """얼굴 (shadow=True면 눈 밑·코 밑 진한 그림자, 찡그린 눈)"""
    d.ellipse([cx - r, cy - r * 1.15, cx + r, cy + r * 1.15], fill=skin)
    d.chord([cx - r * 1.08, cy - r * 1.3, cx + r * 1.08, cy + r * 0.2], 180, 360, fill=HAIR)
    if shadow:
        for ex in (-0.38, 0.38):
            d.line([(cx + ex * r - r * 0.16, cy + r * 0.05), (cx + ex * r + r * 0.16, cy + r * 0.05)], fill=(60, 40, 40), width=max(2, int(r * 0.07)))
            d.ellipse([cx + ex * r - r * 0.22, cy + r * 0.12, cx + ex * r + r * 0.22, cy + r * 0.32], fill=(196, 150, 128))
        d.polygon([(cx - r * 0.12, cy + r * 0.45), (cx + r * 0.12, cy + r * 0.45), (cx, cy + r * 0.62)], fill=(180, 132, 112))
        d.line([(cx - r * 0.22, cy + r * 0.72), (cx + r * 0.22, cy + r * 0.72)], fill=(150, 80, 80), width=max(2, int(r * 0.06)))
    else:
        for ex in (-0.38, 0.38):
            d.ellipse([cx + ex * r - r * 0.1, cy - r * 0.02, cx + ex * r + r * 0.1, cy + r * 0.18], fill=(50, 36, 36))
            d.ellipse([cx + ex * r - r * 0.02, cy + r * 0.02, cx + ex * r + r * 0.04, cy + r * 0.08], fill=(255, 255, 255))
            d.ellipse([cx + ex * r - r * 0.26, cy + r * 0.3, cx + ex * r + r * 0.12, cy + r * 0.44], fill=(250, 180, 170))
        if smile:
            d.arc([cx - r * 0.3, cy + r * 0.38, cx + r * 0.3, cy + r * 0.78], 20, 160, fill=(190, 80, 80), width=max(2, int(r * 0.08)))


def full_body(d, cx, base, s=1.0, legs=1.0):
    """전신 인물. legs: 다리 길이 비율"""
    lh = 230 * s * legs
    top = base - lh
    d.rounded_rectangle([cx - 30 * s, top, cx - 4 * s, base], int(10 * s), fill=PANTS)
    d.rounded_rectangle([cx + 4 * s, top, cx + 30 * s, base], int(10 * s), fill=PANTS)
    d.rounded_rectangle([cx - 48 * s, top - 170 * s, cx + 48 * s, top + 10 * s], int(26 * s), fill=SHIRT)
    face(d, cx, top - 215 * s, 40 * s)


# 01 서론: 친구를 찍어 주는 장면
def intro():
    img = gradient(W, H, (252, 236, 226), (240, 220, 210))
    d = ImageDraw.Draw(img)
    # 배경 화분/벽
    d.rectangle([0, 600, W, H], fill=(226, 200, 186))
    # 찍히는 친구 (오른쪽)
    full_body(d, 880, 640, 1.2)
    # 찍는 사람의 손 + 폰 (왼쪽 앞)
    px, py, pw, ph = 170, 180, 300, 520
    d.rounded_rectangle([px, py, px + pw, py + ph], 40, fill=(36, 36, 44))
    screen = gradient(pw - 30, ph - 50, (252, 236, 226), (240, 220, 210))
    sd = ImageDraw.Draw(screen)
    sd.rectangle([0, ph - 160, pw, ph], fill=(226, 200, 186))
    full_body(sd, (pw - 30) / 2, ph - 90, 0.62)
    img.paste(screen, (px + 15, py + 25))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([px - 50, py + 380, px + 40, py + 470], 40, fill=SKIN)
    d.rounded_rectangle([px + pw - 20, py + 400, px + pw + 70, py + 480], 40, fill=SKIN)
    d.rounded_rectangle([40, 40, 470, 112], 18, fill=(255, 255, 255))
    d.text((64, 52), "\"나 좀 찍어 줘!\"", font=font(38, True), fill=INK)
    noise(img, seed=2).save(OUT / "01_intro.png")


# 02 본론1: 강한 햇빛 vs 그늘
def body1():
    img = gradient(W, H, (246, 240, 236), (232, 222, 216))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "빛: 얼굴에 그늘진 부드러운 빛 찾기", font(42, True), INK)
    pw, ph = 480, 380
    for i, (title, sub, shadow, sky) in enumerate((
            ("한낮 직사광선", "그림자 진하고 눈이 부셔요", True, ((120, 180, 235), (190, 220, 245))),
            ("그늘 + 밝은 배경", "피부가 부드럽고 눈이 반짝", False, ((214, 230, 220), (236, 242, 236))))):
        x = 90 + i * (pw + 50)
        pic = gradient(pw, ph, *sky)
        pd = ImageDraw.Draw(pic)
        if shadow:
            pd.ellipse([pw - 110, 30, pw - 40, 100], fill=(255, 248, 200))
        else:
            pd.rectangle([0, 0, pw, 70], fill=(90, 130, 100))  # 나무 그늘
        pd.rounded_rectangle([pw / 2 - 110, ph - 120, pw / 2 + 110, ph + 40], 60, fill=SHIRT)
        face(pd, pw / 2, ph / 2 + 10, 95, smile=not shadow, shadow=shadow,
             skin=(250, 220, 196) if shadow else (248, 218, 198))
        d.rounded_rectangle([x - 10, 120, x + pw + 10, 120 + ph + 150], 20, fill=(255, 255, 255))
        img.paste(pic, (x, 130))
        d = ImageDraw.Draw(img)
        center_text(d, 130 + ph + 22, title, font(32, True), INK, x0=x, width=pw)
        center_text(d, 130 + ph + 70, sub, font(24), ACCENT if not shadow else (130, 120, 130), x0=x, width=pw)
    center_text(d, H - 60, "역광이면 얼굴을 길게 눌러 노출 맞추기", font(26, True), (120, 100, 104))
    noise(img, seed=3).save(OUT / "02_body1.png")


# 03 본론2: 높이와 거리
def body2():
    img = gradient(W, H, (246, 240, 236), (232, 222, 216))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "높이와 거리: 휴대폰은 낮게, 줌 대신 다가가기", font(40, True), INK)
    cw, ch = 340, 470
    xs = [70, 430, 790]
    titles = [("눈높이에서 내려다보기", "머리 크고 다리 짧게", (130, 120, 130)),
              ("허리 높이에서 올려 찍기", "발끝은 화면 아래 끝에", ACCENT),
              ("얼굴은 눈높이 + 2배", "이목구비가 자연스럽게", ACCENT)]
    for i, x in enumerate(xs):
        pic = gradient(cw, ch, (236, 228, 236), (220, 212, 222))
        pd = ImageDraw.Draw(pic)
        pd.rectangle([0, ch - 60, cw, ch], fill=(200, 190, 196))
        if i == 0:
            full_body(pd, cw / 2, ch - 70, 0.95, legs=0.65)
            pd.ellipse([cw / 2 - 60, 70, cw / 2 + 60, 190], outline=(255, 255, 255), width=0)
        elif i == 1:
            full_body(pd, cw / 2, ch - 4, 0.68, legs=1.15)
        else:
            pd.rounded_rectangle([cw / 2 - 150, ch - 160, cw / 2 + 150, ch + 60], 80, fill=SHIRT)
            face(pd, cw / 2, ch / 2 - 10, 110)
        d.rounded_rectangle([x - 10, 110, x + cw + 10, 110 + ch + 150], 20, fill=(255, 255, 255))
        img.paste(pic, (x, 120))
        d = ImageDraw.Draw(img)
        center_text(d, 120 + ch + 18, titles[i][0], font(26, True), INK, x0=x, width=cw)
        center_text(d, 120 + ch + 62, titles[i][1], font(22), titles[i][2], x0=x, width=cw)
    # X / O 표시
    d.line([(xs[0] + 20, 140), (xs[0] + 70, 190)], fill=(150, 140, 150), width=8)
    d.line([(xs[0] + 70, 140), (xs[0] + 20, 190)], fill=(150, 140, 150), width=8)
    for x in xs[1:]:
        d.ellipse([x + 20, 140, x + 72, 192], outline=ACCENT, width=8)
    noise(img, seed=4).save(OUT / "03_body2.png")


# 04 본론3: 움직임 연속 컷
def body3():
    img = gradient(W, H, (246, 240, 236), (232, 222, 216))
    d = ImageDraw.Draw(img)
    center_text(d, 36, "표정과 동작: 포즈 대신 움직임을 주문하기", font(40, True), INK)
    cw, ch = 250, 330
    actions = ["걸어오기", "머리 넘기기", "뒤돌아보기", "커피 한 모금"]
    x0 = (W - cw * 4 - 25 * 3) / 2
    for i, name in enumerate(actions):
        x = int(x0 + i * (cw + 25))
        pic = gradient(cw, ch, (240, 226, 216), (222, 206, 196))
        pd = ImageDraw.Draw(pic)
        cx, cy = cw / 2, 140
        pd.rounded_rectangle([cx - 70, cy + 70, cx + 70, ch + 40], 50, fill=SHIRT)
        face(pd, cx, cy, 62)
        if i == 0:  # 걷기: 흔들림 선
            for k in range(3):
                pd.line([(14, 200 + k * 30), (54, 200 + k * 30)], fill=(200, 180, 180), width=4)
        elif i == 1:  # 머리 넘기는 손
            pd.rounded_rectangle([cx + 40, cy - 90, cx + 90, cy - 20], 24, fill=SKIN)
            pd.arc([cx + 10, cy - 130, cx + 120, cy - 40], 200, 330, fill=HAIR, width=8)
        elif i == 2:  # 뒤돌아보기: 어깨 비틀기
            pd.rounded_rectangle([cx - 110, cy + 80, cx + 20, ch + 40], 50, fill=(90, 130, 180))
        else:  # 커피잔
            pd.rounded_rectangle([cx + 30, cy + 70, cx + 90, cy + 140], 12, fill=(250, 250, 248))
            pd.rounded_rectangle([cx + 10, cy + 100, cx + 50, cy + 150], 20, fill=SKIN)
        d.rectangle([x - 8, 120, x + cw + 8, 120 + ch + 70], fill=(255, 255, 255))
        img.paste(pic, (x, 128))
        d = ImageDraw.Draw(img)
        center_text(d, 128 + ch + 14, name, font(26, True), INK, x0=x, width=cw)
    # 연속 촬영 + 대화 말풍선
    d.rounded_rectangle([140, 600, 560, 680], 40, fill=ACCENT)
    center_text(d, 618, "셔터 길게 → 연속 촬영", font(30, True), (255, 255, 255), x0=140, width=420)
    d.rounded_rectangle([640, 600, 1060, 680], 30, fill=(255, 255, 255))
    d.polygon([(680, 678), (720, 678), (690, 710)], fill=(255, 255, 255))
    center_text(d, 618, "\"요즘 제일 맛있던 거 뭐야?\"", font(26, True), INK, x0=640, width=420)
    noise(img, seed=5).save(OUT / "04_body3.png")


# 05 결론: 브랜드
def outro():
    img = gradient(W, H, (42, 36, 38), (22, 20, 22))
    d = ImageDraw.Draw(img)
    for y0 in (0, H - 60):
        d.rectangle([0, y0, W, y0 + 60], fill=(14, 13, 13))
        for x in range(20, W, 60):
            d.rounded_rectangle([x, y0 + 17, x + 32, y0 + 43], 4, fill=(225, 200, 165))
    # 인물 아이콘 (선)
    cx = W // 2
    d.ellipse([cx - 40, 130, cx + 40, 210], outline=(225, 200, 165), width=7)
    d.arc([cx - 80, 220, cx + 80, 360], 180, 360, fill=(225, 200, 165), width=7)
    center_text(d, 320, "지담 스튜디오", font(100, True), (250, 238, 220))
    center_text(d, 470, "일상을 작품으로 남기는 사진 스튜디오", font(36), (225, 200, 165))
    center_text(d, 535, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (205, 180, 150))
    noise(img, seed=6).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

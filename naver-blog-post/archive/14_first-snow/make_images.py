"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 첫눈 오는 날 감성 사진 갤러리)"""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (40, 48, 60)


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


def snowflake(d, cx, cy, r, color=(255, 255, 255), width=2):
    for i in range(6):
        ang = math.radians(i * 60)
        x2 = cx + r * math.cos(ang)
        y2 = cy + r * math.sin(ang)
        d.line([(cx, cy), (x2, y2)], fill=color, width=width)
        # 곁가지
        bx1 = cx + (r * 0.6) * math.cos(ang)
        by1 = cy + (r * 0.6) * math.sin(ang)
        for d_ang in (30, -30):
            bx2 = bx1 + (r * 0.3) * math.cos(ang + math.radians(d_ang))
            by2 = by1 + (r * 0.3) * math.sin(ang + math.radians(d_ang))
            d.line([(bx1, by1), (bx2, by2)], fill=color, width=width)


# 01 서론: 첫눈 흩날리는 밤거리 풍경과 스마트폰 촬영
def intro():
    # 밤하늘 그라디언트 (깊은 네이비 -> 은은한 보랏빛 도는 밤)
    img = gradient(W, H, (20, 26, 42), (48, 56, 80))
    d = ImageDraw.Draw(img)

    # 지면 눈 쌓임
    d.rectangle([0, H - 180, W, H], fill=(225, 235, 248))
    d.ellipse([-100, H - 240, 700, H - 100], fill=(240, 245, 255))
    d.ellipse([500, H - 250, W + 200, H - 90], fill=(235, 242, 252))

    # 가로등 기둥 및 갓
    lx, ly = 360, 220
    d.line([(lx, ly), (lx, H - 180)], fill=(70, 75, 85), width=14)
    d.polygon([(lx - 70, ly), (lx + 70, ly), (lx + 50, ly - 35), (lx - 50, ly - 35)], fill=(50, 55, 65))

    # 가로등 빛 번짐 (부드러운 조명 원뿔)
    cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cone)
    cd.polygon([(lx, ly), (lx - 280, H - 180), (lx + 280, H - 180)], fill=(255, 230, 160, 120))
    cd.ellipse([lx - 120, ly - 30, lx + 120, ly + 210], fill=(255, 245, 190, 180))
    cone = cone.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img.convert("RGBA"), cone).convert("RGB")
    d = ImageDraw.Draw(img)

    # 흩날리는 눈송이들 (크고 작은 원들)
    rnd = random.Random(42)
    snow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(snow)
    for _ in range(250):
        sx = rnd.randint(0, W)
        sy = rnd.randint(0, H - 100)
        sr = rnd.randint(2, 9)
        alpha = rnd.randint(140, 240)
        sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255, alpha))
    snow_blur = snow.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img.convert("RGBA"), snow_blur)
    img = Image.alpha_composite(img, snow).convert("RGB")
    d = ImageDraw.Draw(img)

    # 스마트폰 뷰파인더 일러스트 (오른쪽 전면)
    px, py, pw, ph = 780, 280, 280, 460
    d.rounded_rectangle([px, py, px + pw, py + ph], 32, fill=(28, 30, 36), outline=(90, 95, 105), width=6)
    # 화면 안쪽
    d.rounded_rectangle([px + 12, py + 16, px + pw - 12, py + ph - 16], 20, fill=(30, 38, 56))
    # 폰 화면 안 가로등 불빛과 눈
    d.ellipse([px + pw // 2 - 40, py + 70, px + pw // 2 + 40, py + 150], fill=(255, 230, 150))
    for _ in range(40):
        fx = rnd.randint(px + 20, px + pw - 20)
        fy = rnd.randint(py + 40, py + ph - 80)
        fr = rnd.randint(2, 5)
        d.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=(255, 255, 255))
    # 폰 촬영 셔터 버튼
    d.ellipse([px + pw // 2 - 24, py + ph - 65, px + pw // 2 + 24, py + ph - 17], fill=(255, 255, 255))

    # 타이틀 카드
    label(d, 60, 60, "감성 사진 갤러리 · 첫눈 오는 날", 34, bg=(255, 255, 255), fg=(30, 40, 60))
    label(d, 60, 140, "스마트폰으로 담는 겨울 감성 3가지 장면", 24, bg=(40, 52, 75), fg=(255, 255, 255))

    noise(img, seed=101).save(OUT / "01_intro.png")


# 02 본론1: 가로등 불빛 아래 흩날리는 밤눈
def body1():
    img = gradient(W, H, (14, 18, 30), (28, 34, 52))
    d = ImageDraw.Draw(img)

    # 중앙 상단 가로등
    gx, gy = 600, 140
    d.line([(gx, 0), (gx, gy)], fill=(80, 85, 95), width=16)
    d.polygon([(gx - 90, gy), (gx + 90, gy), (gx + 60, gy - 40), (gx - 60, gy - 40)], fill=(55, 60, 70))

    # 환한 역광 조명과 빛 번짐
    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    ld.polygon([(gx, gy), (gx - 450, H), (gx + 450, H)], fill=(255, 220, 140, 90))
    ld.ellipse([gx - 180, gy - 20, gx + 180, gy + 340], fill=(255, 240, 180, 160))
    ld.ellipse([gx - 80, gy + 10, gx + 80, gy + 170], fill=(255, 255, 230, 230))
    light = light.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img.convert("RGBA"), light).convert("RGB")

    # 빛 속에서 반짝이는 눈송이들 (역광 반사 림라이트 효과)
    snow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(snow)
    rnd = random.Random(77)
    for _ in range(320):
        sx = rnd.randint(150, W - 150)
        sy = rnd.randint(gy, H)
        dist_to_center = abs(sx - gx)
        # 빛 중심일수록 눈이 더 환하고 큼
        if dist_to_center < 350:
            sr = rnd.randint(4, 12)
            alpha = rnd.randint(180, 255)
            # 빛 받는 황금빛/화이트 눈
            sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 250, 220, alpha))
        else:
            sr = rnd.randint(2, 6)
            alpha = rnd.randint(100, 180)
            sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(230, 240, 255, alpha))

    snow_b = snow.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img.convert("RGBA"), snow_b)
    img = Image.alpha_composite(img, snow).convert("RGB")
    d = ImageDraw.Draw(img)

    label(d, 50, 60, "장면 하나 · 가로등 불빛 아래 흩날리는 밤눈", 30)
    label(d, 50, 135, "핵심 팁: 역광 조명 + 어두운 밤하늘 배경 + 노출 -0.5", 22, bg=(30, 36, 50), fg=(255, 255, 255))

    # 하단 팁 카드 박스
    d.rounded_rectangle([50, H - 150, W - 50, H - 40], 20, fill=(25, 32, 48), outline=(70, 85, 115), width=2)
    d.text((80, H - 128), "✔ 조명을 등 뒤에 두지 말고, 조명과 카메라 사이에 눈송이가 오도록 역광 각도 잡기", font=font(22), fill=(240, 245, 255))
    d.text((80, H - 85), "✔ 어두운 배경에 초점을 맞추고 밝기 슬라이더를 살짝 낮춰 반짝이는 눈송이만 강조", font=font(22), fill=(255, 220, 150))

    noise(img, seed=102).save(OUT / "02_body1.png")


# 03 본론2: 나뭇가지와 벤치 위 소복한 눈의 디테일
def body2():
    # 차분하고 깨끗한 겨울 아침 배경 그라디언트 (쿨 그레이 -> 소프트 아이스)
    img = gradient(W, H, (205, 215, 228), (230, 238, 246))
    d = ImageDraw.Draw(img)

    # 배경 아웃포커싱 나무 실루엣
    bg_tree = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    btd = ImageDraw.Draw(bg_tree)
    for bx in (200, 850, 1050):
        btd.line([(bx, 100), (bx, H)], fill=(160, 175, 195, 160), width=28)
        btd.line([(bx, 300), (bx - 120, 200)], fill=(160, 175, 195, 140), width=14)
        btd.line([(bx, 360), (bx + 140, 240)], fill=(160, 175, 195, 140), width=14)
    bg_tree = bg_tree.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img.convert("RGBA"), bg_tree).convert("RGB")
    d = ImageDraw.Draw(img)

    # 전경 메인 나뭇가지 (짙은 고동색)
    branch_pts = [(100, 480), (350, 450), (650, 400), (950, 360), (1150, 320)]
    for i in range(len(branch_pts) - 1):
        d.line([branch_pts[i], branch_pts[i + 1]], fill=(65, 50, 42), width=32)

    # 가지 갈래
    d.line([(500, 420), (600, 280), (750, 220)], fill=(65, 50, 42), width=18)
    d.line([(780, 380), (900, 520)], fill=(65, 50, 42), width=14)

    # 나뭇가지 위에 소복이 얹힌 새하얀 눈 (부드러운 곡선 캡슐들)
    snow_caps = [
        (100, 435, 360, 445),
        (340, 405, 660, 415),
        (640, 355, 960, 370),
        (940, 310, 1150, 335),
        (520, 260, 760, 235),
    ]
    for x1, y1, x2, y2 in snow_caps:
        # 그림자 층
        d.line([(x1, y1 + 10), (x2, y2 + 10)], fill=(195, 210, 230), width=36)
        # 흰 눈 층
        d.line([(x1, y1), (x2, y2)], fill=(255, 255, 255), width=32)
        # 눈 둥근 덩어리들
        steps = 8
        for s in range(steps):
            tx = x1 + (x2 - x1) * (s / steps)
            ty = y1 + (y2 - y1) * (s / steps) - 8
            d.ellipse([tx - 18, ty - 14, tx + 18, ty + 14], fill=(255, 255, 255))

    # 포인트 컬러: 빨간 겨울 산수유/남천 열매들 (눈 속에 쏙 박힌 열매)
    berries = [(420, 460), (450, 480), (480, 450), (720, 420), (750, 440), (880, 540), (910, 530)]
    for bx, by in berries:
        d.ellipse([bx - 14, by - 14, bx + 14, by + 14], fill=(210, 45, 45))
        d.ellipse([bx - 6, by - 8, bx + 2, by], fill=(250, 140, 140))  # 하이라이트
        # 열매 위 살짝 얹힌 눈
        d.ellipse([bx - 8, by - 16, bx + 8, by - 8], fill=(255, 255, 255))

    label(d, 50, 60, "장면 둘 · 소복이 쌓인 눈의 포근한 질감", 30)
    label(d, 50, 135, "핵심 팁: 2~3배 망원 렌즈 + 노출(+0.5~+1.0) 올려 뽀얀 순백색 살리기", 22, bg=(60, 70, 85), fg=(255, 255, 255))

    # 하단 팁 카드
    d.rounded_rectangle([50, H - 150, W - 50, H - 40], 20, fill=(255, 255, 255), outline=(180, 195, 215), width=2)
    d.text((80, H - 128), "✔ 카메라는 눈을 너무 밝다고 착각해 어둡게 찍으므로, 노출 슬라이더를 꼭 올려주기", font=font(22), fill=(45, 55, 70))
    d.text((80, H - 85), "✔ 빨간 열매나 벤치 목재처럼 흰 눈과 대비되는 포인트 색상을 함께 담으면 생기 UP", font=font(22), fill=(190, 40, 40))

    noise(img, seed=103).save(OUT / "03_body2.png")


# 04 본론3: 눈 덮인 골목길의 발자국과 따뜻한 창가 온기
def body3():
    # 차가운 눈길과 따뜻한 건물의 대비 배경
    img = gradient(W, H, (140, 160, 185), (200, 215, 235))
    d = ImageDraw.Draw(img)

    # 우측 건물 벽 (따뜻한 벽돌 브라운)
    d.polygon([(720, 0), (W, 0), (W, H), (640, H)], fill=(120, 85, 75))

    # 건물 창문 (따뜻한 오렌지 3000K 조명)
    wx, wy, ww, wh = 780, 160, 320, 260
    d.rectangle([wx - 10, wy - 10, wx + ww + 10, wy + wh + 10], fill=(70, 50, 42))  # 창틀
    d.rectangle([wx, wy, wx + ww, wy + wh], fill=(255, 175, 75))  # 창문 불빛
    d.line([(wx + ww // 2, wy), (wx + ww // 2, wy + wh)], fill=(70, 50, 42), width=10)
    d.line([(wx, wy + wh // 2), (wx + ww, wy + wh // 2)], fill=(70, 50, 42), width=10)

    # 창가에서 눈길로 퍼지는 부드러운 주황빛 온기
    warm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(warm)
    wd.ellipse([wx - 250, wy - 50, wx + ww + 100, wy + wh + 350], fill=(255, 180, 80, 120))
    warm = warm.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img.convert("RGBA"), warm).convert("RGB")
    d = ImageDraw.Draw(img)

    # 눈 쌓인 골목길 (좌측 및 중앙 바닥)
    d.polygon([(0, 300), (720, 300), (640, H), (0, H)], fill=(225, 235, 248))

    # 골목길 원근감 선 (벽과 바닥 경계 눈 둔덕)
    d.line([(720, 300), (640, H)], fill=(190, 205, 225), width=8)

    # 뽀드득 첫 발자국들 (하단에서 창가/골목 안쪽으로 이어지는 유도선)
    # 원근감: 아래쪽은 크고 짙으며, 멀어질수록 작고 촘촘해짐
    footsteps = [
        (220, 720, 32, 54, 15),
        (300, 640, 28, 48, -10),
        (360, 570, 24, 42, 12),
        (430, 500, 20, 36, -8),
        (480, 440, 17, 30, 10),
        (530, 390, 14, 25, -5),
        (570, 345, 11, 20, 8),
        (610, 310, 8, 15, -4),
    ]
    for fx, fy, fw, fh, fang in footsteps:
        # 발자국 그림자 웅덩이
        d.ellipse([fx - fw, fy - fh // 2, fx + fw, fy + fh // 2], fill=(165, 185, 210))
        # 깊이감 안쪽 음영
        d.ellipse([fx - fw + 4, fy - fh // 2 + 3, fx + fw - 4, fy + fh // 2 - 3], fill=(145, 165, 195))

    # 창문 처마 위에 얹힌 눈
    d.rounded_rectangle([wx - 20, wy - 28, wx + ww + 20, wy - 2], 12, fill=(255, 255, 255))

    label(d, 50, 60, "장면 셋 · 눈 덮인 골목길과 따뜻한 창가", 30)
    label(d, 50, 135, "핵심 팁: 발자국 유도선 구도 + 로우 앵글 + 차가움/따뜻함 색감 대비", 22, bg=(45, 55, 70), fg=(255, 255, 255))

    # 하단 팁 카드
    d.rounded_rectangle([50, H - 150, W - 50, H - 40], 20, fill=(28, 34, 46), outline=(90, 105, 130), width=2)
    d.text((80, H - 128), "✔ 발자국을 화면 하단부터 시작해 안쪽으로 이어지는 유도선(Leading Line)으로 배치", font=font(22), fill=(240, 245, 255))
    d.text((80, H - 85), "✔ 차가운 하얀 눈과 창가에서 흘러나오는 주황빛 조명(3000K)을 한 프레임에 담아 온기 극대화", font=font(22), fill=(255, 195, 110))

    noise(img, seed=104).save(OUT / "04_body3.png")


# 05 결론: 지담 스튜디오 아웃트로 카드
def outro():
    img = gradient(W, H, (26, 32, 46), (16, 20, 30))
    d = ImageDraw.Draw(img)

    # 상/하단 필름 퍼포레이션 디자인
    for y0 in (0, H - 60):
        d.rectangle([0, y0, W, y0 + 60], fill=(12, 15, 22))
        for x in range(20, W, 60):
            d.rounded_rectangle([x, y0 + 17, x + 32, y0 + 43], 4, fill=(180, 200, 230))

    # 겨울 눈꽃 심볼 그래픽
    snowflake(d, W // 2, 230, 75, color=(200, 225, 255), width=3)
    snowflake(d, W // 2, 230, 40, color=(255, 255, 255), width=3)

    center_text(d, 330, "지담 스튜디오", font(96, True), (245, 250, 255))
    center_text(d, 470, "일상을 작품으로 남기는 사진 스튜디오", font(34), (200, 220, 245))
    center_text(d, 530, "스마트폰 하나로도 감성 사진은 충분하다", font(28, True), (170, 195, 230))

    # 하단 링크 안내 문구
    center_text(d, 630, "공감과 댓글 · 이웃추가는 지담 스튜디오에 큰 힘이 됩니다", font(22), (130, 150, 180))

    noise(img, seed=105).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro()
    body1()
    body2()
    body3()
    outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

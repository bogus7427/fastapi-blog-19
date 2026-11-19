"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다. (주제: 북촌 한옥마을 골목 스냅 촬영 후기)"""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
INK = (45, 42, 38)


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


# 한옥 기와 지붕 곡선 그리기
def draw_roof(d, x1, y1, x2, y2, color=(45, 48, 54), curve=25):
    pts = [(x1, y1)]
    steps = 20
    for i in range(steps + 1):
        t = i / steps
        bx = x1 + (x2 - x1) * t
        # 아래로 살짝 휘어졌다가 끝이 들리는 기와 처마 곡선
        by = y1 + (y2 - y1) * t + curve * math.sin(t * math.pi)
        pts.append((bx, by))
    pts.append((x2, y2 + 40))
    pts.append((x1, y1 + 40))
    d.polygon(pts, fill=color)


# 01 서론: 북촌 한옥마을 골목길 풍경과 스마트폰 촬영
def intro():
    # 맑고 차분한 겨울 오후 하늘 (소프트 스카이블루 -> 따스한 햇살빛)
    img = gradient(W, H, (145, 175, 205), (225, 215, 195))
    d = ImageDraw.Draw(img)

    # 먼 산/도시 실루엣
    d.polygon([(0, 320), (300, 260), (700, 310), (1000, 250), (W, 300), (W, 450), (0, 450)], fill=(120, 140, 160))

    # 골목길 바닥 (오르막 돌길)
    d.polygon([(350, 360), (850, 360), (W + 200, H), (-200, H)], fill=(185, 175, 160))
    # 바닥 돌길 텍스처
    for y in range(400, H, 35):
        w_offset = int((y - 360) * 0.8)
        d.line([(600 - w_offset, y), (600 + w_offset, y)], fill=(160, 150, 138), width=3)

    # 좌측 한옥 기와와 돌담
    d.polygon([(0, 180), (450, 260), (450, H), (0, H)], fill=(155, 115, 90))  # 벽면
    draw_roof(d, -50, 160, 480, 250, (50, 52, 58), curve=30)
    # 우측 한옥 기와와 벽면
    d.polygon([(750, 260), (W, 160), (W, H), (750, H)], fill=(145, 105, 82))
    draw_roof(d, 720, 250, W + 50, 140, (45, 48, 54), curve=30)

    # 골목 사이로 쏟아지는 따스한 햇살
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.polygon([(600, 180), (100, H), (1100, H)], fill=(255, 240, 190, 75))
    sun = sun.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img.convert("RGBA"), sun).convert("RGB")
    d = ImageDraw.Draw(img)

    # 스마트폰 뷰파인더 일러스트 (오른쪽 전면)
    px, py, pw, ph = 780, 300, 270, 440
    d.rounded_rectangle([px, py, px + pw, py + ph], 28, fill=(28, 30, 34), outline=(85, 90, 98), width=6)
    # 폰 화면 안 기와 곡선
    d.rounded_rectangle([px + 12, py + 14, px + pw - 12, py + ph - 14], 18, fill=(160, 185, 210))
    # 폰 안 기와 실루엣
    d.polygon([(px + 12, py + 120), (px + pw - 12, py + 180), (px + pw - 12, py + ph - 14), (px + 12, py + ph - 14)], fill=(65, 50, 42))
    draw_roof(d, px + 12, py + 100, px + pw - 12, py + 170, (40, 44, 50), curve=15)
    # 셔터 버튼
    d.ellipse([px + pw // 2 - 22, py + ph - 60, px + pw // 2 + 22, py + ph - 16], fill=(255, 255, 255))

    # 타이틀 카드
    label(d, 60, 60, "촬영 후기 · 북촌 한옥마을 골목 스냅", 34, bg=(255, 255, 255), fg=(50, 42, 36))
    label(d, 60, 140, "스마트폰 하나로 고즈넉한 한국의 감성 담기", 24, bg=(75, 60, 52), fg=(255, 255, 255))

    noise(img, seed=201).save(OUT / "01_intro.png")


# 02 본론1: 겹겹이 이어지는 처마선과 하늘의 여백
def body1():
    # 맑은 겨울 하늘 (코발트 블루 -> 스카이블루)
    img = gradient(W, H, (55, 115, 175), (145, 185, 220))
    d = ImageDraw.Draw(img)

    # 대각선으로 뻗어나오는 한옥 처마 (좌측 하단에서 우측 상단으로)
    pts_left = [
        (-40, 480), (150, 420), (380, 330), (620, 220), (740, 140),
        (760, 170), (640, 260), (400, 380), (160, 490), (-40, 570)
    ]
    # 기와 처마 밑 서까래 (목재 갈색)
    d.polygon([(-40, 520), (740, 180), (740, 320), (-40, 720)], fill=(125, 75, 48))
    # 서까래 살
    for x in range(0, 700, 45):
        y_top = int(480 - x * 0.45)
        d.line([(x, y_top), (x - 40, y_top + 160)], fill=(95, 55, 35), width=8)

    # 기와 암키와·수키와 입체감
    d.polygon([(-50, 470), (750, 130), (780, 150), (720, 220), (-50, 560)], fill=(40, 44, 52))
    # 처마 끝 날렵한 곡선 반전
    d.polygon([(720, 130), (780, 110), (750, 160)], fill=(32, 35, 42))

    # 반대편 우측 한옥 처마 실루엣 (겹겹의 깊이감)
    d.polygon([(820, 0), (W + 20, 0), (W + 20, 380), (820, 240)], fill=(50, 54, 62))
    draw_roof(d, 800, 230, W + 20, 370, (35, 38, 45), curve=15)

    # 하늘 여백 강조 가이드 선 (3분의 1 황금분할선)
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    gd.line([(W // 3, 0), (W // 3, H)], fill=(255, 255, 255, 70), width=2)
    gd.line([(2 * W // 3, 0), (2 * W // 3, H)], fill=(255, 255, 255, 70), width=2)
    gd.line([(0, H // 3), (W, H // 3)], fill=(255, 255, 255, 70), width=2)
    # 처마 꼭짓점 강조 원
    gd.ellipse([730, 80, 810, 160], outline=(255, 225, 120, 220), width=4)
    img = Image.alpha_composite(img.convert("RGBA"), grid).convert("RGB")
    d = ImageDraw.Draw(img)

    label(d, 50, 60, "첫 번째 컷 · 겹겹이 이어지는 처마선과 하늘 여백", 30)
    label(d, 50, 135, "핵심 팁: 스마트폰 로우 앵글 + 격자선(그리드) 켜고 3분의 1 하늘 여백 남기기", 22, bg=(40, 50, 65), fg=(255, 255, 255))

    # 하단 팁 박스
    d.rounded_rectangle([50, H - 150, W - 50, H - 40], 20, fill=(28, 35, 48), outline=(80, 100, 130), width=2)
    d.text((80, H - 128), "✔ 스마트폰을 거꾸로 들고 처마를 올려다보면 날렵한 곡선미와 웅장함 극대화", font=font(22), fill=(240, 245, 255))
    d.text((80, H - 85), "✔ 프레임 전체를 채우기보다 푸른 겨울 하늘을 3분의 1 여백으로 두어 단아한 숨통 틔우기", font=font(22), fill=(255, 220, 130))

    noise(img, seed=202).save(OUT / "02_body1.png")


# 03 본론2: 돌담길 위로 길게 드리운 오후의 빛과 그림자
def body2():
    # 따스한 골든아워 빛 그라디언트
    img = gradient(W, H, (230, 205, 175), (195, 160, 130))
    d = ImageDraw.Draw(img)

    # 좌측 돌담 벽면 (원근감으로 안쪽으로 좁아짐)
    wall_pts = [(0, 0), (620, 220), (620, H), (0, H)]
    d.polygon(wall_pts, fill=(155, 140, 125))

    # 돌담 상단 기와 지붕
    draw_roof(d, -30, 0, 640, 220, (55, 58, 65), curve=10)

    # 돌담 석재 패턴 및 음영
    rnd = random.Random(88)
    for row in range(12):
        y_pos = int(120 + row * 55)
        for col in range(8):
            x_pos = int(col * 75 - (row * 15))
            if x_pos < 580:
                stone_w = rnd.randint(55, 80)
                stone_h = rnd.randint(35, 48)
                # 빛 받는 면과 그림자 면
                d.rounded_rectangle([x_pos, y_pos, x_pos + stone_w, y_pos + stone_h], 8,
                                    fill=(175 + rnd.randint(-15, 20), 160 + rnd.randint(-15, 20), 145 + rnd.randint(-15, 20)),
                                    outline=(115, 100, 85), width=2)

    # 우측 바닥 길과 벽돌 바닥
    d.polygon([(620, 220), (W, 140), (W, H), (620, H)], fill=(210, 190, 165))

    # 강렬한 오후 3시 낮은 햇살과 긴 그림자 효과
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shd = ImageDraw.Draw(shadow)
    # 돌담에서 바닥으로 길게 뻗은 대각선 그림자
    shd.polygon([(180, H), (620, 220), (780, 220), (520, H)], fill=(45, 38, 35, 140))
    shd.polygon([(360, H), (620, 220), (880, 220), (700, H)], fill=(45, 38, 35, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    d = ImageDraw.Draw(img)

    label(d, 50, 60, "두 번째 컷 · 돌담길 위로 드리운 빛과 그림자", 30)
    label(d, 50, 135, "핵심 팁: 2배 망원 렌즈로 소실점 구도 압축 + 노출 살짝 낮춰 깊은 명암 살리기", 22, bg=(70, 58, 48), fg=(255, 255, 255))

    # 하단 팁 카드
    d.rounded_rectangle([50, H - 150, W - 50, H - 40], 20, fill=(35, 30, 26), outline=(95, 80, 68), width=2)
    d.text((80, H - 128), "✔ 오후 3~4시 비스듬히 들어오는 사광(Side Light)을 활용해 석재 돌담의 거친 결 강조", font=font(22), fill=(245, 240, 230))
    d.text((80, H - 85), "✔ 밝은 곳을 터치하고 노출 슬라이더를 내려 어둠을 깊게 누르면 영화 스틸컷 같은 분위기", font=font(22), fill=(255, 205, 130))

    noise(img, seed=203).save(OUT / "03_body2.png")


# 04 본론3: 창호문 너머로 번지는 온기와 작은 디테일 스냅
def body3():
    # 고즈넉한 전통 목재 벽면 배경
    img = gradient(W, H, (115, 80, 60), (75, 52, 40))
    d = ImageDraw.Draw(img)

    # 전통 창호문 프레임 (우측에 위치)
    wx, wy, ww, wh = 380, 120, 580, 540
    # 문틀 목재
    d.rectangle([wx - 24, wy - 24, wx + ww + 24, wy + wh + 24], fill=(62, 42, 32), outline=(42, 28, 20), width=4)
    # 한지 창호지 바탕 (은은한 주황빛 조명이 투과되는 따스한 빛)
    d.rectangle([wx, wy, wx + ww, wy + wh], fill=(255, 220, 145))

    # 부드러운 실내 온기 번짐 (가우시안 블러)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gld = ImageDraw.Draw(glow)
    gld.rectangle([wx - 50, wy - 50, wx + ww + 50, wy + wh + 50], fill=(255, 195, 90, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)

    # 창호문 격자살 (아자살/세살 문양)
    grid_cols = 6
    grid_rows = 7
    cw = ww / grid_cols
    rh = wh / grid_rows
    for c in range(1, grid_cols):
        gx = wx + c * cw
        d.line([(gx, wy), (gx, wy + wh)], fill=(85, 55, 38), width=8)
    for r in range(1, grid_rows):
        gy = wy + r * rh
        d.line([(wx, gy), (wx + ww, gy)], fill=(85, 55, 38), width=8)

    # 좌측 전통 놋쇠 문고리 (클로즈업 초점 포인트)
    kx, ky = 260, 420
    # 놋쇠 받침판 (원형 꽃 문양)
    d.ellipse([kx - 65, ky - 65, kx + 65, ky + 65], fill=(195, 155, 75), outline=(145, 105, 45), width=4)
    d.ellipse([kx - 45, ky - 45, kx + 45, ky + 45], fill=(215, 175, 90))
    # 문고리 고리 (U자 형태)
    d.arc([kx - 35, ky - 20, kx + 35, ky + 70], 0, 180, fill=(170, 125, 55), width=16)
    d.ellipse([kx - 14, ky - 14, kx + 14, ky + 14], fill=(140, 95, 40))  # 고리 연결 못

    # 하이라이트 빛반사
    d.arc([kx - 30, ky - 15, kx + 30, ky + 65], 45, 135, fill=(255, 235, 160), width=6)

    label(d, 50, 60, "세 번째 컷 · 창호문 온기와 놋쇠 문고리 디테일", 30)
    label(d, 50, 135, "핵심 팁: 30~50cm 거리 + 인물 모드(아웃포커싱)로 작은 디테일 감성 살리기", 22, bg=(60, 42, 30), fg=(255, 255, 255))

    # 하단 팁 카드
    d.rounded_rectangle([50, H - 150, W - 50, H - 40], 20, fill=(28, 20, 16), outline=(85, 60, 45), width=2)
    d.text((80, H - 128), "✔ 격자 창호문 너머로 새어나오는 주황빛 조명과 차가운 바깥 공기의 감성 대비", font=font(22), fill=(245, 235, 220))
    d.text((80, H - 85), "✔ 문고리나 문살의 질감에 초점을 맞추고 뒷배경을 부드럽게 흐려 풍성한 이야기 완성", font=font(22), fill=(255, 210, 120))

    noise(img, seed=204).save(OUT / "04_body3.png")


# 05 결론: 지담 스튜디오 시그니처 아웃트로 카드
def outro():
    img = gradient(W, H, (38, 32, 28), (22, 18, 16))
    d = ImageDraw.Draw(img)

    # 상/하단 필름 퍼포레이션 디자인
    for y0 in (0, H - 60):
        d.rectangle([0, y0, W, y0 + 60], fill=(14, 12, 10))
        for x in range(20, W, 60):
            d.rounded_rectangle([x, y0 + 17, x + 32, y0 + 43], 4, fill=(210, 185, 150))

    # 한옥 처마 곡선 심볼
    draw_roof(d, W // 2 - 130, 200, W // 2 + 130, 200, (230, 195, 140), curve=22)
    # 문고리 심볼 원
    d.ellipse([W // 2 - 20, 245, W // 2 + 20, 285], outline=(230, 195, 140), width=4)

    center_text(d, 330, "지담 스튜디오", font(96, True), (250, 242, 232))
    center_text(d, 470, "일상을 작품으로 남기는 사진 스튜디오", font(34), (230, 195, 140))
    center_text(d, 530, "스마트폰 하나로도 감성 사진은 충분하다", font(28, True), (195, 170, 140))

    center_text(d, 630, "공감과 댓글 · 이웃추가는 지담 스튜디오에 큰 힘이 됩니다", font(22), (150, 130, 110))

    noise(img, seed=205).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro()
    body1()
    body2()
    body3()
    outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

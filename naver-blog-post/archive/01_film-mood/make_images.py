"""블로그 이미지 5장(1200x800, 3:2)을 Pillow로 생성합니다."""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 800
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)

FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    return img


def grain(img, amount=14, seed=1):
    rnd = random.Random(seed)
    noise = Image.new("L", img.size)
    noise.putdata([128 + rnd.randint(-amount, amount) for _ in range(img.size[0] * img.size[1])])
    noise = noise.convert("RGB")
    return Image.blend(img, noise, 0.06)


def center_text(d, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


def caption(d, text, fill=(80, 60, 50)):
    center_text(d, H - 70, text, font(30, True), fill)


# 01 서론: 스마트폰 화면 속 노을 창가
def intro():
    img = gradient(W, H, (250, 232, 214), (236, 205, 180))
    d = ImageDraw.Draw(img)
    # 휴대폰
    px, py, pw, ph = 440, 60, 320, 620
    d.rounded_rectangle([px + 12, py + 14, px + pw + 12, py + ph + 14], 44, fill=(205, 170, 145))
    d.rounded_rectangle([px, py, px + pw, py + ph], 44, fill=(40, 36, 40))
    sx, sy, sw, sh = px + 18, py + 40, pw - 36, ph - 80
    scene = gradient(sw, sh, (255, 180, 120), (250, 120, 110))
    sd = ImageDraw.Draw(scene)
    sd.ellipse([sw / 2 - 60, sh * 0.42, sw / 2 + 60, sh * 0.42 + 120], fill=(255, 226, 150))
    sd.rectangle([0, sh * 0.58, sw, sh], fill=(120, 80, 90))
    # 창틀
    sd.rectangle([0, 0, sw, sh], outline=(250, 240, 230), width=14)
    sd.line([(sw / 2, 0), (sw / 2, sh * 0.58)], fill=(250, 240, 230), width=10)
    sd.line([(0, sh * 0.3), (sw, sh * 0.3)], fill=(250, 240, 230), width=10)
    # 창가 화분
    sd.rectangle([sw * 0.62, sh * 0.72, sw * 0.82, sh * 0.86], fill=(200, 120, 90))
    for dx in (-30, 0, 30):
        sd.ellipse([sw * 0.72 + dx - 22, sh * 0.62, sw * 0.72 + dx + 22, sh * 0.74], fill=(90, 130, 90))
    scene = grain(scene.filter(ImageFilter.GaussianBlur(0.6)), seed=2)
    img.paste(scene, (sx, sy))
    d.ellipse([px + pw / 2 - 24, py + ph - 34, px + pw / 2 + 24, py + ph - 14], outline=(90, 90, 95), width=3)
    # 셔터 아이콘 & 문구
    d.text((110, 300), "FILM", font=font(64, True), fill=(160, 100, 80))
    d.text((110, 380), "MOOD", font=font(64, True), fill=(160, 100, 80))
    d.text((850, 300), "폰 하나로", font=font(46, True), fill=(110, 70, 60))
    d.text((850, 365), "감성 사진", font=font(46, True), fill=(110, 70, 60))
    caption(d, "스마트폰 하나로 만드는 필름 감성")
    grain(img, seed=3).save(OUT / "01_intro.png")


# 02 본론1: 빛 (골든아워 / 그늘 / 창가)
def body1():
    img = gradient(W, H, (255, 243, 224), (250, 228, 200))
    d = ImageDraw.Draw(img)
    center_text(d, 50, "빛을 고르면 사진의 절반은 끝난다", font(46, True), (110, 70, 50))
    # 해의 궤적
    d.arc([150, 200, 1050, 1000], 180, 360, fill=(220, 170, 120), width=6)
    suns = [(205, 470, "골든아워", (255, 170, 80)), (600, 210, "한낮 → 그늘로", (255, 215, 110)),
            (995, 470, "골든아워", (255, 140, 90))]
    for x, y, label, c in suns:
        d.ellipse([x - 50, y - 50, x + 50, y + 50], fill=c)
        w = d.textlength(label, font=font(30, True))
        d.text((x - w / 2, y + 62), label, font=font(30, True), fill=(120, 80, 60))
    # 창가 아이콘
    wx, wy = 470, 470
    d.rectangle([wx, wy, wx + 260, wy + 180], fill=(205, 230, 245), outline=(150, 110, 90), width=8)
    d.line([(wx + 130, wy), (wx + 130, wy + 180)], fill=(150, 110, 90), width=6)
    d.polygon([(wx + 260, wy + 30), (wx + 420, wy + 120), (wx + 420, wy + 200), (wx + 260, wy + 180)],
              fill=(255, 230, 170))
    d.text((wx + 30, wy + 195), "실내는 창가 옆에서", font=font(28, True), fill=(120, 80, 60))
    caption(d, "해 뜬 후 1시간 · 해 지기 전 1시간을 노려보세요")
    grain(img, seed=4).save(OUT / "02_body1.png")


# 03 본론2: 3분할 구도와 여백
def body2():
    img = gradient(W, H, (226, 236, 240), (200, 218, 226))
    d = ImageDraw.Draw(img)
    center_text(d, 50, "구도는 덜어낼수록 감성이 된다", font(46, True), (50, 70, 90))
    fx, fy, fw, fh = 210, 150, 780, 520
    frame = gradient(fw, fh, (190, 215, 235), (240, 235, 225))
    fd = ImageDraw.Draw(frame)
    fd.rectangle([0, fh * 0.72, fw, fh], fill=(215, 200, 180))
    # 피사체(나무)를 교차점에
    tx, ty = fw / 3, fh * 2 / 3
    fd.rectangle([tx - 10, ty - 40, tx + 10, ty + 60], fill=(120, 90, 70))
    fd.ellipse([tx - 75, ty - 190, tx + 75, ty - 20], fill=(110, 150, 110))
    # 격자
    for i in (1, 2):
        fd.line([(fw * i / 3, 0), (fw * i / 3, fh)], fill=(255, 255, 255), width=3)
        fd.line([(0, fh * i / 3), (fw, fh * i / 3)], fill=(255, 255, 255), width=3)
    for i in (1, 2):
        for j in (1, 2):
            cx, cy = fw * i / 3, fh * j / 3
            fd.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=(240, 120, 90), width=4)
    fd.text((fw * 0.76, fh * 0.08), "여백", font=font(44, True), fill=(255, 255, 255))
    img.paste(grain(frame, seed=5), (fx, fy))
    d.rectangle([fx, fy, fx + fw, fy + fh], outline=(60, 70, 80), width=6)
    caption(d, "격자를 켜고, 주인공은 교차점에 · 나머지는 비워두기", fill=(50, 70, 90))
    img.save(OUT / "03_body2.png")


# 04 본론3: 보정 슬라이더
def body3():
    img = gradient(W, H, (245, 236, 226), (232, 218, 204))
    d = ImageDraw.Draw(img)
    center_text(d, 50, "필름 톤 보정, 슬라이더 네 개면 충분", font(46, True), (100, 70, 55))
    sliders = [("노출", "-5 ~ -10", 0.42), ("대비", "-10", 0.40), ("따뜻함", "+10", 0.60), ("그레인", "약하게", 0.20)]
    top = 190
    for i, (name, val, pos) in enumerate(sliders):
        y = top + i * 115
        d.text((180, y - 22), name, font=font(36, True), fill=(90, 60, 50))
        x0, x1 = 400, 900
        d.rounded_rectangle([x0, y - 6, x1, y + 6], 6, fill=(210, 190, 175))
        d.rounded_rectangle([x0, y - 6, x0 + (x1 - x0) * pos, y + 6], 6, fill=(220, 140, 100))
        kx = x0 + (x1 - x0) * pos
        d.ellipse([kx - 22, y - 22, kx + 22, y + 22], fill=(255, 255, 255), outline=(220, 140, 100), width=5)
        d.text((940, y - 22), val, font=font(32, True), fill=(180, 100, 70))
    caption(d, "조금 아쉬운데? 싶을 때 멈추는 게 요령")
    grain(img, seed=6).save(OUT / "04_body3.png")


# 05 결론: 브랜드
def outro():
    img = gradient(W, H, (60, 50, 48), (35, 30, 30))
    d = ImageDraw.Draw(img)
    # 필름 스트립 테두리
    for y0 in (40, H - 90):
        d.rectangle([0, y0, W, y0 + 50], fill=(20, 18, 18))
        for x in range(30, W, 70):
            d.rounded_rectangle([x, y0 + 14, x + 34, y0 + 36], 4, fill=(230, 200, 160))
    # 렌즈 원
    d.ellipse([W / 2 - 70, 190, W / 2 + 70, 330], outline=(230, 200, 160), width=8)
    d.ellipse([W / 2 - 30, 230, W / 2 + 30, 290], fill=(230, 200, 160))
    center_text(d, 360, "지담 스튜디오", font(96, True), (250, 235, 215))
    center_text(d, 500, "일상을 작품으로 남기는 사진 스튜디오", font(36), (230, 200, 160))
    center_text(d, 570, "스마트폰 하나로도 감성 사진은 충분하다", font(30, True), (200, 170, 140))
    grain(img, seed=7).save(OUT / "05_outro.png")


if __name__ == "__main__":
    intro(); body1(); body2(); body3(); outro()
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as im:
            print(p.name, im.size)

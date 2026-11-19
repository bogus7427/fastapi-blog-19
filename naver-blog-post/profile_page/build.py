"""지담 스튜디오 링크 프로필 페이지(index.html) 생성
- 이미지는 data URI로 넣음 (Artifact는 외부 이미지 불가)
사용법: uv run python profile_page/build.py
"""
import base64
import html
import io
from pathlib import Path

from PIL import Image

BASE = Path(__file__).parent
ROOT = BASE.parent
BLOG = "https://blog.naver.com/bogus7427"


def data_uri(path, width, quality=80):
    im = Image.open(path).convert("RGB")
    im.thumbnail((width, width * 2))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


LOGO = data_uri(ROOT / "skin/profile.png", 240, 88)

# 카테고리별 대표 글 (발행된 글 번호)
LINKS = [
    ("스튜디오 소식", "지담 스튜디오 블로그 오픈 인사", "224483226809", "07_blog-open"),
    ("스마트폰 사진 팁", "인물 사진 잘 찍는 법, 자연스럽고 예쁘게", "224483301479", "10_portrait"),
    ("보정 노하우", "무드별 색감 보정 레시피 3가지", "224483333539", "13_color-recipe"),
    ("카메라 촬영 기초", "초점과 화이트밸런스 기초", "224483311562", "12_focus-wb"),
    ("감성 사진 갤러리", "늦가을 감성 사진, 지금 담기 좋은 장면", "224483306785", "11_late-autumn"),
    ("촬영 후기", "한강 노을 스냅 촬영 후기", "224483192053", "04_hangang-review"),
]

GALLERY = [
    ("02_dica-mood", "01_intro.png", "디카 감성 스냅", "224483114318"),
    ("09_travel-photo", "03_body2.png", "여행 사진 구도", "224483294827"),
    ("08_food-photo", "01_intro.png", "카페 디저트 사진", "224483289516"),
    ("05_rainy-gallery", "01_intro.png", "비 오는 날 창가", "224483202382"),
    ("11_late-autumn", "02_body1.png", "늦가을 낙엽 탑뷰", "224483306785"),
    ("06_exposure-basics", "02_body1.png", "셔터 속도 비교", "224483210544"),
]


def link_card(cat, title, log_no, folder):
    thumb = data_uri(ROOT / "archive" / folder / "images/01_intro.png", 120, 70)
    return f"""
      <a class="card link" href="{BLOG}/{log_no}" target="_blank" rel="noopener">
        <img class="thumb" src="{thumb}" alt="" width="44" height="44">
        <span class="link-text">
          <span class="link-title">{html.escape(title)}</span>
          <span class="link-sub">{html.escape(cat)} · blog.naver.com</span>
        </span>
        <span class="chev" aria-hidden="true">›</span>
      </a>"""


def gallery_item(folder, img, caption, log_no):
    src = data_uri(ROOT / "archive" / folder / "images" / img, 520, 78)
    return f"""
          <a class="shot" href="{BLOG}/{log_no}" target="_blank" rel="noopener">
            <img src="{src}" alt="{html.escape(caption)} 일러스트" loading="lazy">
            <span class="cap">{html.escape(caption)}</span>
          </a>"""


page = f"""<title>지담 스튜디오</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@700&family=Noto+Sans+KR:wght@400;500;700&display=swap">
<style>
  /* Layout: 모바일 링크 프로필 — 가운데 480px 기둥, 베이지 바탕 위 흰 카드 목록 */
  :root {{
    --page: #e9ddbc;      /* 크라프트지 베이지 (참고 페이지 톤) */
    --page-edge: #dccd9f;
    --card: #ffffff;
    --ink: #2b2522;
    --muted: #7b6f62;
    --pill: #2b2522;
    --pill-ink: #fbf6ea;
    --line: #e8e0cd;
    --gold: #a8854f;
    --font-display: "Gowun Batang", "Noto Serif KR", Georgia, serif;
    --font-body: "Noto Sans KR", "Malgun Gothic", system-ui, sans-serif;
    --font-latin: Georgia, "Times New Roman", serif;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --page: #2a2620; --page-edge: #221f1a; --card: #36312a; --ink: #f3ece0; --muted: #b9ad9b;
      --pill: #f3ece0; --pill-ink: #2a2620; --line: #4a4339; --gold: #d2b07a; color-scheme: dark;
    }}
  }}
  :root[data-theme="dark"] {{
    --page: #2a2620; --page-edge: #221f1a; --card: #36312a; --ink: #f3ece0; --muted: #b9ad9b;
    --pill: #f3ece0; --pill-ink: #2a2620; --line: #4a4339; --gold: #d2b07a; color-scheme: dark;
  }}
  * {{ box-sizing: border-box; }}
  body {{ background: var(--page-edge); color: var(--ink); font-family: var(--font-body); }}
  .column {{
    max-width: 480px; margin: 0 auto; min-height: 100vh; background: var(--page);
    padding-block: 28px 0;
    padding-left: max(16px, env(safe-area-inset-left, 0px));
    padding-right: max(16px, env(safe-area-inset-right, 0px));
    display: flex; flex-direction: column; gap: 12px;
  }}
  header {{ display: flex; flex-direction: column; align-items: center; text-align: center; gap: 6px; padding-bottom: 14px; }}
  .logo {{ width: 96px; height: 96px; border-radius: 50%; object-fit: cover; box-shadow: 0 2px 10px rgb(0 0 0 / .12); margin-bottom: 8px; }}
  .latin {{ font-family: var(--font-latin); letter-spacing: .28em; font-size: 11px; color: var(--gold); text-transform: uppercase; }}
  h1 {{ font-family: var(--font-display); font-size: 24px; margin: 0; text-wrap: balance; }}
  .intro {{ color: var(--muted); font-size: 14px; line-height: 1.6; margin: 2px 0 0; max-width: 30ch; }}
  .pills {{ display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap; justify-content: center; }}
  .pill {{ display: inline-flex; align-items: center; gap: 6px; background: var(--pill); color: var(--pill-ink);
           text-decoration: none; font-weight: 700; font-size: 14px; padding: 10px 20px; border-radius: 999px; }}
  .card {{ background: var(--card); border-radius: 12px; }}
  .link {{ display: flex; align-items: center; gap: 12px; padding: 14px 16px; text-decoration: none; color: inherit; }}
  .thumb {{ width: 44px; height: 44px; border-radius: 10px; object-fit: cover; flex: none; border: 1px solid var(--line); }}
  .link-text {{ display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1; }}
  .link-title {{ font-weight: 700; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .link-sub {{ font-size: 12px; color: var(--muted); }}
  .chev {{ color: var(--muted); font-size: 22px; line-height: 1; }}
  a:focus-visible {{ outline: 3px solid var(--gold); outline-offset: 2px; }}
  .link:hover .link-title {{ text-decoration: underline; }}
  details.card {{ padding: 16px; }}
  summary {{ font-weight: 700; font-size: 16px; cursor: pointer; list-style: none; display: flex; justify-content: space-between; }}
  summary::-webkit-details-marker {{ display: none; }}
  summary::after {{ content: "⌃"; color: var(--muted); transform: rotate(0deg); }}
  details:not([open]) summary::after {{ transform: rotate(180deg); }}
  .gallery {{ display: grid; grid-auto-flow: column; grid-auto-columns: 78%; gap: 8px; overflow-x: auto;
              scroll-snap-type: x mandatory; margin-top: 12px; padding-bottom: 4px; }}
  .shot {{ scroll-snap-align: start; position: relative; display: block; border-radius: 10px; overflow: hidden; }}
  .shot img {{ display: block; width: 100%; aspect-ratio: 3 / 2; object-fit: cover; }}
  .cap {{ position: absolute; left: 8px; bottom: 8px; background: rgb(0 0 0 / .55); color: #fff; font-size: 12px;
          padding: 4px 8px; border-radius: 6px; }}
  dl {{ display: grid; grid-template-columns: 4.5em 1fr; gap: 8px 10px; margin: 12px 0 0; font-size: 14px; }}
  dt {{ color: var(--muted); }}
  dd {{ margin: 0; min-width: 0; overflow-wrap: anywhere; }}
  dd a {{ color: var(--gold); }}
  .note {{ text-align: center; color: var(--muted); font-size: 12px; margin: 10px 0 0; }}
  footer {{ margin-top: 18px; padding: 22px 0 28px; text-align: center; color: var(--muted); font-size: 12px;
            border-top: 1px solid var(--line); font-family: var(--font-latin); letter-spacing: .2em; }}
  @media (prefers-reduced-motion: no-preference) {{ .gallery {{ scroll-behavior: smooth; }} }}
</style>

<div class="column">
  <header>
    <img class="logo" src="{LOGO}" alt="지담 스튜디오 로고" width="96" height="96">
    <span class="latin">Jidam Studio</span>
    <h1>지담 스튜디오</h1>
    <p class="intro">일상을 작품으로 남기는 사진 스튜디오. 스마트폰 하나로도 감성 사진은 충분해요.</p>
    <div class="pills">
      <a class="pill" href="{BLOG}" target="_blank" rel="noopener">블로그 보기</a>
      <a class="pill" href="{BLOG}/224483226809" target="_blank" rel="noopener">오픈 인사 읽기</a>
    </div>
  </header>

  {"".join(link_card(*l) for l in LINKS)}

  <details class="card" open>
    <summary>갤러리</summary>
    <div class="gallery" tabindex="0" aria-label="블로그 글 이미지 모음, 옆으로 넘겨 보기">
      {"".join(gallery_item(*g) for g in GALLERY)}
    </div>
  </details>

  <details class="card" open>
    <summary>기본 정보</summary>
    <dl>
      <dt>블로그</dt><dd><a href="{BLOG}" target="_blank" rel="noopener">blog.naver.com/bogus7427</a></dd>
      <dt>운영</dt><dd>지담 (지담 스튜디오)</dd>
      <dt>주제</dt><dd>스마트폰 사진 팁 · 보정 노하우 · 카메라 촬영 기초 · 감성 사진 갤러리 · 촬영 후기</dd>
    </dl>
  </details>

  <p class="note">새 글 소식은 블로그 이웃추가로 받아 보세요.</p>
  <footer>EVERYDAY MOMENTS, MADE ART.</footer>
</div>
"""

out = BASE / "index.html"
out.write_text(page, encoding="utf-8")
print("saved", out, f"{out.stat().st_size / 1024:.0f} KB")

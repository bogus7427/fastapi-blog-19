"""post.md 내용을 네이버 블로그 글쓰기 화면에 자동으로 입력합니다.

사용법:
    uv run python naver-blog-post/upload.py

- 처음 실행하면 Chrome 창에서 네이버에 직접 로그인하세요. 로그인 상태는
  naver-blog-post/.browser-profile 에 저장되어 다음부터는 바로 진행됩니다.
- 제목, 본문, 이미지 5장, 해시태그를 입력한 뒤 멈춥니다.
  내용을 확인하고 '발행' 버튼은 직접 눌러 주세요.
"""
import re
import sys
from pathlib import Path

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

from naver_login import ensure_login
from notify import notify

BLOG_ID = "bogus7427"
BASE = Path(__file__).parent
PROFILE = BASE / ".browser-profile"
WRITE_URL = f"https://blog.naver.com/{BLOG_ID}?Redirect=Write"


def parse_category():
    """post.md 맨 위의 <!-- category: 이름 --> 읽기 (없으면 None)"""
    m = re.search(r"<!--\s*category:\s*(.+?)\s*-->", (BASE / "post.md").read_text(encoding="utf-8"))
    return m[1] if m else None


def open_publish_layer(page, frame):
    """상단 [발행]을 눌러 설정 창 열기. 늦게 뜨거나 클릭이 씹히면 다시 누름"""
    cat = frame.locator("button[aria-label='카테고리 목록 버튼']")
    for _ in range(4):
        frame.locator("button[class*=publish_btn]:visible").first.click()
        try:
            cat.first.wait_for(state="visible", timeout=8000)
            page.wait_for_timeout(800)
            return
        except PWTimeout:
            page.keyboard.press("Escape")  # 다른 팝업이 가리고 있으면 닫기
            page.wait_for_timeout(1000)
    raise RuntimeError("발행 설정 창이 열리지 않았습니다.")


def set_category(page, frame, name):
    """발행 설정 창의 카테고리 드롭다운에서 name 선택"""
    trigger = frame.locator("button[aria-label='카테고리 목록 버튼']").first
    if not trigger.count():
        trigger = frame.locator("button[class*=selectbox_button]:visible").first
    for _ in range(3):
        trigger.click()
        page.wait_for_timeout(1000)
        if trigger.get_attribute("aria-expanded") == "true":
            break
    items = frame.locator("[data-testid^=categoryItemText]")
    names = [t.strip() for t in items.all_inner_texts()]
    option = items.filter(has_text=name).locator("visible=true")
    if not option.count():
        raise RuntimeError(f"'{name}' 카테고리를 찾지 못했습니다. 목록: {names}")
    option.last.click()
    page.wait_for_timeout(800)
    current = trigger.inner_text().strip()
    if name not in current:
        raise RuntimeError(f"카테고리 선택 실패 (현재: {current})")
    print("카테고리 선택:", current)


def set_tags(page, frame, tags):
    box = frame.locator("input[placeholder*='태그']:visible").first
    if not box.count():
        return
    box.click()
    for t in tags[:30]:
        page.keyboard.type(t, delay=10)
        page.keyboard.press("Enter")
    print("태그 입력:", len(tags[:30]), "개")


def parse_post():
    md = (BASE / "post.md").read_text(encoding="utf-8")
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    title, blocks, tags = "", [], []
    for line in md.splitlines():
        s = line.strip()
        if not s or s == "---" or s.startswith("## "):
            continue
        if s.startswith("# "):
            title = s[2:]
        elif m := re.match(r"!\[(.+?)\]\((.+?)\)", s):
            blocks.append(("image", str((BASE / m[2]).resolve())))
        elif s.startswith("### "):
            blocks.append(("heading", s[4:]))
        elif s.startswith("#"):
            tags = [t.lstrip("#") for t in s.split()]
        else:
            blocks.append(("text", re.sub(r"\*\*(.+?)\*\*", r"\1", s)))
    return title, blocks, tags


def editor_frame(page):
    """글쓰기 에디터는 mainFrame iframe 안에 있음"""
    for _ in range(60):
        for f in page.frames:
            if f.name == "mainFrame" or "PostWriteForm" in f.url:
                if f.locator(".se-content").count():
                    return f
        page.wait_for_timeout(1000)
    raise RuntimeError("글쓰기 에디터를 찾지 못했습니다.")


def close_popups(frame):
    # '작성 중인 글이 있습니다' → 취소, 도움말 패널 닫기
    for sel in (".se-popup-button-cancel", ".se-help-panel-close-button"):
        try:
            frame.locator(sel).first.click(timeout=2000)
        except PWTimeout:
            pass


def type_text(page, text):
    page.keyboard.type(text, delay=5)
    page.keyboard.press("Enter")


BODY = ".se-component:not(.se-documentTitle)"


def body_components(frame):
    """본문 구성 요소를 순서대로: ['IMG', 'TXT 첫부분...']"""
    return frame.evaluate("""(sel) => [...document.querySelectorAll(sel)].map(c =>
        c.classList.contains('se-image') ? 'IMG' : 'TXT ' + [...c.querySelectorAll('.se-text-paragraph')]
            .map(p => p.textContent).join(' ').replace(/[\\s\\u200b]+/g, ' ').trim().slice(0, 25))""", BODY)


def clear_body(page, frame):
    """본문을 통째로 비움 (임시저장·기존 내용이 섞이는 것 방지)"""
    for _ in range(3):
        frame.locator(BODY).first.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        page.wait_for_timeout(500)
        comps = body_components(frame)
        # 빈 문단 하나만 남으면 성공 (빈 문단에는 '글감과 함께…' 안내 문구가 보임)
        if len(comps) <= 1 and (not comps or comps[0] == "TXT " or "글감과 함께" in comps[0]):
            return
    raise RuntimeError(f"본문을 비우지 못했습니다: {body_components(frame)[:5]}")


def cursor_to_end(page, frame):
    """커서를 문서 맨 끝의 빈 문단으로"""
    last = frame.locator(BODY).last
    if "se-text" in (last.get_attribute("class") or ""):
        last.locator(".se-text-paragraph").last.click()
        page.keyboard.press("Control+End")
    else:  # 마지막이 이미지면 이미지를 선택한 뒤 Enter → 아래에 새 문단
        last.click()
        page.keyboard.press("Enter")
    page.wait_for_timeout(300)


def insert_image(page, frame, path):
    before = frame.locator(".se-component.se-image").count()
    with page.expect_file_chooser(timeout=10000) as fc:
        frame.locator("button.se-image-toolbar-button").first.click()
    fc.value.set_files(path)
    # 업로드 완료(이미지 개수 증가) 대기
    for _ in range(60):
        if frame.locator(".se-component.se-image").count() > before:
            break
        page.wait_for_timeout(500)
    page.wait_for_timeout(1500)
    cursor_to_end(page, frame)


def fill_editor(page, frame, title, blocks, tags):
    """제목·본문을 비우고 처음부터 입력"""
    frame.locator(".se-documentTitle .se-text-paragraph").first.click()
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    page.keyboard.type(title, delay=5)

    clear_body(page, frame)
    cursor_to_end(page, frame)
    for kind, value in blocks:
        if kind == "image":
            insert_image(page, frame, value)
        elif kind == "heading":
            page.keyboard.press("Control+B")
            page.keyboard.type(value, delay=5)
            page.keyboard.press("Control+B")
            page.keyboard.press("Enter")
        else:
            type_text(page, value)
        print(f"  입력: {kind} {Path(value).name if kind == 'image' else value[:30]}")
    if tags:
        page.keyboard.type(" ".join("#" + t for t in tags), delay=5)


def verify_editor(frame, blocks):
    """입력 결과가 원고 순서(이미지/글)와 같은지 검사"""
    want = []
    for k, _ in blocks:  # 연속된 글·소제목은 에디터에서 한 묶음이 되므로 하나로 셈
        kind = "IMG" if k == "image" else "TXT"
        if not (kind == "TXT" and want and want[-1] == "TXT"):
            want.append(kind)
    got = [c.split()[0] for c in body_components(frame) if c != "TXT " and "글감과 함께" not in c]
    ok = got[:len(want)] == want and got.count("IMG") == want.count("IMG")
    return ok, got


def main():
    title, blocks, tags = parse_post()
    print(f"제목: {title}\n블록 {len(blocks)}개, 태그 {len(tags)}개")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE), channel="chrome", headless=False, viewport={"width": 1280, "height": 900}
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(WRITE_URL)

        ensure_login(page, WRITE_URL)

        frame = editor_frame(page)
        page.wait_for_timeout(2000)
        close_popups(frame)

        fill_editor(page, frame, title, blocks, tags)
        ok, got = verify_editor(frame, blocks)
        print("구성 검사:", "OK" if ok else f"순서 어긋남 {got}")
        if not ok:
            notify(f"⚠️ 글 구성 순서가 원고와 다릅니다. 발행 전에 확인해 주세요.\n{got}")

        # 발행 설정 창: 카테고리·태그 자동 선택 및 최종 자동 발행
        category = parse_category()
        open_publish_layer(page, frame)
        if category:
            set_category(page, frame, category)
        set_tags(page, frame, tags)

        cat_msg = f"카테고리: {category}\n" if category else ""
        print("\n설정 완료! 최종 발행 버튼을 자동으로 클릭합니다...")
        page.wait_for_timeout(1500)
        frame.locator("button:has-text('발행'):visible").last.click()
        print("발행 버튼 클릭 완료! 페이지 이동 대기 중...")

        # 발행되면 글 주소(blog.naver.com/아이디/글번호)로 이동함 → 최대 60초 대기
        post_url = re.compile(rf"blog\.naver\.com/(?:{BLOG_ID}/(\d+)|PostView\.naver\?.*logNo=(\d+))")
        try:
            page.wait_for_url(post_url, timeout=60_000)
            print("발행 완료:", page.url)
            notify(f"✅ 블로그 발행 완료!\n{title}\n{page.url}")
            page.wait_for_timeout(5000)
        except PWTimeout:
            print("발행 완료 URL로 이동을 감지하지 못했습니다. 화면 확인 필요.")
            notify(f"⚠️ 발행 후 페이지 이동 대기 시간 초과\n제목: {title}\n현재 주소: {page.url}")
        except Exception as e:
            print("발행 확인 중 오류:", e)
            notify(f"⚠️ 발행 확인 중 오류 발생: {e}")
        ctx.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("오류:", e)
        notify(f"❌ 블로그 업로드 오류\n{str(e)[:300]}")
        sys.exit(1)

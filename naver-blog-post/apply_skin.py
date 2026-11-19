"""블로그 리모콘에 스튜디오 스킨 적용 (스킨배경 + 타이틀)
사용법: uv run python apply_skin.py
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from naver_login import ensure_login
from notify import notify

BLOG_ID = "bogus7427"
BASE = Path(__file__).parent
SKIN = BASE / "skin"
PROFILE = BASE / ".browser-profile"
ADMIN = f"https://admin.blog.naver.com/{BLOG_ID}"
SHOT = BASE / "skin" / "_result.png"

FIND = """(t) => [...document.querySelectorAll('*')].filter(e => {
    const own = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
    if (own !== t) return false;
    const r = e.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden';
}).map(e => { const r = e.getBoundingClientRect(); return [r.x + r.width/2, r.y + r.height/2]; })"""


def click_text(page, text, index=-1):
    hits = page.evaluate(FIND, text)
    if not hits:
        raise RuntimeError(f"'{text}' 버튼을 찾지 못했습니다.")
    x, y = hits[index]
    page.mouse.click(x, y)
    page.wait_for_timeout(2000)


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE), channel="chrome", headless=False, viewport={"width": 1400, "height": 950}
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.on("dialog", lambda d: d.accept())

        page.goto(ADMIN)
        page.wait_for_timeout(3000)
        ensure_login(page, ADMIN)
        page.wait_for_timeout(3000)

        # 관리 → 꾸미기 설정 → 세부 디자인 설정 (직접 주소로 가면 권한 오류가 나서 메뉴로 이동)
        page.goto(f"{ADMIN}/skin/list")
        page.wait_for_timeout(4000)
        page.locator("a:has-text('세부 디자인 설정'):visible").first.click()
        page.wait_for_url("**/Remocon.naver*", timeout=30000)
        page.wait_for_timeout(6000)
        print("리모콘 열림")

        # 스킨배경 → 직접등록 → 상단 이미지 + 하단 패턴
        click_text(page, "스킨배경", 0)
        click_text(page, "직접등록")
        page.locator("#input_top_file").set_input_files(str(SKIN / "background.png"))
        page.wait_for_timeout(5000)
        page.locator("#input_bottom_file").set_input_files(str(SKIN / "pattern.png"))
        page.wait_for_timeout(5000)
        print("스킨배경 등록")

        # 타이틀 → 직접등록 → 이미지 + 높이 300
        click_text(page, "타이틀", 0)
        click_text(page, "직접등록")
        page.locator("#titleInputFile").set_input_files(str(SKIN / "title.png"))
        page.wait_for_timeout(5000)
        page.evaluate("""() => {
            const el = document.querySelector('#title_height');
            el.focus(); el.value = '300';
            for (const t of ['input','change','keyup','blur']) el.dispatchEvent(new Event(t, {bubbles: true}));
        }""")
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)
        print("타이틀 등록, 높이:", page.locator("#title_height").input_value())

        # 적용
        click_text(page, "적용")
        page.wait_for_timeout(3000)
        for label in ("확인", "적용"):  # 확인 레이어가 뜨는 경우
            try:
                click_text(page, label)
            except RuntimeError:
                pass
        page.wait_for_timeout(4000)

        page.goto(f"https://blog.naver.com/{BLOG_ID}")
        page.wait_for_timeout(6000)
        page.screenshot(path=str(SHOT))
        print("완료 → 결과 화면:", SHOT)
        notify("🎨 블로그 스튜디오 스킨 적용 완료!\nhttps://blog.naver.com/" + BLOG_ID)
        ctx.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("오류:", e)
        notify(f"❌ 스킨 적용 오류\n{str(e)[:300]}")
        sys.exit(1)

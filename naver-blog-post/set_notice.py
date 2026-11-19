"""발행된 글을 공지사항으로 등록: uv run python set_notice.py 글번호
(본문은 건드리지 않고 발행 설정의 '공지사항으로 등록'만 체크한 뒤 다시 발행)
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from naver_login import ensure_login
from notify import notify
from upload import BLOG_ID, close_popups, editor_frame, open_publish_layer

BASE = Path(__file__).parent
log_no = sys.argv[1]
URL = f"https://blog.naver.com/{BLOG_ID}?Redirect=Update&logNo={log_no}"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(BASE / ".browser-profile"), channel="chrome",
                                               headless=False, viewport={"width": 1400, "height": 950})
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto(URL)
    page.wait_for_timeout(3000)
    ensure_login(page, URL)
    frame = editor_frame(page)
    page.wait_for_timeout(3000)
    close_popups(frame)

    open_publish_layer(page, frame)
    if "--inspect" in sys.argv:
        print(frame.evaluate("""() => [...document.querySelectorAll('input[type=checkbox]')].map(i => {
            const lab = document.querySelector('label[for="' + i.id + '"]');
            return '#' + i.id + ' checked=' + i.checked + ' label=' + (lab ? lab.innerText.trim() : '-'); }).join('\\n')"""))
        ctx.close(); raise SystemExit
    box = frame.locator("#set-notice")
    if not box.is_checked():
        frame.locator("label[for='set-notice']").click()
        page.wait_for_timeout(800)
    print("공지사항 체크:", box.is_checked())
    if not box.is_checked():
        raise SystemExit("공지사항 체크에 실패했습니다.")

    frame.locator("button:has-text('발행'):visible").last.click()
    page.wait_for_url(f"**/{log_no}**", timeout=60000)
    page.wait_for_timeout(3000)
    print("공지 등록 완료:", page.url)
    notify(f"📌 공지사항 등록 완료\nhttps://blog.naver.com/{BLOG_ID}/{log_no}")
    ctx.close()

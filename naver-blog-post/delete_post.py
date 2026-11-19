"""글 삭제: uv run python delete_post.py 글번호
(되돌릴 수 없으니 글번호를 꼭 확인하고 실행)
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from naver_login import ensure_login

BLOG_ID = "bogus7427"
BASE = Path(__file__).parent
log_no = sys.argv[1]
URL = f"https://blog.naver.com/PostView.naver?blogId={BLOG_ID}&logNo={log_no}"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(BASE / ".browser-profile"), channel="chrome",
                                               headless=False, viewport={"width": 1400, "height": 950})
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.on("dialog", lambda d: (print("확인창:", d.message), d.accept()))
    page.goto(URL)
    page.wait_for_timeout(3000)
    ensure_login(page, URL)
    page.wait_for_timeout(3000)

    title = page.locator(".se-title-text, .pcol1").first.inner_text().strip()
    print("삭제할 글:", log_no, "/", title)

    if "--inspect" in sys.argv:
        print(page.evaluate("""() => [...document.querySelectorAll('a,button')].filter(e => e.innerText.trim() === '삭제')
            .map(e => e.outerHTML.slice(0, 220) + '  || parent=' + String(e.parentElement.className) + ' / ' + String(e.closest('[id]')?.id)).join('\\n')"""))
        ctx.close(); raise SystemExit
    # 이 글 본문 영역(post_글번호) 안의 '삭제' 링크만 누름 (공지 줄의 '삭제'는 공지 내리기라서 제외)
    page.locator(".area_btn_postedit a._deletePost").first.click()
    page.wait_for_timeout(4000)

    # 삭제 확인: 글 목록에 글번호가 더 이상 없는지
    page.goto(f"https://blog.naver.com/PostTitleListAsync.naver?blogId={BLOG_ID}&currentPage=1&categoryNo=0&countPerPage=30")
    gone = f'"logNo":"{log_no}"' not in page.content()
    print("삭제 확인:", "삭제됨" if gone else "아직 남아 있음")
    ctx.close()
    sys.exit(0 if gone else 1)

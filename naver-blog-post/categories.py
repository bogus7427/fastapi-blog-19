"""블로그 카테고리(메뉴) 만들기
uv run python categories.py inspect   # 화면 구조 확인
uv run python categories.py           # 아래 CATEGORIES 생성
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from naver_login import ensure_login

BLOG_ID = "bogus7427"
BASE = Path(__file__).parent
URL = f"https://admin.blog.naver.com/{BLOG_ID}/config/blog"

CATEGORIES = [
    "스튜디오 소식",
    "스마트폰 사진 팁",
    "카메라 촬영 기초",
    "보정 노하우",
    "감성 사진 갤러리",
    "촬영 후기",
]

RENAME_TO = "스마트폰 사진 팁"  # 기존 '게시판'을 이 이름으로 바꿈

mode = sys.argv[1] if len(sys.argv) > 1 else "apply"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(BASE / ".browser-profile"), channel="chrome",
                                               headless=False, viewport={"width": 1400, "height": 950})
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.on("dialog", lambda d: (print("dialog:", d.message), d.accept()))
    page.goto(URL)
    page.wait_for_timeout(3000)
    ensure_login(page, URL)
    page.wait_for_timeout(4000)
    f = page.frame(name="papermain")

    if mode == "debugadd":
        li = f.locator("li.tree-node:has-text('스마트폰 사진 팁')").first
        box = li.locator("div").first.bounding_box()
        page.mouse.click(box["x"] + 30, box["y"] + box["height"] / 2)
        page.wait_for_timeout(800)
        print("before:", f.locator("li.tree-node").count())
        b = f.locator("img._addCategoryView").bounding_box()
        page.mouse.click(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
        page.wait_for_timeout(1500)
        print("after:", f.locator("li.tree-node").count())
        print(f.evaluate("() => document.querySelector('ul').parentElement.innerHTML.replace(/\\s+/g,' ').slice(0, 1500)"))
    elif mode == "tree":
        print(f.evaluate("() => [...document.querySelectorAll('li.tree-node')].slice(0,3).map(e => e.outerHTML.slice(0, 600)).join('\\n\\n')"))
    elif mode == "inspect":
        print(f.url)
        print(f.evaluate("""() => [...document.querySelectorAll('a,button,input,select,li')]
            .filter(e => e.offsetParent).map(e => e.tagName + ' #' + e.id + ' .' + String(e.className).slice(0, 35)
            + ' | ' + (e.innerText || e.value || e.title || '').trim().replace(/\\s+/g, ' ').slice(0, 30)).join('\\n')"""))
    else:
        def select(li):
            """목록 항목 선택: 안쪽 div를 마우스로 눌러야 선택됨"""
            box = li.locator("div").first.bounding_box()
            page.mouse.click(box["x"] + 30, box["y"] + box["height"] / 2)
            page.wait_for_timeout(600)
            if "tree-selected" not in (li.get_attribute("class") or "") and \
                    "selected" not in (li.locator("div").first.get_attribute("class") or ""):
                print("  (선택 확인 안 됨)", li.inner_text().strip())

        def tree():
            return f.evaluate("() => [...document.querySelectorAll('li.tree-node')].map(e => e.innerText.trim()).join(' / ')")

        # 1) 빈 구분선 삭제
        for _ in range(10):
            line = f.locator("li.tree-node:has-text('구분선')")
            if not line.count():
                break
            select(line.first)
            page.wait_for_timeout(500)
            b = f.locator("img._deleteCategoryView").bounding_box()
            page.mouse.click(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
            page.wait_for_timeout(1000)
        print("구분선 정리 완료")

        def set_name(name):
            box = f.locator("#category_name")
            box.click()
            box.fill("")
            box.type(name, delay=20)  # 입력 이벤트로 왼쪽 목록 이름이 바뀜
            page.wait_for_timeout(500)

        # 2) 기존 '게시판' → 첫 번째 메뉴 이름으로 (기존 글이 그대로 들어감)
        existing = [n for n in CATEGORIES if f.locator(f"li.tree-node:has-text('{n}')").count()]
        if f.locator("li.tree-node:has-text('게시판')").count():
            select(f.locator("li.tree-node:has-text('게시판')").first)
            set_name(RENAME_TO)
            existing.append(RENAME_TO)
            print("게시판 →", RENAME_TO)

        def press(img_class):
            """이미지 버튼은 마우스로 직접 눌러야 동작함"""
            b = f.locator(f"img.{img_class}").bounding_box()
            page.mouse.click(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
            page.wait_for_timeout(1200)

        # 3) 잘못 들어간 하위 메뉴 정리 (이전 실행에서 생긴 것)
        for _ in range(10):
            child = f.locator("#tree li.tree-node li.tree-node")
            if not child.count():
                break
            print("하위 메뉴 삭제:", child.first.inner_text().strip().split("\n")[0])
            select(child.first)
            press("_deleteCategoryView")
            if f.locator("#tree li.tree-node li.tree-node").count() == child.count():
                break  # 지워지지 않으면 무한반복 방지

        # 4) 나머지 추가: 최상위(카테고리 전체보기)를 선택한 뒤 추가해야 하위로 안 들어감
        for name in CATEGORIES:
            if f.locator(f"#tree span._categoryName:text-is('{name}')").count():
                continue
            added = False
            for _ in range(4):  # 처음 몇 번은 선택이 안 먹는 경우가 있어 재시도
                select(f.locator("#tree > li.first-child"))
                before = f.locator("#tree li.tree-node").count()
                press("_addCategoryView")
                if f.locator("#tree li.tree-node").count() > before:
                    added = True
                    break
            if not added:
                print("  추가 실패:", name)
                continue
            set_name(name)  # 새로 추가된 항목이 자동 선택됨
            print("추가:", name)

        print("저장 전 목록:", tree())
        f.locator("#submit_button").click()
        page.wait_for_timeout(4000)
        print("저장 완료")
        page.goto(URL)
        page.wait_for_timeout(4000)
        f = page.frame(name="papermain")
        print("현재 메뉴:", f.evaluate("() => [...document.querySelectorAll('li.tree-node')].map(e => e.innerText.trim()).join(' / ')"))
    page.screenshot(path=str(BASE / "skin" / "_result.png"))
    ctx.close()


"""블로그 정보(별명·소개글) 설정: uv run python set_profile.py"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from naver_login import ensure_login

BLOG_ID = "bogus7427"
BASE = Path(__file__).parent
URL = f"https://admin.blog.naver.com/{BLOG_ID}"

NICKNAME = "지담"
INTRO = ("안녕하세요, 지담 스튜디오입니다.\n"
         "스마트폰 하나로도 따라 할 수 있는 촬영 팁, 보정 노하우, 감성 사진 이야기를 나누려고 블로그를 열었어요.\n"
         "궁금한 점은 댓글로 편하게 남겨 주시고, 이웃추가로 함께해 주세요 :)")

mode = sys.argv[1] if len(sys.argv) > 1 else "apply"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(BASE / ".browser-profile"), channel="chrome",
                                               headless=False, viewport={"width": 1400, "height": 950})
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.on("dialog", lambda d: (print("dialog:", d.message), d.accept()))
    page.goto(URL)
    page.wait_for_timeout(3000)
    ensure_login(page, URL)
    page.wait_for_timeout(3000)

    frames = page.frames
    if mode == "photo":
        f = page.frame(name="papermain")
        before = f.locator("#profile_161").get_attribute("src")
        path = str(BASE / "skin" / "profile.png")
        try:
            with page.expect_file_chooser(timeout=8000) as fc:
                f.locator("a._btnProfileImageUpload").click()
            fc.value.set_files(path)
            print("파일 선택창으로 업로드")
        except Exception:
            # 팝업 창으로 열리는 경우
            pop = ctx.pages[-1]
            pop.wait_for_timeout(2000)
            print("팝업:", pop.url)
            for fr in pop.frames:
                if fr.locator("input[type=file]").count():
                    fr.locator("input[type=file]").first.set_input_files(path)
                    break
            pop.wait_for_timeout(1500)
            pop.screenshot(path=str(BASE / "skin" / "_popup.png"))
            for fr in pop.frames:
                print("POPUP FRAME", fr.url[:80])
                print(fr.evaluate("""() => [...document.querySelectorAll('a,button,input,img,form')].map(e => e.tagName + ' #' + e.id
                    + ' .' + String(e.className).slice(0, 30) + ' ' + (e.type || '') + ' | ' + (e.innerText || e.value || e.alt || e.action || '').trim().slice(0, 40)
                    + ' onclick=' + (e.getAttribute('onclick') || '').slice(0, 60)).join('\\n')"""))
            # 팝업의 확인 버튼(#submitBtn → goSubmit())으로 업로드, 끝나면 팝업이 닫힘
            try:
                if not pop.is_closed():
                    pop.locator("#submitBtn").click(timeout=5000)
                    pop.wait_for_event("close", timeout=30000)
            except Exception as e:
                print("팝업 확인 처리:", type(e).__name__)
            print("팝업 닫힘:", pop.is_closed())
        page.wait_for_timeout(5000)
        after = f.locator("#profile_161").get_attribute("src")
        print("미리보기 바뀜:", before != after)
        f.locator("input._btnConfirm").first.click()
        page.wait_for_timeout(3000)
        print("저장 완료")
    elif mode == "photo-inspect":
        f = page.frame(name="papermain")
        print(f.evaluate("""() => [...document.querySelectorAll('input[type=file], a, button, input[type=button], img')]
            .filter(e => /프로필|profile|등록|삭제/i.test((e.innerText || e.value || e.alt || e.id || e.name || e.className || '')))
            .map(e => e.tagName + ' #' + e.id + ' name=' + (e.name || '') + ' .' + String(e.className).slice(0, 40)
                 + ' | ' + (e.innerText || e.value || e.alt || '').trim().slice(0, 20) + ' vis=' + !!e.offsetParent).join('\\n')"""))
    elif mode == "inspect":
        for f in frames:
            try:
                print("== FRAME", f.name, f.url[:80])
                print(f.evaluate("""() => [...document.querySelectorAll('input[type=text],textarea,button,a.btn,input[type=button],input[type=submit]')]
                  .filter(e=>e.offsetParent).map(e=>e.tagName+' #'+e.id+' name='+e.name+' .'+String(e.className).slice(0,30)+' v='+(e.value||e.innerText||'').slice(0,20)).join('\\n')"""))
            except Exception:
                pass
    else:
        f = next(fr for fr in frames if fr.locator("#frmIntroduce").count())
        f.locator("#frmNickname").fill(NICKNAME)
        f.locator("#frmIntroduce").fill(INTRO)
        f.locator("input._btnConfirm").first.click()
        page.wait_for_timeout(3000)
        print("저장 완료: 별명 =", NICKNAME, "/ 소개글", len(INTRO), "자")
    page.screenshot(path=str(BASE / "skin" / "_result.png"))
    ctx.close()

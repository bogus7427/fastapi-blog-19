"""네이버 자동 로그인 도우미

.env 에 아래 두 줄이 있으면 로그인 화면에서 자동으로 입력합니다.
    NAVER_ID=네이버아이디
    NAVER_PW=네이버비밀번호
- '로그인 상태 유지'를 자동으로 체크합니다.
- 보안문자(캡차)·2단계 인증이 나오면 직접 입력할 때까지 기다립니다.
"""
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from notify import notify

load_dotenv(Path(__file__).parent.parent / ".env")

LOGIN_HOST = "nid.naver.com"


def is_login_page(page) -> bool:
    return LOGIN_HOST in page.url


def ensure_login(page, return_url: str, wait_minutes: int = 5) -> None:
    """로그인 화면이면 자동 로그인 → 실패 시 직접 로그인 대기 → return_url 로 이동"""
    if not is_login_page(page):
        return

    naver_id = os.getenv("NAVER_ID", "").strip()
    naver_pw = os.getenv("NAVER_PW", "").strip()

    if naver_id and naver_pw:
        print("네이버 자동 로그인 중...")
        page.wait_for_selector("#id", timeout=15000)
        # 키보드 입력 대신 값을 직접 넣어야 자동입력 방지에 덜 걸림
        page.evaluate(
            """([id, pw]) => {
                const set = (sel, v) => {
                    const el = document.querySelector(sel);
                    el.focus(); el.value = v;
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                };
                set('#id', id); set('#pw', pw);
                const keep = document.querySelector('#loginStay, #keep, input[name="nvlong"]');
                if (keep && !keep.checked) keep.click();
            }""",
            [naver_id, naver_pw],
        )
        page.wait_for_timeout(500)
        # 화면 크기에 따라 로그인 버튼이 두 개(column/row) 있어 보이는 쪽을 누름
        page.locator("#loginBtn_column:visible, #loginBtn_row:visible, #log\\.login:visible").first.click()
        page.wait_for_timeout(4000)

    if is_login_page(page):
        reason = "보안문자/추가 인증" if naver_id else "로그인"
        print(f"{reason}이 필요합니다. Chrome 창에서 직접 진행해 주세요 (최대 {wait_minutes}분 대기)...")
        notify(f"🔑 네이버 {reason}이 필요합니다. Chrome 창에서 {wait_minutes}분 안에 진행해 주세요.")
        page.wait_for_url(lambda u: LOGIN_HOST not in u, timeout=wait_minutes * 60_000)

    print("로그인 완료")
    if not re.match(re.escape(return_url.split("?")[0]), page.url):
        page.goto(return_url)

"""텔레그램 알림 보내기

.env 설정:
    TELEGRAM_BOT_TOKEN=BotFather에서 받은 토큰
    TELEGRAM_CHAT_ID=내 채팅 ID (아래 명령으로 확인)

채팅 ID 확인: 봇에게 아무 메시지나 보낸 뒤
    uv run python naver-blog-post/notify.py --chat-id
테스트 전송:
    uv run python naver-blog-post/notify.py 테스트 메시지
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def _api(method: str, data: dict | None = None) -> dict:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(".env에 TELEGRAM_BOT_TOKEN이 없습니다.")
    url = f"https://api.telegram.org/bot{token}/{method}"
    body = urllib.parse.urlencode(data).encode() if data else None
    with urllib.request.urlopen(url, data=body, timeout=10) as res:
        return json.loads(res.read().decode())


def notify(text: str) -> bool:
    """알림 전송. 설정이 없거나 실패해도 프로그램은 멈추지 않음"""
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not chat_id or not os.getenv("TELEGRAM_BOT_TOKEN"):
        return False
    try:
        _api("sendMessage", {"chat_id": chat_id, "text": text})
        return True
    except Exception as e:
        print("텔레그램 알림 실패:", e)
        return False


def find_chat_ids():
    updates = _api("getUpdates").get("result", [])
    chats = {}
    for u in updates:
        msg = u.get("message") or u.get("channel_post") or {}
        chat = msg.get("chat")
        if chat:
            chats[chat["id"]] = chat.get("username") or chat.get("title") or chat.get("first_name")
    if not chats:
        print("받은 메시지가 없습니다. 텔레그램에서 봇에게 아무 메시지나 먼저 보내 주세요.")
    for cid, name in chats.items():
        print(f"TELEGRAM_CHAT_ID={cid}   ({name})")


if __name__ == "__main__":
    if sys.argv[1:] == ["--chat-id"]:
        find_chat_ids()
    else:
        text = " ".join(sys.argv[1:]) or "블로그 자동화 텔레그램 알림 테스트입니다."
        print("전송 성공" if notify(text) else "전송 안 됨 (.env의 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 확인)")

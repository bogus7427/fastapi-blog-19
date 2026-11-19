"""지담 스튜디오 네이버 블로그 자동화 에이전트

실행 방법:
    uv run python main.py check    # 1. 원고(post.md) 검사 및 HTML 생성
    uv run python main.py images   # 2. 블로그 본문 이미지 5장 생성
    uv run python main.py upload   # 3. 네이버 블로그에 자동 업로드
    uv run python main.py all      # 전체 한 번에 실행 (검사 -> 이미지 -> 업로드)
"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent / "naver-blog-post"


def run_check() -> bool:
    print("\n▶ [1단계] 원고 검사 및 HTML 변환...")
    res = subprocess.run([sys.executable, str(BASE / "check.py")])
    return res.returncode == 0


def run_images() -> bool:
    print("\n▶ [2단계] 블로그 본문 이미지(5장) 생성...")
    res = subprocess.run([sys.executable, str(BASE / "make_images.py")])
    return res.returncode == 0


def run_upload() -> bool:
    print("\n▶ [3단계] 네이버 블로그 자동 업로드 실행...")
    res = subprocess.run([sys.executable, str(BASE / "upload.py")])
    return res.returncode == 0


def main():
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "check"

    if cmd == "check":
        run_check()
    elif cmd == "images":
        run_images()
    elif cmd == "upload":
        run_upload()
    elif cmd == "all":
        if run_check() and run_images():
            run_upload()
    else:
        print(f"알 수 없는 명령어: {cmd}")
        print("사용 가능 명령어: check, images, upload, all")


if __name__ == "__main__":
    main()

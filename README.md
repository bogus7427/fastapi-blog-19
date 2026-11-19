# 지담 스튜디오 네이버 블로그 자동화 에이전트

지담 스튜디오 네이버 블로그(`bogus7427`)의 포스팅 기획, 이미지 생성, 자동 업로드 및 알림을 담당하는 프로젝트입니다.

---

## 📁 주요 구성 및 폴더 안내

```
blog-agent-19/
├── .env                          # 네이버 로그인, OpenAI API 키, 텔레그램 봇 토큰 등
├── pyproject.toml / uv.lock      # 파이썬 의존성 환경 (uv)
└── naver-blog-post/              # 블로그 자동화 핵심 폴더
    ├── .browser-profile/         # 네이버 브라우저 로그인 세션 쿠키
    ├── archive/                  # 지금까지 발행된 포스팅 원본 아카이브 (01~13)
    ├── images/                   # 현재 작성 중인 글의 이미지 파일들
    ├── post.md                   # 현재 작업 중인 포스팅 원고 (마크다운)
    ├── post.html                 # 네이버 에디터 업로드용 HTML 변환본
    │
    ├── make_images.py            # 원고 기반 로컬 일러스트/다이어그램 이미지 생성
    ├── make_images_ai.py         # OpenAI DALL-E 기반 이미지 생성
    ├── check.py                  # 원고 글자수 검사 및 post.html 생성
    ├── upload.py                 # Playwright 기반 네이버 블로그 자동 업로드
    ├── notify.py                 # 텔레그램 알림 발송 모듈
    │
    ├── naver_login.py            # 네이버 로그인 검증 모듈
    ├── categories.py             # 블로그 카테고리 설정 스크립트
    ├── set_notice.py             # 공지사항 등록 스크립트
    ├── set_profile.py            # 프로필 이미지/소개글 설정 스크립트
    └── delete_post.py            # 특정 글 삭제 유틸리티
```

---

## 🚀 사용 방법

### 1. 가상환경 및 패키지 실행
이 프로젝트는 `uv`를 통해 실행합니다:
```bash
uv run python naver-blog-post/check.py       # 원고 검사 및 HTML 생성
uv run python naver-blog-post/make_images.py # 이미지 생성
uv run python naver-blog-post/upload.py      # 블로그 업로드 실행
```

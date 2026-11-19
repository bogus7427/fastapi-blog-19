"""post.md 섹션별 글자 수(공백 포함) 검사 + 이미지·브랜드 확인 + post.html 생성"""
import html
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
MIN_LEN = 200
BRAND = "지담 스튜디오"
THEME = "스마트폰 하나로도 감성 사진은 충분하다"

md = (BASE / "post.md").read_text(encoding="utf-8")


def body_text(chunk: str) -> str:
    """제목·이미지·주석·빈 줄을 뺀 본문만"""
    lines = []
    for line in chunk.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("![") or s.startswith("<!--") or s == "---":
            continue
        lines.append(re.sub(r"\*\*(.+?)\*\*", r"\1", s))
    return "\n".join(lines)


def section(start: str, end: str | None) -> str:
    i = md.index(start) + len(start)
    j = md.index(end, i) if end else len(md)
    return md[i:j]


sections = {
    "서론": section("## 서론", "## 본론"),
    "본론1": section("### 1.", "### 2."),
    "본론2": section("### 2.", "### 3."),
    "본론3": section("### 3.", "## 결론"),
    "결론": section("## 결론", "\n---"),
}

ok = True
print("[글자 수 검사] (공백 포함, 기준 200자 이상)")
for name, chunk in sections.items():
    n = len(body_text(chunk))
    flag = "OK" if n >= MIN_LEN else "부족"
    ok &= n >= MIN_LEN
    print(f"  {name:4s}: {n:4d}자  {flag}")

print("\n[이미지 검사]")
images = re.findall(r"!\[(.+?)\]\((images/[^)]+)\)", md)
for alt, path in images:
    exists = (BASE / path).exists()
    ok &= exists
    print(f"  {'OK ' if exists else '없음'} {path}  alt: {alt}")
if len(images) != 5:
    ok = False
    print(f"  이미지가 {len(images)}장입니다 (5장 필요)")

print("\n[결론 검사]")
outro = sections["결론"]
for label, word in (("브랜드명", BRAND), ("강조 주제", THEME)):
    found = word in outro
    ok &= found
    print(f"  {label} 포함: {'OK' if found else '없음'}  ({outro.count(word)}회)")

tags = re.findall(r"#\S+", md.split("\n---")[-1])
print(f"\n[해시태그] {len(tags)}개")


# ----- post.html 생성 (스마트에디터 복사·붙여넣기용) -----
def inline(s: str) -> str:
    s = html.escape(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


parts = []
for line in re.sub(r"<!--.*?-->", "", md, flags=re.S).splitlines():
    s = line.strip()
    if not s or s == "---":
        continue
    if m := re.match(r"!\[(.+?)\]\((.+?)\)", s):
        parts.append(f'<p class="img"><img src="{m[2]}" alt="{html.escape(m[1])}"></p>')
    elif s.startswith("### "):
        parts.append(f"<h3>{inline(s[4:])}</h3>")
    elif s.startswith("## "):
        continue  # 서론/본론/결론 라벨은 블로그 본문에 넣지 않음
    elif s.startswith("# "):
        title = s[2:]
        parts.append(f"<h1>{inline(title)}</h1>")
    elif s.startswith("#"):
        parts.append(f'<p class="tags">{inline(s)}</p>')
    else:
        parts.append(f"<p>{inline(s)}</p>")

page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  body {{ background:#f5f5f5; margin:0; padding:24px 16px; font-family:"Malgun Gothic",sans-serif; color:#333; }}
  article {{ max-width:760px; margin:0 auto; background:#fff; padding:40px 32px; border-radius:8px; }}
  h1 {{ font-size:26px; line-height:1.4; }}
  h3 {{ font-size:20px; margin-top:36px; color:#7a4a35; }}
  p {{ font-size:16px; line-height:1.9; }}
  .img img {{ width:100%; height:auto; border-radius:4px; }}
  .tags {{ color:#03a94d; margin-top:32px; }}
</style>
</head>
<body>
<article>
{chr(10).join(parts)}
</article>
</body>
</html>
"""
(BASE / "post.html").write_text(page, encoding="utf-8")
print("\npost.html 생성 완료")

print("\n결과:", "모두 통과" if ok else "보강 필요")
sys.exit(0 if ok else 1)

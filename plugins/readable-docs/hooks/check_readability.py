#!/usr/bin/env python3
"""읽기 좋은 기술문서 구조 게이트 (PostToolUse hook).

품질의 핵심은 readable-docs 스킬이 담당한다.
이 스크립트는 '명백한 구조 누락'만 잡는 안전망이다:
  1) 상단 요약(TL;DR) 누락
  2) 예시/코드블록 누락
  3) 벽글(빈 줄 없이 너무 긴 산문 문단)
"""
import json
import re
import sys

# 벽글 임계치(한국어 기준): 빈 줄 없이 이 글자수를 넘는 산문 문단을 벽글로 본다.
WALL_OF_TEXT_CHARS = 400
# 상단 요약으로 인정할 최소 길이
MIN_SUMMARY_CHARS = 20


def _blocks_outside_code(text):
    """코드펜스 밖의, 빈 줄로 구분된 블록(줄 리스트)들을 반환한다."""
    blocks, current, in_fence = [], [], False
    for ln in text.split("\n"):
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            if current:
                blocks.append(current)
                current = []
            continue
        if in_fence:
            continue
        if ln.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(ln)
    if current:
        blocks.append(current)
    return blocks


def _is_prose(block):
    """리스트/표/헤딩/인용이 아닌 산문 블록인가."""
    prose = [l for l in block
             if not l.lstrip().startswith(("-", "*", "|", "#", ">"))
             and not re.match(r"\s*\d+\.", l)]
    return len(prose) >= max(1, len(block) // 2)


def check_readability(text):
    """마크다운 본문을 검사해 실패 사유 리스트를 반환한다. 빈 리스트면 통과."""
    failures = []
    lines = text.split("\n")
    fence_count = sum(1 for ln in lines if ln.lstrip().startswith("```"))

    # 1) 상단 요약: 첫 '## ' 이전에 본문 산문이 있는가
    summary = []
    for ln in lines:
        if ln.startswith("## "):
            break
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("```"):
            continue
        summary.append(s)
    if len(" ".join(summary)) < MIN_SUMMARY_CHARS:
        failures.append("상단 요약(TL;DR) 누락 — 첫 섹션(##) 이전에 '무엇을/누가/언제 쓰나' 3~5줄 요약을 두세요.")

    # 2) 예시/코드블록: 펜스가 2개 이상(여닫이 1쌍)인가
    if fence_count < 2:
        failures.append("예시/코드블록 누락 — 실행 가능한 예시 1개 이상을 코드블록으로 넣으세요.")

    # 3) 벽글: 코드 밖 산문 문단 중 임계치 초과(첫 1건만 보고)
    for block in _blocks_outside_code(text):
        if not _is_prose(block):
            continue
        joined = "".join(l.strip() for l in block)
        if len(joined) > WALL_OF_TEXT_CHARS:
            failures.append(f"벽글 감지({len(joined)}자) — 빈 줄로 문단을 나누거나 표/리스트로 압축하세요.")
            break

    return failures


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except (ValueError, TypeError):
        sys.exit(0)  # 입력 파싱 실패 시 통과(작업 방해 금지)

    file_path = (payload.get("tool_input") or {}).get("file_path", "") or ""
    base = file_path.rsplit("/", 1)[-1]
    # 대상(spec §6): docs/ 하위 마크다운 또는 최상위 README.md
    is_target = file_path.endswith(".md") and ("/docs/" in file_path or base == "README.md")
    if not is_target:
        sys.exit(0)
    if base == "SKILL.md" or "/.claude-plugin/" in file_path:
        sys.exit(0)  # 스킬/매니페스트 마크다운은 게이트 제외

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        sys.exit(0)

    failures = check_readability(text)
    if failures:
        msg = "[readable-docs] 가독성 구조 점검 실패:\n"
        msg += "\n".join(f"  - {x}" for x in failures)
        msg += "\n(품질은 readable-docs 스킬 기준으로, 위 구조 누락을 보완해 다시 저장하세요.)"
        print(msg, file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()

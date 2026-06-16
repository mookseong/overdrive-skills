"""debug-docs v2 브라우저 스모크: overview + 여러 다이어그램 타입(시퀀스/클래스/플로우차트) 렌더.
실행: ~/.cache/flowdocs-venv/bin/python test_browser_smoke.py  (성공 시 'SMOKE OK', exit 0)
"""
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIEWER = HERE.parent / "viewer"
SAMPLE = HERE.parent / "examples" / "sample-debug.json"
PORT = 8795


def wait_up(url, tries=60):
    for _ in range(tries):
        try:
            urllib.request.urlopen(url)
            return True
        except Exception:
            time.sleep(0.1)
    return False


def main():
    from playwright.sync_api import sync_playwright

    work = Path(tempfile.mkdtemp())
    data = work / "debug.json"
    # 정상 샘플(3종) + 일부러 깨진 다이어그램 1개를 주입해 에러 격리(페이지 안 죽음)를 검증한다.
    doc = json.loads(SAMPLE.read_text(encoding="utf-8"))
    n_ok = len(doc["diagrams"])
    doc["diagrams"].append({"title": "깨진 것", "type": "flowchart", "mermaid": "flowchart TD\n  ((("})
    data.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.Popen([sys.executable, str(VIEWER / "serve.py"), str(data), "--port", str(PORT)])
    try:
        assert wait_up(f"http://127.0.0.1:{PORT}/api/data"), "server did not start"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.goto(f"http://127.0.0.1:{PORT}/")
            # 1) 카드가 모두 생성됨(정상 + 깨진 것 1개)
            page.wait_for_selector(".diagram-card", timeout=10000)
            cards = page.locator(".diagram-card").count()
            assert cards == n_ok + 1, f"card count: {cards} != {n_ok + 1}"
            # 2) 정상 다이어그램들은 svg 로 렌더(>= n_ok)
            page.wait_for_function(
                f"document.querySelectorAll('.diagram-card .diagram svg').length >= {n_ok}",
                timeout=10000,
            )
            svgs = page.locator(".diagram-card .diagram svg").count()
            assert svgs >= n_ok, f"svg count {svgs} < {n_ok}"
            # 3) 타입별 실제 렌더 확인: 시퀀스 액터 + 클래스 박스 텍스트가 SVG 안에 존재
            body_text = page.locator("#diagrams").inner_text()
            assert "PaymentAPI" in body_text, "sequence diagram not rendered"
            assert "ConnectionPool" in body_text, "class diagram not rendered"
            # 4) overview 렌더
            assert "상황" in page.locator("#overview").inner_text(), "overview not rendered"
            # 5) 에러 격리: 깨진 다이어그램은 .error 1개만, 페이지 스크립트 에러는 없음
            assert page.locator(".diagram .error").count() == 1, "broken diagram should isolate to one error card"
            assert errs == [], f"page errors: {errs}"
            browser.close()
        print("SMOKE OK")
    finally:
        proc.terminate()
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

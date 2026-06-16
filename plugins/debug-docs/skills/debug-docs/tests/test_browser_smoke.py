"""debug-docs 브라우저 스모크: blocks 보고서(마크다운 섹션 + 인라인 차트) 렌더 + 에러 격리.
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
    doc = json.loads(SAMPLE.read_text(encoding="utf-8"))
    ok_charts = sum(1 for b in doc["blocks"] if b.get("type") == "chart")
    # 일부러 깨진 차트 1개 주입 → 에러 격리(보고서 나머지 유지) 검증
    doc["blocks"].append({"type": "chart", "title": "깨진 것", "chartType": "flowchart", "mermaid": "flowchart TD\n  ((("})
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
            page.wait_for_selector("#report .chart .diagram svg", timeout=10000)
            # 정상 차트들은 svg 로 렌더(>= ok_charts)
            page.wait_for_function(
                f"document.querySelectorAll('#report .chart .diagram svg').length >= {ok_charts}",
                timeout=10000,
            )
            svgs = page.locator("#report .chart .diagram svg").count()
            assert svgs >= ok_charts, f"svg {svgs} < {ok_charts}"
            # 마크다운 섹션도 함께 렌더(보고서 본문)
            assert page.locator("#report .md").count() >= 4, "markdown sections missing"
            # 인라인 순서: 첫 자식이 마크다운(개요), 차트와 마크다운이 교차
            kinds = page.eval_on_selector_all("#report > *", "els => els.map(e => e.className)")
            assert kinds[0] == "md", f"first block should be markdown, got {kinds[:1]}"
            assert "chart" in kinds and "md" in kinds, "blocks not interleaved"
            # 타입별 실제 렌더 확인(어골도 flowchart + 시퀀스)
            body = page.locator("#report").inner_text()
            assert "PaymentAPI" in body, "sequence diagram not rendered"
            # 에러 격리: 깨진 차트는 .error 1개, 페이지 스크립트 에러 없음
            assert page.locator(".diagram .error").count() == 1, "broken chart should isolate to one error"
            assert errs == [], f"page errors: {errs}"
            browser.close()
        print("SMOKE OK")
    finally:
        proc.terminate()
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

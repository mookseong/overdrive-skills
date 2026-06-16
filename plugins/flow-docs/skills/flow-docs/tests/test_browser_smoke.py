"""flow-docs 브라우저 스모크: blocks 보고서(PRD 섹션 + 인라인 차트) 렌더 + 에러 격리.
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
SAMPLE = HERE.parent / "examples" / "sample-prd.json"
PORT = 8796


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
    data = work / "prd.json"
    doc = json.loads(SAMPLE.read_text(encoding="utf-8"))
    ok_charts = sum(1 for b in doc["blocks"] if b.get("type") == "chart")
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
            page.wait_for_function(
                f"document.querySelectorAll('#report .chart .diagram svg').length >= {ok_charts}",
                timeout=10000,
            )
            svgs = page.locator("#report .chart .diagram svg").count()
            assert svgs >= ok_charts, f"svg {svgs} < {ok_charts}"
            assert page.locator("#report .md").count() >= 6, "PRD sections missing"
            body = page.locator("#report").inner_text()
            # PRD 구조 섹션 + 마인드맵(네이티브) 렌더 확인
            assert "문제 정의" in body, "PRD section missing"
            assert "ASIS" in body, "ASIS-TOBE section missing"
            assert "노쇼 원인" in body, "mindmap not rendered"
            assert page.locator(".diagram .error").count() == 1, "broken chart should isolate to one error"
            assert errs == [], f"page errors: {errs}"
            browser.close()
        print("SMOKE OK")
    finally:
        proc.terminate()
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

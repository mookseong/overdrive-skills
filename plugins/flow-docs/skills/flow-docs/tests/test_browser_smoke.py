"""flow-docs 브라우저 왕복 스모크: 렌더→선택→편집→저장→영속.
실행: python3 test_browser_smoke.py   (성공 시 'SMOKE OK', exit 0)
"""
import json
import os
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
PORT = 8791


def wait_up(url, tries=50):
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
    shutil.copy(SAMPLE, data)
    proc = subprocess.Popen([sys.executable, str(VIEWER / "serve.py"), str(data), "--port", str(PORT)])
    try:
        assert wait_up(f"http://127.0.0.1:{PORT}/api/data"), "server did not start"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{PORT}/")
            # 1) 다이어그램 렌더 (sample 엣지 라벨에 괄호가 있어 Mermaid 괄호 처리 회귀도 함께 검증)
            page.wait_for_selector("#diagram svg", timeout=10000)
            assert page.locator("#diagram .error").count() == 0, "diagram render error (Mermaid label?)"
            assert page.locator("#node-list .node-item").count() == 3, "node list not rendered"
            # 2) 선택(목록) → detail 표시
            page.locator('#node-list .node-item[data-id="n1"]').click()
            page.wait_for_selector("#detail-panel h3")
            assert "장바구니" in page.locator("#detail-panel").inner_text()
            # 2b) 선택(다이어그램 SVG 노드 클릭) → detail 갱신 (Mermaid click 디렉티브 + bindFunctions)
            page.locator("#diagram svg .node", has_text="결제수단 선택").first.click()
            page.wait_for_function(
                "document.getElementById('detail-panel').innerText.includes('결제수단 선택')",
                timeout=5000,
            )
            # 3) 편집: 첫 노드 라벨 변경 → 저장
            label_input = page.locator('.edit-row input[data-k="label"]').first
            label_input.fill("장바구니(변경)")
            label_input.dispatch_event("change")
            page.locator("#save-btn").click()
            page.wait_for_function("document.getElementById('save-status').textContent.includes('저장됨')", timeout=5000)
            # 4) 새로고침 → 영속 확인
            page.reload()
            page.wait_for_selector("#node-list .node-item")
            assert "장바구니(변경)" in page.locator("#node-list").inner_text(), "edit not persisted"
            browser.close()
        saved = json.loads(data.read_text(encoding="utf-8"))
        assert saved["nodes"][0]["label"] == "장바구니(변경)", "file not updated"
        print("SMOKE OK")
    finally:
        proc.terminate()
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

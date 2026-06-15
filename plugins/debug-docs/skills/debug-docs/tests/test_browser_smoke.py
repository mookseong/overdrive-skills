"""debug-docs 브라우저 왕복 스모크: 렌더(상태색)→선택→상태변경→저장→영속.
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
PORT = 8793


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
    shutil.copy(SAMPLE, data)
    proc = subprocess.Popen([sys.executable, str(VIEWER / "serve.py"), str(data), "--port", str(PORT)])
    try:
        assert wait_up(f"http://127.0.0.1:{PORT}/api/data"), "server did not start"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{PORT}/")
            # 1) 렌더 + 에러 없음
            page.wait_for_selector("#diagram svg", timeout=10000)
            assert page.locator("#diagram .error").count() == 0, "render error"
            assert page.locator("#node-list .node-item").count() == 5, "node list not rendered"
            # 1b) 상태 색 클래스 적용 확인(확정/기각). vendored Mermaid가 class를 노드 <g>에 안 붙이고
            #     <style>로만 적용하면 이 셀렉터가 0 → 그 경우 노드 fill 계산값으로 검증하도록 교체(아래 Expected NOTE).
            assert page.locator("#diagram svg .s_confirm").count() >= 1, "confirm status color missing"
            assert page.locator("#diagram svg .s_reject").count() >= 1, "reject status color missing"
            # 1c) Mermaid 라벨 이스케이프 회귀 가드: 노드 라벨 요소만 읽어(<style> 블록 오탐 방지)
            #     특수문자(" < > #)가 엔티티로 먹히거나 태그로 스트립되지 않고 리터럴로 살아남는지 검증.
            node_labels = page.eval_on_selector_all(
                "#diagram svg .nodeLabel", "els => els.map(e => e.textContent)"
            )
            joined = "".join(node_labels)
            assert '"List<int>"' in joined, "quote/angle-bracket escaping regression (#1 quotes, <tag> strip)"
            assert "#504;" in joined, "hash entity escaping regression (#2)"
            # 2) 노드 선택 → 증거 + 상태 배지
            page.locator('#node-list .node-item[data-id="h3"]').click()
            page.wait_for_selector("#detail-panel h3")
            assert "DB 커넥션 풀 고갈" in page.locator("#detail-panel").inner_text()
            assert "확정" in page.locator("#detail-panel .badge").inner_text()
            # 2b) 다이어그램 SVG 노드 직접 클릭(상태색 적용 노드) → 선택 동작 + classDef/click 공존 검증
            page.locator("#diagram svg .node", has_text="외부 PG 타임아웃").first.click()
            page.wait_for_function(
                "document.getElementById('detail-panel').innerText.includes('외부 PG 타임아웃')",
                timeout=5000,
            )
            # 3) 첫 노드(sym) 상태 변경 → 저장
            sel = page.locator('.edit-row select[data-k="status"]').first
            sel.select_option("조사중")
            page.locator("#save-btn").click()
            page.wait_for_function("document.getElementById('save-status').textContent.includes('저장됨')", timeout=5000)
            # 4) 새로고침 → 영속
            page.reload()
            page.wait_for_selector("#node-list .node-item")
            assert "[조사중]" in page.locator('#node-list .node-item[data-id="sym"]').inner_text(), "status not persisted"
            browser.close()
        saved = json.loads(data.read_text(encoding="utf-8"))
        assert saved["nodes"][0]["status"] == "조사중", "file status not updated"
        print("SMOKE OK")
    finally:
        proc.terminate()
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

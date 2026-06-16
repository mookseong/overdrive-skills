import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

VIEWER = Path(__file__).resolve().parent.parent / "viewer"
sys.path.insert(0, str(VIEWER))
import serve  # noqa: E402

SAMPLE = {
    "title": "T",
    "overview": "ov",
    "diagrams": [
        {"title": "flow", "type": "sequence", "mermaid": "sequenceDiagram\n  A->>B: x"},
        {"title": "tree", "type": "flowchart", "mermaid": "flowchart TD\n  a-->b"},
    ],
}


class TestServer(unittest.TestCase):
    def setUp(self):
        self.appdir = tempfile.mkdtemp()
        (Path(self.appdir) / "index.html").write_text("<html>debug-docs</html>", encoding="utf-8")
        (Path(self.appdir) / "app.js").write_text("// app", encoding="utf-8")
        os.makedirs(Path(self.appdir) / "vendor")
        (Path(self.appdir) / "vendor" / "mermaid.min.js").write_text("// mermaid", encoding="utf-8")
        fd, self.data = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        Path(self.data).write_text(json.dumps(SAMPLE, ensure_ascii=False), encoding="utf-8")
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve.make_handler(self.data, app_dir=self.appdir))
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def tearDown(self):
        self.httpd.shutdown()
        os.unlink(self.data)
        shutil.rmtree(self.appdir, ignore_errors=True)

    def url(self, p):
        return f"http://127.0.0.1:{self.port}{p}"

    def get(self, p):
        with urllib.request.urlopen(self.url(p)) as r:
            return r.status, r.read()

    def test_index(self):
        st, body = self.get("/")
        self.assertEqual(st, 200)
        self.assertIn(b"debug-docs", body)

    def test_static_app_js(self):
        st, _ = self.get("/app.js")
        self.assertEqual(st, 200)

    def test_static_vendor(self):
        st, _ = self.get("/vendor/mermaid.min.js")
        self.assertEqual(st, 200)

    def test_get_data(self):
        st, body = self.get("/api/data")
        self.assertEqual(st, 200)
        obj = json.loads(body)
        self.assertEqual(obj["title"], "T")
        self.assertEqual(len(obj["diagrams"]), 2)

    def test_missing_asset_404(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(self.url("/nope.js"))
        self.assertEqual(cm.exception.code, 404)

    def test_post_not_supported(self):
        # 보기 전용 서버: 저장(POST)은 없다.
        req = urllib.request.Request(self.url("/api/data"), data=b"{}",
                                     method="POST", headers={"Content-Type": "application/json"})
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertIn(cm.exception.code, (404, 405, 501))
        # 데이터 파일은 그대로
        self.assertEqual(json.loads(Path(self.data).read_text(encoding="utf-8"))["title"], "T")

    def test_traversal_blocked(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(self.url("/../../../../etc/passwd"))
        self.assertIn(cm.exception.code, (403, 404))


if __name__ == "__main__":
    unittest.main()

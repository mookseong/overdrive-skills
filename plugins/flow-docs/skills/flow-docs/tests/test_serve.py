import json
import os
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
    "nodes": [
        {"id": "n1", "label": "A", "detail": "d1"},
        {"id": "n2", "label": "B", "detail": "d2"},
    ],
    "edges": [{"from": "n1", "to": "n2", "label": "go"}],
}


class TestValidate(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(serve.validate_prd(SAMPLE), [])

    def test_missing_key(self):
        bad = {"title": "t", "nodes": [], "edges": []}  # overview 없음
        self.assertTrue(any("overview" in e for e in serve.validate_prd(bad)))

    def test_node_without_id(self):
        bad = dict(SAMPLE, nodes=[{"label": "x"}])
        self.assertTrue(any("id/label" in e for e in serve.validate_prd(bad)))

    def test_edge_unknown_node(self):
        bad = dict(SAMPLE, edges=[{"from": "n1", "to": "zzz"}])
        self.assertTrue(any("zzz" in e for e in serve.validate_prd(bad)))


class TestServer(unittest.TestCase):
    def setUp(self):
        self.appdir = tempfile.mkdtemp()
        (Path(self.appdir) / "index.html").write_text("<html>flow-docs</html>", encoding="utf-8")
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

    def url(self, p):
        return f"http://127.0.0.1:{self.port}{p}"

    def get(self, p):
        with urllib.request.urlopen(self.url(p)) as r:
            return r.status, r.read()

    def test_index(self):
        st, body = self.get("/")
        self.assertEqual(st, 200)
        self.assertIn(b"flow-docs", body)

    def test_static_app_js(self):
        st, _ = self.get("/app.js")
        self.assertEqual(st, 200)

    def test_static_vendor(self):
        st, _ = self.get("/vendor/mermaid.min.js")
        self.assertEqual(st, 200)

    def test_get_data(self):
        st, body = self.get("/api/data")
        self.assertEqual(st, 200)
        self.assertEqual(json.loads(body)["title"], "T")

    def test_post_valid_roundtrip(self):
        new = dict(SAMPLE, title="CHANGED")
        req = urllib.request.Request(self.url("/api/data"), data=json.dumps(new).encode(),
                                     method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(Path(self.data).read_text(encoding="utf-8"))["title"], "CHANGED")

    def test_post_invalid_json_unchanged(self):
        req = urllib.request.Request(self.url("/api/data"), data=b"{not json",
                                     method="POST", headers={"Content-Type": "application/json"})
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(json.loads(Path(self.data).read_text(encoding="utf-8"))["title"], "T")

    def test_post_invalid_schema_unchanged(self):
        bad = {"title": "x"}  # nodes/edges/overview 없음
        req = urllib.request.Request(self.url("/api/data"), data=json.dumps(bad).encode(),
                                     method="POST", headers={"Content-Type": "application/json"})
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(json.loads(Path(self.data).read_text(encoding="utf-8"))["title"], "T")

    def test_traversal_blocked(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(self.url("/../../../../etc/passwd"))
        self.assertIn(cm.exception.code, (403, 404))


if __name__ == "__main__":
    unittest.main()

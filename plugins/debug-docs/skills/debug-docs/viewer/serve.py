#!/usr/bin/env python3
"""debug-docs 로컬 서버: 정적 앱 서빙 + debug.json 읽기/쓰기.

GET  /            -> app/index.html
GET  /<asset>     -> app/ 하위 정적 파일 (traversal 차단)
GET  /api/data    -> debug.json 내용
POST /api/data    -> 검증 후 debug.json에 원자적 저장
"""
import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent / "app"

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}


def validate_prd(obj):
    """prd 데이터 검증. 실패 사유 리스트 반환(빈 리스트=유효)."""
    if not isinstance(obj, dict):
        return ["최상위가 객체가 아님"]
    errors = []
    for key in ("title", "overview", "nodes", "edges"):
        if key not in obj:
            errors.append(f"필수 키 누락: {key}")
    nodes = obj.get("nodes", [])
    edges = obj.get("edges", [])
    if not isinstance(nodes, list):
        errors.append("nodes는 배열이어야 함")
        nodes = []
    if not isinstance(edges, list):
        errors.append("edges는 배열이어야 함")
        edges = []
    ids = set()
    for i, n in enumerate(nodes):
        if not isinstance(n, dict) or "id" not in n or "label" not in n:
            errors.append(f"노드[{i}]에 id/label 필요")
            continue
        ids.add(n["id"])
    for i, e in enumerate(edges):
        if not isinstance(e, dict) or "from" not in e or "to" not in e:
            errors.append(f"엣지[{i}]에 from/to 필요")
            continue
        if e["from"] not in ids:
            errors.append(f"엣지[{i}] from '{e['from']}'가 노드에 없음")
        if e["to"] not in ids:
            errors.append(f"엣지[{i}] to '{e['to']}'가 노드에 없음")
    return errors


def make_handler(data_path, app_dir=APP_DIR):
    data_path = Path(data_path).resolve()
    app_dir = Path(app_dir).resolve()

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/api/data":
                try:
                    body = data_path.read_bytes()
                except OSError:
                    self._send(404, b'{"error":"data not found"}', CONTENT_TYPES[".json"])
                    return
                self._send(200, body, CONTENT_TYPES[".json"])
                return
            rel = "index.html" if path == "/" else path.lstrip("/")
            target = (app_dir / rel).resolve()
            if target != app_dir and not str(target).startswith(str(app_dir) + os.sep):
                self._send(403, b"forbidden")
                return
            if not target.is_file():
                self._send(404, b"not found")
                return
            ctype = CONTENT_TYPES.get(target.suffix, "application/octet-stream")
            self._send(200, target.read_bytes(), ctype)

        def do_POST(self):
            if self.path.split("?", 1)[0] != "/api/data":
                self._send(404, b"not found")
                return
            length = max(0, int(self.headers.get("Content-Length", 0) or 0))
            raw = self.rfile.read(length) if length else b""
            try:
                obj = json.loads(raw)
            except (ValueError, TypeError):
                self._send(400, b'{"error":"invalid json"}', CONTENT_TYPES[".json"])
                return
            errs = validate_prd(obj)
            if errs:
                body = json.dumps({"error": "validation", "details": errs}, ensure_ascii=False).encode()
                self._send(400, body, CONTENT_TYPES[".json"])
                return
            tmp = data_path.with_suffix(data_path.suffix + ".tmp")
            tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(tmp, data_path)
            self._send(200, b'{"ok":true}', CONTENT_TYPES[".json"])

        def log_message(self, *args):
            pass

    return Handler


def main(argv=None):
    p = argparse.ArgumentParser(description="debug-docs 로컬 서버")
    p.add_argument("data", help="debug.json 경로")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args(argv)
    httpd = ThreadingHTTPServer((args.host, args.port), make_handler(args.data))
    print(f"debug-docs: http://localhost:{args.port}  (data: {args.data})")
    print("종료: Ctrl+C")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    main()

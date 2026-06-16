#!/usr/bin/env python3
"""보고서 뷰어 로컬 서버(보기 전용): 정적 앱 + 데이터(JSON) 서빙.

GET  /            -> app/index.html
GET  /<asset>     -> app/ 하위 정적 파일 (traversal 차단)
GET  /api/data    -> 데이터 JSON 내용
저장(POST)은 없다 — 보고서와 차트를 빠르게 보여주는 뷰어다.
"""
import argparse
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
            try:
                target = (app_dir / rel).resolve()
                if target != app_dir and not str(target).startswith(str(app_dir) + os.sep):
                    self._send(403, b"forbidden")
                    return
                if not target.is_file():
                    self._send(404, b"not found")
                    return
                ctype = CONTENT_TYPES.get(target.suffix.lower(), "application/octet-stream")
                self._send(200, target.read_bytes(), ctype)
            except (OSError, ValueError):
                # 잘못된 경로(널바이트 등)·읽기 직전 삭제(TOCTOU) 등 → 404로 안전 응답.
                self._send(404, b"not found")

        def log_message(self, *args):
            pass

    return Handler


def main(argv=None):
    p = argparse.ArgumentParser(description="보고서 뷰어 로컬 서버(보기 전용)")
    p.add_argument("data", help="데이터 JSON 경로(예: debug.json / prd.json)")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args(argv)
    httpd = ThreadingHTTPServer((args.host, args.port), make_handler(args.data))
    print(f"report viewer: http://localhost:{args.port}  (data: {args.data})")
    print("종료: Ctrl+C")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    main()

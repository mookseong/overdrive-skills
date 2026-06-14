import json
import os
import subprocess
import sys
import tempfile
import unittest

from check_readability import check_readability

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_readability.py")

GOOD_DOC = """# 결제 모듈

이 모듈은 주문 결제를 처리한다. 백엔드 개발자가 결제 연동 시 사용한다.

## 사용 예시

```python
pay(order_id=1, amount=1000)
```
"""


def run_hook(file_path):
    payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": file_path}})
    p = subprocess.run([sys.executable, HOOK], input=payload,
                       capture_output=True, text=True)
    return p.returncode, p.stderr


class TestCheckReadability(unittest.TestCase):
    def test_good_doc_passes(self):
        self.assertEqual(check_readability(GOOD_DOC), [])

    def test_missing_summary(self):
        doc = "# 제목\n\n## 바로 상세\n\n```\nx\nx\n```\n"
        fails = check_readability(doc)
        self.assertTrue(any("상단 요약" in f for f in fails))

    def test_missing_code_block(self):
        doc = "# 제목\n\n요약 문장이 여기에 충분히 길게 들어간다 정말로요.\n\n## 섹션\n\n내용\n"
        fails = check_readability(doc)
        self.assertTrue(any("예시/코드블록" in f for f in fails))

    def test_wall_of_text(self):
        wall = "가" * 500
        doc = ("# 제목\n\n짧은 요약 문장이다 충분히 길게 적는다 정말로요.\n\n"
               "## 섹션\n\n" + wall + "\n\n```\nx\nx\n```\n")
        fails = check_readability(doc)
        self.assertTrue(any("벽글" in f for f in fails))


class TestHookProcess(unittest.TestCase):
    def test_target_bad_doc_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            docs = os.path.join(d, "docs")
            os.makedirs(docs)
            path = os.path.join(docs, "bad.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write("# 제목\n\n## 바로 상세\n\n내용만 있음\n")
            rc, err = run_hook(path)
            self.assertEqual(rc, 2)
            self.assertIn("가독성", err)

    def test_target_good_doc_exits_0(self):
        with tempfile.TemporaryDirectory() as d:
            docs = os.path.join(d, "docs")
            os.makedirs(docs)
            path = os.path.join(docs, "good.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(GOOD_DOC)
            rc, err = run_hook(path)
            self.assertEqual(rc, 0)
            self.assertEqual(err, "")

    def test_non_md_passes(self):
        rc, err = run_hook("/tmp/does-not-matter.py")
        self.assertEqual(rc, 0)

    def test_non_target_md_passes(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                         encoding="utf-8") as f:
            f.write("# 제목\n\n## 상세\n\n내용만 있음\n")
            path = f.name
        try:
            rc, err = run_hook(path)
            self.assertEqual(rc, 0)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()

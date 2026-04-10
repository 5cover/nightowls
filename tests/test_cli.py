from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import git

from nightowls.cli import _resolve_chart_title, main


class CliTests(unittest.TestCase):
    def test_chart_title_resolution_prefers_custom_title(self) -> None:
        title = _resolve_chart_title("My title", "repo")
        self.assertEqual(title, "My title")

    def test_chart_title_resolution_uses_repo_name(self) -> None:
        title = _resolve_chart_title(None, "repo")
        self.assertEqual(title, "Commits by hour (stacked by member) - repo")

    def test_chart_title_resolution_fallback(self) -> None:
        title = _resolve_chart_title(None, None)
        self.assertEqual(title, "Commits by hour (stacked by member)")

    def test_members_output_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = git.Repo.init(root)

            file_path = root / "a.txt"
            file_path.write_text("hello\n", encoding="utf-8")
            repo.index.add([str(file_path)])
            actor = git.Actor("Alice", "alice@example.com")
            repo.index.commit(
                "first",
                author=actor,
                committer=actor,
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main([str(root), "--output-format", "members"])

            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["members"][0][0], "Alice")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nightowls.config import resolve_config
from nightowls.errors import ConfigError


class ConfigTests(unittest.TestCase):
    def test_precedence_cli_overrides_explicit_and_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nightowls.json").write_text(
                json.dumps(
                    {
                        "timezone": "local",
                        "output": {"format": "json", "path": "repo.json"},
                    }
                ),
                encoding="utf-8",
            )
            explicit = root / "custom.json"
            explicit.write_text(
                json.dumps(
                    {
                        "timezone": "utc",
                        "output": {"format": "png"},
                        "filters": {"no_merges": True},
                    }
                ),
                encoding="utf-8",
            )

            cli_overrides = {
                "output": {"format": "config", "path": "cli.json"},
            }

            with patch("nightowls.config._find_repo_root", return_value=root):
                config = resolve_config(
                    repo_path=root,
                    explicit_config_path=explicit,
                    cli_overrides=cli_overrides,
                )

            self.assertEqual(config["timezone"], "utc")
            self.assertEqual(config["output"]["format"], "config")
            self.assertEqual(config["output"]["path"], "cli.json")
            self.assertTrue(config["filters"]["no_merges"])

    def test_invalid_config_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = root / "bad.json"
            bad.write_text(json.dumps({"timezone": "mars"}), encoding="utf-8")

            with patch("nightowls.config._find_repo_root", return_value=None):
                with self.assertRaises(ConfigError):
                    resolve_config(
                        repo_path=root,
                        explicit_config_path=bad,
                        cli_overrides={},
                    )


if __name__ == "__main__":
    unittest.main()

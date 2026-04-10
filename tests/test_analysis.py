from __future__ import annotations

import unittest
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from nightowls.analysis import analyze_commits


@dataclass
class Actor:
    name: str
    email: str


@dataclass
class Commit:
    author: Actor
    committer: Actor
    authored_datetime: datetime
    committed_datetime: datetime


class AnalysisTests(unittest.TestCase):
    @staticmethod
    def _base_config() -> dict[str, object]:
        return {
            "timezone": "local",
            "identity_source": "author",
            "member_sort": "commit_count",
            "output": {"format": "json", "path": None},
            "chart": {"title": None},
            "filters": {"since": None, "until": None, "branch": None, "no_merges": False},
            "members": [],
        }

    def test_utc_conversion_changes_bucket(self) -> None:
        commit = Commit(
            author=Actor(name="A", email="a@example.com"),
            committer=Actor(name="A", email="a@example.com"),
            authored_datetime=datetime(2026, 1, 1, 23, 0, tzinfo=timezone(timedelta(hours=-2))),
            committed_datetime=datetime(2026, 1, 1, 23, 0, tzinfo=timezone(timedelta(hours=-2))),
        )
        base_config = self._base_config()

        local_result, _ = analyze_commits([commit], {**base_config, "timezone": "local"})
        utc_result, _ = analyze_commits([commit], {**base_config, "timezone": "utc"})

        self.assertEqual(local_result.counts_by_member["A"][23], 1)
        self.assertEqual(utc_result.counts_by_member["A"][1], 1)

    def test_default_member_sort_is_commit_count(self) -> None:
        commits = [
            Commit(
                author=Actor(name="zeta", email="z@example.com"),
                committer=Actor(name="zeta", email="z@example.com"),
                authored_datetime=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
                committed_datetime=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            ),
            Commit(
                author=Actor(name="zeta", email="z@example.com"),
                committer=Actor(name="zeta", email="z@example.com"),
                authored_datetime=datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
                committed_datetime=datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
            ),
            Commit(
                author=Actor(name="alpha", email="a@example.com"),
                committer=Actor(name="alpha", email="a@example.com"),
                authored_datetime=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
                committed_datetime=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
            ),
        ]

        config = self._base_config()

        result, _ = analyze_commits(commits, config)
        self.assertEqual(list(result.counts_by_member.keys()), ["zeta", "alpha"])

    def test_member_sort_alphabetical(self) -> None:
        commits = [
            Commit(
                author=Actor(name="zeta", email="z@example.com"),
                committer=Actor(name="zeta", email="z@example.com"),
                authored_datetime=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
                committed_datetime=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            ),
            Commit(
                author=Actor(name="alpha", email="a@example.com"),
                committer=Actor(name="alpha", email="a@example.com"),
                authored_datetime=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
                committed_datetime=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
            ),
        ]
        config = {**self._base_config(), "member_sort": "alphabetical"}
        result, _ = analyze_commits(commits, config)
        self.assertEqual(list(result.counts_by_member.keys()), ["alpha", "zeta"])

    def test_member_sort_custom_list(self) -> None:
        commits = [
            Commit(
                author=Actor(name="zeta", email="z@example.com"),
                committer=Actor(name="zeta", email="z@example.com"),
                authored_datetime=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
                committed_datetime=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            ),
            Commit(
                author=Actor(name="alpha", email="a@example.com"),
                committer=Actor(name="alpha", email="a@example.com"),
                authored_datetime=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
                committed_datetime=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
            ),
            Commit(
                author=Actor(name="beta", email="b@example.com"),
                committer=Actor(name="beta", email="b@example.com"),
                authored_datetime=datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc),
                committed_datetime=datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc),
            ),
        ]
        config = {**self._base_config(), "member_sort": ["beta", "alpha"]}
        result, _ = analyze_commits(commits, config)
        self.assertEqual(list(result.counts_by_member.keys()), ["beta", "alpha", "zeta"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .members import Identity, identity_from_commit, resolve_member_name
from .types import ConfigDict


@dataclass
class AnalysisResult:
    counts_by_member: dict[str, list[int]]
    total_commits: int


def _normalize_datetime(value: datetime, timezone_mode: str) -> datetime:
    dt = value
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    if timezone_mode == "utc":
        return dt.astimezone(UTC)

    return dt


def _identity_datetime(commit: Any, identity_source: str) -> datetime:
    if identity_source == "committer":
        return commit.committed_datetime
    return commit.authored_datetime


def _commit_weight(commit: Any, metric: str) -> int:
    if metric == "lines_changed":
        total = getattr(getattr(commit, "stats", None), "total", {}) or {}
        insertions = total.get("insertions", 0)
        deletions = total.get("deletions", 0)
        return int(insertions) + int(deletions)
    return 1


def _ordered_member_counts(
    counts: dict[str, list[int]],
    member_sort: str | list[str],
) -> dict[str, list[int]]:
    if isinstance(member_sort, list):
        rank = {name: index for index, name in enumerate(member_sort)}
        return dict(
            sorted(
                counts.items(),
                key=lambda item: (rank.get(item[0], len(rank)), item[0].lower()),
            )
        )

    if member_sort == "alphabetical":
        return dict(sorted(counts.items(), key=lambda item: item[0].lower()))

    # default and fallback: highest commit count first
    return dict(
        sorted(
            counts.items(),
            key=lambda item: (-sum(item[1]), item[0].lower()),
        )
    )


def analyze_commits(commits: list[Any], config: ConfigDict) -> tuple[AnalysisResult, list[Identity]]:
    counts: dict[str, list[int]] = defaultdict(lambda: [0] * 24)
    identities: list[Identity] = []

    for commit in commits:
        identity = identity_from_commit(commit, config["identity_source"])
        identities.append(identity)

        member_name = resolve_member_name(identity, config["members"])
        event_dt = _normalize_datetime(
            _identity_datetime(commit, config["identity_source"]),
            config["timezone"],
        )
        counts[member_name][event_dt.hour] += _commit_weight(commit, config["metric"])

    ordered_counts = _ordered_member_counts(counts, config["member_sort"])

    return AnalysisResult(counts_by_member=ordered_counts, total_commits=len(commits)), identities


def analysis_to_json(
    result: AnalysisResult,
    *,
    timezone_mode: str,
    identity_source: str,
    metric: str,
) -> dict[str, Any]:
    totals_by_hour = [0] * 24
    for counts in result.counts_by_member.values():
        for hour, value in enumerate(counts):
            totals_by_hour[hour] += value

    return {
        "metadata": {
            "timezone": timezone_mode,
            "identity_source": identity_source,
            "metric": metric,
            "total_commits": result.total_commits,
        },
        "hours": list(range(24)),
        "totals_by_hour": totals_by_hour,
        "members": [
            {
                "member": member,
                "counts_by_hour": counts,
                "total": sum(counts),
            }
            for member, counts in result.counts_by_member.items()
        ],
    }

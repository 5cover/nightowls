from __future__ import annotations

from typing import Any, Literal, TypedDict


TimezoneMode = Literal["local", "utc"]
OutputFormat = Literal["json", "png", "config", "members"]
IdentitySource = Literal["author", "committer"]
MemberSortMode = Literal["alphabetical", "commit_count"] | list[str]


class RegexMatcher(TypedDict):
    regex: str


MatcherValue = str | RegexMatcher | None


class MemberMatcher(TypedDict, total=False):
    name: MatcherValue
    email: MatcherValue


class OutputConfig(TypedDict):
    format: OutputFormat
    path: str | None


class ChartConfig(TypedDict):
    title: str | None


class FiltersConfig(TypedDict):
    since: str | None
    until: str | None
    branch: str | None
    no_merges: bool


class ConfigDict(TypedDict):
    timezone: TimezoneMode
    identity_source: IdentitySource
    member_sort: MemberSortMode
    output: OutputConfig
    chart: ChartConfig
    filters: FiltersConfig
    members: list[list[Any]]

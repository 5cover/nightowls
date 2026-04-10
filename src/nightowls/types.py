from __future__ import annotations

from typing import Any, Literal, TypedDict


TimezoneMode = Literal["local", "utc"]
OutputFormat = Literal["json", "png", "config", "members"]
IdentitySource = Literal["author", "committer"]


class RegexMatcher(TypedDict):
    regex: str


MatcherValue = str | RegexMatcher | None


class MemberMatcher(TypedDict, total=False):
    name: MatcherValue
    email: MatcherValue


class OutputConfig(TypedDict):
    format: OutputFormat
    path: str | None


class FiltersConfig(TypedDict):
    since: str | None
    until: str | None
    branch: str | None
    no_merges: bool


class ConfigDict(TypedDict):
    timezone: TimezoneMode
    identity_source: IdentitySource
    output: OutputConfig
    filters: FiltersConfig
    members: list[list[Any]]

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .types import IdentitySource


@dataclass(frozen=True)
class Identity:
    name: str
    email: str


def _string_or_empty(value: str | None) -> str:
    return value or ""


def identity_from_commit(commit: Any, identity_source: IdentitySource) -> Identity:
    actor = commit.author if identity_source == "author" else commit.committer
    return Identity(name=_string_or_empty(actor.name), email=_string_or_empty(actor.email))


def _matches_value(rule_value: Any, actual: str) -> bool:
    if rule_value is None:
        return True

    if isinstance(rule_value, str):
        return actual == rule_value

    if isinstance(rule_value, dict):
        regex = rule_value.get("regex")
        if isinstance(regex, str):
            return re.search(regex, actual) is not None

    return False


def _matches_matcher(matcher: dict[str, Any], identity: Identity) -> bool:
    name_rule = matcher.get("name")
    email_rule = matcher.get("email")
    return _matches_value(name_rule, identity.name) and _matches_value(email_rule, identity.email)


def resolve_member_name(identity: Identity, member_rules: list[list[Any]]) -> str:
    for rule in member_rules:
        if len(rule) != 2:
            continue

        member_name = rule[0]
        matcher = rule[1]
        if not isinstance(member_name, str) or not isinstance(matcher, dict):
            continue

        if _matches_matcher(matcher, identity):
            return member_name

    return identity.name or identity.email or "unknown"


def bootstrap_member_rules(identities: Iterable[Identity]) -> list[list[Any]]:
    seen: set[tuple[str, str]] = set()
    entries: list[tuple[str, str, str]] = []

    for identity in identities:
        key = (identity.name, identity.email)
        if key in seen:
            continue

        seen.add(key)
        member_name = identity.name or identity.email or "unknown"
        entries.append((member_name, identity.name, identity.email))

    entries.sort(key=lambda item: (item[0].lower(), item[1].lower(), item[2].lower()))

    output: list[list[Any]] = []
    for member_name, name, email in entries:
        output.append([member_name, {"name": name, "email": email}])
    return output

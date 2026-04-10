from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from urllib.parse import urlparse

import git

from .errors import RepoError


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


def _repo_name_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    if name.endswith(".git"):
        name = name[:-4]
    name = name.strip()
    return name or None


@contextmanager
def open_repo(path_or_url: str) -> Iterator[tuple[git.Repo, Path, str | None]]:
    if _is_url(path_or_url):
        with TemporaryDirectory() as tmpdir:
            try:
                repo = git.Repo.clone_from(path_or_url, tmpdir)
            except git.GitCommandError as exc:
                raise RepoError(f"Failed to clone repository: {exc}") from exc
            yield repo, Path(tmpdir), _repo_name_from_url(path_or_url)
            return

    path = Path(path_or_url)
    try:
        repo = git.Repo(path, search_parent_directories=True)
    except (git.InvalidGitRepositoryError, git.NoSuchPathError) as exc:
        raise RepoError(str(exc)) from exc

    root = repo.working_tree_dir
    if root is None:
        raise RepoError("Bare repositories are not supported for local analysis")

    repo_name = Path(root).name.strip() or None
    yield repo, Path(root), repo_name


def iter_commits(repo: git.Repo, *, filters: dict[str, Any]) -> Iterator[git.Commit]:
    kwargs: dict[str, Any] = {}
    since = filters.get("since")
    until = filters.get("until")
    no_merges = filters.get("no_merges")

    if since:
        kwargs["since"] = since
    if until:
        kwargs["until"] = until
    if no_merges:
        kwargs["no_merges"] = True

    branch = filters.get("branch")
    rev = branch if branch else "HEAD"
    return repo.iter_commits(rev=rev, **kwargs)

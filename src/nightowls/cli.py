from __future__ import annotations

import argparse
import sys
from typing import Any

import git

from .analysis import analysis_to_json, analyze_commits
from .config import resolve_config
from .errors import ConfigError, RepoError
from .members import bootstrap_member_rules
from .outputs import emit_json, emit_png
from .repo import iter_commits, open_repo


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nightowls",
        description="Analyze git commit activity by hour with member mapping.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository path or clone URL")
    parser.add_argument("-c", "--config", help="Path to JSON config file")
    parser.add_argument("--timezone", choices=["local", "utc"], help="Timezone mode")
    parser.add_argument(
        "-f", "--output-format",
        choices=["json", "png", "config", "members"],
        help="Output format",
    )
    parser.add_argument("-o", "--output-path", help="Write output to this path")
    parser.add_argument("--chart-title", help="Custom chart title for PNG output")
    parser.add_argument(
        "--identity-source",
        choices=["author", "committer"],
        help="Choose whether identity/time is taken from author or committer",
    )
    parser.add_argument("--since", help="Only include commits after this date expression")
    parser.add_argument("--until", help="Only include commits before this date expression")
    parser.add_argument("--branch", help="Branch or revision to analyze (default: HEAD)")
    parser.add_argument("--no-merges", action="store_true", help="Exclude merge commits")
    return parser


def _build_cli_overrides(args: argparse.Namespace) -> dict[str, Any]:
    overrides: dict[str, Any] = {}

    if args.timezone is not None:
        overrides["timezone"] = args.timezone

    if args.identity_source is not None:
        overrides["identity_source"] = args.identity_source

    output: dict[str, Any] = {}
    if args.output_format is not None:
        output["format"] = args.output_format
    if args.output_path is not None:
        output["path"] = args.output_path
    if output:
        overrides["output"] = output

    if args.chart_title is not None:
        overrides["chart"] = {"title": args.chart_title}

    filters: dict[str, Any] = {}
    if args.since is not None:
        filters["since"] = args.since
    if args.until is not None:
        filters["until"] = args.until
    if args.branch is not None:
        filters["branch"] = args.branch
    if args.no_merges:
        filters["no_merges"] = True
    if filters:
        overrides["filters"] = filters

    return overrides


def _resolve_chart_title(config_title: str | None, repo_name: str | None) -> str:
    if config_title:
        return config_title
    if repo_name:
        return f"Commits by hour (stacked by member) - {repo_name}"
    return "Commits by hour (stacked by member)"


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        with open_repo(args.path) as (repo, repo_root, repo_name):
            config = resolve_config(
                repo_path=repo_root,
                explicit_config_path=args.config,
                cli_overrides=_build_cli_overrides(args),
            )

            output_format = config["output"]["format"]
            output_path = config["output"]["path"]

            if output_format == "config":
                emit_json(config, output_path)
                return 0

            commits = list(iter_commits(repo, filters=config["filters"]))
            analysis_result, identities = analyze_commits(commits, config)

            if output_format == "json":
                emit_json(
                    analysis_to_json(
                        analysis_result,
                        timezone_mode=config["timezone"],
                        identity_source=config["identity_source"],
                    ),
                    output_path,
                )
            elif output_format == "png":
                emit_png(
                    analysis_result,
                    output_path,
                    title=_resolve_chart_title(config["chart"]["title"], repo_name),
                )
            elif output_format == "members":
                emit_json({"members": bootstrap_member_rules(identities)}, output_path)
            else:
                raise ConfigError(f"Unsupported output format: {output_format}")

            return 0
    except (ConfigError, RepoError, git.GitCommandError) as exc:
        print(f"nightowls: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

# NightOwls

[![Tests](https://github.com/5cover/nightowls/actions/workflows/ci.yml/badge.svg)](https://github.com/5cover/nightowls/actions/workflows/ci.yml)
[![Package Check](https://github.com/5cover/nightowls/actions/workflows/package.yml/badge.svg)](https://github.com/5cover/nightowls/actions/workflows/package.yml)
[![Publish](https://github.com/5cover/nightowls/actions/workflows/publish.yml/badge.svg)](https://github.com/5cover/nightowls/actions/workflows/publish.yml)
[![PyPI version](https://badge.fury.io/py/nightowls.svg)](https://badge.fury.io/py/nightowls)
![PyPI - Downloads](https://img.shields.io/pypi/dm/nightowls)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

NightOwls is a Python CLI for analyzing Git commit activity by hour of day.

It supports:

- JSON analysis output
- stacked bar chart PNG output (x: hour, y: commit count, stacked by member)
- resolved config output
- bootstrapped members map output

## Install

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
PYTHONPATH=src python -m nightowls --help
```

Or after install:

```bash
nightowls --help
```

## Configuration Sources And Precedence

NightOwls merges configuration in this order:

1. CLI options
2. `-c /path/to/config.json`
3. `nightowls.json` in repository root
4. internal defaults

## JSON Schema

Schema file in repo:

- `src/nightowls/schemas/nightowls.schema.json`

Raw URL (for `$schema`):

- `https://raw.githubusercontent.com/5cover/nightowls/main/src/nightowls/schemas/nightowls.schema.json`

Example header in `nightowls.json`:

```json
{
  "$schema": "https://raw.githubusercontent.com/5cover/nightowls/main/src/nightowls/schemas/nightowls.schema.json"
}
```

## `nightowls.json` Format

```json
{
  "$schema": "https://raw.githubusercontent.com/5cover/nightowls/main/src/nightowls/schemas/nightowls.schema.json",
  "timezone": "local",
  "identity_source": "author",
  "metric": "commit_count",
  "member_sort": "commit_count",
  "output": {
    "format": "json",
    "path": null
  },
  "chart": {
    "title": null
  },
  "filters": {
    "since": null,
    "until": null,
    "branch": null,
    "no_merges": false
  },
  "members": [
    ["Raphael", { "name": "Scover", "email": "thediscover22450@gmail.com" }],
    ["Romain", { "name": "Soladoc" }],
    ["Noreply", { "email": { "regex": "@users\\.noreply\\.github\\.com$" } }],
    ["Unknown", {}]
  ]
}
```

## Members Mapping Semantics

`members` is an ordered list of pairs:

```json
[member_name, matcher]
```

Rules:

- first match wins
- `matcher.name` and `matcher.email` are optional
- missing or `null` means wildcard for that field
- string value means exact match
- `{ "regex": "..." }` means regex match
- if nothing matches, NightOwls falls back to the git actor name

## Aggregation Metric

`metric` controls bar segment size and JSON totals:

- `"commit_count"` (default): each commit contributes `1`
- `"lines_changed"`: each commit contributes `insertions + deletions`

## Member Ordering

`member_sort` controls member order in JSON output and chart stacking/color assignment.

- `"commit_count"` (default): descending by aggregated metric total, then alphabetical
- `"alphabetical"`: ascending by member name
- `["name1", "name2", ...]`: custom order; members not listed are appended alphabetically

## Chart Title Behavior

- If `chart.title` (or `--chart-title`) is set, it is used.
- Otherwise title is `Commits by hour (stacked by member) - {repo name}` when repo name is available.
- Final fallback is `Commits by hour (stacked by member)`.

## CLI Options

```text
nightowls [path]
  -c, --config PATH
  --timezone {local,utc}
  --metric {commit_count,lines_changed}
  --output-format {json,png,config,members}
  --output-path PATH
  --chart-title TEXT
  --identity-source {author,committer}
  --since EXPR
  --until EXPR
  --branch REV
  --no-merges
```

## Examples

JSON output:

```bash
nightowls . --output-format json
```

PNG output:

```bash
nightowls . --output-format png --output-path out.png
```

PNG output weighted by changed lines:

```bash
nightowls . --output-format png --metric lines_changed --output-path out.png
```

PNG output with custom title:

```bash
nightowls . --output-format png --chart-title "Night activity overview"
```

Resolved config output:

```bash
nightowls . --output-format config
```

Bootstrap members map:

```bash
nightowls . --output-format members > members.json
```

Use custom config:

```bash
nightowls . -c ./nightowls.json --output-format json
```

## Build

```bash
python -m build
```

## Publish To PyPI

- The `Publish` workflow runs on tags matching `v*` (for example `v1.0.1`).
- Configure PyPI Trusted Publishing for this repository, then create and push a version tag:

```bash
git tag v1.0.1
git push origin v1.0.1
```

## Test

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
```

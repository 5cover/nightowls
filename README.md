# NightOwls

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
  "output": {
    "format": "json",
    "path": null
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

## CLI Options

```text
nightowls [path]
  -c, --config PATH
  --timezone {local,utc}
  --output-format {json,png,config,members}
  --output-path PATH
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

## Test

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
```

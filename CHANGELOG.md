# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-04-10

### Added
- Proper Python package structure with `src/` layout and `python -m nightowls` entrypoint.
- CLI with config precedence: `CLI > -c config file > repo nightowls.json > defaults`.
- JSON Schema validation for configuration.
- Output modes: `json`, `png`, `config`, `members`.
- Timezone modes: `local` and `utc`.
- Identity source option: `author` or `committer`.
- Commit filters: `since`, `until`, `branch`, and `no_merges`.
- Unit and CLI smoke tests.

### Changed
- Replaced demo script layout with reusable modules (`config`, `repo`, `members`, `analysis`, `outputs`, `cli`).

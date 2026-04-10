# Repository Guidelines

## Project Structure & Module Organization
- Source code lives in `src/nightowls/`.
- CLI entrypoints: `src/nightowls/cli.py` and `src/nightowls/__main__.py` (`python -m nightowls`).
- Core modules are split by responsibility:
  - `config.py` (load/merge/validate config)
  - `repo.py` (open repo, iterate commits)
  - `members.py` (identity mapping rules)
  - `analysis.py` (hourly aggregation)
  - `outputs.py` (JSON/PNG emitters)
- JSON Schema is in `src/nightowls/schemas/nightowls.schema.json`.
- Tests are in `tests/` (`test_*.py`).

## Build, Test, and Development Commands
- `python -m pip install -r requirements.txt`: install runtime/dev dependencies.
- `PYTHONPATH=src python -m nightowls --help`: run CLI from source tree.
- `PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'`: run test suite.
- `python -m build`: build distributable artifacts (wheel/sdist).

## Coding Style & Naming Conventions
- Target Python 3.13 with type annotations on public functions.
- Follow PEP 8: 4-space indentation, snake_case for functions/modules, PascalCase for classes.
- Keep modules focused and small; prefer explicit helper functions over large monolithic routines.
- Preserve deterministic outputs where possible (e.g., stable JSON key ordering).

## Testing Guidelines
- Use the built-in `unittest` framework.
- Name files `test_<feature>.py` and test methods `test_<behavior>()`.
- Add/adjust tests for any change in config semantics, matching behavior, or CLI/output modes.
- Include regression tests for bug fixes before merging.

## Commit & Pull Request Guidelines
- Use concise, imperative commit messages (e.g., `Add configurable chart titles`).
- Keep commits scoped to one logical change.
- PRs should include:
  - What changed and why
  - Any config/schema/readme updates
  - Test evidence (command + result)
  - Example output or screenshot for PNG/chart-related changes

## Security & Configuration Tips
- Never commit secrets in `nightowls.json`.
- Validate config changes against the schema and keep `$schema` URL/docs in sync when schema evolves.

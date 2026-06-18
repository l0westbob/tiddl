# tiddl Agent Guide

## Repo Map
- `tiddl/cli/`: CLI entrypoints, commands, prompts, and local path/config helpers.
- `tiddl/core/`: compatibility layer for API, auth, metadata, and utility logic.
- `tiddl/providers/`: provider-specific implementations, currently Tidal.
- `tiddl/application/`: orchestration and planning logic.
- `tiddl/infrastructure/`: filesystem, network, media, and runtime adapters.
- `tests/`: characterization and regression coverage mirroring the package layout.
- `downloads/`: local prompt assets and scratch data; do not commit generated content.

## Canonical Commands
- `uv run pytest`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run ty check` (until stabilized in CI)
- `uv run uv build`

## Ignore By Default
- `.idea/`
- `.venv/`
- `.ruff_cache/`
- `.pytest_cache/`
- `dist/`
- `downloads/`
- `.local/`

## Runtime And Smoke Rules
- Runtime state must stay under `TIDDL_PATH`.
- For local dev, use `TIDDL_PATH=/Users/benochocki/Herd/tiddl/downloads/local`.
- Smoke output goes in `/Users/benochocki/Herd/tiddl/downloads/smoke`.
- Use this exact smoke command when needed:
  `TIDDL_PATH=/Users/benochocki/Herd/tiddl/downloads/local uv run tiddl download --path /Users/benochocki/Herd/tiddl/downloads/smoke --threads-count 1 url https://tidal.com/album/358969963/track/358969965`
- After every smoke test, remove only `/Users/benochocki/Herd/tiddl/downloads/smoke` and recreate it if needed.
- Never delete `/Users/benochocki/Herd/tiddl/downloads/local`.

## Slice Discipline
- After each slice: run tests and the relevant lint/format checks.
- After marked phases: run smoke checks when valid local auth is available.
- Smoke command:
  `TIDDL_PATH=/Users/benochocki/Herd/tiddl/downloads/local uv run tiddl download --path /Users/benochocki/Herd/tiddl/downloads/smoke --threads-count 1 url https://tidal.com/album/358969963/track/358969965`
- Smoke cleanup:
  - remove only `/Users/benochocki/Herd/tiddl/downloads/smoke`
  - recreate it if needed
  - never delete `/Users/benochocki/Herd/tiddl/downloads/local`
- Keep each slice working end to end before moving on.

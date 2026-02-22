# atlas-mcp-server Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-22

## Active Technologies

- Python 3.12 (exceeds constitution minimum of 3.11+) + FastMCP 3.0, geonamescache 3.0.0, pycountry 24.x (001-atlas-game)

## Project Structure

```text
src/
tests/
```

## Commands

```bash
uv sync                        # install dependencies
uv run pytest                  # run all tests
uv run pytest tests/contract/  # contract tests only
uv run ruff check src/ tests/  # lint
uv run ruff format src/ tests/ # format
uv run mypy src/               # type check
uv run fastmcp run src/atlas/server.py  # start server
uv run fastmcp list src/atlas/server.py # list tools
```

## Code Style

Python 3.12 (exceeds constitution minimum of 3.11+): Follow standard conventions

## Recent Changes

- 001-atlas-game: Added Python 3.12 (exceeds constitution minimum of 3.11+) + FastMCP 3.0, geonamescache 3.0.0, pycountry 24.x

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

# Quickstart: ATLAS Word Game MCP Server

**Feature**: 001-atlas-game
**Date**: 2026-02-22

---

## Prerequisites

- Python 3.12 installed and active
- `uv` package manager installed (`pip install uv`)
- Claude Desktop or Claude Code (any MCP-compatible client)

---

## Installation

```bash
# Clone and enter the repo
git clone <repo-url>
cd atlas-mcp-server

# Install all dependencies (runtime + dev, uv reads pyproject.toml and uv.lock)
uv sync --all-extras

# Build the geographic corpus (only needed once, or after updating geo data)
# This uses geonamescache + pycountry (dev deps) to produce src/atlas/data/geo_corpus.json
uv run python scripts/build_corpus.py

# Verify installation
uv run python -c "from atlas.server import create_server; print('OK')"
```

> **Note**: `src/atlas/data/geo_corpus.json` is committed to the repo, so contributors
> do not need to re-run `build_corpus.py` unless they want to refresh the geographic data.

---

## Running the Server (stdio — for Claude Desktop/Code)

```bash
uv run python -m atlas.server
```

Or via FastMCP CLI:

```bash
uv run fastmcp run src/atlas/server.py
```

---

## Connecting to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "atlas-game": {
      "command": "uv",
      "args": ["run", "python", "-m", "atlas.server"],
      "cwd": "/path/to/atlas-mcp-server"
    }
  }
}
```

Restart Claude Desktop, then use Claude to play:

```
Start a game of ATLAS.
```

---

## Playing via FastMCP CLI (manual testing)

```bash
# List available tools
uv run fastmcp list src/atlas/server.py

# Start a game
uv run fastmcp call src/atlas/server.py atlas_start '{}'

# Submit a word (replace required letter based on previous output)
uv run fastmcp call src/atlas/server.py atlas_play '{"word": "India"}'

# Concede when stuck
uv run fastmcp call src/atlas/server.py atlas_concede '{}'
```

---

## Running Tests

```bash
# All tests
uv run pytest

# Only contract tests
uv run pytest tests/contract/

# Only integration tests
uv run pytest tests/integration/

# With coverage
uv run pytest --cov=atlas --cov-report=term-missing

# Lint + type check
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run ty check src/
```

---

## Validation Checklist

Run this checklist manually after the server is built to confirm the spec is met:

- [ ] `atlas_start` prints the ATLAS title screen with "A T L A S" visible
- [ ] Two consecutive `atlas_start` calls show different first movers at least
  occasionally (random coin flip is working)
- [ ] `atlas_play` with a valid word is accepted; server responds with its own word
- [ ] `atlas_play` with a wrong starting letter is rejected; tool returns error message
- [ ] `atlas_play` with a non-geographic name is rejected
- [ ] `atlas_play` with a repeated word is rejected
- [ ] After rejection, `atlas_play` with the correct word is accepted (turn not lost)
- [ ] `atlas_concede` ends the game and shows the full word chain
- [ ] Starting a new game after a concession clears all prior state
- [ ] Server concedes (and user wins) when server has no words for the required letter

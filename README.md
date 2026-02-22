# atlas-mcp-server

```
╔══════════════════════════════════════╗
║                                      ║
║   🌍  A T L A S  🌍                 ║
║   this is the game of atlas          ║
║                                      ║
╚══════════════════════════════════════╝
```

A geographic word-chaining game delivered as an [MCP](https://modelcontextprotocol.io) server. Play against an AI opponent inside Claude Desktop, Claude Code, or any MCP-compatible client.

## Rules

- Name any **continent, country, state, or major city**.
- Each new word must **start with the last letter** of the previous word.
- No word may be **repeated** in the same game.
- The game ends only when a player **genuinely runs out of valid words** — invalid submissions never cost you a turn.

## Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `atlas_start` | — | Start (or restart) a game. Flips a coin to decide who goes first. |
| `atlas_play` | `word: str` | Submit your geographic name. Server responds automatically. |
| `atlas_concede` | — | Give up when you can't think of a word. |

## Requirements

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) package manager

## Installation

```bash
git clone https://github.com/healthkowshik/atlas-mcp-server
cd atlas-mcp-server
uv sync --all-extras
```

The geographic corpus (`src/atlas/data/geo_corpus.json`, ~6,200 names) is committed to the repo — no extra build step needed.

To regenerate it (e.g. after a geography library update):

```bash
uv run python scripts/build_corpus.py
```

## Connect to Claude Desktop

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

Restart Claude Desktop, then tell Claude: **"Start a game of ATLAS."**

## Development

```bash
# Run all tests (66 tests)
uv run pytest

# Lint + format + type check
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run mypy src/
```

## Project structure

```
src/atlas/
  server.py       # MCP tools: atlas_start, atlas_play, atlas_concede
  game.py         # Session state, validation, word selection
  geography.py    # Corpus loading and geo-name lookup
  display.py      # Message formatting (title, rejection, game-over)
  data/
    geo_corpus.json  # Pre-built corpus (~6,200 names, all lowercase)
scripts/
  build_corpus.py  # Dev-only: rebuilds geo_corpus.json
tests/
  contract/        # Tool schema registration tests
  integration/     # Full game-flow tests
  unit/            # Pure logic tests (game.py, geography.py)
```

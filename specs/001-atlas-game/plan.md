# Implementation Plan: ATLAS Word Game

**Branch**: `001-atlas-game` | **Date**: 2026-02-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-atlas-game/spec.md`

## Summary

Build a FastMCP 3.0 MCP server that hosts the ATLAS geographic word-chaining game.
The server exposes three atomic tools: `atlas_start` (title screen + coin flip + optional
opening move), `atlas_play` (user word submission with validation + server response),
and `atlas_concede` (user gives up, game ends). Game state is maintained per-session
using FastMCP's built-in session state (`ctx.set_state`/`ctx.get_state`). Geographic
validation draws from `geonamescache` (countries, cities) and `pycountry` (ISO 3166-2
subdivisions) — both pure-Python, offline packages.

## Technical Context

**Language/Version**: Python 3.12 (exceeds constitution minimum of 3.11+)
**Primary Dependencies**: FastMCP 3.0 (runtime); geonamescache 2.0.0 + pycountry 24.6.1
(build/dev only — used by `scripts/build_corpus.py` to generate `src/atlas/data/geo_corpus.json`;
not loaded at runtime)
**Storage**: `src/atlas/data/geo_corpus.json` (committed, pre-built geographic corpus,
~7-8k names); in-memory session state via FastMCP `ctx.set_state`/`ctx.get_state`
(JSON-serializable, per-session, no persistent storage)
**Testing**: pytest + pytest-asyncio + FastMCP `run_server_async` + FastMCP `Client`
**Target Platform**: MCP server (stdio transport for Claude Desktop/Code; supports SSE)
**Project Type**: MCP server
**Performance Goals**: Title screen + first move delivered within 1 second (SC-001);
word validation response within 1 second per move (frozenset O(1) lookup)
**Constraints**: No external API calls; offline-capable; in-memory state only (no DB)
**Scale/Scope**: Single user per session; no concurrency requirements; interactive game

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|-----------|-------|--------|
| I. Protocol Compliance | All capabilities expressed as `@mcp.tool()` decorators; no proprietary extensions; tool schemas validated via FastMCP's type annotation system | ✅ PASS |
| II. Tool Atomicity | Three tools, each performing exactly one user-facing operation (`atlas_start`, `atlas_play`, `atlas_concede`). Session state is FastMCP's sanctioned per-session store (not global mutable state); each tool is independently callable and testable | ✅ PASS |
| III. Test-First | Contract tests and integration tests are specified in this plan and MUST be written before any implementation code. Red-Green-Refactor enforced. | ✅ PASS |
| IV. Observability | FastMCP 3.0 OpenTelemetry tracing configured at server start; `ctx.info`/`ctx.error` logging in every tool; standard Python exceptions propagate to MCP error format | ✅ PASS |
| V. Simplicity | Three tools, no database, two offline geo packages (minimum needed to cover spec scope: countries + cities + non-US subdivisions), in-memory state. No abstractions added beyond what the game logic requires. | ✅ PASS |

*Post-design re-check: All principles upheld after Phase 1. No Complexity Tracking
entries required — no violations detected.*

## Project Structure

### Documentation (this feature)

```text
specs/001-atlas-game/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── atlas_start.md
│   ├── atlas_play.md
│   └── atlas_concede.md
└── tasks.md             # Phase 2 output (/speckit.tasks — not created here)
```

### Source Code (repository root)

```text
src/
└── atlas/
    ├── __init__.py
    ├── server.py         # FastMCP server instantiation + tool registrations
    ├── game.py           # Game logic: session state helpers, turn management
    ├── geography.py      # Geographic corpus loader (reads geo_corpus.json)
    ├── display.py        # ATLAS title screen renderer
    └── data/
        └── geo_corpus.json   # Pre-built geographic name corpus (~7-8k names, committed)

scripts/
└── build_corpus.py       # Dev-only: generates geo_corpus.json from geonamescache + pycountry

tests/
├── contract/
│   └── test_tool_schemas.py   # Validate tool input/output schemas via FastMCP
├── integration/
│   └── test_game_flow.py      # Full game turn sequences via FastMCP Client
└── unit/
    ├── test_game.py            # Game logic: validation rules, state transitions
    └── test_geography.py       # Geography: corpus coverage, letter-index lookups

pyproject.toml         # runtime deps: fastmcp; dev deps: geonamescache, pycountry, pytest, ...
.python-version
uv.lock
```

**Structure Decision**: Single project (Option 1). The ATLAS game is a self-contained
MCP server with no frontend, no external API, and no separate backend service. All game
logic lives in the `atlas` package under `src/`. Tests follow the standard pytest layout
with contract, integration, and unit subdirectories per the constitution.

## Complexity Tracking

> No violations detected. No entries required.

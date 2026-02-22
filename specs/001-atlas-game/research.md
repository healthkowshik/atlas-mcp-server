# Research: ATLAS Word Game

**Feature**: 001-atlas-game
**Date**: 2026-02-22
**Phase**: 0 — Outline & Research

---

## Decision 1: MCP Framework

**Decision**: FastMCP 3.0 (jlowin/fastmcp, installable via `pip install fastmcp`)

**Rationale**: Mandated by the project constitution (Technical Standards). FastMCP 3.0
provides the `@mcp.tool()` decorator, built-in session state (`ctx.set_state`/
`ctx.get_state`), native OpenTelemetry tracing, and a Python test client — all of which
directly satisfy the game's requirements.

**Key APIs confirmed**:

```python
# Tool definition
@mcp.tool
async def my_tool(word: str, ctx: Context) -> str:
    await ctx.info("Processing word")
    return "result"

# Session state (async, JSON-serializable by default, per-session)
await ctx.set_state("words_played", ["India", "Austria"])
words = await ctx.get_state("words_played")  # returns ["India", "Austria"] or None

# Non-serializable values (request-scoped only)
await ctx.set_state("db_conn", conn, serializable=False)

# Delete state
await ctx.delete_state("words_played")
```

**Session state characteristics**:
- Scoped per MCP client session (each connected client has isolated state)
- JSON-serializable values persist across requests within the session
- State expires after 1 day of inactivity
- Works correctly with stdio, SSE, and streamable-HTTP transports

**Error handling**: Standard Python exceptions propagate to MCP error format
automatically. No special exception class required.

**Alternatives considered**: Raw MCP Python SDK (`mcp`) — rejected because it requires
manual protocol handling that FastMCP abstracts away, violating Principle V (Simplicity).

---

## Decision 2: Geographic Data Package & Build Strategy

**Decision**: Build-script pattern — `geonamescache` (v2.0.0) + `pycountry` (v24.6.1)
as **build-time / dev dependencies only**, generating a bundled `src/atlas/data/geo_corpus.json`
that the runtime server loads. Zero geo-package runtime dependencies.

**Rationale**:

Neither package alone satisfies all four entity types the spec requires:
- `geonamescache` covers continents, countries, US states, and cities (filterable by
  population) — but **only US states** among administrative subdivisions.
- `pycountry` covers countries and all ISO 3166-2 subdivisions (Indian states, Canadian
  provinces, German Länder, etc.) — but **no city data**.

Running both as build deps in a one-time `scripts/build_corpus.py` script produces a
pre-normalised JSON corpus that is committed to the repo and loaded at server startup.
The runtime server has zero dependency on either package.

**Corpus composition** (~7,000–8,000 unique names after deduplication):

| Source | Entities | Approx. count |
|--------|----------|---------------|
| Hardcoded (7 continents) | Continents | 7 |
| `pycountry` ISO 3166-1 | Countries + aliases | ~500 |
| `pycountry` ISO 3166-2 | All subdivisions (states/provinces) | ~5,000 |
| `geonamescache` (pop ≥ 500k) | Major world cities | ~2,500 |
| **Total (deduped, normalised)** | | **~7,000–8,000** |

**Build script pattern** (`scripts/build_corpus.py`):
```python
import json, unicodedata
from pathlib import Path
import geonamescache, pycountry

def normalize(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s.strip().lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))

names: set[str] = set()
for continent in ["Africa","Antarctica","Asia","Europe",
                  "North America","Oceania","South America"]:
    names.add(normalize(continent))
for country in pycountry.countries:
    names.add(normalize(country.name))
    if hasattr(country, "common_name"):
        names.add(normalize(country.common_name))
for sub in pycountry.subdivisions:
    names.add(normalize(sub.name))
for city in geonamescache.GeonamesCache().get_cities().values():
    if city["population"] >= 500_000:
        names.add(normalize(city["name"]))

out = Path("src/atlas/data/geo_corpus.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(sorted(names), ensure_ascii=False, indent=2))
```

**Runtime loader** (`src/atlas/geography.py`):
```python
import json, unicodedata
from pathlib import Path
from functools import lru_cache

_DATA = Path(__file__).parent / "data" / "geo_corpus.json"

@lru_cache(maxsize=1)
def _corpus() -> frozenset[str]:
    return frozenset(json.loads(_DATA.read_text()))

def is_valid_geo_name(name: str) -> bool:
    return _normalize(name) in _corpus()

def names_starting_with(letter: str) -> list[str]:
    return [n for n in _corpus() if n.startswith(letter.lower())]

def _normalize(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name.strip().lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))
```

**Benefits of this approach**:
- Runtime server has zero geo-package dependencies (faster cold start)
- Corpus is deterministic and version-controlled (committed JSON)
- Diacritic normalisation baked in at build time
- Easy to audit, tune, or extend the corpus by re-running the build script
- O(1) validation via `frozenset` lookup; O(n_letter) enumeration via letter prefix scan

**Alternatives considered**:
- Runtime `geonamescache` only — rejected: no non-US subdivisions (Indian states, etc.)
- Runtime `pycountry` only — rejected: no city data
- Both packages at runtime — rejected: unnecessary runtime dependencies when a pre-built
  JSON eliminates them; aligns better with Principle V (Simplicity)
- `countryinfo` — rejected: abandoned (last release 2019), no iteration API, sparse data

---

## Decision 3: Testing Strategy

**Decision**: pytest + pytest-asyncio + FastMCP `run_server_async` + FastMCP `Client`

**Rationale**: FastMCP's official testing pattern uses `run_server_async` to start the
server in-process as an asyncio task, then `Client` to call tools. This avoids subprocess
management and integrates cleanly with pytest-asyncio.

**Pattern**:
```python
import pytest
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.utilities.tests import run_server_async
from atlas.server import create_server

@pytest.mark.asyncio
async def test_atlas_start():
    server = create_server()
    async with run_server_async(server) as url:
        async with Client(url) as client:
            result = await client.call_tool("atlas_start", {})
            content = result[0].text
            assert "A T L A S" in content

@pytest.mark.asyncio
async def test_atlas_play_valid_word():
    server = create_server()
    async with run_server_async(server) as url:
        async with Client(url) as client:
            await client.call_tool("atlas_start", {})
            # ... set up known state, then play
```

**Contract tests** validate tool schemas using FastMCP's tool listing:
```python
async with Client(url) as client:
    tools = await client.list_tools()
    tool = next(t for t in tools if t.name == "atlas_play")
    assert "word" in tool.inputSchema["properties"]
```

**Alternatives considered**: `run_server_in_process` (subprocess) — rejected as more
complex with subprocess coordination issues. Direct unit testing of tool functions without
FastMCP — rejected because it bypasses schema validation (contract tests require the MCP
layer).

---

## Decision 4: Display / Title Screen

**Decision**: Rich Unicode/emoji formatting rendered as a plain string returned by the
`atlas_start` tool.

**Rationale**: MCP tools return text content. The "fun, visually engaging" title screen
(FR-001) can be rendered using Unicode box-drawing characters and emoji in the returned
string — no additional library required. This satisfies Principle V (Simplicity).

**Example**:
```
╔══════════════════════════════════╗
║                                  ║
║   🌍  A T L A S  🌍             ║
║   · · · · · · · · · · ·         ║
║   this is the game of atlas      ║
║                                  ║
╚══════════════════════════════════╝
```

**Alternative considered**: `rich` library — rejected (unnecessary dependency; plain
Unicode strings are sufficient and simpler).

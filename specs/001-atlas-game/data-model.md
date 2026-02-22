# Data Model: ATLAS Word Game

**Feature**: 001-atlas-game
**Date**: 2026-02-22
**Phase**: 1 — Design

---

## Entities

### GameSession

The active state of one ATLAS game. Stored as a JSON-serializable dict in FastMCP
session state under the key `"atlas_session"`.

| Field | Type | Description |
|-------|------|-------------|
| `game_active` | `bool` | True while the game is in progress; False once ended |
| `words_played` | `list[str]` | Ordered list of all accepted words (both players), in lowercase |
| `required_letter` | `str \| None` | Lowercase single character the next word must start with; None before game starts |
| `current_turn` | `"user" \| "server" \| None` | Whose turn it is; None before game starts |
| `first_mover` | `"user" \| "server" \| None` | Who played the opening word (set at game start) |
| `winner` | `"user" \| "server" \| None` | Set when game ends; None while in progress |

**State transitions**:

```
[No session] ──atlas_start()──► [game_active=True, current_turn set]
                                      │
                              atlas_play(valid word)
                                      │
                                      ▼
                              [words_played updated, required_letter updated]
                                      │
                              server cannot play / atlas_concede()
                                      │
                                      ▼
                              [game_active=False, winner set]
```

**Invariants**:
- `words_played` contains no duplicates (case-insensitive)
- `required_letter` is always the last alphabetic character (stripped of diacritics and
  punctuation) of the last entry in `words_played`
- `current_turn` alternates between "user" and "server" after each accepted word

---

### GeographicWord

A canonical entry in the geographic name corpus. Stored in-memory at server startup as
part of the letter index; not persisted to session state.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Canonical display name (e.g., "India", "New York") |
| `name_lower` | `str` | Lowercase normalised form used for lookups and deduplication |
| `first_letter` | `str` | First alphabetic character, lowercase (extracted after diacritic stripping) |
| `last_letter` | `str` | Last alphabetic character, lowercase (extracted after diacritic stripping) |
| `category` | `"continent" \| "country" \| "subdivision" \| "city"` | Geographic entity type |

**Validation rules** (applied to user submissions):
1. `name_lower` must exist in the corpus (geographic authenticity)
2. `first_letter` must equal `GameSession.required_letter` (chain rule)
3. `name_lower` must not appear in `GameSession.words_played` (no repeats)

**Letter index** (in-memory, built at server startup):
```python
# Maps first_letter → sorted list of canonical names available from that letter
letter_index: dict[str, list[str]]
# Maps name_lower → GeographicWord (for O(1) validation lookup)
word_lookup: dict[str, GeographicWord]
```

---

### Move

A record of a single turn taken by either participant. Used internally for logging and
composing the word-chain summary shown at game over. Derived from `words_played` at
display time; not stored separately in session state.

| Field | Type | Description |
|-------|------|-------------|
| `player` | `"user" \| "server"` | Who played this move |
| `word` | `str` | The word that was played |
| `position` | `int` | Zero-based index in the words_played list |

---

## State Schema (JSON)

The complete GameSession stored under key `"atlas_session"` in FastMCP session state:

```json
{
  "game_active": true,
  "words_played": ["india", "austria", "albania"],
  "required_letter": "a",
  "current_turn": "user",
  "first_mover": "server",
  "winner": null
}
```

---

## Geographic Corpus Composition

The corpus is pre-built at development time by `scripts/build_corpus.py` and committed
to the repo as `src/atlas/data/geo_corpus.json`. The runtime server loads this file
once at startup into a `frozenset` for O(1) validation — no geo-package runtime deps.

| Source | Entities | Approximate Count |
|--------|----------|-------------------|
| Hardcoded | 7 continents | 7 |
| `pycountry` ISO 3166-1 | Countries + common/official name aliases | ~500 |
| `pycountry` ISO 3166-2 | All administrative subdivisions (US states, Indian states, Canadian provinces, etc.) | ~5,000 |
| `geonamescache` (pop ≥ 500k) | Major world cities and national/regional capitals | ~2,500 |
| **Total (deduped, diacritics normalised)** | | **~7,000–8,000** |

`geonamescache` and `pycountry` are **dev/build dependencies only** — not runtime deps.

Letter coverage: All 26 letters have at least one valid geographic name. Letters with
fewer options (Q, X, Z) will cause more frequent server concessions — this is expected
and correct per the game rules (a rare letter is a legitimate winning move).

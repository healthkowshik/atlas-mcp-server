---

description: "Task list for ATLAS Word Game MCP server implementation"
---

# Tasks: ATLAS Word Game

**Input**: Design documents from `/specs/001-atlas-game/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Included — constitution mandates Test-First (Principle III, NON-NEGOTIABLE).
Tests MUST be written before the implementation tasks they test. Run each test and
confirm it FAILS before writing the corresponding implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation
and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared state)
- **[Story]**: Which user story this task belongs to (US1–US4)
- File paths are absolute relative to repository root

## Path Conventions

- Source code: `src/atlas/`
- Tests: `tests/contract/`, `tests/integration/`, `tests/unit/`
- Build scripts: `scripts/`
- Static data: `src/atlas/data/`

---

## Phase 1: Setup

**Purpose**: Project initialization — all tasks can run before any user story work.

- [ ] T001 Create `pyproject.toml` at repository root with runtime dep `fastmcp>=3.0`, dev deps `pytest`, `pytest-asyncio`, `geonamescache>=2.0`, `pycountry>=24.6`, `ruff`, `mypy`, and project metadata (name: `atlas-mcp-server`, version: `0.1.0`, requires-python: `>=3.12`)
- [ ] T002 Create `.python-version` at repository root containing `3.12`
- [ ] T003 [P] Create `src/atlas/__init__.py` (empty), `src/atlas/data/` directory, and `src/atlas/data/.gitkeep` so the data directory is tracked before geo_corpus.json is generated
- [ ] T004 [P] Create `tests/__init__.py`, `tests/contract/__init__.py`, `tests/integration/__init__.py`, `tests/unit/__init__.py` (all empty), and `tests/conftest.py` with a placeholder comment — to be populated in Phase 2
- [ ] T005 [P] Create `scripts/__init__.py` (empty) so `scripts/` is a recognisable Python directory; confirm `uv sync --all-extras` resolves without errors

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared geographic corpus and core game logic — MUST be complete before
any user story can be implemented. Tests are written first (Red phase), then implementation (Green phase).

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Geographic Corpus Build

- [ ] T006 Write `scripts/build_corpus.py`: use `pycountry` (countries + ISO 3166-2 subdivisions) and `geonamescache` (cities with population ≥ 500 000) to collect geographic names; normalise each name with `unicodedata.normalize("NFKD", ...)` stripping combining characters; lowercase; deduplicate; include 7 hardcoded continents; write sorted list to `src/atlas/data/geo_corpus.json` as UTF-8 JSON; print final count to stdout
- [ ] T007 Run `uv run python scripts/build_corpus.py` and verify `src/atlas/data/geo_corpus.json` is created, contains ≥ 5 000 entries, and all entries are lowercase strings

### Geography Module (TDD)

> **Write T008 first — confirm it FAILS — then implement T009 to make it GREEN**

- [ ] T008 [P] Write FAILING unit tests in `tests/unit/test_geography.py` covering: (a) `is_valid_geo_name("india")` returns True; (b) `is_valid_geo_name("blorbistan")` returns False; (c) `names_starting_with("a")` returns a non-empty list where every name starts with "a"; (d) `_normalize("São Paulo")` returns `"sao paulo"`; (e) `is_valid_geo_name("India")` (mixed case) returns True (case-insensitive); (f) corpus loads only once (`_corpus` cached)
- [ ] T009 Implement `src/atlas/geography.py`: `_normalize(name: str) -> str` (NFKD + strip combining chars + lower + strip); `_corpus() -> frozenset[str]` (load `src/atlas/data/geo_corpus.json`, cache with `@lru_cache(maxsize=1)`); `is_valid_geo_name(name: str) -> bool` (normalize then check frozenset); `names_starting_with(letter: str) -> list[str]` (return sorted list of corpus names with matching first char after normalize) — run `pytest tests/unit/test_geography.py` and confirm all tests PASS

### Game Logic Module (TDD)

> **Write T010 first — confirm it FAILS — then implement T011 to make it GREEN**

- [ ] T010 [P] Write FAILING unit tests in `tests/unit/test_game.py` covering: (a) `extract_last_letter("India")` returns `"a"`; (b) `extract_last_letter("New York")` returns `"k"`; (c) `extract_last_letter("São Paulo")` returns `"o"` (diacritic-stripped); (d) `extract_last_letter("Azerbaijan")` returns `"n"`; (e) `validate_submission("argentina", required_letter="a", words_played=[])` returns `(True, None)`; (f) `validate_submission("brazil", required_letter="a", words_played=[])` returns `(False, "wrong_letter")`; (g) `validate_submission("blorbistan", required_letter="b", words_played=[])` returns `(False, "not_geographic")`; (h) `validate_submission("india", required_letter="i", words_played=["india"])` returns `(False, "already_used")`; (i) `pick_server_word(required_letter="i", words_played=[])` returns a non-empty string that starts with `"i"` and `is_valid_geo_name` on it returns True; (j) `pick_server_word(required_letter="x", words_played=[])` returns None if no "x" words exist in corpus (or returns a valid one if any do); (k) `pick_server_word` never returns a word in `words_played`
- [ ] T011 Implement `src/atlas/game.py`: `extract_last_letter(word: str) -> str` (normalize, find last alpha char); `validate_submission(word: str, required_letter: str, words_played: list[str]) -> tuple[bool, str | None]` (apply rules in order: geographic authenticity → chain letter → duplicate; return error code string or None); `pick_server_word(required_letter: str, words_played: list[str]) -> str | None` (filter corpus names starting with required letter, exclude already played, shuffle, return first or None); `build_game_session(**kwargs) -> dict` (typed GameSession dict factory); `get_session(ctx) -> dict | None` (async, reads "atlas_session" from FastMCP context); `save_session(ctx, session: dict) -> None` (async, writes "atlas_session" to FastMCP context) — run `pytest tests/unit/test_game.py` and confirm all tests PASS

### Test Fixtures

- [ ] T012 Populate `tests/conftest.py` with: `import pytest` and `from fastmcp import FastMCP`; `from fastmcp.utilities.tests import run_server_async`; `from fastmcp.client import Client`; `from atlas.server import create_server`; define async fixture `atlas_client` that calls `create_server()`, enters `run_server_async(server)` context, enters `Client(url)` context, and yields the connected client — mark fixture with `@pytest.fixture` and `scope="function"`; add `pytest.ini_options` or `conftest` `asyncio_mode = "auto"` to support `pytest-asyncio`

**Checkpoint**: Geography corpus loaded, game logic tested and passing, fixtures ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Start the Game (Priority: P1) 🎯 MVP

**Goal**: Display the ATLAS title screen and initialise a game session, randomly deciding
who plays the first word.

**Independent Test**: Call `atlas_start` on a fresh session and verify: (a) response
contains "A T L A S", (b) the tool is registered with no required parameters, (c) calling
it twice resets state.

### Tests for User Story 1 ⚠️ Write FIRST — confirm FAIL — then implement

- [ ] T013 [P] [US1] Write FAILING contract test in `tests/contract/test_tool_schemas.py`: list all tools from the server; find `atlas_start`; assert `inputSchema["properties"] == {}` (no parameters); assert `atlas_start` is present in tool names
- [ ] T014 [P] [US1] Write FAILING integration tests in `tests/integration/test_game_flow.py` for US1: (a) `atlas_start` response contains the string `"A T L A S"`; (b) `atlas_start` response is a non-empty string; (c) calling `atlas_start` twice does not raise an error and the second response still contains `"A T L A S"`; (d) after `atlas_start`, calling `atlas_play` with a valid word does not fail with "wrong starting letter" due to stale state (session was reset)

### Implementation for User Story 1

- [ ] T015 [US1] Implement `src/atlas/display.py`: `render_title() -> str` returning the ATLAS title screen as a Unicode-decorated string containing the literal text `"A T L A S"` followed by `"this is the game of atlas"` on a second line, wrapped in a box using Unicode box-drawing characters and including globe emoji 🌍; `render_server_goes_first(word: str, next_letter: str) -> str` returning a message announcing the server's opening word and the required starting letter for the user; `render_user_goes_first() -> str` returning a prompt for the user to enter the opening word
- [ ] T016 [US1] Implement `src/atlas/server.py`: define `create_server() -> FastMCP` that creates a `FastMCP("Atlas Game 🌍")` instance; register the `atlas_start` async tool using `@mcp.tool` with `ctx: Context` parameter; inside `atlas_start`: call `build_game_session` to create a fresh session; call `save_session(ctx, session)` to reset any prior state; coin-flip via `random.choice(["server", "user"])`; if server goes first: call `pick_server_word(required_letter=random.choice(list("abcdefghijklmnopqrstuvwxyz")), words_played=[])` to get opening word, update session (words_played, required_letter, current_turn="user", first_mover="server"), save, return `render_title() + "\n\n" + render_server_goes_first(word, next_letter)`; if user goes first: set current_turn="user", first_mover="user", save, return `render_title() + "\n\n" + render_user_goes_first()`; add `if __name__ == "__main__": create_server().run()` at module bottom — run `pytest tests/contract/test_tool_schemas.py tests/integration/test_game_flow.py -k "start"` and confirm all US1 tests PASS

**Checkpoint**: `atlas_start` is fully functional. Title screen displays, coin flip works, session initialises. MVP is demonstrable via `fastmcp call src/atlas/server.py atlas_start '{}'`.

---

## Phase 4: User Story 2 - Player Submits a Word (Priority: P2)

**Goal**: Accept and validate the user's word submission; reject invalid words with a
specific reason; accept valid words and update session state.

**Independent Test**: With a game in progress (US1 complete), submit (a) a word with
the wrong starting letter, (b) a non-geographic word, (c) a previously used word — each
must be rejected with a specific message naming the rule violated, and the turn must not
advance.

### Tests for User Story 2 ⚠️ Write FIRST — confirm FAIL — then implement

- [ ] T017 [P] [US2] Write FAILING contract test in `tests/contract/test_tool_schemas.py` for `atlas_play`: assert tool is registered; assert `inputSchema["properties"]` contains `"word"` with type `"string"`; assert `"word"` is in `inputSchema.get("required", [])`
- [ ] T018 [P] [US2] Write FAILING integration tests in `tests/integration/test_game_flow.py` for US2 rejection scenarios (all tested after `atlas_start` sets up a session): (a) submit a word starting with the wrong letter → response contains `"❌"` and does not contain `"✅"`; (b) submit a non-geographic name (e.g., `"Blorbistan"`) → response contains `"❌"` and `"not a recognised"`; (c) after playing `"India"` in a prior turn, submit `"India"` again → response contains `"❌"` and `"already"`; (d) submitting an invalid word followed by a valid word (same required letter) → the valid word is accepted (`"✅"` in response), confirming turn was not lost after the rejection; (e) calling `atlas_play` with no prior `atlas_start` → response contains `"No game in progress"`

### Implementation for User Story 2

- [ ] T019 [US2] Implement `render_rejection(word: str, reason: str, required_letter: str) -> str` in `src/atlas/display.py`: `reason` is one of `"wrong_letter"`, `"not_geographic"`, `"already_used"`; return a `❌`-prefixed message explaining the specific rule violated and prompting the user to try again; messages must match the spec contract examples (see `contracts/atlas_play.md`)
- [ ] T020 [US2] Add `atlas_play` async tool to `src/atlas/server.py`: `word: str` parameter, `ctx: Context`; load session with `get_session(ctx)` — if None or `game_active=False`, return error `"No game in progress. Call atlas_start to begin."`; if `current_turn != "user"`, return error `"It's not your turn yet."`; call `validate_submission(word, required_letter, words_played)` — if invalid, call `render_rejection` and return without modifying session state; if valid: append `word.strip().lower()` to `words_played`, update `required_letter` to `extract_last_letter(word)`, set `current_turn="server"`, save session, return `"✅ Great move! '{word}' is valid.\n\n[Server response — coming in US3]"` as a placeholder — run `pytest tests/contract/test_tool_schemas.py tests/integration/test_game_flow.py -k "play"` and confirm all US2 tests PASS

**Checkpoint**: All three rejection scenarios are tested and pass. Valid word acceptance updates state. Turn is never lost on an invalid submission.

---

## Phase 5: User Story 3 - Server Plays Its Turn (Priority: P3)

**Goal**: After the user plays a valid word, the server automatically selects an unused
geographic name starting with the required letter and announces it; if no word is
available, the server concedes and the user wins.

**Independent Test**: After `atlas_start` + one valid user word via `atlas_play`, verify
the server's response includes a valid geographic name starting with the correct letter,
not previously played, and states the next required starting letter.

### Tests for User Story 3 ⚠️ Write FIRST — confirm FAIL — then implement

- [ ] T021 [P] [US3] Write FAILING integration tests in `tests/integration/test_game_flow.py` for US3: (a) after `atlas_start` and a valid `atlas_play("india")`, the response contains `"🤖"` and a server word starting with `"a"`; (b) the server word in the response is itself a recognised geographic name (`is_valid_geo_name(server_word)` is True); (c) the response states the next required starting letter; (d) after multiple turns, the server never repeats a word it has previously played (simulate 3 rounds and check); (e) if forced to a letter with no available words (mock `pick_server_word` to return None), the response declares the user has won

### Implementation for User Story 3

- [ ] T022 [US3] Implement `render_server_plays(word: str, next_letter: str, chain: list[str]) -> str` in `src/atlas/display.py`: return a `🤖`-prefixed message announcing the server's chosen word and the letter the user must start with next; optionally show a brief "Chain so far: X → Y → Z" summary
- [ ] T023 [US3] Replace the US2 placeholder in `atlas_play` in `src/atlas/server.py` with the full server response: after updating session state with the user's valid word, call `pick_server_word(required_letter=new_required_letter, words_played=session["words_played"])` — if a word is returned: append server word (lowercase) to `words_played`, update `required_letter` to `extract_last_letter(server_word)`, set `current_turn="user"`, save session, return user-acceptance message + `"\n\n" + render_server_plays(server_word, next_letter, words_played)`; if `pick_server_word` returns None: set `game_active=False`, `winner="user"`, save session, return user-acceptance message + `"\n\n"` + game-over message declaring user wins (use `render_game_over` from display.py — implement a stub here if T026 is not yet done, or implement T026 first) — run `pytest tests/integration/test_game_flow.py -k "US3 or server"` and confirm all US3 tests PASS

**Checkpoint**: Full game loop works: `atlas_start` → `atlas_play` (valid word) → server responds → user's next required letter shown. Game ends correctly when server cannot continue.

---

## Phase 6: User Story 4 - Player Runs Out of Words (Priority: P4)

**Goal**: When either player cannot produce a valid word, the game ends with a clear
winner declaration, the complete word chain displayed, and an offer to restart.

**Independent Test**: Call `atlas_concede` after an active game and verify: game-over
message contains the word chain, declares the server the winner, and offers to restart.
Also verify that when `pick_server_word` returns None inside `atlas_play`, an equivalent
game-over message declares the user the winner.

### Tests for User Story 4 ⚠️ Write FIRST — confirm FAIL — then implement

- [ ] T024 [P] [US4] Write FAILING contract test in `tests/contract/test_tool_schemas.py` for `atlas_concede`: assert tool is registered; assert `inputSchema["properties"] == {}` (no parameters)
- [ ] T025 [P] [US4] Write FAILING integration tests in `tests/integration/test_game_flow.py` for US4: (a) `atlas_concede` with no active game returns `"No game in progress"`; (b) `atlas_concede` after an active game returns a string containing `"😔"` or `"concede"`, declares server wins, and lists all played words; (c) `atlas_play` after `atlas_concede` returns `"game already over"`; (d) `atlas_start` after `atlas_concede` works correctly (fresh game); (e) after a simulated server concession inside `atlas_play`, response contains the user-wins declaration and the word chain

### Implementation for User Story 4

- [ ] T026 [US4] Implement `render_game_over(winner: str, words_played: list[str], first_mover: str) -> str` in `src/atlas/display.py`: display winner announcement (🏆 for winner, 😔 for loser); display numbered word chain with player attribution (odd positions = first_mover, even positions = other player); append "Type `atlas_start` to play again!" — this function is called by both `atlas_concede` (user loses) and the server-concession path in `atlas_play` (user wins)
- [ ] T027 [US4] Add `atlas_concede` async tool to `src/atlas/server.py`: `ctx: Context`; load session — if None or `game_active=False`, return `"No game in progress. Call atlas_start to begin."`; set `game_active=False`, `winner="server"`, save session; return `render_game_over(winner="server", words_played=session["words_played"], first_mover=session["first_mover"])`
- [ ] T028 [US4] Update the server-concession path in `atlas_play` (T023) to call `render_game_over(winner="user", ...)` using the implemented `render_game_over` from T026 (replace any stub used in T023) — run `pytest tests/contract/ tests/integration/ tests/unit/` and confirm ALL tests PASS

**Checkpoint**: All four user stories are independently functional and tested. `atlas_concede` works. Server concession (inside `atlas_play`) works. Word chain is displayed correctly on both game-over paths.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates, configuration, and documentation completeness.

- [ ] T029 [P] Add `[tool.ruff]` and `[tool.ruff.lint]` sections to `pyproject.toml` (select: `["E", "F", "I", "UP"]`; line-length: 100); add `[tool.mypy]` section (strict = true, python_version = "3.12"); add `[tool.pytest.ini_options]` (asyncio_mode = "auto", testpaths = ["tests"])
- [ ] T030 [P] Run `uv run ruff check src/ tests/ scripts/` and fix all reported lint issues across all Python files
- [ ] T031 [P] Run `uv run ruff format src/ tests/ scripts/` to auto-format all Python files
- [ ] T032 [P] Run `uv run mypy src/` and fix all type errors; ensure all public functions have complete type annotations
- [ ] T033 Run full test suite `uv run pytest --tb=short -q` and confirm 100% of tests pass; record final test count in a comment at the bottom of this file
- [ ] T034 [P] Update `README.md` with: project description (ATLAS geographic word game, MCP server); installation instructions (`uv sync --all-extras`, `build_corpus.py`); how to connect to Claude Desktop (copy the JSON config from quickstart.md); list of the three tools (`atlas_start`, `atlas_play`, `atlas_concede`) with one-line descriptions
- [ ] T035 Run `uv run fastmcp list src/atlas/server.py` and `uv run fastmcp call src/atlas/server.py atlas_start '{}'` to validate the server registers and responds correctly via the FastMCP CLI (quickstart.md validation step)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
  - T006-T007 (corpus) must complete before T008-T009 (geography.py tests depend on corpus)
  - T009 (geography.py) must complete before T011 (game.py uses geography functions)
  - T012 (conftest.py) must complete before any integration tests run
- **US1 (Phase 3)**: Depends on Phase 2 completion — T013/T014 (tests) before T015/T016 (impl)
- **US2 (Phase 4)**: Depends on Phase 2 + US1 (server.py started in US1); T017/T018 before T019/T020
- **US3 (Phase 5)**: Depends on US2 (extends atlas_play); T021 before T022/T023
- **US4 (Phase 6)**: Depends on US2 + US3 (uses session state established in earlier stories); T024/T025 before T026/T027/T028
- **Polish (Final Phase)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational — no user story dependencies
- **US2 (P2)**: Starts after Foundational + US1 (`server.py` exists with `atlas_start`)
- **US3 (P3)**: Starts after US2 (extends `atlas_play` implementation)
- **US4 (P4)**: Starts after US2 + US3 (needs full `atlas_play` + session state)

### Within Each User Story

1. Tests written first → confirmed FAILING
2. Implementation → tests turn GREEN
3. Story complete before moving to next

### Parallel Opportunities

- T003, T004, T005 can run in parallel (Phase 1)
- T008 and T010 can run in parallel (both are test-writing tasks for different modules)
- T013 and T014 can run in parallel (contract test + integration test, different test files)
- T017 and T018 can run in parallel (contract test + integration test)
- T024 and T025 can run in parallel (contract test + integration test)
- T029, T030, T031, T032, T034, T035 can run in parallel (Final Phase)

---

## Parallel Example: Phase 2 Foundational

```bash
# After T006 + T007 complete (corpus built), launch in parallel:
Task: "Write FAILING unit tests in tests/unit/test_geography.py"   # T008
Task: "Write FAILING unit tests in tests/unit/test_game.py"        # T010
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (`atlas_start`)
4. **STOP and VALIDATE**: Run `fastmcp call src/atlas/server.py atlas_start '{}'`
   — confirm title screen appears and session initialises
5. Demo to user / stakeholder as MVP

### Incremental Delivery

1. Complete Setup + Foundational → Infrastructure ready
2. Add US1 (`atlas_start`) → Title screen + coin flip ✅ Demo!
3. Add US2 (`atlas_play` validation) → Word submission + rejection ✅ Demo!
4. Add US3 (server auto-plays) → Full game loop ✅ Demo!
5. Add US4 (`atlas_concede` + game-over) → Complete experience ✅ Final demo!
6. Polish → Production-ready

---

## Notes

- `[P]` tasks = different files, no unresolved dependencies — safe to run in parallel
- `[Story]` label maps each task to its user story for traceability
- **TDD is enforced**: tests MUST fail before implementation starts (constitution Principle III)
- **Run tests after each task group** to catch regressions early
- `pick_server_word` shuffles the available words to avoid always picking the same answer
- Session state key `"atlas_session"` must be consistently used across all tools
- `render_game_over` is shared by both `atlas_concede` (user loses) and the server-concession path in `atlas_play` (user wins) — reuse the same function with different `winner` argument

<!-- Final test count: TBD after T033 -->

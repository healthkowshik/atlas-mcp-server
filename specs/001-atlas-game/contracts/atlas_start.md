# Tool Contract: atlas_start

**Tool name**: `atlas_start`
**Version**: 1.0
**Category**: Game lifecycle
**Atomic operation**: Initialise or reset an ATLAS game session

---

## Purpose

Starts a new ATLAS game (or resets an existing one). Displays the title screen, randomly
decides who plays the first geographic word, and either (a) plays the server's opening
word, or (b) prompts the user to enter the opening word.

---

## Input Schema

```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false
}
```

**No parameters.** Every call to `atlas_start` starts a fresh game unconditionally.

---

## Output

**Type**: `string` (MCP text content)

**Structure** (cases vary by coin flip outcome):

### Case A — Server goes first

```
╔══════════════════════════════════════╗
║   🌍  A T L A S  🌍                ║
║   · · · · · · · · · · ·             ║
║      this is the game of atlas      ║
╚══════════════════════════════════════╝

🎲 I'll go first!

My word: **India**
🔤 Your turn — your word must start with: **A**
```

### Case B — User goes first

```
╔══════════════════════════════════════╗
║   🌍  A T L A S  🌍                ║
║   · · · · · · · · · · ·             ║
║      this is the game of atlas      ║
╚══════════════════════════════════════╝

🎲 You go first!

🔤 Name a continent, country, state, or city to begin.
```

---

## Side Effects

Overwrites the entire `atlas_session` key in FastMCP session state:

```json
{
  "game_active": true,
  "words_played": [],
  "required_letter": null,
  "current_turn": "user",
  "first_mover": "user",
  "winner": null
}
```

When server goes first, the session state after `atlas_start` will have:
- `words_played: ["india"]` (server's opening word, lowercase)
- `required_letter: "a"` (last letter of "india")
- `current_turn: "user"`
- `first_mover: "server"`

---

## Error Cases

| Condition | Error message |
|-----------|--------------|
| Geographic corpus fails to load at startup | MCP error: "Server initialisation failed: geographic data unavailable" |

*Note: A new game started while one is in progress silently resets state — this is
correct behaviour per FR-014 and is not an error.*

---

## Contract Tests (must fail before implementation)

```python
async def test_atlas_start_schema():
    """Tool must be registered and accept no arguments."""
    tools = await client.list_tools()
    tool = next(t for t in tools if t.name == "atlas_start")
    assert tool.inputSchema["properties"] == {}

async def test_atlas_start_shows_title():
    """Response must contain the ATLAS title string."""
    result = await client.call_tool("atlas_start", {})
    assert "A T L A S" in result[0].text

async def test_atlas_start_resets_state():
    """Calling atlas_start twice must produce a fresh session."""
    await client.call_tool("atlas_start", {})
    await client.call_tool("atlas_play", {"word": "India"})
    await client.call_tool("atlas_start", {})
    # Verify that subsequent atlas_play sees no prior words
    result = await client.call_tool("atlas_play", {"word": "Albania"})
    # Should not fail with "wrong starting letter" due to stale state
    assert "already been used" not in result[0].text
```

# Tool Contract: atlas_concede

**Tool name**: `atlas_concede`
**Version**: 1.0
**Category**: Game lifecycle
**Atomic operation**: User explicitly gives up their turn; game ends with user losing

---

## Purpose

Called when the user cannot think of a valid geographic name starting with the required
letter and wishes to end the game. This is a deliberate concession — it is the ONLY
way a user's inability to continue terminates the game (invalid word submissions never
end the game; they just trigger a retry).

---

## Input Schema

```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false
}
```

**No parameters.**

---

## Output

**Type**: `string` (MCP text content)

```
😔 You've conceded — no valid geographic name starting with **A** comes to mind!

🏆 I win this round!

📜 Full word chain (N moves):
   1. India       (server)
   2. Austria     (you)
   3. Albania     (server)
   4. ...

Type `atlas_start` to play again!
```

---

## Side Effects

Sets `game_active` to `false` and `winner` to `"server"` in the FastMCP session state.
The `words_played` list is preserved (for display in the summary).

After `atlas_concede`, calling `atlas_play` must return an error until `atlas_start` is
called again.

---

## Error Cases

| Condition | Error message |
|-----------|--------------|
| No active game session | MCP error: "No game in progress. Call atlas_start to begin." |
| Game already ended | MCP error: "Game already over. Call atlas_start to begin a new game." |

---

## Contract Tests (must fail before implementation)

```python
async def test_atlas_concede_schema():
    """Tool must be registered and accept no arguments."""
    tools = await client.list_tools()
    tool = next(t for t in tools if t.name == "atlas_concede")
    assert tool.inputSchema["properties"] == {}

async def test_atlas_concede_no_session():
    """Conceding with no active game must error."""
    result = await client.call_tool("atlas_concede", {})
    assert "No game in progress" in result[0].text

async def test_atlas_concede_ends_game():
    """Conceding an active game must mark game as over and user as loser."""
    await client.call_tool("atlas_start", {})
    result = await client.call_tool("atlas_concede", {})
    assert "win" in result[0].text.lower()
    assert "word chain" in result[0].text.lower()

async def test_atlas_play_after_concede_errors():
    """atlas_play called after concede must require a new atlas_start."""
    await client.call_tool("atlas_start", {})
    await client.call_tool("atlas_concede", {})
    result = await client.call_tool("atlas_play", {"word": "India"})
    assert "game already over" in result[0].text.lower()

async def test_atlas_concede_preserves_word_chain():
    """Game over summary must list all words played in order."""
    await client.call_tool("atlas_start", {})
    # ... play a few words
    result = await client.call_tool("atlas_concede", {})
    assert "word chain" in result[0].text.lower()
```

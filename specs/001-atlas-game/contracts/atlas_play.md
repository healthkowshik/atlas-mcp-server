# Tool Contract: atlas_play

**Tool name**: `atlas_play`
**Version**: 1.0
**Category**: Gameplay
**Atomic operation**: User submits a word; server validates and responds

---

## Purpose

Accepts the user's geographic word during their turn. Validates it against three rules
(geographic authenticity, letter-chain, no repeats). On success, the server automatically
selects and plays its own word and passes the turn back. On failure, the turn is NOT
advanced and the user may try again.

---

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "word": {
      "type": "string",
      "description": "The geographic name (continent, country, state, or city) the user wants to play.",
      "minLength": 1
    }
  },
  "required": ["word"],
  "additionalProperties": false
}
```

---

## Output

**Type**: `string` (MCP text content)

**Cases**:

### Case A — Valid user word, server responds successfully

```
✅ Great move! "India" is valid.

🤖 My word: **Austria**
🔤 Your turn — your word must start with: **A**

📜 Chain so far: India → Austria
```

### Case B — Invalid word (wrong starting letter)

```
❌ "Brazil" doesn't work — your word must start with **A** (the last letter of "India").

Try again! 🔤
```

### Case C — Invalid word (not a geographic name)

```
❌ "Blorbistan" isn't a recognised continent, country, state, or city.

Try again! 🔤
```

### Case D — Invalid word (already played)

```
❌ "India" has already been played in this game.

Try again! 🔤
```

### Case E — Valid user word, server cannot respond (server concedes)

```
✅ Great move! "Azerbaijan" is valid.

🤖 I give up — I can't think of a geographic name starting with **N**. 😔

🏆 You win! Congratulations!

📜 Full word chain:
   1. India (server)
   2. Austria (you)
   3. Azerbaijan (you)

Type `atlas_start` to play again!
```

### Case F — Valid user word, it's the last move and game ends (edge case: no words at all left for server)

Same as Case E.

---

## Side Effects

**On valid submission**:

Session state `words_played` is extended with the user's word (lowercase) and, if the
server responds, the server's word (lowercase). `required_letter` is updated to the last
letter of whichever word was played last. `current_turn` is set to "user" (after server
plays) or game ends.

**On invalid submission**: Session state is NOT modified.

**On game over** (Case E): `game_active` is set to `false`, `winner` is set to `"user"`.

---

## Error Cases

| Condition | Error message |
|-----------|--------------|
| No active game session (atlas_start not called) | MCP error: "No game in progress. Call atlas_start to begin." |
| It is not the user's turn | MCP error: "It's not your turn yet." |
| `word` is empty after stripping whitespace | MCP error: "Word cannot be empty." |

---

## Validation Rules (in order applied)

1. **Geographic authenticity**: `word.strip().lower()` must exist in the geographic corpus
2. **Letter chain**: first alphabetic character of `word` (lowercase) == `required_letter`
3. **No repeats**: `word.strip().lower()` must not appear in `words_played`

*All three rules are applied even if the first fails — the error message reports the
specific violated rule (always the first failing check in order).*

---

## Contract Tests (must fail before implementation)

```python
async def test_atlas_play_schema():
    """Tool must require 'word' parameter as string."""
    tools = await client.list_tools()
    tool = next(t for t in tools if t.name == "atlas_play")
    props = tool.inputSchema["properties"]
    assert "word" in props
    assert props["word"]["type"] == "string"
    assert "word" in tool.inputSchema.get("required", [])

async def test_atlas_play_no_session():
    """Calling atlas_play without atlas_start must error."""
    # Fresh session — no game started
    result = await client.call_tool("atlas_play", {"word": "India"})
    assert "No game in progress" in result[0].text

async def test_atlas_play_wrong_letter():
    """Word starting with wrong letter must be rejected, turn not advanced."""
    # Set up known state: required_letter = "a"
    ...
    result = await client.call_tool("atlas_play", {"word": "Brazil"})
    assert "❌" in result[0].text
    assert "start with" in result[0].text.lower()

async def test_atlas_play_valid_word_advances_chain():
    """Valid word must be accepted and chain letter updated."""
    ...
    result = await client.call_tool("atlas_play", {"word": "Austria"})
    assert "✅" in result[0].text

async def test_atlas_play_duplicate_rejected():
    """Previously played word must be rejected."""
    ...
    result = await client.call_tool("atlas_play", {"word": "India"})
    assert "already been played" in result[0].text.lower()

async def test_atlas_play_invalid_word_does_not_advance_turn():
    """After a rejection, the same required_letter must still be required."""
    ...
    await client.call_tool("atlas_play", {"word": "Brazil"})  # wrong letter
    result = await client.call_tool("atlas_play", {"word": "Argentina"})  # correct
    assert "✅" in result[0].text  # second attempt with correct letter succeeds
```

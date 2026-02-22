"""ATLAS Game MCP server — all three tools: atlas_start, atlas_play, atlas_concede."""

import random

from fastmcp import Context, FastMCP

from atlas.display import (
    render_game_over,
    render_rejection,
    render_server_goes_first,
    render_server_plays,
    render_title,
    render_user_goes_first,
)
from atlas.game import (
    build_game_session,
    extract_last_letter,
    get_session,
    pick_server_word,
    save_session,
    validate_submission,
)
from atlas.geography import _normalize, is_valid_geo_name


def create_server() -> FastMCP:
    """Create and return the configured ATLAS FastMCP server instance."""
    mcp = FastMCP(
        "Atlas Game 🌍",
        instructions="""
You are the host of ATLAS, a geographic word-chaining game.

CRITICAL RULES FOR YOU (the assistant):
- NEVER suggest words, give hints, or list possible answers for the user.
- NEVER say things like "Try Nigeria, Nepal, Nairobi..." or "You could play..."
- The user must come up with their own word. That IS the game.
- Simply relay the tool output to the user and wait for their next move.
- If the user asks for help or hints, remind them that figuring out the word is the challenge.

Workflow:
1. User says they want to play → call atlas_start
2. Show the user the result (who goes first, the required letter)
3. Wait for the user to name a geographic place → call atlas_play with their word
4. Show the result (accepted or rejected, server's response, next required letter)
5. Repeat until someone concedes or runs out of words

Keep your messages short. Let the game output speak for itself.
""",
    )

    # ------------------------------------------------------------------
    # atlas_start — US1
    # ------------------------------------------------------------------

    @mcp.tool
    async def atlas_start(ctx: Context) -> str:
        """Start (or restart) a game of ATLAS.

        Displays the title screen, flips a coin to decide who plays first,
        and resets the session. If the server goes first it plays an opening
        word and states the letter the user must start with.
        """
        session = build_game_session(game_active=True)
        first_mover = random.choice(["server", "user"])
        session["first_mover"] = first_mover

        if first_mover == "server":
            # Server picks an opening word from a random starting letter
            opening_letter = random.choice(list("abcdefghijklmnopqrstuvwxyz"))
            server_word = pick_server_word(opening_letter, words_played=[])
            # Fall back to any available letter if the chosen one has no words
            if server_word is None:
                for letter in "abcdefghijklmnopqrstuvwxyz":
                    server_word = pick_server_word(letter, words_played=[])
                    if server_word is not None:
                        break
            if server_word is None:
                # Extremely unlikely — corpus is empty
                return render_title() + "\n\n⚠️ Corpus is empty; cannot start a game."

            next_letter = extract_last_letter(server_word)
            session["words_played"] = [server_word]
            session["required_letter"] = next_letter
            session["current_turn"] = "user"
            await save_session(ctx, session)
            return render_title() + "\n\n" + render_server_goes_first(server_word, next_letter)

        else:
            # User goes first — no required letter yet
            session["current_turn"] = "user"
            session["required_letter"] = None
            await save_session(ctx, session)
            return render_title() + "\n\n" + render_user_goes_first()

    # ------------------------------------------------------------------
    # atlas_play — US2 (validation) + US3 (server response)
    # ------------------------------------------------------------------

    @mcp.tool
    async def atlas_play(ctx: Context, word: str) -> str:
        """Submit a geographic name as your move.

        The word must:
        - Start with the required letter (last letter of the previous word).
        - Be a recognised continent, country, state, or major city.
        - Not have been played before in this game.

        After a valid move the server automatically plays its word.
        If the server cannot find a word it concedes and you win.
        """
        session = await get_session(ctx)

        if session is None or not session.get("game_active"):
            return "No game in progress. Call  atlas_start  to begin."

        if session.get("current_turn") != "user":
            return "It's not your turn yet."

        required_letter: str | None = session.get("required_letter")
        words_played: list[str] = session.get("words_played", [])

        # First move of a user-goes-first game: any starting letter is valid
        if required_letter is None:
            # Validate only geographic authenticity and no-repeat
            if not is_valid_geo_name(word):
                return render_rejection(word, "not_geographic", "?")
            if _normalize(word) in {_normalize(w) for w in words_played}:
                return render_rejection(word, "already_used", "?")
            # Valid first move
            required_letter = ""  # will be replaced by extract_last_letter below
        else:
            valid, error_code = validate_submission(word, required_letter, words_played)
            if not valid:
                return render_rejection(word, error_code or "invalid", required_letter)

        # Accept the user's word
        word_norm = word.strip().lower()
        words_played.append(word_norm)
        new_required_letter = extract_last_letter(word_norm)

        # --- Server's turn (US3) ---
        server_word = pick_server_word(new_required_letter, words_played)

        if server_word is None:
            # Server cannot play — user wins
            session["game_active"] = False
            session["winner"] = "user"
            session["words_played"] = words_played
            session["required_letter"] = new_required_letter
            await save_session(ctx, session)
            acceptance = f"✅ Great move! '{word_norm}' is valid.\n\n"
            return acceptance + render_game_over(
                winner="user",
                words_played=words_played,
                first_mover=session.get("first_mover", "user"),
            )

        # Server plays its word
        words_played.append(server_word)
        next_letter_for_user = extract_last_letter(server_word)
        session["words_played"] = words_played
        session["required_letter"] = next_letter_for_user
        session["current_turn"] = "user"
        session["game_active"] = True
        await save_session(ctx, session)

        acceptance = f"✅ Great move! '{word_norm}' is valid.\n\n"
        return acceptance + render_server_plays(server_word, next_letter_for_user, words_played)

    # ------------------------------------------------------------------
    # atlas_concede — US4
    # ------------------------------------------------------------------

    @mcp.tool
    async def atlas_concede(ctx: Context) -> str:
        """Concede the current game — you give up and the server wins.

        Use this when you cannot think of a valid word for the required letter.
        The full word chain is displayed and you can start a new game immediately.
        """
        session = await get_session(ctx)

        if session is None or not session.get("game_active"):
            return "No game in progress. Call  atlas_start  to begin."

        session["game_active"] = False
        session["winner"] = "server"
        await save_session(ctx, session)

        return render_game_over(
            winner="server",
            words_played=session.get("words_played", []),
            first_mover=session.get("first_mover", "user"),
        )

    return mcp


def main() -> None:
    """Entry point for the MCP server."""
    create_server().run()


if __name__ == "__main__":
    main()

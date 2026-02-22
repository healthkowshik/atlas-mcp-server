"""Display helpers — format all ATLAS game messages as rich Unicode strings."""

from __future__ import annotations

_TITLE_BOX = """\
╔══════════════════════════════════════╗
║                                      ║
║   🌍  A T L A S  🌍                 ║
║   this is the game of atlas          ║
║                                      ║
╚══════════════════════════════════════╝"""


def render_title() -> str:
    """Return the ATLAS title screen string."""
    return _TITLE_BOX


def render_server_goes_first(word: str, next_letter: str) -> str:
    """Announce that the server opens the game with *word*."""
    return (
        f"🤖 I'll go first!\n"
        f"   My opening word: **{word}**\n\n"
        f"🎯 Your turn! Your word must start with the letter  « {next_letter.upper()} »"
    )


def render_user_goes_first() -> str:
    """Prompt the user to enter the opening word."""
    return (
        "🎲 You go first!\n\n"
        "🌍 Name any continent, country, state, or city to begin.\n"
        "   Use  atlas_play(word='...')  to submit your word."
    )


def render_rejection(word: str, reason: str, required_letter: str) -> str:
    """Return a rejection message for an invalid submission.

    *reason* is one of: ``"wrong_letter"``, ``"not_geographic"``, ``"already_used"``
    """
    if reason == "wrong_letter":
        first = next((c for c in word if c.isalpha()), "?").upper()
        req = required_letter.upper()
        return (
            f"❌ '{word}' starts with «{first}» but the required letter is «{req}».\n"
            f"   Please try a geographic name starting with «{req}»."
        )
    if reason == "not_geographic":
        req = required_letter.upper()
        return (
            f"❌ '{word}' is not a recognised geographic name.\n"
            f"   Try a continent, country, state, or major city starting with «{req}»."
        )
    if reason == "already_used":
        return (
            f"❌ '{word}' has already been played in this game.\n"
            f"   Choose a different geographic name starting with «{required_letter.upper()}»."
        )
    return f"❌ '{word}' is not valid. Please try again."


def render_server_plays(word: str, next_letter: str, chain: list[str]) -> str:
    """Announce the server's chosen word and the next required letter."""
    chain_str = " → ".join(chain[-6:])  # show last 6 words at most
    return (
        f"🤖 My word: **{word}**\n\n"
        f"🔗 Chain so far: {chain_str}\n\n"
        f"🎯 Your turn! Your word must start with the letter  « {next_letter.upper()} »"
    )


def render_game_over(winner: str, words_played: list[str], first_mover: str) -> str:
    """Return the end-of-game summary.

    *winner* is ``"user"`` or ``"server"``.
    *first_mover* is ``"user"`` or ``"server"`` — used to attribute each word in the chain.
    """
    if winner == "user":
        header = "🏆 You win! The server ran out of words. Well played!\n😔 Server concedes."
    else:
        header = "😔 You've run out of words — the server wins this round!\n🏆 Server wins!"

    # Build numbered word chain with player attribution
    lines = [header, "", "📜 Word chain:"]
    current = first_mover
    for i, word in enumerate(words_played, start=1):
        label = "You" if current == "user" else "🤖 Server"
        lines.append(f"   {i:>3}. {label}: {word}")
        current = "server" if current == "user" else "user"

    lines.append("")
    lines.append("💡 Type  atlas_start  to play again!")
    return "\n".join(lines)

"""Core game logic for the ATLAS word-chaining game.

Provides:
- Session state factory and typed helpers
- Word validation (3 rules: geographic, chain letter, no repeats)
- Server word selection (pick an unused geo name from corpus)
- Last-letter extraction with diacritic/punctuation stripping
"""

import random
import unicodedata
from typing import Any

from atlas.geography import is_valid_geo_name, names_starting_with

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

SESSION_KEY = "atlas_session"


def build_game_session(
    *,
    game_active: bool = False,
    words_played: list[str] | None = None,
    required_letter: str | None = None,
    current_turn: str | None = None,
    first_mover: str | None = None,
    winner: str | None = None,
) -> dict[str, Any]:
    """Return a fresh (or partially initialised) GameSession dict."""
    return {
        "game_active": game_active,
        "words_played": words_played if words_played is not None else [],
        "required_letter": required_letter,
        "current_turn": current_turn,
        "first_mover": first_mover,
        "winner": winner,
    }


async def get_session(ctx: Any) -> dict[str, Any] | None:
    """Load the current GameSession from FastMCP session state."""
    return await ctx.get_state(SESSION_KEY)


async def save_session(ctx: Any, session: dict[str, Any]) -> None:
    """Persist the GameSession into FastMCP session state."""
    await ctx.set_state(SESSION_KEY, session)


# ---------------------------------------------------------------------------
# String helpers
# ---------------------------------------------------------------------------


def _strip_to_alpha(text: str) -> str:
    """Normalise diacritics and return only alphabetic characters (lowercase)."""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if c.isalpha())


def extract_last_letter(word: str) -> str:
    """Return the last alphabetic character of *word*, normalised to lowercase.

    Diacritics are stripped before extraction, so "São Paulo" → "o".
    """
    alpha_only = _strip_to_alpha(word)
    if not alpha_only:
        raise ValueError(f"No alphabetic characters found in word: {word!r}")
    return alpha_only[-1]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_submission(
    word: str,
    required_letter: str,
    words_played: list[str],
) -> tuple[bool, str | None]:
    """Validate a user's word submission against the three game rules.

    Rules applied in order:
    1. Chain letter: first alpha char of *word* must equal *required_letter*
    2. Geographic authenticity: *word* must exist in the corpus
    3. No repeats: *word* must not appear in *words_played*

    Returns:
        (True, None) if valid
        (False, error_code) where error_code is one of:
            "wrong_letter", "not_geographic", "already_used"
    """
    normalised = word.strip().lower()
    nfkd = unicodedata.normalize("NFKD", normalised)
    stripped = "".join(c for c in nfkd if c.isalpha() or c == " ")
    first_alpha = next((c for c in stripped if c.isalpha()), "")

    # Rule 1: chain letter
    if first_alpha != required_letter.lower():
        return False, "wrong_letter"

    # Rule 2: geographic authenticity
    if not is_valid_geo_name(word):
        return False, "not_geographic"

    # Rule 3: no repeats (case-insensitive, diacritic-normalised)
    from atlas.geography import _normalize  # avoid circular at module level

    if _normalize(word) in {_normalize(w) for w in words_played}:
        return False, "already_used"

    return True, None


# ---------------------------------------------------------------------------
# Server word selection
# ---------------------------------------------------------------------------


def pick_server_word(required_letter: str, words_played: list[str]) -> str | None:
    """Choose a random valid geographic name starting with *required_letter*.

    Excludes any name already in *words_played*.
    Returns None if no valid candidates remain.
    """
    candidates = names_starting_with(required_letter)
    played_set = set(words_played)
    available = [w for w in candidates if w not in played_set]
    if not available:
        return None
    return random.choice(available)

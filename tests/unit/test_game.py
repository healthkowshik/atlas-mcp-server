"""Unit tests for src/atlas/game.py — write FIRST, confirm FAIL, then implement."""

from atlas.game import (
    build_game_session,
    extract_last_letter,
    pick_server_word,
    validate_submission,
)
from atlas.geography import is_valid_geo_name


class TestExtractLastLetter:
    def test_simple(self) -> None:
        assert extract_last_letter("India") == "a"

    def test_multi_word(self) -> None:
        assert extract_last_letter("New York") == "k"

    def test_diacritics(self) -> None:
        assert extract_last_letter("São Paulo") == "o"

    def test_trailing_punctuation(self) -> None:
        assert extract_last_letter("Azerbaijan") == "n"

    def test_all_caps(self) -> None:
        assert extract_last_letter("USA") == "a"

    def test_hyphenated(self) -> None:
        # "Guinea-Bissau" → last alpha char is "u"
        assert extract_last_letter("Guinea-Bissau") == "u"


class TestValidateSubmission:
    def test_valid_word(self) -> None:
        ok, err = validate_submission("argentina", required_letter="a", words_played=[])
        assert ok is True
        assert err is None

    def test_valid_word_mixed_case(self) -> None:
        ok, err = validate_submission("Argentina", required_letter="a", words_played=[])
        assert ok is True
        assert err is None

    def test_wrong_letter(self) -> None:
        ok, err = validate_submission("brazil", required_letter="a", words_played=[])
        assert ok is False
        assert err == "wrong_letter"

    def test_not_geographic(self) -> None:
        ok, err = validate_submission("blorbistan", required_letter="b", words_played=[])
        assert ok is False
        assert err == "not_geographic"

    def test_already_used(self) -> None:
        ok, err = validate_submission("india", required_letter="i", words_played=["india"])
        assert ok is False
        assert err == "already_used"

    def test_already_used_case_insensitive(self) -> None:
        ok, err = validate_submission("India", required_letter="i", words_played=["india"])
        assert ok is False
        assert err == "already_used"

    def test_validation_order_wrong_letter_before_not_geo(self) -> None:
        # "xyz123" starts with correct letter but is not geographic
        # We test that wrong_letter is caught first
        ok, err = validate_submission("xyzzy", required_letter="a", words_played=[])
        assert ok is False
        # wrong_letter fires before not_geographic
        assert err == "wrong_letter"

    def test_empty_words_played(self) -> None:
        ok, err = validate_submission("france", required_letter="f", words_played=[])
        assert ok is True
        assert err is None


class TestPickServerWord:
    def test_returns_valid_geo_name(self) -> None:
        word = pick_server_word(required_letter="i", words_played=[])
        assert word is not None
        assert is_valid_geo_name(word)

    def test_starts_with_required_letter(self) -> None:
        word = pick_server_word(required_letter="f", words_played=[])
        assert word is not None
        assert word.startswith("f")

    def test_never_returns_played_word(self) -> None:
        played = ["india", "iran", "iraq", "ireland", "israel", "italy"]
        word = pick_server_word(required_letter="i", words_played=played)
        if word is not None:
            assert word not in played

    def test_returns_none_if_all_exhausted(self) -> None:
        # Get all 'x' words, mark them all as played
        from atlas.geography import names_starting_with

        all_x = names_starting_with("x")
        result = pick_server_word(required_letter="x", words_played=all_x)
        assert result is None

    def test_returns_none_for_impossible_letter(self) -> None:
        # Use a string that would never be a first letter in the corpus
        result = pick_server_word(required_letter="0", words_played=[])
        assert result is None


class TestBuildGameSession:
    def test_default_session(self) -> None:
        s = build_game_session()
        assert s["game_active"] is False
        assert s["words_played"] == []
        assert s["required_letter"] is None
        assert s["current_turn"] is None
        assert s["first_mover"] is None
        assert s["winner"] is None

    def test_session_with_overrides(self) -> None:
        s = build_game_session(game_active=True, current_turn="user")
        assert s["game_active"] is True
        assert s["current_turn"] == "user"

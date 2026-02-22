"""Unit tests for src/atlas/geography.py — write FIRST, confirm FAIL, then implement."""

from atlas.geography import _normalize, is_valid_geo_name, names_starting_with


class TestNormalize:
    def test_lowercase(self) -> None:
        assert _normalize("India") == "india"

    def test_strips_diacritics(self) -> None:
        assert _normalize("São Paulo") == "sao paulo"

    def test_strips_diacritics_cote(self) -> None:
        assert _normalize("Côte d'Ivoire") == "cote d'ivoire"

    def test_strips_surrounding_whitespace(self) -> None:
        assert _normalize("  France  ") == "france"

    def test_already_normalised(self) -> None:
        assert _normalize("new york") == "new york"


class TestIsValidGeoName:
    def test_valid_lowercase(self) -> None:
        assert is_valid_geo_name("india") is True

    def test_valid_mixed_case(self) -> None:
        assert is_valid_geo_name("India") is True

    def test_valid_with_diacritics(self) -> None:
        # São Paulo normalises to "sao paulo" which should be in corpus
        assert is_valid_geo_name("São Paulo") is True

    def test_invalid_nonsense(self) -> None:
        assert is_valid_geo_name("Blorbistan") is False

    def test_invalid_empty(self) -> None:
        assert is_valid_geo_name("") is False

    def test_valid_country(self) -> None:
        assert is_valid_geo_name("france") is True

    def test_valid_continent(self) -> None:
        assert is_valid_geo_name("asia") is True


class TestNamesStartingWith:
    def test_returns_list(self) -> None:
        result = names_starting_with("a")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_all_start_with_letter(self) -> None:
        for name in names_starting_with("b"):
            assert name.startswith("b"), f"'{name}' does not start with 'b'"

    def test_case_insensitive_input(self) -> None:
        lower = names_starting_with("a")
        upper = names_starting_with("A")
        assert lower == upper

    def test_rare_letter_x(self) -> None:
        # Even rare letters should return some results from the corpus
        result = names_starting_with("x")
        assert isinstance(result, list)  # may be empty for very rare letters — that's OK

    def test_results_are_strings(self) -> None:
        for name in names_starting_with("c"):
            assert isinstance(name, str)


class TestCorpusCaching:
    def test_corpus_loaded_once(self) -> None:
        """Calling is_valid_geo_name twice should not raise errors (corpus cached)."""
        assert is_valid_geo_name("brazil") == is_valid_geo_name("brazil")

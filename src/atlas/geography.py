"""Geographic name corpus loader and validation utilities.

Loads the pre-built corpus from src/atlas/data/geo_corpus.json (committed to repo).
No runtime dependency on geonamescache or pycountry.
"""

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

_DATA_FILE = Path(__file__).parent / "data" / "geo_corpus.json"


def _normalize(name: str) -> str:
    """Lowercase, strip diacritics/combining chars, strip surrounding whitespace."""
    nfkd = unicodedata.normalize("NFKD", name.strip().lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


@lru_cache(maxsize=1)
def _corpus() -> frozenset[str]:
    """Load the geographic corpus once and cache it for the process lifetime."""
    names: list[str] = json.loads(_DATA_FILE.read_text(encoding="utf-8"))
    return frozenset(names)


def is_valid_geo_name(name: str) -> bool:
    """Return True if *name* is a recognised geographic name in the corpus."""
    if not name.strip():
        return False
    return _normalize(name) in _corpus()


def names_starting_with(letter: str) -> list[str]:
    """Return a sorted list of all corpus names whose first character equals *letter*.

    The lookup is case-insensitive: ``names_starting_with("A")`` and
    ``names_starting_with("a")`` return the same result.
    """
    prefix = letter.lower()
    return sorted(n for n in _corpus() if n.startswith(prefix))

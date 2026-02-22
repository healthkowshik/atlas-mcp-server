"""Build the geographic name corpus used by the ATLAS game server.

Run once (dev-time only):
    uv run python scripts/build_corpus.py

Outputs: src/atlas/data/geo_corpus.json — a sorted JSON array of lowercase,
diacritic-normalised geographic names drawn from:
  - 7 hardcoded continents
  - pycountry ISO 3166-1 (countries + aliases)
  - pycountry ISO 3166-2 (all administrative subdivisions)
  - geonamescache cities with population >= 500,000

Runtime server has zero dependency on this script or its packages.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import geonamescache
import pycountry

OUTPUT = Path(__file__).parent.parent / "src" / "atlas" / "data" / "geo_corpus.json"

CONTINENTS = [
    "Africa",
    "Antarctica",
    "Asia",
    "Europe",
    "North America",
    "Oceania",
    "South America",
]


def normalize(name: str) -> str:
    """Lowercase, strip diacritics/combining chars, strip surrounding whitespace."""
    nfkd = unicodedata.normalize("NFKD", name.strip().lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def build() -> list[str]:
    names: set[str] = set()

    # Continents
    for c in CONTINENTS:
        names.add(normalize(c))

    # Countries (ISO 3166-1)
    for country in pycountry.countries:
        names.add(normalize(country.name))
        if hasattr(country, "common_name"):
            names.add(normalize(country.common_name))
        if hasattr(country, "official_name"):
            names.add(normalize(country.official_name))

    # Administrative subdivisions (ISO 3166-2: US states, Indian states, etc.)
    for sub in pycountry.subdivisions:
        names.add(normalize(sub.name))

    # Major cities (population >= 500,000)
    gc = geonamescache.GeonamesCache()
    for city in gc.get_cities().values():
        if city["population"] >= 500_000:
            names.add(normalize(city["name"]))

    # Remove empty strings that might arise from whitespace-only names
    names.discard("")

    return sorted(names)


def main() -> None:
    corpus = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Corpus built: {len(corpus):,} names → {OUTPUT}")


if __name__ == "__main__":
    main()

"""Helpers for deriving ordered gameplay hints from country records."""

CONTINENT = "continent"
CLIMATE = "climate"
LANGUAGE = "language"
POPULATION = "population"
CAPITAL = "capital"

HINT_SLOT_ORDER = (
    CONTINENT,
    CLIMATE,
    LANGUAGE,
    POPULATION,
    CAPITAL,
)


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _has_required_fields(country: dict) -> bool:
    if not isinstance(country, dict):
        return False

    for field in (CONTINENT, CLIMATE, LANGUAGE, CAPITAL):
        if not _is_non_empty_string(country.get(field)):
            return False

    population = country.get(POPULATION)
    if not isinstance(population, int) or population < 0:
        return False

    return True


def build_country_hints(country: dict) -> list[str]:
    """
    Build a deterministic set of five hints from a country record.

    Returns an empty list when the record is missing any required source field.
    """
    if not _has_required_fields(country):
        return []

    continent = country[CONTINENT].strip()
    climate = country[CLIMATE].strip()
    language = country[LANGUAGE].strip()
    capital = country[CAPITAL].strip()
    population_formatted = f"{country[POPULATION]:,}"
    capital_period = "" if capital.endswith((".", "!", "?")) else "."

    return [
        f"This country is in {continent}.",
        f"Its climate is generally {climate}.",
        f"A primary language spoken here is {language}.",
        f"Its population is about {population_formatted}.",
        f"Its capital city is {capital}{capital_period}",
    ]

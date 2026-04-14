"""Helpers for deriving ordered gameplay hints from country records."""

import random

NAME = 'name'
POPULATION = 'population'
CONTINENT = 'continent'
CAPITAL = 'capital'
GDP = 'gdp'
AREA = 'area'
FOUNDED = 'founded'
PRESIDENT = 'president'
FLAG_COLOR = 'flag_color'
LANGUAGE = 'language'
CLIMATE = 'climate'

# Difficulty levels for country hints (1 = easiest, 5 = hardest)
HINT_DIFFICULTY = {
    1: [CONTINENT, CAPITAL, NAME],
    2: [PRESIDENT, LANGUAGE],
    3: [FLAG_COLOR, GDP],
    4: [POPULATION, CLIMATE],
    5: [AREA, FOUNDED],
}


def get_random_stat(difficulty):
    difficulty_list = HINT_DIFFICULTY.get(difficulty)
    return random.choice(difficulty_list) if difficulty_list else None


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _has_required_fields(country: dict) -> bool:
    if not isinstance(country, dict):
        return False

    required_fields = [
        CONTINENT, CAPITAL, PRESIDENT, LANGUAGE, FLAG_COLOR,
        GDP, POPULATION, CLIMATE, AREA, FOUNDED, NAME
    ]

    for field in required_fields:
        if field == POPULATION:
            population = country.get(POPULATION)
            if not isinstance(population, int) or population < 0:
                return False
        else:
            if not _is_non_empty_string(country.get(field)):
                return False

    return True


def build_country_hints(country: dict) -> list[str]:
    if not _has_required_fields(country):
        return []

    hints = []

    for difficulty in range(5, 0, -1):
        difficulty_fields = HINT_DIFFICULTY.get(difficulty, [])
        if not difficulty_fields:
            continue

        selected_field = random.choice(difficulty_fields)

        hint = _generate_hint_for_field(country, selected_field)
        if hint:
            hints.append(hint)

    return hints


def _generate_hint_for_field(country: dict, field: str) -> str:
    if field == NAME:
        return f"The name of this country is {country[NAME].strip()}."
    elif field == CONTINENT:
        return f"This country is in {country[CONTINENT].strip()}."
    elif field == CLIMATE:
        return f"Its climate is generally {country[CLIMATE].strip()}."
    elif field == LANGUAGE:
        language = country[LANGUAGE].strip()
        return f"A primary language spoken here is {language}."
    elif field == POPULATION:
        population_formatted = f"{country[POPULATION]:,}"
        return f"Its population is about {population_formatted}."
    elif field == CAPITAL:
        capital = country[CAPITAL].strip()
        capital_period = "" if capital.endswith((".", "!", "?")) else "."
        return (
            f"Its capital city is {capital}{capital_period}"
        )
    elif field == AREA:
        return f"The area of this country is {country[AREA].strip()}."
    elif field == FOUNDED:
        return f"This country was founded in {country[FOUNDED].strip()}."
    elif field == PRESIDENT:
        return f"The current president is {country[PRESIDENT].strip()}."
    elif field == FLAG_COLOR:
        return f"The colors on the flag are {country[FLAG_COLOR].strip()}."
    elif field == GDP:
        return f"The GDP of this country is {country[GDP].strip()}."
    return None

POPULATION = "population"
CAPITAL = "capital"
GOVERNOR = "governor"
COUNTRY_CODE = "country_code"
CODE = "code"

HINT_SLOT_ORDER = (
    COUNTRY_CODE,
    POPULATION,
    CAPITAL,
    GOVERNOR,
    CODE,
)


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _has_required_fields(states: dict) -> bool:
    if not isinstance(states, dict):
        return False

    for field in (COUNTRY_CODE, CAPITAL, GOVERNOR, CODE):
        if not _is_non_empty_string(states.get(field)):
            return False

    population = states.get(POPULATION)
    if not isinstance(population, int) or population < 0:
        return False

    return True


def build_states_hints(states: dict) -> list[str]:
    if not _has_required_fields(states):
        return []

    country_code = states[COUNTRY_CODE].strip()
    population_formatted = f"{states[POPULATION]:,}"
    capital = states[CAPITAL].strip()
    governor = states[GOVERNOR].strip()
    code = states[CODE].strip()
    capital_period = "" if capital.endswith((".", "!", "?")) else "."

    return [
        f"This state is in {country_code}.",
        f"Its population is about {population_formatted}.",
        f"Its capital city is {capital}{capital_period}",
        f"The governor of this state is {governor}.",
        f"The state code is {code}.",
    ]
POPULATION = "population"
CAPITAL = "capital"
CODE = "code"
STATEHOOD_DATE = "statehood_date"
AREA = "area"
GDP = "gdp"
CLIMATE = "climate"
STATE_BIRD = "state_bird"
GOVERNOR = "governor"

HINT_SLOT_ORDER = (
    AREA,
    STATEHOOD_DATE,
    POPULATION,
    CAPITAL,
    CODE,
)


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _has_required_fields(state: dict) -> bool:
    if not isinstance(state, dict):
        return False

    for field in (CAPITAL, CODE, STATEHOOD_DATE, AREA):
        if not _is_non_empty_string(state.get(field)):
            return False

    population = state.get(POPULATION)
    if not isinstance(population, int) or population < 0:
        return False

    return True


def build_states_hints(state: dict) -> list[str]:
    if not _has_required_fields(state):
        return []

    area = state[AREA].strip()
    statehood_date = state[STATEHOOD_DATE].strip()
    population_formatted = f"{state[POPULATION]:,}"
    capital = state[CAPITAL].strip()
    code = state[CODE].strip()

    return [
        f"The area is about {area}.",
        f"This state was founded in {statehood_date}.",
        f"Its population is about {population_formatted}.",
        f"Its capital city is {capital}.",
        f"The state code is {code}.",
    ]

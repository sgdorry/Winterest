POPULATION = "population"
CAPITAL = "capital"
GOVERNOR = "governor"
CODE = "code"
GDP = "gdp"
STATEHOOD_DATE = "statehood_date"
AREA = "area"

HINT_SLOT_ORDER = (
    POPULATION,
    CAPITAL,
    GOVERNOR,
    CODE,
    GDP,
    STATEHOOD_DATE,
    AREA
)


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _has_required_fields(states: dict) -> bool:
    if not isinstance(states, dict):
        return False

    for field in (CAPITAL, GOVERNOR, CODE):
        if not _is_non_empty_string(states.get(field)):
            return False

    population = states.get(POPULATION)
    if not isinstance(population, int) or population < 0:
        return False

    return True


def build_states_hints(states: dict) -> list[str]:
    if not _has_required_fields(states):
        return []

    population_formatted = f"{states[POPULATION]:,}"
    capital = states[CAPITAL].strip()
    governor = states[GOVERNOR].strip()
    code = states[CODE].strip()
    statehood_date = states[STATEHOOD_DATE].strip()
    gdp = states[GDP].strip()
    area = states[AREA].strip()
    capital_period = "" if capital.endswith((".", "!", "?")) else "."

    return [
        f"Its population is about {population_formatted}.",
        f"Its capital city is {capital}{capital_period}",
        f"The governor of this state is {governor}.",
        f"The state code is {code}.",
        f"The area is about {area}",
        f"The GDP is about {gdp}",
        f"The date the state was founded is {statehood_date}"
    ]

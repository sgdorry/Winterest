import random

NAME = 'name'
POPULATION = 'population'
AREA = 'area'
STATEHOOD_DATE = 'statehood_date'
GDP = 'gdp'
CAPITAL = 'capital'
GOVERNOR = 'governor'
CODE = 'code'
CLIMATE = 'climate'
STATE_BIRD = 'state_bird'


HINT_DIFFICULTY = {
    1: [NAME, CODE],
    2: [GOVERNOR, CAPITAL],
    3: [AREA, STATEHOOD_DATE],
    4: [POPULATION, CLIMATE],
    5: [GDP, STATE_BIRD],
}


def get_random_stat(difficulty):
    difficulty_list = HINT_DIFFICULTY.get(difficulty)
    return random.choice(difficulty_list) if difficulty_list else None


def generate_hint_slots():
    hint_slots = []
    for difficulty in range(5, 0, -1):
        stat = get_random_stat(difficulty)
        if stat:
            hint_slots.append(stat)
    return hint_slots


HINT_SLOT_ORDER = generate_hint_slots()


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _has_required_fields(state: dict) -> bool:
    if not isinstance(state, dict):
        return False

    for field in HINT_SLOT_ORDER:
        if field == POPULATION:
            continue
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
    founded = state[STATEHOOD_DATE].strip()
    population_formatted = f"{state[POPULATION]:,}"
    capital = state[CAPITAL].strip()
    governor = state[GOVERNOR].strip()
    code = state[CODE].strip()
    gdp = state[GDP].strip()
    climate = state[CLIMATE].strip()
    state_bird = state[STATE_BIRD].strip()

    return [
        f"The area is about {area}.",
        f"This state was founded in {founded}.",
        f"Its population is about {population_formatted}.",
        f"Its capital city is {capital}.",
        f"The state's governor is {governor}.",
        f"The state code is {code}.",
        f"The state's GDP is {gdp}.",
        f"The state's climate is {climate}.",
        f"The state bird is {state_bird}.",
    ]

import random

NAME = 'name'
POPULATION = 'population'
AREA = 'area'
STATEHOOD_DATE = 'founded'
GDP = 'gdp'
CAPITAL = 'capital'
GOVERNOR = 'governor'
CODE = 'state_code'
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


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _has_required_fields(state: dict) -> bool:
    if not isinstance(state, dict):
        return False

    required_fields = [
        NAME,
        CODE,
        GOVERNOR,
        CAPITAL,
        AREA,
        STATEHOOD_DATE,
        POPULATION,
        CLIMATE,
        GDP,
        STATE_BIRD,
    ]

    for field in required_fields:
        if field == POPULATION:
            population = state.get(POPULATION)
            if not isinstance(population, int) or population < 0:
                return False
        else:
            if not _is_non_empty_string(state.get(field)):
                return False

    return True


def build_states_hints(state: dict) -> list[str]:
    if not _has_required_fields(state):
        return []

    hints = []

    for difficulty in range(5, 0, -1):
        difficulty_fields = HINT_DIFFICULTY.get(difficulty, [])
        if not difficulty_fields:
            continue

        selected_field = random.choice(difficulty_fields)

        hint = _generate_hint_for_field(state, selected_field)
        if hint:
            hints.append(hint)

    return hints


def _generate_hint_for_field(state: dict, field: str) -> str:
    if field == NAME:
        return f"The state is called {state[NAME].strip()}."
    elif field == POPULATION:
        return f"Its population is about {state[POPULATION]:,}."
    elif field == AREA:
        return f"The area is about {state[AREA].strip()}."
    elif field == STATEHOOD_DATE:
        return f"This state was founded in {state[STATEHOOD_DATE].strip()}."
    elif field == GDP:
        return f"The state's GDP is {state[GDP].strip()}."
    elif field == CAPITAL:
        return f"Its capital city is {state[CAPITAL].strip()}."
    elif field == GOVERNOR:
        return f"The state's governor is {state[GOVERNOR].strip()}."
    elif field == CODE:
        return f"The state code is {state[CODE].strip()}."
    elif field == CLIMATE:
        return f"The state's climate is {state[CLIMATE].strip()}."
    elif field == STATE_BIRD:
        return f"The state bird is {state[STATE_BIRD].strip()}."
    return None

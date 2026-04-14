import random

POPULATION = "population"
STATE = "state"
STATE_CODE = "state_code"
FOUNDED = "founded"
MAYOR = "mayor"
AREA = "area"

# Difficulty levels for city hints (1 = easiest, 5 = hardest)
HINT_DIFFICULTY = {
    1: [STATE],          # Easiest - state location
    2: [MAYOR],          # City leadership
    3: [AREA],           # Physical size
    4: [POPULATION],     # Population size
    5: [FOUNDED],        # Hardest - founding date
}


def get_random_stat(difficulty):
    difficulty_list = HINT_DIFFICULTY.get(difficulty)
    return random.choice(difficulty_list) if difficulty_list else None


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _has_required_fields(city: dict) -> bool:
    if not isinstance(city, dict):
        return False

    required_fields = [POPULATION, STATE, FOUNDED, MAYOR, AREA]
    
    for field in required_fields:
        if not _is_non_empty_string(city.get(field)):
            return False

    return True


def build_cities_hints(city: dict) -> list[str]:
    if not _has_required_fields(city):
        return []

    hints = []
    
    for difficulty in range(5, 0, -1):
        difficulty_fields = HINT_DIFFICULTY.get(difficulty, [])
        if not difficulty_fields:
            continue
            
        selected_field = random.choice(difficulty_fields)
        
        hint = _generate_hint_for_field(city, selected_field)
        if hint:
            hints.append(hint)
    
    return hints


def _generate_hint_for_field(city: dict, field: str) -> str:
    """Generate a hint string for a specific field."""
    if field == FOUNDED:
        return f"This city was founded in {city[FOUNDED].strip()}."
    elif field == POPULATION:
        return f"Its population is about {city[POPULATION].strip()}."
    elif field == STATE:
        return f"This city is in {city[STATE].strip()}."
    elif field == AREA:
        return f"Its area is {city[AREA].strip()}."
    elif field == MAYOR:
        return f"The mayor of this city is {city[MAYOR].strip()}."
    return None

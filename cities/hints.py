POPULATION = "population"
STATE = "state"
STATE_CODE = "state_code"
FOUNDED = "founded"
MAYOR = "mayor"
AREA = "area"

HINT_SLOT_ORDER = (
    FOUNDED,
    POPULATION,
    STATE,
    AREA,
    MAYOR,
)


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _has_required_fields(city: dict) -> bool:
    if not isinstance(city, dict):
        return False

    for field in HINT_SLOT_ORDER:
        if not _is_non_empty_string(city.get(field)):
            return False

    return True


def build_cities_hints(city: dict) -> list[str]:
    if not _has_required_fields(city):
        return []

    founded = city[FOUNDED].strip()
    population = city[POPULATION].strip()
    state = city[STATE].strip()
    area = city[AREA].strip()
    mayor = city[MAYOR].strip()

    return [
        f"This city was founded in {founded}.",
        f"Its population is about {population}.",
        f"This city is in {state}.",
        f"Its area is {area}.",
        f"The mayor of this city is {mayor}.",
    ]

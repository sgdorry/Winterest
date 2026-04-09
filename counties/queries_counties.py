from functools import wraps
import data.db_connect as dbc

COLLECTION = 'counties'

MIN_ID_LEN = 1
ID = 'id'
NAME = 'name'
POPULATION = 'population'
STATE = 'state'
AREA = 'area'
FOUNDED = 'founded'
COUNTY_SEAT = 'county_seat'
STATE_CODE = 'STATE_CODE'

SAMPLE_COUNTY = {
    NAME: 'Los Angeles County',
    POPULATION: 10000000,
    STATE: 'California',
    AREA: '4,751 sq mi',
    FOUNDED: '1850',
    COUNTY_SEAT: 'Los Angeles',
    STATE_CODE: 'CA'
}

county_cache = {
    1: SAMPLE_COUNTY,
}


def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not county_cache:
            docs = dbc.read(COLLECTION)
            for doc in docs:
                county_id = doc.get(ID)
                if county_id is not None:
                    county_cache[county_id] = doc
        return fn(*args, **kwargs)
    return wrapper


def is_valid_id(_id: str):
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


@needs_cache
def num_counties():
    return len(county_cache)


def is_valid_population(_population):
    if not isinstance(_population, int):
        return False
    if _population < 0:
        return False
    return True


def create(fields: dict):

    if not isinstance(fields, dict):
        raise ValueError(f'Bad type for {type(fields)=}')

    if not fields.get(NAME) or not isinstance(fields[NAME], str):
        raise ValueError(f'Bad value for {fields.get(NAME)=}')

    if not fields.get(POPULATION) or not isinstance(fields[POPULATION], int):
        raise ValueError(f'Bad value for {fields.get(POPULATION)=}')

    if not fields.get(STATE) or not isinstance(fields[STATE], str):
        raise ValueError(f'Bad value for {fields.get(STATE)=}')

    if not fields.get(AREA) or not isinstance(fields[AREA], str):
        raise ValueError(f'Bad value for {fields.get(AREA)=}')

    if not fields.get(FOUNDED) or not isinstance(fields[FOUNDED], str):
        raise ValueError(f'Bad value for {fields.get(FOUNDED)=}')

    if not fields.get(COUNTY_SEAT) or not isinstance(fields[COUNTY_SEAT], str):
        raise ValueError(f'Bad value for {fields.get(COUNTY_SEAT)=}')

    new_id = dbc.create(COLLECTION, fields)
    county_cache[new_id] = fields
    return new_id


@needs_cache
def read(county_id=None):
    return dbc.read(COLLECTION)


def update(name: str, state_code: str, fields: dict):
    if not isinstance(fields, dict):
        raise ValueError(f'Bad type for {type(fields)=}')
    if not name or not isinstance(name, str):
        raise ValueError(f'Bad value for {name=}')
    if not state_code or not isinstance(state_code, str):
        raise ValueError(f'Bad value for {state_code=}')

    # Validate fields if provided
    if NAME in fields and (not fields[NAME] or
                           not isinstance(fields[NAME], str)):
        raise ValueError(f'Bad value for {fields.get(NAME)=}')
    if POPULATION in fields and (not isinstance(fields[POPULATION], int) or
                                 fields[POPULATION] < 0):
        raise ValueError(f'Bad value for {fields.get(POPULATION)=}')
    if STATE in fields and (not fields[STATE] or
                            not isinstance(fields[STATE], str)):
        raise ValueError(f'Bad value for {fields.get(STATE)=}')
    if AREA in fields and (not fields[AREA] or
                           not isinstance(fields[AREA], str)):
        raise ValueError(f'Bad value for {fields.get(AREA)=}')
    if FOUNDED in fields and (not fields[FOUNDED] or
                              not isinstance(fields[FOUNDED], str)):
        raise ValueError(f'Bad value for {fields.get(FOUNDED)=}')
    if COUNTY_SEAT in fields and (not fields[COUNTY_SEAT] or
                                  not isinstance(fields[COUNTY_SEAT], str)):
        raise ValueError(f'Bad value for {fields.get(COUNTY_SEAT)=}')
    if STATE_CODE in fields and (not fields[STATE_CODE] or
                                 not isinstance(fields[STATE_CODE], str)):
        raise ValueError(f'Bad value for {fields.get(STATE_CODE)=}')

    result = dbc.update(COLLECTION, {NAME: name, STATE_CODE: state_code},
                        fields)
    if result < 1:
        raise ValueError(f'County not found: {name}, {state_code}')

    # Update cache
    if county_cache:
        for key, county in county_cache.items():
            if (county.get(NAME) == name and
                    county.get(STATE_CODE) == state_code):
                county_cache[key].update(fields)
                break

    return result


def delete(name: str, state_code: str):
    result = dbc.delete(COLLECTION, {NAME: name, STATE_CODE: state_code})
    if result < 1:
        raise ValueError(f'County not found: {name}, {state_code}')
    return result

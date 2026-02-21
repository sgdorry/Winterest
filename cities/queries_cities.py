from functools import wraps
import data.db_connect as dbc
COLLECTION = 'cities'

MIN_ID_LEN = 1
ID = 'id'
NAME = 'name'
POPULATION = 'population'
STATE = 'state'
AREA = 'area'
FOUNDED = 'founded'
MAYOR = 'mayor'
STATE_CODE = 'state_code'

SAMPLE_CITY = {
    NAME: 'New York City',
    POPULATION: '8,478,000',
    STATE: 'New York',
    STATE_CODE: 'NY',
    AREA: '469 sq mi',
    FOUNDED: '1624',
    MAYOR: 'Eric Adams'
}


city_cache = {
    1: SAMPLE_CITY
}


def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not city_cache:
            docs = dbc.read(COLLECTION)
            for doc in docs:
                county_id = doc.get(ID)
                if county_id is not None:
                    city_cache[county_id] = doc
        return fn(*args, **kwargs)
    return wrapper


def is_valid_id(_id: str):
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


@needs_cache
def num_cities():
    return len(city_cache)


@needs_cache
def create(fields: dict):
    if (not isinstance(fields, dict)):
        raise ValueError(f'Bad type for {type(fields)=}')
    if (not fields.get(NAME)):
        raise ValueError(f'Bad value for {fields.get(NAME)=}')
    if (not fields.get(STATE_CODE)
            or not isinstance(fields[STATE_CODE], str)
            or len(fields[STATE_CODE]) < MIN_ID_LEN):
        raise ValueError(
            f'Bad value for {fields.get(STATE_CODE)=}'
        )
    new_id = dbc.create(COLLECTION, fields)
    city_cache[new_id] = fields
    return new_id


@needs_cache
def read(city_id=None):
    return dbc.read(COLLECTION)


def update(name: str, fields: dict):
    if not isinstance(fields, dict):
        raise ValueError(f'Bad type for {type(fields)=}')
    if not name or not isinstance(name, str):
        raise ValueError(f'Bad value for {name=}')

    # Validate fields if provided
    if NAME in fields and (not fields[NAME] or
                           not isinstance(fields[NAME], str)):
        raise ValueError(f'Bad value for {fields.get(NAME)=}')
    if STATE in fields and (not fields[STATE] or
                            not isinstance(fields[STATE], str)):
        raise ValueError(f'Bad value for {fields.get(STATE)=}')
    if STATE_CODE in fields and (not fields[STATE_CODE] or
                                 not isinstance(fields[STATE_CODE], str) or
                                 len(fields[STATE_CODE]) < MIN_ID_LEN):
        raise ValueError(f'Bad value for {fields.get(STATE_CODE)=}')
    if POPULATION in fields and (not fields[POPULATION] or
                                 not isinstance(fields[POPULATION], str)):
        raise ValueError(f'Bad value for {fields.get(POPULATION)=}')
    if AREA in fields and (not fields[AREA] or
                           not isinstance(fields[AREA], str)):
        raise ValueError(f'Bad value for {fields.get(AREA)=}')
    if FOUNDED in fields and (not fields[FOUNDED] or
                              not isinstance(fields[FOUNDED], str)):
        raise ValueError(f'Bad value for {fields.get(FOUNDED)=}')
    if MAYOR in fields and (not fields[MAYOR] or
                            not isinstance(fields[MAYOR], str)):
        raise ValueError(f'Bad value for {fields.get(MAYOR)=}')

    result = dbc.update(COLLECTION, {NAME: name}, fields)
    if result < 1:
        raise ValueError(f'City not found: {name}')

    # Update cache
    if city_cache:
        for key, city in city_cache.items():
            if city.get(NAME) == name:
                city_cache[key].update(fields)
                break

    return result


def delete(name: str):
    result = dbc.delete(COLLECTION, {NAME: name})
    if result < 1:
        raise ValueError(f'City not found: {name}')
    return result

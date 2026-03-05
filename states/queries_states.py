from functools import wraps
import data.db_connect as dbc

COLLECTION = 'states'

MIN_ID_LEN = 1
ID = 'id'
NAME = 'name'
POPULATION = 'population'
AREA = 'area'
STATEHOOD_DATE = 'statehood_date'
GDP = 'gdp'
CAPITAL = 'capital'
GOVERNOR = 'governor'
CODE = 'code'

SAMPLE_STATE = {
    NAME: 'New York',
    POPULATION: 19870000,
    AREA: '54,556 sq miles',
    STATEHOOD_DATE: '07/26/1788',
    GDP: '2.32 trillion USD',
    CAPITAL: 'Albany',
    GOVERNOR: 'Kathy Hochul',
    CODE: 'NY'
}

state_cache = {
    "1": SAMPLE_STATE,
}


def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not state_cache:
            docs = dbc.read(COLLECTION)
            for doc in docs:
                state_id = doc.get(ID)
                if state_id is not None:
                    state_cache[state_id] = doc
        return fn(*args, **kwargs)
    return wrapper


def is_valid_id(_id: str):
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def is_valid_population(_population):
    if not isinstance(_population, int):
        return False
    if _population < 0:
        return False
    return True


def is_valid_governor(_governor: str):
    if not isinstance(_governor, str):
        return False
    if len(_governor) < MIN_ID_LEN:
        return False
    return True


@needs_cache
def num_states():
    return len(state_cache)


def create(fields: dict):
    if (not isinstance(fields, dict)):
        raise ValueError(f'Bad type for {type(fields)=}')
    if (not fields.get(NAME) or not isinstance(fields[NAME], str)):
        raise ValueError(f'Bad value for {fields.get(NAME)=}')
    if (not fields.get(CAPITAL) or not isinstance(fields[CAPITAL], str)):
        raise ValueError(f'Bad value for {fields.get(CAPITAL)=}')
    if (not fields.get(POPULATION) 
        or not isinstance(fields[POPULATION], int)):
        raise ValueError(f'Bad value for {fields.get(POPULATION)=}')
    if (not fields.get(AREA) or not isinstance(fields[AREA], str)):
        raise ValueError(f'Bad value for {fields.get(AREA)=}')
    if (not fields.get(STATEHOOD_DATE) or 
        not isinstance(fields[STATEHOOD_DATE], str)):
        raise ValueError(f'Bad value for {fields.get(AREA)=}')
    if (not fields.get(GDP) or not isinstance(fields[GDP], str)):
        raise ValueError(f'Bad value for {fields.get(GDP)=}')
    
    new_id = dbc.create(COLLECTION, fields)
    state_cache[new_id] = fields
    return new_id


@needs_cache
def read(state_id=None):
    return dbc.read(COLLECTION)


def update(state_id: str, fields: dict):
    if not isinstance(fields, dict):
        raise ValueError(f'Bad type for {type(fields)=}')
    if not state_id or not isinstance(state_id, str):
        raise ValueError(f'Bad value for {state_id=}')

    # Validate fields if provided
    if NAME in fields and (not fields[NAME] or
                           not isinstance(fields[NAME], str)):
        raise ValueError(f'Bad value for {fields.get(NAME)=}')
    if CAPITAL in fields and (not fields[CAPITAL] or
                              not isinstance(fields[CAPITAL], str)):
        raise ValueError(f'Bad value for {fields.get(CAPITAL)=}')
    if POPULATION in fields and (not isinstance(fields[POPULATION], int) or
                                 fields[POPULATION] < 0):
        raise ValueError(f'Bad value for {fields.get(POPULATION)=}')
    if CODE in fields and (not fields[CODE] or
                           not isinstance(fields[CODE], str)):
        raise ValueError(f'Bad value for {fields.get(CODE)=}')
    if GOVERNOR in fields and (not fields[GOVERNOR] or
                               not isinstance(fields[GOVERNOR], str)):
        raise ValueError(f'Bad value for {fields.get(GOVERNOR)=}')
    if AREA in fields and (not fields[AREA] or
                               not isinstance(fields[AREA], str)):
        raise ValueError(f'Bad value for {fields.get(AREA)=}')
    if GDP in fields and (not fields[GDP] or
                               not isinstance(fields[GDP], str)):
        raise ValueError(f'Bad value for {fields.get(GDP)=}')
    if STATEHOOD_DATE in fields and (not fields[STATEHOOD_DATE] or
                               not isinstance(fields[STATEHOOD_DATE], str)):
        raise ValueError(f'Bad value for {fields.get(STATEHOOD_DATE)=}')

    result = dbc.update(COLLECTION, {ID: state_id}, fields)
    if result < 1:
        raise ValueError(f'State not found: {state_id}')

    # Update cache
    if state_cache and state_id in state_cache:
        state_cache[state_id].update(fields)

    return result


def delete(state_id: str):
    if state_id not in state_cache:
        raise ValueError(f'No such state: {state_id}')
    del state_cache[state_id]
    return True

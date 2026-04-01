import data.db_connect as dbc

from functools import wraps

COUNTRIES_COLLECTION = "countries"

MIN_ID_LEN = 1
COUNTRY_ID = 'country_id'
ID = 'id'
NAME = 'name'
POPULATION = 'population'
CONTINENT = 'continent'
CAPITAL = 'capital'
GDP = 'gdp'
AREA = 'area'
FOUNDED = 'founded'
PRESIDENT = 'president'
FLAG_COLOR = 'flag_color'
LANGUAGE = 'language'
CLIMATE = 'climate'


SAMPLE_COUNTRY = {
    COUNTRY_ID: 'US',
    NAME: 'United States of America',
    POPULATION: 340000000,
    CONTINENT: 'North America',
    CAPITAL: 'Washington DC',
    GDP: '29.18 trillion USD',
    AREA: '3,810,000 sq mi',
    FOUNDED: '1776',
    PRESIDENT: 'Donald Trump',
    FLAG_COLOR: 'Red, White, and Blue',
    LANGUAGE: 'English',
    CLIMATE: 'Varies widely by region; temperate to subtropical'
}


country_cache = None


def _normalized_country_id(country_id: str):
    if not isinstance(country_id, str):
        return None
    normalized = country_id.strip().upper()
    if len(normalized) < MIN_ID_LEN:
        return None
    return normalized


def _country_id_from_doc(doc: dict):
    country_id = _normalized_country_id(doc.get(COUNTRY_ID))
    if country_id:
        return country_id
    return _normalized_country_id(doc.get(ID))


def _normalize_country_doc(doc: dict):
    if not isinstance(doc, dict):
        return doc
    normalized_doc = dict(doc)
    normalized_country_id = _country_id_from_doc(normalized_doc)
    if normalized_country_id:
        normalized_doc[COUNTRY_ID] = normalized_country_id
        if ID in normalized_doc:
            del normalized_doc[ID]
    return normalized_doc


def _normalize_country_fields(fields: dict):
    normalized_fields = dict(fields)
    if COUNTRY_ID not in normalized_fields and ID in normalized_fields:
        normalized_fields[COUNTRY_ID] = normalized_fields[ID]
    normalized_country_id = _normalized_country_id(
        normalized_fields.get(COUNTRY_ID)
    )
    if normalized_country_id:
        normalized_fields[COUNTRY_ID] = normalized_country_id
    if ID in normalized_fields:
        del normalized_fields[ID]
    return normalized_fields


def _country_id_filter(country_id: str):
    return {'$or': [{COUNTRY_ID: country_id}, {ID: country_id}]}


def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        global country_cache
        if not country_cache:
            country_cache = {}
            docs = dbc.read(COUNTRIES_COLLECTION)
            for doc in docs:
                country_id = _country_id_from_doc(doc)
                if country_id is not None:
                    country_cache[country_id] = _normalize_country_doc(doc)
        return fn(*args, **kwargs)
    return wrapper


def is_valid_id(_id: str):
    return _normalized_country_id(_id) is not None


def is_valid_population(_population):
    if not isinstance(_population, int):
        return False
    if _population < 0:
        return False
    return True


@needs_cache
def num_countries():
    return len(country_cache)


@needs_cache
def create(fields: dict):
    if (not isinstance(fields, dict)):
        raise ValueError(f'Bad type for {type(fields)=}')
    fields = _normalize_country_fields(fields)
    normalized_country_id = _normalized_country_id(fields.get(COUNTRY_ID))
    if not normalized_country_id:
        raise ValueError(f'Bad value for {fields.get(COUNTRY_ID)=}')
    fields[COUNTRY_ID] = normalized_country_id
    existing_country = dbc.read_one(
        COUNTRIES_COLLECTION,
        _country_id_filter(fields[COUNTRY_ID]),
    )
    if existing_country:
        raise ValueError(f'Country ID already exists: {fields[COUNTRY_ID]}')
    if (not fields.get(NAME) or not isinstance(fields[NAME], str)):
        raise ValueError(f'Bad value for {fields.get(NAME)=}')
    if (not fields.get(POPULATION) or not isinstance(fields[POPULATION], int)):
        raise ValueError(f'Bad value for {fields.get(POPULATION)=}')
    if (not fields.get(CONTINENT) or not isinstance(fields[CONTINENT],
                                                    str)):
        raise ValueError(f'Bad value for {fields.get(CONTINENT)=}')
    if (not fields.get(CAPITAL) or not isinstance(fields[CAPITAL], str)):
        raise ValueError(f'Bad value for {fields.get(CAPITAL)=}')
    if (not fields.get(GDP) or not isinstance(fields[GDP], str)):
        raise ValueError(f'Bad value for {fields.get(GDP)=}')
    if (not fields.get(AREA) or not isinstance(fields[AREA], str)):
        raise ValueError(f'Bad value for {fields.get(AREA)=}')
    if (not fields.get(FOUNDED) or not isinstance(fields[FOUNDED], str)):
        raise ValueError(f'Bad value for {fields.get(FOUNDED)=}')
    if (not fields.get(PRESIDENT) or not isinstance(fields[PRESIDENT], str)):
        raise ValueError(f'Bad value for {fields.get(PRESIDENT)=}')
    if (not fields.get(FLAG_COLOR) or not isinstance(fields[FLAG_COLOR], str)):
        raise ValueError(f'Bad value for {fields.get(FLAG_COLOR)=}')
    if (not fields.get(LANGUAGE) or not isinstance(fields[LANGUAGE], str)):
        raise ValueError(f'Bad value for {fields.get(LANGUAGE)=}')
    if (not fields.get(CLIMATE) or not isinstance(fields[CLIMATE], str)):
        raise ValueError(f'Bad value for {fields.get(CLIMATE)=}')
    new_id = dbc.create(COUNTRIES_COLLECTION, fields)
    country_cache[fields[COUNTRY_ID]] = fields
    return new_id


@needs_cache
def read(country_id=None):
    if country_id is None:
        all_countries = dbc.read(COUNTRIES_COLLECTION)
        return [_normalize_country_doc(country) for country in all_countries]

    normalized_country_id = _normalized_country_id(country_id)
    if not normalized_country_id:
        raise ValueError(f'Bad value for {country_id=}')

    country = dbc.read_one(
        COUNTRIES_COLLECTION,
        _country_id_filter(normalized_country_id),
    )
    return _normalize_country_doc(country)


def update(country_id: str, fields: dict):
    if not isinstance(fields, dict):
        raise ValueError(f'Bad type for {type(fields)=}')
    normalized_country_id = _normalized_country_id(country_id)
    if not normalized_country_id:
        raise ValueError(f'Bad value for {country_id=}')
    fields = _normalize_country_fields(fields)
    if COUNTRY_ID in fields:
        raise ValueError(f'Cannot update {COUNTRY_ID}.')

    # Validate fields if provided
    if NAME in fields and (not fields[NAME] or
                           not isinstance(fields[NAME], str)):
        raise ValueError(f'Bad value for {fields.get(NAME)=}')
    if POPULATION in fields and (not isinstance(fields[POPULATION], int) or
                                 fields[POPULATION] < 0):
        raise ValueError(f'Bad value for {fields.get(POPULATION)=}')
    if CONTINENT in fields and (not fields[CONTINENT] or
                                not isinstance(fields[CONTINENT], str)):
        raise ValueError(f'Bad value for {fields.get(CONTINENT)=}')
    if CAPITAL in fields and (not fields[CAPITAL] or
                              not isinstance(fields[CAPITAL], str)):
        raise ValueError(f'Bad value for {fields.get(CAPITAL)=}')
    if GDP in fields and (not fields[GDP] or
                          not isinstance(fields[GDP], str)):
        raise ValueError(f'Bad value for {fields.get(GDP)=}')
    if AREA in fields and (not fields[AREA] or
                           not isinstance(fields[AREA], str)):
        raise ValueError(f'Bad value for {fields.get(AREA)=}')
    if FOUNDED in fields and (not fields[FOUNDED] or
                              not isinstance(fields[FOUNDED], str)):
        raise ValueError(f'Bad value for {fields.get(FOUNDED)=}')
    if PRESIDENT in fields and (not fields[PRESIDENT] or
                                not isinstance(fields[PRESIDENT], str)):
        raise ValueError(f'Bad value for {fields.get(PRESIDENT)=}')
    if FLAG_COLOR in fields and (not fields[FLAG_COLOR] or
                                 not isinstance(fields[FLAG_COLOR], str)):
        raise ValueError(f'Bad value for {fields.get(FLAG_COLOR)=}')
    if LANGUAGE in fields and (not fields[LANGUAGE] or
                               not isinstance(fields[LANGUAGE], str)):
        raise ValueError(f'Bad value for {fields.get(LANGUAGE)=}')
    if CLIMATE in fields and (not fields[CLIMATE] or
                              not isinstance(fields[CLIMATE], str)):
        raise ValueError(f'Bad value for {fields.get(CLIMATE)=}')

    result = dbc.update(
        COUNTRIES_COLLECTION,
        _country_id_filter(normalized_country_id),
        fields,
    )
    if result < 1:
        raise ValueError(f'Country not found: {country_id}')

    # Update cache
    if country_cache and normalized_country_id in country_cache:
        country_cache[normalized_country_id].update(fields)

    return result


def delete(country_id: str):
    normalized_country_id = _normalized_country_id(country_id)
    if not normalized_country_id:
        raise ValueError(f'Bad value for {country_id=}')
    result = dbc.delete(COUNTRIES_COLLECTION,
                        _country_id_filter(normalized_country_id))
    if result < 1:
        raise ValueError(f'Country not found: {country_id}')
    if country_cache and normalized_country_id in country_cache:
        del country_cache[normalized_country_id]
    return result

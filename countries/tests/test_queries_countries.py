from copy import deepcopy
from unittest.mock import patch
import pytest
from contextlib import contextmanager

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import queries_countries as qry


def make_country(country_id='US'):
    country = deepcopy(qry.SAMPLE_COUNTRY)
    country[qry.COUNTRY_ID] = country_id
    return country


@pytest.fixture(autouse=True)
def clear_country_cache():
    qry.country_cache = None
    yield
    qry.country_cache = None


@patch('data.db_connect.read')
def test_num_countries_is_cached(mock_read):
    mock_read.return_value = [
        make_country('US'),
        make_country('CA'),
    ]

    assert qry.num_countries() == 2
    assert qry.num_countries() == 2
    assert mock_read.call_count == 1


@patch('data.db_connect.read')
def test_read_all_normalizes_legacy_id(mock_read):
    legacy_doc = make_country()
    legacy_doc[qry.ID] = 'us'
    del legacy_doc[qry.COUNTRY_ID]
    mock_read.return_value = [legacy_doc]

    countries = qry.read()

    assert len(countries) == 1
    assert countries[0][qry.COUNTRY_ID] == 'US'
    assert qry.ID not in countries[0]


@patch('data.db_connect.read')
@patch('data.db_connect.read_one')
def test_read_by_country_id_uses_single_doc_lookup(mock_read_one, mock_read):
    mock_read.return_value = []
    mock_read_one.return_value = make_country('ca')

    country = qry.read('ca')

    assert country[qry.COUNTRY_ID] == 'CA'
    mock_read_one.assert_called_once_with(
        qry.COUNTRIES_COLLECTION,
        {'$or': [{qry.COUNTRY_ID: 'CA'}, {qry.ID: 'CA'}]},
    )


@patch('data.db_connect.read')
def test_read_by_country_id_bad_id(mock_read):
    mock_read.return_value = []
    with pytest.raises(ValueError):
        qry.read('')


@patch('data.db_connect.read')
@patch('data.db_connect.read_one')
def test_create_requires_country_id(mock_read_one, mock_read):
    payload = make_country()
    del payload[qry.COUNTRY_ID]
    mock_read.return_value = []
    mock_read_one.return_value = None

    with pytest.raises(ValueError):
        qry.create(payload)
        
@pytest.fixture
def country_delta():
    @contextmanager
    def _country_delta(delta=0):
        old_count = qry.num_countries()
        yield
        new_count = qry.num_countries()
        assert new_count - old_count == delta
    return _country_delta

def test_bad_name(country_delta):
    with country_delta():
        with pytest.raises(Exception):
            qry.create({'id': 'US', 'name': 5, 'population': 340000000, 'continent': 'North America', 
                        'capital': 'Washington DC', 'gdp': '29.18 trillion USD', 'area': '3,810,000 sq mi', 
                        'founded': '1776', 'president': 'Donald Trump', 'flag_color': 'Red, White, and Blue', 
                        'language': 'English', 'climate': 'Varies widely by region; temperate to subtropical'})
        
def test_bad_population(country_delta):
    with country_delta():
        with pytest.raises(Exception):
            qry.create({'id': 'US', 'name': 'United States of America', 'population': 'bruh', 'continent': 'North America', 
                        'capital': 'Washington DC', 'gdp': '29.18 trillion USD', 'area': '3,810,000 sq mi', 
                        'founded': '1776', 'president': 'Donald Trump', 'flag_color': 'Red, White, and Blue', 
                        'language': 'English', 'climate': 'Varies widely by region; temperate to subtropical'})

@patch('data.db_connect.read')
@patch('data.db_connect.read_one')
@patch('data.db_connect.create')
def test_create_normalizes_legacy_id(
        mock_create, mock_read_one, mock_read):
    payload = make_country()
    payload[qry.ID] = 'us'
    del payload[qry.COUNTRY_ID]
    mock_read.return_value = []
    mock_read_one.return_value = None
    mock_create.return_value = 'mongo-id'

    result = qry.create(payload)

    assert result == 'mongo-id'
    created_doc = mock_create.call_args[0][1]
    assert created_doc[qry.COUNTRY_ID] == 'US'
    assert qry.ID not in created_doc
    assert qry.country_cache['US'][qry.COUNTRY_ID] == 'US'


@patch('data.db_connect.read')
@patch('data.db_connect.read_one')
@patch('data.db_connect.create')
def test_create_rejects_duplicate_country_id(
        mock_create, mock_read_one, mock_read):
    payload = make_country('US')
    mock_read.return_value = []
    mock_read_one.return_value = make_country('US')

    with pytest.raises(ValueError):
        qry.create(payload)

    mock_create.assert_not_called()


@patch('data.db_connect.update')
def test_update_by_country_id_updates_cache(mock_update):
    qry.country_cache = {'US': make_country('US')}
    mock_update.return_value = 1

    result = qry.update('us', {qry.CAPITAL: 'Test Capital'})

    assert result == 1
    mock_update.assert_called_once_with(
        qry.COUNTRIES_COLLECTION,
        {'$or': [{qry.COUNTRY_ID: 'US'}, {qry.ID: 'US'}]},
        {qry.CAPITAL: 'Test Capital'},
    )
    assert qry.country_cache['US'][qry.CAPITAL] == 'Test Capital'


def test_update_rejects_country_id_mutation():
    with pytest.raises(ValueError):
        qry.update('US', {qry.COUNTRY_ID: 'CA'})


@patch('data.db_connect.update')
def test_update_country_not_found(mock_update):
    mock_update.return_value = 0
    with pytest.raises(ValueError):
        qry.update('US', {qry.CAPITAL: 'Test Capital'})


@patch('data.db_connect.delete')
def test_delete_by_country_id_removes_cache(mock_delete):
    qry.country_cache = {'US': make_country('US')}
    mock_delete.return_value = 1

    result = qry.delete('us')

    assert result == 1
    mock_delete.assert_called_once_with(
        qry.COUNTRIES_COLLECTION,
        {'$or': [{qry.COUNTRY_ID: 'US'}, {qry.ID: 'US'}]},
    )
    assert 'US' not in qry.country_cache


@patch('data.db_connect.delete')
def test_delete_country_not_found(mock_delete):
    mock_delete.return_value = 0
    with pytest.raises(ValueError):
        qry.delete('US')

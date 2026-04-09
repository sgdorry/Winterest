from copy import deepcopy
from unittest.mock import patch
import pytest
from contextlib import contextmanager

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import queries_counties as qry

def create_temp_county():
    return deepcopy(qry.SAMPLE_COUNTY)

@pytest.fixture(scope='function')
def temp_county():
    temp_county = create_temp_county()
    new_id = qry.create(create_temp_county())
    yield new_id
    try:
        qry.delete(temp_county[qry.NAME], temp_county[qry.STATE_CODE])
    except ValueError:
        print('The record has already been deleted.')

@pytest.fixture(scope='function')
def temp_county_no_delete():
    temp_county = create_temp_county()
    new_id = qry.create(create_temp_county())
    return temp_county
        
@pytest.fixture
def county_delta():
    @contextmanager
    def _county_delta(delta=0):
        old_count = qry.num_counties()
        yield
        new_count = qry.num_counties()
        assert new_count - old_count == delta
    return _county_delta


def test_create_bad_name():
    old_count = qry.num_counties() #current count of counties
    with pytest.raises(Exception):
        qry.create(None)
    assert qry.num_counties() == old_count #ensuring no invalid county was created

def test_create_bad_param_type():
    old_count = qry.num_counties() #current count of counties
    with pytest.raises(Exception):
        qry.create([1, 2, 3])
    assert qry.num_counties() == old_count #make sure number of counties did not change
    
def test_create_bad_state(county_delta):
    with county_delta():
        with pytest.raises(Exception):
            qry.create({'id': '1', 'name': 'Bronx', 'population': 1472654, 'state': 2305354, 'area': '42.2 sq miles', 'founded': '1914','county_seat': 'Bronx Borough Hall'})

def test_create_bad_population(county_delta):
    with county_delta():
        with pytest.raises(Exception):
            qry.create({'id': '1', 'name': 'Bronx', 'population': 'test', 'state': 'New York', 'area': '42.2 sq miles', 'founded': '1914','county_seat': 'Bronx Borough Hall'})


def test_read(temp_county):
    all_counties = qry.read()
    assert isinstance(all_counties, list)
    assert create_temp_county() in all_counties

def test_delete(temp_county_no_delete):
    result = qry.delete(temp_county_no_delete[qry.NAME], temp_county_no_delete[qry.STATE_CODE])
    assert result == 1

@pytest.mark.skip
@patch('data.db_connect.read')
def test_read_cant_connect(mock_dbc_read):
    from data.db_connect import DBError
    mock_dbc_read.side_effect = DBError("Connection failed")
    with pytest.raises(DBError):
        counties = qry.read()


@pytest.mark.skip
def test_good_create(temp_county):
    assert qry.is_valid_id(temp_county) # checking if the id is valid
    assert temp_county in qry.county_cache # verify the county was created


def test_create_bad_population():
    old_count = qry.num_counties() #current count of counties
    with pytest.raises(Exception):
        qry.create({'name': 'Test County', 'population': 'not a number', 'state': 'California', 'area': '100 sq mi', 'founded': '1900', 'county_seat': 'Test City'})
    assert qry.num_counties() == old_count #ensuring no invalid county was created

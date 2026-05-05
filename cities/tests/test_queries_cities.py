from copy import deepcopy
from unittest.mock import patch
import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import queries_cities as qry
def create_temp_city():
    return deepcopy(qry.SAMPLE_CITY)

@pytest.fixture(scope='function')
def temp_city():
    temp_city = create_temp_city()
    new_id = qry.create(create_temp_city())
    yield new_id
    try:
        qry.delete(new_id)
    except ValueError:
        print('The record has already been deleted.')


@pytest.fixture(scope='function')
def temp_city_no_delete():
    temp_city = create_temp_city()
    new_id = qry.create(create_temp_city())
    return (temp_city, new_id)


@pytest.mark.skip
def test_num_cities(temp_city):
    # verify the city was created and is counted
    assert qry.is_valid_id(temp_city)
    assert temp_city in qry.city_cache

@pytest.mark.skip
def test_good_create(temp_city):
    assert qry.is_valid_id(temp_city) # checking if the id is valid
    assert temp_city in qry.city_cache # verify the city was created

def test_create_bad_name():
    old_count = qry.num_cities() #current count of cities
    with pytest.raises(Exception):
        qry.create(None)
    assert qry.num_cities() == old_count #ensuring no invalid citie was created
    
def test_create_bad_param_type():
    old_count = qry.num_cities() #current count of cities
    with pytest.raises(Exception):
        qry.create([1, 2, 3])
    assert qry.num_cities() == old_count #make sure number of cities did not change


def test_read(temp_city):
    # test reading all cities
    all_cities = qry.read()
    assert isinstance(all_cities, list)
    assert create_temp_city() in all_cities

@pytest.mark.skip
@patch('data.db_connect.read')
def test_read_cant_connect(mock_dbc_read):
    from data.db_connect import DBError
    mock_dbc_read.side_effect = DBError("Connection failed")
    with pytest.raises(DBError):
        cities = qry.read()


def test_bad_test_for_num_cities():
    # test that num_cities returns a valid non-negative integer
    count = qry.num_cities()
    assert isinstance(count, int)
    assert count >= 0


def test_bad_name(temp_city):
    old_count = qry.num_cities() #current count of cities
    with pytest.raises(Exception):
        qry.create({'id': '1', 'name': 5, 'population': 19870000, 'state': 'New York', 
                    'mayor': 'Zohran Mamdani', 'area': '469 sq mi', 'founded': '1624', 'gdp': '1.5 trillion USD', 
                    'climate': 'Humid subtropical', 'nickname': 'The Big Apple'})


def test_bad_population(temp_city):
    old_count = qry.num_cities() #current count of cities
    with pytest.raises(Exception):
        qry.create({'id': '1', 'name': 'New York City', 'population': 'bruh', 'state': 'New York', 
                    'mayor': 'Zohran Mamdani', 'area': '469 sq mi', 'founded': '1624', 'gdp': '1.5 trillion USD', 
                    'climate': 'Humid subtropical', 'nickname': 'The Big Apple'}) 

#updating the connection broke this test the person who updates delete to use the state code and city name will be able to fix this test
@pytest.mark.skip 
def test_delete(temp_city_no_delete):
    assert temp_city in qry.city_cache
    with city_delta(-1): #expecting num_cities to decrease -1
        # delete the city
        qry.delete(temp_city)
    # verify it's no longer in the cache
    assert temp_city not in qry.city_cache

def test_city_has_valid_state():
    city = create_temp_city()
    state = city.get(qry.STATE, "").strip()

    # Ensure 'state' field exists and has a non-empty string
    assert state, "City record should contain a non-empty 'state' value"
    assert isinstance(state, str), "'state' should be a string"
    
    invalid_values = {"unknown", "n/a", "none", "null", ""}
    assert state.lower() not in invalid_values, f"Invalid state value: {state}"

    valid_states = {
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
        "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
        "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
        "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
        "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
        "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
    }
    assert state in valid_states, f"'{state}' is not a recognized valid US state"

@pytest.fixture
def db_failure():
    with patch('data.db_connect.read') as mock_dbc_read:
        mock_dbc_read.side_effect = Exception("Database failure")
        yield mock_dbc_read

@pytest.mark.skip
def test_read_handles_db_failure(db_failure):
    with pytest.raises(Exception) as exc_info:
        qry.read("123")
    assert "Database failure" in str(exc_info.value)


def test_city_has_valid_mayor():
    city = create_temp_city()
    mayor = city.get(qry.MAYOR, "")

    # Ensure 'state' field exists and has a non-empty string
    assert mayor, "City record should contain a non-rempty 'mayor' value"
    assert isinstance(mayor, str), "'mayor' should be a string"

    # Check that mayor name is not a placeholder or invalid value
    invalid_values = {"unknown", "n/a", "none", "null", "tbd", "vacant", ""}
    assert mayor.lower() not in invalid_values, f"Invalid mayor name: {mayor}"

    test_city = {
        qry.NAME: 'Test City',
        qry.POPULATION: '1,000',
        qry.STATE: 'Arkansas',
        qry.MAYOR: 'Richard'
    }

    test_mayor = test_city.get(qry.MAYOR)
    assert test_mayor == 'Richard', f"Expected mayor 'Richard, got '{test_mayor}'"
    assert isinstance(test_mayor, str), "Mayor name should be a string"
    assert len(test_mayor) > 0, "Mayor name should not be empty"
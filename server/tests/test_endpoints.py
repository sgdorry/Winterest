from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
    CREATED,
)
from unittest.mock import patch

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import endpoints as ep

TEST_CLIENT = ep.app.test_client()


def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


@patch('countries.queries_countries.read')
def test_get_all_countries(mock_read):
    """Test GET /countries endpoint"""
    mock_read.return_value = []
    resp = TEST_CLIENT.get('/countries')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'countries' in resp_json
    assert isinstance(resp_json['countries'], list)


@patch('countries.queries_countries.read')
def test_get_all_countries_includes_computed_hints(mock_read):
    """Test GET /countries returns ordered computed hints for complete docs"""
    mock_read.return_value = [{
        'country_id': 'CA',
        'name': 'Canada',
        'continent': 'North America',
        'climate': 'mostly cold with temperate regions in the south',
        'language': 'English and French',
        'population': 41000000,
        'capital': 'Ottawa',
        'gdp': '2.2 trillion USD',
        'area': '3,855,100 sq mi',
        'founded': '1867',
        'president': 'N/A',
        'flag_color': 'Red and White',
    }]

    resp = TEST_CLIENT.get('/countries')

    assert resp.status_code == OK
    resp_json = resp.get_json()
    country = resp_json['countries'][0]

    assert country['name'] == 'Canada'
    assert 'hints' in country
    assert len(country['hints']) == 5
    assert all(isinstance(hint, str) for hint in country['hints'])


@patch('countries.queries_countries.read')
def test_get_all_countries_returns_empty_hints_when_required_field_missing(
        mock_read):
    """Test GET /countries returns [] hints for incomplete country docs"""
    mock_read.return_value = [{
        'country_id': 'FR',
        'name': 'France',
        'continent': 'Europe',
        'language': 'French',
        'population': 68000000,
        'capital': 'Paris',
    }]

    resp = TEST_CLIENT.get('/countries')

    assert resp.status_code == OK
    resp_json = resp.get_json()
    country = resp_json['countries'][0]

    assert country['name'] == 'France'
    assert country['hints'] == []


@patch('states.queries_states.read')
def test_get_all_states(mock_read):
    """Test GET /states endpoint"""
    mock_read.return_value = []
    resp = TEST_CLIENT.get('/states')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'states' in resp_json
    assert isinstance(resp_json['states'], list)


@patch('cities.queries_cities.read')
def test_get_all_cities(mock_read):
    """Test GET /cities endpoint"""
    mock_read.return_value = []
    resp = TEST_CLIENT.get('/cities')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'cities' in resp_json
    assert isinstance(resp_json['cities'], list)


@patch('countries.queries_countries.create')
def test_create_country(mock_create):
    """Test POST /countries endpoint"""
    mock_create.return_value = 'test-id'
    country_data = {
        'name': 'Test Country',
        'population': 1000000,
        'contentient': 'Test Continent',
        'capital': 'Test Capital',
        'gdp': '1.5 trillion USD',
        'area': '500,000 sq mi',
        'founded': '2000',
        'president': 'Test President'
    }

    resp = TEST_CLIENT.post('/countries', json=country_data)

    assert resp.status_code == CREATED
    resp_json = resp.get_json()
    assert 'id' in resp_json
    assert 'message' in resp_json


@patch('states.queries_states.create')
def test_create_state(mock_create):
    """Test POST /states endpoint"""
    mock_create.return_value = 'test-id'
    state_data = {
        'name': 'Test State',
        'population': 5000000,
        'capital': 'Test Capital',
        'governor': 'Test Governor',
        'country_code': 'US',
        'code': 'TS'
    }

    resp = TEST_CLIENT.post('/states', json=state_data)

    assert resp.status_code == CREATED
    resp_json = resp.get_json()
    assert 'id' in resp_json
    assert 'message' in resp_json


@patch('cities.queries_cities.create')
def test_create_city(mock_create):
    """Test POST /cities endpoint"""
    mock_create.return_value = 'test-id'
    city_data = {
        'name': 'Test City',
        'population': '100,000',
        'state': 'Test State',
        'state_code': 'TS',
        'area': '50 sq mi',
        'founded': '1950',
        'mayor': 'Test Mayor'
    }

    resp = TEST_CLIENT.post('/cities', json=city_data)

    assert resp.status_code == CREATED
    resp_json = resp.get_json()
    assert 'id' in resp_json
    assert 'message' in resp_json


@patch('countries.queries_countries.create')
def test_create_country_bad_data(mock_create):
    """Test POST /countries with invalid data (missing required field)"""
    mock_create.side_effect = ValueError('Bad value for population')
    bad_data = {
        'name': 'Test Country'
        # Missing required fields
    }

    resp = TEST_CLIENT.post('/countries', json=bad_data)

    assert resp.status_code == BAD_REQUEST
    resp_json = resp.get_json()
    assert 'error' in resp_json


def test_create_state_bad_data():
    """Test POST /states with invalid data"""
    bad_data = {
        'name': 'Test State',
        'population': 'not a number'
    }

    resp = TEST_CLIENT.post('/states', json=bad_data)

    assert resp.status_code == BAD_REQUEST
    resp_json = resp.get_json()
    assert 'error' in resp_json


@patch('countries.queries_countries.read')
def test_get_single_country(mock_read):
    """Test GET /countries/<id> endpoint"""
    mock_read.return_value = {
        'id': 'test-id',
        'name': 'Test Country',
        'population': 1000000
    }

    resp = TEST_CLIENT.get('/countries/test-id')

    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'name' in resp_json


@patch('countries.queries_countries.read')
def test_get_single_country_not_found(mock_read):
    """Test GET /countries/<id> with non-existent ID"""
    mock_read.return_value = None
    resp = TEST_CLIENT.get('/countries/nonexistent-id')
    assert resp.status_code == NOT_FOUND
    resp_json = resp.get_json()
    assert 'error' in resp_json


@patch('states.queries_states.read')
def test_get_single_state(mock_read):
    """Test GET /states/<id> endpoint"""
    mock_read.return_value = {
        'id': 'test-id',
        'name': 'Test State',
        'population': 5000000
    }

    resp = TEST_CLIENT.get('/states/test-id')

    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'name' in resp_json


@patch('cities.queries_cities.read')
def test_get_single_city(mock_read):
    """Test GET /cities/<id> endpoint"""
    mock_read.return_value = {
        'id': 'test-id',
        'name': 'Test City',
        'population': '100,000'
    }

    resp = TEST_CLIENT.get('/cities/test-id')

    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'name' in resp_json


@patch('countries.queries_countries.update')
def test_update_country(mock_update):
    """Test PUT /countries/<id> endpoint"""
    mock_update.return_value = 1
    update_data = {
        'population': 2000000,
        'president': 'New President'
    }

    resp = TEST_CLIENT.put('/countries/test-id', json=update_data)

    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'message' in resp_json
    assert resp_json['message'] == 'Country updated successfully'


@patch('countries.queries_countries.update')
def test_update_country_not_found(mock_update):
    """Test PUT /countries/<id> with non-existent ID"""
    mock_update.side_effect = ValueError('Country not found: test-id')
    update_data = {'population': 2000000}
    resp = TEST_CLIENT.put('/countries/nonexistent-id', json=update_data)
    assert resp.status_code == BAD_REQUEST
    resp_json = resp.get_json()
    assert 'error' in resp_json


@patch('states.queries_states.update')
def test_update_state(mock_update):
    """Test PUT /states/<id> endpoint"""
    mock_update.return_value = 1
    update_data = {
        'population': 6000000,
        'governor': 'New Governor'
    }

    resp = TEST_CLIENT.put('/states/test-id', json=update_data)

    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'message' in resp_json


@patch('cities.queries_cities.update')
def test_update_city(mock_update):
    """Test PUT /cities/<id> endpoint"""
    mock_update.return_value = 1
    update_data = {
        'population': '200,000',
        'mayor': 'New Mayor'
    }

    resp = TEST_CLIENT.put('/cities/test-id', json=update_data)

    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'message' in resp_json


@patch('countries.queries_countries.delete')
def test_delete_country(mock_delete):
    """Test DELETE /countries/<id> endpoint"""
    mock_delete.return_value = 1
    resp = TEST_CLIENT.delete('/countries/test-id')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'message' in resp_json
    assert resp_json['message'] == 'Country deleted successfully'


@patch('countries.queries_countries.delete')
def test_delete_country_not_found(mock_delete):
    """Test DELETE /countries/<id> with non-existent ID"""
    mock_delete.side_effect = ValueError('Country not found: test-id')
    resp = TEST_CLIENT.delete('/countries/nonexistent-id')
    assert resp.status_code == NOT_FOUND
    resp_json = resp.get_json()
    assert 'error' in resp_json


@patch('states.queries_states.delete')
def test_delete_state(mock_delete):
    """Test DELETE /states/<id> endpoint"""
    mock_delete.return_value = 1
    resp = TEST_CLIENT.delete('/states/test-id')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'message' in resp_json


@patch('cities.queries_cities.delete')
def test_delete_city(mock_delete):
    """Test DELETE /cities/<id> endpoint"""
    mock_delete.return_value = 1
    resp = TEST_CLIENT.delete('/cities/test-id')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'message' in resp_json


@patch('scores.queries_scores.read')
def test_get_scores(mock_read):
    """Test GET /scores endpoint"""
    mock_read.return_value = [
        {'id': 'a', 'player': 'Alice', 'score': 200,
         'guesses_used': 2, 'entity_type': 'cities'},
        {'id': 'b', 'player': 'anonymous', 'score': 100,
         'guesses_used': 5, 'entity_type': 'states'},
    ]

    resp = TEST_CLIENT.get(ep.SCORES_EP)

    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'scores' in resp_json
    assert isinstance(resp_json['scores'], list)
    assert resp_json['scores'][0]['score'] >= resp_json['scores'][1]['score']


@patch('scores.queries_scores.create')
def test_post_score(mock_create):
    """Test POST /scores endpoint"""
    mock_create.return_value = 'new-score-id'
    score_data = {
        'entity_type': 'cities',
        'score': 150,
        'guesses_used': 3,
        'player': 'Bob',
    }

    resp = TEST_CLIENT.post(ep.SCORES_EP, json=score_data)

    assert resp.status_code == CREATED
    resp_json = resp.get_json()
    assert 'id' in resp_json
    assert resp_json['id'] == 'new-score-id'
    assert 'message' in resp_json


@patch('scores.queries_scores.create')
def test_post_score_bad_data(mock_create):
    """Test POST /scores with invalid data"""
    mock_create.side_effect = ValueError('Missing/invalid score')
    resp = TEST_CLIENT.post(ep.SCORES_EP, json={'entity_type': 'cities'})
    assert resp.status_code == BAD_REQUEST
    resp_json = resp.get_json()
    assert 'error' in resp_json


@patch('countries.queries_countries.read')
@patch('states.queries_states.read')
@patch('cities.queries_cities.read')
@patch('prompts.queries_prompts.read')
def test_stats_endpoint(
        mock_prompts, mock_cities, mock_states, mock_countries):
    """Test GET /stats endpoint"""
    mock_countries.return_value = []
    mock_states.return_value = []
    mock_cities.return_value = []
    mock_prompts.return_value = []

    resp = TEST_CLIENT.get('/stats')

    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'countries' in resp_json
    assert 'states' in resp_json
    assert 'cities' in resp_json


def test_health_endpoint():
    """Test GET /health endpoint"""
    resp = TEST_CLIENT.get('/health')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'status' in resp_json
    assert resp_json['status'] == 'ok'


def test_endpoints_list():
    """Test GET /endpoints endpoint"""
    resp = TEST_CLIENT.get('/endpoints')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'Available endpoints' in resp_json
    assert isinstance(resp_json['Available endpoints'], list)
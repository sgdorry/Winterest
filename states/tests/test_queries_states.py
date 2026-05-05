from copy import deepcopy
from unittest.mock import patch
import pytest
from contextlib import contextmanager

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import queries_states as qry

def create_temp_state():
    return deepcopy(qry.SAMPLE_STATE)


@pytest.fixture(scope='function')
def temp_state():
    temp_state = create_temp_state()
    new_state_id = qry.create(create_temp_state())
    yield new_state_id
    try:
        qry.delete(temp_state[qry.NAME], temp_state[qry.STATE_CODE])
    except ValueError:
        print('The record was already deleted.')

       
@pytest.fixture(scope='function')
def temp_state_no_del():
    temp_state = create_temp_state()
    qry.create(create_temp_state())
    return temp_state
      

@pytest.fixture(scope='function')
def temp_state():
    new_rec_id = qry.create(create_temp_state())
    yield new_rec_id
    try:
        qry.delete(new_rec_id)
    except ValueError:
        print('The record was already deleted.')

#reset state_cache before every test
@pytest.fixture(autouse=True)
def reset_cache():
    cache = getattr(qry, "state_cache", None)
    if cache is not None:
        cache.clear()

#checks if number of states has changed according to argument 
@pytest.fixture
def state_delta():
    @contextmanager
    def _state_delta(delta=0):
        old_count = qry.num_states()
        yield
        new_count = qry.num_states()
        assert new_count - old_count == delta
    return _state_delta


def test_num_states(state_delta):
    with state_delta(+1):
        qry.create(create_temp_state()) #adding a new state

  
def test_good_create(state_delta):
    with state_delta(+1):
        temp_state_data = create_temp_state()
        new_rec_id = qry.create(temp_state_data) #new record
        assert qry.is_valid_id(new_rec_id) #checking if the new id created is a valid one
        assert qry.is_valid_population(temp_state_data["population"]) #check if the population entered is valid
        assert qry.is_valid_governor(temp_state_data["governor"]) #check if the governor entered is valid
        assert qry.is_valid_capital(temp_state_data["capital"]) #check if the capital entered is valid
        assert qry.is_valid_code(temp_state_data["state_code"]) #check if the state code entered is valid

   
def test_create_bad_param_type(state_delta):
    with state_delta():
        with pytest.raises(Exception):
            qry.create([1, 2, 3])


@patch('data.db_connect.read')
def test_read(mock_dbc_read, temp_state):
    # mock the dbc.read to return test data
    mock_dbc_read.return_value = [{'id': '1', 'name': 'New York'}, {'id': '2', 'name': 'California'}]

    # test reading all states
    all_states = qry.read()
    assert isinstance(all_states, list)
    assert len(all_states) > 0


@patch('data.db_connect.read')
def test_read_cant_connect(mock_dbc_read):
    # mock dbc.read to raise an error
    from data.db_connect import DBError
    mock_dbc_read.side_effect = DBError("Connection failed")

    with pytest.raises(DBError):
        states = qry.read()


def test_create_bad_name(state_delta):
    with state_delta():
        with pytest.raises(Exception):
            qry.create({'id': '1', 'name': 5, 'population': 19870000, 'capital': 'Albany', 'governor': 'Kathy Hochul'}) #test with an integer as the name

def test_create_bad_population(state_delta):
    with state_delta():
        with pytest.raises(Exception):
            qry.create({'id': '1', 'name': 'New York', 'population': '19870000', 'capital': 'Albany', 'governor': 'Kathy Hochul'}) #test with a string as the population
               

def test_create_bad_capital(state_delta):
    with state_delta():
        with pytest.raises(Exception):
            qry.create({'id': '1', 'name': 'New York', 'population': 19870000, 'capital': 293745, 'governor': 'Kathy Hochul'})

           
def test_create_bad_governor(state_delta):
    with state_delta():
        with pytest.raises(Exception):
            qry.create({'id': '1', 'name': 'New York', 'population': 19870000, 'capital': 'Albany', 'governor': 293745})

            
def test_create_bad_id(state_delta):
    with state_delta():
        with pytest.raises(Exception):
            qry.create({'id': 123, 'name': 'New York', 'population': 19870000, 'capital': 'Albany', 'governor': 'Kathy Hochul'})

          
def test_create_bad_climate(state_delta):
    with state_delta():
        with pytest.raises(Exception):
            qry.create({'id': '1', 'name': 'New York', 'population': 19870000, 'capital': 'Albany', 'governor': 'Kathy Hochul', 'climate': 293745})


def test_create_bad_state_bird(state_delta):
    with state_delta():
        with pytest.raises(Exception):
            qry.create({'id': '1', 'name': 'New York', 'population': 19870000, 'capital': 'Albany', 'governor': 'Kathy Hochul', 'state_bird': 293745})


def test_create_bad_statehood_date(state_delta):
    with state_delta():
        with pytest.raises(Exception):
            qry.create({'id': '1', 'name': 'New York', 'population': 19870000, 'capital': 'Albany', 'governor': 'Kathy Hochul', 'statehood_date': 293745})

        
def test_create_bad_gdp(state_delta):
    with state_delta():
        with pytest.raises(Exception):
            qry.create({'id': '1', 'name': 'New York', 'population': 19870000, 'capital': 'Albany', 'governor': 'Kathy Hochul', 'gdp': 293745})


@pytest.mark.skip
def test_bad_test_for_num_states():
    # test that num_states returns a valid non-negative integer
    count = qry.num_states()
    assert isinstance(count, int) 
    assert count >= 0 


@pytest.mark.skip
def test_delete(temp_state, state_delta):
    assert temp_state in qry.state_cache
    with state_delta(-1): #expecting num_cities to decrease -1
        # delete the state
        qry.delete(temp_state)
    assert temp_state not in qry.state_cache


def test_delete_not_there():
    with pytest.raises(ValueError):
        qry.delete('a state that has not yet been created')

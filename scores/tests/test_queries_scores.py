from unittest.mock import patch
import pytest

import scores.queries_scores as sq


@patch('data.db_connect.read', return_value=[])
@patch('data.db_connect.create')
def test_create_valid_score(mock_db_create, mock_db_read):
    sq.score_cache.clear()
    sid = sq.create({
        'score': 100,
        'guesses_used': 3,
        'entity_type': 'cities',
        'player': 'Alice',
    })
    assert isinstance(sid, str)
    assert len(sid) > 0
    mock_db_create.assert_called_once()
    doc = mock_db_create.call_args[0][1]
    assert doc['player'] == 'Alice'
    assert doc['score'] == 100
    assert doc['guesses_used'] == 3
    assert doc['entity_type'] == 'cities'
    assert 'timestamp' in doc


@patch('data.db_connect.read', return_value=[])
@patch('data.db_connect.create')
def test_create_anonymous_when_no_player(mock_db_create, mock_db_read):
    sq.score_cache.clear()
    sid = sq.create({
        'score': 50,
        'guesses_used': 5,
        'entity_type': 'states',
    })
    doc = mock_db_create.call_args[0][1]
    assert doc['player'] == 'anonymous'


@patch('data.db_connect.read', return_value=[])
def test_create_missing_score_raises(mock_db_read):
    sq.score_cache.clear()
    with pytest.raises(ValueError, match="Missing/invalid score"):
        sq.create({'guesses_used': 3, 'entity_type': 'cities'})


@patch('data.db_connect.read', return_value=[])
def test_create_missing_guesses_used_raises(mock_db_read):
    sq.score_cache.clear()
    with pytest.raises(ValueError, match="Missing/invalid guesses_used"):
        sq.create({'score': 10, 'entity_type': 'cities'})


@patch('data.db_connect.read', return_value=[])
def test_create_missing_entity_type_raises(mock_db_read):
    sq.score_cache.clear()
    with pytest.raises(ValueError, match="Missing/invalid entity_type"):
        sq.create({'score': 10, 'guesses_used': 3})


@patch('data.db_connect.read', return_value=[])
def test_create_invalid_entity_type_raises(mock_db_read):
    sq.score_cache.clear()
    with pytest.raises(ValueError, match="entity_type must be one of"):
        sq.create({
            'score': 10,
            'guesses_used': 3,
            'entity_type': 'planets',
        })


@patch('data.db_connect.read', return_value=[])
def test_create_non_dict_raises(mock_db_read):
    sq.score_cache.clear()
    with pytest.raises(ValueError, match="fields must be a dict"):
        sq.create("not a dict")


@patch('data.db_connect.read', return_value=[])
def test_read_returns_sorted_by_score_desc(mock_db_read):
    sq.score_cache.clear()
    sq.score_cache['a'] = {'id': 'a', 'score': 50}
    sq.score_cache['b'] = {'id': 'b', 'score': 200}
    sq.score_cache['c'] = {'id': 'c', 'score': 100}

    result = sq.read()
    scores = [d['score'] for d in result]
    assert scores == [200, 100, 50]

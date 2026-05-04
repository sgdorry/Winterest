from unittest.mock import patch

import pytest

import prompts.queries_prompts as pq


def _reset_cache():
    pq.prompt_cache.clear()


def _seed(docs):
    pq.prompt_cache.clear()
    for doc in docs:
        pq.prompt_cache[doc[pq.ID]] = doc


def _make_prompt(pid='p1', ptype='country',
                 entity_type='country', entity_id='c1',
                 answer='Canada', approved=True,
                 asset_url='', asset_text='Outline of country'):
    return {
        pq.ID: pid,
        pq.TYPE: ptype,
        pq.ENTITY_TYPE: entity_type,
        pq.ENTITY_ID: entity_id,
        pq.ANSWER: answer,
        pq.APPROVED: approved,
        pq.ASSET_URL: asset_url,
        pq.ASSET_TEXT: asset_text,
    }


@patch('data.db_connect.create')
@patch('data.db_connect.read', return_value=[])
def test_create_with_asset_url(mock_db_read, mock_db_create):
    _reset_cache()
    pid = pq.create({
        pq.TYPE: 'country',
        pq.ENTITY_TYPE: 'country',
        pq.ENTITY_ID: 'c1',
        pq.ANSWER: 'Canada',
        pq.ASSET_URL: 'https://example.com/canada.png',
    })
    assert isinstance(pid, str) and len(pid) > 0
    mock_db_create.assert_called_once()
    stored = mock_db_create.call_args[0][1]
    assert stored[pq.ASSET_URL] == 'https://example.com/canada.png'
    assert stored[pq.APPROVED] is True
    assert pid in pq.prompt_cache


@patch('data.db_connect.create')
@patch('data.db_connect.read', return_value=[])
def test_create_with_asset_text(mock_db_read, mock_db_create):
    _reset_cache()
    pid = pq.create({
        pq.TYPE: 'country',
        pq.ENTITY_TYPE: 'country',
        pq.ENTITY_ID: 'c1',
        pq.ANSWER: 'Canada',
        pq.ASSET_TEXT: 'Northern country',
    })
    stored = mock_db_create.call_args[0][1]
    assert stored[pq.ASSET_TEXT] == 'Northern country'
    assert stored[pq.ASSET_URL] == ''
    assert pid in pq.prompt_cache


@patch('data.db_connect.read', return_value=[])
def test_create_non_dict_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match="fields must be a dict"):
        pq.create("not-a-dict")


@patch('data.db_connect.read', return_value=[])
def test_create_missing_type_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match=f"Missing/invalid {pq.TYPE}"):
        pq.create({
            pq.ENTITY_TYPE: 'country',
            pq.ENTITY_ID: 'c1',
            pq.ANSWER: 'Canada',
            pq.ASSET_URL: 'https://example.com/canada.png',
        })


@patch('data.db_connect.read', return_value=[])
def test_create_missing_entity_type_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match=f"Missing/invalid {pq.ENTITY_TYPE}"):
        pq.create({
            pq.TYPE: 'country',
            pq.ENTITY_ID: 'c1',
            pq.ANSWER: 'Canada',
            pq.ASSET_URL: 'https://example.com/canada.png',
        })


@patch('data.db_connect.read', return_value=[])
def test_create_missing_entity_id_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match=f"Missing/invalid {pq.ENTITY_ID}"):
        pq.create({
            pq.TYPE: 'country',
            pq.ENTITY_TYPE: 'country',
            pq.ANSWER: 'Canada',
            pq.ASSET_URL: 'https://example.com/canada.png',
        })


@patch('data.db_connect.read', return_value=[])
def test_create_missing_answer_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match=f"Missing/invalid {pq.ANSWER}"):
        pq.create({
            pq.TYPE: 'country',
            pq.ENTITY_TYPE: 'country',
            pq.ENTITY_ID: 'c1',
            pq.ASSET_URL: 'https://example.com/canada.png',
        })


@patch('data.db_connect.read', return_value=[])
def test_create_missing_both_assets_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match="asset_url or asset_text"):
        pq.create({
            pq.TYPE: 'country',
            pq.ENTITY_TYPE: 'country',
            pq.ENTITY_ID: 'c1',
            pq.ANSWER: 'Canada',
        })


@patch('data.db_connect.create')
@patch('data.db_connect.read', return_value=[])
def test_create_approved_defaults_true(mock_db_read, mock_db_create):
    _reset_cache()
    pq.create({
        pq.TYPE: 'country',
        pq.ENTITY_TYPE: 'country',
        pq.ENTITY_ID: 'c1',
        pq.ANSWER: 'Canada',
        pq.ASSET_URL: 'https://example.com/canada.png',
    })
    stored = mock_db_create.call_args[0][1]
    assert stored[pq.APPROVED] is True


@patch('data.db_connect.create')
@patch('data.db_connect.read', return_value=[])
def test_create_approved_can_be_false(mock_db_read, mock_db_create):
    _reset_cache()
    pq.create({
        pq.TYPE: 'country',
        pq.ENTITY_TYPE: 'country',
        pq.ENTITY_ID: 'c1',
        pq.ANSWER: 'Canada',
        pq.ASSET_URL: 'https://example.com/canada.png',
        pq.APPROVED: False,
    })
    stored = mock_db_create.call_args[0][1]
    assert stored[pq.APPROVED] is False


def test_read_returns_all():
    _seed([
        _make_prompt(pid='a', ptype='country'),
        _make_prompt(pid='b', ptype='state'),
        _make_prompt(pid='c', ptype='country'),
    ])
    docs = pq.read()
    assert len(docs) == 3


def test_read_filters_by_type():
    _seed([
        _make_prompt(pid='a', ptype='country'),
        _make_prompt(pid='b', ptype='state'),
        _make_prompt(pid='c', ptype='country'),
    ])
    docs = pq.read(prompt_type='country')
    assert len(docs) == 2
    assert all(d[pq.TYPE] == 'country' for d in docs)


def test_read_unknown_type_returns_empty():
    _seed([_make_prompt(pid='a', ptype='country')])
    assert pq.read(prompt_type='no-such-type') == []


def test_random_questions_missing_type_raises():
    _seed([_make_prompt()])
    with pytest.raises(ValueError, match="type is required"):
        pq.random_questions('', count=5)


def test_random_questions_filters_unapproved():
    _seed([
        _make_prompt(pid='a', ptype='country', approved=True),
        _make_prompt(pid='b', ptype='country', approved=False),
        _make_prompt(pid='c', ptype='country', approved=True),
    ])
    result = pq.random_questions('country', count=10)
    assert len(result) == 2
    assert all(d[pq.APPROVED] is True for d in result)


def test_random_questions_empty_pool_returns_empty():
    _seed([_make_prompt(pid='a', ptype='state')])
    assert pq.random_questions('country', count=3) == []


def test_random_questions_caps_count_at_pool_size():
    _seed([
        _make_prompt(pid='a', ptype='country', approved=True),
        _make_prompt(pid='b', ptype='country', approved=True),
    ])
    result = pq.random_questions('country', count=99)
    assert len(result) == 2


def test_random_questions_respects_exact_count():
    _seed([
        _make_prompt(pid=str(i), ptype='country', approved=True)
        for i in range(10)
    ])
    result = pq.random_questions('country', count=3)
    assert len(result) == 3


def test_random_questions_invalid_count_falls_back_to_default():
    _seed([
        _make_prompt(pid=str(i), ptype='country', approved=True)
        for i in range(7)
    ])
    result = pq.random_questions('country', count=0)
    assert len(result) == 5


def test_random_questions_negative_count_falls_back_to_default():
    _seed([
        _make_prompt(pid=str(i), ptype='country', approved=True)
        for i in range(7)
    ])
    result = pq.random_questions('country', count=-3)
    assert len(result) == 5

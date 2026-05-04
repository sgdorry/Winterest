from unittest.mock import patch

import pytest

import friends.queries_friends as fq


def _reset_cache():
    fq.friend_cache.clear()


def _seed(docs):
    fq.friend_cache.clear()
    for doc in docs:
        fq.friend_cache[doc[fq.ID]] = doc


def _make_doc(fid, user_id, friend_id):
    return {fq.ID: fid, fq.USER_ID: user_id, fq.FRIEND_ID: friend_id}


@patch('data.db_connect.create')
@patch('data.db_connect.read', return_value=[])
def test_create_creates_two_reciprocal_docs(mock_db_read, mock_db_create):
    _reset_cache()
    fq.create('u1', 'u2')
    assert mock_db_create.call_count == 2
    cached_pairs = {
        (doc[fq.USER_ID], doc[fq.FRIEND_ID])
        for doc in fq.friend_cache.values()
    }
    assert ('u1', 'u2') in cached_pairs
    assert ('u2', 'u1') in cached_pairs


@patch('data.db_connect.read', return_value=[])
def test_create_missing_user_id_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match="user_id and friend_id are required"):
        fq.create('', 'u2')


@patch('data.db_connect.read', return_value=[])
def test_create_missing_friend_id_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match="user_id and friend_id are required"):
        fq.create('u1', '')


@patch('data.db_connect.read', return_value=[])
def test_create_self_friend_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match="Cannot add yourself"):
        fq.create('u1', 'u1')


@patch('data.db_connect.create')
@patch('data.db_connect.read', return_value=[])
def test_create_duplicate_raises(mock_db_read, mock_db_create):
    _seed([_make_doc('a', 'u1', 'u2')])
    with pytest.raises(ValueError, match="Already friends"):
        fq.create('u1', 'u2')
    mock_db_create.assert_not_called()


def test_read_returns_friend_ids():
    _seed([
        _make_doc('a', 'u1', 'u2'),
        _make_doc('b', 'u2', 'u1'),
        _make_doc('c', 'u1', 'u3'),
        _make_doc('d', 'u3', 'u1'),
    ])
    result = fq.read('u1')
    assert sorted(result) == ['u2', 'u3']


def test_read_empty_user_id_returns_empty_list():
    _seed([_make_doc('a', 'u1', 'u2')])
    assert fq.read('') == []
    assert fq.read(None) == []


def test_read_user_with_no_friends_returns_empty_list():
    _seed([_make_doc('a', 'u1', 'u2')])
    assert fq.read('u9') == []


@patch('data.db_connect.delete')
def test_delete_removes_both_reciprocal_docs(mock_db_delete):
    _seed([
        _make_doc('a', 'u1', 'u2'),
        _make_doc('b', 'u2', 'u1'),
        _make_doc('c', 'u1', 'u3'),
        _make_doc('d', 'u3', 'u1'),
    ])
    fq.delete('u1', 'u2')
    remaining_pairs = {
        (doc[fq.USER_ID], doc[fq.FRIEND_ID])
        for doc in fq.friend_cache.values()
    }
    assert ('u1', 'u2') not in remaining_pairs
    assert ('u2', 'u1') not in remaining_pairs
    assert ('u1', 'u3') in remaining_pairs
    assert ('u3', 'u1') in remaining_pairs
    assert mock_db_delete.call_count == 2


@patch('data.db_connect.delete')
def test_delete_missing_user_id_raises(mock_db_delete):
    _seed([_make_doc('a', 'u1', 'u2')])
    with pytest.raises(ValueError, match="user_id and friend_id are required"):
        fq.delete('', 'u2')
    mock_db_delete.assert_not_called()


@patch('data.db_connect.delete')
def test_delete_missing_friend_id_raises(mock_db_delete):
    _seed([_make_doc('a', 'u1', 'u2')])
    with pytest.raises(ValueError, match="user_id and friend_id are required"):
        fq.delete('u1', '')
    mock_db_delete.assert_not_called()


@patch('data.db_connect.delete')
def test_delete_nonexistent_friendship_is_noop(mock_db_delete):
    _seed([_make_doc('a', 'u1', 'u2')])
    fq.delete('u9', 'u8')
    assert len(fq.friend_cache) == 1
    mock_db_delete.assert_not_called()

from unittest.mock import patch

import pytest

import users.queries_users as qu


def _reset_cache():
    qu.user_cache.clear()


def _seed(users):
    qu.user_cache.clear()
    for user in users:
        qu.user_cache[user[qu.ID]] = user


def _make_user(uid="u1", email="alice@example.com", username="alice",
               password="hashed", friends=None, score=0, games=0):
    return {
        qu.ID: uid,
        qu.EMAIL: email,
        qu.USERNAME: username,
        qu.PASSWORD: password,
        qu.FRIENDS: list(friends) if friends else [],
        qu.SCORE: score,
        qu.GAMES_PLAYED: games,
    }


@patch('users.queries_users._hash_password', return_value='hashed-pw')
@patch('data.db_connect.create')
@patch('data.db_connect.read', return_value=[])
def test_create_happy_path(mock_db_read, mock_db_create, mock_hash):
    _reset_cache()
    uid = qu.create({
        qu.EMAIL: 'Player@Example.COM',
        qu.USERNAME: 'Player_One',
        qu.PASSWORD: 'goodpassword',
    })
    assert isinstance(uid, str)
    assert len(uid) > 0
    mock_db_create.assert_called_once()
    stored = mock_db_create.call_args[0][1]
    assert stored[qu.EMAIL] == 'player@example.com'
    assert stored[qu.USERNAME] == 'player_one'
    assert stored[qu.PASSWORD] == 'hashed-pw'
    assert stored[qu.FRIENDS] == []
    assert stored[qu.SCORE] == 0
    assert stored[qu.GAMES_PLAYED] == 0
    assert uid in qu.user_cache


@patch('data.db_connect.read', return_value=[])
def test_create_non_dict_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match="fields must be a dict"):
        qu.create("not-a-dict")


@patch('data.db_connect.read', return_value=[])
def test_create_missing_email_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match=f"Missing/invalid {qu.EMAIL}"):
        qu.create({
            qu.USERNAME: 'player_one',
            qu.PASSWORD: 'goodpassword',
        })


@patch('data.db_connect.read', return_value=[])
def test_create_missing_username_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match=f"Missing/invalid {qu.USERNAME}"):
        qu.create({
            qu.EMAIL: 'player@example.com',
            qu.PASSWORD: 'goodpassword',
        })


@patch('data.db_connect.read', return_value=[])
def test_create_missing_password_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match=f"Missing/invalid {qu.PASSWORD}"):
        qu.create({
            qu.EMAIL: 'player@example.com',
            qu.USERNAME: 'player_one',
        })


@patch('data.db_connect.read', return_value=[])
def test_create_invalid_username_pattern_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match="letters, numbers, and underscores"):
        qu.create({
            qu.EMAIL: 'player@example.com',
            qu.USERNAME: 'bad name!',
            qu.PASSWORD: 'goodpassword',
        })


@patch('data.db_connect.read', return_value=[])
def test_create_short_password_raises(mock_db_read):
    _reset_cache()
    with pytest.raises(ValueError, match="Password must be at least"):
        qu.create({
            qu.EMAIL: 'player@example.com',
            qu.USERNAME: 'player_one',
            qu.PASSWORD: 'abc',
        })


@patch('users.queries_users._hash_password', return_value='hashed-pw')
@patch('data.db_connect.create')
@patch('data.db_connect.read', return_value=[])
def test_create_duplicate_email_raises(mock_db_read, mock_db_create,
                                       mock_hash):
    _seed([_make_user(email='taken@example.com', username='someone')])
    with pytest.raises(ValueError, match="User already exists"):
        qu.create({
            qu.EMAIL: 'taken@example.com',
            qu.USERNAME: 'fresh_name',
            qu.PASSWORD: 'goodpassword',
        })


@patch('users.queries_users._hash_password', return_value='hashed-pw')
@patch('data.db_connect.create')
@patch('data.db_connect.read', return_value=[])
def test_create_duplicate_username_raises(mock_db_read, mock_db_create,
                                          mock_hash):
    _seed([_make_user(email='someone@example.com', username='taken_name')])
    with pytest.raises(ValueError, match="Username already exists"):
        qu.create({
            qu.EMAIL: 'fresh@example.com',
            qu.USERNAME: 'taken_name',
            qu.PASSWORD: 'goodpassword',
        })


def test_find_by_email_hit():
    _seed([_make_user(uid='u1', email='alice@example.com')])
    user = qu.find_by_email('Alice@Example.com')
    assert user is not None
    assert user[qu.ID] == 'u1'


def test_find_by_email_miss():
    _seed([_make_user(uid='u1', email='alice@example.com')])
    assert qu.find_by_email('absent@example.com') is None


def test_find_by_email_invalid_input():
    _seed([_make_user(uid='u1', email='alice@example.com')])
    assert qu.find_by_email('') is None
    assert qu.find_by_email(None) is None
    assert qu.find_by_email(123) is None


def test_find_by_username_hit():
    _seed([_make_user(uid='u1', username='alice')])
    user = qu.find_by_username('Alice')
    assert user is not None
    assert user[qu.ID] == 'u1'


def test_find_by_username_miss():
    _seed([_make_user(uid='u1', username='alice')])
    assert qu.find_by_username('bob') is None


def test_find_by_username_invalid_input():
    _seed([_make_user(uid='u1', username='alice')])
    assert qu.find_by_username('') is None
    assert qu.find_by_username(None) is None
    assert qu.find_by_username(123) is None


@patch('users.queries_users.pw.check_password', return_value=True)
def test_verify_correct_password(mock_check):
    _seed([_make_user(uid='u1', email='alice@example.com',
                      password='hashed')])
    user = qu.verify('alice@example.com', 'plain-text')
    assert user is not None
    assert user[qu.ID] == 'u1'
    mock_check.assert_called_once_with('hashed', 'plain-text')


@patch('users.queries_users.pw.check_password', return_value=False)
def test_verify_wrong_password(mock_check):
    _seed([_make_user(uid='u1', email='alice@example.com',
                      password='hashed')])
    assert qu.verify('alice@example.com', 'wrong') is None


def test_verify_unknown_user():
    _seed([_make_user(uid='u1', email='alice@example.com')])
    assert qu.verify('nobody@example.com', 'whatever') is None


def test_verify_empty_inputs():
    _seed([_make_user(uid='u1', email='alice@example.com')])
    assert qu.verify('', 'pw') is None
    assert qu.verify('alice@example.com', '') is None
    assert qu.verify(None, 'pw') is None
    assert qu.verify('alice@example.com', None) is None


@patch('users.queries_users.pw.check_password', return_value=True)
def test_verify_falls_back_to_username(mock_check):
    _seed([_make_user(uid='u1', email='alice@example.com',
                      username='alice', password='hashed')])
    user = qu.verify('alice', 'plain-text')
    assert user is not None
    assert user[qu.ID] == 'u1'


@patch('data.db_connect.update')
def test_update_username_happy_path(mock_db_update):
    _seed([_make_user(uid='u1', username='oldname')])
    user = qu.update_username('u1', 'NewName')
    assert user[qu.USERNAME] == 'newname'
    mock_db_update.assert_called_once()


@patch('data.db_connect.update')
def test_update_username_unknown_user(mock_db_update):
    _seed([_make_user(uid='u1', username='oldname')])
    with pytest.raises(ValueError, match="User not found"):
        qu.update_username('does-not-exist', 'newname')


@patch('data.db_connect.update')
def test_update_username_duplicate(mock_db_update):
    _seed([
        _make_user(uid='u1', username='alice'),
        _make_user(uid='u2', email='bob@example.com', username='bob'),
    ])
    with pytest.raises(ValueError, match="Username already exists"):
        qu.update_username('u1', 'bob')


@patch('data.db_connect.update')
def test_update_username_invalid_pattern(mock_db_update):
    _seed([_make_user(uid='u1', username='alice')])
    with pytest.raises(ValueError, match="letters, numbers, and underscores"):
        qu.update_username('u1', 'bad name!')


@patch('data.db_connect.update')
def test_update_username_same_value_is_noop(mock_db_update):
    _seed([_make_user(uid='u1', username='alice')])
    user = qu.update_username('u1', 'alice')
    assert user[qu.USERNAME] == 'alice'
    mock_db_update.assert_not_called()


@patch('data.db_connect.update')
def test_update_username_missing_args(mock_db_update):
    _seed([_make_user(uid='u1', username='alice')])
    with pytest.raises(ValueError, match="user_id is required"):
        qu.update_username('', 'whatever')
    with pytest.raises(ValueError, match="username is required"):
        qu.update_username('u1', '')


@patch('data.db_connect.update')
def test_update_score_increments(mock_db_update):
    _seed([_make_user(uid='u1', score=10, games=2)])
    result = qu.update_score('u1', 50, games_delta=1)
    assert result[qu.SCORE] == 60
    assert result[qu.GAMES_PLAYED] == 3
    mock_db_update.assert_called_once()


@patch('data.db_connect.update')
def test_update_score_unknown_user(mock_db_update):
    _seed([_make_user(uid='u1')])
    with pytest.raises(ValueError, match="User not found"):
        qu.update_score('does-not-exist', 5)


@patch('data.db_connect.update')
def test_update_score_non_int_raises(mock_db_update):
    _seed([_make_user(uid='u1')])
    with pytest.raises(ValueError, match="score_delta must be an int"):
        qu.update_score('u1', 'oops')
    with pytest.raises(ValueError, match="games_delta must be an int"):
        qu.update_score('u1', 5, games_delta='oops')


@patch('data.db_connect.update')
def test_update_score_missing_user_id(mock_db_update):
    _seed([_make_user(uid='u1')])
    with pytest.raises(ValueError, match="user_id is required"):
        qu.update_score('', 5)


def test_get_leaderboard_sorted_desc_and_limit():
    _seed([
        _make_user(uid='a', email='a@example.com', username='a', score=50),
        _make_user(uid='b', email='b@example.com', username='b', score=200),
        _make_user(uid='c', email='c@example.com', username='c', score=100),
    ])
    top_two = qu.get_leaderboard(limit=2)
    assert [u[qu.SCORE] for u in top_two] == [200, 100]


def test_get_leaderboard_invalid_limit():
    _seed([_make_user()])
    with pytest.raises(ValueError, match="limit must be a positive int"):
        qu.get_leaderboard(limit=0)
    with pytest.raises(ValueError, match="limit must be a positive int"):
        qu.get_leaderboard(limit=-1)
    with pytest.raises(ValueError, match="limit must be a positive int"):
        qu.get_leaderboard(limit='ten')


@patch('data.db_connect.update')
def test_add_friend_bidirectional(mock_db_update):
    _seed([
        _make_user(uid='u1', email='u1@example.com', username='u1'),
        _make_user(uid='u2', email='u2@example.com', username='u2'),
    ])
    result = qu.add_friend('u1', 'u2')
    assert 'u2' in result
    assert 'u2' in qu.user_cache['u1'][qu.FRIENDS]
    assert 'u1' in qu.user_cache['u2'][qu.FRIENDS]
    assert mock_db_update.call_count == 2


@patch('data.db_connect.update')
def test_add_friend_self_raises(mock_db_update):
    _seed([_make_user(uid='u1')])
    with pytest.raises(ValueError, match="Cannot add yourself"):
        qu.add_friend('u1', 'u1')


@patch('data.db_connect.update')
def test_add_friend_unknown_user_raises(mock_db_update):
    _seed([_make_user(uid='u1')])
    with pytest.raises(ValueError, match="User not found"):
        qu.add_friend('u1', 'nope')


@patch('data.db_connect.update')
def test_add_friend_missing_args_raises(mock_db_update):
    _seed([_make_user(uid='u1')])
    with pytest.raises(ValueError, match="required"):
        qu.add_friend('', 'u2')
    with pytest.raises(ValueError, match="required"):
        qu.add_friend('u1', '')


@patch('data.db_connect.update')
def test_add_friend_idempotent(mock_db_update):
    u1 = _make_user(uid='u1', email='u1@example.com', username='u1',
                    friends=['u2'])
    u2 = _make_user(uid='u2', email='u2@example.com', username='u2',
                    friends=['u1'])
    _seed([u1, u2])
    result = qu.add_friend('u1', 'u2')
    assert result.count('u2') == 1
    assert qu.user_cache['u1'][qu.FRIENDS].count('u2') == 1
    assert qu.user_cache['u2'][qu.FRIENDS].count('u1') == 1


def test_read_returns_all_users():
    _seed([
        _make_user(uid='u1', email='u1@example.com', username='u1'),
        _make_user(uid='u2', email='u2@example.com', username='u2'),
    ])
    users = qu.read()
    ids = sorted(u[qu.ID] for u in users)
    assert ids == ['u1', 'u2']

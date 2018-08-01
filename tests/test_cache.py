import tempfile
from eeweather.cache import KeyValueStore
from datetime import datetime
import pytz

import pytest


@pytest.fixture
def s():
    return KeyValueStore('sqlite:///{}/cache.db'.format(tempfile.mkdtemp()))


def test_key_value_store(s):
    # key 'a' does not exist yet
    assert s.key_exists('a') is False
    assert s.retrieve_json('a') is None
    assert s.key_updated('a') is None

    # create key 'a'
    s.save_json('a', {'b': [1, 'two', 3.0]})
    assert s.key_exists('a') is True
    data = s.retrieve_json('a')
    assert len(data['b']) == 3
    assert data['b'][0] == 1
    assert data['b'][1] == 'two'
    assert data['b'][2] == 3.0
    dt1 = s.key_updated('a')
    assert dt1.date() == datetime.utcnow().date()

    # update key 'a'
    s.save_json('a', ['updated'])
    data = s.retrieve_json('a')
    assert data[0] == 'updated'

    # clear key 'a' (and everything)
    s.clear()
    assert s.key_exists('a') is False


def test_key_value_store_repr(s):
    assert repr(s) == 'KeyValueStore("{}")'.format(s.url)


def test_key_value_store_clear_single_key(s):
    # clear single key
    s.save_json('a', 'b')
    s.save_json('b', 'c')
    assert s.key_exists('a') is True
    assert s.key_exists('b') is True
    s.clear('b')
    assert s.key_exists('a') is True
    assert s.key_exists('b') is False


def test_get_datetime_if_exists(s):
    data = None
    result = s._get_datetime_if_exists(data)
    assert result == None

    data = [datetime(2018,1,1)]
    result = s._get_datetime_if_exists(data)
    assert result == pytz.utc.localize(datetime(2018,1,1))

    data = [pytz.utc.localize(datetime(2018,1,1))]
    result = s._get_datetime_if_exists(data)
    assert result == pytz.utc.localize(datetime(2018,1,1))

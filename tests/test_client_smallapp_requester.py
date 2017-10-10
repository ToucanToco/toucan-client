import pytest

from toucanclient.client import SmallAppRequester

BASE_ROUTE = 'fake.route/my-small-app'
BASE_ROUTE_2 = 'fake.route/my-small-app/'


@pytest.fixture(name='small_app', scope='module')
def gen_small_app():
    return SmallAppRequester(BASE_ROUTE)


def test_simple_get(small_app):
    """It should build the right URL"""
    _ = small_app.config.etl.get
    assert small_app.method == 'get'
    assert small_app.route == '{}/config/etl'.format(BASE_ROUTE)


def test_simple_get_with_baseroute_2():
    small_app = SmallAppRequester(BASE_ROUTE_2)
    _ = small_app.config.etl.get
    assert small_app.method == 'get'
    assert small_app.route == '{}/config/etl'.format(BASE_ROUTE)


def test_simple_get_with_stage(small_app):
    """It should build the right URL (with staging stage)"""
    small_app.stage = 'staging'
    _ = small_app.config.etl.get
    assert small_app.method == 'get'
    assert small_app.route == '{}/config/etl?stage=staging'.format(BASE_ROUTE)


def test_kwargs(small_app):
    """It should add kwargs"""
    small_app.best_character = 'Ryu'
    _ = small_app.config.etl.get
    assert small_app.kwargs == {'best_character': 'Ryu'}


def test_dfs(small_app, mocker):
    """It should use the cache properly"""
    mock_exists = mocker.patch('os.path.exists')
    mock_get = mocker.patch('requests.get')
    mock_read_cache = mocker.patch(
        'toucanclient.client.SmallAppRequester.read_cache')
    mock_cache_dfs = mocker.patch(
        'toucanclient.client.SmallAppRequester.cache_dfs')
    # 1. Cache directory exists
    mock_exists.return_value = True
    mock_get.side_effect = RuntimeError('test')
    mock_read_cache.return_value = 1

    dfs = small_app.dfs
    assert dfs == 1

    # 2. No cache
    mock_exists.return_value = False
    mock_get.return_value = 1
    mock_read_cache.side_effect = RuntimeError('test')
    mock_cache_dfs.return_value = 1

    dfs = small_app.dfs
    assert dfs == 1

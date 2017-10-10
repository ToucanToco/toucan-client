import pytest

from toucanclient.client import SmallAppRequester

base_route = 'fake.route/my-small-app'


@pytest.fixture(scope='module')
def small_app():
    return SmallAppRequester(base_route)


def test_simple_get(small_app):
    """It should build the right URL"""
    _ = small_app.config.etl.get
    assert small_app.method == 'get'
    assert small_app.route == '{}/config/etl'.format(base_route)


def test_simple_get_with_stage(small_app):
    """It should build the right URL (with staging stage)"""
    small_app.stage = 'staging'
    _ = small_app.config.etl.get
    assert small_app.method == 'get'
    assert small_app.route == '{}/config/etl?stage=staging'.format(base_route)


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


def test_cache_dfs():
    pass

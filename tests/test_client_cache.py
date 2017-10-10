import copy
import shutil
from collections import namedtuple

import pandas as pd
import pytest

from tests.utils import default_zip_file
from toucan_client.client import SmallAppRequester

DF = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
DF2 = pd.DataFrame({'a': ['a', 'b'], 'b': ['c', 'd']})
ZIP_CONTENT = default_zip_file(DF, DF2)
BASE_ROUTE = 'fake.route/my-small-app'


@pytest.fixture(name='small_app')
def gen_small_app():
    small_app = SmallAppRequester(BASE_ROUTE)
    yield small_app
    shutil.rmtree(small_app.EXTRACTION_CACHE_PATH)


def test_cache(small_app, mocker):
    Response = namedtuple('MockResponse', ['content'])
    mock_get = mocker.patch('requests.get')
    mock_get.return_value = Response(content=copy.copy(ZIP_CONTENT))

    # Cache is empty -> fill it
    dfs = small_app.dfs
    mock_get.assert_called_once()
    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])

    # Cache is filled, no request to the server should been made
    mock_get.reset_mock()
    new_small_app = SmallAppRequester(BASE_ROUTE)
    dfs = new_small_app.dfs
    mock_get.assert_not_called()

    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])


def test_invalidate_cache(mocker):
    small_app = SmallAppRequester(BASE_ROUTE)

    Response = namedtuple('MockResponse', ['content'])
    mock_get = mocker.patch('requests.get')
    mock_get.return_value = Response(content=copy.copy(ZIP_CONTENT))
    mock_cache = mocker.patch(
        'toucan_client.client.SmallAppRequester.cache_dfs')

    # Cache is empty -> fill it
    _ = small_app.dfs
    mock_cache.assert_called_once()
    mock_cache.reset_mock()

    # Cache is already filled
    _ = small_app.dfs
    mock_cache.assert_not_called()

    small_app.invalidate_cache()

    # Cache has been invalidated
    _ = small_app.dfs
    mock_cache.assert_called_once()

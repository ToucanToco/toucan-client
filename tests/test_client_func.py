import copy
import shutil
from collections import namedtuple

import pandas as pd
import pytest

from tests.utils import default_zip_file
from toucanclient.client import SmallAppRequester

DF = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
DF2 = pd.DataFrame({'a': ['a', 'b'], 'b': ['c', 'd']})
ZIP_CONTENT = default_zip_file(DF, DF2)


@pytest.fixture
def small_app():
    base_route = 'fake.route/my-small-app'
    small_app = SmallAppRequester(base_route)
    yield (small_app, small_app)
    shutil.rmtree(small_app.EXTRACTION_CACHE_PATH)


def test_cache(small_app, mocker):
    Response = namedtuple('MockResponse', ['content'])
    mock_get = mocker.patch('requests.get')
    mock_get.return_value = Response(content=copy.copy(ZIP_CONTENT))

    # Cache is empty -> fill it
    small_app_1 = small_app[0]
    dfs = small_app_1.dfs
    mock_get.assert_called_once()
    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])

    # Cache is filled, no request to the server should been made
    mock_get.reset_mock()
    small_app_2 = small_app[1]
    dfs = small_app_2.dfs
    mock_get.assert_not_called()

    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])

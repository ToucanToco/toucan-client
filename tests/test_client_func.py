import copy
import tempfile
from collections import namedtuple
from unittest import TestCase
from unittest.mock import patch

import pandas as pd

from sdk.client import SmallAppRequester
from tests.utils import default_zip_file


class TestSmallAppRequesterCache(TestCase):

    ZIP_CONTENT = None
    DF = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    DF2 = pd.DataFrame({'a': ['a', 'b'], 'b': ['c', 'd']})

    @classmethod
    def setUpClass(cls):
        cls.ZIP_CONTENT = default_zip_file(cls.DF, cls.DF2)

    def setUp(self):
        self.zip = copy.copy(self.ZIP_CONTENT)
        self.base_route = 'fake.route/my-small-app'
        self.small_app = SmallAppRequester(self.base_route)
        self.df = self.DF.copy()
        self.df2 = self.DF2.copy()

    @patch('requests.get')
    def test_cache(self, mock_get):
        with tempfile.TemporaryDirectory() as temp:
            Response = namedtuple('MockResponse', ['content'])
            mock_get.return_value = Response(content=self.zip)
            self.small_app.EXTRACTION_CACHE_PATH = temp

            # Cache is empty -> fill it
            dfs = self.small_app.dfs

            self.assertTrue(isinstance(dfs, dict))
            self.assertIn('df', dfs)
            self.assertIn('df2', dfs)

            self.assertTrue(self.df.equals(dfs['df']))
            self.assertTrue(self.df2.equals(dfs['df2']))

            # Cache is filled, no request to the server should been made
            mock_get.side_effect = RuntimeError('test')
            dfs = self.small_app.dfs

            self.assertTrue(isinstance(dfs, dict))
            self.assertIn('df', dfs)
            self.assertIn('df2', dfs)

            self.assertTrue(self.df.equals(dfs['df']))
            self.assertTrue(self.df2.equals(dfs['df2']))

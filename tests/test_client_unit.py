import copy
from collections import namedtuple
import io
import tempfile
from unittest import TestCase
from unittest.mock import patch
import zipfile

import pandas as pd

from sdk.client import SmallAppRequester


class TestSmallAppRequester(TestCase):

    def setUp(self):
        self.base_route = 'fake.route/my-small-app'
        self.small_app = SmallAppRequester(self.base_route)

    def test_simple_get(self):
        """It should build the right URL"""
        _ = self.small_app.config.etl.get
        method = self.small_app.method
        route = self.small_app.route
        self.assertEqual(method, 'get')
        self.assertEqual(route, f'{self.base_route}/config/etl')

    def test_simple_get_with_stage(self):
        """It should build the right URL (with staging stage)"""
        self.small_app.stage = 'staging'

        _ = self.small_app.config.etl.get
        method = self.small_app.method
        route = self.small_app.route
        self.assertEqual(method, 'get')
        self.assertEqual(route, f'{self.base_route}/config/etl?stage=staging')

    @patch('sdk.client.SmallAppRequester.cache_dfs')
    @patch('sdk.client.SmallAppRequester.read_cache')
    @patch('requests.get')
    @patch('os.path.exists')
    def test_dfs(self, mock_exists, mock_get, mock_read_cache, mock_cache_dfs):
        """It should use the cache properly"""
        # 1. Cache directory exists
        mock_exists.return_value = True
        mock_get.side_effect = RuntimeError('test')
        mock_read_cache.return_value = 1

        dfs = self.small_app.dfs
        self.assertEqual(dfs, 1)

        # 2. No cache
        mock_exists.return_value = False
        mock_get.return_value = 1
        mock_read_cache.side_effect = RuntimeError('test')
        mock_cache_dfs.return_value = 1

        dfs = self.small_app.dfs
        self.assertEqual(dfs, 1)

    def test_cache_dfs(self):
        pass

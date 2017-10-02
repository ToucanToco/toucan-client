from unittest import TestCase
from unittest.mock import patch

from sdk.client import SmallAppRequester


ARGS = 0
KWARGS = 1
ROUTE = 0


class TestSmallAppRequester(TestCase):

    def setUp(self):
        self.base_route = 'fake.route/my-small-app'
        self.small_app = SmallAppRequester(self.base_route)

    def test_simple_get(self):
        _ = self.small_app.config.etl.get
        method = self.small_app.method
        route = self.small_app.route
        self.assertEqual(method, 'get')
        self.assertEqual(route, f'{self.base_route}/config/etl')

    def test_simple_get_with_stage(self):
        self.small_app.stage = 'staging'

        _ = self.small_app.config.etl.get
        method = self.small_app.method
        route = self.small_app.route
        self.assertEqual(method, 'get')
        self.assertEqual(route, f'{self.base_route}/config/etl?stage=staging')

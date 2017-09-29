from unittest import TestCase
from unittest.mock import patch

from sdk.client import SmallAppRequester


ARGS = 0
KWARGS = 1
ROUTE = 0


class TestSmallAppRequester(TestCase):

    def setUp(self):
        self.get_calls = []
        self.post_calls = []
        self.put_calls = []
        self.delete_calls = []

        self.base_url = 'fake.route'
        self.small_app_name = 'my-small-app'
        self.small_app = SmallAppRequester(f'{self.base_url}/{self.small_app_name}')

    def _mock_requests(self, mock_get, mock_post, mock_put, mock_delete):
        def get(*args, **kwargs):
            self.get_calls.append((args, kwargs))
            return 'get'

        def post(*args, **kwargs):
            self.post_calls.append((args, kwargs))
            return 'post'

        def put(*args, **kwargs):
            self.put_calls.append((args, kwargs))
            return 'put'

        def delete(*args, **kwargs):
            self.delete_calls.append((args, kwargs))
            return 'delete'

        mock_get.side_effect = get
        mock_post.side_effect = post
        mock_put.side_effect = put
        mock_delete.side_effect = delete

    @patch('requests.delete')
    @patch('requests.put')
    @patch('requests.post')
    @patch('requests.get')
    def test_simple_get(self, mock_get, mock_post, mock_put, mock_delete):
        self._mock_requests(
            mock_get=mock_get,
            mock_post=mock_post,
            mock_put=mock_put,
            mock_delete=mock_delete
        )

        resp = self.small_app.config.etl.get()
        self.assertEqual(resp, 'get')

        route = self.get_calls[0][ARGS][ROUTE]
        self.assertEqual(route, f'{self.base_url}/{self.small_app_name}/config/etl')

    @patch('requests.delete')
    @patch('requests.put')
    @patch('requests.post')
    @patch('requests.get')
    def test_simple_post(self, mock_get, mock_post, mock_put, mock_delete):
        self._mock_requests(
            mock_get=mock_get,
            mock_post=mock_post,
            mock_put=mock_put,
            mock_delete=mock_delete
        )

        expected_json_data = {'some': 'json'}
        self.small_app.json = expected_json_data
        resp = self.small_app.config.etl.post()
        self.assertEqual(resp, 'post')

        route = self.post_calls[0][ARGS][ROUTE]
        self.assertEqual(route, f'{self.base_url}/{self.small_app_name}/config/etl')

        json_data = self.post_calls[0][KWARGS]
        self.assertEqual(json_data, {'json': expected_json_data})

    @patch('requests.delete')
    @patch('requests.put')
    @patch('requests.post')
    @patch('requests.get')
    def test_simple_get_with_stage(self, mock_get, mock_post, mock_put, mock_delete):
        self._mock_requests(
            mock_get=mock_get,
            mock_post=mock_post,
            mock_put=mock_put,
            mock_delete=mock_delete
        )

        self.small_app.stage = 'staging'
        resp = self.small_app.config.etl.get()
        self.assertEqual(resp, 'get')

        route = self.get_calls[0][ARGS][ROUTE]
        self.assertEqual(route, f'{self.base_url}/{self.small_app_name}/config/etl?stage=staging')

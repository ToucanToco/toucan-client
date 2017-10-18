from toucan_client.client import ToucanClient, SmallAppRequester

BASE_ROUTE = 'fake.route/my-small-app'
SMALL_APP_NAME = 'my-small-app'


def test_toucanclient():
    """It should create a ToucanClient from one or multiple small-app(s)"""
    client = ToucanClient('fake.route', SMALL_APP_NAME, auth=('user', '123'))
    assert len(client.instances) == 1
    small_app = client[SMALL_APP_NAME]
    assert isinstance(small_app, SmallAppRequester)
    assert small_app.route == BASE_ROUTE
    assert small_app.kwargs['auth'].username == 'user'

    client = ToucanClient(BASE_ROUTE, ['sa1', 'sa2', 'sa3'], token='ABC')
    assert len(client.instances) == 3
    small_app = client['sa1']
    assert small_app.kwargs['headers']['Authorization'] == 'Bearer ABC'

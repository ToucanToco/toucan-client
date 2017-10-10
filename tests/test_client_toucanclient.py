from toucanclient.client import ToucanClient, SmallAppRequester

BASE_ROUTE = 'fake.route/my-small-app'
SMALL_APP_NAME = 'my-small-app'


def test_toucanclient():
    """It should create a ToucanClient from one or multiple small-app(s)"""
    client = ToucanClient('fake.route', SMALL_APP_NAME)
    assert len(client.instances) == 1
    small_app = client[SMALL_APP_NAME]
    assert isinstance(small_app, SmallAppRequester)
    assert small_app.route == BASE_ROUTE

    client = ToucanClient(BASE_ROUTE, ['my_sa1', 'my_sa2', 'my_sa3'])
    assert len(client.instances) == 3

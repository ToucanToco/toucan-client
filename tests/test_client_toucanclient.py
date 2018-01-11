from collections import namedtuple

import pytest

from tests import METHODS, BASE_ROUTE
from toucan_client.client import ToucanClient
from tests.fixtures import client, requests_wrapper


def test_toucanclient():
    client = ToucanClient(BASE_ROUTE + '/', auth=1, stage='staging')
    assert client.base_route == BASE_ROUTE
    assert client.kwargs == {'auth': 1, 'stage': 'staging'}


@pytest.mark.usefixtures('client')
def test_simple_get(client):
    """It should build the right URL"""
    _ = client.config.etl.get
    assert client.method == 'get'
    assert client.route == '{}/config/etl'.format(BASE_ROUTE)


@pytest.mark.usefixtures('client')
def test_simple_get_with_baseroute_2(client):
    _ = client.config.etl.get
    assert client.method == 'get'
    assert client.route == '{}/config/etl'.format(BASE_ROUTE)


@pytest.mark.usefixtures('client')
def test_simple_get_with_stage(client):
    """It should build the right URL (with staging stage)"""
    client.stage = 'staging'
    _ = client.config.etl.get
    assert client.method == 'get'
    assert client.route == '{}/config/etl?stage=staging'.format(BASE_ROUTE)


@pytest.mark.usefixtures('client', 'requests_wrapper')
def test_call(client, requests_wrapper):
    res = client.config.etl.get()
    assert res == 1


@pytest.mark.usefixtures('client')
def test_kwargs(client):
    """It should add kwargs"""
    client.best_character = 'Ryu'
    _ = client.config.etl.get
    assert client.kwargs == {'best_character': 'Ryu'}

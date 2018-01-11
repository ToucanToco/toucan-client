from collections import namedtuple

import pytest

from tests import METHODS, BASE_ROUTE
from toucan_client import ToucanClient


@pytest.fixture(scope='function')
def requests_wrapper(mocker):
    """Add this fixture if mocking is needed (even if mocker object is not used)"""
    wrapper_cls = namedtuple('RequestsMocker', ['get', 'post', 'put', 'delete'])
    return wrapper_cls(
        get=mocker.patch('requests.get', return_value=METHODS['get']),
        post=mocker.patch('requests.post', return_value=METHODS['post']),
        put=mocker.patch('requests.put', return_value=METHODS['put']),
        delete=mocker.patch('requests.delete', return_value=METHODS['delete'])
    )


@pytest.fixture(scope='function')
def client():
    return ToucanClient(BASE_ROUTE)

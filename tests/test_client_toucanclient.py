import json
import tempfile
from collections import namedtuple

import os
import pytest

from toucan_client.client import ToucanClient

SMALL_APP_NAME = 'my-small-app'

BASE_ROUTE = 'fake.route/my-small-app'

METHODS = {
    'get': 1,
    'post': 2,
    'put': 3,
    'delete': 4,
}


@pytest.fixture(name='requests_wrapper', scope='function')
def gen_requests_mockers(mocker):
    """Add this fixture if mocking is needed (even if mocker object is not used)"""
    wrapper_cls = namedtuple('RequestsMocker', ['get', 'post', 'put', 'delete'])
    return wrapper_cls(
        get=mocker.patch('requests.get', return_value=METHODS['get']),
        post=mocker.patch('requests.post', return_value=METHODS['post']),
        put=mocker.patch('requests.put', return_value=METHODS['put']),
        delete=mocker.patch('requests.delete', return_value=METHODS['delete'])
    )


@pytest.fixture(name='client', scope='function')
def gen_small_app():
    return ToucanClient(BASE_ROUTE)


def test_toucanclient():
    client = ToucanClient(BASE_ROUTE + '/', auth=1, stage='staging')
    assert client.base_route == BASE_ROUTE
    assert client.kwargs == {'auth': 1, 'stage': 'staging'}


def test_simple_get(client):
    """It should build the right URL"""
    _ = client.config.etl.get
    assert client.method == 'get'
    assert client.route == '{}/config/etl'.format(BASE_ROUTE)


def test_simple_get_with_baseroute_2(client):
    _ = client.config.etl.get
    assert client.method == 'get'
    assert client.route == '{}/config/etl'.format(BASE_ROUTE)


def test_simple_get_with_stage(client):
    """It should build the right URL (with staging stage)"""
    client.stage = 'staging'
    _ = client.config.etl.get
    assert client.method == 'get'
    assert client.route == '{}/config/etl?stage=staging'.format(BASE_ROUTE)


def test_call(client, requests_wrapper):
    res = client.config.etl.get()
    assert res == 1


def test_kwargs(client):
    """It should add kwargs"""
    client.best_character = 'Ryu'
    _ = client.config.etl.get
    assert client.kwargs == {'best_character': 'Ryu'}


def test_build_route(client):
    # 1. No option, stage: production
    route = client.build_route('bla')
    assert route == BASE_ROUTE + '/bla'

    # 2. Options, stage: staging
    client.stage = 'staging'
    route = client.build_route('bla', ['format=json', 'python=love'])
    assert len(route) == len(BASE_ROUTE + '/bla?stage=staging&format=json&python=love')
    assert 'stage=staging' in route
    assert 'format=json' in route
    assert 'python=love' in route


def test_upload_config_file(client, requests_wrapper):
    """Test that upload configuration file method builds the expected request."""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        with open(f.name, mode='w') as file:
            file.write('aa')

        res = client.upload_config_file(f.name, 'config/etl')
        assert res == METHODS['put']

        route, kwargs = requests_wrapper.put.call_args
        assert route[0] == BASE_ROUTE + '/config/etl?format=cson'
        assert kwargs == {'data': b'aa', 'auth': None}


def test_upload_python_module(client, requests_wrapper):
    """Test that upload python module method builds the expected request."""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        with open(f.name, mode='w') as file:
            file.write('aa')

        client.upload_python_module(f.name, 'config/augment', 'augment.py')
        route, kwargs = requests_wrapper.put.call_args
        assert route[0] == BASE_ROUTE + '/config/augment'
        assert kwargs == {'files': {'file': ('augment.py', b'aa')}, 'auth': None}


def test_upload_template(client, requests_wrapper):
    """Test that upload template method builds the expected request."""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        with open(f.name, mode='w') as file:
            file.write('aa')

        template_type = os.path.basename(os.path.dirname(f.name))
        template_name = os.path.basename(f.name).replace('.cson', '')

        client.upload_template(f.name)
        route, kwargs = requests_wrapper.put.call_args
        expected_route = '{}/templates/{}/{}?format=cson'.format(
            BASE_ROUTE, template_type, template_name)

        assert route[0] == expected_route
        assert kwargs == {
            'json': {'content': 'aa', 'type': template_type, 'name': template_name},
            'auth': None
        }


def test_upload_data_source(client, requests_wrapper):
    """Test that upload data source method builds the expected request."""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        with open(f.name, mode='w') as file:
            file.write('aa')

        client.upload_data_source(f.name)
        route, kwargs = requests_wrapper.post.call_args
        assert route[0] == BASE_ROUTE + '/data/sources'

        file_basename = os.path.basename(f.name)
        expected_kwargs = {
            'files': {'file': (file_basename, b'aa')},
            'data': {'data': json.dumps({'filename': file_basename})},
            'auth': None,
        }
        assert kwargs == expected_kwargs


def test_upload_config_file_methods(client, requests_wrapper):
    """Test return values (mostly here for coverage)"""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        res = client.upload_front_config(f.name)
        assert res == METHODS['put']

        res = client.upload_etl_config(f.name)
        assert res == METHODS['put']

        res = client.upload_preprocess_validation(f.name)
        assert res == METHODS['put']


def test_upload_python_module_methods(client, requests_wrapper):
    """Test return values (mostly here for coverage)."""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        res = client.upload_augment_py(f.name)
        assert res == METHODS['put']

        res = client.upload_permissions_py(f.name)
        assert res == METHODS['put']

        res = client.upload_notifications_handler(f.name)
        assert res == METHODS['put']

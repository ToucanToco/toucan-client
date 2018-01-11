import json
import tempfile

import os

import pytest

from tests import BASE_ROUTE, METHODS
from tests.fixtures import client, requests_wrapper
from toucan_client.utils import build_route, upload_python_module, upload_config_file, \
    upload_template, upload_front_config, upload_etl_config, upload_preprocess_validation, \
    upload_augment_py, upload_permissions_py, upload_notifications_handler, upload_data_source


@pytest.mark.usefixtures('client')
def test_build_route(client):
    # 1. No option, stage: production
    route = build_route(client, 'bla')
    assert route == BASE_ROUTE + '/bla'

    # 2. Options, stage: staging
    client.stage = 'staging'
    route = build_route(client, 'bla', ['format=json', 'python=love'])
    assert len(route) == len(BASE_ROUTE + '/bla?stage=staging&format=json&python=love')
    assert 'stage=staging' in route
    assert 'format=json' in route
    assert 'python=love' in route


@pytest.mark.usefixtures('client', 'requests_wrapper')
def test_upload_config_file(client, requests_wrapper):
    """Test that upload configuration file method builds the expected request."""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        with open(f.name, mode='w') as file:
            file.write('aa')

        res = upload_config_file(client, f.name, 'config/etl')
        assert res == METHODS['put']

        route, kwargs = requests_wrapper.put.call_args
        assert route[0] == BASE_ROUTE + '/config/etl?format=cson'
        assert kwargs == {'data': b'aa', 'auth': None}


@pytest.mark.usefixtures('client', 'requests_wrapper')
def test_upload_python_module(client, requests_wrapper):
    """Test that upload python module method builds the expected request."""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        with open(f.name, mode='w') as file:
            file.write('aa')

        upload_python_module(client, f.name, 'config/augment', 'augment.py')
        route, kwargs = requests_wrapper.put.call_args
        assert route[0] == BASE_ROUTE + '/config/augment'
        assert kwargs == {'files': {'file': ('augment.py', b'aa')}, 'auth': None}


@pytest.mark.usefixtures("requests_wrapper")
def test_upload_template(client, requests_wrapper):
    """Test that upload template method builds the expected request."""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        with open(f.name, mode='w') as file:
            file.write('aa')

        template_type = os.path.basename(os.path.dirname(f.name))
        template_name = os.path.basename(f.name).replace('.cson', '')

        upload_template(client, f.name)
        route, kwargs = requests_wrapper.put.call_args
        expected_route = '{}/templates/{}/{}?format=cson'.format(
            BASE_ROUTE, template_type, template_name)

        assert route[0] == expected_route
        assert kwargs == {
            'json': {'content': 'aa', 'type': template_type, 'name': template_name},
            'auth': None
        }


@pytest.mark.usefixtures('client', 'requests_wrapper')
def test_upload_data_source(client, requests_wrapper):
    """Test that upload data source method builds the expected request."""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        with open(f.name, mode='w') as file:
            file.write('aa')

        upload_data_source(client, f.name)
        route, kwargs = requests_wrapper.post.call_args
        assert route[0] == BASE_ROUTE + '/data/sources'

        file_basename = os.path.basename(f.name)
        expected_kwargs = {
            'files': {'file': (file_basename, b'aa')},
            'data': {'data': json.dumps({'filename': file_basename})},
            'auth': None,
        }
        assert kwargs == expected_kwargs


@pytest.mark.usefixtures('client', 'requests_wrapper')
def test_upload_config_file_methods(client, requests_wrapper):
    """Test return values (mostly here for coverage)"""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        res = upload_front_config(client, f.name)
        assert res == METHODS['put']

        res = upload_etl_config(client, f.name)
        assert res == METHODS['put']

        res = upload_preprocess_validation(client, f.name)
        assert res == METHODS['put']


@pytest.mark.usefixtures('client', 'requests_wrapper')
def test_upload_python_module_methods(client, requests_wrapper):
    """Test return values (mostly here for coverage)."""
    with tempfile.NamedTemporaryFile(mode='r') as f:
        res = upload_augment_py(client, f.name)
        assert res == METHODS['put']

        res = upload_permissions_py(client, f.name)
        assert res == METHODS['put']

        res = upload_notifications_handler(client, f.name)
        assert res == METHODS['put']

import json
import os

import requests


def build_route(client, relative_route, options=None):
    if not options:
        options = []
    if client.stage:
        options += ['stage={}'.format(client.stage)]

    args = '&'.join([arg for arg in options if arg])
    if args:
        return '{}/{}?{}'.format(client.base_route, relative_route, args)
    return '{}/{}'.format(client.base_route, relative_route)


def upload_front_config(client, config_path):
    return upload_config_file(client, config_path, 'config')


def upload_etl_config(client, config_path):
    return upload_config_file(client, config_path, 'config/etl')


def upload_preprocess_validation(client, preprocess_validation_path):
    return upload_config_file(client, preprocess_validation_path, 'config/preprocess_validation')


def upload_augment_py(client, augment_path):
    return upload_python_module(client, augment_path, 'config/augment', 'augment.py')


def upload_permissions_py(client, permissions_path):
    return upload_python_module(client, permissions_path, 'config/permissions', 'permissions.py')


def upload_notifications_handler(client, handler_path):
    return upload_python_module(
        client, handler_path, 'config/notifications_handlers', 'notifications_handler.py')


def upload_data_source(client, file_path):
    file_name = os.path.basename(file_path)
    route = build_route(client, 'data/sources')

    with open(file_path, mode='rb') as f:
        return requests.post(
            route,
            files={'file': (file_name, f.read())},
            data={'data': json.dumps({'filename': file_name})},
            auth=client.kwargs.get('auth', None)
        )


def upload_template(client, template_path):
    template_type = os.path.basename(os.path.dirname(template_path))
    template_name = os.path.basename(template_path).replace('.cson', '')
    route = build_route(
        client,
        'templates/{}/{}'.format(template_type, template_name),
        ['format=cson'])

    with open(template_path, mode='r') as f:
        return requests.put(
            route,
            json={'content': f.read(), 'type': template_type, 'name': template_name},
            auth=client.kwargs.get('auth', None)
        )


def upload_config_file(client, config_path, relative_route):
    options = ['format=cson']
    route = build_route(client, relative_route, options)

    with open(config_path, mode='rb') as file:
        return requests.put(
            route,
            data=file.read(),
            auth=client.kwargs.get('auth', None)
        )


def upload_python_module(client, module_path, relative_route, file_name):
    route = build_route(client, relative_route)

    with open(module_path, mode='rb') as file:
        return requests.put(
            route,
            files={'file': (file_name, file.read())},
            auth=client.kwargs.get('auth', None)
        )

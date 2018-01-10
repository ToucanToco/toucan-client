import json
import logging

import os
import requests


logger = logging.getLogger(__name__)


class ToucanClient:
    """
    Small client for sending request to a Toucan Toco back end.
    The constructor's mandatory parameter is the API base url. One can pass
    a small app name or a list of small app names, a token or an auth object
    for authentication.

    >>> # Example: Fetch etl config
    >>> client = ToucanClient('https://api.some.project.com')
    >>> small_app = client['my-small-app']
    >>> etl_config = small_app.config.etl.get()
    >>>
    >>> # Example: send a post request with some json data
    >>> response = small_app.config.etl.put(json={'DATA_SOURCE': ['example']})
    >>> # response.status_code equals 200 if everything went well
    """

    EXTRACTION_CACHE_PATH = 'extraction_cache'

    def __init__(self, base_route, **kwargs):
        self.__dict__['_path'] = []
        self.__dict__['kwargs'] = kwargs
        self.__dict__['stage'] = ''
        self.__dict__['_dfs'] = None
        self.__dict__['_cache_path'] = None

        self.__dict__['base_route'] = base_route
        if base_route.endswith('/'):
            self.__dict__['base_route'] = base_route[:-1]

    @property
    def method(self):
        # type: () -> str
        return self._path[-1]

    @property
    def options(self):
        # type: () -> str
        if self.stage:
            return '?stage={}'.format(self.stage)
        return ''

    @property
    def route(self):
        # type: () -> str
        route = '/'.join([self.base_route] + self._path[:-1])
        route += self.options

        self.__dict__['_path'] = []
        return route

    def build_route(self, relative_route, options=None):
        if not options:
            options = []
        if self.stage:
            options += [f'stage={self.stage}']

        args = '&'.join([arg for arg in options if arg])
        if args:
            return f'{self.base_route}/{relative_route}?{args}'
        return f'{self.base_route}/{relative_route}'

    def upload_front_config(self, config_path):
        return self.upload_config_file(config_path, 'config')

    def upload_etl_config(self, config_path):
        return self.upload_config_file(config_path, 'config/etl')

    def upload_preprocess_validation(self, preprocess_validation_path):
        return self.upload_config_file(preprocess_validation_path, 'config/preprocess_validation')

    def upload_augment_py(self, augment_path):
        return self.upload_python_module(augment_path, 'config/augment', 'augment.py')

    def upload_permissions_py(self, permissions_path):
        return self.upload_python_module(permissions_path, 'config/permissions', 'permissions.py')

    def upload_notifications_handler(self, handler_path):
        return self.upload_python_module(
            handler_path, 'config/notifications_handlers', 'notifications_handler.py')

    def upload_data_source(self, file_path):
        file_name = os.path.basename(file_path)
        route = self.build_route('data/sources')

        with open(file_path, mode='rb') as f:
            return requests.post(
                route,
                files={'file': (file_name, f.read())},
                data={'data': json.dumps({'filename': file_name})},
                auth=self.kwargs.get('auth', None)
            )

    def upload_template(self, template_path):
        template_type = os.path.basename(os.path.dirname(template_path))
        template_name = os.path.basename(template_path).replace('.cson', '')
        route = self.build_route(f'templates/{template_type}/{template_name}', ['format=cson'])

        with open(template_path, mode='r') as f:
            return requests.put(
                route,
                json={'content': f.read(), 'type': template_type, 'name': template_name},
                auth=self.kwargs.get('auth', None)
            )

    def upload_config_file(self, config_path, relative_route):
        options = ['format=cson']
        route = self.build_route(relative_route, options)

        with open(config_path, mode='rb') as file:
            return requests.put(
                route,
                data=file.read(),
                auth=self.kwargs.get('auth', None)
            )

    def upload_python_module(self, module_path, relative_route, file_name):
        route = self.build_route(relative_route)

        with open(module_path, mode='rb') as file:
            return requests.put(
                route,
                files={'file': (file_name, file.read())},
                auth=self.kwargs.get('auth', None)
            )

    def __getattr__(self, key):
        self._path.append(key)
        return self

    def __setattr__(self, key, value):
        if key == 'stage':
            self.__dict__['stage'] = value
        else:
            self.kwargs[key] = value

    def __call__(self):
        # type: () -> requests.Response
        method, route = self.method, self.route
        func = getattr(requests, method)
        return func(route, **self.kwargs)

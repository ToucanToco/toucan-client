from typing import Union

import requests
import logging


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

    def __init__(self,
                 base_url: str,
                 instance_names: Union[list, str] ='',
                 auth=None,
                 token=None):
        self.instances = self._build_instances(instance_names)
        self.base_url = base_url
        self.auth = auth
        self.token = token

        logger.info(
            f'[ToucanClient] new client for project \'{base_url}\' '
            'with instance: '
            ','.join([f'{name}' for name in self.instances.keys()])
        )

    def _build_instances(self, instance_names: Union[list, str]) -> dict:
        def base_route(small_app_name: str) -> str:
            return f'{self.base_url}/{small_app_name}'

        if isinstance(instance_names, list):
            return {
                name: SmallAppRequester(base_route(name), auth=self.auth)
                for name in instance_names
            }
        elif isinstance(instance_names, str):
            return {instance_names: SmallAppRequester(
                base_route(instance_names), auth=self.auth)
            }

    def __getitem__(self, instance_name: str) -> SmallAppRequester:
        return self.instances[instance_name]


class SmallAppRequester:
    """
    Tool for sending http request to a server.

    >>> small_app = SmallAppRequester('https://api.some.project.com')
    >>> small_app.config.etl.get()
    >>> # -> uses the requests library to send get request to
    >>> # -> https://api.some.project.com/config/etl
    >>>
    >>> # pass stage ->
    >>> small_app.stage = 'staging'
    """

    def __init__(self, base_route: str, **kwargs):
        self.__dict__['_path'] = []
        self.__dict__['kwargs'] = kwargs
        self.__dict__['stage'] = ''

        self.__dict__['base_route'] = base_route
        if base_route.endswith('/'):
            self.__dict__['base_route'] = base_route[:-1]

    @property
    def method(self) -> str:
        logger.info('f[SmallAppRequester] http method is \'{route}\'')
        return self._path[-1]

    @property
    def options(self) -> str:
        if self.stage:
            return f'?stage={self.stage}'
        return ''

    @property
    def route(self) -> str:
        route = '/'.join([self.base_route] + self._path[:-1])
        route += self.options

        self.__dict__['_path'] = []

        logger.info('f[SmallAppRequester] route is \'{route}\'')
        return route

    def __getattr__(self, key) -> type:
        self._path.append(key)
        return self

    def __setattr__(self, key, value):
        if key == 'stage':
            self.__dict__['stage'] = value
        else:
            self.kwargs[key] = value

    def __call__(self) -> requests.Response:
        func = getattr(requests, self.method)
        return func(self.route, **self.kwargs)

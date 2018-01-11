import inspect
import logging

import requests

from toucan_client.utils import build_route, filter_call

logger = logging.getLogger(__name__)


API_KEYWORDS = [
    'config',
    'etl',
    'preprocess',
    'data',
    'release',
    'populate',
    'state',
    'refresh',
    'operations',
    'load',
    'providers',
    'sources',
    'reports',
    'dashboards',
    'augment',
    'permissions',
    'front',
    'get',

    # HTTP methods
    'post',
    'delete',
    'put',
    'patch'
]


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
        self.kwargs = kwargs
        self.stage = kwargs.pop('stage', '')
        self._base_route = base_route
        self._paths = []

        for attr in API_KEYWORDS:
            setattr(self, attr, self)
        setattr(self, '__setattr__', self._setattr)

    @property
    def base_route(self):
        if self._base_route.endswith('/'):
            return self._base_route[:-1]
        return self._base_route

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
        route = '/'.join([self.base_route] + self._paths[:-1])
        route += self.options

        self.__dict__['_paths'] = []
        return route

    def reset_kwargs(self):
        self.__dict__['kwargs'] = {}

    def _setattr(self, key, value):
        """
        Special attributes (like stage) and kwargs to pass to requests (at
        each call).
        """
        if key == 'stage':
            self.stage = value
        else:
            self.kwargs[key] = value

    def __getattr__(self, item):
        print(f'getattr {item}:: _paths is {self.__dict__["_paths"]}')
        self.__dict__['_paths'].append(item)
        return super(ToucanClient, self).__getattr__(item)

    def __objclass__(self):
        return self.__class__

    def __name__(self):
        return 'ToucanClient'

    def __call__(self, **kwargs):
        """
        Use inspect to find how this method has been called.
        Example: client.config.etl.get(). The first item on the stack gives us
        information about the call to __call__, the second one to
        client.config.etl.get(). The code_context is a list of one string:
        'client.config.etl.get()'

        Args:
            **kwargs: pass kwargs to requests.get/post/etc.

        Returns:
            requests.Response

        """
        # type: () -> requests.Response
        stack = inspect.stack()

        call = stack[1].code_context[0].strip().split('.')  # stack[0] is the call to __call__
        split = filter_call(call)

        import ipdb; ipdb.set_trace()

        func_name = split.func_name
        func = getattr(requests, func_name)
        route = build_route(self, '/'.join(split.route))

        self._paths = []

        kwargs.update(self.kwargs)
        return func(route, **kwargs)

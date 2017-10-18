import io
import logging
import os
import zipfile

import pandas as pd
import requests

logger = logging.getLogger(__name__)


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

    EXTRACTION_CACHE_PATH = 'extraction_cache'

    def __init__(self, base_route, **kwargs):
        # type: (str) -> SmallAppRequester
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

    @property
    def dfs(self):
        if self._dfs is None:
            if os.path.exists(self.EXTRACTION_CACHE_PATH):
                self.__dict__['_dfs'] = self.read_cache()
                logger.info('DataFrames extracted from cache')
            else:
                resp = self.sdk.get()
                dfs = self.cache_dfs(resp.content)
                self.__dict__['_dfs'] = dfs
                logger.info('Data fetched and cached')
        return self._dfs

    def cache_dfs(self, dfs_zip):
        # type: (dfs_zip) -> Dict[str, DataFrame]
        if not os.path.exists(self.EXTRACTION_CACHE_PATH):
            os.makedirs(self.EXTRACTION_CACHE_PATH)

        with io.BytesIO(dfs_zip) as bio:
            with zipfile.ZipFile(bio, mode='r') as zfile:
                names = zfile.namelist()
                for name in names:
                    data = zfile.read(name)
                    self._write_entry(name, data)
                return {
                    name: self._read_entry(name) for name in names
                }

    def read_cache(self):
        # type: () -> Dict[str, DataFrame]
        logger.info(
            'Reading data from cache ({})'.format(self.EXTRACTION_CACHE_PATH))
        return {
            name: self._read_entry(name)
            for name in os.listdir(self.EXTRACTION_CACHE_PATH)
        }

    def invalidate_cache(self):
        self.__dict__['_dfs'] = None

    def _write_entry(self, file_name, data):
        # type: (str, bytes) -> None
        file_path = os.path.join(self.EXTRACTION_CACHE_PATH, file_name)
        with open(file_path, mode='wb') as f:
            f.write(data)
        logger.info('Cache entry added: {}'.format(file_path))

    def _read_entry(self, file_name):
        # type: (str) -> pd.DataFrame
        file_path = os.path.join(self.EXTRACTION_CACHE_PATH, file_name)

        logger.info('Reading cache entry: {}'.format(file_path))
        return pd.read_feather(file_path)

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

    def __init__(self, base_url, instance_names='', auth=None, token=None):
        # type: (str, Union[list, str], Optional[str], Optional[str]) -> None
        self.requests_kwargs = {}
        if auth is not None:
            self.requests_kwargs['auth'] = requests.auth.HTTPBasicAuth(*auth)
        elif token is not None:
            self.requests_kwargs['headers'] = {
                "Authorization": "Bearer {}".format(token)
            }

        self.base_url = base_url
        self.instances = self._build_instances(instance_names)

        logger.info(
            '[ToucanClient] new client for project \'{}\' with instance: {}'
            .format(base_url,
                    ','.join([name for name in self.instances.keys()]))
        )

    def _build_instances(self, instance_names):
        # type: (Union[list, str]) -> dict

        def base_route(small_app_name):
            # type: (str) -> str
            return self.base_url + '/' + small_app_name

        if isinstance(instance_names, list):
            return {
                name: SmallAppRequester(base_route(name), **self.requests_kwargs)
                for name in instance_names
            }
        elif isinstance(instance_names, str):
            return {instance_names: SmallAppRequester(
                base_route(instance_names), **self.requests_kwargs)
            }

    def __getitem__(self, instance_name):
        # type: (str) -> SmallAppRequester
        return self.instances[instance_name]

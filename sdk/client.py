import zipfile
from typing import Union, Dict

import io
import os

import pandas as pd
import requests
import logging

from pandas import DataFrame

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

    def __init__(self, base_route: str, **kwargs):
        self.__dict__['_path'] = []
        self.__dict__['kwargs'] = kwargs
        self.__dict__['stage'] = ''
        self.__dict__['_dfs'] = None
        self.__dict__['_cache_path'] = None

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

    @property
    def dfs(self):
        if self._dfs is None:
            if os.path.exists(self.EXTRACTION_CACHE_PATH):
                self.__dict__['_dfs'] = self.read_cache()
                logger.info('DataFrames extracted from cache')
            resp = self.sdk.get()
            dfs = self.cache_dfs(resp.content)
            self.__dict__['_dfs'] = dfs
            logger.info('Data fetched and cached')
        return self._dfs

    def cache_dfs(self, dfs_zip) -> Dict[str, DataFrame]:
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

    def read_cache(self) -> Dict[str, DataFrame]:
        logger.info(f'Reading data from cache ({self.EXTRACTION_CACHE_PATH})')
        return {
            name: self._read_entry(name)
            for name in os.listdir(self.EXTRACTION_CACHE_PATH)
        }

    def invalidate_cache(self):
        self.__dict__['_dfs'] = None

    def _write_entry(self, file_name: str, data: bytes):
        file_path = os.path.join(self.EXTRACTION_CACHE_PATH, file_name)
        with open(file_path, mode='wb') as f:
            f.write(data)
        logger.info(f'Cache entry added: {file_path}')

    def _read_entry(self, file_name) -> DataFrame:
        file_path = os.path.join(self.EXTRACTION_CACHE_PATH, file_name)

        logger.info(f'Reading cache entry: {file_path}')
        return pd.read_feather(file_path)

    def __getattr__(self, key) -> type:
        self._path.append(key)
        return self

    def __setattr__(self, key, value):
        if key == 'stage':
            self.__dict__['stage'] = value
        else:
            self.kwargs[key] = value

    def __call__(self) -> requests.Response:
        method, route, kwargs = self.method, self.route, self.kwargs
        func = getattr(requests, method)

        logger.info(
            f'Sending {method} request to {route} with kwargs: {kwargs}...'
        )
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

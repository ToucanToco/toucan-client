[![Pypi-v](https://img.shields.io/pypi/v/toucan-client.svg)](https://pypi.python.org/pypi/toucan-client)
[![Pypi-pyversions](https://img.shields.io/pypi/pyversions/toucan-client.svg)](https://pypi.python.org/pypi/toucan-client)
[![Pypi-l](https://img.shields.io/pypi/l/toucan-client.svg)](https://pypi.python.org/pypi/toucan-client)
[![Pypi-wheel](https://img.shields.io/pypi/wheel/toucan-client.svg)](https://pypi.python.org/pypi/toucan-client)
[![GitHub Actions](https://github.com/ToucanToco/toucan-client/workflows/CI/badge.svg)](https://github.com/ToucanToco/toucan-client/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/ToucanToco/toucan-client/branch/main/graph/badge.svg)](https://codecov.io/gh/ToucanToco/toucan-client)

# Installation

`pip install toucan_client`

# Usage

```python
# Initialize client
auth = ('<username>', '<password>')
client = ToucanClient('https://api.some.project.com/my_small_app', auth=auth)

# Retrieve ETL config
etl_config = client.config.etl.get()  # -> GET 'https://api.some.project.com/config/etl'
client.config.etl.get(stage='staging')  # -> GET 'https://api.some.project.com/config/etl?stage=staging'

# Operations control, start a preprocess
client.data.preprocess.post(stage='staging', json={'async': True})

# Operations control, release to prod
client.data.release.post(stage='staging')
```

# Development

You need to install [poetry](https://python-poetry.org/) either globally or in a virtualenv.
Then run `make install`

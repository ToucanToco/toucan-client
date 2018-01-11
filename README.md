[![Pypi-v](https://img.shields.io/pypi/v/toucan-client.svg)](https://pypi.python.org/pypi/toucan-client)
[![Pypi-pyversions](https://img.shields.io/pypi/pyversions/toucan-client.svg)](https://pypi.python.org/pypi/toucan-client)
[![Pypi-l](https://img.shields.io/pypi/l/toucan-client.svg)](https://pypi.python.org/pypi/toucan-client)
[![Pypi-wheel](https://img.shields.io/pypi/wheel/toucan-client.svg)](https://pypi.python.org/pypi/toucan-client)
[![CircleCI](https://img.shields.io/circleci/project/github/ToucanToco/toucan-client.svg)](https://circleci.com/gh/ToucanToco/toucan-client)
[![codecov](https://codecov.io/gh/ToucanToco/toucan-client/branch/master/graph/badge.svg)](https://codecov.io/gh/ToucanToco/toucan-client)

# Installation

`pip install toucan_client`

# Usage

```python
auth = ('<username>', '<password>')
client = ToucanClient('https://api.some.project.com/my_small_app', auth=auth)
etl_config = client.config.etl.get()  # -> GET 'https://api.some.project.com/config/etl'

# Example: add staging option
client.stage = 'staging'  # -> GET 'https://api.some.project.com/config/etl?stage=staging'

# Example: send a post request with some json data
client.json = {'DATA_SOURCE': ['example']}
response = client.config.etl.put()
# response.status_code equals 200 if everything went well
```

## Upload files: routes, utils

\<api>: 'https://api-myproject.toucantoco.com/my-small-app' for example

The auth parameter can also be an requests.auth.HTTPBasicAuth object.

### etl_config.cson
PUT \<api>/config/etl[?stage=staging]

Parameters:
* files={'file': (< file_name >, \file_content>)}
* auth=(<user_name>, \<password>)

#### Util function
upload_etl_config(client: ToucanClient, etl_config_path: str) -> requests.Response

example
```python
from toucan_client.utils import upload_etl_config

upload_etl_config(client, 'my-small-app/etl_config.cson')
```

### front_config.cson
PUT \<api>/config[?stage=staging]

Parameters:
* files={'file': (<file_name>, <file_content>)}
* auth=(<user_name>, \<password>)

#### Util function
upload_front_config(client: ToucanClient, etl_config_path: str) -> requests.Response

example
```python
from toucan_client.utils import upload_front_config

upload_front_config(client, 'my-small-app/front_config.cson')
```

### preprocess_validation.cson
PUT \<api>/config/preprocess_validation[?stage=staging]

Parameters:
* files={'file': (<file_name>, <file_content>)}
* auth=(<user_name>, \<password>)

#### Util function
upload_preprocess_validation(client: ToucanClient, etl_config_path: str) -> requests.Response

example
```python
from toucan_client.utils import upload_preprocess_validation


upload_preprocess_validation(client, 'my-small-app/preprocess/preprocess_validation
.cson')
```

### augment.py
PUT \<api>/config/augment[?stage=staging]

Parameters:
* files={'file': (<file_name>, <file_content>)}
* auth=(<user_name>, \<password>)

#### Util function
upload_augment_py(client; ToucanClient, etl_config_path: str) -> requests.Response

example
```python
from toucan_client.utils import upload_augment_py

upload_augment_py(client, 'my-small-app/preprocess/augment.py')
```

### permissions.py
PUT \<api>/config/augment[?stage=staging]

Parameters:
* files={'file': (<file_name>, <file_content>)}
* auth=(<user_name>, \<password>)

#### Util function
upload_permissions_py(client: ToucanClient, permissions_path: str) -> requests.Response

example
```python
from toucan_client.utils import upload_permissions_py

upload_permissions_py(client, 'my-small-app/permissions.py')
```

### notifications_handler.py
PUT \<api>/config/notifications_handlers[?stage=staging]

Parameters:
* files={'file': (<file_name>, <file_content>)}
* auth=(<user_name>, \<password>)

#### Util function
upload_notifications_handler(client: ToucanClient, handler_path: str) -> requests.Response

example
````python
from toucan_client.utils import upload_notifications_handler

upload_notifications_handler(client, 'my-small-app/notifications_handler.py')
````

### data source
POST \<api>/data/sources[?stage=staging]

Parameters:
* files={'file': (<file_name>, <file_content>)}
* data={'data': '{"filename": <file_name>}'}
* auth=(<user_name>, \<password>)

#### Util function
upload_data_source(client: ToucanClient, file_path: str) -> requests.Response

example
````python
from toucan_client.utils import upload_data_source

upload_data_source(client, 'my-small-app/data_sources/test.csv')
````

### template (report/dashboard)
PUT \<api>/templates/<template_type>/<template_name>[?stage=staging]

Parameters:
* json={'content': <file_content>, 'type': <template_type>, 'name': <template_name>}
* auth=(<user_name>, \<password>)

#### Util function
upload_template(client: ToucanClient, template_path: str) -> requests.Response

example
````python
from toucan_client.utils import upload_template

upload_template(client, 'my-small-app/templates/reports/report1.cson')
````


# Development

## PEP8

New code must be PEP8-valid (with a maximum of 100 chars): tests wont pass if code is not.
To see PEP8 errors, run `pycodestyle <path_to_file_name>` or recursively: `pycodestyle -r .`

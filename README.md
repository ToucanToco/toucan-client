# Usage

```python
client = ToucanClient('https://api.some.project.com')
small_app = client['my-small-app']
etl_config = small_app.config.etl.get()  # -> GET 'https://api.some.project.com/config/etl'

# Example: send a post request with some json data
response = small_app.config.etl.put(json={'DATA_SOURCE': ['example']})
# response.status_code equals 200 if everything went well

# Example: add staging option
small_app.stage = 'staging'  # -> GET 'https://api.some.project.com/config/etl?stage=staging'
```

# Development

## PEP8

New code must be PEP8-valid: tests wont pass if code is not.
To see PEP8 errors, run `pycodestyle <path_to_file_name>` or recursively: `pycodestyle -r .`

# Inanna

Inanna is a python client for the Toucan Toco back end.

## Usage

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

## Sumerian goddess

> Inanna was the Sumerian goddess of love, beauty, sex, desire, fertility, war, combat, and political power, equivalent to the Akkadian, Babylonian, and Assyrian goddess Ishtar. She was also the patron goddess of the Eanna temple at the city of Uruk, which was her main cult center. She was associated with the planet Venus and her most prominent symbols included the lion and the eight-pointed star.

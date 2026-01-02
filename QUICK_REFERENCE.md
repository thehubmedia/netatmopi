# InkyPi Plugin Quick Reference

## Essential BasePlugin Interface

### Required Method

```python
def generate_image(self, settings, device_config) -> Image.Image:
    """
    Generate PIL Image for e-ink display.

    Args:
        settings: User settings from web UI (dict)
        device_config: Config instance with display settings

    Returns:
        PIL.Image object

    Raises:
        RuntimeError: For configuration errors
    """
```

### Class Structure

```python
from ..base_plugin.base_plugin import BasePlugin
from PIL import Image

class MyPlugin(BasePlugin):
    def __init__(self, config, **dependencies):
        super().__init__(config, **dependencies)

    def generate_image(self, settings, device_config):
        # 1. Load env vars: device_config.load_env_key("KEY")
        # 2. Get display config: device_config.get_config("width")
        # 3. Fetch data
        # 4. Return PIL Image
        pass
```

## Loading Configuration

### Environment Variables (.env file)

```python
api_key = device_config.load_env_key("MY_API_KEY")

if not api_key:
    raise RuntimeError("MY_API_KEY not configured in .env file")
```

### Display Settings

```python
width = device_config.get_config("width", default=800)
height = device_config.get_config("height", default=480)
timezone = device_config.get_config("timezone", default="America/New_York")
time_format = device_config.get_config("time_format", default="12h")
```

### User Settings

```python
# Get from settings dict with defaults
units = settings.get('units', 'metric')
custom_title = settings.get('customTitle', '')

# Persist values for next refresh
settings['last_updated'] = datetime.now().isoformat()
```

## Rendering Images

### Method 1: HTML/CSS Template (Recommended)

```python
return self.render_image(
    dimensions=(width, height),
    html_file="template.html",      # In render/ subdirectory
    css_file="styles.css",           # In render/ subdirectory
    template_params={
        'title': 'Weather',
        'temp': '72°F',
        'data': weather_data
    }
)
```

### Method 2: Direct PIL Drawing

```python
from PIL import Image, ImageDraw, ImageFont

image = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/path/to/font.ttf", 36)
draw.text((10, 10), "Hello", font=font, fill='black')
return image
```

## Settings Template

```python
def generate_settings_template(self):
    template_params = super().generate_settings_template()

    # Single API key
    template_params['api_key'] = {
        "required": True,
        "service": "OpenWeatherMap",
        "expected_key": "OPEN_WEATHER_MAP_SECRET"
    }

    # Multiple API keys
    template_params['api_keys'] = [
        {"required": True, "service": "API 1", "expected_key": "KEY1"},
        {"required": True, "service": "API 2", "expected_key": "KEY2"}
    ]

    # Enable style settings (frames, colors, etc)
    template_params['style_settings'] = True

    return template_params
```

## Error Handling

```python
# Missing configuration
if not api_key:
    raise RuntimeError(
        "API key not configured. Add MY_API_KEY to .env file."
    )

# API failure
if not response.ok:
    raise RuntimeError(
        f"API request failed: {response.status_code}. "
        "Check your API key and network connection."
    )

# Invalid settings
if value not in valid_options:
    raise RuntimeError(
        f"Invalid value: {value}. Must be one of {valid_options}."
    )
```

## Directory Structure

```
plugins/my_plugin/
├── my_plugin.py           # Main class
├── plugin-info.json       # Metadata
├── icon.png              # Web UI icon
├── settings.html         # Configuration form
└── render/               # Templates
    ├── template.html
    └── styles.css
```

## plugin-info.json

```json
{
  "display_name": "My Plugin",
  "id": "my_plugin",
  "class": "MyPluginClass"
}
```

## HTML Template (render/template.html)

```html
{% extends "plugin.html" %}
{% block content %}
<div class="container">
  <h1>{{ title }}</h1>
  <div class="temperature">{{ temp }}</div>
  {% for item in items %}
    <div>{{ item.name }}: {{ item.value }}</div>
  {% endfor %}
</div>
{% endblock %}
```

## Testing Mock

```python
if __name__ == "__main__":
    import os

    class MockDeviceConfig:
        def load_env_key(self, key):
            return os.getenv(key)

        def get_config(self, key=None, default=None):
            config = {"width": 800, "height": 480}
            return config.get(key, default) if key else config

    plugin = MyPlugin({})
    settings = {"units": "metric"}
    device_config = MockDeviceConfig()

    image = plugin.generate_image(settings, device_config)
    print(f"Generated: {image.size}")
```

## Netatmo Weather Plugin Example

### Load Credentials

```python
netatmo_client_id = device_config.load_env_key("NETATMO_CLIENT_ID")
netatmo_client_secret = device_config.load_env_key("NETATMO_CLIENT_SECRET")
netatmo_refresh_token = device_config.load_env_key("NETATMO_REFRESH_TOKEN")
owm_api_key = device_config.load_env_key("OPEN_WEATHER_MAP_SECRET")
```

### Initialize API Clients

```python
self.netatmo = NetatmoClient(
    netatmo_client_id,
    netatmo_client_secret,
    refresh_token=netatmo_refresh_token
)

if not self.netatmo.refresh_access_token():
    raise RuntimeError("Netatmo authentication failed")

self.owm = OpenWeatherMapClient(owm_api_key)
```

### Fetch and Render

```python
# Fetch data
self.update_data(force=True)

# Prepare template data
template_params = self.get_render_data()

# Get display size
width = device_config.get_config("width", default=800)
height = device_config.get_config("height", default=480)

# Render
return self.render_image(
    dimensions=(width, height),
    html_file="weather.html",
    css_file="weather.css",
    template_params=template_params
)
```

## Key Methods

| Method | Purpose |
|--------|---------|
| `device_config.load_env_key(key)` | Load environment variable from .env |
| `device_config.get_config(key, default)` | Get display configuration |
| `self.render_image(...)` | Convert HTML/CSS to PIL Image |
| `generate_settings_template()` | Configure web UI form |
| `generate_image(settings, device_config)` | **REQUIRED** - Generate display image |

## Common Patterns

### Lazy API Client Initialization

```python
def generate_image(self, settings, device_config):
    if not hasattr(self, 'api_client') or self.api_client is None:
        api_key = device_config.load_env_key("API_KEY")
        self.api_client = APIClient(api_key)
```

### Settings Validation

```python
required_settings = ['latitude', 'longitude', 'units']
for setting in required_settings:
    if setting not in settings:
        raise RuntimeError(f"Missing required setting: {setting}")
```

### Data Caching

```python
now = datetime.now()
cache_age = (now - self.last_update).total_seconds()

if cache_age >= self.UPDATE_INTERVAL:
    self.data = self.fetch_data()
    self.last_update = now
```

## Files

- **Integration Guide**: `/home/garrinmf/TheHubMedia/netatmopi/INKYPI_INTEGRATION_GUIDE.md`
- **Updates Summary**: `/home/garrinmf/TheHubMedia/netatmopi/PLUGIN_UPDATES_SUMMARY.md`
- **Plugin Code**: `/home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin/netatmo_weather.py`

# InkyPi Plugin Integration Guide

## Overview

This guide explains how to integrate the Netatmo Weather plugin with InkyPi's BasePlugin architecture for e-ink display rendering.

## InkyPi BasePlugin Architecture

### 1. BasePlugin Class Interface

All InkyPi plugins must inherit from `BasePlugin` and implement specific methods:

```python
from ..base_plugin.base_plugin import BasePlugin
from PIL import Image

class MyPlugin(BasePlugin):
    def __init__(self, config, **dependencies):
        """
        Initialize the plugin.

        Args:
            config: Plugin configuration from plugin-info.json
            **dependencies: Additional dependencies injected by InkyPi
        """
        super().__init__(config, **dependencies)
        # Your initialization code here

    def generate_image(self, settings, device_config):
        """
        REQUIRED: Generate the display image.

        Args:
            settings: Dict with user-configured values from web UI
            device_config: Config instance with display settings and env keys

        Returns:
            PIL.Image object for the e-ink display

        Raises:
            RuntimeError: For configuration errors or API failures
        """
        raise NotImplementedError("Must implement generate_image")
```

### 2. Configuration Loading

InkyPi provides two methods for accessing configuration:

#### Loading Environment Variables

```python
def generate_image(self, settings, device_config):
    # Load API keys from .env file
    api_key = device_config.load_env_key("MY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "API key not configured. "
            "Please add MY_API_KEY to .env file."
        )
```

The `load_env_key()` method:
- Uses `python-dotenv` with override enabled
- Returns the environment variable value or `None`
- Pattern: `device_config.load_env_key("VARIABLE_NAME")`

#### Accessing Device Configuration

```python
def generate_image(self, settings, device_config):
    # Get display dimensions
    width = device_config.get_config("width", default=800)
    height = device_config.get_config("height", default=480)

    # Get user preferences
    timezone = device_config.get_config("timezone", default="America/New_York")
    time_format = device_config.get_config("time_format", default="12h")
```

The `get_config()` method:
- Signature: `get_config(key=None, default={})`
- With key: returns specific config value or default
- Without key: returns entire config dictionary

### 3. Settings Template (Optional)

Override `generate_settings_template()` to customize the web UI form:

```python
def generate_settings_template(self):
    """Generate parameters for the settings form."""
    template_params = super().generate_settings_template()

    # Inform UI about required API keys
    template_params['api_key'] = {
        "required": True,
        "service": "OpenWeatherMap",
        "expected_key": "OPEN_WEATHER_MAP_SECRET"
    }

    # Or multiple keys:
    template_params['api_keys'] = [
        {
            "required": True,
            "service": "Service Name",
            "expected_key": "ENV_VAR_NAME"
        }
    ]

    # Enable standard style settings (frame, colors, etc.)
    template_params['style_settings'] = True

    return template_params
```

### 4. Rendering Images

InkyPi provides two approaches for generating images:

#### Option A: Direct PIL Image Creation

```python
from PIL import Image, ImageDraw, ImageFont

def generate_image(self, settings, device_config):
    width = device_config.get_config("width", default=800)
    height = device_config.get_config("height", default=480)

    # Create image
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Draw your content
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    draw.text((10, 10), "Hello World", font=font, fill='black')

    return image
```

#### Option B: HTML/CSS Template Rendering (Recommended)

```python
def generate_image(self, settings, device_config):
    # Prepare data for template
    template_params = {
        'title': 'Weather',
        'temperature': '72°F',
        'conditions': 'Sunny',
        'forecast': [...]
    }

    # Get display dimensions
    width = device_config.get_config("width", default=800)
    height = device_config.get_config("height", default=480)

    # Render HTML/CSS to image
    return self.render_image(
        dimensions=(width, height),
        html_file="weather.html",      # In render/ subdirectory
        css_file="weather.css",         # In render/ subdirectory
        template_params=template_params
    )
```

The `render_image()` method:
- Uses Jinja2 for template rendering
- Converts HTML to screenshot using headless Chromium
- Looks for templates in plugin's `render/` directory
- Automatically merges base plugin CSS with your CSS

## Netatmo Weather Plugin Implementation

### Class Structure

```python
class NetatmoWeatherPlugin(BasePlugin):
    """
    Combined Netatmo + OpenWeatherMap weather display.

    Inherits from InkyPi's BasePlugin to integrate with e-ink display.
    """

    # Update intervals
    NETATMO_UPDATE_INTERVAL = 300  # 5 minutes
    OWM_UPDATE_INTERVAL = 7200     # 2 hours

    def __init__(self, config, **dependencies):
        super().__init__(config, **dependencies)

        # Initialize state
        self.stations = []
        self.current_station_index = 0
        self.netatmo_data = None
        self.owm_data = None

        # API clients initialized in generate_image
```

### Loading API Keys

```python
def generate_image(self, settings, device_config):
    # Load credentials from .env file
    netatmo_client_id = device_config.load_env_key("NETATMO_CLIENT_ID")
    netatmo_client_secret = device_config.load_env_key("NETATMO_CLIENT_SECRET")
    netatmo_refresh_token = device_config.load_env_key("NETATMO_REFRESH_TOKEN")
    owm_api_key = device_config.load_env_key("OPEN_WEATHER_MAP_SECRET")

    # Validate credentials
    if not netatmo_client_id or not netatmo_client_secret:
        raise RuntimeError(
            "Netatmo credentials not configured. "
            "Please add NETATMO_CLIENT_ID and NETATMO_CLIENT_SECRET to .env"
        )

    if not netatmo_refresh_token:
        raise RuntimeError(
            "NETATMO_REFRESH_TOKEN not found. "
            "Run netatmo_auth_flow.py to obtain token."
        )

    # Initialize API clients
    self.netatmo = NetatmoClient(
        netatmo_client_id,
        netatmo_client_secret,
        refresh_token=netatmo_refresh_token
    )

    self.owm = OpenWeatherMapClient(owm_api_key)
```

### Fetching and Rendering Data

```python
def generate_image(self, settings, device_config):
    # ... load credentials (see above) ...

    # Get user settings from web UI
    units = settings.get('units', 'metric')
    forecast_days = int(settings.get('forecast_days', 5))

    # Fetch weather data
    self.update_data(force=True)

    # Prepare template parameters
    template_params = self.get_render_data()
    template_params.update({
        'units': units,
        'forecast_days': forecast_days,
    })

    # Get display dimensions
    width = device_config.get_config("width", default=800)
    height = device_config.get_config("height", default=480)

    # Render using HTML/CSS template
    return self.render_image(
        dimensions=(width, height),
        html_file="weather.html",
        css_file="weather.css",
        template_params=template_params
    )
```

### Returning PIL Image

The `generate_image()` method **must** return a `PIL.Image` object:

```python
from PIL import Image

def generate_image(self, settings, device_config) -> Image.Image:
    # ... your code ...

    # Option 1: Via render_image (returns PIL.Image)
    return self.render_image(...)

    # Option 2: Create directly
    image = Image.new('RGB', (width, height), 'white')
    # ... draw on image ...
    return image
```

## Directory Structure

For proper InkyPi integration, organize your plugin as:

```
plugins/
└── netatmo_weather/
    ├── netatmo_weather.py      # Main plugin class
    ├── plugin-info.json         # Plugin metadata
    ├── icon.png                 # Plugin icon for web UI
    ├── settings.html            # Settings form (optional)
    └── render/                  # HTML/CSS templates
        ├── weather.html
        └── weather.css
```

### plugin-info.json

```json
{
  "display_name": "Netatmo Weather",
  "id": "netatmo_weather",
  "class": "NetatmoWeatherPlugin"
}
```

### settings.html Example

```html
<div class="form-group">
  <label for="units">Units</label>
  <select id="units" name="units" class="form-control">
    <option value="metric">Metric (°C)</option>
    <option value="imperial">Imperial (°F)</option>
  </select>
</div>

<div class="form-group">
  <label for="forecast_days">Forecast Days</label>
  <input type="number" id="forecast_days" name="forecast_days"
         class="form-control" min="1" max="7" value="5">
</div>

<script>
// Prepopulate when editing existing instance
if (loadPluginSettings) {
  document.getElementById('units').value =
    pluginSettings.units || 'metric';
  document.getElementById('forecast_days').value =
    pluginSettings.forecast_days || 5;
}
</script>
```

## Complete Working Example

Here's the minimal plugin structure:

```python
from PIL import Image
from ..base_plugin.base_plugin import BasePlugin

class NetatmoWeatherPlugin(BasePlugin):
    def __init__(self, config, **dependencies):
        super().__init__(config, **dependencies)

    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params['api_keys'] = [
            {
                "required": True,
                "service": "Netatmo Client ID",
                "expected_key": "NETATMO_CLIENT_ID"
            },
            {
                "required": True,
                "service": "OpenWeatherMap",
                "expected_key": "OPEN_WEATHER_MAP_SECRET"
            }
        ]
        return template_params

    def generate_image(self, settings, device_config) -> Image.Image:
        # 1. Load environment variables
        api_key = device_config.load_env_key("MY_API_KEY")
        if not api_key:
            raise RuntimeError("API key not configured")

        # 2. Get display config
        width = device_config.get_config("width", default=800)
        height = device_config.get_config("height", default=480)

        # 3. Get user settings
        units = settings.get('units', 'metric')

        # 4. Fetch data (your API calls)
        data = self.fetch_weather_data(api_key, units)

        # 5. Prepare template parameters
        template_params = {
            'temperature': data['temp'],
            'conditions': data['conditions']
        }

        # 6. Render and return PIL Image
        return self.render_image(
            dimensions=(width, height),
            html_file="weather.html",
            css_file="weather.css",
            template_params=template_params
        )
```

## Error Handling

Always raise `RuntimeError` with clear messages for configuration issues:

```python
# Missing API key
if not api_key:
    raise RuntimeError(
        "API key not configured. "
        "Please add MY_API_KEY to .env file."
    )

# API call failed
if not data:
    raise RuntimeError(
        "Failed to fetch weather data. "
        "Check your API key and network connection."
    )

# Invalid settings
if units not in ['metric', 'imperial']:
    raise RuntimeError(
        f"Invalid units: {units}. "
        "Must be 'metric' or 'imperial'."
    )
```

## Testing Outside InkyPi

Create a mock device_config for standalone testing:

```python
if __name__ == "__main__":
    import os

    class MockDeviceConfig:
        def load_env_key(self, key):
            return os.getenv(key)

        def get_config(self, key=None, default=None):
            config = {"width": 800, "height": 480}
            return config.get(key, default) if key else config

    plugin = NetatmoWeatherPlugin({})
    settings = {"units": "metric", "forecast_days": 5}
    device_config = MockDeviceConfig()

    try:
        image = plugin.generate_image(settings, device_config)
        print(f"Generated image: {image.size}")
    except Exception as e:
        print(f"Error: {e}")
```

## Key Takeaways

1. **Inherit from BasePlugin** - Import from `..base_plugin.base_plugin`
2. **Implement generate_image(settings, device_config)** - Required method
3. **Load credentials** - Use `device_config.load_env_key("KEY_NAME")`
4. **Get display settings** - Use `device_config.get_config("width")`
5. **Return PIL.Image** - Either via `render_image()` or direct creation
6. **Raise RuntimeError** - For configuration errors with clear messages
7. **Use HTML/CSS templates** - Place in `render/` subdirectory for complex layouts
8. **Settings persistence** - Values in `settings` dict persist across refreshes

## References

- InkyPi Repository: https://github.com/fatihak/InkyPi
- Plugin Building Guide: https://github.com/fatihak/InkyPi/blob/main/docs/building_plugins.md
- Weather Plugin Example: https://github.com/fatihak/InkyPi/blob/main/src/plugins/weather/weather.py
- BasePlugin Source: https://github.com/fatihak/InkyPi/blob/main/src/plugins/base_plugin/base_plugin.py

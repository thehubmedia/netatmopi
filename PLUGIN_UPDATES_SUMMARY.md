# Netatmo Weather Plugin - InkyPi Integration Updates

## Summary of Changes

The Netatmo Weather plugin has been updated to properly integrate with the InkyPi e-ink display framework by implementing the BasePlugin interface.

## Key Changes Made

### 1. Class Inheritance

**Before:**
```python
class NetatmoWeatherPlugin:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
```

**After:**
```python
class NetatmoWeatherPlugin(BasePlugin):
    def __init__(self, config: Dict[str, Any], **dependencies):
        super().__init__(config, **dependencies)
```

### 2. Added BasePlugin Import

```python
# InkyPi imports - these will be available when running in InkyPi
try:
    from ..base_plugin.base_plugin import BasePlugin
except ImportError:
    # Fallback for standalone testing
    class BasePlugin:
        def __init__(self, config, **dependencies):
            self.config = config
        def render_image(self, dimensions, html_file, css_file=None, template_params={}):
            raise NotImplementedError("render_image only works within InkyPi")
```

### 3. Implemented generate_image() Method

Added the required `generate_image(settings, device_config)` method that:

- **Loads credentials from .env** using `device_config.load_env_key()`
  ```python
  netatmo_client_id = device_config.load_env_key("NETATMO_CLIENT_ID")
  netatmo_client_secret = device_config.load_env_key("NETATMO_CLIENT_SECRET")
  netatmo_refresh_token = device_config.load_env_key("NETATMO_REFRESH_TOKEN")
  owm_api_key = device_config.load_env_key("OPEN_WEATHER_MAP_SECRET")
  ```

- **Validates credentials** and raises clear errors
  ```python
  if not netatmo_refresh_token:
      raise RuntimeError(
          "Netatmo refresh token not configured. "
          "Run netatmo_auth_flow.py and add NETATMO_REFRESH_TOKEN to .env file."
      )
  ```

- **Fetches weather data** from Netatmo and OpenWeatherMap APIs

- **Gets display dimensions** from device config
  ```python
  width = device_config.get_config("width", default=800)
  height = device_config.get_config("height", default=480)
  ```

- **Returns PIL.Image** via render_image()
  ```python
  return self.render_image(
      dimensions=(width, height),
      html_file="weather.html",
      css_file="weather.css",
      template_params=template_params
  )
  ```

### 4. Added generate_settings_template() Method

Informs the InkyPi web UI about required API keys:

```python
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
            "service": "Netatmo Client Secret",
            "expected_key": "NETATMO_CLIENT_SECRET"
        },
        {
            "required": True,
            "service": "Netatmo Refresh Token",
            "expected_key": "NETATMO_REFRESH_TOKEN"
        },
        {
            "required": True,
            "service": "OpenWeatherMap",
            "expected_key": "OPEN_WEATHER_MAP_SECRET"
        }
    ]
    template_params['style_settings'] = True
    return template_params
```

### 5. Deferred API Client Initialization

**Before:** Clients initialized in `__init__` with credentials from config

**After:** Clients initialized in `generate_image()` with credentials from device_config

This allows credentials to be loaded from the .env file at runtime rather than requiring them at initialization.

### 6. Updated Testing Code

Added mock device_config for standalone testing:

```python
class MockDeviceConfig:
    def load_env_key(self, key):
        return os.getenv(key)

    def get_config(self, key=None, default=None):
        config = {
            "width": 800,
            "height": 480,
            "timezone": "America/New_York",
            "time_format": "12h"
        }
        if key:
            return config.get(key, default)
        return config
```

## Required Environment Variables

The plugin now expects these variables in the .env file:

```bash
# Netatmo API Credentials
NETATMO_CLIENT_ID=your_client_id
NETATMO_CLIENT_SECRET=your_client_secret
NETATMO_REFRESH_TOKEN=your_refresh_token

# OpenWeatherMap API Key
OPEN_WEATHER_MAP_SECRET=your_owm_api_key
```

## Files Still Needed

To complete the InkyPi integration, you'll need to create:

### 1. Plugin Directory Structure
```
plugins/netatmo_weather/
├── netatmo_weather.py      # ✓ Updated
├── plugin-info.json         # TODO: Create
├── icon.png                 # TODO: Create
├── settings.html            # TODO: Create
└── render/                  # TODO: Create
    ├── weather.html
    └── weather.css
```

### 2. plugin-info.json
```json
{
  "display_name": "Netatmo Weather",
  "id": "netatmo_weather",
  "class": "NetatmoWeatherPlugin"
}
```

### 3. settings.html
Form for user to configure:
- Units (metric/imperial)
- Number of forecast days
- Station selection (if multiple stations)

### 4. render/weather.html
Jinja2 template that extends InkyPi's base template:
```html
{% extends "plugin.html" %}
{% block content %}
  <!-- Your weather display HTML here -->
  <div class="weather-display">
    <h1>{{ station.name }}</h1>
    <div class="current-temp">{{ netatmo.temperature }}</div>
    <!-- etc -->
  </div>
{% endblock %}
```

### 5. render/weather.css
Styles for the weather display optimized for e-ink screens (grayscale, high contrast)

## Testing the Plugin

### Standalone Test (Current)
```bash
cd /home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin
python netatmo_weather.py
```

This will test data fetching but not rendering (requires InkyPi environment).

### Within InkyPi (After Setup)
1. Copy plugin to InkyPi's `src/plugins/netatmo_weather/` directory
2. Restart InkyPi service: `sudo systemctl restart inkypi.service`
3. Configure via web UI
4. Test rendering on e-ink display

## What Works Now

✓ BasePlugin inheritance
✓ Proper credential loading from .env
✓ generate_image() method implementation
✓ Settings template configuration
✓ Error handling with clear messages
✓ PIL.Image return type
✓ Standalone testing capability

## What's Left to Do

- [ ] Create plugin-info.json
- [ ] Create icon.png (plugin icon for web UI)
- [ ] Create settings.html (configuration form)
- [ ] Create render/weather.html (display template)
- [ ] Create render/weather.css (display styles)
- [ ] Test within InkyPi environment
- [ ] Handle button press events (if using physical buttons)

## Integration Benefits

1. **Credentials Management**: API keys stored securely in .env file
2. **Display Flexibility**: Automatically adapts to display dimensions from device config
3. **Web UI Configuration**: Users can configure plugin without editing code
4. **Template Rendering**: HTML/CSS for complex layouts instead of manual PIL drawing
5. **Error Handling**: Clear error messages guide users to fix configuration issues
6. **Standalone Testing**: Can test data fetching without full InkyPi setup

## References

- Updated Plugin: `/home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin/netatmo_weather.py`
- Integration Guide: `/home/garrinmf/TheHubMedia/netatmopi/INKYPI_INTEGRATION_GUIDE.md`
- InkyPi Repository: https://github.com/fatihak/InkyPi

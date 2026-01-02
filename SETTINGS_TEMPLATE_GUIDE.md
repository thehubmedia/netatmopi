# InkyPi Settings.html Template Guide

## Summary

This guide shows how to create a `settings.html` template for InkyPi plugins, with specific examples for the Netatmo Weather plugin.

## Best Example: Simple Settings Form

The **Weather plugin** from InkyPi repository demonstrates the recommended pattern. For the Netatmo plugin, create a `settings.html` file in the plugin directory with the following structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Netatmo Weather Settings</title>
</head>
<body>

<!-- Temperature Units Selection -->
<div class="form-group">
    <label for="units" class="form-label">Units</label>
    <select id="units" name="units" class="form-input">
        <option value="metric">Metric (°C)</option>
        <option value="imperial">Imperial (°F)</option>
    </select>
</div>

<!-- Forecast Days Selection -->
<div class="form-group">
    <label for="forecastDays" class="form-label">Forecast Days</label>
    <select id="forecastDays" name="forecastDays" class="form-input">
        <option value="3">3 Days</option>
        <option value="5">5 Days</option>
        <option value="7">7 Days</option>
    </select>
</div>

<!-- Refresh Interval -->
<div class="form-group">
    <label for="refreshInterval" class="form-label">Refresh Interval (seconds)</label>
    <input type="number" id="refreshInterval" name="refreshInterval" 
           class="form-input" min="60" max="3600" step="60" value="300">
</div>

<!-- Wind Unit Selection -->
<div class="form-group">
    <label for="windUnit" class="form-label">Wind Speed Unit</label>
    <select id="windUnit" name="windUnit" class="form-input">
        <option value="ms">Meters/Second (m/s)</option>
        <option value="kmh">Kilometers/Hour (km/h)</option>
        <option value="mph">Miles/Hour (mph)</option>
    </select>
</div>

<!-- Display Options -->
<div class="form-group">
    <label class="form-label">Display Options</label>
    <input type="checkbox" id="showIndoor" name="showIndoor" value="true">
    <label for="showIndoor">Show Indoor Conditions</label>
    <br>
    <input type="checkbox" id="showRain" name="showRain" value="true">
    <label for="showRain">Show Rain Data</label>
    <br>
    <input type="checkbox" id="showWind" name="showWind" value="true">
    <label for="showWind">Show Wind Data</label>
</div>

<!-- Station Selection -->
<div class="form-group">
    <label for="stationRotation" class="form-label">Station Rotation</label>
    <select id="stationRotation" name="stationRotation" class="form-input">
        <option value="manual">Manual (use buttons)</option>
        <option value="auto">Auto (rotate every 30s)</option>
    </select>
</div>

<script>
// Load existing settings when editing
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're editing an existing plugin instance
    if (typeof loadPluginSettings !== 'undefined' && loadPluginSettings) {
        // Prepopulate form with saved settings
        document.getElementById('units').value = pluginSettings.units || 'metric';
        document.getElementById('forecastDays').value = pluginSettings.forecastDays || 5;
        document.getElementById('refreshInterval').value = pluginSettings.refreshInterval || 300;
        document.getElementById('windUnit').value = pluginSettings.windUnit || 'kmh';
        
        // Handle checkboxes
        document.getElementById('showIndoor').checked = pluginSettings.showIndoor === 'true';
        document.getElementById('showRain').checked = pluginSettings.showRain === 'true';
        document.getElementById('showWind').checked = pluginSettings.showWind === 'true';
        
        document.getElementById('stationRotation').value = pluginSettings.stationRotation || 'manual';
    }
});
</script>

</body>
</html>
```

## Key Structural Elements Required

### 1. Form Groups
Each setting should be wrapped in a `<div class="form-group">`:
```html
<div class="form-group">
    <label for="fieldId" class="form-label">Field Label</label>
    <input type="..." id="fieldId" name="fieldId" class="form-input" ...>
</div>
```

### 2. The `name` Attribute
All input elements **must have a `name` attribute**. This becomes the key in the `settings` dictionary passed to `generate_image()`:
```python
def generate_image(self, settings, device_config):
    units = settings.get('units', 'metric')           # From name="units"
    forecast_days = settings.get('forecastDays', 5)   # From name="forecastDays"
```

### 3. Settings Prepopulation Script
Always include JavaScript to load existing settings when editing:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    if (typeof loadPluginSettings !== 'undefined' && loadPluginSettings) {
        // loadPluginSettings is a global variable set by InkyPi
        // pluginSettings object contains the saved settings
        document.getElementById('fieldId').value = pluginSettings.fieldId || 'defaultValue';
    }
});
```

### 4. Default Values
Use the `||` operator to provide defaults in case settings don't exist:
```javascript
pluginSettings.units || 'metric'
```

## How Settings Flow Through the Plugin

1. **settings.html** form inputs have `name` attributes
2. User fills form and clicks Save
3. InkyPi collects all form values into a dictionary using input `name` as keys
4. This dictionary is passed as the `settings` parameter to `generate_image()`
5. Plugin retrieves values using `settings.get(key, default)`

Example flow:
```html
<!-- settings.html -->
<input name="units" value="imperial">
<input name="forecastDays" value="7">

<!-- gets passed to plugin as: -->
settings = {
    'units': 'imperial',
    'forecastDays': '7'
}

<!-- plugin retrieves with: -->
units = settings.get('units', 'metric')  # Returns 'imperial'
forecast_days = int(settings.get('forecastDays', 5))  # Returns 7
```

## API Key Configuration in generate_settings_template()

The Python code declares required API keys:

```python
def generate_settings_template(self):
    template_params = super().generate_settings_template()
    
    # Declare required API keys - InkyPi handles the form display
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
            "service": "OpenWeatherMap API Key",
            "expected_key": "OPEN_WEATHER_MAP_SECRET"
        }
    ]
    
    # Enable style configuration UI (frames, colors, borders)
    template_params['style_settings'] = True
    
    return template_params
```

**Important**: The API key declaration in Python adds UI elements automatically. You typically **don't** add API key inputs to your `settings.html` - InkyPi's base template handles that.

## Common CSS Classes

The following classes are standard across InkyPi plugins:

| Class | Purpose |
|-------|---------|
| `.form-group` | Container for a label + input pair |
| `.form-label` | Styling for form labels |
| `.form-input` | Styling for text inputs, selects, textareas |
| `.nowrap` | Prevent text from wrapping |
| `.btn` | Button styling |

## Input Types Supported

- `<input type="text">` - Text input
- `<input type="number">` - Numeric input with min/max validation
- `<input type="checkbox">` - Checkbox (use value="true" for clarity)
- `<input type="radio">` - Radio buttons (use same `name` for groups)
- `<select>` - Dropdown lists
- `<textarea>` - Multi-line text

## Directory Structure

```
inkypi-netatmo-plugin/
├── netatmo_weather.py          # Main plugin class
├── plugin-info.json             # Plugin metadata
├── icon.png                      # Web UI icon (64x64)
├── settings.html                 # SETTINGS FORM (NEW)
├── requirements.txt
├── render/
│   ├── weather.html             # Display template
│   └── weather.css              # Display stylesheet
├── static/
│   └── netatmo_weather.css
└── templates/
    └── netatmo_weather.html
```

## Example: Netatmo Plugin Settings.html Implementation

Create `/home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin/settings.html` with these settings:

1. **Temperature Units** - metric/imperial
2. **Forecast Days** - 3/5/7 day options
3. **Wind Speed Unit** - m/s, km/h, mph
4. **Display Toggles** - show indoor, rain, wind
5. **Station Rotation** - manual or auto

The API keys (NETATMO_CLIENT_ID, etc.) are declared in the Python code and handled automatically by InkyPi.

## Testing Settings Integration

Update `generate_image()` to use settings:

```python
def generate_image(self, settings, device_config) -> Image.Image:
    # Get user settings from the settings.html form
    units = settings.get('units', 'metric')
    forecast_days = int(settings.get('forecastDays', 5))
    wind_unit = settings.get('windUnit', 'kmh')
    show_indoor = settings.get('showIndoor') == 'true'
    show_rain = settings.get('showRain') == 'true'
    show_wind = settings.get('showWind') == 'true'
    
    # ... rest of implementation ...
    
    # Pass to template
    template_params = self.get_render_data()
    template_params.update({
        'units': units,
        'forecast_days': forecast_days,
        'wind_unit': wind_unit,
        'show_indoor': show_indoor,
        'show_rain': show_rain,
        'show_wind': show_wind
    })
    
    return self.render_image(
        dimensions=(width, height),
        html_file="weather.html",
        css_file="weather.css",
        template_params=template_params
    )
```

## References

- Current plugin: `/home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin/netatmo_weather.py`
- Integration guide: `/home/garrinmf/TheHubMedia/netatmopi/INKYPI_INTEGRATION_GUIDE.md`
- InkyPi repository: https://github.com/fatihak/InkyPi
- Weather plugin example: https://github.com/fatihak/InkyPi/blob/main/src/plugins/weather/settings.html
- AI Text plugin example: https://github.com/fatihak/InkyPi/blob/main/src/plugins/ai_text/settings.html

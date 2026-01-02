# InkyPi settings.html - Quick Reference Checklist

## Before You Start

Your plugin already has `generate_settings_template()` defined in `netatmo_weather.py`:
- Declares 4 API keys (InkyPi handles form display automatically)
- Enables `style_settings = True` (adds frame/color options automatically)

You need to create: `/home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin/settings.html`

## Minimal Template Structure

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Netatmo Weather Settings</title>
</head>
<body>
    <!-- Your form fields here -->
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof loadPluginSettings !== 'undefined' && loadPluginSettings) {
            // Prepopulate existing settings
        }
    });
    </script>
</body>
</html>
```

## Every Form Field MUST Have

Checklist for each input:
- [ ] Wrapped in `<div class="form-group">`
- [ ] Has a `<label class="form-label">` with `for` attribute
- [ ] Has `id` attribute matching label's `for`
- [ ] Has `name` attribute (becomes key in settings dict)
- [ ] Has `class="form-input"` (or inherits from parent select/textarea)
- [ ] Has default value in prepopulation script

## Field Example Template

Copy this for each field:

```html
<div class="form-group">
    <label for="FIELD_ID" class="form-label">Display Label</label>
    <input type="FIELD_TYPE" id="FIELD_ID" name="FIELD_NAME" 
           class="form-input" value="DEFAULT_VALUE">
</div>

<!-- In script section: -->
document.getElementById('FIELD_ID').value = pluginSettings.FIELD_NAME || 'DEFAULT_VALUE';
```

## Common Field Types

Dropdown:
```html
<select id="units" name="units" class="form-input">
    <option value="metric">Metric (°C)</option>
    <option value="imperial">Imperial (°F)</option>
</select>
```

Checkbox:
```html
<input type="checkbox" id="showIndoor" name="showIndoor" value="true">
<label for="showIndoor">Show Indoor Data</label>
```

Number Input:
```html
<input type="number" id="refreshInterval" name="refreshInterval" 
       class="form-input" min="60" max="3600" step="60" value="300">
```

Radio Buttons:
```html
<input type="radio" id="manualRotation" name="stationRotation" value="manual">
<label for="manualRotation">Manual</label>
<input type="radio" id="autoRotation" name="stationRotation" value="auto">
<label for="autoRotation">Auto</label>
```

## Prepopulation Script Template

```javascript
<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof loadPluginSettings !== 'undefined' && loadPluginSettings) {
        // Text/Select
        document.getElementById('units').value = pluginSettings.units || 'metric';
        
        // Checkboxes (important: compare to 'true' string)
        document.getElementById('showIndoor').checked = pluginSettings.showIndoor === 'true';
        
        // Number inputs
        document.getElementById('refreshInterval').value = pluginSettings.refreshInterval || 300;
        
        // Radio buttons
        if (pluginSettings.stationRotation) {
            document.querySelector(`input[name="stationRotation"][value="${pluginSettings.stationRotation}"]`).checked = true;
        }
    }
});
</script>
```

## How Settings Connect to Python Code

1. User fills form in web UI
2. User clicks "Save" button
3. InkyPi collects form values using input `name` attributes
4. Dictionary created: `{'units': 'metric', 'forecastDays': '5', ...}`
5. When plugin runs, `generate_image()` receives this dict as `settings` parameter
6. Plugin retrieves values: `units = settings.get('units', 'metric')`

## Recommended Fields for Netatmo Plugin

Based on weather data structure:

```
1. units (select)
   - name: units
   - options: metric, imperial
   
2. forecastDays (select)
   - name: forecastDays
   - options: 3, 5, 7
   
3. windUnit (select)
   - name: windUnit
   - options: ms, kmh, mph
   
4. showIndoor (checkbox)
   - name: showIndoor
   - value: true
   
5. showRain (checkbox)
   - name: showRain
   - value: true
   
6. showWind (checkbox)
   - name: showWind
   - value: true
```

## What NOT to Include

- Do NOT add API key inputs - Python code handles them
- Do NOT use custom CSS classes - only use: form-group, form-label, form-input
- Do NOT add buttons besides modal buttons - Save button is added by InkyPi
- Do NOT add form tag - InkyPi wraps your content in a form

## CSS Classes Available

Always use these standard classes:
- `.form-group` - Container wrapper
- `.form-label` - Label text
- `.form-input` - Input/select/textarea styling
- `.btn` - Button styling (if you add buttons)

## Testing Your Template

1. Check all inputs have `name` attribute
2. Check all inputs have `id` and matching label `for`
3. Check prepopulation script handles all fields
4. Check checkbox prepopulation compares to 'true' string
5. Verify no API key fields are included
6. Run through generate_image() - it should receive proper settings dict

## Quick Syntax Check

For each `<input>`:
```
<div class="form-group">
    <label for="abc" class="form-label">Label</label>
    <input type="..." id="abc" name="abc" class="form-input">
</div>
```

name="abc" -> in settings dict becomes settings['abc']
id="abc" -> connects to <label for="abc">

## File Locations

Create at:
```
/home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin/settings.html
```

Reference files:
```
/home/garrinmf/TheHubMedia/netatmopi/SETTINGS_TEMPLATE_GUIDE.md
/home/garrinmf/TheHubMedia/netatmopi/SETTINGS_HTML_EXAMPLES.md
```

Plugin code with generate_settings_template():
```
/home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin/netatmo_weather.py (line 352)
```

## Real Examples

Simple plugin (3 fields):
https://github.com/fatihak/InkyPi/blob/main/src/plugins/ai_text/settings.html

Complex plugin (many options, modals):
https://github.com/fatihak/InkyPi/blob/main/src/plugins/weather/settings.html

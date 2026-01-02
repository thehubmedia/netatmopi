# InkyPi settings.html - Real Examples from Plugins

## Example 1: Weather Plugin (Complex)

From: https://github.com/fatihak/InkyPi/blob/main/src/plugins/weather/settings.html

This is a more complex example with conditional display based on provider selection:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.css">

<!-- Location Selection -->
<div class="form-group">
    <label for="latitude" class="form-label">Latitude</label>
    <input type="text" id="latitude" name="latitude" class="form-input" readonly>
</div>

<div class="form-group">
    <label for="longitude" class="form-label">Longitude</label>
    <input type="text" id="longitude" name="longitude" class="form-input" readonly>
</div>

<button type="button" id="selectLocationBtn" class="btn" style="margin-bottom: 1rem;">Select Location</button>

<!-- Provider Selection -->
<div class="form-group">
    <label for="provider" class="form-label">Weather Provider</label>
    <select id="provider" name="provider" class="form-input">
        <option value="open-meteo">Open-Meteo</option>
        <option value="openweathermap">OpenWeatherMap</option>
    </select>
</div>

<!-- Units Selection -->
<div class="form-group">
    <label for="units" class="form-label">Units</label>
    <select id="units" name="units" class="form-input">
        <option value="metric">Metric (°C)</option>
        <option value="imperial">Imperial (°F)</option>
        <option value="standard">Standard (K)</option>
    </select>
</div>

<!-- Title Options -->
<div id="titleOptions" class="form-group" style="display: none;">
    <label class="form-label">Title Source</label>
    <input type="radio" id="titleLocation" name="titleSource" value="location">
    <label for="titleLocation">Use Location Name</label>
    <input type="radio" id="titleCustom" name="titleSource" value="custom">
    <label for="titleCustom">Custom Title</label>
    <input type="text" id="customTitle" name="customTitle" class="form-input" 
           placeholder="Enter custom title" style="display: none; margin-top: 0.5rem;">
</div>

<!-- Display Options -->
<div class="form-group">
    <label class="form-label">Display Options</label>
    <input type="checkbox" id="showRefresh" name="showRefresh" value="true">
    <label for="showRefresh">Show Refresh Time</label>
    <input type="checkbox" id="showMetrics" name="showMetrics" value="true">
    <label for="showMetrics">Show Performance Metrics</label>
    <input type="checkbox" id="showGraph" name="showGraph" value="true">
    <label for="showGraph">Show Weather Graph</label>
    <input type="checkbox" id="showRain" name="showRain" value="true">
    <label for="showRain">Show Precipitation Amount</label>
    <input type="checkbox" id="showMoon" name="showMoon" value="true">
    <label for="showMoon">Show Lunar Phase</label>
</div>

<!-- Forecast Settings -->
<div class="form-group">
    <label class="form-label">Forecast</label>
    <input type="checkbox" id="showForecast" name="showForecast" value="true">
    <label for="showForecast">Show Forecast</label>
    <select id="forecastDays" name="forecastDays" class="form-input" style="margin-left: 1rem; margin-top: 0.5rem;">
        <option value="3">3 Days</option>
        <option value="5">5 Days</option>
        <option value="7">7 Days</option>
    </select>
</div>

<!-- Timezone Selection -->
<div class="form-group">
    <label for="timezone" class="form-label">Time Zone</label>
    <select id="timezone" name="timezone" class="form-input">
        <option value="location">Location Time Zone</option>
        <option value="local">Local System Time Zone</option>
    </select>
</div>

<!-- Location Selection Modal -->
<div id="locationModal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                               background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; 
                               align-items: center;">
    <div style="background: white; padding: 1rem; border-radius: 8px; width: 90%; max-width: 500px;">
        <h2>Select Location</h2>
        <div id="map" style="height: 300px; margin-bottom: 1rem;"></div>
        <button type="button" id="saveLocationBtn" class="btn">Save Location</button>
        <button type="button" id="closeLocationBtn" class="btn" style="margin-left: 0.5rem;">Cancel</button>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js"></script>
<script>
let map = null;
let marker = null;

document.addEventListener('DOMContentLoaded', function() {
    // Load existing settings
    if (typeof loadPluginSettings !== 'undefined' && loadPluginSettings) {
        document.getElementById('latitude').value = pluginSettings.latitude || '';
        document.getElementById('longitude').value = pluginSettings.longitude || '';
        document.getElementById('provider').value = pluginSettings.provider || 'open-meteo';
        document.getElementById('units').value = pluginSettings.units || 'metric';
        
        if (pluginSettings.titleSource) {
            document.getElementById('title' + pluginSettings.titleSource.charAt(0).toUpperCase() + 
                                  pluginSettings.titleSource.slice(1)).checked = true;
            if (pluginSettings.titleSource === 'custom') {
                document.getElementById('customTitle').style.display = 'block';
            }
        }
        
        document.getElementById('customTitle').value = pluginSettings.customTitle || '';
        document.getElementById('showRefresh').checked = pluginSettings.showRefresh === 'true';
        document.getElementById('showMetrics').checked = pluginSettings.showMetrics === 'true';
        document.getElementById('showGraph').checked = pluginSettings.showGraph === 'true';
        document.getElementById('showRain').checked = pluginSettings.showRain === 'true';
        document.getElementById('showMoon').checked = pluginSettings.showMoon === 'true';
        document.getElementById('showForecast').checked = pluginSettings.showForecast === 'true';
        document.getElementById('forecastDays').value = pluginSettings.forecastDays || '5';
        document.getElementById('timezone').value = pluginSettings.timezone || 'location';
    }
    
    // Update title options visibility
    updateTitleOptions();
    
    // Event listeners
    document.getElementById('provider').addEventListener('change', updateTitleOptions);
    document.getElementById('titleCustom').addEventListener('change', function() {
        document.getElementById('customTitle').style.display = this.checked ? 'block' : 'none';
    });
    
    // Location modal
    document.getElementById('selectLocationBtn').addEventListener('click', openLocationModal);
    document.getElementById('closeLocationBtn').addEventListener('click', closeLocationModal);
    document.getElementById('saveLocationBtn').addEventListener('click', saveLocation);
});

function updateTitleOptions() {
    const provider = document.getElementById('provider').value;
    const titleOptions = document.getElementById('titleOptions');
    
    if (provider === 'openweathermap') {
        titleOptions.style.display = 'block';
    } else {
        titleOptions.style.display = 'none';
    }
}

function openLocationModal() {
    document.getElementById('locationModal').style.display = 'flex';
    
    if (!map) {
        const lat = parseFloat(document.getElementById('latitude').value) || 40;
        const lon = parseFloat(document.getElementById('longitude').value) || -74;
        
        map = L.map('map').setView([lat, lon], 10);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        
        marker = L.marker([lat, lon], {draggable: true}).addTo(map);
    }
}

function closeLocationModal() {
    document.getElementById('locationModal').style.display = 'none';
}

function saveLocation() {
    const pos = marker.getLatLng();
    document.getElementById('latitude').value = pos.lat.toFixed(4);
    document.getElementById('longitude').value = pos.lng.toFixed(4);
    closeLocationModal();
}
</script>
```

## Example 2: AI Text Plugin (Simple)

From: https://github.com/fatihak/InkyPi/blob/main/src/plugins/ai_text/settings.html

This is a simple, straightforward example:

```html
<!-- Title -->
<div class="form-group">
    <label for="title" class="form-label">Title</label>
    <input type="text" id="title" name="title" class="form-input" 
           placeholder="Enter title for the display">
</div>

<!-- Text Prompt -->
<div class="form-group">
    <label for="prompt" class="form-label">Text Prompt</label>
    <input type="text" id="prompt" name="prompt" class="form-input" 
           placeholder="Enter your prompt">
</div>

<!-- Model Selection -->
<div class="form-group">
    <label for="model" class="form-label">Text Model</label>
    <select id="model" name="model" class="form-input">
        <option value="gpt4o-mini">GPT-4o mini</option>
        <option value="gpt4o">GPT-4o</option>
        <option value="gpt41">GPT-4.1</option>
        <option value="gpt41-mini">GPT-4.1 mini</option>
        <option value="gpt41-nano">GPT-4.1 nano</option>
        <option value="gpt5">GPT-5</option>
        <option value="gpt5-mini">GPT-5 mini</option>
        <option value="gpt5-nano">GPT-5 nano</option>
    </select>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof loadPluginSettings !== 'undefined' && loadPluginSettings) {
        document.getElementById('title').value = pluginSettings.title || '';
        document.getElementById('prompt').value = pluginSettings.prompt || '';
        document.getElementById('model').value = pluginSettings.model || 'gpt4o-mini';
    }
});
</script>
```

## Key Takeaways from Real Examples

### 1. Form Structure is Simple
- Wrap inputs in `.form-group` divs
- Use `.form-label` and `.form-input` classes
- Always include the `name` attribute

### 2. Settings Prepopulation Pattern
Every plugin uses this pattern:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    if (typeof loadPluginSettings !== 'undefined' && loadPluginSettings) {
        // Populate fields from pluginSettings object
        document.getElementById('fieldId').value = pluginSettings.fieldName || 'default';
    }
});
```

### 3. Conditional Display
Use JavaScript event listeners to show/hide fields based on user selections:
```javascript
document.getElementById('provider').addEventListener('change', updateTitleOptions);
```

### 4. No API Key Inputs
API keys are declared in Python's `generate_settings_template()` method, not in the HTML.

### 5. CSS Styling
Use only the standard classes provided by InkyPi:
- `.form-group`
- `.form-label`
- `.form-input`
- `.btn`

Don't add custom CSS - keep it consistent with other plugins.

## Netatmo Plugin Recommended Structure

Based on the existing code's `generate_settings_template()`, create a `settings.html` with:

```html
<div class="form-group">
    <label for="units" class="form-label">Temperature Units</label>
    <select id="units" name="units" class="form-input">
        <option value="metric">Metric (°C)</option>
        <option value="imperial">Imperial (°F)</option>
    </select>
</div>

<div class="form-group">
    <label for="forecastDays" class="form-label">Forecast Days</label>
    <select id="forecastDays" name="forecastDays" class="form-input">
        <option value="3">3 Days</option>
        <option value="5">5 Days</option>
        <option value="7">7 Days</option>
    </select>
</div>

<div class="form-group">
    <label for="windUnit" class="form-label">Wind Speed Unit</label>
    <select id="windUnit" name="windUnit" class="form-input">
        <option value="ms">Meters/Second (m/s)</option>
        <option value="kmh">Kilometers/Hour (km/h)</option>
        <option value="mph">Miles/Hour (mph)</option>
    </select>
</div>

<div class="form-group">
    <label class="form-label">Display Options</label>
    <input type="checkbox" id="showIndoor" name="showIndoor" value="true">
    <label for="showIndoor">Show Indoor Data</label><br>
    <input type="checkbox" id="showRain" name="showRain" value="true">
    <label for="showRain">Show Rain Data</label><br>
    <input type="checkbox" id="showWind" name="showWind" value="true">
    <label for="showWind">Show Wind Data</label>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof loadPluginSettings !== 'undefined' && loadPluginSettings) {
        document.getElementById('units').value = pluginSettings.units || 'metric';
        document.getElementById('forecastDays').value = pluginSettings.forecastDays || 5;
        document.getElementById('windUnit').value = pluginSettings.windUnit || 'kmh';
        document.getElementById('showIndoor').checked = pluginSettings.showIndoor === 'true';
        document.getElementById('showRain').checked = pluginSettings.showRain === 'true';
        document.getElementById('showWind').checked = pluginSettings.showWind === 'true';
    }
});
</script>
```

This follows InkyPi conventions while providing all the settings needed for the Netatmo weather display.

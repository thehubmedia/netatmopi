# InkyPi Weather Plugin Analysis

## Overview
The InkyPi weather plugin is an open-source e-ink weather display created by AKZ Dev (fatihak on GitHub). It pulls weather data from OpenWeatherMap or Open-Meteo and renders it as a beautiful HTML/CSS dashboard that gets displayed on e-ink screens (primarily the 7.3-inch Inky Impression from Pimoroni).

**Repository**: https://github.com/fatihak/InkyPi

## Visual Design & Layout

### Layout Structure
The weather display uses a responsive flexbox-based design with the following sections:

1. **Header Section** (15% of display height)
   - Title (location name or custom text)
   - Current date
   - Optional "Last refresh" timestamp in top-right corner

2. **Today Container** (Main content area)
   - **Left Side (50% width)**: Current weather
     - Large weather icon
     - Current temperature (45cqmin font size - very prominent)
     - "Feels Like" temperature
     - Today's high/low temperatures

   - **Right Side (50% width)**: Data Points Grid
     - 2-column grid (landscape) or 4-column grid (portrait)
     - Displays 6-9 metrics with icons:
       - Sunrise/Sunset times
       - Wind speed and direction
       - Humidity percentage
       - Pressure
       - UV Index
       - Visibility
       - Air Quality Index

3. **Hourly Temperature Chart** (16% of display height)
   - Chart.js powered visualization
   - Dual y-axes:
     - Left: Temperature line graph with gradient fill
     - Right: Precipitation probability as bars
   - Shows next 24 hours
   - Orange/yellow gradient for temperature
   - Blue gradient for precipitation
   - Rain amounts displayed on bars when significant

4. **Forecast Cards** (Bottom section)
   - Horizontal row of forecast cards (3, 5, or 7 days configurable)
   - Each card shows:
     - Day name
     - Weather icon
     - High/Low temperatures
     - Optional: Moon phase icon with illumination percentage

### Responsive Design
The layout adapts based on screen aspect ratio:
- **Portrait mode** (aspect ratio < 1): Stacks current weather above data grid
- **Landscape mode**: Side-by-side layout
- **Ultra-narrow screens** (aspect < 1/2): 3-column data grid
- **Ultra-wide screens** (aspect > 2): 3-column, 3-row data grid
- **Very small widths** (< 250px): Switches to "Dogica" font

### Visual Aesthetics
- **Font**: "Jost" (modern, clean sans-serif)
- **Colors**: Configurable text color, typically black on white for e-ink
- **Borders**: Rounded borders (1.2vw radius) on forecast cards
- **Spacing**: Uses dvh (viewport height) and dvw (viewport width) units for fluid scaling
- **Icons**: Custom weather icons for all conditions, day/night variants
- **Chart styling**: Smooth curves (tension: 0.5), gradient fills, minimal gridlines

## Weather Data Displayed

### Current Conditions
- Current temperature
- "Feels Like" temperature
- Weather icon (day/night specific)
- Today's high/low forecast

### Metrics (Toggleable)
- **Sunrise/Sunset**: Times formatted in 12h or 24h format
- **Wind**: Speed (mph or m/s) with directional arrow
- **Humidity**: Percentage
- **Pressure**: hPa or inHg
- **UV Index**: Numerical value
- **Visibility**: Miles or kilometers
- **Air Quality**: AQI value (OpenWeatherMap only)

### Hourly Forecast (Next 24 hours)
- Temperature trend
- Precipitation probability (%)
- Rain amount (inches or mm) when significant

### Multi-Day Forecast (3, 5, or 7 days)
- Day name
- Weather icon
- High temperature
- Low temperature
- Moon phase icon (optional)
- Moon illumination percentage (optional)

### Moon Phase Data
- Calculated using the 'astral' library
- Shows current phase icon
- Displays illumination percentage
- Automatically adjusts for hemisphere (Northern/Southern)

## Data Sources

### OpenWeatherMap
- Uses One Call API 3.0
- Requires API key
- Free tier: 1,000 requests/day
- Provides:
  - Current weather
  - 7-day forecast
  - Hourly forecast
  - Air quality data
  - Timezone information

### Open-Meteo
- Completely free, no API key required
- Provides:
  - Current weather
  - 7-day forecast
  - Hourly forecast
  - Weather codes mapped to icons
- Does not provide:
  - Location-based title
  - Air quality data

## Configuration Options

Users can configure via web interface (`settings.html`):

### Required Settings
- **Location**: Latitude/Longitude (interactive map selection)
- **Weather Provider**: OpenWeatherMap or Open-Meteo
- **API Key**: Required for OpenWeatherMap only

### Display Preferences
- **Units**: Imperial (°F, mph, in), Metric (°C, m/s, mm), or Standard (K)
- **Title**: Location-based or custom text
- **Time Format**: 12-hour or 24-hour
- **Timezone**: Location's native or user's local

### Toggleable Elements
- Refresh time display (show/hide)
- Weather metrics grid (show/hide)
- Hourly temperature graph (show/hide)
- Rain amount annotations (show/hide)
- Moon phase information (show/hide)
- Forecast section (show/hide)
- **Forecast Days**: 3, 5, or 7 days

## Technical Implementation

### Backend (weather.py)
**Language**: Python
**Base Class**: Extends `BasePlugin`

**Key Methods**:
- `fetch_weather_data()`: Main data retrieval orchestrator
- `fetch_weather_data_openweather()`: OpenWeatherMap API integration
- `fetch_weather_data_openmeteo()`: Open-Meteo API integration
- `get_air_quality()`: AQI data from OpenWeatherMap
- `get_moon_phase()`: Calculate moon phase using astral library
- `map_weather_code_to_icon()`: Convert weather codes to icon paths
- `format_time()`: Handle 12h/24h time formatting with timezones

**Data Processing**:
- Unit conversions (rainfall mm to inches, temperature scales)
- Timezone handling (both location-based and user-local)
- Weather code mapping to icons
- Moon phase calculations with hemisphere adjustment
- Wind direction to arrow character conversion

### Frontend (weather.html + weather.css)
**Template Engine**: Jinja2
**Charting Library**: Chart.js
**Styling**: Modern CSS with container queries, flexbox, and grid

**Key Features**:
- Conditional rendering based on plugin settings
- Dynamic unit display
- Responsive layout with media queries
- Custom Chart.js plugin for rain annotations
- Gradient fills on temperature and precipitation
- SVG-like weather icons

### Icon System
**Total Icons**: 38 PNG files

**Weather Condition Icons**:
- Clear sky (day/night)
- Few clouds (day/night)
- Scattered/broken clouds
- Rain/showers (day/night)
- Thunderstorms
- Snow (various intensities)
- Mist/fog
- Freezing rain
- Dust/sand

**Moon Phase Icons**:
- New moon, first quarter, full moon, last quarter
- Waxing/waning crescent and gibbous

**Metric Icons**:
- Humidity, pressure, wind, visibility
- UV index, air quality
- Sunrise, sunset

## Design Principles

1. **E-Ink Optimized**
   - High contrast black on white
   - Minimal animations (Chart.js animation: 0)
   - Clean, readable typography
   - Large text sizes for visibility

2. **Information Density**
   - Comprehensive data without clutter
   - Logical grouping (current, hourly, daily)
   - Progressive disclosure (toggleable sections)

3. **Responsive Flexibility**
   - Works in portrait and landscape
   - Adapts to various e-ink display sizes
   - Fluid typography using viewport units

4. **Visual Hierarchy**
   - Current temperature most prominent (45cqmin)
   - Supporting data appropriately sized
   - Icons aid quick scanning
   - Consistent spacing and alignment

5. **Configurability**
   - All major sections can be toggled
   - Multiple unit systems
   - Choice of data provider
   - Customizable forecast length

## Screenshots & Examples

Unfortunately, the GitHub repository does not include actual screenshots of the weather plugin in the main documentation. However, the plugin has been featured in several tech publications:

- **XDA Developers**: "This stunning Raspberry Pi e-ink weather dashboard gives you the forecast in style"
- **Hacker News**: Featured on Show HN with significant community interest
- **Instructables**: Tutorial on building color e-ink dashboards using InkyPi

To see actual examples, users would need to:
1. Visit the YouTube channel of AKZ Dev
2. Check the GitHub Discussions or Issues for user-posted examples
3. Look at the community builds section (if populated)

## Key Design Takeaways for Inspiration

1. **Clean, Modern Layout**: The use of Jost font and ample whitespace creates a contemporary look suitable for e-ink displays

2. **Smart Information Architecture**:
   - Most important info (current temp) is largest
   - Related metrics grouped visually
   - Temporal progression (current → hourly → daily) flows naturally

3. **Effective Use of Icons**:
   - Every metric has an associated icon
   - Day/night variants for weather conditions
   - Moon phases add visual interest

4. **Chart Integration**:
   - Dual-axis chart elegantly shows temperature and precipitation
   - Gradient fills add visual appeal even on monochrome displays
   - Minimal chrome keeps focus on data

5. **Responsive Excellence**:
   - Layout adapts intelligently to different aspect ratios
   - Uses modern CSS (container queries, dvh/dvw units)
   - Maintains readability across device sizes

6. **Configurability**:
   - Nearly every display element is optional
   - Multiple data sources supported
   - Extensive unit preferences

7. **Moon Phase Integration**:
   - Adds unique visual element
   - Shows both icon and percentage
   - Hemisphere-aware calculations

8. **Hourly Chart Design**:
   - Temperature line with warm gradient (yellow/orange)
   - Precipitation bars with cool gradient (blue)
   - Rain amounts annotated intelligently (above/below bar based on height)
   - Minimal axis labels (just min/max values)

## Plugin Architecture

**File Structure**:
```
weather/
├── icons/              # 38 PNG weather/moon/metric icons
├── render/
│   ├── weather.html    # Jinja2 template
│   └── weather.css     # Stylesheet
├── icon.png           # Plugin icon
├── plugin-info.json   # Metadata
├── settings.html      # Web UI configuration form
└── weather.py         # Python implementation
```

**Integration Points**:
- Extends `BasePlugin` from InkyPi framework
- Uses shared `plugin.html` base template
- Leverages Chart.js from shared static directory
- Chromium headless captures rendered HTML
- Output sent to e-ink display driver

## Conclusion

The InkyPi weather plugin demonstrates excellent design for e-ink displays with a focus on:
- Readability and clarity
- Information density without clutter
- Responsive, adaptive layouts
- Beautiful data visualization
- Extensive configurability
- Clean, modern aesthetics

The HTML/CSS rendering approach allows for sophisticated layouts and charting that would be difficult to achieve with direct framebuffer drawing, making it an excellent reference for designing weather displays.

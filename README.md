# E-Ink Weather Dashboard w/ Netatmo Support

A custom [InkyPi](https://github.com/fatihak/InkyPi) plugin that combines real-time weather data from your Netatmo weather station with OpenWeatherMap forecasts on a Pimoroni Inky Impression e-ink display.

## Features

- **Dual Data Sources**: Real-time local conditions from Netatmo + accurate forecasts from OpenWeatherMap
- **Multi-Station Support**: Cycle through multiple Netatmo stations using display buttons
- **Smart Updates**:
  - Netatmo data refreshes every 5 minutes (partial screen update)
  - OWM forecast refreshes every 2 hours
  - LED feedback during data fetching
- **Location-Aware Forecasts**: OWM forecast automatically updates when you switch Netatmo stations
- **E-ink Optimized**: High-contrast design with partial refresh support for the Inky Impression 2025 edition

## Hardware Requirements

- Raspberry Pi (3, 4, or Zero 2 W recommended)
- Pimoroni Inky Impression Display 2025 edition (7.3" or 13.3")
- Internet connection

## Software Requirements

- [InkyPi](https://github.com/fatihak/InkyPi) installed and running (see their documentation)
- Python 3.9+
- Netatmo Weather Station with API access
- OpenWeatherMap API key (free tier: 1000 calls/day)

## Installation

### 1. Prerequisites

First, install and configure InkyPi following their [official documentation](https://github.com/fatihak/InkyPi).

### 2. Install the Plugin

On your Raspberry Pi, navigate to the InkyPi plugins directory and clone/copy this plugin:

```bash
cd /path/to/inkypi/src/plugins/
cp -r /path/to/netatmopi/inkypi-netatmo-plugin netatmo_weather
```

### 3. Install Python Dependencies

```bash
cd netatmo_weather
pip3 install -r requirements.txt
```

### 4. Configure API Credentials

Copy the example configuration file and edit it with your credentials:

```bash
cp config.example.yaml config.yaml
nano config.yaml
```

Fill in your credentials:

**Netatmo Credentials**:
1. Go to https://dev.netatmo.com/
2. Create an app to get your Client ID and Client Secret
3. Use your Netatmo account email and password

**OpenWeatherMap API Key**:
1. Sign up at https://openweathermap.org/
2. Go to API Keys section
3. Generate a new API key
4. Subscribe to the "One Call API 3.0" (free for 1000 calls/day)

Alternatively, you can use environment variables from a `.env` file:

```bash
NETATMO_CLIENT_ID=your_client_id
NETATMO_CLIENT_SECRET=your_client_secret
NETATMO_USERNAME=your_email
NETATMO_PASSWORD=your_password
OPEN_WEATHER_MAP_SECRET=your_api_key
```

### 5. Enable the Plugin in InkyPi

Follow InkyPi's plugin activation process to enable the Netatmo Weather plugin through the web interface.

## Usage

### Button Controls

- **Button 1**: Switch to previous Netatmo station
- **Button 2**: Switch to next Netatmo station
- **Button 3**: Force full refresh of all data
- **Button 4**: (Reserved for future features)

When you switch stations, the display automatically:
1. Updates to show that station's real-time data
2. Fetches OWM forecast for that station's location
3. Performs a full screen refresh
4. Flashes the LED during data retrieval

### Configuration Options

Edit `config.yaml` to customize:

- **Units**: `metric` (Celsius, km/h) or `imperial` (Fahrenheit, mph)
- **Forecast Days**: Number of days to display (1-8)
- **Update Intervals**: How often to refresh each data source
- **Button Mappings**: Customize button behavior

## Display Layout

The screen is divided into two panels:

**Left Panel - Netatmo Real-Time**:
- Large current temperature display
- Humidity, pressure, wind speed
- Rain accumulation (1h/24h)
- Indoor CO₂ and noise levels (if available)
- Indoor temperature and humidity

**Right Panel - OpenWeatherMap Forecast**:
- Current conditions with "feels like" temperature
- 12-hour forecast (hourly)
- 5-day forecast (daily)
- Precipitation probability indicators

## Troubleshooting

### Authentication Issues

If Netatmo authentication fails:
1. Verify your client ID and secret at https://dev.netatmo.com/
2. Check that your username/password are correct
3. Ensure your app has the `read_station` scope enabled

### No Stations Found

If no Netatmo stations appear:
1. Verify your weather station is online in the Netatmo app
2. Check that your account has access to the station
3. Review logs for API errors

### Display Not Updating

1. Check InkyPi service status
2. Verify internet connectivity
3. Check API rate limits (OWM free tier = 1000 calls/day)
4. Review plugin logs for errors

## Development

### Testing Locally

You can test the plugin data fetching without InkyPi:

```bash
cd inkypi-netatmo-plugin
export $(cat ../.env | xargs)
python3 netatmo_weather.py
```

This will output JSON data that would be passed to the template.

### File Structure

```
inkypi-netatmo-plugin/
├── netatmo_weather.py       # Main plugin code
├── templates/
│   └── netatmo_weather.html # Display template
├── static/
│   └── netatmo_weather.css  # Styles optimized for e-ink
├── requirements.txt         # Python dependencies
├── config.example.yaml      # Example configuration
└── README.md               # This file
```

## Credits

- Built with [InkyPi](https://github.com/fatihak/InkyPi) by fatihak
- Weather display design inspired by InkyPi's weather plugin
- Uses [Netatmo API](https://dev.netatmo.com/)
- Uses [OpenWeatherMap One Call API 3.0](https://openweathermap.org/api/one-call-3)

## License

MIT License - See LICENSE file for details

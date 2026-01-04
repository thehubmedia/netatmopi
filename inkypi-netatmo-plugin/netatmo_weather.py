"""
Netatmo + OpenWeatherMap Combined Weather Plugin for InkyPi

Displays real-time data from Netatmo weather stations combined with
OpenWeatherMap forecast data. Supports multiple stations with button navigation.

This plugin integrates with InkyPi's BasePlugin architecture.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from zoneinfo import ZoneInfo
import requests
from dataclasses import dataclass

# PIL is only needed when running within InkyPi
try:
    from PIL import Image
except ImportError:
    Image = None

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

logger = logging.getLogger(__name__)


@dataclass
class NetatmoStation:
    """Represents a Netatmo weather station"""
    id: str
    name: str
    latitude: float
    longitude: float
    altitude: int
    timezone: str


@dataclass
class NetatmoData:
    """Current weather data from Netatmo"""
    station_name: str
    temperature: float
    feels_like: Optional[float]
    humidity: int
    pressure: float
    co2: Optional[int]
    noise: Optional[int]
    wind_speed: Optional[float]
    wind_direction: Optional[int]
    gust_speed: Optional[float]
    rain_1h: Optional[float]
    rain_24h: Optional[float]
    rain_today: Optional[float]
    timestamp: datetime

    # Outdoor module data
    outdoor_temp: Optional[float] = None
    outdoor_humidity: Optional[int] = None


class NetatmoClient:
    """Client for Netatmo API with OAuth2 authentication"""

    BASE_URL = "https://api.netatmo.com"
    AUTH_URL = f"{BASE_URL}/oauth2/token"
    STATION_URL = f"{BASE_URL}/api/getstationsdata"

    def __init__(self, client_id: str, client_secret: str, refresh_token: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = refresh_token
        self.token_expires_at: Optional[datetime] = None

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with Netatmo using username/password.
        Note: This uses the Resource Owner Password Credentials flow.
        For production, consider using Authorization Code flow instead.
        """
        try:
            response = requests.post(
                self.AUTH_URL,
                data={
                    "grant_type": "password",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "username": username,
                    "password": password,
                    "scope": "read_station"
                }
            )
            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            expires_in = data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info("Successfully authenticated with Netatmo")
            return True

        except requests.exceptions.HTTPError as e:
            logger.error(f"Netatmo authentication failed: {e}")
            logger.error(f"Response status: {e.response.status_code}")
            try:
                error_data = e.response.json()
                logger.error(f"Error details: {error_data}")
            except:
                logger.error(f"Response text: {e.response.text}")

            # Provide helpful hints based on status code
            if e.response.status_code == 403:
                logger.error("HINT: 403 Forbidden usually means:")
                logger.error("  1. Your app is not activated at https://dev.netatmo.com/apps")
                logger.error("  2. The 'Password' grant type is not enabled for your app")
                logger.error("  3. The 'read_station' scope is not enabled")
                logger.error("  See TROUBLESHOOTING_NETATMO.md for detailed help")
            return False
        except Exception as e:
            logger.error(f"Netatmo authentication failed: {e}")
            return False

    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            return False

        try:
            response = requests.post(
                self.AUTH_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token
                }
            )
            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            expires_in = data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info("Successfully refreshed Netatmo access token")
            return True

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return False

    def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token"""
        if not self.access_token:
            return False

        # Refresh token if it expires in the next 5 minutes
        if self.token_expires_at and datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            return self.refresh_access_token()

        return True

    def get_stations(self) -> List[NetatmoStation]:
        """Get list of all accessible Netatmo weather stations"""
        if not self._ensure_valid_token():
            logger.error("No valid access token available")
            return []

        try:
            response = requests.post(
                self.STATION_URL,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            data = response.json()

            stations = []
            for device in data.get("body", {}).get("devices", []):
                station = NetatmoStation(
                    id=device["_id"],
                    name=device.get("station_name", device.get("module_name", "Unknown")),
                    latitude=device["place"]["location"][1],
                    longitude=device["place"]["location"][0],
                    altitude=device["place"]["altitude"],
                    timezone=device["place"]["timezone"]
                )
                stations.append(station)

            return stations

        except Exception as e:
            logger.error(f"Failed to fetch Netatmo stations: {e}")
            return []

    def get_station_data(self, station_id: Optional[str] = None) -> Optional[NetatmoData]:
        """
        Get current weather data from a Netatmo station.
        If station_id is None, returns data from the first available station.
        """
        if not self._ensure_valid_token():
            logger.error("No valid access token available")
            return None

        try:
            params = {}
            if station_id:
                params["device_id"] = station_id

            response = requests.post(
                self.STATION_URL,
                headers={"Authorization": f"Bearer {self.access_token}"},
                data=params
            )
            response.raise_for_status()
            data = response.json()

            devices = data.get("body", {}).get("devices", [])
            if not devices:
                logger.warning("No Netatmo devices found")
                return None

            device = devices[0]
            dashboard = device.get("dashboard_data", {})

            # Extract indoor module data
            netatmo_data = NetatmoData(
                station_name=device.get("station_name", "Unknown Station"),
                temperature=dashboard.get("Temperature", 0),
                feels_like=None,  # Netatmo doesn't provide feels_like
                humidity=dashboard.get("Humidity", 0),
                pressure=dashboard.get("Pressure", 0),
                co2=dashboard.get("CO2"),
                noise=dashboard.get("Noise"),
                wind_speed=None,
                wind_direction=None,
                gust_speed=None,
                rain_1h=None,
                rain_24h=None,
                rain_today=None,
                timestamp=datetime.fromtimestamp(dashboard.get("time_utc", time.time()))
            )

            # Debug: Log module information
            modules = device.get("modules", [])
            logger.info(f"Found {len(modules)} modules for station {device.get('station_name')}")

            # Extract outdoor module data if available
            for module in modules:
                module_type = module.get("type")
                module_name = module.get("module_name", "Unknown")
                module_data = module.get("dashboard_data", {})

                logger.info(f"Processing module: {module_name} (Type: {module_type})")
                logger.info(f"Module keys: {list(module.keys())}")
                logger.info(f"Module reachable: {module.get('reachable')}, Battery: {module.get('battery_percent')}%")
                logger.info(f"Dashboard data keys: {list(module_data.keys()) if module_data else 'No dashboard_data'}")

                if module_type == "NAModule1":  # Outdoor module
                    outdoor_temp = module_data.get("Temperature")
                    outdoor_humidity = module_data.get("Humidity")
                    logger.info(f"Outdoor module found - Temp: {outdoor_temp}°C, Humidity: {outdoor_humidity}%")
                    netatmo_data.outdoor_temp = outdoor_temp
                    netatmo_data.outdoor_humidity = outdoor_humidity

                elif module_type == "NAModule2":  # Wind gauge
                    netatmo_data.wind_speed = module_data.get("WindStrength")
                    netatmo_data.wind_direction = module_data.get("WindAngle")
                    netatmo_data.gust_speed = module_data.get("GustStrength")
                    logger.info(f"Wind module found - Speed: {netatmo_data.wind_speed}")

                elif module_type == "NAModule3":  # Rain gauge
                    netatmo_data.rain_1h = module_data.get("Rain")
                    netatmo_data.rain_24h = module_data.get("sum_rain_24")
                    logger.info(f"Rain module found - 1h: {netatmo_data.rain_1h}mm")

            logger.info(f"Final outdoor_temp: {netatmo_data.outdoor_temp}, indoor_temp: {netatmo_data.temperature}")
            return netatmo_data

        except Exception as e:
            logger.error(f"Failed to fetch Netatmo data: {e}")
            return None


class OpenWeatherMapClient:
    """Client for OpenWeatherMap One Call API 3.0"""

    BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_forecast(self, lat: float, lon: float, units: str = "metric") -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for a location.

        Args:
            lat: Latitude
            lon: Longitude
            units: Unit system (metric, imperial, standard)
        """
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": units,
                "exclude": "minutely"  # We don't need minute-by-minute data
            }

            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to fetch OpenWeatherMap data: {e}")
            return None


class NetatmoWeatherPlugin(BasePlugin):
    """
    InkyPi plugin that combines Netatmo real-time data with OpenWeatherMap forecasts.

    This plugin displays:
    - Current conditions from Netatmo (real-time, high accuracy)
    - Hourly and daily forecasts from OpenWeatherMap
    - Supports multiple Netatmo stations with button navigation

    Inherits from InkyPi's BasePlugin to integrate with the e-ink display system.
    """

    # Update intervals (in seconds)
    NETATMO_UPDATE_INTERVAL = 300  # 5 minutes
    OWM_UPDATE_INTERVAL = 7200     # 2 hours

    def __init__(self, config: Dict[str, Any], **dependencies):
        """
        Initialize the plugin following InkyPi's BasePlugin pattern.

        Args:
            config: Plugin configuration from plugin-info.json
            **dependencies: Additional dependencies injected by InkyPi
        """
        # Initialize BasePlugin
        super().__init__(config, **dependencies)

        # Station management
        self.stations: List[NetatmoStation] = []
        self.current_station_index = 0

        # Cached data
        self.netatmo_data: Optional[NetatmoData] = None
        self.owm_data: Optional[Dict[str, Any]] = None
        self.last_netatmo_update = None
        self.last_owm_update = None

        # API clients will be initialized in generate_image with credentials

    def generate_settings_template(self):
        """
        Generate template parameters for the settings UI.

        Returns dict with parameters for rendering settings.html
        """
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

    def generate_image(self, settings: Dict[str, Any], device_config):
        """
        Generate the weather display image for the e-ink screen.

        This is the main method required by InkyPi's BasePlugin.

        Args:
            settings: User-configured settings from the web UI
            device_config: InkyPi Config instance with display settings and env keys

        Returns:
            PIL.Image object ready for display on the e-ink screen

        Raises:
            RuntimeError: If required configuration is missing or API calls fail
        """
        # Load API credentials from environment variables
        netatmo_client_id = device_config.load_env_key("NETATMO_CLIENT_ID")
        netatmo_client_secret = device_config.load_env_key("NETATMO_CLIENT_SECRET")
        netatmo_refresh_token = device_config.load_env_key("NETATMO_REFRESH_TOKEN")
        owm_api_key = device_config.load_env_key("OPEN_WEATHER_MAP_SECRET")

        # Validate required credentials
        if not netatmo_client_id or not netatmo_client_secret:
            raise RuntimeError(
                "Netatmo credentials not configured. "
                "Please add NETATMO_CLIENT_ID and NETATMO_CLIENT_SECRET to .env file."
            )

        if not netatmo_refresh_token:
            raise RuntimeError(
                "Netatmo refresh token not configured. "
                "Run netatmo_auth_flow.py and add NETATMO_REFRESH_TOKEN to .env file."
            )

        if not owm_api_key:
            raise RuntimeError(
                "OpenWeatherMap API key not configured. "
                "Please add OPEN_WEATHER_MAP_SECRET to .env file."
            )

        # Initialize API clients if not already done
        if not hasattr(self, 'netatmo') or self.netatmo is None:
            self.netatmo = NetatmoClient(
                netatmo_client_id,
                netatmo_client_secret,
                refresh_token=netatmo_refresh_token
            )
            # Authenticate using refresh token
            if not self.netatmo.refresh_access_token():
                raise RuntimeError(
                    "Failed to authenticate with Netatmo. "
                    "Your refresh token may have expired. Run netatmo_auth_flow.py again."
                )

        if not hasattr(self, 'owm') or self.owm is None:
            self.owm = OpenWeatherMapClient(owm_api_key)

        # Load stations if needed
        if not self.stations:
            self._load_stations()

        if not self.stations:
            raise RuntimeError(
                "No Netatmo weather stations found. "
                "Please ensure your Netatmo account has at least one weather station."
            )

        # Get settings with defaults
        units = settings.get('units', 'metric')
        forecast_days = int(settings.get('forecast_days', 5))
        station_index = int(settings.get('station_index', 0))

        # Ensure station index is valid
        if station_index >= len(self.stations):
            station_index = 0
        self.current_station_index = station_index

        # Store units in config so it's available during data updates
        self.config['units'] = units

        # Update weather data
        self.update_data(force=True)

        # Prepare template parameters
        template_params = self.get_render_data()
        template_params.update({
            'units': units,
            'forecast_days': forecast_days,
        })

        # Format last refresh time (matching InkyPi weather plugin format)
        timezone_str = device_config.get_config("timezone", default="America/New_York")
        time_format = device_config.get_config("time_format", default="12h")
        try:
            tz = ZoneInfo(timezone_str)
        except Exception:
            tz = ZoneInfo("UTC")
        now = datetime.now(tz)
        if time_format == "24h":
            template_params["updated"] = now.strftime("%Y-%m-%d %H:%M")
        else:
            template_params["updated"] = now.strftime("%Y-%m-%d %I:%M %p")

        # Add plugin_settings for the base template (required for frame/style settings)
        template_params["plugin_settings"] = settings

        # Get display dimensions from device config
        width = device_config.get_config("width", default=800)
        height = device_config.get_config("height", default=480)

        # Render the image using HTML/CSS template
        return self.render_image(
            dimensions=(width, height),
            html_file="weather.html",
            css_file="weather.css",
            template_params=template_params
        )

    def _load_stations(self):
        """Load available Netatmo stations"""
        self.stations = self.netatmo.get_stations()
        if self.stations:
            logger.info(f"Loaded {len(self.stations)} Netatmo stations")
        else:
            logger.warning("No Netatmo stations found")

    def get_current_station(self) -> Optional[NetatmoStation]:
        """Get the currently selected station"""
        if not self.stations:
            return None
        return self.stations[self.current_station_index]

    def next_station(self):
        """Switch to the next station"""
        if self.stations:
            self.current_station_index = (self.current_station_index + 1) % len(self.stations)
            logger.info(f"Switched to station: {self.get_current_station().name}")
            # Force immediate update
            self.update_data(force=True)

    def previous_station(self):
        """Switch to the previous station"""
        if self.stations:
            self.current_station_index = (self.current_station_index - 1) % len(self.stations)
            logger.info(f"Switched to station: {self.get_current_station().name}")
            # Force immediate update
            self.update_data(force=True)

    def update_data(self, force: bool = False):
        """
        Update weather data from APIs.

        Args:
            force: If True, update regardless of cache age
        """
        now = datetime.now()
        station = self.get_current_station()

        if not station:
            logger.warning("No station selected, cannot update data")
            return

        # Update Netatmo data
        should_update_netatmo = (
            force or
            self.last_netatmo_update is None or
            (now - self.last_netatmo_update).total_seconds() >= self.NETATMO_UPDATE_INTERVAL
        )

        if should_update_netatmo:
            logger.info(f"Updating Netatmo data from {station.name}")
            self.netatmo_data = self.netatmo.get_station_data(station.id)
            self.last_netatmo_update = now

        # Update OWM data
        should_update_owm = (
            force or
            self.last_owm_update is None or
            (now - self.last_owm_update).total_seconds() >= self.OWM_UPDATE_INTERVAL
        )

        if should_update_owm:
            logger.info(f"Updating OWM forecast for {station.name} location")
            self.owm_data = self.owm.get_forecast(
                station.latitude,
                station.longitude,
                self.config.get("units", "metric")
            )
            self.last_owm_update = now

    def get_render_data(self) -> Dict[str, Any]:
        """
        Get data for rendering the display.

        Returns a dict containing both Netatmo and OWM data formatted for the template.
        """
        # Ensure data is up to date
        self.update_data()

        station = self.get_current_station()
        units = self.config.get("units", "metric")
        temp_unit = "°C" if units == "metric" else "°F"
        wind_unit = "km/h" if units == "metric" else "mph"

        return {
            "station": {
                "name": station.name if station else "No Station",
                "index": self.current_station_index + 1,
                "total": len(self.stations)
            },
            "netatmo": self._format_netatmo_data(temp_unit, wind_unit),
            "owm": self._format_owm_data(temp_unit, wind_unit),
            "units": {
                "temperature": temp_unit,
                "wind": wind_unit,
                "pressure": "hPa" if units == "metric" else "inHg"
            },
            "updated": datetime.now().strftime("%H:%M")
        }

    def _celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convert Celsius to Fahrenheit"""
        return (celsius * 9/5) + 32

    def _hpa_to_inhg(self, hpa: float) -> float:
        """Convert hectopascals to inches of mercury"""
        return hpa * 0.02953

    def _convert_temp(self, temp_c: float, units: str) -> float:
        """Convert temperature based on unit preference"""
        if units == "imperial":
            return self._celsius_to_fahrenheit(temp_c)
        return temp_c

    def _convert_pressure(self, hpa: float, units: str) -> tuple[float, str]:
        """Convert pressure based on unit preference, returns (value, unit_label)"""
        if units == "imperial":
            return (self._hpa_to_inhg(hpa), "inHg")
        return (hpa, "hPa")

    def _mm_to_inches(self, mm: float) -> float:
        """Convert millimeters to inches"""
        return mm * 0.03937

    def _convert_rain(self, mm: float, units: str) -> tuple[float, str]:
        """Convert rain measurement based on unit preference, returns (value, unit_label)"""
        if units == "imperial":
            return (self._mm_to_inches(mm), "in")
        return (mm, "mm")

    def _format_netatmo_data(self, temp_unit: str, wind_unit: str) -> Dict[str, Any]:
        """Format Netatmo data for template"""
        if not self.netatmo_data:
            return {"available": False}

        data = self.netatmo_data
        units = self.config.get("units", "metric")

        # Netatmo always returns Celsius, convert if needed
        outdoor_temp = data.outdoor_temp if data.outdoor_temp is not None else data.temperature
        indoor_temp = data.temperature
        outdoor_humidity = data.outdoor_humidity if data.outdoor_humidity is not None else data.humidity

        # Convert pressure
        pressure_value, pressure_unit = self._convert_pressure(data.pressure, units)

        return {
            "available": True,
            "outdoor_temp": f"{self._convert_temp(outdoor_temp, units):.1f}{temp_unit}",
            "outdoor_humidity": f"{outdoor_humidity}%",
            "indoor_temp": f"{self._convert_temp(indoor_temp, units):.1f}{temp_unit}",
            "indoor_humidity": f"{data.humidity}%",
            "pressure": f"{pressure_value:.2f} {pressure_unit}",
            "co2": f"{data.co2} ppm" if data.co2 else None,
            "noise": f"{data.noise} dB" if data.noise else None,
            "wind_speed": f"{data.wind_speed:.1f} {wind_unit}" if data.wind_speed else None,
            "wind_direction": data.wind_direction,
            "rain_1h": f"{self._convert_rain(data.rain_1h, units)[0]:.2f} {self._convert_rain(data.rain_1h, units)[1]}" if data.rain_1h is not None else None,
            "rain_24h": f"{self._convert_rain(data.rain_24h, units)[0]:.2f} {self._convert_rain(data.rain_24h, units)[1]}" if data.rain_24h is not None else None,
        }

    def _format_owm_data(self, temp_unit: str, wind_unit: str) -> Dict[str, Any]:
        """Format OpenWeatherMap data for template"""
        if not self.owm_data:
            return {"available": False}

        current = self.owm_data.get("current", {})
        hourly = self.owm_data.get("hourly", [])[:24]  # Next 24 hours
        daily = self.owm_data.get("daily", [])[:self.config.get("forecast_days", 5)]

        return {
            "available": True,
            "current": {
                "temp": f"{current.get('temp', 0):.1f}{temp_unit}",
                "feels_like": f"{current.get('feels_like', 0):.1f}{temp_unit}",
                "description": current.get("weather", [{}])[0].get("description", ""),
                "icon": current.get("weather", [{}])[0].get("icon", ""),
            },
            "hourly": [
                {
                    "time": datetime.fromtimestamp(h["dt"]).strftime("%H:%M"),
                    "temp": f"{h['temp']:.0f}",
                    "icon": h["weather"][0]["icon"],
                    "pop": int(h.get("pop", 0) * 100)  # Probability of precipitation
                }
                for h in hourly
            ],
            "daily": [
                {
                    "day": datetime.fromtimestamp(d["dt"]).strftime("%a"),
                    "high": f"{d['temp']['max']:.0f}",
                    "low": f"{d['temp']['min']:.0f}",
                    "icon": d["weather"][0]["icon"],
                    "pop": int(d.get("pop", 0) * 100),
                    "rain": d.get("rain", 0)  # Rain volume in mm
                }
                for d in daily
            ],
            "today_rain_forecast": self._format_rain_forecast(daily[0] if daily else None)
        }

    def _format_rain_forecast(self, today_data: Optional[Dict]) -> Optional[str]:
        """Format today's rain forecast from OWM data"""
        if not today_data:
            return None

        rain_mm = today_data.get("rain", 0)
        pop = int(today_data.get("pop", 0) * 100)
        units = self.config.get("units", "metric")

        if units == "imperial":
            rain_value = rain_mm * 0.03937  # Convert mm to inches
            rain_unit = "in"
        else:
            rain_value = rain_mm
            rain_unit = "mm"

        return {
            "amount": f"{rain_value:.2f} {rain_unit}",
            "chance": f"{pop}%"
        }

    def handle_button(self, button_id: int, settings: Dict[str, Any], device_config):
        """
        Handle button press events.

        Button mapping:
        - Button 1: Previous station
        - Button 2: Next station
        - Button 3: Force full refresh
        - Button 4: (Reserved for future use)

        Returns: New image to display
        """
        logger.info(f"Button {button_id} pressed")

        if button_id == 1:
            self.previous_station()
        elif button_id == 2:
            self.next_station()
        elif button_id == 3:
            logger.info("Forcing full refresh")
            self.update_data(force=True)

        # Regenerate and return the updated image
        return self.generate_image(settings, device_config)


# Example standalone testing (when not running within InkyPi)
if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)

    # Mock device_config for testing
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

    # Create plugin instance (with empty config since we're not using plugin-info.json)
    plugin = NetatmoWeatherPlugin({})

    # Simulate settings from web UI
    settings = {
        "units": "metric",
        "forecast_days": 5,
        "station_index": 0
    }

    device_config = MockDeviceConfig()

    try:
        # Test generate_image method
        # Note: This will fail at render_image unless running in InkyPi
        # but will successfully fetch and format the data
        plugin.generate_image(settings, device_config)
    except NotImplementedError as e:
        # Expected when running standalone - just test data retrieval
        logger.info("Render not available in standalone mode, testing data retrieval only")
        render_data = plugin.get_render_data()
        print(json.dumps(render_data, indent=2, default=str))

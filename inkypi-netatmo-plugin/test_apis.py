#!/usr/bin/env python3
"""
Test script to verify Netatmo and OpenWeatherMap API connections
Run this to ensure your credentials are working before deploying to the Pi
"""

import os
import sys
import logging
from dotenv import load_dotenv
from netatmo_weather import NetatmoClient, OpenWeatherMapClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_netatmo():
    """Test Netatmo API connection"""
    print("\n" + "="*60)
    print("Testing Netatmo API Connection")
    print("="*60)

    client_id = os.getenv("NETATMO_CLIENT_ID")
    client_secret = os.getenv("NETATMO_CLIENT_SECRET")
    refresh_token = os.getenv("NETATMO_REFRESH_TOKEN")
    username = os.getenv("NETATMO_USERNAME")
    password = os.getenv("NETATMO_PASSWORD")

    # Check that we have at least client credentials
    if not client_id or not client_secret:
        print("❌ Missing Netatmo credentials in .env file")
        print("   Required: NETATMO_CLIENT_ID, NETATMO_CLIENT_SECRET")
        return False

    # Check that we have either refresh token OR username/password
    if not refresh_token and not (username and password):
        print("❌ Missing Netatmo authentication method in .env file")
        print("   Required ONE of:")
        print("     - NETATMO_REFRESH_TOKEN (recommended)")
        print("     - NETATMO_USERNAME + NETATMO_PASSWORD (fallback)")
        print()
        print("   To get a refresh token, see: GET_NETATMO_TOKEN.md")
        return False

    print(f"Client ID: {client_id[:10]}...")

    # Initialize client
    client = NetatmoClient(client_id, client_secret, refresh_token=refresh_token)

    # Test authentication
    print("\nAuthenticating...")

    if refresh_token:
        print("Using refresh token...")
        if not client.refresh_access_token():
            print("❌ Authentication with refresh token failed!")
            print("   Your token may be expired or revoked.")
            print("   Generate a new one - see GET_NETATMO_TOKEN.md")
            return False
    else:
        print(f"Using username/password (Username: {username})...")
        if not client.authenticate(username, password):
            print("❌ Authentication failed!")
            print("   Note: New Netatmo apps don't support username/password.")
            print("   Use refresh token instead - see GET_NETATMO_TOKEN.md")
            return False

    print("✅ Authentication successful!")

    # Get stations
    print("\nFetching stations...")
    stations = client.get_stations()

    if not stations:
        print("❌ No stations found!")
        return False

    print(f"✅ Found {len(stations)} station(s):")
    for i, station in enumerate(stations, 1):
        print(f"\n   Station {i}: {station.name}")
        print(f"   Location: {station.latitude}, {station.longitude}")
        print(f"   Altitude: {station.altitude}m")
        print(f"   Timezone: {station.timezone}")

    # Get data from first station
    print(f"\nFetching data from {stations[0].name}...")
    data = client.get_station_data(stations[0].id)

    if not data:
        print("❌ Failed to fetch station data!")
        return False

    print("✅ Successfully fetched weather data:")
    print(f"\n   Temperature: {data.temperature}°C")
    print(f"   Humidity: {data.humidity}%")
    print(f"   Pressure: {data.pressure} hPa")

    if data.outdoor_temp:
        print(f"   Outdoor Temp: {data.outdoor_temp}°C")
    if data.wind_speed:
        print(f"   Wind Speed: {data.wind_speed} km/h")
    if data.rain_1h:
        print(f"   Rain (1h): {data.rain_1h} mm")
    if data.co2:
        print(f"   CO₂: {data.co2} ppm")
    if data.noise:
        print(f"   Noise: {data.noise} dB")

    print(f"\n   Last updated: {data.timestamp}")

    return True

def test_openweathermap(lat=None, lon=None):
    """Test OpenWeatherMap API connection"""
    print("\n" + "="*60)
    print("Testing OpenWeatherMap API Connection")
    print("="*60)

    api_key = os.getenv("OPEN_WEATHER_MAP_SECRET")

    if not api_key:
        print("❌ Missing OpenWeatherMap API key in .env file")
        print("   Required: OPEN_WEATHER_MAP_SECRET")
        return False

    print(f"API Key: {api_key[:10]}...")

    # Use default coordinates if not provided (San Francisco)
    if lat is None or lon is None:
        lat, lon = 37.7749, -122.4194
        print(f"Using default location: San Francisco ({lat}, {lon})")
    else:
        print(f"Using location: {lat}, {lon}")

    # Initialize client
    client = OpenWeatherMapClient(api_key)

    # Fetch forecast
    print("\nFetching forecast...")
    forecast = client.get_forecast(lat, lon)

    if not forecast:
        print("❌ Failed to fetch forecast!")
        print("   Check that you have subscribed to One Call API 3.0")
        print("   Free tier: https://openweathermap.org/price")
        return False

    print("✅ Successfully fetched forecast!")

    # Display current conditions
    current = forecast.get("current", {})
    print(f"\n   Current Temperature: {current.get('temp')}°C")
    print(f"   Feels Like: {current.get('feels_like')}°C")
    print(f"   Humidity: {current.get('humidity')}%")
    print(f"   Pressure: {current.get('pressure')} hPa")

    weather = current.get("weather", [{}])[0]
    print(f"   Conditions: {weather.get('description', 'N/A')}")

    # Display hourly forecast count
    hourly = forecast.get("hourly", [])
    print(f"\n   Hourly forecast: {len(hourly)} hours")

    # Display daily forecast count
    daily = forecast.get("daily", [])
    print(f"   Daily forecast: {len(daily)} days")

    if daily:
        print("\n   Next 3 days:")
        from datetime import datetime
        for day in daily[:3]:
            date = datetime.fromtimestamp(day["dt"])
            temp_max = day["temp"]["max"]
            temp_min = day["temp"]["min"]
            desc = day["weather"][0]["description"]
            print(f"      {date.strftime('%A')}: {temp_min}°C - {temp_max}°C, {desc}")

    return True

def main():
    """Run all tests"""
    # Load environment variables from .env file
    # Try multiple locations to support both development and deployment
    env_locations = [
        # Development: .env in parent directory
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        # Deployment: .env at InkyPi root
        os.path.join(os.path.expanduser("~"), "InkyPi", ".env"),
        # Alternative InkyPi location
        "/home/pi/InkyPi/.env",
    ]

    env_file = None
    for location in env_locations:
        if os.path.exists(location):
            env_file = location
            break

    if not env_file:
        print(f"❌ .env file not found in any of these locations:")
        for loc in env_locations:
            print(f"   - {loc}")
        print("\n   Create a .env file with your API credentials")
        sys.exit(1)

    print(f"Loading credentials from: {env_file}")
    load_dotenv(env_file)

    print("\n" + "="*60)
    print("API Connection Test Suite")
    print("="*60)

    # Test Netatmo
    netatmo_ok = test_netatmo()

    # Get location from Netatmo for OWM test if available
    lat, lon = None, None
    if netatmo_ok:
        client_id = os.getenv("NETATMO_CLIENT_ID")
        client_secret = os.getenv("NETATMO_CLIENT_SECRET")
        username = os.getenv("NETATMO_USERNAME")
        password = os.getenv("NETATMO_PASSWORD")

        client = NetatmoClient(client_id, client_secret)
        client.authenticate(username, password)
        stations = client.get_stations()

        if stations:
            lat = stations[0].latitude
            lon = stations[0].longitude

    # Test OpenWeatherMap
    owm_ok = test_openweathermap(lat, lon)

    # Summary
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    print(f"Netatmo API: {'✅ PASS' if netatmo_ok else '❌ FAIL'}")
    print(f"OpenWeatherMap API: {'✅ PASS' if owm_ok else '❌ FAIL'}")

    if netatmo_ok and owm_ok:
        print("\n🎉 All tests passed! Your APIs are configured correctly.")
        print("   You can now deploy the plugin to your Raspberry Pi.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()

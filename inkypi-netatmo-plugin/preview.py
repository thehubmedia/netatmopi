#!/usr/bin/env python3
"""
Preview script for Netatmo Weather Plugin

Generates standalone HTML and PNG preview of the plugin output
without requiring the full InkyPi environment.

Usage (from repo root):
    venv/bin/python inkypi-netatmo-plugin/preview.py
    venv/bin/python inkypi-netatmo-plugin/preview.py --html-only
    venv/bin/python inkypi-netatmo-plugin/preview.py --units imperial

Requirements:
    pip install jinja2 playwright
    playwright install chromium
"""

import os
import sys
import json
import argparse
import logging
import base64
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Determine script location and add to path
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent

# Add plugin directory to path for imports
sys.path.insert(0, str(SCRIPT_DIR))

from jinja2 import Environment, BaseLoader
from dotenv import load_dotenv

from netatmo_weather import NetatmoWeatherPlugin

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Display dimensions (Inky Impression 5.7")
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

# Base template that InkyPi normally provides
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width={{ width }}, height={{ height }}">
    <title>Netatmo Weather Preview</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: {{ width }}px;
            height: {{ height }}px;
            overflow: hidden;
        }
    </style>
    <link rel="stylesheet" href="render/weather.css">
</head>
<body>
{% block content %}{% endblock %}
</body>
</html>
"""


class MockDeviceConfig:
    """Mock device config for standalone testing"""

    def __init__(self):
        # Try loading .env from multiple locations
        for env_path in [REPO_ROOT / '.env', SCRIPT_DIR / '.env']:
            if env_path.exists():
                load_dotenv(env_path)
                logger.info(f"Loaded environment from: {env_path}")
                break
        else:
            logger.warning("No .env file found")

    def load_env_key(self, key):
        return os.getenv(key)

    def get_config(self, key=None, default=None):
        config = {
            "width": DISPLAY_WIDTH,
            "height": DISPLAY_HEIGHT,
            "timezone": "America/New_York",
            "time_format": "12h"
        }
        if key:
            return config.get(key, default)
        return config


def fetch_weather_data(settings: dict) -> dict:
    """Fetch real weather data from APIs"""
    logger.info("Fetching weather data from APIs...")

    device_config = MockDeviceConfig()
    plugin = NetatmoWeatherPlugin({})

    # Initialize API clients and authenticate
    netatmo_client_id = device_config.load_env_key("NETATMO_CLIENT_ID")
    netatmo_client_secret = device_config.load_env_key("NETATMO_CLIENT_SECRET")
    netatmo_refresh_token = device_config.load_env_key("NETATMO_REFRESH_TOKEN")
    owm_api_key = device_config.load_env_key("OPEN_WEATHER_MAP_SECRET")

    # Validate credentials
    missing = []
    if not netatmo_client_id:
        missing.append("NETATMO_CLIENT_ID")
    if not netatmo_client_secret:
        missing.append("NETATMO_CLIENT_SECRET")
    if not netatmo_refresh_token:
        missing.append("NETATMO_REFRESH_TOKEN")
    if not owm_api_key:
        missing.append("OPEN_WEATHER_MAP_SECRET")

    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        logger.error("Please set these in your .env file")
        sys.exit(1)

    # Import and initialize clients
    from netatmo_weather import NetatmoClient, OpenWeatherMapClient

    plugin.netatmo = NetatmoClient(
        netatmo_client_id,
        netatmo_client_secret,
        refresh_token=netatmo_refresh_token
    )

    if not plugin.netatmo.refresh_access_token():
        logger.error("Failed to authenticate with Netatmo")
        sys.exit(1)

    plugin.owm = OpenWeatherMapClient(owm_api_key)

    # Load stations
    plugin.stations = plugin.netatmo.get_stations()
    if not plugin.stations:
        logger.error("No Netatmo stations found")
        sys.exit(1)

    logger.info(f"Found {len(plugin.stations)} station(s)")

    # Set config for data formatting
    plugin.config['units'] = settings.get('units', 'metric')
    plugin.config['forecast_days'] = settings.get('forecast_days', 5)

    # Fetch data
    plugin.update_data(force=True)

    # Get formatted render data
    render_data = plugin.get_render_data()
    render_data['units'] = settings.get('units', 'metric')
    render_data['forecast_days'] = settings.get('forecast_days', 5)
    render_data['plugin_settings'] = settings

    # Format last refresh time (matching InkyPi weather plugin format)
    timezone_str = settings.get('timezone', 'America/New_York')
    time_format = settings.get('time_format', '12h')
    try:
        tz = ZoneInfo(timezone_str)
    except Exception:
        tz = ZoneInfo("UTC")
    now = datetime.now(tz)
    if time_format == "24h":
        render_data["updated"] = now.strftime("%Y-%m-%d %H:%M")
    else:
        render_data["updated"] = now.strftime("%Y-%m-%d %I:%M %p")

    return render_data


def convert_svg_to_data_uri(svg_content: str) -> str:
    """Convert SVG content to data URI for inline embedding"""
    # Encode SVG content to base64
    encoded = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{encoded}"


def render_html(template_data: dict, output_path: Path) -> str:
    """Render the weather template to HTML"""
    logger.info("Rendering HTML template...")

    # Create a custom environment that handles the extends
    # by providing a mock plugin.html base template
    class PreviewLoader(BaseLoader):
        def __init__(self, template_dir):
            self.template_dir = Path(template_dir)

        def get_source(self, environment, template):
            if template == "plugin.html":
                return (BASE_TEMPLATE, "plugin.html", lambda: True)

            # Try render subdirectory first, then root
            for search_path in [self.template_dir / "render", self.template_dir]:
                path = search_path / template
                if path.exists():
                    with open(path) as f:
                        source = f.read()
                    return (source, str(path), lambda: True)

            raise Exception(f"Template not found: {template}")

    env = Environment(loader=PreviewLoader(SCRIPT_DIR))

    # Load and render the weather template
    template = env.get_template("weather.html")

    # Add display dimensions
    template_data['width'] = DISPLAY_WIDTH
    template_data['height'] = DISPLAY_HEIGHT

    html_content = template.render(**template_data)

    # For standalone HTML, we need to inline the CSS or use absolute path
    css_path = SCRIPT_DIR / "render" / "weather.css"
    with open(css_path) as f:
        css_content = f.read()

    # Convert icon paths to data URIs for standalone HTML
    icons_dir = SCRIPT_DIR / "render" / "icons"
    icon_replacements = {}
    if icons_dir.exists():
        for icon_file in icons_dir.glob("*.svg"):
            with open(icon_file, 'r') as f:
                svg_content = f.read()
            data_uri = convert_svg_to_data_uri(svg_content)
            icon_replacements[f'icons/{icon_file.name}'] = data_uri

    # Replace all icon src paths with data URIs
    for icon_path, data_uri in icon_replacements.items():
        html_content = html_content.replace(f'src="{icon_path}"', f'src="{data_uri}"')

    # Create standalone HTML with inlined CSS
    standalone_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width={DISPLAY_WIDTH}, height={DISPLAY_HEIGHT}">
    <title>Netatmo Weather Preview</title>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: {DISPLAY_WIDTH}px;
            height: {DISPLAY_HEIGHT}px;
            overflow: hidden;
        }}
        {css_content}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

    # Write HTML file
    with open(output_path, 'w') as f:
        f.write(standalone_html)

    logger.info(f"HTML saved to: {output_path}")
    return standalone_html


def render_png(html_path: Path, output_path: Path):
    """Render HTML to PNG using Playwright"""
    logger.info("Rendering PNG with Playwright...")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright not installed. Install with:")
        logger.error("  pip install playwright")
        logger.error("  playwright install chromium")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': DISPLAY_WIDTH, 'height': DISPLAY_HEIGHT})

        # Load the HTML file
        page.goto(f"file://{html_path.absolute()}")

        # Wait for fonts to load
        page.wait_for_load_state('networkidle')

        # Take screenshot
        page.screenshot(path=str(output_path), full_page=False)

        browser.close()

    logger.info(f"PNG saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Preview Netatmo Weather Plugin output')
    parser.add_argument('--html-only', action='store_true', help='Generate HTML only')
    parser.add_argument('--png-only', action='store_true', help='Generate PNG only')
    parser.add_argument('--units', choices=['metric', 'imperial'], default='metric',
                        help='Temperature units (default: metric)')
    parser.add_argument('--forecast-days', type=int, default=5, choices=[3, 5, 7],
                        help='Number of forecast days (default: 5)')
    parser.add_argument('--timezone', type=str, default='America/New_York',
                        help='Timezone for timestamp (default: America/New_York)')
    parser.add_argument('--time-format', choices=['12h', '24h'], default='12h',
                        help='Time format (default: 12h)')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Output directory for generated files')
    args = parser.parse_args()

    # Settings
    settings = {
        'units': args.units,
        'forecast_days': args.forecast_days,
        'station_index': 0,
        'timezone': args.timezone,
        'time_format': args.time_format
    }

    # Output paths
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_path = output_dir / f"preview_{timestamp}.html"
    png_path = output_dir / f"preview_{timestamp}.png"

    # Fetch data
    template_data = fetch_weather_data(settings)

    # Save raw data for debugging
    data_path = output_dir / f"preview_{timestamp}_data.json"
    with open(data_path, 'w') as f:
        json.dump(template_data, f, indent=2, default=str)
    logger.info(f"Data saved to: {data_path}")

    # Generate outputs
    generate_html = not args.png_only
    generate_png = not args.html_only

    if generate_html or generate_png:
        render_html(template_data, html_path)

    if generate_png:
        render_png(html_path, png_path)

    # Summary
    print("\n" + "=" * 50)
    print("Preview generated successfully!")
    print("=" * 50)
    if generate_html:
        print(f"  HTML: {html_path}")
    if generate_png:
        print(f"  PNG:  {png_path}")
    print(f"  Data: {data_path}")
    print("\nOpen the HTML in a browser or view the PNG to see the output.")


if __name__ == "__main__":
    main()

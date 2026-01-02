#!/usr/bin/env python3
"""
Netatmo Authorization Code Flow Helper

This script helps you authenticate with Netatmo using the OAuth2 Authorization Code flow.
Since Netatmo no longer supports Password grant for new apps, this is the proper way
to get your initial tokens.

This is a ONE-TIME setup. After you get the refresh token, you can use it indefinitely.

Usage:
    python3 netatmo_auth_flow.py

Steps:
1. Set up redirect URI in Netatmo app settings
2. Run this script
3. Open the URL in your browser
4. Authorize the app
5. Copy the refresh token to your .env file
"""

import os
import sys
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv

# Simple HTTP server to catch the OAuth callback
class CallbackHandler(BaseHTTPRequestHandler):
    authorization_code = None

    def do_GET(self):
        # Parse the callback URL
        query_components = parse_qs(urlparse(self.path).query)

        if 'code' in query_components:
            CallbackHandler.authorization_code = query_components['code'][0]

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = """
            <html>
            <head><title>Netatmo Authorization Successful</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">✅ Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            # Handle error
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            error = query_components.get('error', ['Unknown error'])[0]
            html = f"""
            <html>
            <head><title>Authorization Failed</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ Authorization Failed</h1>
                <p>Error: {error}</p>
                <p>Please try again or check your app configuration.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

    def log_message(self, format, *args):
        # Suppress log messages
        pass


def get_netatmo_tokens_via_oauth():
    """Guide user through OAuth2 Authorization Code flow"""

    print("="*70)
    print("Netatmo OAuth2 Authorization Code Flow")
    print("="*70)
    print()

    # Load environment
    load_dotenv()

    client_id = os.getenv("NETATMO_CLIENT_ID")
    client_secret = os.getenv("NETATMO_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("❌ ERROR: NETATMO_CLIENT_ID and NETATMO_CLIENT_SECRET must be set in .env")
        sys.exit(1)

    print(f"Client ID: {client_id[:10]}...")
    print()

    # Configuration
    REDIRECT_URI = "http://localhost:8080/callback"
    SCOPE = "read_station"

    print("STEP 1: Configure Redirect URI in Netatmo App")
    print("-" * 70)
    print("1. Go to: https://dev.netatmo.com/apps")
    print("2. Click on your app")
    print("3. Find 'Redirect URI' field")
    print(f"4. Add this redirect URI: {REDIRECT_URI}")
    print("5. Save the app")
    print()

    input("Press ENTER once you've added the redirect URI...")
    print()

    # Build authorization URL
    auth_params = {
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'state': 'netatmo_auth'  # CSRF protection
    }

    auth_url = f"https://api.netatmo.com/oauth2/authorize?{urlencode(auth_params)}"

    print("STEP 2: Authorize the Application")
    print("-" * 70)
    print("Opening authorization URL in your browser...")
    print()
    print(f"URL: {auth_url}")
    print()
    print("If the browser doesn't open automatically, copy the URL above")
    print("and paste it into your browser.")
    print()

    # Try to open browser
    try:
        webbrowser.open(auth_url)
    except:
        pass

    print("After authorizing, you'll be redirected back to this script.")
    print()

    # Start local server to catch callback
    print("STEP 3: Waiting for Authorization...")
    print("-" * 70)
    print("Starting local callback server on http://localhost:8080")
    print("Please complete the authorization in your browser...")
    print()

    try:
        server = HTTPServer(('localhost', 8080), CallbackHandler)
        server.handle_request()  # Wait for one request

        if not CallbackHandler.authorization_code:
            print("❌ ERROR: No authorization code received")
            sys.exit(1)

        print("✅ Authorization code received!")
        print()

    except OSError as e:
        print(f"❌ ERROR: Could not start callback server on port 8080")
        print(f"   {e}")
        print()
        print("Make sure port 8080 is not in use and try again.")
        sys.exit(1)

    # Exchange authorization code for tokens
    print("STEP 4: Exchanging Authorization Code for Tokens")
    print("-" * 70)

    try:
        response = requests.post(
            "https://api.netatmo.com/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": CallbackHandler.authorization_code,
                "redirect_uri": REDIRECT_URI,
                "scope": SCOPE
            }
        )

        response.raise_for_status()
        tokens = response.json()

        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        expires_in = tokens.get('expires_in', 3600)

        print("✅ Successfully obtained tokens!")
        print()
        print("="*70)
        print("SUCCESS! Save this refresh token to your .env file:")
        print("="*70)
        print()
        print(f"NETATMO_REFRESH_TOKEN={refresh_token}")
        print()
        print("="*70)
        print()
        print("IMPORTANT NEXT STEPS:")
        print("-" * 70)
        print("1. Add the line above to your .env file")
        print("2. You can now REMOVE NETATMO_USERNAME and NETATMO_PASSWORD")
        print("3. The plugin will use the refresh token automatically")
        print("4. The refresh token renews itself - it never expires")
        print()
        print("Your .env should have:")
        print("  NETATMO_CLIENT_ID=...")
        print("  NETATMO_CLIENT_SECRET=...")
        print("  NETATMO_REFRESH_TOKEN=...")
        print()

        # Test the tokens
        print("STEP 5: Testing Token (Optional)")
        print("-" * 70)
        test = input("Test the token by fetching your stations? (y/N) ")

        if test.lower() == 'y':
            print("Fetching stations...")
            try:
                stations_response = requests.post(
                    "https://api.netatmo.com/api/getstationsdata",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                stations_response.raise_for_status()
                data = stations_response.json()

                devices = data.get('body', {}).get('devices', [])
                print(f"✅ Found {len(devices)} station(s):")
                for device in devices:
                    name = device.get('station_name', 'Unknown')
                    print(f"   - {name}")
                print()
            except Exception as e:
                print(f"⚠️  Warning: Could not fetch stations: {e}")
                print("   But your refresh token should still work!")
                print()

        print("="*70)
        print("Setup complete! You can now use the plugin.")
        print("="*70)

        return True

    except requests.exceptions.HTTPError as e:
        print(f"❌ ERROR: Failed to exchange authorization code for tokens")
        print(f"   Status: {e.response.status_code}")
        try:
            print(f"   Response: {e.response.json()}")
        except:
            print(f"   Response: {e.response.text}")
        return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    print()
    print("This script will guide you through Netatmo OAuth2 authentication.")
    print("You'll need to authorize the app in your browser.")
    print()

    success = get_netatmo_tokens_via_oauth()
    sys.exit(0 if success else 1)

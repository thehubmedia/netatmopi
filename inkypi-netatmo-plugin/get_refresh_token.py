#!/usr/bin/env python3
"""
One-time script to obtain a Netatmo refresh token.

Run this on your development machine to get a refresh token that can be used
on the Raspberry Pi without storing your password.

Usage:
    python3 get_refresh_token.py

This will prompt for your Netatmo credentials and output a refresh token
that you can add to your Pi's .env file as NETATMO_REFRESH_TOKEN.
"""

import os
import sys
import getpass
import requests
from dotenv import load_dotenv

def get_refresh_token():
    """Authenticate with Netatmo and get a refresh token"""

    print("="*60)
    print("Netatmo Refresh Token Generator")
    print("="*60)
    print()
    print("This script will authenticate with Netatmo and provide a")
    print("refresh token that can be used instead of storing your password.")
    print()

    # Load environment for client ID/secret
    load_dotenv()

    # Get client credentials
    client_id = os.getenv("NETATMO_CLIENT_ID")
    client_secret = os.getenv("NETATMO_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: NETATMO_CLIENT_ID and NETATMO_CLIENT_SECRET must be set in .env")
        sys.exit(1)

    print(f"Client ID: {client_id[:10]}...")
    print()

    # Get username/password from user
    username = input("Netatmo Email: ").strip()
    password = getpass.getpass("Netatmo Password: ")

    if not username or not password:
        print("ERROR: Username and password are required")
        sys.exit(1)

    print()
    print("Authenticating with Netatmo...")

    # Authenticate
    try:
        response = requests.post(
            "https://api.netatmo.com/oauth2/token",
            data={
                "grant_type": "password",
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username,
                "password": password,
                "scope": "read_station"
            }
        )
        response.raise_for_status()
        data = response.json()

        refresh_token = data["refresh_token"]

        print()
        print("="*60)
        print("✅ SUCCESS! Authentication successful")
        print("="*60)
        print()
        print("Add this line to your .env file on the Raspberry Pi:")
        print()
        print(f"NETATMO_REFRESH_TOKEN={refresh_token}")
        print()
        print("="*60)
        print()
        print("IMPORTANT:")
        print("- You can now remove NETATMO_USERNAME and NETATMO_PASSWORD from .env")
        print("- The refresh token will automatically renew itself")
        print("- Keep this token secure - it provides access to your Netatmo data")
        print()

        return True

    except requests.exceptions.HTTPError as e:
        print()
        print(f"❌ ERROR: Authentication failed - {e}")
        print()
        print("Please check:")
        print("  - Your email and password are correct")
        print("  - Your Netatmo client ID and secret are valid")
        print("  - Your app has the 'read_station' scope enabled")
        return False

    except Exception as e:
        print()
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    success = get_refresh_token()
    sys.exit(0 if success else 1)

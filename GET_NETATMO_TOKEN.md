# How to Get Netatmo Refresh Token

Since new Netatmo apps don't support the "Password" grant type anymore, you need to use a refresh token instead. There are **two ways** to get one:

## Method 1: Use Netatmo's Token Generator (EASIEST!) ⭐

If you see a "Token Generator" in your Netatmo developer console:

1. Go to https://dev.netatmo.com/apps
2. Click on your app
3. Look for **"Token Generator"** or **"Generate Token"** button/section
4. Click it to generate tokens
5. Copy the **Refresh Token** (NOT the Access Token)
6. Add it to your `.env` file:

```bash
NETATMO_REFRESH_TOKEN=your_refresh_token_here
```

That's it! The plugin will use this token automatically.

## Method 2: Use the OAuth2 Flow Script (If no token generator)

If you don't see a token generator in the console, use our helper script:

### Prerequisites

1. **Add Redirect URI** to your Netatmo app:
   - Go to https://dev.netatmo.com/apps
   - Click your app
   - Find "Redirect URI" field
   - Add: `http://localhost:8080/callback`
   - Save

### Run the Script

```bash
cd inkypi-netatmo-plugin
python3 netatmo_auth_flow.py
```

This will:
1. Open your browser to authorize the app
2. Catch the authorization code
3. Exchange it for tokens
4. Display your refresh token

Copy the refresh token to your `.env` file.

## What to Put in .env

After getting your refresh token, your `.env` should have:

```bash
# OpenWeatherMap
OPEN_WEATHER_MAP_SECRET=your_owm_api_key

# Netatmo - NEW METHOD (refresh token only)
NETATMO_CLIENT_ID=your_client_id
NETATMO_CLIENT_SECRET=your_client_secret
NETATMO_REFRESH_TOKEN=your_refresh_token_from_above

# You can REMOVE these (no longer needed):
# NETATMO_USERNAME=...
# NETATMO_PASSWORD=...
```

## Testing

After adding the refresh token:

```bash
cd inkypi-netatmo-plugin
python3 test_apis.py
```

You should see:
```
✅ Authentication successful!
✅ Found X station(s)
```

## How It Works

- The **access token** expires after ~3 hours
- The **refresh token** never expires (but can be revoked)
- The plugin automatically uses the refresh token to get new access tokens
- You never need to re-authenticate manually

## Troubleshooting

### "Invalid refresh token"

The token may have been revoked. Generate a new one using either method above.

### "No token generator in console"

Use Method 2 (OAuth2 flow script). Some Netatmo apps don't have the token generator feature.

### "Redirect URI mismatch"

Make sure you added `http://localhost:8080/callback` to your app's Redirect URI settings.

## Security Note

The refresh token provides access to your Netatmo data. Keep it secure:
- Don't commit it to git (it's in .gitignore)
- Don't share it publicly
- You can revoke it anytime from https://dev.netatmo.com/

However, it's much more secure than storing your username/password!

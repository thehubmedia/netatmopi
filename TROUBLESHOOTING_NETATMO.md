# Troubleshooting Netatmo 403 Forbidden Error

## Common Causes

When you get a `403 Forbidden` error from Netatmo's API, it's usually one of these issues:

### 1. App Not Activated ⚠️ MOST COMMON

Netatmo requires you to **activate your app** before it can be used:

1. Go to https://dev.netatmo.com/apps
2. Find your app
3. Look for an "Activate" or "Submit for Activation" button
4. **Apps must be activated before they work** (even for personal use)

**Status Check**: Make sure your app shows as "Active" or "Validated"

### 2. Incorrect Scope

Your app needs the `read_station` scope enabled:

1. Go to https://dev.netatmo.com/apps
2. Edit your app
3. Under "Scopes" or "Permissions", ensure **"read_station"** is checked
4. Save changes

### 3. Wrong Grant Type

Netatmo has deprecated the "Resource Owner Password Credentials" flow for new apps.

**If your app was created recently (2024+)**, you may need to use the Authorization Code flow instead.

### 4. Client ID/Secret Mismatch

Double-check:
- Client ID is copied correctly (no extra spaces)
- Client Secret is copied correctly
- You're using credentials from the same app

## Quick Fixes to Try

### Fix 1: Verify App Status

```bash
# Check your app at:
https://dev.netatmo.com/apps

# Look for:
- Status: "Active" or "Validated" (NOT "Pending" or "Draft")
- Token Generation Method: Should include "Password"
- Scope: "read_station" should be enabled
```

### Fix 2: Recreate the App

If your app is old or has wrong settings:

1. Go to https://dev.netatmo.com/apps
2. Click "Create"
3. Fill in:
   - **App Name**: (anything, e.g., "My Weather Station")
   - **Description**: "Personal weather display"
   - **Data Protection Officer**: Your email
4. **Token Generation Method**:
   - Check **"Authorization Code"**
   - Check **"Password"** (if available)
5. **Scopes**: Check **"read_station"**
6. Save and **activate** the app
7. Copy the new Client ID and Client Secret to your `.env`

### Fix 3: Use Authorization Code Flow (Advanced)

If Password flow is disabled for your app, you'll need to use OAuth Authorization Code flow:

This requires:
1. Setting up a redirect URI
2. Getting an authorization code via web browser
3. Exchanging it for tokens

(This is more complex - let me know if you need help with this)

## Testing Your Fix

After making changes, test again:

```bash
cd inkypi-netatmo-plugin
python3 test_apis.py
```

You should see:
```
✅ Authentication successful!
✅ Found X station(s)
```

## Still Not Working?

### Check Netatmo API Status

Visit: https://dev.netatmo.com/

Look for any service status warnings or maintenance notices.

### Enable Debug Logging

Edit `test_apis.py` to see the full error response:

```python
# Around line 30, add this after the failed request:
except requests.exceptions.HTTPError as e:
    print(f"Status Code: {e.response.status_code}")
    print(f"Response: {e.response.text}")  # ADD THIS LINE
    logger.error(f"Netatmo authentication failed: {e}")
```

Run again and share the full response text - it will tell us exactly why Netatmo is rejecting the request.

### Contact Netatmo Support

If none of the above works:
1. Go to https://dev.netatmo.com/
2. Click "Support" or "Contact"
3. Ask: "Why is my app getting 403 Forbidden on /oauth2/token?"
4. Provide your Client ID (but NOT your secret)

## Alternative: Test with Netatmo's API Explorer

Netatmo has a web-based API explorer:

1. Go to https://dev.netatmo.com/
2. Find "API Documentation" or "Try the API"
3. Authenticate there first
4. If it works in the explorer but not in your code, the issue is with your app configuration

## Next Steps

Let me know:
1. Is your app status "Active"?
2. Does it have both "Password" and "Authorization Code" grant types?
3. Is "read_station" scope enabled?
4. What does the full error response say (if you added debug logging)?

I can help you set up the Authorization Code flow if needed!

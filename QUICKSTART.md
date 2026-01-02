# Quick Start Guide

This guide will help you get the Netatmo Weather Plugin up and running quickly.

## Prerequisites Checklist

- [ ] Raspberry Pi with InkyPi installed and working
- [ ] Netatmo Weather Station online and accessible
- [ ] Netatmo Developer App created (client ID & secret)
- [ ] OpenWeatherMap API key with One Call API 3.0 access

## Step 1: Configure Credentials (On Your Dev Machine)

You have **two options** for Netatmo authentication:

### Option A: Username/Password (Simpler) ✅ RECOMMENDED

Edit the `.env` file and add your Netatmo credentials:

```bash
# .env file
OPEN_WEATHER_MAP_SECRET=your_owm_api_key
NETATMO_CLIENT_ID=your_client_id
NETATMO_CLIENT_SECRET=your_client_secret
NETATMO_USERNAME=your_netatmo_email@example.com
NETATMO_PASSWORD=your_netatmo_password
```

**Pros**: Simple, works automatically
**Cons**: Password stored in .env (same as all other API keys in InkyPi)

### Option B: Refresh Token Only (More Secure) 🔐

Generate a refresh token locally (no password on Pi):

```bash
cd inkypi-netatmo-plugin
pip3 install -r requirements.txt
python3 get_refresh_token.py
```

Follow the prompts, then add the output to `.env`:

```bash
# .env file
OPEN_WEATHER_MAP_SECRET=your_owm_api_key
NETATMO_CLIENT_ID=your_client_id
NETATMO_CLIENT_SECRET=your_client_secret
NETATMO_REFRESH_TOKEN=your_refresh_token_from_script
```

**Pros**: No password stored on Pi
**Cons**: Extra setup step required

## Step 2: Test APIs Locally (Optional but Recommended)

Before deploying to the Pi, test that your API credentials work:

```bash
cd inkypi-netatmo-plugin
pip3 install -r requirements.txt
python3 test_apis.py
```

You should see output like:

```
Testing Netatmo API Connection
✅ Authentication successful!
✅ Found 1 station(s)

Testing OpenWeatherMap API Connection
✅ Successfully fetched forecast!

Test Results Summary
Netatmo API: ✅ PASS
OpenWeatherMap API: ✅ PASS

🎉 All tests passed!
```

## Step 3: Deploy to Raspberry Pi

Run the deployment script:

```bash
./deploy.sh raspberrypi.local
# Or use IP address: ./deploy.sh 192.168.1.100
```

The script will:
- Copy all plugin files to the Pi
- Install Python dependencies
- Copy your `.env` file with credentials
- Optionally test the APIs on the Pi

## Step 4: Enable in InkyPi

1. Open InkyPi web interface (usually http://raspberrypi.local)
2. Go to Plugins section
3. Enable "Netatmo Weather" plugin
4. Configure refresh intervals if needed
5. Save and apply

## Step 5: Test on the Display

The display should now show:
- **Left panel**: Real-time Netatmo data
- **Right panel**: OpenWeatherMap forecast

Use the buttons to:
- Button 1/2: Cycle through stations (if you have multiple)
- Button 3: Force refresh
- Watch the LED flash during updates

## Troubleshooting

### "No stations found"

1. Check Netatmo credentials in `.env`
2. Verify station is online in Netatmo app
3. SSH to Pi and run: `cd ~/InkyPi/src/plugins/netatmo_weather && python3 test_apis.py`

### "OWM authentication failed"

1. Verify API key is correct
2. Check you're subscribed to One Call API 3.0
3. Visit: https://home.openweathermap.org/subscriptions

### Display not updating

1. Check InkyPi service: `systemctl status inkypi`
2. Check plugin logs in InkyPi
3. Verify network connectivity

## Manual Installation (Alternative to deploy.sh)

If the deployment script doesn't work, you can deploy manually:

```bash
# On your dev machine
scp -r inkypi-netatmo-plugin pi@raspberrypi.local:~/

# SSH to Pi
ssh pi@raspberrypi.local

# Move to InkyPi plugins directory
sudo mv ~/inkypi-netatmo-plugin /path/to/InkyPi/src/plugins/netatmo_weather

# Install dependencies
cd /path/to/InkyPi/src/plugins/netatmo_weather
pip3 install -r requirements.txt

# Copy .env file
scp your-dev-machine:.env .

# Test
python3 test_apis.py
```

## Next Steps

Once working, you can customize:

- Edit `config.yaml` to change units, forecast days, update intervals
- Modify `templates/netatmo_weather.html` to adjust layout
- Edit `static/netatmo_weather.css` to change styling
- Adjust `netatmo_weather.py` for different button behaviors

## Support

- InkyPi documentation: https://github.com/fatihak/InkyPi
- Netatmo API docs: https://dev.netatmo.com/
- OpenWeatherMap docs: https://openweathermap.org/api/one-call-3
- Issues: Check the logs in InkyPi web interface

---

**Happy Weather Watching!** 🌤️

# E-Ink Weather Dashboard w/ Netatmo Support

1. Runs on a Raspberry Pi (Newer Models)
1. Drives a Pomoroni Inky Impressions Display 2025 edition (either 7.3" or 13.3")
1. Pulls Forecast data from the OpenWeatherMap API (paid subscription required, but free for the first 1000 calls)
1. Pulls your local actual weather from Netatmo
1. Updates the Netatmo on a schedule (e.g. every 5 minutes)
1. Updates the OpenWeatherMap forecast on a separate schedule (e.g. every 2 hours)
1. The main display would show forecast from OWM while realtime from Netatmo.
    1. For speed/efficiency, ideally it would do partial screen updates
    1. Changing Netatmo stations with buttons would change OWM forecast based on station location
1. Supports the buttons of the InkyImpressions display
    1. Cycle through Netatmo Stations you have access too
    1. Do a full update of everything
1. When fetching data & updating, flash the LED that InkyImpressions 2025 editions have.

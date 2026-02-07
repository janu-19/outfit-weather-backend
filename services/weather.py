import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

def get_weather(city=None, lat=None, lon=None):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    # Graceful fallback instead of crash
    if not API_KEY:
        print("WARNING: OPENWEATHER_API_KEY is not set. Returning default/empty weather data.")
        return 20, 0, {
            "humidity": None, "clouds": None, "description": "Unknown",
            "sun_exposure": "Unknown", "min_temp": 20, "max_temp": 20, 
            "daily_rain_prob": 0
        }
    
    city = city.strip() if city else ""

    # Default fallback details
    default_details = {
        "humidity": None, 
        "clouds": None, 
        "description": "Unknown", 
        "sun_exposure": "Unknown",
        "min_temp": 20,
        "max_temp": 20,
        "daily_rain_prob": 0
    }

    # If coordinates provided, prefer them
    if lat is not None and lon is not None:
        source = f"lat={lat}, lon={lon}"
    elif not city:
        print("City name is empty and no coordinates provided")
        return 20, 0, default_details
    else:
        source = city

    # Use 5 day / 3 hour forecast to get daily min/max
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "appid": API_KEY,
        "units": "metric"
    }
    if lat is not None and lon is not None:
        params.update({"lat": lat, "lon": lon})
    else:
        params.update({"q": city})

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if response.status_code != 200:
            print(f"Weather API error for {source}: {data}")
            return 20, 0, default_details

        # Get current items for today (approximate by taking first 8 intervals = 24h)
        # Or better: filter by date.
        
        forecast_list = data.get("list", [])
        if not forecast_list:
            return 20, 0, default_details

        # Current weather is roughly the first item
        current = forecast_list[0]
        current_temp = current.get("main", {}).get("temp", 20)
        current_humidity = current.get("main", {}).get("humidity")
        current_clouds = current.get("clouds", {}).get("all")
        current_desc = current.get("weather", [{}])[0].get("description", "Unknown")

        # Calculate daily min/max and rain prob from the next 24h (8 items)
        next_24h = forecast_list[:8]
        temps = [item.get("main", {}).get("temp") for item in next_24h]
        min_temp = min(temps)
        max_temp = max(temps)
        
        # Rain probability (pop is Probability of Precipitation)
        # Max pop in next 24h
        pops = [item.get("pop", 0) for item in next_24h]
        max_pop = max(pops)
        daily_rain_prob = max_pop * 100 # Convert to percentage

        # Determine overall rain volume (approx)
        total_rain_vol = 0
        for item in next_24h:
            rain_info = item.get("rain", {})
            total_rain_vol += rain_info.get("3h", 0)

        # Approximate sun exposure
        sun_exposure = "Unknown"
        try:
            if current_clouds is None:
                sun_exposure = "Unknown"
            elif current_clouds < 30 and current_temp >= 25:
                sun_exposure = "☀ Strong sun exposure"
            elif current_clouds < 50 and current_temp >= 20:
                sun_exposure = "☀ Moderate sun exposure"
            else:
                sun_exposure = "☁ Low sun exposure"
        except Exception:
            sun_exposure = "Unknown"

        # Humidity descriptor
        humidity_desc = None
        if current_humidity is not None:
            if current_humidity <= 40:
                humidity_desc = " Low humidity"
            elif current_humidity <= 70:
                humidity_desc = " Moderate humidity"
            else:
                humidity_desc = " High humidity"

        details = {
            "humidity": current_humidity,
            "humidity_desc": humidity_desc,
            "clouds": current_clouds,
            "description": current_desc,
            "sun_exposure": sun_exposure,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "daily_rain_prob": daily_rain_prob
        }

        print(f"Weather data for {source}: current={current_temp}, min={min_temp}, max={max_temp}, rain_prob={daily_rain_prob}%")
        
        # Return current_temp for main logic, but pass daily stats in details
        # Pass predicted rain (pop) as the main rain metric if it's high, or volume
        # The original code expected rain volume in mm? or boolean?
        # Original: rain = data.get("rain", {}).get("1h", 0) -> This is mm.
        # Let's return total_rain_vol for compatibility but use max_pop for advice.
        
        return current_temp, total_rain_vol, details

    except requests.exceptions.RequestException as e:
        print(f"Network error fetching weather for {city}: {e}")
        return 20, 0, default_details

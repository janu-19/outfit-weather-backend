import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_weather(city):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY environment variable is not set. Please create a .env file with your API key.")
    
    city = city.strip() if city else ""

    # Default fallback details
    default_details = {"humidity": None, "clouds": None, "description": "Unknown", "sun_exposure": "Unknown"}

    if not city:
        print("City name is empty")
        return 20, 0, default_details

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        #  API error (wrong city / invalid key / limit exceeded)
        if response.status_code != 200:
            print(f"Weather API error for {city}: {data}")
            return 20, 0, default_details

        temp = data.get("main", {}).get("temp", 20)
        rain = data.get("rain", {}).get("1h", 0)
        humidity = data.get("main", {}).get("humidity")
        clouds = data.get("clouds", {}).get("all")
        weather_desc = " ".join([w.get("description", "") for w in data.get("weather", [])]).strip() or data.get("weather", [{}])[0].get("main", "")

        # Approximate sun exposure from cloud cover and temperature
        sun_exposure = "Unknown"
        try:
            if clouds is None:
                sun_exposure = "Unknown"
            elif clouds < 30 and temp >= 25:
                sun_exposure = "☀ Strong sun exposure"
            elif clouds < 50 and temp >= 20:
                sun_exposure = "☀ Moderate sun exposure"
            else:
                sun_exposure = "☁ Low sun exposure"
        except Exception:
            sun_exposure = "Unknown"

        # Humidity descriptor
        humidity_desc = None
        if humidity is not None:
            if humidity <= 40:
                humidity_desc = " Low humidity"
            elif humidity <= 70:
                humidity_desc = " Moderate humidity"
            else:
                humidity_desc = " High humidity"

        details = {
            "humidity": humidity,
            "humidity_desc": humidity_desc,
            "clouds": clouds,
            "description": weather_desc,
            "sun_exposure": sun_exposure
        }

        print(f"Weather data for {city}: temp={temp}, rain={rain}, humidity={humidity}, clouds={clouds}")
        return temp, rain, details

    except requests.exceptions.RequestException as e:
        print(f"Network error fetching weather for {city}: {e}")
        return 20, 0, default_details

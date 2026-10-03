import requests


def current_weather(city: str):
    try:
        # 1. 根据城市名获取经纬度
        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

        geocoding_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        }

        response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        if "results" not in data or not data["results"]:
            return {
                "success": False,
                "error": "city_not_found",
            }

        location = data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        # 2. 根据经纬度获取天气
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m",
            "timezone": "auto",
        }

        response = requests.get(
            weather_url,
            params=weather_params,
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        current = data["current"]

        # 3. Tool Result
        return {
            "success": True,
            "data": {
                "city": city,
                "time": current["time"],
                "temperature": current["temperature_2m"],
                "temperature_unit": data["current_units"]["temperature_2m"],
                "wind_speed": current["wind_speed_10m"],
                "wind_speed_unit": data["current_units"]["wind_speed_10m"],
            },
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "timeout",
        }

    except requests.exceptions.HTTPError:
        return {
            "success": False,
            "error": "service_error",
        }
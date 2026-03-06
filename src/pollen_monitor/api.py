import os
import json
import requests
from dotenv import load_dotenv
from pollen_monitor.logger import logger

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BASE_URL = "https://pollen.googleapis.com/v1/forecast:lookup"

def get_pollen_forecast(latitude: float, longitude: float):
    try:
        # Check if API key is available
        if not GOOGLE_API_KEY:
            raise ValueError("Google API key is not set. Please check your .env file.")
        
        params = {
            "location.latitude": latitude,
            "location.longitude": longitude,
            "key": GOOGLE_API_KEY,
            "days": 1,
        }

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # This stops the code if the API call fails
        data = response.json()

        # Validation: Check if dailyInfo exists
        if not data.get("dailyInfo"):
            raise ValueError("API returned empty dailyInfo. Check coordinates or API status.")
        
        # Extracting UPI and Tree data from the first day's forecast
        daily_info = data.get("dailyInfo", [])[0]
        pollen_info = daily_info.get("pollenTypeInfo", [])

        if not pollen_info:
            raise ValueError("No pollenTypeInfo found in the API response.")

        # Initialize values
        pollen_data = {
            "tree": None,
            "grass": None,
            "weed": None
        }
        result = {
            "pollen_type": 'all',
            "pollen_level": 0,
            "pollen_data": pollen_data,
            "health_recommendations": None,
            "index_description": None,
        }

        for item in pollen_info:
            # Check if indexInfo actually exists before trying to access 'value'
            index_info = item.get("indexInfo")
            if not index_info:
                continue

            code = item.get("code", "").lower()
            entry = {
                "category": index_info.get("category", "N/A"),
                "value": index_info.get("value", "N/A"),
                "indexDescription": index_info.get("indexDescription", "N/A")
            }

            if item.get("code") == "TREE":
                result["pollen_level"] = index_info.get("value", 0)
                result["index_description"] = index_info.get("indexDescription", "N/A")

                health_recommendations = item.get("healthRecommendations")
                if health_recommendations:
                    result["health_recommendations"] = health_recommendations

            if code in pollen_data:
                pollen_data[code] = entry

        if pollen_data["tree"] is None:
            raise ValueError("Required pollen data (Tree) is missing in the API response.")

        return result
    except Exception as e:
        logger.error(f"Failed to fetch pollen data: {e}")
        raise
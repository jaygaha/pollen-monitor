import sys
import os
from pollen_monitor.api import get_pollen_forecast
from pollen_monitor.database import init_db, log_reading
from pollen_monitor.logger import logger
from pollen_monitor.notifier import send_slack_alert, compose_slack_message, send_email_alert
from pollen_monitor.monitor import check_threshold
from dotenv import load_dotenv

load_dotenv()

LAT, LON = float(os.getenv("LATITUDE", 35.63473023327269)), float(os.getenv("LONGITUDE", 139.72009180418843))
PLACE_NAME = os.getenv("PLACE_NAME", "Meguro, Tokyo")
THRESHOLD = int(os.getenv("THRESHOLD", 3))

"""
THRESHOLD VALUES:
0: "None"
1: "Very low"
2: "Low"
3: "Moderate"
4: "High"
5: "Very high"
"""


def run_monitor():
    try:
        # 1. Initialize DB
        init_db()
        
        # 2. Fetch Data
        print("📡 Fetching pollen levels...")
        data = get_pollen_forecast(LAT, LON)

        # 3. Check Threshold
        triggered = check_threshold(data["pollen_level"], THRESHOLD)
        
        if triggered:
            formatted_message = compose_slack_message(data, PLACE_NAME)
            send_slack_alert(formatted_message)

            # Alert user via email
            send_email_alert(data, PLACE_NAME)

            print(f"⚠️ ALERT: High pollen detected! UPI Index: {data['pollen_level']}")
        else:
            print(f"✅ Pollen levels are manageable. UPI Index: {data['pollen_level']}")
            logger.info(f"Pollen levels are manageable. UPI Index: {data['pollen_level']}")

        # 4. Log to Database
        log_reading(LAT, LON, data["pollen_type"], data["pollen_level"], data["pollen_data"], data["health_recommendations"], data["index_description"], triggered)
    except Exception as e:
        print(f"[ERROR]: {e}")
        logger.error(f"An error occurred while running the monitor: {e}")
        sys.exit(1) # Stop the program with an error code    

if __name__ == "__main__":
    run_monitor()
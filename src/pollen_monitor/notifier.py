import requests
import os
import json
from dotenv import load_dotenv
from pollen_monitor.logger import logger

load_dotenv()

def send_slack_alert(message):
    """Sends an alert message to Slack using a webhook."""

    try:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")

        if not webhook_url:
            raise ValueError("Slack webhook URL is not set. Skipping Slack alert. Please check your .env file.")

        payload = {
            "text": message
        }
        try:
            response = requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            logger.info("Slack alert sent successfully.")
        except Exception as e:
            raise ValueError(f"Failed to send Slack alert: {e}")

    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
        raise


def compose_slack_message(data, place_name):
    """Composes a message string for Slack based on the pollen data."""
    try:
        pollen_type = data.get("pollen_type", "Unknown")
        pollen_level = data.get("pollen_level", "Unknown")
        index_description = data.get("index_description", "No description available.")
        health_recommendations = data.get("health_recommendations", "No recommendations available.")

        status_emoji = "🚨🦠" if isinstance(pollen_level, (int, float)) and pollen_level >= 4 else "🟡"
        formatted_health_recommendations = ""

        # health_recommendations from Google API is a dict with keys like
        # "recommendedOutdoorActivities", "allergicSymptoms", etc.
        if isinstance(health_recommendations, dict):
            for value in health_recommendations.values():
                if value:
                    formatted_health_recommendations += f"\n- {value}"
        elif isinstance(health_recommendations, list):
            for recommendation in health_recommendations:
                formatted_health_recommendations += f"\n- {recommendation}"

        if not formatted_health_recommendations:
            formatted_health_recommendations = "No recommendations available."

        message = (
            f"{status_emoji} *POLLEN ALERT!·花粉注意報!*\n"
            f"*Location:* {place_name}\n"
            f"*Universal Index (UPI):* {pollen_level}\n"
            f"*Description:*\n"
            f"{index_description}\n\n"
            f"*Health Recommendations:*\n"
            f"{formatted_health_recommendations}\n"
        )
        return message

    except Exception as e:
        logger.error(f"Failed to compose Slack message: {e}")
        raise
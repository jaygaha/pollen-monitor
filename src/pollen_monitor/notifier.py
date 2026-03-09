import requests
import os
import json
import resend
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

def send_email_alert(data, place_name):
    """Sends an email alert using the Resend API."""
    try:
        api_key = os.getenv("RESEND_API_KEY")

        if not api_key:
            raise ValueError("Resend API key is not set. Skipping email alert. Please check your .env file.")

        payload = {
            "from": "Pollen Monitor <notifications@contact.jaygaha.com.np>",
            "to": ["jaygaha@gmail.com"],
            "subject": f"Pollen Alert for {place_name}",
            "html": compose_email_body(data, place_name)
        }   
        try:
            resend.Emails.send(payload)
            logger.info("Email alert sent successfully.")
        except Exception as e:
            raise ValueError(f"Failed to send email alert: {e}")
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")
        raise

def _get_severity(pollen_level):
    """Returns (label, accent_color) based on pollen level."""
    if not isinstance(pollen_level, (int, float)):
        return "Unknown", "#888888"
    levels = {
        0: ("None", "#4CAF50"),
        1: ("Very Low", "#8BC34A"),
        2: ("Low", "#FFC107"),
        3: ("Moderate", "#FF9800"),
        4: ("High", "#F44336"),
        5: ("Very High", "#B71C1C"),
    }
    return levels.get(int(pollen_level), ("Unknown", "#888888"))


def compose_email_body(data, place_name):
    """Composes the HTML body for the email alert based on the pollen data."""
    try:
        pollen_level = data.get("pollen_level", "Unknown")
        index_description = data.get("index_description", "No description available.")
        health_recommendations = data.get("health_recommendations", None)
        severity_label, accent_color = _get_severity(pollen_level)

        rec_items = ""
        if isinstance(health_recommendations, dict):
            for value in health_recommendations.values():
                if value:
                    rec_items += (
                        f'<li style="margin-bottom:6px;color:#444;">{value}</li>'
                    )
        elif isinstance(health_recommendations, list):
            for rec in health_recommendations:
                rec_items += (
                    f'<li style="margin-bottom:6px;color:#444;">{rec}</li>'
                )

        if not rec_items:
            rec_items = '<li style="color:#888;">No recommendations available.</li>'

        return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="padding:32px 16px;">
    <tr><td align="center">
      <table role="presentation" width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;">

        <!-- Accent bar -->
        <tr><td style="height:6px;background:{accent_color};"></td></tr>

        <!-- Header -->
        <tr><td style="padding:28px 32px 0;">
          <h1 style="margin:0;font-size:22px;font-weight:600;color:#111;">
            Pollen Alert &middot; {place_name}
          </h1>
        </td></tr>

        <!-- UPI Badge -->
        <tr><td style="padding:20px 32px;">
          <table role="presentation" cellpadding="0" cellspacing="0"><tr>
            <td style="background:{accent_color};color:#fff;font-size:28px;font-weight:700;width:56px;height:56px;text-align:center;border-radius:10px;vertical-align:middle;">
              {pollen_level}
            </td>
            <td style="padding-left:16px;">
              <div style="font-size:15px;font-weight:600;color:#111;">{severity_label}</div>
              <div style="font-size:13px;color:#666;margin-top:2px;">Universal Pollen Index (UPI)</div>
            </td>
          </tr></table>
        </td></tr>

        <!-- Divider -->
        <tr><td style="padding:0 32px;"><hr style="border:none;border-top:1px solid #e5e7eb;margin:0;"></td></tr>

        <!-- Description -->
        <tr><td style="padding:20px 32px 0;">
          <div style="font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;color:#888;margin-bottom:6px;">Description</div>
          <div style="font-size:14px;line-height:1.6;color:#333;">{index_description}</div>
        </td></tr>

        <!-- Recommendations -->
        <tr><td style="padding:20px 32px 28px;">
          <div style="font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;color:#888;margin-bottom:8px;">Health Recommendations</div>
          <ul style="margin:0;padding-left:18px;font-size:14px;line-height:1.6;">
            {rec_items}
          </ul>
        </td></tr>

      </table>

      <!-- Footer -->
      <p style="margin:20px 0 0;font-size:11px;color:#999;text-align:center;">
        Pollen Monitor &middot; Data from Google Pollen API
      </p>
    </td></tr>
  </table>
</body>
</html>"""

    except Exception as e:
        logger.error(f"Failed to compose email body: {e}")
        raise
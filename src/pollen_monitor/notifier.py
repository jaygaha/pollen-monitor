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

        # If message is a dict (blocks), use it directly; otherwise, wrap in text
        if isinstance(message, dict):
            payload = message
        else:
            payload = {"text": message}

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
    """Composes a Slack message using blocks for rich formatting based on the pollen data."""
    try:
        pollen_level = data.get("pollen_level", "Unknown")
        index_description = data.get("index_description", "No description available.")
        health_recommendations = data.get("health_recommendations", "No recommendations available.")

        severity_label, accent_color = _get_severity(pollen_level)

        # Determine status emoji
        status_emoji = "🚨🦠" if isinstance(pollen_level, (int, float)) and pollen_level >= 4 else "🟡"
        status_image_url = "https://images.unsplash.com/vector-1740290028324-039b4d12e2b8?q=80&w=120&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" if isinstance(pollen_level, (int, float)) and pollen_level >= 4 else "https://images.unsplash.com/vector-1740290028314-db647d27d397?q=80&w=120&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

        # Format health recommendations
        formatted_health_recommendations = ""
        if isinstance(health_recommendations, dict):
            for value in health_recommendations.values():
                if value:
                    formatted_health_recommendations += f"• {value}\n"
        elif isinstance(health_recommendations, list):
            for recommendation in health_recommendations:
                formatted_health_recommendations += f"• {recommendation}\n"

        if not formatted_health_recommendations:
            formatted_health_recommendations = "No recommendations available."

        # Build Slack blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{status_emoji} POLLEN ALERT! · 花粉注意報!"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Location:*\n{place_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Universal Index (UPI):*\n{pollen_level} ({severity_label})"
                    }
                ],
                "accessory": {
				"type": "image",
				"image_url": f"{status_image_url}",
				"alt_text": f"{severity_label}"
			}
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{index_description}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Health Recommendations:*\n{formatted_health_recommendations}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Pollen Monitor · Data from Google Pollen API"
                    }
                ]
            }
        ]

        return {"blocks": blocks}

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
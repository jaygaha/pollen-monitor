import pytest
from unittest.mock import patch, MagicMock
from pollen_monitor.notifier import (
    compose_slack_message,
    send_slack_alert,
    compose_email_body,
    send_email_alert,
    _get_severity,
)


class TestComposeSlackMessage:

    def test_moderate_pollen_uses_yellow_emoji(self):
        data = {
            "pollen_type": "all",
            "pollen_level": 3,
            "index_description": "Moderate pollen.",
            "health_recommendations": {
                "allergicSymptoms": "Wear a mask.",
            },
        }
        msg = compose_slack_message(data, "Tokyo, Japan")
        assert "🟡" in msg["blocks"][0]["text"]["text"]
        assert "Tokyo, Japan" in str(msg)
        assert "Wear a mask." in msg["blocks"][4]["text"]["text"]

    def test_high_pollen_uses_alert_emoji(self):
        data = {
            "pollen_type": "all",
            "pollen_level": 5,
            "index_description": "Very high pollen.",
            "health_recommendations": {"tip": "Stay indoors."},
        }
        msg = compose_slack_message(data, "Osaka")
        assert "🚨🦠" in msg["blocks"][0]["text"]["text"]

    def test_health_recommendations_as_dict(self):
        data = {
            "pollen_type": "all",
            "pollen_level": 4,
            "index_description": "High",
            "health_recommendations": {
                "outdoorActivities": "Limit time outside.",
                "allergicSymptoms": "Take antihistamines.",
            },
        }
        msg = compose_slack_message(data, "Shibuya")
        health_text = msg["blocks"][4]["text"]["text"]
        assert "Limit time outside." in health_text
        assert "Take antihistamines." in health_text

    def test_health_recommendations_as_list(self):
        data = {
            "pollen_type": "all",
            "pollen_level": 3,
            "index_description": "Moderate",
            "health_recommendations": ["Wear a mask.", "Close windows."],
        }
        msg = compose_slack_message(data, "Meguro")
        health_text = msg["blocks"][4]["text"]["text"]
        assert "Wear a mask." in health_text
        assert "Close windows." in health_text

    def test_no_health_recommendations(self):
        data = {
            "pollen_type": "all",
            "pollen_level": 1,
            "index_description": "Low",
            "health_recommendations": None,
        }
        msg = compose_slack_message(data, "Shinagawa")
        health_text = msg["blocks"][4]["text"]["text"]
        assert "No recommendations available." in health_text

    def test_missing_fields_use_defaults(self):
        msg = compose_slack_message({}, "Test")
        assert "Test" in str(msg)
        desc_text = msg["blocks"][3]["text"]["text"]
        assert "No description available." in desc_text


class TestSendSlackAlert:

    @patch("pollen_monitor.notifier.os.getenv", return_value=None)
    def test_missing_webhook_url_raises(self, mock_env):
        with pytest.raises(ValueError, match="Slack webhook URL is not set"):
            send_slack_alert("test message")

    @patch("pollen_monitor.notifier.os.getenv", return_value="https://hooks.slack.com/test")
    @patch("pollen_monitor.notifier.requests.post")
    def test_successful_send(self, mock_post, mock_env):
        mock_post.return_value.raise_for_status = MagicMock()
        send_slack_alert("test")
        mock_post.assert_called_once()

    @patch("pollen_monitor.notifier.os.getenv", return_value="https://hooks.slack.com/test")
    @patch("pollen_monitor.notifier.requests.post")
    def test_http_error_raises(self, mock_post, mock_env):
        import requests as req
        mock_post.return_value.raise_for_status.side_effect = req.exceptions.HTTPError("403")
        with pytest.raises(ValueError, match="Failed to send Slack alert"):
            send_slack_alert("test")


class TestGetSeverity:

    def test_level_0(self):
        assert _get_severity(0) == ("None", "#4CAF50")

    def test_level_3(self):
        assert _get_severity(3) == ("Moderate", "#FF9800")

    def test_level_5(self):
        assert _get_severity(5) == ("Very High", "#B71C1C")

    def test_non_numeric(self):
        label, _ = _get_severity("Unknown")
        assert label == "Unknown"


class TestComposeEmailBody:

    def test_contains_place_name(self):
        data = {"pollen_level": 3, "index_description": "Moderate"}
        html = compose_email_body(data, "Tokyo")
        assert "Tokyo" in html

    def test_severity_color_in_output(self):
        data = {"pollen_level": 5, "index_description": "Very high"}
        html = compose_email_body(data, "Osaka")
        assert "#B71C1C" in html  # Very High accent color

    def test_health_recs_dict_rendered(self):
        data = {
            "pollen_level": 4,
            "index_description": "High",
            "health_recommendations": {"tip": "Stay indoors."},
        }
        html = compose_email_body(data, "Shibuya")
        assert "Stay indoors." in html

    def test_health_recs_list_rendered(self):
        data = {
            "pollen_level": 3,
            "index_description": "Moderate",
            "health_recommendations": ["Wear a mask.", "Close windows."],
        }
        html = compose_email_body(data, "Meguro")
        assert "Wear a mask." in html
        assert "Close windows." in html

    def test_no_health_recs_fallback(self):
        data = {"pollen_level": 1, "index_description": "Low"}
        html = compose_email_body(data, "Shinagawa")
        assert "No recommendations available." in html

    def test_valid_html_structure(self):
        data = {"pollen_level": 3, "index_description": "Moderate"}
        html = compose_email_body(data, "Test")
        assert html.strip().startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_uses_inline_styles(self):
        """Ensure no <style> block (email clients strip them)."""
        data = {"pollen_level": 3, "index_description": "Moderate"}
        html = compose_email_body(data, "Test")
        assert "<style>" not in html


class TestSendEmailAlert:

    @patch("pollen_monitor.notifier.os.getenv", return_value=None)
    def test_missing_api_key_raises(self, mock_env):
        with pytest.raises(ValueError, match="Resend API key is not set"):
            send_email_alert({}, "Tokyo")

    @patch("pollen_monitor.notifier.compose_email_body", return_value="<html></html>")
    @patch("pollen_monitor.notifier.resend.Emails.send")
    @patch("pollen_monitor.notifier.os.getenv", return_value="re_test_key")
    def test_successful_send(self, mock_env, mock_send, mock_compose):
        send_email_alert({"pollen_level": 3}, "Tokyo")
        mock_send.assert_called_once()

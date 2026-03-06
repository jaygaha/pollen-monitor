import pytest
from unittest.mock import patch, MagicMock
from pollen_monitor.notifier import compose_slack_message, send_slack_alert


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
        assert "🟡" in msg
        assert "Tokyo, Japan" in msg
        assert "Wear a mask." in msg

    def test_high_pollen_uses_alert_emoji(self):
        data = {
            "pollen_type": "all",
            "pollen_level": 5,
            "index_description": "Very high pollen.",
            "health_recommendations": {"tip": "Stay indoors."},
        }
        msg = compose_slack_message(data, "Osaka")
        assert "🚨🦠" in msg

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
        assert "Limit time outside." in msg
        assert "Take antihistamines." in msg

    def test_health_recommendations_as_list(self):
        data = {
            "pollen_type": "all",
            "pollen_level": 3,
            "index_description": "Moderate",
            "health_recommendations": ["Wear a mask.", "Close windows."],
        }
        msg = compose_slack_message(data, "Meguro")
        assert "Wear a mask." in msg
        assert "Close windows." in msg

    def test_no_health_recommendations(self):
        data = {
            "pollen_type": "all",
            "pollen_level": 1,
            "index_description": "Low",
            "health_recommendations": None,
        }
        msg = compose_slack_message(data, "Shinagawa")
        assert "No recommendations available." in msg

    def test_missing_fields_use_defaults(self):
        msg = compose_slack_message({}, "Test")
        assert "Test" in msg
        assert "No description available." in msg


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

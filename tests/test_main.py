import pytest
from unittest.mock import patch


class TestRunMonitor:

    @patch("pollen_monitor.main.send_slack_alert")
    @patch("pollen_monitor.main.compose_slack_message", return_value="alert!")
    @patch("pollen_monitor.main.send_email_alert")
    @patch("pollen_monitor.main.log_reading")
    @patch("pollen_monitor.main.init_db")
    @patch("pollen_monitor.main.get_pollen_forecast")
    def test_triggers_alert_when_above_threshold(self, mock_fetch, mock_init, mock_log, mock_email, mock_compose, mock_slack):
        mock_fetch.return_value = {
            "pollen_level": 4,
            "pollen_type": "all",
            "pollen_data": {},
            "health_recommendations": None,
            "index_description": "High",
        }

        with patch("pollen_monitor.main.THRESHOLD", 3):
            from pollen_monitor.main import run_monitor
            run_monitor()

        mock_slack.assert_called_once_with("alert!")
        mock_email.assert_called_once()
        mock_log.assert_called_once()

    @patch("pollen_monitor.main.send_slack_alert")
    @patch("pollen_monitor.main.log_reading")
    @patch("pollen_monitor.main.init_db")
    @patch("pollen_monitor.main.get_pollen_forecast")
    def test_no_alert_when_below_threshold(self, mock_fetch, mock_init, mock_log, mock_slack):
        mock_fetch.return_value = {
            "pollen_level": 1,
            "pollen_type": "all",
            "pollen_data": {},
            "health_recommendations": None,
            "index_description": "Low",
        }

        with patch("pollen_monitor.main.THRESHOLD", 3):
            from pollen_monitor.main import run_monitor
            run_monitor()

        mock_slack.assert_not_called()
        mock_log.assert_called_once()

    @patch("pollen_monitor.main.init_db")
    @patch("pollen_monitor.main.get_pollen_forecast", side_effect=Exception("API down"))
    def test_exits_on_error(self, mock_fetch, mock_init):
        from pollen_monitor.main import run_monitor
        with pytest.raises(SystemExit):
            run_monitor()

import pytest
from unittest.mock import patch, MagicMock

from tests.conftest import make_api_response


class TestGetPollenForecast:

    @patch("pollen_monitor.api.GOOGLE_API_KEY", "fake-key")
    @patch("pollen_monitor.api.requests.get")
    def test_successful_fetch(self, mock_get, sample_api_response):
        mock_response = MagicMock()
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from pollen_monitor.api import get_pollen_forecast
        result = get_pollen_forecast(35.6, 139.7)

        assert result["pollen_level"] == 3
        assert result["pollen_type"] == "all"
        assert result["pollen_data"]["tree"] is not None
        assert result["pollen_data"]["grass"] is not None
        assert result["pollen_data"]["weed"] is not None
        assert result["index_description"] == "Tree pollen is moderate."
        assert result["health_recommendations"] is not None

    @patch("pollen_monitor.api.GOOGLE_API_KEY", "fake-key")
    @patch("pollen_monitor.api.requests.get")
    def test_high_pollen_level(self, mock_get, high_pollen_api_response):
        mock_response = MagicMock()
        mock_response.json.return_value = high_pollen_api_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from pollen_monitor.api import get_pollen_forecast
        result = get_pollen_forecast(35.6, 139.7)

        assert result["pollen_level"] == 5

    @patch("pollen_monitor.api.GOOGLE_API_KEY", None)
    def test_missing_api_key(self):
        from pollen_monitor.api import get_pollen_forecast
        with pytest.raises(ValueError, match="Google API key is not set"):
            get_pollen_forecast(35.6, 139.7)

    @patch("pollen_monitor.api.GOOGLE_API_KEY", "fake-key")
    @patch("pollen_monitor.api.requests.get")
    def test_empty_daily_info(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"dailyInfo": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from pollen_monitor.api import get_pollen_forecast
        with pytest.raises(ValueError, match="empty dailyInfo"):
            get_pollen_forecast(35.6, 139.7)

    @patch("pollen_monitor.api.GOOGLE_API_KEY", "fake-key")
    @patch("pollen_monitor.api.requests.get")
    def test_missing_pollen_type_info(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "dailyInfo": [{"date": {}, "pollenTypeInfo": []}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from pollen_monitor.api import get_pollen_forecast
        with pytest.raises(ValueError, match="No pollenTypeInfo"):
            get_pollen_forecast(35.6, 139.7)

    @patch("pollen_monitor.api.GOOGLE_API_KEY", "fake-key")
    @patch("pollen_monitor.api.requests.get")
    def test_missing_tree_data(self, mock_get):
        """API response has grass/weed but no tree data."""
        response_data = make_api_response(tree_value=None)
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from pollen_monitor.api import get_pollen_forecast
        with pytest.raises(ValueError, match="Required pollen data.*Tree"):
            get_pollen_forecast(35.6, 139.7)

    @patch("pollen_monitor.api.GOOGLE_API_KEY", "fake-key")
    @patch("pollen_monitor.api.requests.get")
    def test_pollen_data_accumulates_all_types(self, mock_get, sample_api_response):
        """Verify all pollen types are accumulated, not overwritten."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from pollen_monitor.api import get_pollen_forecast
        result = get_pollen_forecast(35.6, 139.7)

        assert result["pollen_data"]["tree"]["value"] == 3
        assert result["pollen_data"]["grass"]["value"] == 1
        assert result["pollen_data"]["weed"]["value"] == 0

    @patch("pollen_monitor.api.GOOGLE_API_KEY", "fake-key")
    @patch("pollen_monitor.api.requests.get")
    def test_item_without_index_info_skipped(self, mock_get):
        """Pollen type entries missing indexInfo should be skipped."""
        response_data = {
            "dailyInfo": [{
                "pollenTypeInfo": [
                    {"code": "GRASS"},  # no indexInfo
                    {
                        "code": "TREE",
                        "indexInfo": {"value": 2, "category": "Low", "indexDescription": "Low"},
                    },
                ]
            }]
        }
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from pollen_monitor.api import get_pollen_forecast
        result = get_pollen_forecast(35.6, 139.7)

        assert result["pollen_data"]["grass"] is None
        assert result["pollen_data"]["tree"]["value"] == 2

    @patch("pollen_monitor.api.GOOGLE_API_KEY", "fake-key")
    @patch("pollen_monitor.api.requests.get")
    def test_http_error_propagates(self, mock_get):
        import requests as req
        mock_get.return_value.raise_for_status.side_effect = req.exceptions.HTTPError("500 Server Error")

        from pollen_monitor.api import get_pollen_forecast
        with pytest.raises(req.exceptions.HTTPError):
            get_pollen_forecast(35.6, 139.7)

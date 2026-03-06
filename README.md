# Pollen Monitor

A Python-based pollen level monitoring system that fetches real-time pollen forecasts from the Google Pollen API, stores readings in a local SQLite database, and sends Slack alerts when pollen levels exceed a configurable threshold.

## Features

- Fetches daily pollen forecasts (Tree, Grass, Weed) via the [Google Pollen API](https://developers.google.com/maps/documentation/pollen)
- Configurable threshold-based alerting (UPI index 0-5)
- Slack webhook notifications with health recommendations
- SQLite database for historical pollen data logging
- Structured logging to file and console

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- A Google Cloud API key with the Pollen API enabled
- (Optional) A Slack incoming webhook URL

## Installation

```bash
# Clone the repository
git clone git@github.com:jaygaha/pollen-monitor.git
cd pollen-monitor

# Install dependencies
uv sync
```

## Configuration

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `GOOGLE_API_KEY` | Google Cloud API key (required) | — |
| `DATABASE_URL` | SQLite database file path | `pollen_monitor.db` |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | — |
| `LATITUDE` | Monitoring location latitude | `35.740065` |
| `LONGITUDE` | Monitoring location longitude | `139.665694` |
| `PLACE_NAME` | Human-readable location name | `Tokyo, Japan` |
| `THRESHOLD` | UPI level that triggers alerts (0-5) | `3` |

### Threshold Scale

| Value | Meaning |
|---|---|
| 0 | None |
| 1 | Very Low |
| 2 | Low |
| 3 | Moderate |
| 4 | High |
| 5 | Very High |

## Usage

```bash
uv run python -m pollen_monitor.main
```

For scheduled monitoring, use a cron job or task scheduler:

```bash
# Run every day at 7:00 AM
0 7 * * * cd /path/to/pollen-monitor && uv run python -m pollen_monitor.main
```

## Running Tests

```bash
uv run pytest tests/ -v
```

## Project Structure

```
pollen-monitor/
├── src/pollen_monitor/
│   ├── __init__.py
│   ├── main.py          # Entry point and orchestration
│   ├── api.py           # Google Pollen API client
│   ├── database.py      # SQLite storage layer
│   ├── monitor.py       # Threshold checking logic
│   ├── notifier.py      # Slack alert composition and delivery
│   └── logger.py        # Logging configuration
├── tests/
│   ├── conftest.py      # Shared test fixtures
│   ├── test_api.py      # API client tests
│   ├── test_database.py # Database tests
│   ├── test_main.py     # Integration tests
│   ├── test_monitor.py  # Threshold logic tests
│   └── test_notifier.py # Notifier tests
├── .env.example
├── pyproject.toml
└── README.md
```

## Potential Feature Expansions

### Email Alerts

Send email notifications when pollen levels breach the threshold using SMTP or a service like SendGrid/AWS SES. This would allow users who don't use Slack to receive alerts directly in their inbox.

### SMS Notifications

Integrate with Twilio or AWS SNS to send SMS alerts for critical pollen levels (UPI 4-5). Particularly useful for users who need immediate mobile notifications while outdoors.

### Multi-Location Monitoring

Support monitoring multiple locations simultaneously by accepting a list of coordinate/name pairs, enabling users to track pollen across commute routes or family locations.

### Historical Trend Dashboard

Build a web dashboard (e.g., with Flask or Streamlit) to visualize pollen trends over time using the SQLite historical data, helping users identify seasonal patterns.

### Configurable Pollen Type Alerts

Allow users to configure alerts for specific pollen types (Tree, Grass, Weed) independently, since different allergies respond to different pollen sources.

### REST API Endpoint

Expose the stored pollen data via a lightweight REST API so other applications or home automation systems (e.g., Home Assistant) can query current and historical levels.

### Contributing

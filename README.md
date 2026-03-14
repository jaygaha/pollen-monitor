# Pollen Monitor

[![CI](https://github.com/jaygaha/pollen-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/jaygaha/pollen-monitor/actions/workflows/ci.yml)

A Python-based pollen level monitoring system that fetches real-time pollen forecasts from the Google Pollen API, stores readings in a local SQLite database, and sends Slack and email alerts when pollen levels exceed a configurable threshold.

## Features

- Fetches daily pollen forecasts (Tree, Grass, Weed) via the [Google Pollen API](https://developers.google.com/maps/documentation/pollen)
- Configurable threshold-based alerting (UPI index 0-5)
- Slack webhook notifications with health recommendations
- Email alerts via [Resend](https://resend.com/) with a HTML template
- SQLite database for historical pollen data logging
- Structured logging to file and console

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- A Google Cloud API key with the Pollen API enabled
- (Optional) A Slack incoming webhook URL
- (Optional) A [Resend](https://resend.com/) API key for email alerts

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
| `RESEND_API_KEY` | Resend API key for email alerts | — |

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

## Deployment

The application is designed to run on AWS EC2 instances. Follow these steps for manual deployment:

### Initial Setup

1. **Launch EC2 Instance**:
   - Choose Ubuntu 22.04 LTS or Amazon Linux 2
   - Configure security groups for SSH (port 22) and any required outbound access

2. **Install Dependencies**:
   ```bash
   sudo apt update && sudo apt install -y python3 python3-pip curl
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Clone Repository**:
   ```bash
   git clone https://github.com/jaygaha/pollen-monitor.git
   cd pollen-monitor
   ```

4. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

5. **Install Python Dependencies**:
   ```bash
   uv sync
   ```

### Scheduling

Set up a cron job to run the monitor daily:

```bash
# Edit crontab
crontab -e

# Add this line to run at 7:00 AM daily
0 7 * * * cd /home/ubuntu/pollen-monitor && /home/ubuntu/.local/bin/uv run python -m pollen_monitor.main
```

### Monitoring

- Logs are written to `pollen_system.log`
- Database file: `pollen_monitor.db`
- Check system logs for any errors

## Development

### Setup Development Environment

```bash
git clone https://github.com/jaygaha/pollen-monitor.git
cd pollen-monitor
uv sync --group dev
```

### Code Quality

- **Linting**: `uv run ruff check`
- **Formatting**: `uv run ruff format`
- **Testing**: `uv run pytest`

### Project Structure

```
pollen-monitor/
├── src/pollen_monitor/
│   ├── __init__.py
│   ├── api.py          # Google Pollen API client
│   ├── database.py     # SQLite database operations
│   ├── logger.py       # Logging configuration
│   ├── main.py         # Application entry point
│   ├── monitor.py      # Threshold checking logic
│   └── notifier.py     # Slack and email notifications
├── tests/              # Unit tests
├── .github/workflows/  # CI/CD pipelines
└── pyproject.toml      # Project configuration
```

## Notifications

When pollen levels meet or exceed the configured `THRESHOLD`, the monitor sends alerts through two channels:

### Slack

A formatted message is posted to the configured Slack webhook with the UPI index, description, and health recommendations.

### Email (Resend)

An HTML email is sent via the Resend API featuring:

- A **severity-colored accent bar** that shifts from green (None) to red (Very High) based on the UPI level
- A **UPI badge** showing the numeric index alongside the severity label
- **Description** and **health recommendations** sections
- Fully **inline-styled** for reliable rendering across email clients (Gmail, Outlook, Apple Mail)

Set the `RESEND_API_KEY` environment variable to enable email alerts. The sender address and recipients are configured in `notifier.py`.

## Running Tests

```bash
uv run pytest tests/ -v
```

## Potential Feature Expansions

### SMS Notifications

Integrate with Twilio or AWS SNS to send SMS alerts for critical pollen levels (UPI 4-5). Particularly useful for users who need immediate mobile notifications while outdoors.

### Multi-Location Monitoring

Support monitoring multiple locations simultaneously by accepting a list of coordinate/name pairs, enabling users to track pollen across commute routes or family locations.

### Historical Trend Dashboard

Build a web dashboard (e.g., with Flask or Streamlit) to visualize pollen trends over time using the SQLite historical data, helping users identify seasonal patterns.



Allow users to configure alerts for specific pollen types (Tree, Grass, Weed) independently, since different allergies respond to different pollen sources.

### REST API Endpoint

Expose the stored pollen data via a lightweight REST API so other applications or home automation systems (e.g., Home Assistant) can query current and historical levels.

## Contributing

Free free to star this repo and extend the feature

happy coding🧑‍💻
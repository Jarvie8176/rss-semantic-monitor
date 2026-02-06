# RSS Semantic Monitor

A robust, semantic-aware RSS monitoring tool designed for OpenClaw.

## 🚀 Getting Started

### 1. Installation
Clone this repository into your OpenClaw workspace or skills directory:
```bash
git clone git@github.com:Jarvie8176/rss-semantic-monitor.git
```

### 2. Dependency Setup
We recommend using a virtual environment:
```bash
cd rss-semantic-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Copy the example config and edit it:
```bash
cp rss_monitor_settings.json.example rss_monitor_settings.json
```
Edit `rss_monitor_settings.json` to include your:
- Discord Channel ID
- RSS Feed URLs
- Positive Topics (topics you want to be notified about)
- Similarity Threshold (default: 0.4)

### 4. Running
```bash
python3 scripts/monitor.py
```

## 🛠 Project Structure
- `scripts/monitor.py`: Core logic for fetching, filtering, and notifying.
- `scripts/wizard.py`: CLI tool for managing settings (WIP).
- `rss_monitor_settings.json`: Local configuration (ignored by git).
- `processed_history.json`: Tracks processed items (ignored by git).

## 🔒 Security
This project uses GPG signatures for all commits and encourages key-based authentication for deployments.

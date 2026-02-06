# RSS Semantic Monitor Skill

Semantic-based RSS and HTML content monitoring for OpenClaw.

## Features
- **Semantic Filtering**: Uses local LLM embeddings (Sentence-Transformers) to filter news by meaning, not just keywords.
- **Custom HTML Support**: Includes a selector-based scraper for non-RSS sites (e.g., Dealmoon).
- **OpenClaw Integration**: Delivers matches directly to Discord via OpenClaw's messaging system.
- **Configurable**: Decoupled settings for models, thresholds, and target channels.

## Usage
Add this directory to your OpenClaw skills path.

### Tools
- `rss_monitor_run`: Run the semantic monitor once.
- `rss_monitor_setup`: Run the interactive wizard to configure feeds and topics.

### Configuration
Rename `rss_monitor_settings.json.example` to `rss_monitor_settings.json` and fill in your details.

import json
import os
import time
import hashlib
import requests
from bs4 import BeautifulSoup
import feedparser
from sentence_transformers import SentenceTransformer, util

# --- Configuration ---
CONFIG_PATH = "rss_monitor_settings.json"
HISTORY_PATH = "processed_history.json"

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_history(history):
    with open(HISTORY_PATH, 'w') as f:
        json.dump(history[-500:], f) # Keep last 500

def get_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

# --- Notifiers ---
class Notifier:
    def notify(self, items):
        raise NotImplementedError

class OpenClawCLINotifier(Notifier):
    def __init__(self, channel_id):
        self.channel_id = channel_id

    def notify(self, items):
        if not self.channel_id:
            print("Skipping notification: No channel_id provided.")
            return
        
        for item in items:
            msg = f"发现匹配内容：{item['title']} - {item['link']}"
            # Escape single quotes for shell command
            safe_msg = msg.replace("'", "'\"'\"'")
            os.system(f"openclaw message send --target {self.channel_id} --message '{safe_msg}'")

# --- Scrapers ---
def fetch_html_selector_source(url, name):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        items = []
        for card in soup.select(".mlist .item"):
            title_tag = card.select_one(".title")
            link_tag = card.select_one("a")
            if title_tag and link_tag:
                items.append({
                    "title": title_tag.get_text(strip=True),
                    "link": link_tag['href'],
                    "source": name
                })
        return items
    except Exception as e:
        print(f"Error fetching {name}: {e}")
        return []

def fetch_rss(url, name):
    try:
        feed = feedparser.parse(url)
        return [{"title": entry.title, "link": entry.link, "source": name} for entry in feed.entries]
    except Exception as e:
        print(f"Error fetching RSS {name}: {e}")
        return []

# --- Main Logic ---
def main():
    config = load_config()
    history = load_history()
    
    model_name = config.get('model_name', "paraphrase-multilingual-MiniLM-L12-v2")
    threshold = config.get('similarity_threshold', 0.4)
    
    print(f"Loading Local Embedding Model ({model_name})...")
    model = SentenceTransformer(model_name)
    
    pos_topics = list(config.get('positive_topics', {}).keys())
    if not pos_topics:
        print("No topics configured. Exiting.")
        return
    topic_embeddings = model.encode(pos_topics)

    all_items = []
    for feed in config['feeds']:
        print(f"Fetching {feed['name']}...")
        if "dealmoon" in feed['url'].lower():
            all_items.extend(fetch_html_selector_source(feed['url'], feed['name']))
        else:
            all_items.extend(fetch_rss(feed['url'], feed['name']))

    filtered_items = []
    for item in all_items:
        item_hash = get_hash(item['link'] or item['title'])
        if item_hash in history:
            continue
        
        item_embedding = model.encode(item['title'])
        similarities = util.cos_sim(item_embedding, topic_embeddings)[0]
        max_sim = max(similarities).item()
        
        if max_sim > threshold:
            print(f"Match Found: {item['title']} (Sim: {max_sim:.2f})")
            filtered_items.append(item)
            history.append(item_hash)
    
    if filtered_items:
        channel_id = config.get('output', {}).get('discord_channel_id')
        notifier = OpenClawCLINotifier(channel_id)
        notifier.notify(filtered_items)
    
    save_history(history)
    print("Done.")

if __name__ == "__main__":
    main()

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
        with open(HISTORY_PATH, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_PATH, 'w') as f:
        json.dump(history[-500:], f) # Keep last 500

def get_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

# --- Scrapers ---
def fetch_dealmoon():
    # Use web_fetch logic simulation or direct requests if possible
    # For now, we simulate structured extraction from Dealmoon
    try:
        r = requests.get("https://www.dealmoon.ca/", timeout=15)
        soup = BeautifulSoup(r.text, 'lxml')
        items = []
        for card in soup.select(".mlist .item"):
            title = card.select_one(".title").get_text(strip=True) if card.select_one(".title") else ""
            link = card.select_one("a")['href'] if card.select_one("a") else ""
            if title:
                items.append({"title": title, "link": link, "source": "Dealmoon"})
        return items
    except:
        return []

def fetch_rss(url, name):
    feed = feedparser.parse(url)
    return [{"title": entry.title, "link": entry.link, "source": name} for entry in feed.entries]

# --- Main Logic ---
def main():
    config = load_config()
    history = load_history()
    
    model_name = config.get('model_name', "paraphrase-multilingual-MiniLM-L12-v2")
    threshold = config.get('similarity_threshold', 0.4)
    
    print(f"Loading Local Embedding Model ({model_name})...")
    model = SentenceTransformer(model_name)
    
    # Pre-encode topics
    pos_topics = list(config.get('positive_topics', {}).keys())
    if not pos_topics:
        print("No topics configured. Exiting.")
        return
    topic_embeddings = model.encode(pos_topics)

    all_items = []
    for feed in config['feeds']:
        print(f"Fetching {feed['name']}...")
        if "dealmoon" in feed['url']:
            all_items.extend(fetch_dealmoon())
        else:
            all_items.extend(fetch_rss(feed['url'], feed['name']))

    filtered_items = []
    for item in all_items:
        item_hash = get_hash(item['link'] or item['title'])
        if item_hash in history:
            continue
        
        # L2: Local Semantic Filter
        item_embedding = model.encode(item['title'])
        similarities = util.cos_sim(item_embedding, topic_embeddings)[0]
        max_sim = max(similarities).item()
        
        if max_sim > threshold: # Threshold
            print(f"Match Found: {item['title']} (Sim: {max_sim:.2f})")
            filtered_items.append(item)
            history.append(item_hash)
    
    save_history(history)
    
    # L3: Cloud AI Summary & Discord Delivery
    if filtered_items:
        print(f"\nSending {len(filtered_items)} items to AI and Discord...")
        
        target_channel = config.get('output', {}).get('discord_channel_id')
        if not target_channel:
            print("Error: No discord_channel_id found in config['output'].")
            return

        # 构造待分析的内容
        content_to_analyze = "\n".join([f"- {item['title']} ({item['link']})" for item in filtered_items])
        
        print(f"DISCORD_PUSH_TARGET: {target_channel}")
        
        for item in filtered_items:
            # 使用配置中的 channel id
            os.system(f"openclaw message send --target {target_channel} --message '发现匹配内容：{item['title']} - {item['link']}'")

if __name__ == "__main__":
    main()

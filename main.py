import time import feedparser import requests import os from html import unescape

--- Configuration (for Railway environment variables) ---

BOT_TOKEN = os.getenv("BOT_TOKEN", "8066387567:AAGzPCFJE-h7QKyUwisU8OUVm8hcTVpDnE4") CHANNEL = os.getenv("CHANNEL", "@manutdai") CHANNEL_TAG = f"🪆{CHANNEL}" FEED_URL = "https://www.manchestereveningnews.co.uk/all-about/manchester-united-fc/?service=rss" CHECK_INTERVAL = 180  # seconds

HEADERS = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" }

sent_ids = set()

def get_news(): try: response = requests.get(FEED_URL, headers=HEADERS, timeout=10) feed = feedparser.parse(response.content) return feed.entries except Exception as e: print("Fetch error:", e) return []

def extract_image(entry): if "media_content" in entry: return entry.media_content[0].get("url") if "links" in entry: for link in entry.links: if link.get("type", "").startswith("image"): return link.get("href") return None

def send_news(entry): title = unescape(entry.title) link = entry.link image_url = extract_image(entry) caption = f"<b>{title}</b>\n{link}\n\n{CHANNEL_TAG}"

try:
    if image_url:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHANNEL,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "HTML"
        }
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL,
            "text": caption,
            "parse_mode": "HTML"
        }

    requests.post(url, data=payload, timeout=10)
except Exception as e:
    print("Send error:", e)

def main(): while True: try: for entry in get_news(): entry_id = entry.get("id") or entry.link if entry_id not in sent_ids: send_news(entry) sent_ids.add(entry_id) except Exception as e: print("Loop error:", e) time.sleep(CHECK_INTERVAL)

if name == "main": main()


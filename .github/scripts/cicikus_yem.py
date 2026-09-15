from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

BASE_URL = "https://daddylive.dad"
OUTPUT_FILE = "dl/daddyliveevents.m3u"

def fetch_events():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)
        page.wait_for_timeout(5000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    events = []
    current_category = "Standart Etkinlik Kategorisi"

    for row in soup.find_all('tr'):
        if 'category-row' in row.get('class', []):  
            category_td = row.find('td', colspan=True)
            if category_td:
                current_category = category_td.text.strip()
        elif 'event-row' in row.get('class', []):
            time_div = row.find('div', class_='event-time')
            info_div = row.find('div', class_='event-info')
            event_time = time_div.text.strip() if time_div else ""
            event_title = info_div.text.strip() if info_div else ""

            channel_row = row.find_next_sibling('tr', class_='channel-row')
            if channel_row:
                link = channel_row.find('a', href=True)
                if link:
                    href = link['href']
                    id_match = re.search(r'stream-(\d+)\.php', href)
                    if id_match:
                        channel_id = id_match.group(1)
                        stream_url = f"https://new.newkso.ru/wind/premium{channel_id}/mono.m3u8"
                        events.append((event_title, stream_url, channel_id, event_time, current_category))
    return events

def save_m3u(events, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for title, url, channel_id, event_time, category in events:
            id = channel_id
            f.write(f'#EXTINF:-1 tvg-id="{id}" tvg-name="{title}" tvg-logo="https://raw.githubusercontent.com/GitLatte/temporarylists/refs/heads/main/img/daddylive-events-kanallar.png" group-title="{category}",{title} ({event_time})\n{url}\n')

if __name__ == "__main__":
    events = fetch_events()
    save_m3u(events, OUTPUT_FILE)
    print(f"{OUTPUT_FILE} dosyası oluşturuldu. Toplam event: {len(events)}")

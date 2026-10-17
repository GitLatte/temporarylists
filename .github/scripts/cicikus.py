import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import os

BASE_URL = "https://daddylive.dad"
CHANNELS_PAGE = BASE_URL + "/24-7-channels.php"
OUTPUT_FILE = "dl/lattenin-otomasyonu/daddylive_kanallar.m3u"

DOMAINS = [
    "https://new.newkso.ru/wind",
    "https://zekonew.newkso.ru/zeko",
    "https://ddy6new.newkso.ru/ddy6",
    "https://dokko1new.newkso.ru/dokko1",
    "https://ddh2new.ddh2.ru/ddh2",
    "https://top2new.top2.ru/top2",
    "https://wikinew.wiki.ru/wiki",
]

def fetch_channels():
    response = requests.get(CHANNELS_PAGE)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    channels = []

    for item in soup.find_all('div', class_='grid-item'):
        link = item.find('a', href=True)
        if not link or "stream-" not in link['href']:
            continue

        name = link.text.strip()
        href = link['href']
        id_match = re.search(r'stream-(\d+)\.php', href)

        if id_match:
            channel_id = id_match.group(1)

            channel_name_lower = name.lower()

            if 'player' in channel_name_lower:
                continue

            group = name.split()[-1]

            for domain in DOMAINS:
                stream_url = f"{domain}/premium{channel_id}/mono.m3u8"

                try:
                    parsed_url = urlparse(stream_url)
                    path_parts = parsed_url.path.split('/')
                    etiket = ""

                    if len(path_parts) > 1 and path_parts[1] and path_parts[1] != f"premium{channel_id}":
                        etiket = path_parts[1]
                    elif len(parsed_url.netloc.split('.')) > 1:
                        potential_etiket = parsed_url.netloc.split('.')[0]
                        if potential_etiket and potential_etiket not in ['new', 'zekonew', 'ddy6new', 'dokko1new', 'ddh2new', 'top2new', 'wikinew']:
                             etiket = potential_etiket
                        else:
                             etiket = parsed_url.netloc

                    etiket_str = f"({etiket})" if etiket else ""

                except Exception:
                    etiket_str = "(bilinmeyen_etiket)"


                name_tagged = f"{name} {etiket_str}".strip()
                extinf = (
                    f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{name_tagged}" '
                    f'group-title="{group}", {name_tagged}'
                )
                channels.append((extinf, stream_url))

    return channels

def save_m3u(channels, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for extinf, url in channels:
            f.write(f"{extinf}\n{url}\n\n")

if __name__ == "__main__":
    channels = fetch_channels()
    save_m3u(channels, OUTPUT_FILE)
    print(f"{OUTPUT_FILE} dosyası oluşturuldu. Toplam kanal: {len(channels)}")

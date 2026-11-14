import requests
import os
import re
import sys
from collections import defaultdict

OUTPUT_DIR = "tospecial"
OUTPUT_FILENAME = "voturk.m3u"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)

DEFAULT_TVG_LOGO_URL = "https://raw.githubusercontent.com/GitLatte/temporarylists/refs/heads/main/img/v-kanallari.png"

M3U_URL = os.environ.get('M3U_SOURCE_URL')
GITHUB_PAT = os.environ.get("LATTE_PAT")

if not M3U_URL:
    print("Error: Tanımlı secrets'a erişilemiyor")
    sys.exit(1)

if not GITHUB_PAT:
    print("Error: GitHub PAT bulunamadı.")
    sys.exit(1)

print("Liste alınıyor...")

headers = {
    "Authorization": f"token {GITHUB_PAT}"
}

try:
    response = requests.get(M3U_URL, headers=headers, stream=True)
    response.raise_for_status()
    m3u_content = response.text
except requests.exceptions.RequestException as e:
    print(f"M3u alma hatası: {e}")
    sys.exit(1)

print("M3U başarıyla alındı. İşleniyor...")

lines = m3u_content.splitlines()

channels = []
current_extinf = None

for line in lines:
    line = line.strip()
    if line.startswith("#EXTINF:"):
        current_extinf = line
    elif line.startswith("http"):
        if current_extinf:
            tvg_name_match = re.search(r'tvg-name="([^"]*)"', current_extinf)
            tvg_name = tvg_name_match.group(1) if tvg_name_match else ""
            channels.append({"extinf": current_extinf, "url": line, "tvg_name": tvg_name})
        current_extinf = None

print(f"Toplam {len(channels)} kanal girişi bulundu.")

turkey_channels = []
for channel in channels:
    group_title_match = re.search(r'group-title="([^"]*)"', channel["extinf"], re.IGNORECASE)
    if group_title_match:
        group_title = group_title_match.group(1)
        if "turkey" in group_title.lower():
            turkey_channels.append(channel)

print(f"'turkey' grup başlığına sahip {len(turkey_channels)} kanal filtrelendi.")

def sort_key(channel):
    tvg_name = channel["tvg_name"].lower()
    is_bein_spor = "bein" in tvg_name and "spor" in tvg_name
    is_spor = "spor" in tvg_name

    if is_bein_spor:
        group_priority = 0
    elif is_spor:
        group_priority = 1
    else:
        group_priority = 2

    return (group_priority, tvg_name)

processed_channels_temp = []
for channel in turkey_channels:
    sort_info = sort_key(channel)
    group_priority = sort_info[0]

    target_group_title = ""
    if group_priority in [0, 1]:
        target_group_title = "Spor Kanalları"
    else:
        target_group_title = "Genel Kanallar"

    processed_channels_temp.append({
        "original_extinf": channel["extinf"],
        "url": channel["url"],
        "tvg_name": channel["tvg_name"],
        "group_priority": group_priority,
        "target_group_title_base": target_group_title
    })

print("Geçici kanal bilgileri oluşturuldu.")

group_counts = defaultdict(int)
for channel in processed_channels_temp:
    group_counts[channel["target_group_title_base"]] += 1

print(f"Grup sayıları: {dict(group_counts)}")

def add_missing_tvg_attributes_and_update_group_with_count(extinf_line, default_logo_url, target_group_title_base, group_count):
    match = re.match(r'(#EXTINF:-1)(.*)', extinf_line)
    if not match:
        print(f"Uyarı: Tanımsız EXTINF formatı: {extinf_line}")
        return extinf_line

    prefix = match.group(1)
    attributes_and_name_string = match.group(2).strip()

    parts = attributes_and_name_string.split(',')
    display_name = parts[-1].strip()
    attributes_part = ','.join(parts[:-1]).strip()

    existing_attributes = {}
    attribute_matches = re.findall(r'(\S+)="([^"]*)"', attributes_part)

    for key, value in attribute_matches:
        existing_attributes[key.lower()] = value

    new_attributes_list = []

    for key, value in attribute_matches:
         if key.lower() != 'group-title':
             new_attributes_list.append(f'{key}="{value}"')

    target_group_title_with_count = f"{target_group_title_base} ({group_count})"
    new_attributes_list.append(f'group-title="{target_group_title_with_count}"')

    if 'tvg-logo' not in existing_attributes:
        new_attributes_list.append(f'tvg-logo="{default_logo_url}"')

    if 'tvg-language' not in existing_attributes:
        new_attributes_list.append('tvg-language="TR"')

    if 'tvg-country' not in existing_attributes:
        new_attributes_list.append('tvg-country="TR"')

    new_attributes_string = " ".join(new_attributes_list).strip()

    if new_attributes_string:
       return f"{prefix} {new_attributes_string}, {display_name}"
    else:
       return f"{prefix} {display_name}"

processed_channels_final = []
for channel in processed_channels_temp:
    count = group_counts.get(channel["target_group_title_base"], 0)

    modified_extinf = add_missing_tvg_attributes_and_update_group_with_count(
        channel["original_extinf"],
        DEFAULT_TVG_LOGO_URL,
        channel["target_group_title_base"],
        count
    )

    processed_channels_final.append({
        "extinf": modified_extinf,
        "url": channel["url"],
        "group_priority": channel["group_priority"],
        "tvg_name": channel["tvg_name"]
    })

print("Eksik tvg etiketleri eklendi ve group-title'a sayılar dahil edildi.")

def sort_key_for_final_output(channel):
     return (channel["group_priority"], channel["tvg_name"].lower())

processed_channels_final.sort(key=sort_key_for_final_output)

print("Kanal sıralaması tamamlandı.")

output_content = "#EXTM3U\n"

for channel in processed_channels_final:
    output_content += f"{channel['extinf']}\n"
    output_content += f"{channel['url']}\n"

os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(output_content)
    print(f"Başarıyla çıktı dosyası yazıldı: {OUTPUT_PATH}")
except IOError as e:
    print(f"Dosya yazma hatası oluştu {OUTPUT_PATH}: {e}")
    sys.exit(1)

print("İşlem tamamlandı.")

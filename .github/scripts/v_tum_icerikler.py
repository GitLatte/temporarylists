import requests
import json
import os

# Ülke isimlerini Türkçeye çevirme eşleme tablosu
country_mapping = {
    "Germany": ("Almanya", "Almanca"),
    "United Kingdom": ("Birleşik Krallık", "İngilizce"),
    "France": ("Fransa", "Fransızca"),
    "Turkey": ("Türkiye", "Türkçe"),
    "Italy": ("İtalya", "İtalanca"),
    "Spain": ("İspanya", "İspanyolca"),
    "Albania": ("Arnavutluk", "Arnavutça"),
    "Arabia": ("Arabistan", "Arapça"),
    "Balkans": ("Balkanlar", "Türkçe"),
    "Bulgaria": ("Bulgaristan", "Bulgarca"),
    "Netherlands": ("Hollanda", "Felemenkçe"),
    "Poland": ("Polonya", "Lehçe"),
    "Portugal": ("Portekiz", "Portekizce"),
    "Russia": ("Rusya", "Rusça"),
    
}

# JSON verisini çek
url = "https://www2.vavoo.to/live2/index"
response = requests.get(url)
channels = response.json()

# M3U dosya içeriği oluştur
m3u_content = "#EXTM3U\n"
output_dir = "tospecial"
os.makedirs(output_dir, exist_ok=True)  # Eğer dizin yoksa oluştur

for channel in channels:
    group = channel["group"]
    logo = "https://raw.githubusercontent.com/patr0nq/link/refs/heads/main/tv-logo/vavoo.png"
    name = channel["name"]
    url = channel["url"]

    # Ülke adına göre tvg-country ve tvg-language belirleme
    country_name, language_code = country_mapping.get(group, (group, "xx"))

    # tvg-id oluşturma (kanal adı + ülke kodu)
    tvg_id = f"{name.lower().replace(' ', '').replace('.', '')}.{language_code}"

    # URL formatını değiştirme
    stream_url = url.replace("live2/play", "play").replace(".ts", "/index.m3u8")

    # M3U formatında satır ekleme
    m3u_content += f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{country_name}" tvg-country="{country_name}" tvg-language="{language_code}", {name}\n{stream_url}\n'

# Dosyayı `tospecial/v-tum-kanallar.m3u` dizinine kaydet
output_path = os.path.join(output_dir, "v-tum-kanallar.m3u")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(m3u_content)

print(f"M3U listesi oluşturuldu: {output_path}")

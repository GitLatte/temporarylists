import base64
import re

# Dosya yolları
INPUT_FILES = ["dl/dl-daddyliveall.m3u", "dl/daddyliveevents.m3u"]

def decode_base64(encoded_str):
    """Base64 kodunu decode eden fonksiyon"""
    try:
        return base64.b64decode(encoded_str).decode('utf-8')
    except Exception as e:
        return f"Decoding error: {e}"

def process_m3u(file_path):
    """M3U dosyasını temizleyip, Base64 kodlarını decode eder"""
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    processed_lines = []

    for line in lines:
        line = line.strip()

        if line.startswith("http") and "watch/" in line and ".m3u8" in line:
            base64_part = re.search(r'watch/([^\.]+)\.m3u8', line)
            if base64_part:
                decoded_url = decode_base64(base64_part.group(1))
                processed_lines.append(decoded_url)
            else:
                processed_lines.append(line)
        else:
            processed_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(processed_lines))

    print(f"✅ M3U dosyası güncellendi: {file_path}")

# Tüm dosyaları işleyelim
for input_file in INPUT_FILES:
    process_m3u(input_file)

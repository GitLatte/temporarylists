import os
import re

import hashlib
import random

def generate_stream_id(channel_name):
    # Kanal adından benzersiz bir stream ID oluştur
    hash_object = hashlib.md5(channel_name.encode())
    stream_id = int(hash_object.hexdigest(), 16) % (10 ** 8)  # 8 haneli sayı
    return stream_id

def transform_m3u_urls(input_file, username, password):
    # Dosya adını al
    base_name = os.path.basename(input_file)
    name, _ = os.path.splitext(base_name)
    
    # Xtream API URL'sini oluştur
    server_url = 'https://raw.githubusercontent.com/GitLatte/temporarylists/xtream/get.php'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = ['#EXTM3U']
    current_channel = None
    
    for line in lines:
        if line.startswith('#EXTINF'):
            # Kanal bilgilerini parse et
            match = re.search(r'tvg-name="([^"]+)"', line)
            if match:
                current_channel = match.group(1)
                stream_id = generate_stream_id(current_channel)
                # Xtream formatında kanal bilgisi
                new_lines.append(line.strip())
        elif line.startswith('http'):
            if current_channel:
                # Xtream formatında stream URL'si oluştur
                stream_id = generate_stream_id(current_channel)
                new_url = f"{server_url}?username={username}&password={password}&type=m3u&playlist={name}&stream_id={stream_id}"
                new_lines.append(new_url)
                current_channel = None
        else:
            new_lines.append(line.strip())
    
    new_content = '\n'.join(new_lines)
    
    # Yeni dosya adı oluştur
    dir_name = os.path.dirname(input_file)
    base_name = os.path.basename(input_file)
    name, ext = os.path.splitext(base_name)
    output_file = os.path.join(dir_name, f'{name}_protected{ext}')
    
    # Yeni dosyayı kaydet
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return output_file

# Dönüştürülecek dizinlerin listesi
TARGET_DIRECTORIES = os.getenv('TARGET_DIRECTORIES', 'xtreamlists').split(',')

def process_directory(directory):
    username = os.getenv('STREAM_USERNAME')
    password = os.getenv('STREAM_PASSWORD')
    
    if not username or not password:
        raise ValueError('STREAM_USERNAME ve STREAM_PASSWORD environment variables gerekli')
        
    if not TARGET_DIRECTORIES:
        raise ValueError('En az bir hedef dizin belirtilmelidir')
    
    for root, _, files in os.walk(directory):
        # Sadece hedef dizinlerdeki dosyaları işle
        current_dir = os.path.basename(root)
        if current_dir not in TARGET_DIRECTORIES:
            continue
            
        for file in files:
            if file.endswith('.m3u'):
                input_file = os.path.join(root, file)
                try:
                    output_file = transform_m3u_urls(input_file, username, password)
                    print(f'Dönüştürüldü: {input_file} -> {output_file}')
                except Exception as e:
                    print(f'Hata: {input_file} dosyası işlenirken hata oluştu: {str(e)}')

if __name__ == '__main__':
    repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    process_directory(repo_dir)
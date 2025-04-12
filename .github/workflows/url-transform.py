import os
import re

def transform_m3u_urls(input_file, username, password):
    # GitHub raw content URL'sini oluştur
    repo_path = os.path.relpath(input_file, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    repo_url = f'https://raw.githubusercontent.com/patrontech/temporarylists/protected-streams/{repo_path}'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # URL'leri bul ve dönüştür
    pattern = r'https://[^\s\n]+'
    
    # GitHub raw content URL'sini ekle
    content = f"#EXTM3U\n#EXTINF:-1,GitHub Raw Content URL\n{repo_url}?username={username}&password={password}&type=m3u\n\n" + content
    def replace_url(match):
        url = match.group(0)
        # Eğer URL zaten kullanıcı adı ve şifre içeriyorsa, dönüştürme
        if 'username=' in url or 'password=' in url:
            return url
        # URL'yi yeni formata dönüştür
        new_url = f'{url}?username={username}&password={password}&type=m3u'
        return new_url
    
    new_content = re.sub(pattern, replace_url, content)
    
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
TARGET_DIRECTORIES = ['xtreamlists']

def process_directory(directory):
    username = os.getenv('STREAM_USERNAME')
    password = os.getenv('STREAM_PASSWORD')
    
    if not username or not password:
        raise ValueError('STREAM_USERNAME ve STREAM_PASSWORD environment variables gerekli')
    
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
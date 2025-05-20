import requests
import os

# GitHub Secrets'tan API Token ve Space ID'yi alıyoruz
HF_API_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
SPACE_ID = os.getenv("HUGGINGFACE_SPACE_ID")

# Hugging Face API URL'si
url = f"https://huggingface.co/api/spaces/{SPACE_ID}/factory/rebuild"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# API çağrısı
response = requests.post(url, headers=headers)

if response.status_code == 200:
    print("✅ Factory Rebuild başarılı!")
else:
    print(f"❌ Hata oluştu: {response.status_code} - {response.text}")

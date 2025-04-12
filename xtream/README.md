# GitHub Xtream Kod Entegrasyonu

Bu sistem, GitHub deposundaki m3u dosyalarını Xtream kod formatında kullanmanızı sağlar.

## Kullanım

1. Sunucu adresi olarak şunu kullanın:
   ```
   https://raw.githubusercontent.com/GitLatte/temporarylists/xtream
   ```

2. Kullanıcı adı ve şifre:
   - Varsayılan kullanıcı adı: `sinetech`
   - Varsayılan şifre: `sinetech`

## Örnek

Herhangi bir IPTV uygulamasında Xtream kodları şu şekilde girin:

- **Sunucu**: `https://raw.githubusercontent.com/GitLatte/temporarylists/xtream`
- **Kullanıcı Adı**: `sinetech`
- **Şifre**: `sinetech`

## Dosya Yapısı

- `xtream_server.py`: Ana sunucu script'i
- `test.m3u`: Örnek m3u dosyası

## Güvenlik

Kullanıcı adı ve şifre doğrulaması `xtream_server.py` içinde yapılmaktadır. Yeni kullanıcılar eklemek için `CREDENTIALS` sözlüğünü düzenleyebilirsiniz.
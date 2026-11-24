# TarihGram

Gezilen tarihi yerlerin paylaşıldığı, mobil öncelikli bir web uygulaması prototipi (sürüm 1.0 E).

## Bu aşamada neler var

1. **Giriş ekranı**: Arka planda Leaflet ile çizilen, ülkeleri renklendirilmiş bir dünya haritası, ortada TarihGram logosu, "Kayıt Ol" ve "Giriş Yap" butonları, sağ altta "1.0 E" yazısı. Butonlar "Google ile Giriş Yap" penceresini açar.
2. **Ana ekran**: Sol üstte menü (+ Paylaş, Ana Sayfa, Keşfet, Geçmiş, Haritalar, Kaydedilenler, Profil ve en altta kullanıcı bilgileri), sağ üstte Ayarlar, ortada örnek gönderiler (Ayşe'nin Ephesus gönderisi dahil).

> Google girişi şimdilik **taklit edilir**: gerçek bir hesaba bağlanmaz, örnek kullanıcıyla ana ekrana geçer. Gerçek giriş için Firebase Authentication veya Google Identity Services eklenmelidir.

## Çalıştırma

Harita verisi (`data/world.json`) `fetch` ile yüklendiği için dosyayı bir yerel sunucuyla açın:

```bash
python3 -m http.server 8000
# tarayıcıda http://localhost:8000
```

## Dosyalar

- `index.html`: Uygulamanın tamamı (HTML, CSS, JS)
- `data/world.json`: Ülke sınırları (Natural Earth 1:110m, world-atlas paketinden)
- `assets/*.svg`: Örnek gönderi görselleri (çizim)

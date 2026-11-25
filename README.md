# TarihGram

Gezilen tarihi yerlerin paylaşıldığı, mobil öncelikli bir web uygulaması (sürüm 1.0 E).

## Neler çalışıyor

- **Giriş ekranı:** Arka planda Leaflet ile gösterilen fiziki dünya haritası (NASA Blue Marble görüntüsünden üretildi), ortada TarihGram yazısı, "Kayıt Ol" ve "Giriş Yap" butonları, sağ altta "1.0 E".
- **Kayıt / giriş penceresi:** Ad soyad, e-posta ve şifre ile kayıt; e-posta ve şifre ile giriş; şifremi unuttum; altında "Google ile Giriş Yap" butonu.
- **Ana ekran:** Sol üstte menü, sağ üstte Ayarlar (tema, çıkış).
- **Gönderiler:** Gerçek fotoğraflar ve videolar. Beğen (çift dokunuşla da), yorum yap, gönder, kaydet.
- **Gönderi sayfası:** Fotoğraflar ve videolar, mekânın açıklaması ve tarihçesi, Google Haritalar'da tam konumu, benzer mekânların haritası ve listesi, yorumlar.

### Menü
- **+ Paylaş:** Telefondan/bilgisayardan fotoğraf ve video seç (en fazla 10), mekân adını yaz (bilinen mekânlar önerilir ve konumu otomatik dolar), haritaya dokunarak ya da "Konumumu kullan" ile yerini işaretle, not ekle, paylaş. Kendi gönderini silebilirsin.
- **Ana Sayfa:** Tüm gönderilerin akışı.
- **Keşfet:** Arama (mekân, şehir, tür), kategori filtreleri, fotoğraf ızgarası ve keşfedilecek mekânlar listesi.
- **Geçmiş:** Görüntülediğin, beğendiğin, kaydettiğin, yorum yaptığın, paylaştığın ve gönderdiğin her şey gün gün; türe göre filtre ve geçmişi temizleme.
- **Haritalar:** Bütün gönderiler (fotoğraflı işaretler) ve mekânlar tek haritada; Gönderiler / Mekânlar / Kaydedilenler filtresi; işarete dokununca bilgi kartı.
- **Kaydedilenler:** Kaydettiğin gönderiler.
- **Profil:** Profil fotoğrafı, ad soyad ve "Hakkımda" düzenleme; gönderilerin ve kaydettiklerin.
- **En altta:** Profil fotoğrafın, adın, e-postan ve gönderi/beğeni/kayıt sayıların.

## Gerçek hesaplar ve "Google ile Giriş" için Firebase kurulumu

Firebase ayarı eklenmeden uygulama **önizleme modunda** çalışır: e-posta ile açılan hesaplar yalnızca o tarayıcıda saklanır, Google butonu bir uyarı gösterir. Gerçek hesaplar için (ücretsiz):

1. https://console.firebase.google.com adresinde **Proje ekle** ile yeni bir proje aç (ör. `tarihgram`).
2. **Build > Authentication > Get started**. **Sign-in method** sekmesinde **Email/Password** ve **Google** sağlayıcılarını etkinleştir.
3. **Proje ayarları (dişli) > Genel > Uygulamalarınız > Web (`</>`)** ile bir web uygulaması ekle. Sana verilen `firebaseConfig` nesnesini kopyala.
4. `index.html` içinde `var FIREBASE_CONFIG = null;` satırını bulup kopyaladığın nesneyle değiştir:
   ```js
   var FIREBASE_CONFIG = {
     apiKey: "...",
     authDomain: "tarihgram.firebaseapp.com",
     projectId: "tarihgram",
     appId: "..."
   };
   ```
5. **Authentication > Settings > Authorized domains** bölümüne sitenin yayınlandığı adresi ekle (ör. `kullaniciadi.github.io`).

Bu değerler gizli değildir; web sitelerinde açıkça bulunmaları normaldir.

## Yayınlama (GitHub Pages)

Depo ayarlarında **Settings > Pages > Branch** olarak bu dalı ve `/ (root)` klasörünü seç. Birkaç dakika sonra site `https://<kullanıcı-adı>.github.io/<depo-adı>/` adresinde açılır.

Yerelde denemek için dosyayı doğrudan açmak yerine bir sunucuyla aç (veriler `fetch` ile yüklenir):

```bash
python3 -m http.server 8000   # sonra http://localhost:8000
```

## Şimdilik yerel kalanlar

Paylaştığın gönderiler (fotoğraf ve videolarıyla birlikte tarayıcının IndexedDB deposunda), beğeniler, kayıtlar, yorumlar, geçmiş ve profil bilgileri şu an tarayıcıda saklanır; başka kullanıcılar görmez. Bunları herkesle paylaşmak bir sonraki adımda Firebase Firestore ile yapılabilir. "Gönder" penceresindeki kişilere gönderim de mesajlaşma bölümü gelene kadar göstermeliktir; bağlantıyı kopyalama gerçekten çalışır.

## Dosyalar

- `index.html`: Uygulamanın tamamı (HTML, CSS, JS)
- `tools/tek-dosya.py`: Her şeyi içine gömen tek dosyalık sürümü üretir (`python3 tools/tek-dosya.py cikti.html`)
- `data/gonderiler.json`: Örnek gönderiler, mekân açıklamaları, tarihçeler, benzer mekânlar, fotoğraf kaynakları
- `data/kiyilar.json`: Türkiye ve çevresinin kıyı çizgileri (Natural Earth 1:10m), internet haritası yüklenemezse kullanılır
- `assets/fiziki-harita.jpg`: Fiziki dünya haritası (NASA Blue Marble, kamu malı)
- `assets/foto/`, `assets/video/`: Wikimedia Commons'tan alınan fotoğraf ve videolar. Her birinin yazarı ve lisansı gönderi sayfasında "Fotoğraf ve video kaynakları" altında listelenir.

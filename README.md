# TarihGram

Gezilen tarihi yerlerin paylaşıldığı, mobil öncelikli bir web uygulaması (sürüm 1.0 E).

## Neler çalışıyor

- **Giriş ekranı:** Arka planda Leaflet ile gösterilen fiziki dünya haritası (NASA Blue Marble görüntüsünden üretildi), ortada TarihGram yazısı, "Kayıt Ol" ve "Giriş Yap" butonları, sağ altta "1.0 E".
- **Kayıt / giriş penceresi:** Ad soyad, e-posta ve şifre ile kayıt; e-posta ve şifre ile giriş; şifremi unuttum (e-postayla yeni şifre); altında "Google ile Giriş Yap" butonu.
- **Ana ekran:** Sol üstte menü, sağ üstte Ayarlar (tema, çıkış).
- **Gönderiler:** Gerçek fotoğraflar ve videolar. Beğen (çift dokunuşla da), yorum yap, gönder, kaydet.
- **Gönderi sayfası:** Fotoğraflar ve videolar, mekânın açıklaması ve tarihçesi, Google Haritalar'da tam konumu, benzer mekânların haritası ve listesi, yorumlar.

### Menü
- **+ Paylaş:** Fotoğraf ve video seç (en fazla 10; sürükle-bırak ve yapıştır da olur). Mekân adını ve şehri yazarken akıllı öneriler gelir, harf hatalarını tolere eder. Mekân seçilince yeri haritada kendiliğinden işaretlenir. Haritanın üstündeki arama kutusuyla yer aranabilir; haritaya dokunarak ya da "Konumumu kullan" ile de işaretlenebilir. Kendi gönderini silebilirsin.
- **Yönetim (yalnızca yöneticiler):** İstatistikler, tüm gönderiler ve yorumlar (silme), üyeler (kısıtlama, yönetici yapma).
- **Ana Sayfa:** Tüm gönderilerin akışı.
- **Keşfet:** Arama (mekân, şehir, tür), kategori filtreleri, fotoğraf ızgarası ve keşfedilecek mekânlar listesi.
- **Geçmiş:** Görüntülediğin, beğendiğin, kaydettiğin, yorum yaptığın, paylaştığın ve gönderdiğin her şey gün gün; türe göre filtre ve geçmişi temizleme.
- **Haritalar:** Bütün gönderiler (fotoğraflı işaretler) ve mekânlar tek haritada; Gönderiler / Mekânlar / Kaydedilenler filtresi; işarete dokununca bilgi kartı.
- **Kaydedilenler:** Kaydettiğin gönderiler.
- **Profil:** Profil fotoğrafı, ad soyad ve "Hakkımda" düzenleme; gönderilerin ve kaydettiklerin.
- **En altta:** Profil fotoğrafın, adın, e-postan ve gönderi/beğeni/kayıt sayıların.

## Siteyi herkese açık yapmak (Supabase + GitHub Pages)

Ayar yapılmadan uygulama **önizleme modunda** çalışır: hesaplar ve gönderiler yalnızca o tarayıcıda durur. Herkesin birbirinin gönderisini (fotoğraf ve videolar dahil) görmesi için ücretsiz bir Supabase projesi bağlanır. Supabase; giriş (Google dahil), veritabanı ve dosya deposunu tek yerde, kredi kartı istemeden sunar.

### 1. Supabase projesi aç (5 dakika)
1. https://supabase.com adresinde ücretsiz hesap aç, **New project** ile proje oluştur (ör. `tarihgram`, bölge: Frankfurt).
2. Sol menüden **SQL Editor > New query**: `supabase/kurulum.sql` dosyasının tamamını yapıştır ve **Run**'a bas. Tablolar, güvenlik kuralları ve `medya` adlı fotoğraf/video deposu kurulur.
3. Proje ana sayfasındaki **Connect** düğmesinden (ya da **Project Settings > API Keys**) **Project URL** ile **Publishable key**'i kopyala. Eski projelerde bu anahtarın adı **anon public**'tir; ikisi de olur.
4. `index.html` dosyasının en üstündeki betikte şu iki satırı doldur:
   ```js
   var SUPABASE_URL = "https://xxxxxxxx.supabase.co";
   var SUPABASE_ANON_KEY = "eyJhbGciOi...";
   ```
   Bu iki değer gizli değildir; sitede bulunmaları normaldir. Veriyi veritabanındaki kurallar korur.

### 2. Yönetici (admin) olmak
Siteye **ilk kayıt olan kişi otomatik olarak yönetici olur**. Kurulumdan hemen sonra siteye ilk sen kayıt ol. Menünün en altında **Yönetim** bölümü belirir:
- Tüm gönderileri ve yorumları görür, istediğini silersin.
- Üyeleri listeler (e-postaları yalnızca yöneticiye görünür), bir üyeyi **kısıtlayabilir** (paylaşım ve yorum yapamaz) ya da **yönetici yapabilirsin**.

Gerekirse bir hesabı elle yönetici yapmak için `supabase/kurulum.sql` dosyasının en altındaki komutu kullan.

### 3. E-posta ve Google ile giriş
- **Authentication > URL Configuration**: **Site URL** alanına sitenin adresini yaz (ör. `https://kullaniciadi.github.io/depo-adi/`) ve aynı adresi **Redirect URLs** listesine ekle.
- E-posta ile kayıtta Supabase onay e-postası gönderir; kullanıcı bağlantıya tıkladıktan sonra giriş yapar.
- **Google ile giriş** için: Google Cloud Console'da (https://console.cloud.google.com) bir OAuth istemcisi (Web application) oluştur. "Authorized redirect URIs" alanına Supabase'in **Authentication > Providers > Google** sayfasında yazan geri dönüş adresini ekle. Oradan aldığın Client ID ve Client Secret'ı aynı Supabase sayfasına yapıştırıp Google'ı etkinleştir.

### 4. Yayınlama (GitHub Pages)
1. Değişiklikleri `main` dalına birleştir.
2. Depo **Settings > Pages > Build and deployment > Source** alanında **GitHub Actions**'ı seç.
3. `.github/workflows/yayinla.yml` her `main` gönderiminde siteyi otomatik yayınlar. Adres: `https://<kullanıcı-adı>.github.io/<depo-adı>/`.

GitHub Pages, ücretsiz hesaplarda yalnızca herkese açık (public) depolarda çalışır. Depo gizliyse ya herkese açık yap ya da klasörü Netlify (https://app.netlify.com/drop) gibi bir servise sürükleyip bırak.

### Ücretsiz sınırlar
Supabase ücretsiz planında 500 MB veritabanı ve 1 GB dosya deposu vardır; video başına en fazla 50 MB yüklenebilir. Kullanılmayan ücretsiz projeler bir hafta hareketsiz kalınca duraklatılır, panelden tek tıkla yeniden açılır.

## Önizleme modu ve sınırlar

Supabase bağlanmadan önce gönderiler (fotoğraf ve videolarıyla tarayıcının IndexedDB deposunda), beğeniler, kayıtlar, yorumlar ve profil yalnızca o tarayıcıda saklanır. Önizlemede o tarayıcıda ilk açılan hesap yöneticidir. Supabase bağlanınca gönderiler, yorumlar, beğeniler, kayıtlar ve profiller herkese açık veritabanına taşınır. **Geçmiş** her zaman cihazda kalır. "Gönder" penceresindeki kişilere gönderim, mesajlaşma bölümü gelene kadar göstermeliktir; bağlantıyı kopyalama gerçekten çalışır.

Paylaşım sırasında mekân ve şehir alanları yazarken öneri verir ("top" → Topkapı Sarayı, "iskan" → İstanbul, Türkiye). Liste `data/mekanlar.json` (185 mekân) ve `data/sehirler.json` dosyalarından gelir; `tools/mekanlar_uret.py` içine satır ekleyip çalıştırarak yeni mekân eklenebilir. Listede olmayan bir yer haritada aranınca site yayındayken OpenStreetMap'te (Nominatim) aranır.

## Dosyalar

- `index.html`: Uygulamanın tamamı (HTML, CSS, JS)
- `tools/tek-dosya.py`: Her şeyi içine gömen tek dosyalık sürümü üretir (`python3 tools/tek-dosya.py cikti.html`)
- `supabase/kurulum.sql`: Veritabanı, güvenlik kuralları ve dosya deposu kurulumu
- `.github/workflows/yayinla.yml`: GitHub Pages'e otomatik yayın
- `data/mekanlar.json`, `data/sehirler.json`: Arama önerileri için mekân ve şehir listeleri (`tools/mekanlar_uret.py` üretir)
- `data/gonderiler.json`: Örnek gönderiler, mekân açıklamaları, tarihçeler, benzer mekânlar, fotoğraf kaynakları
- `data/kiyilar.json`: Türkiye ve çevresinin kıyı çizgileri (Natural Earth 1:10m), internet haritası yüklenemezse kullanılır
- `assets/fiziki-harita.jpg`: Fiziki dünya haritası (NASA Blue Marble, kamu malı)
- `assets/foto/`, `assets/video/`: Wikimedia Commons'tan alınan fotoğraf ve videolar. Her birinin yazarı ve lisansı gönderi sayfasında "Fotoğraf ve video kaynakları" altında listelenir.

#!/usr/bin/env python3
"""data/mekanlar.json ve data/sehirler.json dosyalarını üretir.
Satır biçimi: ad | diğer adlar (virgülle) | il/şehir | ülke | tür | enlem | boylam | kısa açıklama"""
import json, os
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEKANLAR = """
Topkapı Sarayı|Topkapi Palace,Topkapı Müzesi|İstanbul|Türkiye|Saray|41.0115|28.9834|Osmanlı padişahlarının yaklaşık 400 yıl yaşadığı saray.
Ayasofya|Hagia Sophia,Ayasofya Camii,Ayasofya-i Kebir|İstanbul|Türkiye|Cami ve dini yapı|41.0086|28.9802|537'de tamamlanan dev kubbeli Bizans bazilikası, bugün cami.
Sultanahmet Camii|Mavi Cami,Blue Mosque|İstanbul|Türkiye|Cami ve dini yapı|41.0054|28.9768|Altı minareli, mavi çinileriyle 17. yüzyıl camisi.
Sultanahmet Meydanı (Hipodrom)|Hipodrom,At Meydanı,Dikilitaş|İstanbul|Türkiye|Tarihi yapı|41.0063|28.9753|Bizans'ın araba yarışı alanı; Dikilitaş ve Yılanlı Sütun burada.
Yerebatan Sarnıcı|Basilica Cistern,Yerebatan|İstanbul|Türkiye|Tarihi yapı|41.0084|28.9779|336 sütunlu, 6. yüzyıldan kalma yeraltı su deposu.
Dolmabahçe Sarayı|Dolmabahce Palace|İstanbul|Türkiye|Saray|41.0392|29.0004|Boğaz kıyısındaki 19. yüzyıl Osmanlı sarayı.
Beylerbeyi Sarayı|Beylerbeyi Palace|İstanbul|Türkiye|Saray|41.0425|29.0397|Anadolu yakasında, Sultan Abdülaziz'in yazlık sarayı.
Çırağan Sarayı|Ciragan Palace|İstanbul|Türkiye|Saray|41.0436|29.0153|Boğaz kıyısında, bugün otel olarak kullanılan saray.
Yıldız Sarayı|Yildiz Palace|İstanbul|Türkiye|Saray|41.0490|29.0110|II. Abdülhamid'in korulukla çevrili saray kompleksi.
Süleymaniye Camii|Suleymaniye Mosque|İstanbul|Türkiye|Cami ve dini yapı|41.0162|28.9639|Mimar Sinan'ın Kanuni için yaptığı külliye.
Rüstem Paşa Camii|Rustem Pasha Mosque|İstanbul|Türkiye|Cami ve dini yapı|41.0177|28.9699|İznik çinileriyle kaplı küçük Sinan camisi.
Ortaköy Camii|Büyük Mecidiye Camii|İstanbul|Türkiye|Cami ve dini yapı|41.0473|29.0270|Boğaz kıyısında barok üsluplu cami.
Eyüp Sultan Camii|Eyüpsultan|İstanbul|Türkiye|Cami ve dini yapı|41.0477|28.9339|Fetihten sonra yapılan ilk selatin camilerinden.
Kariye Camii|Khora,Chora Kilisesi|İstanbul|Türkiye|Cami ve dini yapı|41.0312|28.9390|Bizans mozaik ve freskleriyle ünlü yapı.
Aya İrini|Hagia Irene|İstanbul|Türkiye|Cami ve dini yapı|41.0094|28.9813|Topkapı Sarayı avlusundaki Bizans kilisesi.
Kapalıçarşı|Grand Bazaar,Kapalı Çarşı|İstanbul|Türkiye|Tarihi çarşı ve han|41.0107|28.9681|60'tan fazla sokağıyla dünyanın en eski kapalı çarşılarından.
Mısır Çarşısı|Spice Bazaar,Baharatçılar Çarşısı|İstanbul|Türkiye|Tarihi çarşı ve han|41.0166|28.9706|Eminönü'nde 17. yüzyıldan kalma baharat çarşısı.
Galata Kulesi|Galata Tower|İstanbul|Türkiye|Kale ve kule|41.0256|28.9741|Cenevizlilerin 1348'de yaptığı kule.
Kız Kulesi|Maiden's Tower,Leander|İstanbul|Türkiye|Kale ve kule|41.0211|29.0041|Üsküdar açığında küçük bir adacık üzerindeki kule.
Rumeli Hisarı|Rumelihisarı|İstanbul|Türkiye|Kale ve kule|41.0847|29.0569|Fetihten önce Boğaz'ın en dar yerine yapılan kale.
Anadolu Hisarı|Anadoluhisarı|İstanbul|Türkiye|Kale ve kule|41.0822|29.0675|Boğaz'ın Anadolu yakasındaki ilk Osmanlı kalesi.
Yedikule Hisarı|Yedikule Zindanları|İstanbul|Türkiye|Kale ve kule|40.9934|28.9229|Kara surlarının ucundaki yedi kuleli hisar.
Beyazıt Yangın Kulesi|Beyazıt Kulesi|İstanbul|Türkiye|Kale ve kule|41.0115|28.9640|İstanbul Üniversitesi bahçesindeki gözetleme kulesi.
Bozdoğan Su Kemeri|Valens Su Kemeri,Valens Aqueduct|İstanbul|Türkiye|Tarihi yapı|41.0158|28.9558|4. yüzyıldan kalma Roma su kemeri.
İstanbul Arkeoloji Müzeleri|Arkeoloji Müzesi|İstanbul|Türkiye|Müze|41.0117|28.9813|İskender Lahdi'nin de bulunduğu müze kompleksi.
Pera Müzesi|Kaplumbağa Terbiyecisi|İstanbul|Türkiye|Müze|41.0317|28.9752|Oryantalist resim koleksiyonuyla Beyoğlu'ndaki müze.
Selimiye Camii|Selimiye Mosque|Edirne|Türkiye|Cami ve dini yapı|41.6779|26.5594|Mimar Sinan'ın "ustalık eserim" dediği cami.
Bursa Ulu Camii|Ulucami|Bursa|Türkiye|Cami ve dini yapı|40.1840|29.0617|20 kubbeli erken Osmanlı camisi.
Yeşil Türbe|Yesil Turbe|Bursa|Türkiye|Cami ve dini yapı|40.1817|29.0727|Çelebi Mehmed'in yeşil çinili türbesi.
Koza Han|Kozahan|Bursa|Türkiye|Tarihi çarşı ve han|40.1836|29.0626|İpek ticaretinin merkezi olan 15. yüzyıl hanı.
Cumalıkızık|Cumalikizik|Bursa|Türkiye|Tarihi kent|40.1752|29.1717|Osmanlı kuruluş döneminden kalma köy.
Troya|Truva,Troy|Çanakkale|Türkiye|Antik kent|39.9575|26.2389|Dokuz yerleşim katmanıyla efsanevi kent.
Assos|Behramkale|Çanakkale|Türkiye|Antik kent|39.4897|26.3371|Athena Tapınağı'yla Ege'ye bakan antik kent.
Çanakkale Şehitler Abidesi|Gelibolu,Şehitler Abidesi|Çanakkale|Türkiye|Anıt|40.0496|26.2215|Çanakkale Savaşı şehitleri anısına dikilen anıt.
Ephesus (Efes Antik Kenti)|Efes,Ephesus|İzmir|Türkiye|Antik kent|37.9395|27.3417|Celsus Kütüphanesi ve Büyük Tiyatro'yla Ege'nin en büyük antik kenti.
Bergama (Pergamon)|Pergamon,Bergama Akropolü|İzmir|Türkiye|Antik kent|39.1325|27.1844|Dik yamaçtaki tiyatrosu ve Zeus Sunağı'yla Helenistik başkent.
Meryem Ana Evi|Meryemana|İzmir|Türkiye|Cami ve dini yapı|37.9119|27.3335|Bülbül Dağı'nda hac yeri olan küçük yapı.
Aziz Yuhanna Bazilikası|St. Jean,Ayasuluk|İzmir|Türkiye|Cami ve dini yapı|37.9520|27.3684|Selçuk'ta Ayasuluk Tepesi'ndeki Bizans bazilikası.
İzmir Saat Kulesi|Konak Saat Kulesi|İzmir|Türkiye|Kale ve kule|38.4189|27.1287|Konak Meydanı'nın simgesi olan 1901 tarihli kule.
Kadifekale|Pagos|İzmir|Türkiye|Kale ve kule|38.4136|27.1449|Körfeze bakan Helenistik dönem kalesi.
Smyrna Agorası|İzmir Agorası|İzmir|Türkiye|Antik kent|38.4183|27.1393|Kent merkezindeki Roma dönemi pazar yeri.
Şirince|Sirince|İzmir|Türkiye|Tarihi kent|37.9441|27.4291|Taş evleriyle Selçuk yakınındaki dağ köyü.
Afrodisias|Aphrodisias|Aydın|Türkiye|Antik kent|37.7086|28.7238|Heykel atölyeleri ve stadyumuyla antik kent.
Priene|Priene Antik Kenti|Aydın|Türkiye|Antik kent|37.6597|27.2975|Izgara planlı küçük bir İyon kenti.
Milet|Miletos|Aydın|Türkiye|Antik kent|37.5303|27.2781|Thales'in kenti; büyük tiyatrosu ayakta.
Didim Apollon Tapınağı|Didyma|Aydın|Türkiye|Antik kent|37.3850|27.2563|Dev sütunlarıyla kehanet tapınağı.
Hierapolis (Pamukkale)|Hierapolis|Denizli|Türkiye|Antik kent|37.9257|29.1260|Travertenlerin üzerinde Roma dönemi şifa kenti.
Pamukkale Travertenleri|Pamukkale|Denizli|Türkiye|Doğal alan|37.9214|29.1205|Bembeyaz kireç taşı havuzları.
Laodikeia|Laodicea|Denizli|Türkiye|Antik kent|37.8357|29.1076|Kazılarla ortaya çıkan büyük Roma kenti.
Bodrum Kalesi|St. Peter Kalesi,Sualtı Arkeoloji Müzesi|Muğla|Türkiye|Kale ve kule|37.0319|27.4290|Rodos Şövalyeleri'nin kalesi, sualtı arkeoloji müzesi.
Halikarnas Mozolesi|Mausoleum,Mozole|Muğla|Türkiye|Antik kent|37.0379|27.4241|Antik dünyanın yedi harikasından birinin kalıntıları.
Kaunos|Kaunos Kral Mezarları,Dalyan|Muğla|Türkiye|Antik kent|36.8270|28.6230|Dalyan'daki kaya mezarları ve antik kent.
Knidos|Knidos Antik Kenti|Muğla|Türkiye|Antik kent|36.6858|27.3746|Datça Yarımadası'nın ucunda iki limanlı kent.
Amintas Kaya Mezarları|Fethiye Kaya Mezarları|Muğla|Türkiye|Antik kent|36.6194|29.1236|Fethiye'deki Likya kaya mezarları.
Kayaköy|Karmylassos,Levissi|Muğla|Türkiye|Tarihi kent|36.5759|29.0880|Terk edilmiş taş evleriyle hayalet köy.
Saklıkent Kanyonu|Saklıkent|Muğla|Türkiye|Doğal alan|36.4697|29.4060|Buz gibi suyuyla derin kanyon.
Stratonikeia|Eskihisar|Muğla|Türkiye|Antik kent|37.3147|28.0628|Osmanlı köyüyle iç içe antik kent.
Aspendos|Aspendos Tiyatrosu|Antalya|Türkiye|Antik kent|36.9389|31.1722|Dünyanın en iyi korunmuş Roma tiyatrolarından.
Perge|Perge Antik Kenti|Antalya|Türkiye|Antik kent|36.9614|30.8544|Sütunlu caddesi ve stadyumuyla Pamfilya kenti.
Side Antik Kenti|Side,Apollon Tapınağı|Antalya|Türkiye|Antik kent|36.7673|31.3888|Deniz kenarındaki Apollon Tapınağı'yla ünlü.
Termessos|Termessos Antik Kenti|Antalya|Türkiye|Antik kent|37.0347|30.4656|Dağın tepesinde, İskender'in alamadığı kent.
Olimpos|Olympos,Çıralı|Antalya|Türkiye|Antik kent|36.3965|30.4724|Ormanın içinde Likya kenti.
Phaselis|Faselis|Antalya|Türkiye|Antik kent|36.5244|30.5508|Üç limanlı antik liman kenti.
Myra|Myra Kaya Mezarları,Demre|Antalya|Türkiye|Antik kent|36.2593|29.9853|Likya kaya mezarları ve tiyatro.
Aziz Nikolaos Kilisesi|Noel Baba Kilisesi,St. Nicholas|Antalya|Türkiye|Cami ve dini yapı|36.2427|29.9849|Demre'de Noel Baba'nın kilisesi.
Patara|Patara Antik Kenti|Antalya|Türkiye|Antik kent|36.2600|29.3149|Likya Birliği'nin meclis binasıyla antik kent.
Simena (Kaleköy)|Kaleköy,Kekova|Antalya|Türkiye|Kale ve kule|36.1928|29.8630|Kekova'da kalesi ve batık kentiyle köy.
Kaleiçi|Kaleiçi Antalya|Antalya|Türkiye|Tarihi kent|36.8841|30.7056|Antalya'nın surlarla çevrili eski kenti.
Hadrian Kapısı|Üçkapılar|Antalya|Türkiye|Tarihi yapı|36.8854|30.7088|MS 130'da yapılan Roma takı.
Alanya Kalesi|Alanya Castle|Antalya|Türkiye|Kale ve kule|36.5389|31.9918|Yarımadanın tepesindeki Selçuklu kalesi.
Kızıl Kule|Kızılkule|Antalya|Türkiye|Kale ve kule|36.5414|32.0003|Alanya limanındaki sekizgen Selçuklu kulesi.
Sagalassos|Sagalassos Antik Kenti|Burdur|Türkiye|Antik kent|37.6766|30.5175|Toros Dağları'nda anıtsal çeşmesiyle kent.
Kızkalesi|Korykos|Mersin|Türkiye|Kale ve kule|36.4592|34.1531|Denizin içindeki ortaçağ kalesi.
Cennet ve Cehennem Obrukları|Cennet Cehennem|Mersin|Türkiye|Doğal alan|36.4511|34.1047|Silifke yakınındaki dev obruklar.
Kleopatra Kapısı|Tarsus|Mersin|Türkiye|Tarihi yapı|36.9157|34.8913|Tarsus'taki antik kent kapısı.
Silifke Kalesi|Silifke|Mersin|Türkiye|Kale ve kule|36.3769|33.9277|Göksu vadisine bakan ortaçağ kalesi.
Adana Taşköprü|Taşköprü|Adana|Türkiye|Köprü|36.9852|35.3375|Seyhan üzerindeki Roma köprüsü.
Yılankale|Yılan Kalesi|Adana|Türkiye|Kale ve kule|37.0156|35.7460|Çukurova ovasına bakan Ermeni kalesi.
Aziz Petrus Kilisesi|St. Pierre Kilisesi|Hatay|Türkiye|Cami ve dini yapı|36.2126|36.1708|Antakya'da kayaya oyulmuş erken Hristiyan kilisesi.
Zeugma Mozaik Müzesi|Zeugma Müzesi,Çingene Kızı|Gaziantep|Türkiye|Müze|37.0767|37.3722|Çingene Kızı mozaiğinin sergilendiği müze.
Zeugma Antik Kenti|Zeugma|Gaziantep|Türkiye|Antik kent|37.0566|37.8701|Fırat kıyısındaki Kommagene ve Roma kenti.
Gaziantep Kalesi|Antep Kalesi|Gaziantep|Türkiye|Kale ve kule|37.0663|37.3833|Kent merkezindeki tarihi kale.
Göbeklitepe|Gobekli Tepe|Şanlıurfa|Türkiye|Antik kent|37.2232|38.9224|Yaklaşık 11.600 yıllık dünyanın bilinen en eski tapınak alanı.
Balıklıgöl|Halil-ür Rahman Gölü|Şanlıurfa|Türkiye|Cami ve dini yapı|37.1458|38.7838|Hz. İbrahim'in ateşe atıldığına inanılan yer.
Harran|Harran Ören Yeri,Kümbet Evler|Şanlıurfa|Türkiye|Antik kent|36.8628|39.0310|Kümbet evleri ve antik üniversitesiyle kent.
Nemrut Dağı|Nemrut|Adıyaman|Türkiye|Anıt|37.9808|38.7408|Kommagene kralı Antiochos'un dev heykelli tümülüsü.
Mardin Eski Şehir|Mardin|Mardin|Türkiye|Tarihi kent|37.3129|40.7350|Mezopotamya ovasına bakan taş evli kent.
Deyrulzafaran Manastırı|Mor Hananyo|Mardin|Türkiye|Cami ve dini yapı|37.2919|40.7835|Süryani Ortodoks manastırı.
Dara Antik Kenti|Dara|Mardin|Türkiye|Antik kent|37.1767|40.9433|Kayaya oyulmuş sarnıçlarıyla Bizans sınır kenti.
Midyat|Midyat Taş Evleri|Mardin|Türkiye|Tarihi kent|37.4180|41.3389|Taş konakları ve telkari ustalarıyla kent.
Hasankeyf|Hasankeyf Kalesi|Batman|Türkiye|Tarihi kent|37.7130|41.4140|Dicle kıyısında binlerce yıllık yerleşim.
Diyarbakır Surları|Hevsel Bahçeleri,Diyarbakır Kalesi|Diyarbakır|Türkiye|Kale ve kule|37.9103|40.2367|Dünyanın en uzun kent surlarından.
On Gözlü Köprü|Dicle Köprüsü|Diyarbakır|Türkiye|Köprü|37.8817|40.2462|Dicle üzerindeki 11. yüzyıl köprüsü.
Akdamar Kilisesi|Akdamar Adası|Van|Türkiye|Cami ve dini yapı|38.3407|43.0333|Van Gölü'ndeki adada 10. yüzyıl kilisesi.
Van Kalesi|Tuşpa|Van|Türkiye|Kale ve kule|38.5044|43.3437|Urartu başkenti Tuşpa'nın kalesi.
İshak Paşa Sarayı|Ishak Pasa Palace|Ağrı|Türkiye|Saray|39.5223|44.1286|Doğubayazıt'ta 18. yüzyıl saray kompleksi.
Ağrı Dağı|Ararat|Ağrı|Türkiye|Doğal alan|39.7019|44.2983|Türkiye'nin en yüksek dağı, 5.137 m.
Ani Ören Yeri|Ani,Ani Harabeleri|Kars|Türkiye|Antik kent|40.5075|43.5728|"Bin bir kiliseli" ortaçağ başkenti.
Çifte Minareli Medrese|Erzurum Çifte Minare|Erzurum|Türkiye|Cami ve dini yapı|39.9046|41.2770|Erzurum'un simgesi olan Selçuklu medresesi.
Sümela Manastırı|Sumela,Meryem Ana Manastırı|Trabzon|Türkiye|Cami ve dini yapı|40.6903|39.6581|Sarp kayalığa kurulmuş Bizans manastırı.
Trabzon Ayasofya|Ayasofya Trabzon|Trabzon|Türkiye|Cami ve dini yapı|41.0050|39.6867|Freskleriyle 13. yüzyıl Bizans yapısı.
Uzungöl|Uzun Göl|Trabzon|Türkiye|Doğal alan|40.6197|40.2925|Dağlar arasındaki göl ve köy.
Divriği Ulu Camii ve Darüşşifası|Divriği|Sivas|Türkiye|Cami ve dini yapı|39.3713|38.1203|Taş işçiliğiyle UNESCO listesindeki yapı.
Sivas Gök Medrese|Gök Medrese|Sivas|Türkiye|Cami ve dini yapı|39.7470|37.0193|Çini kaplı Selçuklu medresesi.
Kültepe (Kaniş)|Kaniş,Karum|Kayseri|Türkiye|Antik kent|38.8503|35.6350|Anadolu'nun ilk yazılı belgelerinin bulunduğu höyük.
Göreme, Kapadokya|Göreme,Kapadokya,Cappadocia|Nevşehir|Türkiye|Kaya yerleşimi|38.6431|34.8289|Peri bacaları ve balonlarıyla Kapadokya'nın kalbi.
Göreme Açık Hava Müzesi|Karanlık Kilise|Nevşehir|Türkiye|Müze|38.6398|34.8452|Freskli kaya kiliselerinin bulunduğu müze.
Uçhisar Kalesi|Uçhisar|Nevşehir|Türkiye|Kale ve kule|38.6297|34.8044|Bölgenin en yüksek noktasındaki kaya kalesi.
Zelve Açık Hava Müzesi|Zelve|Nevşehir|Türkiye|Kaya yerleşimi|38.6717|34.8611|1950'lere kadar yaşanan kaya köyü.
Kaymaklı Yeraltı Şehri|Kaymaklı|Nevşehir|Türkiye|Kaya yerleşimi|38.4617|34.7514|Dar tünellerle bağlı yeraltı katları.
Derinkuyu Yeraltı Şehri|Derinkuyu|Nevşehir|Türkiye|Kaya yerleşimi|38.3735|34.7346|Binlerce kişilik çok katlı yeraltı kenti.
Ihlara Vadisi|Ihlara|Aksaray|Türkiye|Doğal alan|38.2483|34.2989|Kaya kiliseleriyle dolu kanyon.
Sultanhanı Kervansarayı|Sultanhanı|Aksaray|Türkiye|Tarihi çarşı ve han|38.2494|33.5465|Anadolu'nun en büyük Selçuklu kervansaraylarından.
Soğanlı Vadisi|Soğanlı|Kayseri|Türkiye|Doğal alan|38.3381|35.0711|Kaya kiliseleriyle sessiz bir vadi.
Mevlana Müzesi|Mevlana Türbesi,Yeşil Kubbe|Konya|Türkiye|Müze|37.8708|32.5047|Mevlana Celaleddin Rumi'nin türbesi.
Çatalhöyük|Catalhoyuk|Konya|Türkiye|Antik kent|37.6676|32.8282|9.000 yıllık Neolitik yerleşim.
Alaeddin Camii|Alaaddin Tepesi|Konya|Türkiye|Cami ve dini yapı|37.8738|32.4928|Selçuklu başkentinin ulu camisi.
Anıtkabir|Atatürk'ün Anıt Mezarı|Ankara|Türkiye|Anıt|39.9250|32.8369|Mustafa Kemal Atatürk'ün anıt mezarı.
Ankara Kalesi|Hisar|Ankara|Türkiye|Kale ve kule|39.9410|32.8645|Ulus'ta kente bakan tarihi kale.
Anadolu Medeniyetleri Müzesi|Medeniyetler Müzesi|Ankara|Türkiye|Müze|39.9384|32.8616|Paleolitikten Osmanlı'ya Anadolu eserleri.
Augustus Tapınağı|Monumentum Ancyranum|Ankara|Türkiye|Antik kent|39.9447|32.8574|İmparator Augustus'un vasiyetinin yazılı olduğu tapınak.
Gordion|Gordion Antik Kenti,Midas Tümülüsü|Ankara|Türkiye|Antik kent|39.6540|31.9760|Frigya'nın başkenti, Midas Tümülüsü.
Hattuşa|Hattuşaş,Boğazköy|Çorum|Türkiye|Antik kent|40.0195|34.6153|Hitit İmparatorluğu'nun başkenti.
Alacahöyük|Alaca Höyük|Çorum|Türkiye|Antik kent|40.2352|34.6944|Sfenksli kapısıyla Hitit yerleşimi.
Safranbolu|Safranbolu Evleri|Karabük|Türkiye|Tarihi kent|41.2447|32.6945|Osmanlı konaklarıyla korunmuş kent.
Amasya Kral Kaya Mezarları|Pontus Kral Mezarları|Amasya|Türkiye|Antik kent|40.6527|35.8288|Yeşilırmak'a bakan Pontus kral mezarları.
Ahlat Selçuklu Mezarlığı|Ahlat|Bitlis|Türkiye|Tarihi yapı|38.7584|42.4680|Binlerce işlemeli mezar taşıyla mezarlık.
Odunpazarı|Odunpazarı Evleri|Eskişehir|Türkiye|Tarihi kent|39.7622|30.5254|Renkli Osmanlı evleriyle eski mahalle.
Aizanoi|Zeus Tapınağı Çavdarhisar|Kütahya|Türkiye|Antik kent|39.1997|29.6087|Zeus Tapınağı'yla Frigya kenti.
Sardes|Sard,Sardis|Manisa|Türkiye|Antik kent|38.4883|28.0400|Lidya'nın başkenti, Artemis Tapınağı.
Harput|Harput Kalesi|Elazığ|Türkiye|Tarihi kent|38.7072|39.2556|Kalesi ve camileriyle tarihi kent.
Arslantepe|Arslantepe Höyüğü|Malatya|Türkiye|Antik kent|38.3818|38.3613|Devletin doğuşuna tanıklık eden höyük.
Kolezyum|Colosseum,Kolosseum,Colosseo|Roma|İtalya|Antik kent|41.8902|12.4922|50.000 kişilik Roma amfitiyatrosu.
Pantheon|Panteon|Roma|İtalya|Cami ve dini yapı|41.8986|12.4769|Dev kubbesiyle Roma tapınağı.
Roma Forumu|Forum Romanum|Roma|İtalya|Antik kent|41.8925|12.4853|Antik Roma'nın kamusal merkezi.
Aziz Petrus Bazilikası|Vatikan,St. Peter|Vatikan|Vatikan|Cami ve dini yapı|41.9022|12.4539|Vatikan'daki Rönesans bazilikası.
Pompeii|Pompei|Napoli|İtalya|Antik kent|40.7489|14.4848|MS 79'da Vezüv'ün külleri altında kalan kent.
Pisa Kulesi|Eğik Kule,Torre di Pisa|Pisa|İtalya|Kale ve kule|43.7230|10.3966|Eğik duruşuyla ünlü çan kulesi.
Floransa Katedrali|Duomo,Santa Maria del Fiore|Floransa|İtalya|Cami ve dini yapı|43.7731|11.2560|Brunelleschi'nin kubbesiyle katedral.
San Marco Bazilikası|San Marco|Venedik|İtalya|Cami ve dini yapı|45.4345|12.3397|Altın mozaikli Venedik bazilikası.
Akropolis|Acropolis,Parthenon|Atina|Yunanistan|Antik kent|37.9715|23.7257|Parthenon'un bulunduğu kutsal tepe.
Delfi|Delphi|Delfi|Yunanistan|Antik kent|38.4824|22.5010|Antik dünyanın kehanet merkezi.
Meteora (Yunanistan)|Meteora|Kalambaka|Yunanistan|Doğal alan|39.7217|21.6306|Kaya sütunlarının tepesinde manastırlar.
Knossos|Knosos|Girit|Yunanistan|Antik kent|35.2980|25.1631|Minos uygarlığının sarayı.
Giza Piramitleri|Keops Piramidi,Sfenks,Gize|Kahire|Mısır|Anıt|29.9792|31.1342|Antik dünyanın yedi harikasından ayakta kalan tek eser.
Karnak Tapınağı|Karnak|Luksor|Mısır|Antik kent|25.7188|32.6573|Dev sütun salonuyla tapınak kompleksi.
Abu Simbel|Ebu Simbel|Asvan|Mısır|Anıt|22.3372|31.6258|II. Ramses'in kayaya oyulmuş tapınakları.
Petra|Petra Antik Kenti,El Hazne|Maan|Ürdün|Antik kent|30.3285|35.4444|Pembe kayalara oyulmuş Nebati kenti.
Ceraş (Ürdün)|Jerash,Gerasa|Ceraş|Ürdün|Antik kent|32.2808|35.8917|Sütunlu caddeleriyle Roma kenti.
Baalbek|Heliopolis|Baalbek|Lübnan|Antik kent|34.0069|36.2039|Dev Roma tapınaklarıyla kent.
Kudüs Eski Şehir|Kudüs,Jerusalem|Kudüs|Filistin|Tarihi kent|31.7767|35.2345|Üç büyük dinin kutsal kenti.
Kubbetüs Sahra|Dome of the Rock,Mescid-i Aksa|Kudüs|Filistin|Cami ve dini yapı|31.7780|35.2354|Altın kubbeli 7. yüzyıl yapısı.
Mescid-i Haram|Kabe,Kâbe|Mekke|Suudi Arabistan|Cami ve dini yapı|21.4225|39.8262|Kâbe'nin bulunduğu cami.
Persepolis|Taht-ı Cemşid|Şiraz|İran|Antik kent|29.9355|52.8916|Pers İmparatorluğu'nun tören başkenti.
Nakş-ı Cihan Meydanı|İmam Meydanı|İsfahan|İran|Tarihi yapı|32.6575|51.6777|Camileri ve sarayıyla dev meydan.
Registan Meydanı|Registan|Semerkant|Özbekistan|Tarihi yapı|39.6547|66.9758|Üç medreseyle çevrili meydan.
Buhara Eski Şehir|Buhara|Buhara|Özbekistan|Tarihi kent|39.7747|64.4286|İpek Yolu'nun medreseli kenti.
Bakü İçerişehir|Kız Kalesi Bakü,İçeri Şehir|Bakü|Azerbaycan|Tarihi kent|40.3661|49.8372|Kız Kalesi'yle surlu eski kent.
Tac Mahal|Taj Mahal|Agra|Hindistan|Anıt|27.1751|78.0421|Beyaz mermerden Babür türbesi.
Çin Seddi|Great Wall,Mutianyu|Pekin|Çin|Kale ve kule|40.4319|116.5704|Binlerce kilometrelik savunma duvarı.
Yasak Şehir|Forbidden City|Pekin|Çin|Saray|39.9163|116.3972|Çin imparatorlarının sarayı.
Angkor Wat|Angkor|Siem Reap|Kamboçya|Cami ve dini yapı|13.4125|103.8670|Dünyanın en büyük tapınak kompleksi.
Kinkaku-ji|Altın Köşk|Kyoto|Japonya|Cami ve dini yapı|35.0394|135.7292|Altın kaplı Zen tapınağı.
Machu Picchu|Maçu Pikçu|Cusco|Peru|Antik kent|-13.1631|-72.5450|And Dağları'ndaki İnka kenti.
Chichén Itzá|Chichen Itza,Kukulkan|Yucatán|Meksika|Antik kent|20.6843|-88.5678|El Castillo piramidiyle Maya kenti.
Teotihuacan|Güneş Piramidi|Meksiko|Meksika|Antik kent|19.6925|-98.8438|Güneş ve Ay piramitleriyle antik kent.
Özgürlük Heykeli|Statue of Liberty|New York|ABD|Anıt|40.6892|-74.0445|1886'da Fransa'nın hediye ettiği heykel.
Stonehenge|Stonehenge|Wiltshire|Birleşik Krallık|Anıt|51.1789|-1.8262|Dev taşlardan tarih öncesi anıt.
Londra Kulesi|Tower of London|Londra|Birleşik Krallık|Kale ve kule|51.5081|-0.0759|Thames kıyısındaki ortaçağ kalesi.
Versay Sarayı|Versailles|Versay|Fransa|Saray|48.8049|2.1204|XIV. Louis'nin görkemli sarayı.
Louvre Müzesi|Louvre,Mona Lisa|Paris|Fransa|Müze|48.8606|2.3376|Mona Lisa'nın sergilendiği müze.
Eyfel Kulesi|Eiffel Tower,Eiffel|Paris|Fransa|Kale ve kule|48.8584|2.2945|1889'da yapılan demir kule.
Notre-Dame Katedrali|Notre Dame|Paris|Fransa|Cami ve dini yapı|48.8530|2.3499|Gotik mimarinin simge katedrali.
Neuschwanstein Şatosu|Neuschwanstein|Füssen|Almanya|Saray|47.5576|10.7498|Masal şatosu görünümlü 19. yüzyıl şatosu.
Brandenburg Kapısı|Brandenburger Tor|Berlin|Almanya|Anıt|52.5163|13.3777|Berlin'in simgesi olan neoklasik kapı.
Elhamra Sarayı|Alhambra|Granada|İspanya|Saray|37.1761|-3.5881|Endülüs'ün süslü saray ve kalesi.
Sagrada Familia|Sagrada Família|Barselona|İspanya|Cami ve dini yapı|41.4036|2.1744|Gaudí'nin hâlâ süren bazilikası.
Kurtuba Camii|Mezquita,Córdoba|Kurtuba|İspanya|Cami ve dini yapı|37.8789|-4.7794|Çift kemerli sütun ormanıyla Endülüs camisi.
Prag Kalesi|Prague Castle|Prag|Çekya|Kale ve kule|50.0911|14.4016|Dünyanın en büyük eski kale komplekslerinden.
Schönbrunn Sarayı|Schonbrunn|Viyana|Avusturya|Saray|48.1845|16.3122|Habsburgların yazlık sarayı.
Kremlin ve Kızıl Meydan|Kremlin,Kızıl Meydan|Moskova|Rusya|Saray|55.7520|37.6175|Rusya'nın yönetim merkezi ve meydanı.
Kış Sarayı (Ermitaj)|Ermitaj,Hermitage|St. Petersburg|Rusya|Saray|59.9398|30.3146|Çarların sarayı, bugün Ermitaj Müzesi.
Mostar Köprüsü|Stari Most|Mostar|Bosna-Hersek|Köprü|43.3373|17.8150|Mimar Hayreddin'in 1566 tarihli köprüsü.
Gazi Hüsrev Bey Camii|Gazi Husrev-beg|Saraybosna|Bosna-Hersek|Cami ve dini yapı|43.8594|18.4289|Saraybosna'nın Osmanlı camisi.
Dubrovnik Surları|Dubrovnik|Dubrovnik|Hırvatistan|Kale ve kule|42.6407|18.1077|Adriyatik'e bakan ortaçağ surları.
"""

SEHIRLER_TR = """Adana 37.0000 35.3213;Adıyaman 37.7648 38.2786;Afyonkarahisar 38.7638 30.5403;Ağrı 39.7191 43.0503;Aksaray 38.3687 34.0370;Amasya 40.6499 35.8353;Ankara 39.9334 32.8597;Antalya 36.8969 30.7133;Ardahan 41.1105 42.7022;Artvin 41.1828 41.8183;Aydın 37.8560 27.8416;Balıkesir 39.6484 27.8826;Bartın 41.6344 32.3375;Batman 37.8812 41.1351;Bayburt 40.2552 40.2249;Bilecik 40.1451 29.9799;Bingöl 38.8847 40.4983;Bitlis 38.4006 42.1095;Bolu 40.7392 31.6089;Burdur 37.7203 30.2908;Bursa 40.1885 29.0610;Çanakkale 40.1553 26.4142;Çankırı 40.6013 33.6134;Çorum 40.5506 34.9556;Denizli 37.7765 29.0864;Diyarbakır 37.9144 40.2306;Düzce 40.8438 31.1565;Edirne 41.6818 26.5623;Elazığ 38.6810 39.2264;Erzincan 39.7500 39.5000;Erzurum 39.9000 41.2700;Eskişehir 39.7767 30.5206;Gaziantep 37.0662 37.3833;Giresun 40.9128 38.3895;Gümüşhane 40.4386 39.5086;Hakkari 37.5833 43.7333;Hatay 36.2021 36.1600;Iğdır 39.9237 44.0450;Isparta 37.7648 30.5566;İstanbul 41.0082 28.9784;İzmir 38.4237 27.1428;Kahramanmaraş 37.5858 36.9371;Karabük 41.2061 32.6204;Karaman 37.1759 33.2287;Kars 40.6013 43.0975;Kastamonu 41.3887 33.7827;Kayseri 38.7312 35.4787;Kırıkkale 39.8468 33.5153;Kırklareli 41.7333 27.2167;Kırşehir 39.1425 34.1709;Kilis 36.7184 37.1212;Kocaeli 40.8533 29.8815;Konya 37.8746 32.4932;Kütahya 39.4167 29.9833;Malatya 38.3552 38.3095;Manisa 38.6191 27.4289;Mardin 37.3212 40.7245;Mersin 36.8000 34.6333;Muğla 37.2153 28.3636;Muş 38.7432 41.5065;Nevşehir 38.6939 34.6857;Niğde 37.9667 34.6833;Ordu 40.9839 37.8764;Osmaniye 37.0742 36.2478;Rize 41.0201 40.5234;Sakarya 40.7569 30.3783;Samsun 41.2928 36.3313;Siirt 37.9333 41.9500;Sinop 42.0231 35.1531;Sivas 39.7477 37.0179;Şanlıurfa 37.1591 38.7969;Şırnak 37.5164 42.4611;Tekirdağ 40.9833 27.5167;Tokat 40.3167 36.5500;Trabzon 41.0015 39.7178;Tunceli 39.1079 39.5401;Uşak 38.6823 29.4082;Van 38.4891 43.4089;Yalova 40.6500 29.2667;Yozgat 39.8181 34.8147;Zonguldak 41.4564 31.7987"""
ILCELER = """Selçuk|İzmir 37.9500 27.3700;Bodrum|Muğla 37.0344 27.4305;Fethiye|Muğla 36.6217 29.1164;Marmaris|Muğla 36.8550 28.2742;Datça|Muğla 36.7271 27.6871;Kaş|Antalya 36.2020 29.6377;Alanya|Antalya 36.5444 31.9954;Side|Antalya 36.7675 31.3889;Kemer|Antalya 36.5978 30.5597;Demre|Antalya 36.2453 29.9864;Göreme|Nevşehir 38.6431 34.8289;Ürgüp|Nevşehir 38.6319 34.9122;Avanos|Nevşehir 38.7150 34.8467;Uçhisar|Nevşehir 38.6297 34.8044;Pamukkale|Denizli 37.9137 29.1187;Kuşadası|Aydın 37.8579 27.2610;Çeşme|İzmir 38.3236 26.3027;Bergama|İzmir 39.1214 27.1799;Ayvalık|Balıkesir 39.3194 26.6939;Safranbolu|Karabük 41.2508 32.6939;Midyat|Mardin 37.4188 41.3699;Doğubayazıt|Ağrı 39.5469 44.0839;Divriği|Sivas 39.3714 38.1131;Gelibolu|Çanakkale 40.4106 26.6708;Antakya|Hatay 36.2025 36.1606;Tarsus|Mersin 36.9177 34.8925;Silifke|Mersin 36.3778 33.9344;Beyoğlu|İstanbul 41.0369 28.9775;Fatih|İstanbul 41.0186 28.9397;Üsküdar|İstanbul 41.0226 29.0156;Kadıköy|İstanbul 40.9909 29.0303;Beşiktaş|İstanbul 41.0430 29.0094"""
DUNYA = """Roma|İtalya 41.9028 12.4964;Napoli|İtalya 40.8518 14.2681;Venedik|İtalya 45.4408 12.3155;Floransa|İtalya 43.7696 11.2558;Milano|İtalya 45.4642 9.1900;Paris|Fransa 48.8566 2.3522;Londra|Birleşik Krallık 51.5072 -0.1276;Atina|Yunanistan 37.9838 23.7275;Selanik|Yunanistan 40.6401 22.9444;Kahire|Mısır 30.0444 31.2357;Luksor|Mısır 25.6872 32.6396;İskenderiye|Mısır 31.2001 29.9187;Berlin|Almanya 52.5200 13.4050;Münih|Almanya 48.1351 11.5820;Madrid|İspanya 40.4168 -3.7038;Barselona|İspanya 41.3874 2.1686;Granada|İspanya 37.1773 -3.5986;Sevilla|İspanya 37.3891 -5.9845;Lizbon|Portekiz 38.7223 -9.1393;Amsterdam|Hollanda 52.3676 4.9041;Viyana|Avusturya 48.2082 16.3738;Prag|Çekya 50.0755 14.4378;Budapeşte|Macaristan 47.4979 19.0402;Varşova|Polonya 52.2297 21.0122;Moskova|Rusya 55.7558 37.6173;St. Petersburg|Rusya 59.9311 30.3609;Saraybosna|Bosna-Hersek 43.8563 18.4131;Mostar|Bosna-Hersek 43.3438 17.8078;Üsküp|Kuzey Makedonya 41.9981 21.4254;Dubrovnik|Hırvatistan 42.6507 18.0944;Sofya|Bulgaristan 42.6977 23.3219;Bakü|Azerbaycan 40.4093 49.8671;Tiflis|Gürcistan 41.7151 44.8271;Kudüs|Filistin 31.7683 35.2137;Amman|Ürdün 31.9454 35.9284;Beyrut|Lübnan 33.8938 35.5018;Tahran|İran 35.6892 51.3890;İsfahan|İran 32.6546 51.6680;Semerkant|Özbekistan 39.6270 66.9750;Buhara|Özbekistan 39.7681 64.4556;Delhi|Hindistan 28.6139 77.2090;Agra|Hindistan 27.1767 78.0081;Pekin|Çin 39.9042 116.4074;Tokyo|Japonya 35.6762 139.6503;Kyoto|Japonya 35.0116 135.7681;New York|ABD 40.7128 -74.0060;Washington|ABD 38.9072 -77.0369;Meksiko|Meksika 19.4326 -99.1332;Cusco|Peru 13.5319 -71.9675;Rio de Janeiro|Brezilya -22.9068 -43.1729"""

def main():
    mekanlar = []
    for satir in MEKANLAR.strip().splitlines():
        ad, alt, il, ulke, kat, lat, lng, acik = [x.strip() for x in satir.split("|")]
        mekanlar.append({"ad": ad, "alt": [a.strip() for a in alt.split(",") if a.strip()], "il": il, "ulke": ulke,
                         "kategori": kat, "koordinat": [float(lat), float(lng)], "aciklama": acik})
    sehirler = []
    for s in SEHIRLER_TR.split(";"):
        p = s.rsplit(" ", 2); sehirler.append({"ad": p[0], "ust": "Türkiye", "koordinat": [float(p[1]), float(p[2])], "tur": "il"})
    for s in ILCELER.split(";"):
        a, rest = s.split("|"); p = rest.rsplit(" ", 2); sehirler.append({"ad": a, "ust": p[0] + ", Türkiye", "koordinat": [float(p[1]), float(p[2])], "tur": "ilce"})
    for s in DUNYA.split(";"):
        a, rest = s.split("|"); p = rest.rsplit(" ", 2)
        lat = float(p[1]); lat = -abs(lat) if a == "Cusco" else lat
        sehirler.append({"ad": a, "ust": p[0], "koordinat": [lat, float(p[2])], "tur": "sehir"})
    json.dump(mekanlar, open(os.path.join(KOK, "data/mekanlar.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(sehirler, open(os.path.join(KOK, "data/sehirler.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    il_say = sum(1 for s in sehirler if s["tur"] == "il")
    print(len(mekanlar), "mekân,", len(sehirler), "şehir (", il_say, "il )")
    assert il_say == 81, il_say

if __name__ == "__main__":
    main()

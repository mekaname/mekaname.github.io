#!/usr/bin/env python3
"""index.html'i, tüm veri, fotoğraf, video ve harita dosyaları içine gömülü
tek bir HTML dosyasına dönüştürür (çevrim dışı paylaşım / önizleme için).

Kullanım:  python3 tools/tek-dosya.py cikti.html
"""
import base64, io, json, os, sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIPLER = {".jpg": "image/jpeg", ".png": "image/png", ".mp4": "video/mp4"}


def veri_uri(yol):
    ext = os.path.splitext(yol)[1].lower()
    ham = open(os.path.join(KOK, yol), "rb").read()
    if yol == "assets/fiziki-harita.jpg":
        # Gömülü sürüm için haritayı küçült (3072 -> 2048 px).
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(ham)).resize((2048, 2048), Image.LANCZOS)
            tampon = io.BytesIO(); img.save(tampon, "JPEG", quality=74, optimize=True, progressive=True); ham = tampon.getvalue()
        except ImportError:
            pass
    return "data:%s;base64,%s" % (TIPLER[ext], base64.b64encode(ham).decode())


def main(cikti):
    gomulu = {}
    for ad in ("data/gonderiler.json", "data/kiyilar.json", "data/mekanlar.json", "data/sehirler.json"):
        gomulu[ad] = json.load(open(os.path.join(KOK, ad), encoding="utf-8"))
    gomulu["assets/fiziki-harita.jpg"] = veri_uri("assets/fiziki-harita.jpg")
    for klasor in ("assets/foto", "assets/video"):
        for ad in sorted(os.listdir(os.path.join(KOK, klasor))):
            if os.path.splitext(ad)[1].lower() in TIPLER:
                gomulu[klasor + "/" + ad] = veri_uri(klasor + "/" + ad)

    html = open(os.path.join(KOK, "index.html"), encoding="utf-8").read()
    isaret = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/'
    assert isaret in html, "Leaflet betik satırı bulunamadı"
    js = json.dumps(gomulu, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = html.replace(isaret, "<script>window.TG_GOMULU=" + js + ";</script>\n" + isaret, 1)
    open(cikti, "w", encoding="utf-8").write(html)
    print("%s yazıldı (%.1f MB)" % (cikti, os.path.getsize(cikti) / 1e6))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "mekaname-tek-dosya.html")

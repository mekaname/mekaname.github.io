#!/usr/bin/env python3
"""Haritada Bul oyunu için her mekâna Wikimedia Commons'tan bir fotoğraf indirir.
Çıktı: assets/oyun/<kod>.jpg ve data/oyun-foto.json (yazar/lisans bilgisiyle)."""
import json, re, time, sys, io, os, unicodedata, urllib.request, urllib.parse, html
from PIL import Image

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "KulturizOkulProjesi/1.0 (egitim amacli)"
CIKTI = os.path.join(KOK, "data", "oyun-foto.json")

def kod(ad):
    t = ad.replace("ı", "i").replace("İ", "I")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60]

def al(url, ikili=False):
    for d in range(8):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                b = r.read()
                return b if ikili else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503): time.sleep(5 * (d + 1)); continue
            raise
        except Exception:
            time.sleep(3 * (d + 1))
    raise RuntimeError("alınamadı: " + url)

def temiz(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h or ""))).strip()

def ara(sorgu):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": sorgu + " filetype:bitmap", "gsrlimit": 8, "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime",
        "iiurlwidth": 500, "iiextmetadatafilter": "Artist|LicenseShortName"})
    d = al("https://commons.wikimedia.org/w/api.php?" + q)
    sayfalar = sorted((d.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    for p in sayfalar:
        ii = (p.get("imageinfo") or [{}])[0]
        w, h = ii.get("width", 0), ii.get("height", 1)
        if ii.get("mime") not in ("image/jpeg", "image/png", "image/webp"): continue
        if w < 900 or not (0.65 <= w / h <= 2.1): continue
        if re.search(r"(map|plan|harita|logo|coat|flag|diagram|drawing|stamp|banknote|coin|\.png$)", p["title"], re.I): continue
        md = ii.get("extmetadata", {})
        return {"baslik": p["title"], "thumb": ii.get("thumburl"), "yazar": temiz(md.get("Artist", {}).get("value"))[:80],
                "lisans": temiz(md.get("LicenseShortName", {}).get("value"))}
    return None

def main():
    mek = json.load(open(os.path.join(KOK, "data", "mekanlar.json")))
    gon = json.load(open(os.path.join(KOK, "data", "gonderiler.json")))
    yerler = [(m["ad"], m.get("alt") or [], m.get("il") or "") for m in mek]
    for p in gon["gonderiler"]:
        for b in p.get("benzer", []): yerler.append((b["ad"], [], (b.get("bolge") or "").split(",")[0]))
    sonuc = json.load(open(CIKTI)) if os.path.exists(CIKTI) else {}
    atla = set(sys.argv[1:])
    for ad, alt, il in yerler:
        if ad in sonuc and ad not in atla: continue
        if atla and ad not in atla: continue
        ilq = kod(il).replace("-", " ") if il and kod(il) not in kod(ad) else ""
        en = [a for a in alt if re.match(r"^[A-Za-z0-9 '\-.,]+$", a)][:1]
        sorgular = [(q + " " + ilq).strip() for q in en + [ad]] + en + [ad]
        bulunan = None
        for s in sorgular:
            try: bulunan = ara(s)
            except Exception as e: print("HATA", ad, e); bulunan = None
            time.sleep(2.5)
            if bulunan: break
        if not bulunan: print("YOK", ad); continue
        try:
            b = al(bulunan["thumb"], ikili=True); time.sleep(2.5)
            im = Image.open(io.BytesIO(b)).convert("RGB"); im.thumbnail((480, 480))
            dosya = "assets/oyun/" + kod(ad) + ".jpg"
            im.save(os.path.join(KOK, dosya), "JPEG", quality=78, optimize=True, progressive=True)
        except Exception as e: print("İNDİRİLEMEDİ", ad, e); continue
        sonuc[ad] = {"foto": dosya, "kaynak": bulunan["baslik"], "yazar": bulunan["yazar"], "lisans": bulunan["lisans"]}
        json.dump(sonuc, open(CIKTI, "w"), ensure_ascii=False, indent=0)
        print("OK", ad, "<-", bulunan["baslik"], flush=True)

if __name__ == "__main__": main()

#!/usr/bin/env python3
"""data/gonderiler.json, data/mekanlar.json ve data/sehirler.json içeriğini
index.html'in içine gömer. Böylece sayfa tek başına açılsa bile (ör. iPhone'da
indirilen dosya) mekân araması ve örnek gönderiler çalışır.

Veri dosyalarından birini değiştirdikten sonra çalıştırın:  python3 tools/veri_gom.py
"""
import json, os, re

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSYALAR = ("data/gonderiler.json", "data/mekanlar.json", "data/sehirler.json")
BAS, SON = "<!-- GÖMÜLÜ VERİ BAŞLANGIÇ (tools/veri_gom.py üretir, elle düzenlemeyin) -->", "<!-- GÖMÜLÜ VERİ SON -->"


def main():
    veri = {ad: json.load(open(os.path.join(KOK, ad), encoding="utf-8")) for ad in DOSYALAR}
    js = json.dumps(veri, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    blok = BAS + '\n<script id="tg-veri" type="application/json">' + js + "</script>\n" + SON
    yol = os.path.join(KOK, "index.html")
    html = open(yol, encoding="utf-8").read()
    if BAS in html:
        html = re.sub(re.escape(BAS) + ".*?" + re.escape(SON), lambda m: blok, html, flags=re.S)
    else:
        isaret = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/'
        html = html.replace(isaret, blok + "\n" + isaret, 1)
    open(yol, "w", encoding="utf-8").write(html)
    print("Gömüldü: %d KB" % (len(js) // 1024))


if __name__ == "__main__":
    main()

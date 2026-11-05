"""Gece çekimi — GitHub Actions her gece UTC 23:31 / 23:41 / 23:51'de çalıştırır.

MGM'de yagis00Now UTC 00:00'da (TR 03:00) sıfırlanır. Sıfırlanmadan hemen önceki değer
o günün toplam yağışıdır. Bu script MGM'den veriyi çeker ve istasyonların veri zamanı
UTC 23:30-23:59 penceresindeyse gece/YYYY-MM-DD.json olarak kaydeder.
Üç denemeden pencerede en çok istasyonu yakalayan (eşitse en geç olan) kalır.
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

BASE_URL = "https://servis.mgm.gov.tr/web"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
    "Origin": "https://www.mgm.gov.tr",
    "Referer": "https://www.mgm.gov.tr/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}
KLASOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gece")
TR = timezone(timedelta(hours=3))


def getir(yol):
    hata = None
    for i in range(3):
        try:
            r = requests.get(f"{BASE_URL}/{yol}", headers=HEADERS, timeout=30)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            hata = e
            time.sleep(15)
    raise RuntimeError(f"{yol}: {hata}")


def pencerede(veri_zamani):
    try:
        d = datetime.strptime(veri_zamani[:19], "%Y-%m-%dT%H:%M:%S")
    except (TypeError, ValueError):
        return None
    return d.strftime("%Y-%m-%d") if d.hour == 23 and d.minute >= 30 else None


def main():
    istasyonlar = {i["istNo"]: i for i in getir("istasyonlar/il?plaka=35")}
    sondurum = getir("sondurumlar/ilTumSondurum?ilPlaka=35")
    cekme = datetime.now(TR).strftime("%Y-%m-%d %H:%M:%S")

    kayitlar = []
    for item in sondurum:
        ist = istasyonlar.get(item.get("istNo", ""), {})
        kayitlar.append({
            "istasyonAdi":  ist.get("istAd", f"Bilinmeyen ({item.get('istNo', '')})"),
            "enlem":        ist.get("enlem", ""),
            "boylam":       ist.get("boylam", ""),
            "yukseklik":    ist.get("yukseklik", ""),
            "ilce":         ist.get("ilce", ""),
            "aktuelBasinc": item.get("aktuelBasinc", ""),
            "yagis00Now":   item.get("yagis00Now", ""),
            "yagis10Dk":    item.get("yagis10Dk", ""),
            "yagis1Saat":   item.get("yagis1Saat", ""),
            "yagis6Saat":   item.get("yagis6Saat", ""),
            "yagis12Saat":  item.get("yagis12Saat", ""),
            "yagis24Saat":  item.get("yagis24Saat", ""),
            "ruzgarHiz":    item.get("ruzgarHiz", ""),
            "ruzgarYon":    item.get("ruzgarYon", ""),
            "sicaklik":     item.get("sicaklik", ""),
            "nem":          item.get("nem", ""),
            "veriZamani":   item.get("veriZamani", ""),
            "cekmeZamani":  cekme,
        })

    gunler = [pencerede(k["veriZamani"]) for k in kayitlar]
    gunler = [g for g in gunler if g]
    print(f"{len(kayitlar)} istasyon geldi, {len(gunler)} tanesi UTC 23:30-23:59 penceresinde")
    if not gunler:
        print("Pencere dışında, kaydedilmedi.")
        return

    tarih = max(set(gunler), key=gunler.count)
    adet = gunler.count(tarih)
    yol = os.path.join(KLASOR, f"{tarih}.json")
    if os.path.exists(yol):
        with open(yol, encoding="utf-8") as f:
            eski = json.load(f)
        if eski.get("pencereAdet", 0) > adet:
            print(f"Önceki deneme daha iyi ({eski['pencereAdet']} istasyon), korunuyor.")
            return

    os.makedirs(KLASOR, exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump({"cekmeZamani": cekme, "pencereAdet": adet, "veri": kayitlar},
                  f, ensure_ascii=False, separators=(",", ":"))
    print(f"Kaydedildi: gece/{tarih}.json")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"HATA: {e}")
        sys.exit(1)

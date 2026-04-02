import requests
import json
import webbrowser
import os
import sys
import os
os.environ["TZ"] = "Europe/Istanbul"
try:
    import time
    time.tzset()
except AttributeError:
    pass
from datetime import datetime

# MGM API ayarları
BASE_URL = "https://servis.mgm.gov.tr/web"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,tr-TR;q=0.8,tr;q=0.7",
    "Origin": "https://www.mgm.gov.tr",
    "Referer": "https://www.mgm.gov.tr/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
ARSIV_DOSYASI = os.path.join(SCRIPT_DIR, "index.js")
LOG_DOSYASI   = os.path.join(SCRIPT_DIR, "mgm-log.txt")

# --sessiz: Görev Zamanlayıcı tarafından çağrılınca tarayıcı açılmaz
SESSIZ = "--sessiz" in sys.argv


def log(mesaj):
    """Hem terminale hem log dosyasına yazar."""
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    satir = f"[{zaman}] {mesaj}"
    print(satir)
    try:
        with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
            f.write(satir + "\n")
    except Exception:
        pass


def arsivi_oku():
    if not os.path.exists(ARSIV_DOSYASI):
        return {}
    try:
        with open(ARSIV_DOSYASI, "r", encoding="utf-8") as f:
            icerik = f.read().strip()
        prefix = "const CEKIM_ARSIVI = "
        if icerik.startswith(prefix) and icerik.endswith(";"):
            return json.loads(icerik[len(prefix):-1])
    except Exception as e:
        log(f"Arşiv okunamadı, sıfırdan başlanıyor: {e}")
    return {}


def arsivi_yaz(arsiv):
    with open(ARSIV_DOSYASI, "w", encoding="utf-8") as f:
        f.write("const CEKIM_ARSIVI = ")
        json.dump(arsiv, f, ensure_ascii=False, indent=2)
        f.write(";")


def main():
    mod = "OTOMATİK (sessiz)" if SESSIZ else "MANUEL"
    log(f"─── Çekim başladı [{mod}] ───")

    try:
        # 1. İstasyon bilgilerini çek (koordinatlar dahil)
        log("İstasyon bilgileri çekiliyor...")
        ist_r = requests.get(f"{BASE_URL}/istasyonlar/il?plaka=35", headers=HEADERS, timeout=30)
        ist_r.raise_for_status()
        ist_bilgi = {i["istNo"]: i for i in ist_r.json()}
        ist_adi = {k: v["istAd"] for k, v in ist_bilgi.items()}
        log(f"{len(ist_adi)} istasyon bilgisi alındı")

        # 2. Hava durumu verilerini çek
        log("Hava durumu verileri çekiliyor...")
        r = requests.get(f"{BASE_URL}/sondurumlar/ilTumSondurum?ilPlaka=35", headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        log(f"{len(data)} istasyon verisi geldi")

        # 3. Veriyi hazırla
        cekme_zamani = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        json_data = []
        for item in data:
            ist_no = item.get("istNo", "")
            ist = ist_bilgi.get(ist_no, {})
            json_data.append({
                "istasyonAdi":  ist_adi.get(ist_no, f"Bilinmeyen ({ist_no})"),
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
                "cekmeZamani":  cekme_zamani,
            })

        # 4. Arşive ekle
        arsiv = arsivi_oku()
        arsiv[cekme_zamani] = json_data
        arsivi_yaz(arsiv)
        log(f"index.js güncellendi — toplam {len(arsiv)} çekim arşivde")

        # 5. Tarayıcıyı sadece manuel çalıştırmada aç
        if not SESSIZ:
            html_path = os.path.join(SCRIPT_DIR, "index.html")
            webbrowser.open(f"file:///{html_path}")
            log("index.html açılıyor...")

        log("─── Çekim tamamlandı ───")

    except requests.exceptions.ConnectionError:
        log("HATA: İnternet bağlantısı kurulamadı")
        sys.exit(1)
    except requests.exceptions.Timeout:
        log("HATA: Sunucu yanıt vermedi (timeout)")
        sys.exit(1)
    except Exception as e:
        log(f"HATA: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

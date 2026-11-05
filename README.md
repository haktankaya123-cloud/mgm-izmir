# mgm-izmir

MGM'nin İzmir istasyonlarından yağış, sıcaklık, nem, rüzgar ve basınç verisini çeker; tablo, harita ve yağış istatistiği olarak gösterir.

## Nasıl çalışır

- **Gündüz — elle:** `MGM-Cek.bat`'a çift tıkla. Veriyi çeker, `index.js` arşivine ekler, sayfayı açar.
- **Gece — otomatik:** GitHub Actions her gece UTC 23:31 / 23:41 / 23:51'de (TR 02:31–02:51) MGM'den çeker ve `gece/` klasörüne kaydeder. `MGM-Cek.bat` bir sonraki çalışmada bu gece dosyalarını indirip arşive ekler.

Gece çekiminin nedeni: MGM'de `yagis00Now` her gün UTC 00:00'da (TR 03:00) sıfırlanır. Sıfırlanmadan hemen önceki değer o günün toplam yağışıdır; istatistik sayfası günlük toplamı bu değerden alır.

## Dosyalar

| Dosya | Görevi |
|---|---|
| `MGM-Cek.bat` | Çift tıkla çekim (Python ve `requests` yoksa uyarır/kurar) |
| `mgm-veri.py` | MGM'den çeker, gece dosyalarını birleştirir, `index.js`'e yazar |
| `index.js` | Tüm çekimlerin arşivi |
| `index.html` · `harita.html` · `istatistik.html` | Sayfalar (çift tıkla açılır) |
| `gece-cekim.py` · `.github/workflows/gece-cekim.yml` | Gece çekimi (GitHub'da çalışır) |
| `gece/` | Gece çekimleri, her gün bir dosya |

## Notlar

- Repo **public** kalmalı; `mgm-veri.py` gece dosyalarını şifresiz indiriyor.
- Gece çekimini elle denemek için: **Actions → MGM gece cekimi → Run workflow** (pencere dışındaysa kaydetmez, sadece MGM'ye erişimi gösterir).
- Bilgisayarda Python yoksa: python.org → kurarken **Add to PATH** işaretli olsun.

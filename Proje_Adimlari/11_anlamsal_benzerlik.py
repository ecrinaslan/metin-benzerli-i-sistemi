"""Seviye 3: Anlamsal benzerliği sözcüksel yöntemlerle karşılaştırır.

01_orijinal.txt dosyası diğer test ödevleriyle dört yöntemle karşılaştırılır ve
sonuçlar sonuclar/anlamsal_sonuclar.csv dosyasına kaydedilir.

Gerekli paket: pip install sentence-transformers
(İlk çalıştırmada çok dilli model internetten bir kez indirilir.)
"""
import sys
from pathlib import Path

import pandas as pd

#Proje kök dizinini ekliyoruz ki benzerlik.py modülünü içe aktarabilelim.
KOK_DIZIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK_DIZIN))

from benzerlik import (  # noqa: E402
    ANLAMSAL_KULLANILABILIR,
    anlamsal_benzerlik,
    dosyadan_metin_oku,
    jaccard_benzerligi,
    metin_on_isle,
    ngram_benzerligi,
    tfidf_benzerligi,
)

if not ANLAMSAL_KULLANILABILIR:
    sys.exit("sentence-transformers yüklü değil. Kurmak için: pip install sentence-transformers")

ODEVLER = KOK_DIZIN / "Odevler"
SONUC_DOSYASI = KOK_DIZIN / "sonuclar" / "anlamsal_sonuclar.csv"

SENARYOLAR = {
    "02_birebir_kopya.txt": "Birebir kopya",
    "03_kismi_kopya.txt": "Kısmi kopya",
    "04_esanlamli_degisiklik.txt": "Eş anlamlı değişiklik",
    "05_cumle_sirasi_degisik.txt": "Cümle sırası değişik",
    "06_farkli_konu.txt": "Farklı konu",
    "07_ayni_konu_ozgun.txt": "Aynı konu, özgün",
    "08_buyuk_harf_turkce.txt": "Türkçe büyük harf",
}

orijinal = metin_on_isle(dosyadan_metin_oku(ODEVLER / "01_orijinal.txt"))

satirlar = []
for dosya_adi, senaryo in SENARYOLAR.items():
    diger = metin_on_isle(dosyadan_metin_oku(ODEVLER / dosya_adi))
    satirlar.append({
        "Dosya": dosya_adi,
        "Senaryo": senaryo,
        "Jaccard": jaccard_benzerligi(orijinal, diger),
        "TF-IDF": tfidf_benzerligi(orijinal, diger),
        "Bigram": ngram_benzerligi(orijinal, diger, n=2),
        "Anlamsal": anlamsal_benzerlik(orijinal, diger),
    })

sonuclar = pd.DataFrame(satirlar).round(2)
SONUC_DOSYASI.parent.mkdir(exist_ok=True)
sonuclar.to_csv(SONUC_DOSYASI, index=False, encoding="utf-8-sig")

pd.set_option("display.width", 200)
print("=== 01_orijinal.txt ile karşılaştırma sonuçları (%) ===")
print(sonuclar.to_string(index=False))
print(f"\nSonuçlar kaydedildi: {SONUC_DOSYASI.relative_to(KOK_DIZIN)}")

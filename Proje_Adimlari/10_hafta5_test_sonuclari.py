import string
import sys
from pathlib import Path

import pandas as pd

#Proje kök dizinini ekliyoruz ki benzerlik.py modülünü içe aktarabilelim.
KOK_DIZIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK_DIZIN))

from benzerlik import (  # noqa: E402
    dosyadan_metin_oku,
    jaccard_benzerligi,
    metin_on_isle,
    metin_temizle,
    ngram_benzerligi,
    tfidf_benzerligi,
)

ODEVLER = KOK_DIZIN / "Odevler"
SONUC_DOSYASI = KOK_DIZIN / "sonuclar" / "hafta5_sonuclar.csv"

#Karşılaştırılacak üç ön işleme ayarı
AYARLAR = {
    "a) Temizleme": {},
    "b) Temizleme + Dolgu": {"dolgu_cikar": True},
    "c) Temizleme + Dolgu + Kök": {"dolgu_cikar": True, "kok_bul": True},
}


def eski_metin_temizle(metin):
    #1. adımdaki düzeltmeden önceki hâli: sadece lower() ve string.punctuation.
    metin = metin.lower()
    for isaret in string.punctuation:
        metin = metin.replace(isaret, "")
    return metin


#1_Orijinali diğer tüm dosyalarla karşılaştırma
orijinal_ham = dosyadan_metin_oku(ODEVLER / "01_orijinal.txt")
diger_dosyalar = sorted(yol for yol in ODEVLER.glob("0*.*") if yol.name != "01_orijinal.txt")

satirlar = []
for ayar_adi, ayar in AYARLAR.items():
    orijinal = metin_on_isle(orijinal_ham, **ayar)
    for yol in diger_dosyalar:
        diger = metin_on_isle(dosyadan_metin_oku(yol), **ayar)
        satirlar.append({
            "Ön işleme": ayar_adi,
            "Dosya": yol.name,
            "Jaccard": jaccard_benzerligi(orijinal, diger),
            "TF-IDF": tfidf_benzerligi(orijinal, diger),
            "Unigram": ngram_benzerligi(orijinal, diger, n=1),
            "Bigram": ngram_benzerligi(orijinal, diger, n=2),
            "Trigram": ngram_benzerligi(orijinal, diger, n=3),
        })

sonuclar = pd.DataFrame(satirlar).round(2)
SONUC_DOSYASI.parent.mkdir(exist_ok=True)
sonuclar.to_csv(SONUC_DOSYASI, index=False, encoding="utf-8-sig")

pd.set_option("display.width", 200)
print("=== 01_orijinal.txt ile karşılaştırma sonuçları (%) ===")
for ayar_adi, grup in sonuclar.groupby("Ön işleme", sort=False):
    print(f"\n--- {ayar_adi} ---")
    print(grup.drop(columns="Ön işleme").to_string(index=False))

#2_Türkçe büyük harf düzeltmesinin etkisi (08 dosyası)
buyuk_harfli_ham = dosyadan_metin_oku(ODEVLER / "08_buyuk_harf_turkce.txt")
duzeltme_tablosu = pd.DataFrame([
    {"Küçük harf yöntemi": "Önce: metin.lower()",
     "Jaccard (01 ↔ 08)": jaccard_benzerligi(eski_metin_temizle(orijinal_ham), eski_metin_temizle(buyuk_harfli_ham))},
    {"Küçük harf yöntemi": "Sonra: turkce_kucuk_harf()",
     "Jaccard (01 ↔ 08)": jaccard_benzerligi(metin_temizle(orijinal_ham), metin_temizle(buyuk_harfli_ham))},
]).round(2)

print("\n=== Türkçe büyük/küçük harf düzeltmesi (08_buyuk_harf_turkce.txt) ===")
print(duzeltme_tablosu.to_string(index=False))
print(f"\nSonuçlar kaydedildi: {SONUC_DOSYASI.relative_to(KOK_DIZIN)}")

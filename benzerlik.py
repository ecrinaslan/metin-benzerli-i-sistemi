"""İntihal tespiti için hesaplama fonksiyonları.

Bu modül Streamlit'ten bağımsızdır; app.py, testler ve Proje_Adimlari betikleri buradan içe aktarır.
"""
import io
import string
import unicodedata
import warnings
from functools import lru_cache
from pathlib import Path

import pandas as pd
from docx import Document
from pypdf import PdfReader
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


#1_Veri_Alma(Dosya okuma)
def metin_cikar(dosya_adi, icerik):
    #Dosyanın uzantısına göre içindeki (bayt olarak verilen) metni çıkarıyoruz.
    dosya_adi = dosya_adi.lower()

    if dosya_adi.endswith(".txt"):
        return icerik.decode("utf-8-sig", errors="ignore")
    if dosya_adi.endswith(".pdf"):
        okuyucu = PdfReader(io.BytesIO(icerik))
        return "\n".join(sayfa.extract_text() or "" for sayfa in okuyucu.pages)
    if dosya_adi.endswith(".docx"):
        belge = Document(io.BytesIO(icerik))
        return "\n".join(paragraf.text for paragraf in belge.paragraphs)
    return ""


def dosyadan_metin_oku(dosya_yolu):
    #Diskteki bir dosyayı okuyup metnini döndürüyoruz (testler ve betikler için).
    dosya_yolu = Path(dosya_yolu)
    return metin_cikar(dosya_yolu.name, dosya_yolu.read_bytes())


#2_Metin Ön İşleme
#Kesme işaretleri silinir ("Türkiye'nin" -> "türkiyenin"), diğer işaretler ve sayılar boşluğa çevrilir.
KESME_ISARETLERI = "'’‘"
NOKTALAMA_ISARETLERI = string.punctuation.replace("'", "") + "“”«»…–—" + string.digits
TEMIZLEME_TABLOSU = str.maketrans(
    {**{isaret: "" for isaret in KESME_ISARETLERI}, **{isaret: " " for isaret in NOKTALAMA_ISARETLERI}}
)
SAPKA_TABLOSU = str.maketrans("âîû", "aiu")


def turkce_kucuk_harf(metin):
    #Python'un lower() fonksiyonu "İ" harfini "i̇" (i + nokta), "I" harfini "i" yapar.
    #Bu yüzden önce Türkçeye özgü harfleri elle çeviriyoruz.
    return metin.replace("I", "ı").replace("İ", "i").lower()


def metin_temizle(metin):
    metin = unicodedata.normalize("NFC", metin) #PDF'ten gelen ayrık harfleri (I + ̇) birleştiriyoruz.
    metin = turkce_kucuk_harf(metin) #Tüm harfleri Türkçe kurallarına göre küçük harfe çeviriyoruz.
    metin = metin.translate(SAPKA_TABLOSU) #"zekâ" ile "zeka" aynı kelime sayılsın diye şapkaları kaldırıyoruz.
    metin = metin.translate(TEMIZLEME_TABLOSU) #Noktalama işaretlerini ve sayıları temizliyoruz.
    return " ".join(metin.split()) #Fazla boşlukları siliyoruz.


#2b_Türkçe Ön İşleme: dolgu kelimeleri ve kök bulma
DOLGU_KELIMELERI_DOSYASI = Path(__file__).with_name("turkce_dolgu_kelimeleri.txt")


def dolgu_kelimelerini_yukle(dosya_yolu=DOLGU_KELIMELERI_DOSYASI):
    #Boş satırları ve "#" ile başlayan açıklama satırlarını atlayarak kelimeleri okuyoruz.
    satirlar = Path(dosya_yolu).read_text(encoding="utf-8").splitlines()
    return {metin_temizle(satir) for satir in satirlar if satir.strip() and not satir.startswith("#")}


DOLGU_KELIMELERI = dolgu_kelimelerini_yukle()

#snowballstemmer yüklü değilse uygulama çökmesin; kök bulma atlanır ve uyarı verilir.
try:
    import snowballstemmer
    KOK_BULUCU = snowballstemmer.stemmer("turkish")
except ImportError:
    KOK_BULUCU = None
KOK_BULMA_KULLANILABILIR = KOK_BULUCU is not None


def dolgu_kelimelerini_cikar(metin):
    return " ".join(kelime for kelime in metin.split() if kelime not in DOLGU_KELIMELERI)


@lru_cache(maxsize=50000)
def kelime_koku(kelime):
    return KOK_BULUCU.stemWord(kelime)


def kokleri_bul(metin):
    if not KOK_BULMA_KULLANILABILIR:
        warnings.warn("snowballstemmer paketi yüklü değil; kök bulma adımı atlandı.")
        return metin
    return " ".join(kelime_koku(kelime) for kelime in metin.split())


def metin_on_isle(metin, dolgu_cikar=False, kok_bul=False):
    #Temizleme her zaman yapılır; dolgu çıkarma ve kök bulma isteğe bağlıdır.
    metin = metin_temizle(metin)
    if dolgu_cikar:
        metin = dolgu_kelimelerini_cikar(metin)
    if kok_bul:
        metin = kokleri_bul(metin)
    return metin


#3_Algoritma_Benzerlik_Hesaplama
def jaccard_benzerligi(metin1, metin2):
    kume1 = set(metin1.split())
    kume2 = set(metin2.split())
    toplam_kelimeler = kume1.union(kume2)
    if not toplam_kelimeler:
        return 0.0
    #Formül= (Ortak kelime sayısı)/(Toplam benzersiz kelime sayısı)*100
    return len(kume1.intersection(kume2)) / len(toplam_kelimeler) * 100


def tfidf_benzerligi(metin1, metin2):
    #Metinleri TF-IDF vektörlerine çevirip aralarındaki kosinüs benzerliğini buluyoruz.
    #Metin zaten temizlendiği için lowercase=False (yoksa İ/I yeniden yanlış küçültülür).
    try:
        vektorler = TfidfVectorizer(lowercase=False).fit_transform([metin1, metin2])
    except ValueError: #Metinlerde hiç kelime yoksa
        return 0.0
    return float(cosine_similarity(vektorler[0], vektorler[1])[0][0]) * 100


def ngram_benzerligi(metin1, metin2, n=2):
    #Ardışık n kelimelik grupları (n-gram) sayıp kosinüs benzerliğini buluyoruz.
    try:
        vektorler = CountVectorizer(ngram_range=(n, n), lowercase=False).fit_transform([metin1, metin2])
    except ValueError: #Metin n kelimeden kısaysa
        return 0.0
    return float(cosine_similarity(vektorler[0], vektorler[1])[0][0]) * 100


def ortak_kelimeler(metin1, metin2):
    return sorted(set(metin1.split()).intersection(metin2.split()))


def ngramlari_bul(metin, n=2):
    kelimeler = metin.split()
    return {" ".join(kelimeler[i:i + n]) for i in range(len(kelimeler) - n + 1)}


def ortak_ngramlar(metin1, metin2, n=2):
    return sorted(ngramlari_bul(metin1, n).intersection(ngramlari_bul(metin2, n)))


#4_Çoklu Karşılaştırma (karşılaştırma havuzu)
YONTEMLER = {
    "Jaccard": jaccard_benzerligi,
    "TF-IDF + Kosinüs": tfidf_benzerligi,
    "Bigram + Kosinüs": lambda metin1, metin2: ngram_benzerligi(metin1, metin2, n=2),
}


def benzerlik_matrisi(metinler, yontem="TF-IDF + Kosinüs"):
    #metinler: {dosya_adi: on_islenmis_metin}. Tüm dosya çiftleri için benzerlik tablosu döndürür.
    hesapla = YONTEMLER[yontem]
    adlar = list(metinler)
    matris = pd.DataFrame(100.0, index=adlar, columns=adlar)
    for i, ad1 in enumerate(adlar):
        for ad2 in adlar[i + 1:]:
            matris.loc[ad1, ad2] = matris.loc[ad2, ad1] = hesapla(metinler[ad1], metinler[ad2])
    return matris


def supheli_eslesmeler(matris, esik=50):
    #Eşiği aşan dosya çiftlerini (her çift bir kez) en yüksekten düşüğe sıralar.
    adlar = list(matris.index)
    satirlar = [
        {"1. Dosya": ad1, "2. Dosya": ad2, "Benzerlik (%)": round(float(matris.loc[ad1, ad2]), 2)}
        for i, ad1 in enumerate(adlar) for ad2 in adlar[i + 1:]
        if matris.loc[ad1, ad2] >= esik
    ]
    tablo = pd.DataFrame(satirlar, columns=["1. Dosya", "2. Dosya", "Benzerlik (%)"])
    return tablo.sort_values("Benzerlik (%)", ascending=False, ignore_index=True)

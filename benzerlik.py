
"""İntihal tespiti için hesaplama fonksiyonları.

Bu modül Streamlit'ten bağımsızdır; app.py, testler ve
Proje_Adimlari betikleri buradan içe aktarır.
"""

import io
import re
import string
import unicodedata
import warnings

from functools import lru_cache
from pathlib import Path

import pandas as pd

from docx import Document
from pypdf import PdfReader

from sklearn.feature_extraction.text import (
    CountVectorizer,
    TfidfVectorizer
)

from sklearn.metrics.pairwise import cosine_similarity


# ==================================================
# 1. VERİ ALMA - DOSYA OKUMA
# ==================================================

def metin_cikar(dosya_adi, icerik):
    """Dosyanın uzantısına göre metin çıkarır."""

    dosya_adi = dosya_adi.lower()

    if dosya_adi.endswith(".txt"):

        return icerik.decode(
            "utf-8-sig",
            errors="ignore"
        )

    if dosya_adi.endswith(".pdf"):

        okuyucu = PdfReader(io.BytesIO(icerik))

        return "\n".join(
            sayfa.extract_text() or ""
            for sayfa in okuyucu.pages
        )

    if dosya_adi.endswith(".docx"):

        belge = Document(io.BytesIO(icerik))

        return "\n".join(
            paragraf.text
            for paragraf in belge.paragraphs
        )

    return ""


def dosyadan_metin_oku(dosya_yolu):
    """Diskteki bir dosyayı okuyup metnini döndürür."""

    dosya_yolu = Path(dosya_yolu)

    return metin_cikar(
        dosya_yolu.name,
        dosya_yolu.read_bytes()
    )


# ==================================================
# 2. METİN ÖN İŞLEME
# ==================================================

KESME_ISARETLERI = "'’‘"

NOKTALAMA_ISARETLERI = (
    string.punctuation.replace("'", "")
    + "“”«»…–—"
    + string.digits
)

TEMIZLEME_TABLOSU = str.maketrans(
    {
        **{
            isaret: ""
            for isaret in KESME_ISARETLERI
        },
        **{
            isaret: " "
            for isaret in NOKTALAMA_ISARETLERI
        }
    }
)

SAPKA_TABLOSU = str.maketrans(
    "âîû",
    "aiu"
)


def turkce_kucuk_harf(metin):
    """Türkçe karakterlere uygun küçük harf dönüşümü."""

    return (
        metin.replace("I", "ı")
        .replace("İ", "i")
        .lower()
    )


def metin_temizle(metin):

    metin = unicodedata.normalize(
        "NFC",
        metin
    )

    metin = turkce_kucuk_harf(metin)

    metin = metin.translate(
        SAPKA_TABLOSU
    )

    metin = metin.translate(
        TEMIZLEME_TABLOSU
    )

    return " ".join(metin.split())


# ==================================================
# 2B. TÜRKÇE ÖN İŞLEME
# ==================================================

DOLGU_KELIMELERI_DOSYASI = (
    Path(__file__).with_name(
        "turkce_dolgu_kelimeleri.txt"
    )
)


def dolgu_kelimelerini_yukle(
    dosya_yolu=DOLGU_KELIMELERI_DOSYASI
):

    satirlar = Path(dosya_yolu).read_text(
        encoding="utf-8"
    ).splitlines()

    return {
        metin_temizle(satir)
        for satir in satirlar
        if satir.strip()
        and not satir.startswith("#")
    }


DOLGU_KELIMELERI = dolgu_kelimelerini_yukle()


try:

    import snowballstemmer

    KOK_BULUCU = snowballstemmer.stemmer(
        "turkish"
    )

except ImportError:

    KOK_BULUCU = None


KOK_BULMA_KULLANILABILIR = (
    KOK_BULUCU is not None
)


def dolgu_kelimelerini_cikar(metin):

    return " ".join(
        kelime
        for kelime in metin.split()
        if kelime not in DOLGU_KELIMELERI
    )


@lru_cache(maxsize=50000)
def kelime_koku(kelime):

    return KOK_BULUCU.stemWord(kelime)


def kokleri_bul(metin):

    if not KOK_BULMA_KULLANILABILIR:

        warnings.warn(
            "snowballstemmer paketi yüklü değil; "
            "kök bulma adımı atlandı."
        )

        return metin

    return " ".join(
        kelime_koku(kelime)
        for kelime in metin.split()
    )


def metin_on_isle(
    metin,
    dolgu_cikar=False,
    kok_bul=False
):

    metin = metin_temizle(metin)

    if dolgu_cikar:

        metin = dolgu_kelimelerini_cikar(
            metin
        )

    if kok_bul:

        metin = kokleri_bul(
            metin
        )

    return metin


# ==================================================
# 2C. BÖLÜM BAZLI ANALİZ
# ==================================================

def bolum_basligini_normalize_et(baslik):
    """
    Başlık numarasını kaldırır ve başlığı
    karşılaştırmaya uygun hâle getirir.

    Örnek:
    1. GİRİŞ -> giriş
    2. Giriş -> giriş
    """

    baslik = re.sub(
        r"^\s*\d+(?:\.\d+)*\.?\s*",
        "",
        baslik
    )

    return metin_temizle(baslik)


def bolumlere_ayir(metin):
    """
    Numaralı başlıkları algılayarak metni bölümlere ayırır.

    Örnek:
    1. GİRİŞ
    1.1 Amaç
    2. YÖNTEM
    3. SONUÇ

    Aynı isimli başlıklar tek bölüm altında birleştirilir.
    Başlık bulunamazsa belge tek bölüm kabul edilir.
    """

    bolumler = {}

    aktif_baslik = None

    aktif_metin = []

    def bolumu_kaydet():

        if aktif_baslik is not None:

            icerik = "\n".join(
                aktif_metin
            ).strip()

            if icerik:

                anahtar = bolum_basligini_normalize_et(
                    aktif_baslik
                )

                if anahtar in bolumler:

                    bolumler[anahtar]["metin"] += (
                        "\n" + icerik
                    )

                else:

                    bolumler[anahtar] = {
                        "baslik": aktif_baslik,
                        "metin": icerik
                    }

    for satir in metin.splitlines():

        satir = satir.strip()

        # Numaralı başlıkları algıla.
        eslesme = re.match(
            r"^\s*(\d+(?:\.\d+)*\.?)\s+(.{2,100})$",
            satir
        )

        if (
            eslesme
            and not satir.endswith((".", ",", ";"))
        ):

            bolumu_kaydet()

            aktif_baslik = eslesme.group(2).strip()

            aktif_metin = []

        elif aktif_baslik is not None:

            aktif_metin.append(satir)

    bolumu_kaydet()

    # Başlık bulunamadıysa bütün metni tek bölüm yap.
    if not bolumler:

        return {
            "belgenin tamamı": {
                "baslik": "Belgenin Tamamı",
                "metin": metin
            }
        }

    return bolumler


# ==================================================
# 3. ALGORİTMA BENZERLİK HESAPLAMA
# ==================================================

def jaccard_benzerligi(metin1, metin2):

    kume1 = set(metin1.split())

    kume2 = set(metin2.split())

    toplam_kelimeler = kume1.union(
        kume2
    )

    if not toplam_kelimeler:

        return 0.0

    return (
        len(kume1.intersection(kume2))
        / len(toplam_kelimeler)
        * 100
    )


def tfidf_benzerligi(metin1, metin2):

    try:

        vektorler = TfidfVectorizer(
            lowercase=False
        ).fit_transform(
            [metin1, metin2]
        )

    except ValueError:

        return 0.0

    return float(
        cosine_similarity(
            vektorler[0],
            vektorler[1]
        )[0][0]
    ) * 100


def ngram_benzerligi(
    metin1,
    metin2,
    n=2
):

    try:

        vektorler = CountVectorizer(
            ngram_range=(n, n),
            lowercase=False
        ).fit_transform(
            [metin1, metin2]
        )

    except ValueError:

        return 0.0

    return float(
        cosine_similarity(
            vektorler[0],
            vektorler[1]
        )[0][0]
    ) * 100


def ortak_kelimeler(metin1, metin2):

    return sorted(
        set(metin1.split()).intersection(
            metin2.split()
        )
    )


def ngramlari_bul(metin, n=2):

    kelimeler = metin.split()

    return {
        " ".join(
            kelimeler[i:i + n]
        )
        for i in range(
            len(kelimeler) - n + 1
        )
    }


def ortak_ngramlar(
    metin1,
    metin2,
    n=2
):

    return sorted(
        ngramlari_bul(metin1, n).intersection(
            ngramlari_bul(metin2, n)
        )
    )


# ==================================================
# 4. ÇOKLU KARŞILAŞTIRMA
# ==================================================

YONTEMLER = {

    "Jaccard": jaccard_benzerligi,

    "TF-IDF + Kosinüs": tfidf_benzerligi,

    "Bigram + Kosinüs": (
        lambda metin1, metin2:
        ngram_benzerligi(
            metin1,
            metin2,
            n=2
        )
    ),

}


def benzerlik_matrisi(
    metinler,
    yontem="TF-IDF + Kosinüs"
):

    hesapla = YONTEMLER[yontem]

    adlar = list(metinler)

    matris = pd.DataFrame(
        100.0,
        index=adlar,
        columns=adlar
    )

    for i, ad1 in enumerate(adlar):

        for ad2 in adlar[i + 1:]:

            matris.loc[ad1, ad2] = (
                matris.loc[ad2, ad1]
                = hesapla(
                    metinler[ad1],
                    metinler[ad2]
                )
            )

    return matris


def supheli_eslesmeler(
    matris,
    esik=50
):

    adlar = list(matris.index)

    satirlar = [

        {
            "1. Dosya": ad1,
            "2. Dosya": ad2,
            "Benzerlik (%)": round(
                float(matris.loc[ad1, ad2]),
                2
            )
        }

        for i, ad1 in enumerate(adlar)

        for ad2 in adlar[i + 1:]

        if matris.loc[ad1, ad2] >= esik

    ]

    tablo = pd.DataFrame(
        satirlar,
        columns=[
            "1. Dosya",
            "2. Dosya",
            "Benzerlik (%)"
        ]
    )

    return tablo.sort_values(
        "Benzerlik (%)",
        ascending=False,
        ignore_index=True
    )

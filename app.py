import re
import string
from io import BytesIO

import streamlit as st
import pandas as pd
from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------------------------
# Sayfa ayarları
# --------------------------------------------------

st.set_page_config(
    page_title="Metin Benzerliği Tespit Sistemi",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Metin Benzerliği Tespit Sistemi")
st.write(
    "İki ödev dosyasını yükleyerek Jaccard, "
    "TF-IDF + kosinüs ve Bigram + kosinüs "
    "benzerliklerini karşılaştırın."
)


# --------------------------------------------------
# Dosyadan metin çıkarma
# --------------------------------------------------

def dosyadan_metin_cikar(dosya):
    uzanti = dosya.name.lower().rsplit(".", 1)[-1]

    if uzanti == "txt":
        return dosya.getvalue().decode("utf-8-sig")

    elif uzanti == "pdf":
        okuyucu = PdfReader(BytesIO(dosya.getvalue()))
        return "\n".join(
            sayfa.extract_text() or ""
            for sayfa in okuyucu.pages
        )

    elif uzanti == "docx":
        belge = Document(BytesIO(dosya.getvalue()))
        return "\n".join(
            paragraf.text
            for paragraf in belge.paragraphs
        )

    raise ValueError(
        "Yalnızca PDF, DOCX veya TXT dosyaları yükleyebilirsiniz."
    )


# --------------------------------------------------
# Metin ön işleme
# --------------------------------------------------

def metin_temizle(metin):
    metin = metin.lower()

    for isaret in string.punctuation:
        metin = metin.replace(isaret, "")

    return re.sub(r"\s+", " ", metin).strip()


# --------------------------------------------------
# Jaccard benzerliği
# --------------------------------------------------

def jaccard_benzerligi(metin1, metin2):
    kelimeler1 = set(metin1.split())
    kelimeler2 = set(metin2.split())

    birlesim = kelimeler1 | kelimeler2
    ortak = kelimeler1 & kelimeler2

    if not birlesim:
        return 0.0

    return len(ortak) / len(birlesim) * 100


# --------------------------------------------------
# TF-IDF + kosinüs benzerliği
# --------------------------------------------------

def tfidf_kosinus_benzerligi(metin1, metin2):
    vectorizer = TfidfVectorizer()
    vektorler = vectorizer.fit_transform([metin1, metin2])

    return cosine_similarity(
        vektorler[0], vektorler[1]
    )[0][0] * 100


# --------------------------------------------------
# N-gram benzerliği
# --------------------------------------------------

def ngram_benzerligi(metin1, metin2, n=2):
    """
    N-gram özelliklerini çıkarır ve kosinüs benzerliğini hesaplar.
    n=1: unigram, n=2: bigram, n=3: trigram.
    """

    vectorizer = CountVectorizer(
        ngram_range=(n, n),
        lowercase=True
    )

    try:
        vektorler = vectorizer.fit_transform([metin1, metin2])

        return cosine_similarity(
            vektorler[0], vektorler[1]
        )[0][0] * 100

    except ValueError:
        return 0.0


# --------------------------------------------------
# Ortak kelimeleri bulma
# --------------------------------------------------

def ortak_kelimeleri_bul(metin1, metin2):
    kelimeler1 = set(metin1.split())
    kelimeler2 = set(metin2.split())

    return sorted(kelimeler1 & kelimeler2)


# --------------------------------------------------
# N-gram dizilerini bulma
# --------------------------------------------------

def ngramlari_bul(metin, n=2):
    vectorizer = CountVectorizer(
        ngram_range=(n, n),
        lowercase=True
    )

    try:
        vectorizer.fit([metin])
        return set(vectorizer.get_feature_names_out())

    except ValueError:
        return set()


# --------------------------------------------------
# Ortak N-gram ifadelerini bulma
# --------------------------------------------------

def ortak_ngramlari_bul(metin1, metin2, n=2):
    ngramlar1 = ngramlari_bul(metin1, n)
    ngramlar2 = ngramlari_bul(metin2, n)

    return sorted(ngramlar1 & ngramlar2)


# --------------------------------------------------
# Dosya yükleme alanları
# --------------------------------------------------

dosya1 = st.file_uploader(
    "1. ödev dosyasını yükleyin",
    type=["txt", "pdf", "docx"],
    key="dosya1"
)

dosya2 = st.file_uploader(
    "2. ödev dosyasını yükleyin",
    type=["txt", "pdf", "docx"],
    key="dosya2"
)


# --------------------------------------------------
# Benzerlik analizi
# --------------------------------------------------

if st.button(
    "Benzerliği Hesapla",
    type="primary",
    use_container_width=True
):

    if dosya1 is None or dosya2 is None:
        st.warning("Lütfen iki dosyayı da yükleyin.")

    else:
        try:
            # Dosyalardan metin çıkarma
            ham1 = dosyadan_metin_cikar(dosya1)
            ham2 = dosyadan_metin_cikar(dosya2)

            # Metinleri temizleme
            temiz1 = metin_temizle(ham1)
            temiz2 = metin_temizle(ham2)

            if not temiz1 or not temiz2:
                st.error(
                    "Dosyalardan en az biri boş veya "
                    "okunabilir metin içermiyor."
                )

            else:
                # Algoritmaların çalıştırılması
                jaccard = jaccard_benzerligi(temiz1, temiz2)
                tfidf = tfidf_kosinus_benzerligi(temiz1, temiz2)
                bigram = ngram_benzerligi(temiz1, temiz2, n=2)

                # Ortak kelime ve ifadeler
                ortak_kelimeler = ortak_kelimeleri_bul(
                    temiz1, temiz2
                )

                ortak_bigramlar = ortak_ngramlari_bul(
                    temiz1, temiz2, n=2
                )

                # ------------------------------------------
                # Sonuç kartları
                # ------------------------------------------

                st.subheader("Analiz Sonuçları")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Jaccard",
                        f"%{jaccard:.2f}"
                    )

                with col2:
                    st.metric(
                        "TF-IDF + Kosinüs",
                        f"%{tfidf:.2f}"
                    )

                with col3:
                    st.metric(
                        "Bigram + Kosinüs",
                        f"%{bigram:.2f}"
                    )

                st.caption(
                    "Benzerlik yüzdeleri metinlerin içerik benzerliğini "
                    "gösterir; tek başına intihal kanıtı değildir."
                )

                # ------------------------------------------
                # Algoritma karşılaştırma grafiği
                # ------------------------------------------

                st.subheader("Algoritma Karşılaştırması")

                grafik_verisi = pd.DataFrame({
                    "Algoritma": [
                        "Jaccard",
                        "TF-IDF + Kosinüs",
                        "Bigram + Kosinüs"
                    ],
                    "Benzerlik (%)": [
                        jaccard,
                        tfidf,
                        bigram
                    ]
                })

                st.bar_chart(
                    grafik_verisi,
                    x="Algoritma",
                    y="Benzerlik (%)",
                    y_label="Benzerlik (%)"
                )

                # ------------------------------------------
                # Ortak kelime ve ifadeler
                # ------------------------------------------

                st.subheader("Ortak Kelime ve İfadeler")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Ortak kelime sayısı",
                        len(ortak_kelimeler)
                    )

                    if ortak_kelimeler:
                        st.write("**Ortak kelimeler:**")
                        st.write(", ".join(ortak_kelimeler))
                    else:
                        st.info("Ortak kelime bulunamadı.")

                with col2:
                    st.metric(
                        "Ortak bigram sayısı",
                        len(ortak_bigramlar)
                    )

                    if ortak_bigramlar:
                        st.write("**Ortak ikili ifadeler:**")
                        st.write(", ".join(ortak_bigramlar))
                    else:
                        st.info("Ortak ikili ifade bulunamadı.")

                # ------------------------------------------
                # Çıkarılan metinler
                # ------------------------------------------

                with st.expander("Çıkarılan metinleri görüntüle"):
                    st.write("**1. dosya:**", dosya1.name)
                    st.text(ham1[:5000])

                    st.write("**2. dosya:**", dosya2.name)
                    st.text(ham2[:5000])

        except (ValueError, UnicodeDecodeError) as hata:
            st.error(f"Dosya işlenemedi: {hata}")

        except Exception as hata:
            st.error(f"Analiz sırasında hata oluştu: {hata}")
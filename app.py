
import re
import string
from io import BytesIO

import streamlit as st
from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


st.set_page_config(
    page_title="Metin Benzerliği Tespit Sistemi",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Metin Benzerliği Tespit Sistemi")
st.write(
    "İki ödev dosyasını yükleyerek Jaccard ve "
    "TF-IDF + kosinüs benzerliklerini karşılaştırın."
)


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

    raise ValueError("Yalnızca PDF, DOCX veya TXT yükleyebilirsiniz.")


def metin_temizle(metin):
    metin = metin.lower()

    for isaret in string.punctuation:
        metin = metin.replace(isaret, "")

    return re.sub(r"\s+", " ", metin).strip()


def jaccard_benzerligi(metin1, metin2):
    kelimeler1 = set(metin1.split())
    kelimeler2 = set(metin2.split())

    birlesim = kelimeler1 | kelimeler2
    ortak = kelimeler1 & kelimeler2

    if not birlesim:
        return 0.0

    return len(ortak) / len(birlesim) * 100


def tfidf_kosinus_benzerligi(metin1, metin2):
    vectorizer = TfidfVectorizer()
    vektorler = vectorizer.fit_transform([metin1, metin2])

    return cosine_similarity(
        vektorler[0], vektorler[1]
    )[0][0] * 100


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

if st.button("Benzerliği Hesapla", type="primary", use_container_width=True):
    if dosya1 is None or dosya2 is None:
        st.warning("Lütfen iki dosyayı da yükleyin.")

    else:
        try:
            ham1 = dosyadan_metin_cikar(dosya1)
            ham2 = dosyadan_metin_cikar(dosya2)

            temiz1 = metin_temizle(ham1)
            temiz2 = metin_temizle(ham2)

            if not temiz1 or not temiz2:
                st.error(
                    "Dosyalardan en az biri boş veya "
                    "okunabilir metin içermiyor."
                )

            else:
                jaccard = jaccard_benzerligi(temiz1, temiz2)
                tfidf = tfidf_kosinus_benzerligi(temiz1, temiz2)

                st.subheader("Analiz Sonuçları")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Jaccard", f"%{jaccard:.2f}")

                with col2:
                    st.metric("TF-IDF + Kosinüs", f"%{tfidf:.2f}")

                st.caption(
                    "Bu yüzdeler metin benzerliğini gösterir; "
                    "tek başına intihal kanıtı değildir."
                )

                with st.expander("Çıkarılan metinleri görüntüle"):
                    st.write("**1. dosya**")
                    st.text(ham1[:5000])
                    st.write("**2. dosya**")
                    st.text(ham2[:5000])

        except (ValueError, UnicodeDecodeError) as hata:
            st.error(f"Dosya işlenemedi: {hata}")

        except Exception as hata:
            st.error(f"Analiz sırasında hata oluştu: {hata}")

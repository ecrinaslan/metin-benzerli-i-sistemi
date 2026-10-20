
from pathlib import Path
import re
import string

from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROJE_KLASORU = Path(__file__).resolve().parent.parent
ODEVLER_KLASORU = PROJE_KLASORU / "Odevler"

dosya1_yolu = ODEVLER_KLASORU / "odev1.txt"
dosya2_yolu = ODEVLER_KLASORU / "odev2.txt"


def dosyadan_metin_cikar(dosya_yolu):
    yol = Path(dosya_yolu)
    uzanti = yol.suffix.lower()

    if uzanti == ".txt":
        return yol.read_text(encoding="utf-8")

    elif uzanti == ".pdf":
        okuyucu = PdfReader(str(yol))
        return "\n".join(
            sayfa.extract_text() or ""
            for sayfa in okuyucu.pages
        )

    elif uzanti == ".docx":
        belge = Document(str(yol))
        return "\n".join(
            paragraf.text
            for paragraf in belge.paragraphs
        )

    else:
        raise ValueError(
            "Desteklenmeyen dosya türü: PDF, DOCX veya TXT kullanın."
        )


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

    benzerlik = cosine_similarity(
        vektorler[0], vektorler[1]
    )[0][0]

    return benzerlik * 100


def main():
    try:
        ham1 = dosyadan_metin_cikar(dosya1_yolu)
        ham2 = dosyadan_metin_cikar(dosya2_yolu)

        temiz1 = metin_temizle(ham1)
        temiz2 = metin_temizle(ham2)

        if not temiz1 or not temiz2:
            print("Hata: Dosyalardan en az biri boş metin içeriyor.")
            return

        jaccard = jaccard_benzerligi(temiz1, temiz2)
        tfidf = tfidf_kosinus_benzerligi(temiz1, temiz2)

        print("\n--- DOSYA BENZERLİK ANALİZİ ---")
        print("1. Dosya:", dosya1_yolu.name)
        print("2. Dosya:", dosya2_yolu.name)
        print("-" * 35)
        print(f"Jaccard benzerliği       : %{jaccard:.2f}")
        print(f"TF-IDF + Kosinüs         : %{tfidf:.2f}")
        print("-" * 35)

    except FileNotFoundError as hata:
        print("Dosya bulunamadı:", hata.filename)

    except ValueError as hata:
        print("Analiz hatası:", hata)


if __name__ == "__main__":
    main()

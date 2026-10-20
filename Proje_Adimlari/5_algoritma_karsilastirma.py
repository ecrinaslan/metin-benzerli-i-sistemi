
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROJE_KLASORU = Path(__file__).resolve().parent.parent
ODEVLER_KLASORU = PROJE_KLASORU / "Odevler"

dosya1_yolu = ODEVLER_KLASORU / "odev1.txt"
dosya2_yolu = ODEVLER_KLASORU / "odev2.txt"


def metin_oku(dosya_yolu):
    with open(dosya_yolu, "r", encoding="utf-8") as dosya:
        return dosya.read()


def metin_temizle(metin):
    import string

    metin = metin.lower()

    for isaret in string.punctuation:
        metin = metin.replace(isaret, "")

    return metin


def jaccard_benzerligi(metin1, metin2):
    kelimeler1 = set(metin_temizle(metin1).split())
    kelimeler2 = set(metin_temizle(metin2).split())

    birlesim = kelimeler1.union(kelimeler2)
    ortak = kelimeler1.intersection(kelimeler2)

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
        metin1 = metin_oku(dosya1_yolu)
        metin2 = metin_oku(dosya2_yolu)

        jaccard_sonuc = jaccard_benzerligi(metin1, metin2)
        tfidf_sonuc = tfidf_kosinus_benzerligi(metin1, metin2)

        print("\n--- METİN BENZERLİĞİ KARŞILAŞTIRMASI ---")
        print(f"1. Dosya: {dosya1_yolu.name}")
        print(f"2. Dosya: {dosya2_yolu.name}")
        print("----------------------------------------")
        print(f"Jaccard Benzerliği       : %{jaccard_sonuc:.2f}")
        print(f"TF-IDF + Kosinüs         : %{tfidf_sonuc:.2f}")
        print("----------------------------------------")

    except FileNotFoundError as hata:
        print("Dosya bulunamadı:", hata.filename)

    except ValueError as hata:
        print("Metinler analiz edilemedi:", hata)


if __name__ == "__main__":
    main()

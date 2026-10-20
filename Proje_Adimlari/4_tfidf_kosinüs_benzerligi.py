
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

        sonuc = tfidf_kosinus_benzerligi(metin1, metin2)

        print("----- TF-IDF BENZERLİK ANALİZİ -----")
        print(f"1. Dosya: {dosya1_yolu.name}")
        print(f"2. Dosya: {dosya2_yolu.name}")
        print(f"TF-IDF Kosinüs Benzerliği: %{sonuc:.2f}")

    except FileNotFoundError as hata:
        print("Hata: Dosya bulunamadı.")
        print("Aranan dosya:", hata.filename)

    except ValueError as hata:
        print("Metinler analiz edilemedi:", hata)


if __name__ == "__main__":
    main()

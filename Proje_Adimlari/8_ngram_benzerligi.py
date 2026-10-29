from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def ngram_benzerligi(metin1, metin2, n=2):
    """
    İki metin arasındaki N-gram benzerliğini hesaplar.

    n=1: Unigram (tek kelimeler)
    n=2: Bigram (iki kelimelik diziler)
    n=3: Trigram (üç kelimelik diziler)
    """

    if not metin1.strip() or not metin2.strip():
        return 0.0

    vectorizer = CountVectorizer(
        ngram_range=(n, n),
        lowercase=True
    )

    try:
        matris = vectorizer.fit_transform([metin1, metin2])
        benzerlik = cosine_similarity(matris[0], matris[1])[0][0]
        return round(float(benzerlik) * 100, 2)

    except ValueError:
        # İstenen uzunlukta kelime dizisi bulunamadığında
        return 0.0


if __name__ == "__main__":
    metin1 = "öğrenci başarı oranı metin analizi"
    metin2 = "öğrenci başarı oranı veri analizi"

    for n in (1, 2, 3):
        sonuc = ngram_benzerligi(metin1, metin2, n)
        print(f"{n}-gram benzerliği: %{sonuc}")
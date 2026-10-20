
from pathlib import Path
from pypdf import PdfReader
from docx import Document


def txt_metni_oku(dosya_yolu):
    """TXT dosyasından metin çıkarır."""
    return Path(dosya_yolu).read_text(encoding="utf-8")


def pdf_metni_oku(dosya_yolu):
    """PDF dosyasındaki metinleri çıkarır."""
    okuyucu = PdfReader(dosya_yolu)
    sayfa_metinleri = []

    for sayfa in okuyucu.pages:
        metin = sayfa.extract_text() or ""
        sayfa_metinleri.append(metin)

    return "\n".join(sayfa_metinleri)


def docx_metni_oku(dosya_yolu):
    """DOCX dosyasındaki paragrafları okur."""
    belge = Document(dosya_yolu)
    paragraflar = []

    for paragraf in belge.paragraphs:
        if paragraf.text.strip():
            paragraflar.append(paragraf.text)

    return "\n".join(paragraflar)


def dosyadan_metin_cikar(dosya_yolu):
    """Dosya uzantısına göre uygun okuma fonksiyonunu çağırır."""
    yol = Path(dosya_yolu)
    uzanti = yol.suffix.lower()

    if uzanti == ".txt":
        return txt_metni_oku(yol)

    elif uzanti == ".pdf":
        return pdf_metni_oku(yol)

    elif uzanti == ".docx":
        return docx_metni_oku(yol)

    else:
        raise ValueError(
            "Desteklenmeyen dosya türü. "
            "PDF, DOCX veya TXT kullanın."
        )


if __name__ == "__main__":
    proje_klasoru = Path(__file__).resolve().parent.parent
    odevler_klasoru = proje_klasoru / "Odevler"

    dosya_yolu = odevler_klasoru / "odev1.txt"

    try:
        metin = dosyadan_metin_cikar(dosya_yolu)

        print("Dosya başarıyla okundu!")
        print("Dosya adı:", dosya_yolu.name)
        print("Çıkarılan karakter sayısı:", len(metin))
        print("\nMetnin ilk 500 karakteri:")
        print(metin[:500])

    except (FileNotFoundError, ValueError) as hata:
        print("Hata:", hata)

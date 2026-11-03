from pathlib import Path

import pytest

import benzerlik
from benzerlik import (
    DOLGU_KELIMELERI,
    dosyadan_metin_oku,
    jaccard_benzerligi,
    metin_on_isle,
    metin_temizle,
    ngram_benzerligi,
    tfidf_benzerligi,
    turkce_kucuk_harf,
)

ODEVLER = Path(__file__).resolve().parent.parent / "Odevler"


def odev(dosya_adi, **ayarlar):
    return metin_on_isle(dosyadan_metin_oku(ODEVLER / dosya_adi), **ayarlar)


@pytest.fixture(scope="module")
def orijinal():
    return odev("01_orijinal.txt")


#---Türkçe küçük harf ve temizleme---
def test_turkce_kucuk_harf():
    assert turkce_kucuk_harf("İSTANBUL IŞIK") == "istanbul ışık"


def test_turkce_kucuk_harf_tum_ozel_harfler():
    assert turkce_kucuk_harf("ÇĞİIÖŞÜ") == "çğiıöşü"


def test_metin_temizle_turkce_noktalama_ve_sayilari_siler():
    metin = "“İstanbul’un” 2024’te — «IŞIK»… ‘Zekâ’ – Türkiye'nin."
    assert metin_temizle(metin) == "istanbulun te ışık zeka türkiyenin"


def test_buyuk_harfli_metin_kucuk_harfliyle_ayni_sayilir():
    assert jaccard_benzerligi(metin_temizle("İSTANBUL IŞIK"), metin_temizle("istanbul ışık")) == 100


#---Dolgu kelimeleri ve kök bulma---
def test_dolgu_listesi_yeterince_kapsamli():
    assert len(DOLGU_KELIMELERI) >= 80
    assert {"ve", "ile", "ama", "için", "bu", "bir", "mi", "mü"} <= DOLGU_KELIMELERI


def test_dolgu_kelimeleri_cikariliyor():
    metin = "Öğrenciler ve öğretmenler bu yeni araç ile daha çok çalışıyor mu?"
    assert metin_on_isle(metin, dolgu_cikar=True) == "öğrenciler öğretmenler yeni araç çalışıyor"


def test_dosyada_hic_dolgu_kelimesi_kalmiyor(orijinal):
    dolgusuz = set(odev("01_orijinal.txt", dolgu_cikar=True).split())
    assert {"ve", "bu", "bir", "için"} <= set(orijinal.split())
    assert not dolgusuz & DOLGU_KELIMELERI


def test_kok_bulma():
    assert metin_on_isle("Öğrencilerin kitaplarından", kok_bul=True) == "öğrenci kitap"


def test_kok_bulucu_yoksa_metin_degismeden_doner(monkeypatch):
    monkeypatch.setattr(benzerlik, "KOK_BULMA_KULLANILABILIR", False)
    with pytest.warns(UserWarning):
        assert metin_on_isle("Öğrencilerin kitaplarından", kok_bul=True) == "öğrencilerin kitaplarından"


#---Benzerlik yöntemleri---
@pytest.mark.parametrize("ayarlar", [{}, {"dolgu_cikar": True}, {"dolgu_cikar": True, "kok_bul": True}])
def test_ayni_metin_tum_yontemlerde_yuzde_yuz(ayarlar):
    metin = odev("01_orijinal.txt", **ayarlar)
    assert jaccard_benzerligi(metin, metin) == pytest.approx(100)
    assert tfidf_benzerligi(metin, metin) == pytest.approx(100)
    for n in (1, 2, 3):
        assert ngram_benzerligi(metin, metin, n=n) == pytest.approx(100)


@pytest.mark.parametrize("metin1, metin2", [("", ""), ("", "yapay zeka"), ("zeka", "zeka"), ("bir iki", "bir iki")])
def test_bos_veya_kisa_metinde_ngram_sifir_doner(metin1, metin2):
    #"bir iki" iki kelimelik olduğu için içinde hiç trigram yoktur.
    assert ngram_benzerligi(metin1, metin2, n=3) == 0


def test_bos_metinde_jaccard_ve_tfidf_sifir_doner():
    assert jaccard_benzerligi("", "") == 0
    assert tfidf_benzerligi("", "") == 0


#---Senaryolar---
def test_tfidf_senaryo_siralamasi(orijinal):
    benzerlik_orani = {dosya: tfidf_benzerligi(orijinal, odev(dosya)) for dosya in [
        "02_birebir_kopya.txt", "03_kismi_kopya.txt", "07_ayni_konu_ozgun.txt", "06_farkli_konu.txt"]}
    oranlar = list(benzerlik_orani.values())
    assert oranlar == sorted(oranlar, reverse=True), benzerlik_orani


def test_cumle_sirasi_degisince_jaccard_yuksek_trigram_dusuk(orijinal):
    karisik = odev("05_cumle_sirasi_degisik.txt")
    kopya = odev("02_birebir_kopya.txt")
    jaccard = jaccard_benzerligi(orijinal, karisik)
    trigram = ngram_benzerligi(orijinal, karisik, n=3)
    assert jaccard >= 90
    assert trigram <= jaccard - 10
    assert trigram < ngram_benzerligi(orijinal, kopya, n=3)


def test_buyuk_harfli_turkce_dosya_orijinalle_neredeyse_ayni(orijinal):
    buyuk_harfli = odev("08_buyuk_harf_turkce.txt")
    assert jaccard_benzerligi(orijinal, buyuk_harfli) >= 95
    #Eski yöntem (sadece lower()) aynı metinleri çok daha farklı bulur.
    eski = lambda metin: benzerlik.metin_temizle(metin.lower())  # noqa: E731
    ham1, ham2 = (dosyadan_metin_oku(ODEVLER / d) for d in ("01_orijinal.txt", "08_buyuk_harf_turkce.txt"))
    assert jaccard_benzerligi(eski(ham1), eski(ham2)) < 70


#---Dosya biçimleri---
@pytest.mark.parametrize("uzanti", ["docx", "pdf"])
def test_txt_docx_pdf_ayni_sonucu_verir(orijinal, uzanti):
    diger = odev(f"01_orijinal.{uzanti}")
    kaynak = odev("03_kismi_kopya.txt")
    assert jaccard_benzerligi(orijinal, diger) >= 99
    assert tfidf_benzerligi(orijinal, kaynak) == pytest.approx(tfidf_benzerligi(diger, kaynak), abs=1)
    assert ngram_benzerligi(orijinal, kaynak, n=2) == pytest.approx(ngram_benzerligi(diger, kaynak, n=2), abs=1)


#---Çoklu karşılaştırma---
def test_benzerlik_matrisi_ve_supheli_eslesmeler():
    metinler = {d: odev(d) for d in ["01_orijinal.txt", "02_birebir_kopya.txt", "06_farkli_konu.txt"]}
    matris = benzerlik.benzerlik_matrisi(metinler, "Jaccard")
    assert matris.shape == (3, 3)
    assert (matris.values == matris.values.T).all() #Matris simetrik olmalı
    assert matris.loc["01_orijinal.txt", "01_orijinal.txt"] == 100

    supheliler = benzerlik.supheli_eslesmeler(matris, esik=50)
    assert len(supheliler) == 1 #Sadece 01-02 çifti eşiği aşar; her çift bir kez listelenir
    assert set(supheliler.iloc[0][["1. Dosya", "2. Dosya"]]) == {"01_orijinal.txt", "02_birebir_kopya.txt"}
    assert benzerlik.supheli_eslesmeler(matris, esik=0)["Benzerlik (%)"].is_monotonic_decreasing

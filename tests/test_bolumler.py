import pytest

from benzerlik import bolum_basligini_normalize_et, bolumlere_ayir


#---Başlık normalizasyonu---
@pytest.mark.parametrize("baslik, beklenen", [
    ("1. GİRİŞ", "giriş"),
    ("2. Giriş", "giriş"),
    ("Giriş", "giriş"),
    ("3.2 Materyal ve Yöntem", "materyal ve yöntem"),
    ("1.2.3. Sonuç", "sonuç"),
    ("  4 ÖZET  ", "özet"),
    ("IŞIK", "ışık"),
])
def test_bolum_basligini_normalize_et(baslik, beklenen):
    assert bolum_basligini_normalize_et(baslik) == beklenen


def test_numarali_ve_numarasiz_ayni_baslik_ayni_anahtari_verir():
    assert bolum_basligini_normalize_et("1. GİRİŞ") == bolum_basligini_normalize_et("Giriş")


#---Bölümlere ayırma---
def test_numarasiz_basliklar_bolumlere_ayrilir():
    metin = "Giriş\nBu bir giriş metnidir.\nSonuç\nBu da sonuç metnidir."
    bolumler = bolumlere_ayir(metin)
    assert list(bolumler) == ["giriş", "sonuç"]
    assert bolumler["giriş"] == {"baslik": "Giriş", "metin": "Bu bir giriş metnidir."}
    assert bolumler["sonuç"]["metin"] == "Bu da sonuç metnidir."


def test_numarali_basliklar_bolumlere_ayrilir():
    metin = "1. GİRİŞ\nGiriş içeriği.\n2. YÖNTEM\nYöntem içeriği.\n3. SONUÇ\nSonuç içeriği."
    bolumler = bolumlere_ayir(metin)
    assert list(bolumler) == ["giriş", "yöntem", "sonuç"]
    #Numaralı başlıklarda numara atılmış başlık saklanır.
    assert bolumler["giriş"]["baslik"] == "GİRİŞ"
    assert bolumler["yöntem"]["metin"] == "Yöntem içeriği."


def test_cok_kelimeli_bilinen_baslik():
    bolumler = bolumlere_ayir("Materyal ve Yöntem\nAnket uygulandı.")
    assert bolumler["materyal ve yöntem"]["metin"] == "Anket uygulandı."


def test_farkli_yazilan_ayni_basliklar_eslesir():
    bolumler1 = bolumlere_ayir("1. GİRİŞ\nBirinci metin.")
    bolumler2 = bolumlere_ayir("Giriş\nİkinci metin.")
    assert set(bolumler1) == set(bolumler2) == {"giriş"}


def test_bilinmeyen_baslik_onceki_bolume_eklenir():
    metin = "Giriş\nİlk paragraf.\n2. Deneyler\nDeney paragrafı."
    bolumler = bolumlere_ayir(metin)
    assert list(bolumler) == ["giriş"]
    assert bolumler["giriş"]["metin"] == "İlk paragraf.\n2. Deneyler\nDeney paragrafı."


def test_ayni_baslik_iki_kez_gecerse_birlestirilir():
    metin = "Giriş\nBirinci kısım.\nSonuç\nSon.\nGiriş\nİkinci kısım."
    bolumler = bolumlere_ayir(metin)
    assert bolumler["giriş"]["metin"] == "Birinci kısım.\nİkinci kısım."


def test_icerigi_bos_bolum_atlanir():
    bolumler = bolumlere_ayir("Giriş\n\n\nSonuç\nSonuç içeriği.")
    assert list(bolumler) == ["sonuç"]


def test_bolum_icindeki_bos_satirlar_korunur_kenarlar_kirpilir():
    bolumler = bolumlere_ayir("Giriş\n\nBirinci paragraf.\n\nİkinci paragraf.\n\n")
    assert bolumler["giriş"]["metin"] == "Birinci paragraf.\n\nİkinci paragraf."


def test_ilk_basliktan_onceki_metin_alinmaz():
    bolumler = bolumlere_ayir("Kapak sayfası\nÖğrenci adı\nGiriş\nAsıl içerik.")
    assert list(bolumler) == ["giriş"]
    assert bolumler["giriş"]["metin"] == "Asıl içerik."


@pytest.mark.parametrize("metin", ["", "Başlıksız bir metin.\nİkinci satır."])
def test_baslik_yoksa_belgenin_tamami_tek_bolumdur(metin):
    assert bolumlere_ayir(metin) == {
        "belgenin tamamı": {"baslik": "Belgenin Tamamı", "metin": metin}
    }


def test_basligi_iceren_cumle_baslik_sayilmaz():
    bolumler = bolumlere_ayir("Sonuç olarak bu çalışma tamamlandı.")
    assert list(bolumler) == ["belgenin tamamı"]

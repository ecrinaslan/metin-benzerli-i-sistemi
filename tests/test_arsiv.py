import sqlite3

import pytest

import arsiv


@pytest.fixture(autouse=True)
def gecici_veritabani(tmp_path, monkeypatch):
    #Gerçek odev_arsivi.db kirlenmesin diye her test kendi geçici veritabanını kullanır.
    yol = tmp_path / "test_arsivi.db"
    monkeypatch.setattr(arsiv, "VERITABANI", yol)
    arsiv.arsiv_tablosunu_hazirla()
    return yol


def ekle(dosya_adi, metin):
    return arsiv.arsive_ekle(dosya_adi, metin, metin.encode("utf-8"))


#---Tablo hazırlama---
def test_tablo_olusturulur(gecici_veritabani):
    assert gecici_veritabani.exists()
    with sqlite3.connect(gecici_veritabani) as conn:
        sutunlar = {satir[1] for satir in conn.execute("PRAGMA table_info(odevler)")}
    assert sutunlar == {"id", "dosya_adi", "dosya_turu", "metin", "dosya_hash", "yuklenme_tarihi"}


def test_tablo_hazirlama_tekrar_cagrilabilir():
    ekle("a.txt", "metin")
    arsiv.arsiv_tablosunu_hazirla()
    assert len(arsiv.arsiv_listesi()) == 1


def test_gercek_veritabani_kullanilmiyor(gecici_veritabani):
    assert arsiv.VERITABANI == gecici_veritabani
    assert arsiv.VERITABANI.name != "odev_arsivi.db"


#---Dosya özeti---
def test_dosya_ozeti_sha256():
    ozet = arsiv.dosya_ozeti(b"abc")
    assert ozet == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_farkli_icerik_farkli_ozet():
    assert arsiv.dosya_ozeti(b"birinci") != arsiv.dosya_ozeti(b"ikinci")


#---Arşive ekleme---
def test_yeni_dosya_eklenir():
    kayit_id, yeni = ekle("odev1.txt", "İstanbul güzel bir şehir.")
    assert yeni is True
    assert isinstance(kayit_id, int)

    kayit = arsiv.arsiv_listesi()[0]
    assert kayit["id"] == kayit_id
    assert kayit["dosya_adi"] == "odev1.txt"
    assert kayit["dosya_turu"] == "txt"
    assert kayit["yuklenme_tarihi"]


@pytest.mark.parametrize("dosya_adi, tur", [("Odev.PDF", "pdf"), ("rapor.Docx", "docx"), ("uzantisiz", "")])
def test_dosya_turu_kucuk_harfle_ve_noktasiz_kaydedilir(dosya_adi, tur):
    ekle(dosya_adi, "içerik")
    assert arsiv.arsiv_listesi()[0]["dosya_turu"] == tur


def test_ayni_icerik_tekrar_eklenmez():
    ilk_id, ilk_yeni = ekle("odev.txt", "aynı içerik")
    ikinci_id, ikinci_yeni = ekle("baska_ad.txt", "aynı içerik")
    assert ilk_yeni is True
    assert ikinci_yeni is False
    assert ikinci_id == ilk_id
    assert len(arsiv.arsiv_listesi()) == 1
    #Mevcut kaydın adı değişmez.
    assert arsiv.arsiv_listesi()[0]["dosya_adi"] == "odev.txt"


def test_ayni_ad_farkli_icerik_ayri_kayit_olur():
    ekle("odev.txt", "birinci sürüm")
    ekle("odev.txt", "ikinci sürüm")
    assert len(arsiv.arsiv_listesi()) == 2


def test_turkce_metin_bozulmadan_saklanir():
    metin = "IŞIK İSTANBUL’da “zekâ” ÇĞÖŞÜ"
    kayit_id, _ = ekle("turkce.txt", metin)
    assert arsiv.arsiv_metinlerini_getir([kayit_id])[0]["metin"] == metin


#---Listeleme---
def test_bos_arsiv_listesi():
    assert arsiv.arsiv_listesi() == []


def test_liste_en_yeni_kayit_basta():
    idler = [ekle(f"odev{i}.txt", f"metin {i}")[0] for i in range(3)]
    assert [kayit["id"] for kayit in arsiv.arsiv_listesi()] == idler[::-1]


def test_liste_metin_ve_hash_dondurmez():
    ekle("odev.txt", "metin")
    assert set(arsiv.arsiv_listesi()[0]) == {"id", "dosya_adi", "dosya_turu", "yuklenme_tarihi"}


#---Metinleri getirme---
@pytest.fixture
def uc_kayit():
    return [ekle(f"odev{i}.txt", f"metin {i}")[0] for i in range(3)]


def test_none_verilirse_tum_kayitlar_id_sirasiyla_gelir(uc_kayit):
    sonuc = arsiv.arsiv_metinlerini_getir()
    assert [kayit["id"] for kayit in sonuc] == uc_kayit
    assert set(sonuc[0]) == {"id", "dosya_adi", "metin"}
    assert sonuc[0]["metin"] == "metin 0"


def test_bos_liste_verilirse_hicbir_kayit_gelmez(uc_kayit):
    assert arsiv.arsiv_metinlerini_getir([]) == []


def test_sadece_secilen_kayitlar_gelir(uc_kayit):
    sonuc = arsiv.arsiv_metinlerini_getir([uc_kayit[2], uc_kayit[0]])
    assert [kayit["id"] for kayit in sonuc] == [uc_kayit[0], uc_kayit[2]]


def test_haric_id_sonuctan_cikarilir(uc_kayit):
    sonuc = arsiv.arsiv_metinlerini_getir(haric_id=uc_kayit[1])
    assert [kayit["id"] for kayit in sonuc] == [uc_kayit[0], uc_kayit[2]]


def test_secim_ve_haric_birlikte_calisir(uc_kayit):
    sonuc = arsiv.arsiv_metinlerini_getir(uc_kayit[:2], haric_id=uc_kayit[0])
    assert [kayit["id"] for kayit in sonuc] == [uc_kayit[1]]


def test_sadece_haric_tutulan_secilirse_bos_doner(uc_kayit):
    assert arsiv.arsiv_metinlerini_getir([uc_kayit[0]], haric_id=uc_kayit[0]) == []


def test_generator_ile_secim_yapilabilir(uc_kayit):
    sonuc = arsiv.arsiv_metinlerini_getir(kayit_id for kayit_id in uc_kayit[:2])
    assert len(sonuc) == 2


def test_olmayan_id_sessizce_yok_sayilir(uc_kayit):
    assert [kayit["id"] for kayit in arsiv.arsiv_metinlerini_getir([uc_kayit[0], 9999])] == [uc_kayit[0]]


#---Silme---
def test_kayit_silinir(uc_kayit):
    arsiv.arsivden_sil(uc_kayit[1])
    assert [kayit["id"] for kayit in arsiv.arsiv_listesi()] == [uc_kayit[2], uc_kayit[0]]


def test_olmayan_kaydi_silmek_hata_vermez(uc_kayit):
    arsiv.arsivden_sil(9999)
    assert len(arsiv.arsiv_listesi()) == 3


def test_silinen_dosya_yeniden_eklenebilir():
    kayit_id, _ = ekle("odev.txt", "metin")
    arsiv.arsivden_sil(kayit_id)
    _, yeni = ekle("odev.txt", "metin")
    assert yeni is True
    assert len(arsiv.arsiv_listesi()) == 1

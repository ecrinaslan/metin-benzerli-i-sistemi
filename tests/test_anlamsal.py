import zlib
from pathlib import Path

import numpy as np
import pytest

import benzerlik
from benzerlik import (
    ANLAMSAL_PARCA_UZUNLUGU,
    anlamsal_benzerlik,
    dosyadan_metin_oku,
    metin_on_isle,
    metni_parcala,
    tfidf_benzerligi,
)

ODEVLER = Path(__file__).resolve().parent.parent / "Odevler"


class SahteModel:
    """Gerçek model yerine kullanılan hızlı, deterministik kelime torbası "modeli"."""

    def __init__(self):
        self.cagrilar = 0

    def encode(self, parcalar, normalize_embeddings=True):
        self.cagrilar += 1
        vektorler = np.zeros((len(parcalar), 64))
        for i, parca in enumerate(parcalar):
            for kelime in parca.split():
                vektorler[i, zlib.crc32(kelime.encode()) % 64] += 1
        normlar = np.linalg.norm(vektorler, axis=1, keepdims=True)
        return vektorler / np.where(normlar == 0, 1, normlar)


@pytest.fixture(autouse=True)
def onbellegi_temizle():
    benzerlik.metin_vektorleri.cache_clear()
    yield
    benzerlik.metin_vektorleri.cache_clear()


@pytest.fixture
def sahte_model(monkeypatch):
    model = SahteModel()
    monkeypatch.setattr(benzerlik, "anlamsal_model", lambda: model)
    return model


#---Metni parçalama---
def test_kisa_metin_tek_parca():
    assert metni_parcala("yapay zeka eğitim") == ["yapay zeka eğitim"]


def test_uzun_metin_parcalara_bolunur():
    metin = " ".join(f"k{i}" for i in range(2 * ANLAMSAL_PARCA_UZUNLUGU + 5))
    parcalar = metni_parcala(metin)
    assert [len(p.split()) for p in parcalar] == [ANLAMSAL_PARCA_UZUNLUGU, ANLAMSAL_PARCA_UZUNLUGU, 5]
    #Parçalar birleştirilince hiçbir kelime kaybolmamalı.
    assert " ".join(parcalar) == metin


def test_ozel_parca_uzunlugu():
    assert metni_parcala("a b c d e", uzunluk=2) == ["a b", "c d", "e"]


def test_bos_metin_parca_vermez():
    assert metni_parcala("") == []
    assert metni_parcala("   ") == []


#---Benzerlik hesabı (sahte modelle)---
def test_ayni_metin_yuzde_yuz(sahte_model):
    assert anlamsal_benzerlik("yapay zeka eğitimde", "yapay zeka eğitimde") == pytest.approx(100)


@pytest.mark.parametrize("metin1, metin2", [("", ""), ("", "yapay zeka"), ("yapay zeka", "   ")])
def test_bos_metinde_sifir_doner_ve_model_yuklenmez(metin1, metin2, monkeypatch):
    def yuklenmemeli():
        raise AssertionError("Boş metin için model yüklenmemeli")
    monkeypatch.setattr(benzerlik, "anlamsal_model", yuklenmemeli)
    assert anlamsal_benzerlik(metin1, metin2) == 0


def test_sonuc_simetrik(sahte_model):
    metin1 = "yapay zeka öğrencilere kişisel öğrenme sunar " * 30
    metin2 = "iklim değişikliği tarımı etkiler yapay zeka " * 10
    assert anlamsal_benzerlik(metin1, metin2) == pytest.approx(anlamsal_benzerlik(metin2, metin1))


def test_sonuc_yuzde_sifir_ile_yuz_arasinda(sahte_model):
    oran = anlamsal_benzerlik("bir iki üç", "dört beş altı")
    assert 0 <= oran <= 100


def test_negatif_kosinus_sifira_kirpilir(monkeypatch):
    class TersModel:
        def encode(self, parcalar, normalize_embeddings=True):
            return np.array([[1.0, 0.0]] if parcalar[0] == "a" else [[-1.0, 0.0]])
    monkeypatch.setattr(benzerlik, "anlamsal_model", lambda: TersModel())
    assert anlamsal_benzerlik("a", "b") == 0


def test_kismi_kopya_tam_kopyadan_dusuk(sahte_model):
    n = ANLAMSAL_PARCA_UZUNLUGU
    kopya_kisim = " ".join(f"ortak{i}" for i in range(n))
    orijinal = kopya_kisim + " " + " ".join(f"ozgun{i}" for i in range(n))
    kismi = kopya_kisim + " " + " ".join(f"yeni{i}" for i in range(n))
    tam = anlamsal_benzerlik(orijinal, orijinal)
    kismi_oran = anlamsal_benzerlik(orijinal, kismi)
    assert 0 < kismi_oran < tam


def test_vektorler_onbellekte_tutulur(sahte_model):
    metinler = {f"d{i}": f"metin numara {i} yapay zeka" for i in range(4)}
    benzerlik.benzerlik_matrisi(metinler, "Anlamsal (Çok Dilli Model)") if benzerlik.ANLAMSAL_KULLANILABILIR else [
        anlamsal_benzerlik(a, b) for a in metinler.values() for b in metinler.values()]
    #6 dosya çifti karşılaştırılsa da her metin yalnızca bir kez vektöre çevrilir.
    assert sahte_model.cagrilar == len(metinler)


def test_paket_varsa_yontem_listesinde():
    assert ("Anlamsal (Çok Dilli Model)" in benzerlik.YONTEMLER) == benzerlik.ANLAMSAL_KULLANILABILIR


#---Gerçek modelle senaryo testleri---
@pytest.fixture(scope="module")
def gercek_model():
    #Model daha önce indirilmediyse (veya paket yoksa) bu testler atlanır;
    #böylece testler internet bağlantısı gerektirmez.
    st = pytest.importorskip("sentence_transformers")
    try:
        return st.SentenceTransformer(benzerlik.ANLAMSAL_MODEL_ADI, local_files_only=True)
    except Exception as hata:
        pytest.skip(f"Anlamsal model bu bilgisayarda indirilmemiş: {hata}")


@pytest.fixture
def model(gercek_model, monkeypatch):
    monkeypatch.setattr(benzerlik, "anlamsal_model", lambda: gercek_model)


def odev(dosya_adi):
    return metin_on_isle(dosyadan_metin_oku(ODEVLER / dosya_adi))


@pytest.fixture(scope="module")
def orijinal():
    return odev("01_orijinal.txt")


def test_gercek_model_birebir_kopya(model, orijinal):
    assert anlamsal_benzerlik(orijinal, odev("02_birebir_kopya.txt")) >= 95


def test_gercek_model_farkli_konu_dusuk(model, orijinal):
    assert anlamsal_benzerlik(orijinal, odev("06_farkli_konu.txt")) < 40


def test_gercek_model_es_anlamli_degisikligi_yakalar(model, orijinal):
    esanlamli = odev("04_esanlamli_degisiklik.txt")
    anlamsal = anlamsal_benzerlik(orijinal, esanlamli)
    #Kelimeler değiştiği için TF-IDF düşük kalır, anlamsal yöntem ise benzerliği yakalar.
    assert anlamsal >= 70
    assert anlamsal >= tfidf_benzerligi(orijinal, esanlamli) + 20


def test_gercek_model_senaryo_siralamasi(model, orijinal):
    oranlar = {d: anlamsal_benzerlik(orijinal, odev(d)) for d in [
        "02_birebir_kopya.txt", "04_esanlamli_degisiklik.txt", "06_farkli_konu.txt"]}
    assert list(oranlar.values()) == sorted(oranlar.values(), reverse=True), oranlar

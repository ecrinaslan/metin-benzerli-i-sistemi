import altair as alt
import pandas as pd
import streamlit as st

from benzerlik import (
    KOK_BULMA_KULLANILABILIR,
    YONTEMLER,
    benzerlik_matrisi,
    metin_cikar,
    metin_on_isle,
    ortak_kelimeler,
    ortak_ngramlar,
    supheli_eslesmeler,
)

DOSYA_TURLERI = ["txt", "pdf", "docx"]
#Isı haritası için tek tonlu mavi skala: açık = düşük benzerlik, koyu = yüksek benzerlik
ISI_HARITASI_RENKLERI = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]


def csv_baytlari(tablo, index=False):
    #Excel'in Türkçe karakterleri doğru göstermesi için UTF-8 BOM ile kaydediyoruz.
    return tablo.to_csv(index=index).encode("utf-8-sig")


def dosya_oku(dosya):
    #Bozuk/şifreli PDF veya DOCX uygulamayı çökertmesin; hatayı gösterip None döndürüyoruz.
    try:
        return metin_cikar(dosya.name, dosya.getvalue())
    except Exception as hata:
        st.error(f"{dosya.name} işlenemedi: {hata}")
        return None


def isi_haritasi(matris):
    #Altair alan adlarındaki "." işaretini iç içe alan sandığı için noktasız adlar kullanıyoruz.
    veri = matris.rename_axis("dosya1").reset_index().melt(id_vars="dosya1", var_name="dosya2", value_name="oran")
    sira = list(matris.index)
    temel = alt.Chart(veri).encode(
        x=alt.X("dosya2:N", sort=sira, title=None, axis=alt.Axis(labelAngle=-40, labelLimit=250)),
        y=alt.Y("dosya1:N", sort=sira, title=None, axis=alt.Axis(labelLimit=250)),
    )
    hucreler = temel.mark_rect(stroke="white", strokeWidth=2).encode(
        color=alt.Color("oran:Q", scale=alt.Scale(domain=[0, 100], range=ISI_HARITASI_RENKLERI),
                        legend=alt.Legend(title="Benzerlik (%)")),
        tooltip=[alt.Tooltip("dosya1:N", title="1. Dosya"), alt.Tooltip("dosya2:N", title="2. Dosya"),
                 alt.Tooltip("oran:Q", title="Benzerlik (%)", format=".2f")],
    )
    #Koyu hücrelerde beyaz, açık hücrelerde siyah yazı kullanıyoruz.
    etiketler = temel.mark_text(fontSize=12).encode(
        text=alt.Text("oran:Q", format=".0f"),
        color=alt.condition(alt.datum.oran >= 55, alt.value("white"), alt.value("#1f1f1f")),
    )
    boyut = max(300, 60 * len(sira))
    return (hucreler + etiketler).properties(width=boyut, height=boyut)


#---ARAYÜZ---
st.set_page_config(page_title="İntihal Tespit Sistemi", layout="wide")
st.title("İntihal Tespit Sistemi")

#Kenar çubuğu: ön işleme ayarları (seçime göre tüm yöntemler yeniden hesaplanır)
st.sidebar.header("Ön İşleme Ayarları")
st.sidebar.caption("Temizleme (küçük harf, noktalama ve sayı silme) her zaman yapılır.")
dolgu_cikar = st.sidebar.checkbox("Dolgu kelimelerini çıkar", help="ve, ile, bu, için gibi yaygın kelimeleri siler.")
kok_bul = st.sidebar.checkbox("Kelime köklerini kullan", help="Örn: öğrencilerin -> öğrenci")
if kok_bul and not KOK_BULMA_KULLANILABILIR:
    st.sidebar.warning("snowballstemmer paketi yüklü değil; kök bulma atlandı. Kurmak için: pip install snowballstemmer")
    kok_bul = False

iki_dosya_sekmesi, coklu_sekme = st.tabs(["İki Dosya", "Çoklu Karşılaştırma"])

#---1. SEKME: İKİ DOSYA---
with iki_dosya_sekmesi:
    st.write("İki ödev dosyası yükleyin (TXT, PDF veya DOCX). Sistem metinleri üç farklı yöntemle karşılaştırır.")

    sol, sag = st.columns(2)
    dosya1 = sol.file_uploader("1. Ödev", type=DOSYA_TURLERI)
    dosya2 = sag.file_uploader("2. Ödev", type=DOSYA_TURLERI)

    ham1 = dosya_oku(dosya1) if dosya1 else None
    ham2 = dosya_oku(dosya2) if dosya2 else None
    temiz1 = metin_on_isle(ham1, dolgu_cikar, kok_bul) if ham1 is not None else ""
    temiz2 = metin_on_isle(ham2, dolgu_cikar, kok_bul) if ham2 is not None else ""

    if not (dosya1 and dosya2):
        st.info("Karşılaştırma için iki dosya yükleyin.")
    elif ham1 is None or ham2 is None:
        pass #Okunamayan dosya için hata mesajı dosya_oku içinde gösterildi.
    elif not temiz1 or not temiz2:
        st.error("Dosyalardan en az biri boş veya okunabilir metin içermiyor.")
    else:
        sonuclar = {yontem: hesapla(temiz1, temiz2) for yontem, hesapla in YONTEMLER.items()}

        st.subheader("Benzerlik Sonuçları")
        for sutun, (yontem, oran) in zip(st.columns(3), sonuclar.items()):
            sutun.metric(yontem, f"%{oran:.2f}")
        st.caption("Benzerlik yüzdeleri metinlerin içerik benzerliğini gösterir; tek başına intihal kanıtı değildir.")

        grafik_verisi = pd.DataFrame({"Benzerlik (%)": list(sonuclar.values())}, index=list(sonuclar.keys()))
        st.bar_chart(grafik_verisi)

        kelimeler = ortak_kelimeler(temiz1, temiz2)
        bigramlar = ortak_ngramlar(temiz1, temiz2, n=2)
        sol, sag = st.columns(2)
        sol.metric("Ortak kelime sayısı", len(kelimeler))
        sag.metric("Ortak bigram sayısı", len(bigramlar))
        with st.expander(f"Ortak kelimeler ({len(kelimeler)})"):
            st.write(", ".join(kelimeler) if kelimeler else "Ortak kelime yok.")
        with st.expander(f"Ortak bigramlar ({len(bigramlar)})"):
            st.write(", ".join(bigramlar) if bigramlar else "Ortak bigram yok.")

        with st.expander("Çıkarılan metinleri görüntüle"):
            sol, sag = st.columns(2)
            sol.text_area(dosya1.name, ham1, height=300)
            sag.text_area(dosya2.name, ham2, height=300)

#---2. SEKME: ÇOKLU KARŞILAŞTIRMA---
with coklu_sekme:
    st.write("En az 3 ödev yükleyin. Sistem tüm dosya çiftlerini karşılaştırır ve şüpheli eşleşmeleri listeler.")

    dosyalar = st.file_uploader("Ödevler", type=DOSYA_TURLERI, accept_multiple_files=True)
    sol, sag = st.columns(2)
    yontem = sol.selectbox("Yöntem", list(YONTEMLER), index=1)
    esik = sag.slider("Şüphe eşiği (%)", min_value=0, max_value=100, value=50, step=5)

    metinler = {}
    if len(dosyalar) >= 3:
        for dosya in dosyalar:
            ad = dosya.name
            sayac = 2
            while ad in metinler: #Aynı adlı iki dosya yüklenirse birbirinin üzerine yazmasın
                ad = f"{dosya.name} ({sayac})"
                sayac += 1
            ham = dosya_oku(dosya)
            if ham is None:
                continue
            metinler[ad] = metin_on_isle(ham, dolgu_cikar, kok_bul)
            if not metinler[ad]:
                st.warning(f"{ad} boş veya okunabilir metin içermiyor; benzerlik oranları %0 çıkacaktır.")

    if len(dosyalar) < 3:
        st.info(f"Çoklu karşılaştırma için en az 3 dosya yükleyin (şu an: {len(dosyalar)}).")
    elif len(metinler) < 3:
        st.error("Okunabilen dosya sayısı 3'ün altında kaldı.")
    else:
        matris = benzerlik_matrisi(metinler, yontem)
        supheliler = supheli_eslesmeler(matris, esik)

        st.subheader(f"Benzerlik Matrisi ({yontem})")
        st.dataframe(matris.round(2), width="stretch")
        st.altair_chart(isi_haritasi(matris))

        st.subheader(f"Şüpheli eşleşmeler (≥ %{esik})")
        if supheliler.empty:
            st.success("Eşiği aşan dosya çifti yok.")
        else:
            st.dataframe(supheliler, hide_index=True, width="stretch")

        sol, sag = st.columns(2)
        sol.download_button("Benzerlik matrisini indir (CSV)", csv_baytlari(matris.round(2), index=True),
                            file_name="benzerlik_matrisi.csv", mime="text/csv")
        sag.download_button("Şüpheli eşleşmeleri indir (CSV)", csv_baytlari(supheliler),
                            file_name="supheli_eslesmeler.csv", mime="text/csv")

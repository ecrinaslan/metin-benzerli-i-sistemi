# İntihal Tespit Sistemi (Plagiarism Checker)

Bir metin benzerliği (intihal/plagiarism) sistemi kurarken verinin alınmasından, işlenmesine ve yapay zeka modelleriyle karşılaştırılmasına kadar belli bir boru hattı (pipeline) kurmamız gerekir. Bu projede adım adım aşağıdaki geliştirme süreci izlenecektir:

## 1. İhtiyaç Analizi ve Kapsam
Öncelikle sistemin çalışma sınırları belirlenmiştir:
* **Dosya Formatları:** `.txt`, `.docx` (Word) ve `.pdf` formatındaki dosyalar desteklenmektedir.
* **Dil:** Sistem Türkçe metinleri analiz etmek üzere kurgulanacaktır.
* **Karşılaştırma Havuzu:** Sisteme yüklenen ödevler, veritabanındaki diğer öğrenci ödevleriyle kendi aralarında kıyaslanacaktır.

## 2. Metin Ön İşleme (Text Preprocessing)
Sisteme yüklenen öğrenci metinlerinin bilgisayarın anlayabileceği formata getirilmesi (temizlenmesi) aşamasıdır:
* Noktalama işaretlerinin ve sayıların temizlenmesi.
* Büyük/küçük harf duyarlılığını kaldırmak için metnin tamamen küçük harfe dönüştürülmesi.
* **Stop-words (Dolgu kelimeleri) Atımı:** "ve, veya, ile, ama, ki" gibi metnin ana anlamına doğrudan katkısı olmayan kelimelerin çıkarılması.
* **Kök Bulma (Lemmatization/Stemming):** Türkçe sondan eklemeli bir dil olduğu için kelimelerin köklerine ayrılması (Örn: "gidiyorum" -> "git").

## 3. Yöntem ve Algoritma Aşamaları
Benzerliği matematiksel olarak ölçmek için basitten karmaşığa şu algoritmalar test edilecektir:
* **Seviye 1 (Sözcüksel Benzerlik):** Sadece kelimelerin birebir aynı olup olmadığını kontrol eden Jaccard Benzerliği veya Levenshtein Mesafesi.
* **Seviye 2 (Vektörel Benzerlik - TF-IDF):** Metinlerin TF-IDF yöntemiyle vektörlere çevrilip, aralarındaki Kosinüs Benzerliğinin (Cosine Similarity) hesaplanması.
* **Seviye 3 (Anlamsal Benzerlik):** Cümlelerin yerini değiştirerek veya eş anlamlı kelimeler kullanarak yapılan hileleri tespit etmek için NLP (Doğal Dil İşleme) modellerinin kullanılması.

## 4. Sistem Mimarisi
* **Backend (Arka Uç):** Proje **Python** programlama dili ile geliştirilecektir. 
* **Veritabanı:** Metin vektörlerinin hızlıca karşılaştırılması ve saklanması için uygun bir yapı kullanılacaktır.

## 5. Kurulum ve Çalıştırma

```bash
# 1. Sanal ortam oluşturup etkinleştirin
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 2. Gerekli paketleri kurun
pip install -r requirements.txt

# 3. Uygulamayı başlatın (tarayıcıda http://localhost:8501 açılır)
streamlit run app.py

# 4. Otomatik testleri çalıştırın
pytest

# 5. Rapor tablosunu üretin (sonuclar/hafta5_sonuclar.csv)
python Proje_Adimlari/10_hafta5_test_sonuclari.py
```

### Proje yapısı
* `app.py` – Streamlit arayüzü ("İki Dosya" ve "Çoklu Karşılaştırma" sekmeleri)
* `benzerlik.py` – Tüm hesaplama fonksiyonları (metin çıkarma, temizleme, ön işleme, Jaccard, TF-IDF, n-gram, benzerlik matrisi)
* `turkce_dolgu_kelimeleri.txt` – Türkçe dolgu kelimeleri listesi
* `tests/` – pytest testleri
* `Odevler/` – Test senaryosu metinleri (ayrıntılar `Odevler/README.md` içinde)
* `Proje_Adimlari/` – Her haftanın ara adım dosyaları
* `araclar/ornek_dosyalari_uret.py` – Örnek ödevin DOCX ve PDF kopyalarını üretir

## 6. 5. Haftada Eklenen Özellikler
* **Türkçe büyük/küçük harf düzeltmesi:** `turkce_kucuk_harf` fonksiyonu "İ → i" ve "I → ı" dönüşümünü doğru yapıyor. Türkçe tırnak ve kesme işaretleri (’ ‘ “ ” « » … – —), sayılar ve şapkalı harfler (â, î, û) de temizleniyor.
* **Modüler yapı:** Hesaplamalar `benzerlik.py` modülüne taşındı; `app.py` sadece arayüzü içeriyor. Paketler `requirements.txt` dosyasında.
* **Türkçe ön işleme:** Dolgu kelimelerini (stop-words) çıkarma ve Snowball Türkçe kök bulucuyla kök bulma. Kenar çubuğundaki onay kutularıyla açılıp kapatılabiliyor.
* **Karşılaştırma havuzu:** "Çoklu Karşılaştırma" sekmesinde 3 veya daha fazla dosya yüklenip tüm çiftler için benzerlik matrisi (tablo + ısı haritası), eşik değerine göre şüpheli eşleşmeler listesi ve CSV indirme.
* **Test senaryoları:** `Odevler/` altında birebir kopya, kısmi kopya, eş anlamlı değişiklik, cümle sırası değişikliği, farklı konu, aynı konuda özgün ödev ve Türkçe büyük harf senaryoları (TXT, DOCX ve PDF).
* **Otomatik testler:** `tests/test_benzerlik.py` içinde pytest testleri.
* **Sonuç tablosu:** `Proje_Adimlari/10_hafta5_test_sonuclari.py` üç ön işleme ayarında beş yöntemin sonuçlarını üretiyor.

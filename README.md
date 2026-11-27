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

# 6. Anlamsal yöntemin karşılaştırma tablosunu üretin (sonuclar/anlamsal_sonuclar.csv)
python Proje_Adimlari/11_anlamsal_benzerlik.py
```

> **Not:** Anlamsal benzerlik modeli (`paraphrase-multilingual-MiniLM-L12-v2`, yaklaşık 470 MB) ilk kullanımda internetten bir kez indirilir ve sonra bilgisayarda önbellekte tutulur. İlk karşılaştırma bu yüzden birkaç dakika sürebilir. Model indirilmemişse ilgili testler otomatik olarak atlanır.

### Proje yapısı
* `app.py` – Streamlit arayüzü ("İki Dosya", "Çoklu Karşılaştırma" ve "Ödev Arşivi" sekmeleri)
* `benzerlik.py` – Tüm hesaplama fonksiyonları (metin çıkarma, temizleme, ön işleme, bölümlere ayırma, Jaccard, TF-IDF, n-gram, anlamsal benzerlik, benzerlik matrisi)
* `arsiv.py` – Ödev arşivi için SQLite işlemleri (ekleme, listeleme, seçerek getirme, silme)
* `odev_arsivi.db` – Uygulama ilk çalıştığında otomatik oluşturulan arşiv veritabanı (git'e eklenmez)
* `turkce_dolgu_kelimeleri.txt` – Türkçe dolgu kelimeleri listesi
* `tests/` – pytest testleri (`test_benzerlik.py`, `test_bolumler.py`, `test_arsiv.py`, `test_anlamsal.py`)
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

## 7. Sonraki Haftalarda Eklenen Özellikler
* **Ödev Arşivi:** "Ödev Arşivi" sekmesinden yüklenen ödevler SQLite veritabanına (`odev_arsivi.db`) kaydedilir. Aynı içerikteki dosya SHA-256 özetiyle tanınır ve ikinci kez eklenmez. Yeni ödev, arşivden seçilen ödevlerle seçilen yöntemle karşılaştırılır; arşivdeki kayıtlar listelenip silinebilir. Veritabanı için ek kurulum gerekmez (Python'un `sqlite3` modülü kullanılır).
* **Bölüm Bazlı Analiz:** "İki Dosya" sekmesinde belgeler başlıklarına göre (Giriş, Yöntem, Bulgular, Sonuç, Kaynakça vb.) bölümlere ayrılır. Hem numaralı ("1. GİRİŞ") hem numarasız ("Giriş") başlıklar tanınır ve iki belgede de bulunan aynı başlıklı bölümler tüm yöntemlerle ayrı ayrı karşılaştırılır; sonuçlar tablo, grafik ve CSV olarak sunulur. Başlık bulunamazsa belge tek bölüm olarak değerlendirilir.
* **Ek testler:** `tests/test_bolumler.py` bölümlere ayırma ve başlık normalizasyonunu, `tests/test_arsiv.py` arşiv işlemlerini test eder. Arşiv testleri gerçek veritabanını değiştirmemek için geçici bir veritabanı kullanır.
* **Seviye 3 – Anlamsal Benzerlik:** `sentence-transformers` kütüphanesiyle Türkçeyi destekleyen çok dilli `paraphrase-multilingual-MiniLM-L12-v2` modeli kullanılır. Model metin parçalarını anlamlarını temsil eden vektörlere çevirir; bu sayede kelimeler eş anlamlılarıyla değiştirilse bile benzerlik yakalanır. Model en fazla 128 token okuyabildiği için metinler ~80 kelimelik parçalara bölünür; her parça diğer metindeki en benzer parçayla eşleştirilir ve iki yönün ortalaması alınır. Yöntem tüm sekmelerde "Anlamsal (Çok Dilli Model)" adıyla seçilebilir.

### Anlamsal yöntemin sonuçları (01_orijinal.txt ile, %)

| Senaryo | Jaccard | TF-IDF | Bigram | Anlamsal |
|---|---|---|---|---|
| Birebir kopya | 97.68 | 99.13 | 98.35 | 99.64 |
| Kısmi kopya | 42.15 | 69.34 | 55.44 | 79.11 |
| **Eş anlamlı değişiklik** | 10.39 | 45.75 | 8.01 | **83.90** |
| Cümle sırası değişik | 98.45 | 99.50 | 92.88 | 80.74 |
| Farklı konu | 6.37 | 28.35 | 1.19 | 24.10 |
| Aynı konu, özgün | 9.11 | 42.15 | 5.28 | 77.09 |
| Türkçe büyük harf | 98.45 | 99.50 | 99.18 | 99.14 |

**Yorum:** Anlamsal yöntem, sözcüksel yöntemlerin kaçırdığı eş anlamlı değişikliği açıkça yakalar (%84; Bigram yalnızca %8). Buna karşılık aynı konuda özgün yazılmış ödeve de yüksek puan verir (%77), çünkü konu benzerliğini de anlam benzerliği olarak görür. Cümle sırası değiştirildiğinde ise parçalar kaydığı için puanı sözcüksel yöntemlerden düşüktür. Bu yüzden yöntemler birbirini tamamlar: **sözcüksel yöntemler düşük ama anlamsal yöntem yüksekse** eş anlamlı kelimelerle yapılmış bir intihal olasılığı vardır; anlamsal sonuç tek başına intihal kanıtı olarak yorumlanmamalıdır.

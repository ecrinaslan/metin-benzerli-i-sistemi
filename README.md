# İntihal Tespit Sistemi (Plagiarism Checker)

Bir metin benzerliği (intihal/plagiarism) sistemi kurarken verinin alınmasından, işlenmesine ve yapay zeka modelleriyle karşılaştırılmasına kadar belli bir boru hattı (pipeline) kurmamız gerekir. Bu projede adım adım aşağıdaki geliştirme süreci izlenecektir:

## 1. İhtiyaç Analizi ve Kapsam
Öncelikle sistemin çalışma sınırları belirlenmiştir:
* **Dosya Formatları:** Başlangıç için sadece `.txt` ve `.docx` (Word) formatındaki dosyalar desteklenecektir.
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
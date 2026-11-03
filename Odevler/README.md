# Test Ödevleri

Bu klasördeki metinler sistemi farklı intihal senaryolarıyla denemek için hazırlandı. 06 numaralı dosya hariç hepsinin konusu **"Yapay Zekânın Eğitimdeki Rolü"**dür. Her metin 300–500 kelime uzunluğundadır.

| Dosya | Senaryo | Açıklama |
|---|---|---|
| `01_orijinal.txt` | Kaynak ödev | Diğer bütün dosyaların karşılaştırıldığı özgün metin. |
| `02_birebir_kopya.txt` | Birebir kopya | 01'in aynısı; sadece başlık ve öğrenci adı değiştirilmiş. |
| `03_kismi_kopya.txt` | Kısmi kopya | 6 paragraftan 3'ü (1., 2. ve 5.) 01'den aynen alınmış, diğer 3'ü yeni yazılmış. |
| `04_esanlamli_degisiklik.txt` | Eş anlamlı değişiklik | 01'in içeriği aynı; kelimeler eş anlamlılarıyla değiştirilmiş (öğrenci → talebe, eğitim → öğretim vb.) ve cümleler yeniden kurulmuş. |
| `05_cumle_sirasi_degisik.txt` | Cümle sırası değişik | 01'deki 25 cümlenin hepsi harfi harfine aynı, ama cümleler karıştırılıp yeni paragraflara dağıtılmış. |
| `06_farkli_konu.txt` | Farklı konu | "İklim Değişikliğinin Tarıma Etkileri" konulu, tamamen ilgisiz bir ödev. |
| `07_ayni_konu_ozgun.txt` | Aynı konu, özgün | Aynı konuda, 01'den bağımsız olarak yazılmış özgün bir ödev. |
| `08_buyuk_harf_turkce.txt` | Türkçe büyük harf | 01'in paragrafları; İ, I, Ş, Ğ, Ü, Ö, Ç içeren kelimelerin çoğu BÜYÜK HARFLE yazılmış. `lower()` hatasının düzeltildiğini göstermek için kullanılır. |
| `01_orijinal.docx` | Dosya biçimi testi | 01'in Word kopyası (DOCX okumayı test eder). |
| `01_orijinal.pdf` | Dosya biçimi testi | 01'in PDF kopyası (PDF okumayı test eder). |

DOCX ve PDF dosyaları `python araclar/ornek_dosyalari_uret.py` komutuyla `01_orijinal.txt` dosyasından yeniden üretilebilir.

> Not: Bu klasördeki `main.py` eski `odev1.txt` / `odev2.txt` dosyalarını okuyan ilk deneme dosyasıdır ve artık kullanılmamaktadır.

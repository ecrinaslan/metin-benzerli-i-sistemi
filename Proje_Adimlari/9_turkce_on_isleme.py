import string
from pathlib import Path

import snowballstemmer

#Dolgu kelimeleri listesi proje kök dizinindeki dosyada duruyor.
DOLGU_DOSYASI = Path(__file__).resolve().parent.parent / "turkce_dolgu_kelimeleri.txt"

ornek_metin = ("YAPAY ZEKÂ, İSTANBUL'daki okullarda öğrencilerin ve öğretmenlerin "
               "IŞIK hızıyla bilgiye ulaşmasını sağlıyor. Bu teknolojiler eğitimde çok önemli bir yer tutuyor.")

#1_Temizleme: Türkçe küçük harf + noktalama ve sayıları silme
def turkce_kucuk_harf(metin):
    #lower() "İ" harfini "i̇", "I" harfini "i" yaptığı için önce bu iki harfi elle çeviriyoruz.
    return metin.replace("I", "ı").replace("İ", "i").lower()

def metin_temizle(metin):
    metin = turkce_kucuk_harf(metin).translate(str.maketrans("âîû", "aiu"))
    metin = metin.replace("'", "").replace("’", "")
    for isaret in string.punctuation + "“”«»…–—" + string.digits:
        metin = metin.replace(isaret, " ")
    return " ".join(metin.split())

#2_Dolgu kelimelerini çıkarma
def dolgu_kelimelerini_oku():
    satirlar = DOLGU_DOSYASI.read_text(encoding="utf-8").splitlines()
    return {satir.strip() for satir in satirlar if satir.strip() and not satir.startswith("#")}

def dolgu_kelimelerini_cikar(metin, dolgu_kelimeleri):
    return " ".join(kelime for kelime in metin.split() if kelime not in dolgu_kelimeleri)

#3_Kök bulma (Snowball Türkçe kök bulucu)
kok_bulucu = snowballstemmer.stemmer("turkish")

def kokleri_bul(metin):
    return " ".join(kok_bulucu.stemWords(metin.split()))

#İşlemleri sırayla çalıştırıyoruz
temiz = metin_temizle(ornek_metin)
dolgusuz = dolgu_kelimelerini_cikar(temiz, dolgu_kelimelerini_oku())
kokler = kokleri_bul(dolgusuz)

print("---Ham Metin---")
print(ornek_metin)
print("\n---1. Temizlenmiş Metin---")
print(temiz)
print("\n---2. Dolgu Kelimeleri Çıkarılmış Metin---")
print(dolgusuz)
print("\n---3. Kökleri Bulunmuş Metin---")
print(kokler)

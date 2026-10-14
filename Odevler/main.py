import string

#1_Veri_Alma(Dosya okuma)
dosya1_yolu="odevler/odev1.txt"
dosya2_yolu="odevler/odev2.txt"

def metin_oku(dosya_yolu):
    with open(dosya_yolu, "r", encoding="utf-8") as dosya:
        return dosya.read() 

#2_Metin Ön İşleme
def metin_temizle(metin):
    metin=metin.lower() #Tüm harfleri küçük harfe çeviriyoruz.
    for isaret in string.punctuation: #Noktalama işaretlerini temizliyoruz.
        metin=metin.replace(isaret,"")
    return metin

#3_Algoritma_Benzerlik_Hesaplama
def jaccard_benzerliği(metin1, metin2):
    #Metinleri kelimelere ayırıyoruz.
    kelimeler1=set(metin1.split())
    kelimeler2=set(metin2.split())
    
    #Kelime listelerini matematiksel kümeye (Set) çeviriyoruz.
    kume1=set(kelimeler1)
    kume2=set(kelimeler2)

    #İki kümenin kesişimi (Ortak Kelimeler)
    ortak_kelimeler=kume1.intersection(kume2)

    #İki kümenin birleşimi (Toplam benzersiz Kelimeler)
    toplam_kelimeler=kume1.union(kume2)

    #Formül= (Ortak kelime sayısı)/(Toplam benzersiz kelime sayısı)*100
    benzerlik_orani=(len(ortak_kelimeler)/len(toplam_kelimeler))*100
    return benzerlik_orani

#---SİSTEMİ ÇALIŞTIRMA BÖLÜMÜ---
# #1_OKUMA
ham1= metin_oku(dosya1_yolu)
ham2= metin_oku(dosya2_yolu)

#2_TEMİZLEME
temiz1= metin_temizle(ham1)
temiz2= metin_temizle(ham2)

#3_BENZERLİK HESAPLAMA
sonuc= jaccard_benzerliği(temiz1, temiz2)

#4_SONUÇLARI EKRANA YAZDIRMA
print(f"1. Seviye Intihal Oranı: %{sonuc:.2f}")
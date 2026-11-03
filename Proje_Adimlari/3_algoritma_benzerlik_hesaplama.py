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

with open("Odevler/01_orijinal.txt", "r", encoding="utf-8") as f1:
    metin1 = f1.read()

with open("Odevler/03_kismi_kopya.txt", "r", encoding="utf-8") as f2:
    metin2 = f2.read()

sonuc = jaccard_benzerliği(metin1, metin2)
print(f"Ödevler Arasındaki Benzerlik Oranı: %{sonuc:.2f}")
import os

#Dosyalarımızın bilgisayardaki yollarını tanımlıyoruz.
dosya1_yolu="odevler/odev1.txt"
dosya2_yolu="odevler/odev2.txt"

#Dosyayı okuyup içindeki metni döndüren bir fonksiyon yazıyoruz.
def metin_oku(dosya_yolu):
    #Pythondaki "with open " yapısı, okuma bitince dosyayı otomatik kapatır (bellek dostudur)
    with open(dosya_yolu, "r", encoding="utf-8") as dosya:
        return dosya.read()

#Fonksiyorunumuzu kullanarak ödevleri sistemin hafızasına alıyoruz.
metin1= metin_oku(dosya1_yolu)
metin2= metin_oku(dosya2_yolu)

#Okuduğumuz verileri kontrol amaçlı ekrana yazdırıyoruz.
print("---1. Öğrencinin ödevi---")
print(metin1)
print("---2. Öğrencinin ödevi---")
print(metin2)
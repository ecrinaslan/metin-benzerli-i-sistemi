import string
#Dosya okuma 
dosya1_yolu="odevler/odev1.txt"
dosya2_yolu="odevler/odev2.txt"

def metin_oku(dosya_yolu):
    with open(dosya_yolu, "r", encoding="utf-8") as dosya:
        return dosya.read() 

def metin_temizle(metin):
    metin=metin.lower() #Tüm harfleri küçük harfe çeviriyoruz.
    for isaret in string.punctuation: #Noktalama işaretlerini temizliyoruz.
        metin=metin.replace(isaret,"")
    return metin

#İşlemleri çalıştırıyoruz
ham1= metin_oku(dosya1_yolu)
ham2= metin_oku(dosya2_yolu)

temiz1= metin_temizle(ham1)
temiz2= metin_temizle(ham2)

print("---1. Ödevin Temiz Hali---")
print(temiz1)
print("\n---2. Ödevin Temiz Hali---")
print(temiz2)

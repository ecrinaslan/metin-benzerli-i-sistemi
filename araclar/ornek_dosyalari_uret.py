"""Odevler/01_orijinal.txt dosyasının .docx ve .pdf kopyalarını üretir.

Çalıştırma (proje kök dizininden):  python araclar/ornek_dosyalari_uret.py
PDF için reportlab ve Türkçe karakterleri (ğ, ş, ı, İ) içeren bir TrueType yazı tipi gerekir.
"""
from pathlib import Path

from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ODEVLER = Path(__file__).resolve().parent.parent / "Odevler"
KAYNAK = ODEVLER / "01_orijinal.txt"

#Türkçe karakterleri doğru gösteren yazı tipleri (bulunan ilk dosya kullanılır)
YAZI_TIPI_ADAYLARI = [
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/Library/Fonts/Arial.ttf"),
]


def bloklari_oku():
    #İlk satır başlık, ikinci satır öğrenci adı, sonrası boş satırla ayrılmış paragraflar.
    bloklar = KAYNAK.read_text(encoding="utf-8").strip().split("\n\n")
    baslik, ogrenci = bloklar[0].split("\n")
    return baslik, ogrenci, bloklar[1:]


def docx_uret(baslik, ogrenci, paragraflar):
    belge = Document()
    belge.add_heading(baslik, level=1)
    belge.add_paragraph(ogrenci)
    for paragraf in paragraflar:
        belge.add_paragraph(paragraf)
    belge.save(ODEVLER / "01_orijinal.docx")


def pdf_uret(baslik, ogrenci, paragraflar):
    yazi_tipi = next((yol for yol in YAZI_TIPI_ADAYLARI if yol.exists()), None)
    if yazi_tipi is None:
        raise SystemExit("Türkçe karakter destekli bir .ttf yazı tipi bulunamadı; YAZI_TIPI_ADAYLARI listesine ekleyin.")
    pdfmetrics.registerFont(TTFont("TurkceYazi", str(yazi_tipi)))

    govde = ParagraphStyle("govde", fontName="TurkceYazi", fontSize=11, leading=16, spaceAfter=8)
    baslik_stili = ParagraphStyle("baslik", parent=govde, fontSize=16, leading=22)
    icerik = [Paragraph(baslik, baslik_stili), Paragraph(ogrenci, govde), Spacer(1, 0.4 * cm)]
    icerik += [Paragraph(paragraf, govde) for paragraf in paragraflar]

    SimpleDocTemplate(str(ODEVLER / "01_orijinal.pdf"), pagesize=A4, title=baslik,
                      leftMargin=2.5 * cm, rightMargin=2.5 * cm).build(icerik)


if __name__ == "__main__":
    baslik, ogrenci, paragraflar = bloklari_oku()
    docx_uret(baslik, ogrenci, paragraflar)
    pdf_uret(baslik, ogrenci, paragraflar)
    print("01_orijinal.docx ve 01_orijinal.pdf oluşturuldu.")

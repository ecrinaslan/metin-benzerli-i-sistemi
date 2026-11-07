"""Ödev arşivi için SQLite işlemleri."""
import hashlib
import sqlite3
from pathlib import Path

VERITABANI = Path(__file__).with_name("odev_arsivi.db")


def baglanti_ac():
    conn = sqlite3.connect(VERITABANI)
    conn.row_factory = sqlite3.Row
    return conn


def arsiv_tablosunu_hazirla():
    with baglanti_ac() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS odevler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dosya_adi TEXT NOT NULL,
                dosya_turu TEXT NOT NULL,
                metin TEXT NOT NULL,
                dosya_hash TEXT NOT NULL UNIQUE,
                yuklenme_tarihi TEXT NOT NULL DEFAULT
                    (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
            )
        """)
        conn.commit()


def dosya_ozeti(icerik):
    return hashlib.sha256(icerik).hexdigest()


def arsive_ekle(dosya_adi, metin, icerik):
    """Dosyayı arşive ekler. (kayit_id, yeni_eklendi_mi) döndürür."""
    uzanti = Path(dosya_adi).suffix.lower().lstrip(".")
    ozet = dosya_ozeti(icerik)

    with baglanti_ac() as conn:
        mevcut = conn.execute(
            "SELECT id FROM odevler WHERE dosya_hash = ?", (ozet,)
        ).fetchone()

        if mevcut:
            return mevcut["id"], False

        imlec = conn.execute(
            """INSERT INTO odevler
               (dosya_adi, dosya_turu, metin, dosya_hash)
               VALUES (?, ?, ?, ?)""",
            (dosya_adi, uzanti, metin, ozet),
        )
        conn.commit()
        return imlec.lastrowid, True


def arsiv_listesi():
    with baglanti_ac() as conn:
        satirlar = conn.execute(
            """SELECT id, dosya_adi, dosya_turu, yuklenme_tarihi
               FROM odevler ORDER BY id DESC"""
        ).fetchall()
    return [dict(satir) for satir in satirlar]


def arsiv_metinlerini_getir(kayit_idleri=None, haric_id=None):
    """Seçilen arşiv kayıtlarının metinlerini getirir.

    kayit_idleri=None ise tüm kayıtları getirir.
    Boş liste verilirse hiçbir kayıt getirmez.
    haric_id verilirse o kayıt sonuçlardan çıkarılır.
    """
    sorgu = "SELECT id, dosya_adi, metin FROM odevler"
    kosullar = []
    parametreler = []

    if kayit_idleri is not None:
        kayit_idleri = list(kayit_idleri)
        if not kayit_idleri:
            return []

        yer_tutucular = ",".join("?" for _ in kayit_idleri)
        kosullar.append(f"id IN ({yer_tutucular})")
        parametreler.extend(kayit_idleri)

    if haric_id is not None:
        kosullar.append("id != ?")
        parametreler.append(haric_id)

    if kosullar:
        sorgu += " WHERE " + " AND ".join(kosullar)

    sorgu += " ORDER BY id"

    with baglanti_ac() as conn:
        satirlar = conn.execute(sorgu, parametreler).fetchall()

    return [dict(satir) for satir in satirlar]


def arsivden_sil(kayit_id):
    with baglanti_ac() as conn:
        conn.execute("DELETE FROM odevler WHERE id = ?", (kayit_id,))
        conn.commit()

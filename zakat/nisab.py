"""Peringatan kemas kini nisab — setiap tiga bulan, mula Januari.

Nisab berubah ikut harga emas, dan ia menentukan sama ada zakat wajib
dibayar langsung. Kalau nilai dalam app terlalu tinggi, app akan berkata
"tak cukup nisab — RM 0.00" sedangkan zakat sebenarnya wajib. Itu bukan
sekadar angka salah — ia boleh menyebabkan seseorang terlepas membayar.

Sebab itu app menyimpan tarikh nisab kali terakhir dikemas kini, dan
mengingatkan pengguna apabila suku baharu bermula:

    Januari · April · Julai · Oktober

Nilai lalai ialah RM 34,000 — sekadar tempat letak, bukan nisab sebenar.
"""

from datetime import date

# Bulan pertama setiap suku.
BULAN_SUKU = (1, 4, 7, 10)

# Tahun paling awal yang app uruskan. Nisab berubah setiap tahun (ia ikut
# harga emas), jadi kiraan qadha mesti menilai setiap tahun dengan nisab
# tahun itu — bukan dengan nisab hari ini. Nama ini milik domain, sebab itu
# ia di sini dan bukan dalam store.py (yang hanya tahu baca/tulis fail).
TAHUN_MULA = 2015


def suku_terkini(hari_ini=None):
    """Tarikh mula suku yang sedang berjalan.

    Pada 17 September 2026, ini pulang 1 Julai 2026 — sebab suku Julai
    bermula 1 Julai dan suku Oktober belum lagi masuk.
    """
    h = hari_ini or date.today()
    bulan = max(b for b in BULAN_SUKU if b <= h.month)
    return date(h.year, bulan, 1)


def nama_suku(hari_ini=None):
    bulan = suku_terkini(hari_ini).month
    return {1: "Januari", 4: "April", 7: "Julai", 10: "Oktober"}[bulan]


def baca_tarikh(cfg):
    """Tarikh nisab dikemas kini, atau None kalau tiada / tak sah."""
    mentah = (cfg.get("nisab_dikemas") or "").strip()
    try:
        return date.fromisoformat(mentah)
    except ValueError:
        return None


def perlu_kemas(cfg, hari_ini=None):
    """Pulang (perlu, tarikh_terakhir, suku_sekarang).

    `perlu` jadi True kalau nisab belum dikemas kini pada suku ini —
    termasuk kes rekod lama yang langsung tiada tarikh.
    """
    suku = suku_terkini(hari_ini)
    terakhir = baca_tarikh(cfg)
    return (terakhir is None or terakhir < suku), terakhir, suku


def tanda_dikemas(cfg, hari_ini=None):
    """Tandakan nisab sudah dikemas kini — simpan tarikh hari ini."""
    cfg["nisab_dikemas"] = (hari_ini or date.today()).isoformat()
    return cfg


def mesej_ringkas(cfg, hari_ini=None):
    """Satu baris untuk dipaparkan pada skrin. Kosong kalau tak perlu."""
    perlu, terakhir, _ = perlu_kemas(cfg, hari_ini)
    if not perlu:
        return ""
    if terakhir is None:
        return "Nisab belum pernah dikemas kini — sahkan dengan pihak zakat."
    return (f"Nisab kali terakhir dikemas kini "
            f"{terakhir.strftime('%d/%m/%Y')} — dah lebih satu suku.")


# ------------------------------------------------------- nisab ikut tahun

def senarai_tahun(hari_ini=None):
    """Semua tahun yang app uruskan — TAHUN_MULA hingga tahun semasa."""
    h = hari_ini or date.today()
    return list(range(TAHUN_MULA, h.year + 1))


def untuk_tahun(cfg, jadual, tahun, hari_ini=None):
    """Nisab bagi satu tahun tertentu, atau None kalau belum diisi.

    Satu kebenaran bagi SETIAP tahun — bukan dua salinan yang dicermin:

      * Tahun SEMASA dibaca daripada cfg["nisab"]. Itulah nilai yang
        disunting di menu Kadar, dan yang dipakai oleh kiraan harian.
      * Tahun LAIN dibaca daripada jadual tahunan.

    Sync dua hala sengaja tidak dibuat. Ia akan merosakkan [R] reset
    (yang tidak menyentuh jadual tahun), dan menyunting tahun lama boleh
    menandakan nisab_dikemas — memadamkan peringatan suku yang sebenarnya
    masih belum lulus.
    """
    h = hari_ini or date.today()
    if tahun == h.year:
        return cfg.get("nisab")
    return jadual.get(str(tahun))

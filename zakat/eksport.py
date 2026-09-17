"""Eksport semua data ke satu fail teks yang boleh dibaca manusia.

Tujuannya backup. Rekod sejarah menyimpan nama pembayar sebenar, dan
kalau telefon hilang atau app dipasang semula, semuanya hilang. Fail ini
ditulis ke folder utama Termux ($HOME), bukan ke dalam folder app, supaya
ia terselamat walau app dipasang semula.

Sengaja dibaca manusia, bukan JSON mentah — supaya tuan boleh buka dan
sahkan isinya sendiri tanpa alat lain.
"""

import os
import subprocess
from datetime import datetime

from . import cetak, nisab, versi

GARIS = "=" * 62
SUB = "-" * 62

MEDAN_TETAPAN = [
    ("kadar_masihi", "Kadar Masihi", "%"),
    ("kadar_hijrah", "Kadar Hijrah", "%"),
    ("nisab", "Nisab", "RM"),
    ("tolakan_diri", "Tolakan diri", "RM"),
    ("tolakan_isteri", "Tolakan isteri", "RM"),
    ("isteri_maks", "Isteri maksimum", "orang"),
    ("tolakan_anak_a", "Tolakan anak A", "RM"),
    ("tolakan_anak_b", "Tolakan anak B", "RM"),
]


def _duit(nilai):
    """'34000' atau '34000.00' -> 'RM 34,000.00'."""
    try:
        d = float(nilai)
    except (TypeError, ValueError):
        return str(nilai)
    return f"RM {d:,.2f}"


def _baris(label, nilai, lebar=30):
    return f"  {label:<{lebar}}{nilai}"


def _satu_hasil(h):
    """Kiraan satu kaedah, sebagai senarai baris."""
    L = [f"    KAEDAH {h['kaedah']}"]
    L.append(_baris("  Pendapatan kasar", _duit(h.get("pendapatan_kasar", 0))))
    if h.get("sumber_kasar"):
        L.append(f"    (dari {h['sumber_kasar']})")

    for t in h.get("tolakan", []):
        nama = t.get("pendek") or t.get("label", "?")
        L.append(_baris(f"  − {nama}", _duit(t.get("nilai", 0))))

    if h.get("tolakan"):
        L.append(_baris("  Jumlah tolakan", _duit(h.get("jumlah_tolakan", 0))))
        L.append(_baris("  Kena zakat", _duit(h.get("kena_zakat", 0))))

    L.append(_baris("  Nisab", _duit(h.get("nisab", 0))))
    # Ayat neutral dengan sengaja. Rekod lama menyimpan bendera ini
    # mengikut kaedah masing-masing, rekod baharu mengikut pendapatan
    # kasar — jadi ayat yang mendakwa "tidak wajib" akan salah bagi
    # sebahagian rekod lama.
    L.append("    " + ("cukup nisab" if h.get("cukup_nisab")
                       else "TAK cukup nisab"))
    L.append(_baris("  Kadar", f"{h.get('kadar', 0)} %"))
    L.append(_baris("  Zakat setahun", _duit(h.get("zakat_setahun", 0))))
    L.append(_baris("  Zakat sebulan", _duit(h.get("zakat_sebulan", 0))))
    return L


def jana(cfg, ev, rekod, hari_ini=None):
    """Hasilkan teks eksport penuh."""
    kini = hari_ini or datetime.now()
    L = [
        GARIS,
        "  TAKSIRAN ZAKAT PENDAPATAN — EKSPORT DATA",
        f"  Versi app    {versi.penuh()}",
        f"  Dieksport    {kini.strftime('%d/%m/%Y %H:%M')}",
        GARIS,
        "",
        "TETAPAN",
        SUB,
    ]

    for kunci, label, unit in MEDAN_TETAPAN:
        nilai = cfg.get(kunci, "")
        if unit == "RM":
            teks = _duit(nilai)
        elif unit == "%":
            try:
                teks = f"{float(nilai):.3f} %"
            except (TypeError, ValueError):
                teks = str(nilai)
        else:
            teks = f"{nilai} {unit}"
        L.append(_baris(label, teks))

    tarikh_nisab = nisab.baca_tarikh(cfg)
    L.append(_baris(
        "Nisab dikemas kini",
        tarikh_nisab.strftime("%d/%m/%Y") if tarikh_nisab else "(tiada rekod)"))
    L.append(_baris("Gaya output print",
                    cetak.nama_gaya(cfg.get("gaya", cetak.GAYA_LALAI))))
    L.append(_baris("Sumber kemas kini", cfg.get("sumber_kemas", "") or "(kosong)"))
    L.append("")

    L.append("EVENT AKTIF")
    L.append(SUB)
    if ev.get("nama"):
        L.append(f"  {ev['nama']}")
        for label, kunci in (("Tarikh", "tarikh"), ("Tempat", "tempat")):
            if ev.get(kunci):
                L.append(_baris(label, ev[kunci]))
    else:
        L.append("  (tiada event didaftarkan)")
    L.append("")

    L.append(f"SEJARAH KIRAAN — {len(rekod)} rekod")
    L.append(GARIS)
    L.append("")

    if not rekod:
        L.append("  (tiada rekod)")
    for i, r in enumerate(rekod, 1):
        L.append(f"[{i}]  {r.get('tarikh', '?')} {r.get('masa', '')}   "
                 f"{r.get('nama') or '(tanpa nama)'}")
        if r.get("event"):
            tempat = " — ".join(x for x in [r.get("tarikh_event"),
                                            r.get("tempat")] if x)
            L.append(f"    Event: {r['event']}" + (f"  ({tempat})" if tempat else ""))
        if r.get("tahun"):
            L.append(f"    Tahun: {r['tahun']}")
        L.append("")
        for h in r.get("hasil", []):
            L.extend(_satu_hasil(h))
            L.append("")
        L.append(SUB)

    L.append("")
    L.append("Habis. Fail ini mengandungi nama pembayar — simpan dengan selamat.")
    return "\n".join(L)


def laluan_keluar(hari_ini=None):
    """~/taksiran-eksport-YYYYMMDD-HHMM.txt"""
    kini = hari_ini or datetime.now()
    nama = f"taksiran-eksport-{kini.strftime('%Y%m%d-%H%M')}.txt"
    return os.path.join(os.path.expanduser("~"), nama)


def tulis(teks, laluan=None):
    """Tulis fail. Pulang (laluan, ralat) — ralat None kalau berjaya."""
    laluan = laluan or laluan_keluar()
    try:
        with open(laluan, "w", encoding="utf-8") as f:
            f.write(teks)
            if not teks.endswith("\n"):
                f.write("\n")
        return laluan, None
    except OSError as e:
        return laluan, str(e)


def salin_ke_clipboard(teks):
    """Cuba salin ke clipboard Termux. Pulang True kalau berjaya."""
    import shutil

    if not shutil.which("termux-clipboard-set"):
        return False
    try:
        p = subprocess.run(["termux-clipboard-set"],
                           input=teks.encode("utf-8"), timeout=10)
        return p.returncode == 0
    except Exception:  # noqa: BLE001
        return False

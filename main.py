#!/usr/bin/env python3
"""Taksiran Zakat Pendapatan — CLI untuk Termux."""

import os
import sys
import textwrap
import threading
from datetime import date, datetime
from decimal import Decimal

from zakat import (cetak, eksport, kemas, nisab, qadha, readme, store,
                   tandatangan, ui, versi)
from zakat.kira import Hasil, Tolakan, kira_kaedah_a, kira_kaedah_b

LEBAR = 52
DALAM = LEBAR - 4  # lebar teks di dalam kotak

# Hasil semakan kemas kini semasa app dibuka. None = belum selesai.
_KEMAS = None

# Mesej yang bermakna "arkib ini gagal pengesahan", berbanding kegagalan
# rangkaian. Perbezaannya penting pada skrin: kegagalan tandatangan ialah
# keputusan muktamad, jadi memberitahu pengguna "cuba lagi" adalah menyesatkan.
_MESEJ_TANDA = (tandatangan.TIADA, tandatangan.ROSAK, tandatangan.TAK_PADAN)


# ---------------------------------------------------------------- utiliti

def tahun_semasa():
    return date.today().year


def tahun_hijri_anggaran():
    return int((date.today().year - 622) * 33 / 32)


def tarikh_hari_ini():
    return date.today().strftime("%d/%m/%Y")


# ------------------------------------------------------------ input asas

def minta_pendapatan():
    """Pulang (nilai_tahunan, nota_sumber), atau None kalau dibatalkan."""
    print(ui.garis("PENDAPATAN", LEBAR))
    mod = ui.tanya_pilih(
        {"1", "2"},
        "  Input data   [1] Bulanan   [2] Tahunan\n  pilih ▸ ",
    )
    if mod is None:
        return None
    if mod == "1":
        v = ui.tanya_duit("Pendapatan kasar (RM/bulan)")
        if v is None:
            return None
        tahunan, nota = v * 12, f"{ui.rm_pendek(v)} × 12"
    else:
        v = ui.tanya_duit("Pendapatan kasar (RM/tahun)")
        if v is None:
            return None
        tahunan, nota = v, ""
    print(ui.warna(
        f"     └ {nota + ' = ' if nota else ''}{ui.rm(tahunan)} /tahun",
        ui.W.HIJAU,
    ))
    return tahunan, nota


def minta_tahun(cfg):
    """Pulang (label_tahun, kadar), atau None kalau dibatalkan."""
    print()
    print(ui.garis("TAHUN KIRAAN", LEBAR))
    pilih = ui.tanya_pilih(
        {"1", "2"},
        f"  [1] Masihi {cfg['kadar_masihi']:.3f}%    "
        f"[2] Hijrah {cfg['kadar_hijrah']:.3f}%\n  pilih ▸ ",
    )
    if pilih is None:
        return None
    if pilih == "1":
        jenis, kadar, lalai = "Masihi", Decimal(str(cfg["kadar_masihi"])), tahun_semasa()
    else:
        jenis, kadar, lalai = "Hijrah", Decimal(str(cfg["kadar_hijrah"])), tahun_hijri_anggaran()
    thn = ui.tanya_int("Tahun", 1300, 2200, str(lalai))
    if thn is None:
        return None
    return f"{thn} ({jenis})", kadar


# ------------------------------------------------------------------ alir

def alir_kaedah_a(cfg):
    ui.bersih()
    print()
    print(ui.warna("  KAEDAH A — TANPA TOLAKAN", ui.W.TEBAL))
    print()

    pend = minta_pendapatan()
    if pend is None:
        return
    kasar, nota = pend

    thn = minta_tahun(cfg)
    if thn is None:
        return
    label_tahun, kadar = thn

    hasil = kira_kaedah_a(kasar, kadar, Decimal(str(cfg["nisab"])), nota)
    skrin_hasil([hasil], label_tahun)


def minta_tolakan(cfg, lelaki):
    """Kumpul tolakan tahunan. Pulang senarai Tolakan, atau None kalau batal.

    Dipakai oleh kiraan biasa DAN oleh kiraan bundle qadha. Dua salinan
    soal selidik yang sama akan menyimpang — satu ditambah medan baharu,
    satu tertinggal — dan pengguna tak akan nampak bezanya.
    """
    print()
    print(ui.garis("TOLAKAN (tahunan)", LEBAR))
    tolakan = []

    nilai_diri = Decimal(str(cfg["tolakan_diri"]))
    tolakan.append(Tolakan("Diri sendiri", nilai_diri))
    print(f"     Diri sendiri = {ui.rm(nilai_diri)} (tetap)")

    if lelaki:
        maks = int(cfg["isteri_maks"])
        bil = ui.tanya_int(f"Isteri (0-{maks} orang)", 0, maks, "0")
        if bil is None:
            return None
        if bil > 0:
            kadar_i = Decimal(str(cfg["tolakan_isteri"]))
            tolakan.append(Tolakan(
                "Isteri", kadar_i * bil,
                nota=f"{bil} × {kadar_i:,.0f}",
                nota_penuh=f"{bil} orang × {ui.rm_pendek(kadar_i)}",
                pendek=f"Isteri {bil}",
            ))
    else:
        print(ui.warna("     Isteri — tiada tolakan untuk suami", ui.W.MALAP))

    kadar_a = Decimal(str(cfg["tolakan_anak_a"]))
    kadar_b = Decimal(str(cfg["tolakan_anak_b"]))
    pilih_kadar = ui.tanya_pilih(
        {"1", "2"},
        f"  Anak kadar   [1] {ui.rm_pendek(kadar_a)} (lalai)   "
        f"[2] {ui.rm_pendek(kadar_b)}\n  pilih ▸ ",
    )
    if pilih_kadar is None:
        return None
    kadar_anak = kadar_a if pilih_kadar == "1" else kadar_b

    bil_anak = ui.tanya_int("Bilangan anak", 0, 30, "0")
    if bil_anak is None:
        return None
    if bil_anak > 0:
        tolakan.append(Tolakan(
            "Anak", kadar_anak * bil_anak,
            nota=f"{bil_anak} × {kadar_anak:,.0f}",
            nota_penuh=f"{bil_anak} orang × {ui.rm_pendek(kadar_anak)}",
            pendek=f"Anak {bil_anak}",
        ))

    # --- caruman bulanan ---
    print()
    print(ui.garis("CARUMAN (input bulanan)", LEBAR))
    for label in ("KWSP", "Tabung Haji", "ILTAT"):
        v = ui.tanya_duit(f"{label} (RM/bulan)", "0")
        if v is None:
            return None
        tolakan.append(Tolakan(
            label, v * 12,
            nota=f"{v:,.0f} × 12",
            nota_penuh=f"{ui.rm_pendek(v)} × 12",
        ))
    return tolakan


def minta_jantina():
    """Pulang True kalau lelaki, False kalau perempuan, None kalau batal."""
    jantina = ui.tanya_pilih(
        {"1", "2"},
        "  Jantina   [1] Lelaki   [2] Perempuan\n  pilih ▸ ",
    )
    if jantina is None:
        return None
    return jantina == "1"


def alir_kaedah_b(cfg):
    ui.bersih()
    print()
    print(ui.warna("  KAEDAH B — DENGAN TOLAKAN", ui.W.TEBAL))
    print()

    lelaki = minta_jantina()
    if lelaki is None:
        return
    print()

    pend = minta_pendapatan()
    if pend is None:
        return
    kasar, nota = pend

    tolakan = minta_tolakan(cfg, lelaki)
    if tolakan is None:
        return

    thn = minta_tahun(cfg)
    if thn is None:
        return
    label_tahun, kadar = thn
    nisab = Decimal(str(cfg["nisab"]))

    # Nisab dinilai pada pendapatan kasar, bukan pada asas selepas tolakan
    # (lihat zakat/kira.py). Jadi Kaedah B tetap wajib walau asasnya jatuh
    # bawah nisab selepas tolakan.
    hasil_a = kira_kaedah_a(kasar, kadar, nisab, nota)
    hasil_b = kira_kaedah_b(kasar, kadar, nisab, tolakan, nota)
    skrin_hasil([hasil_a, hasil_b], label_tahun)


# --------------------------------------------------------------- paparan

def _baris_hasil(hasil_senarai, label_tahun):
    h0 = hasil_senarai[0]
    L = [
        ui.baris_kv(f"Tahun {label_tahun}", f"Kadar  {h0.kadar:.3f}%", DALAM),
        ui.baris_kv("Nisab", ui.rm(h0.nisab), DALAM),
    ]
    # Satu baris sahaja, dan ia ikut pendapatan kasar. Kalau Kaedah A
    # cukup nisab, tiada nota langsung — walaupun Kaedah B jatuh bawah
    # nisab selepas tolakan.
    L.append("  ✓ cukup nisab" if h0.cukup_nisab
             else "  ✗ pendapatan kasar tak cukup nisab — zakat tidak wajib")
    for h in hasil_senarai:
        tajuk = ("KAEDAH A ─ TANPA TOLAKAN" if h.kaedah == "A"
                 else "KAEDAH B ─ DENGAN TOLAKAN")
        L.append("")
        L.append("── " + tajuk + " " + "─" * max(0, DALAM - len(tajuk) - 4))
        L.append(ui.baris_kv("Pendapatan kasar", ui.rm(h.pendapatan_kasar), DALAM))

        if h.tolakan:
            for t in h.tolakan:
                L.append(ui.baris_kv("  " + t.label_kotak(), ui.rm(t.nilai), DALAM))
            L.append(ui.baris_kv("", "─" * 12, DALAM))
            L.append(ui.baris_kv("  Jumlah tolakan", ui.rm(h.jumlah_tolakan), DALAM))
            L.append(ui.baris_kv("  Kena zakat", ui.rm(h.kena_zakat), DALAM))

        L.append("")
        L.append(ui.baris_kv("  Zakat setahun", ui.rm(h.zakat_setahun), DALAM))
        L.append(ui.baris_kv("  Zakat sebulan", ui.rm(h.zakat_sebulan), DALAM))

    if len(hasil_senarai) > 1:
        L.append("")
        L.append(ui.baris_kv("", f"{'SETAHUN':>15}{'SEBULAN':>16}", DALAM))
        for h in hasil_senarai:
            L.append(ui.baris_kv(
                f"  {h.kaedah}",
                f"{ui.rm(h.zakat_setahun):>15}{ui.rm(h.zakat_sebulan):>16}",
                DALAM,
            ))
    return L


def skrin_hasil(hasil_senarai, label_tahun):
    while True:
        ui.bersih()
        print()
        print(ui.kotak(_baris_hasil(hasil_senarai, label_tahun), LEBAR))
        print()
        pesan_nisab = nisab.mesej_ringkas(store.config())
        if pesan_nisab:
            print(ui.warna("  ⚠ " + pesan_nisab, ui.W.KUNING))
            print(ui.warna("    Betulkan di [7] Kadar & Tolakan.", ui.W.MALAP))
            print()
        print("  [P] Print / Salin    [S] Simpan    [0] Menu")
        pilih = ui.tanya_pilih({"p", "s", "0"}, "\n  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        if pilih == "p":
            skrin_cetak(hasil_senarai, label_tahun)
        else:
            simpan_rekod(hasil_senarai, label_tahun)


def _amaran_nisab_cetak():
    """Amaran terakhir sebelum teks keluar. Pulang False kalau dibatalkan.

    Selepas ini teks dihantar kepada pembayar, dan angka yang salah
    sukar ditarik balik. Dipakai oleh cetakan biasa dan cetakan qadha —
    satu salinan sahaja, supaya kedua-duanya tak menyimpang.
    """
    pesan_nisab = nisab.mesej_ringkas(store.config())
    if not pesan_nisab:
        return True
    print()
    print(ui.warna("  ⚠ " + pesan_nisab, ui.W.KUNING))
    print(ui.warna("    Cetakan ini akan keluar dengan nisab itu.", ui.W.KUNING))
    print()
    print("  [ENTER] teruskan    [0] batal")
    return ui.tanya_pilih({"", "0"}, "  pilih ▸ ") != "0"


def skrin_cetak(hasil_senarai, label_tahun):
    ui.bersih()
    print(ui.garis("PRINT", LEBAR))
    print()
    nama = ui.tanya(
        "Nama pembayar (kosongkan kalau tak perlu)", "", boleh_kosong=True
    )
    if nama is None:
        return
    nama = nama.strip()

    if not _amaran_nisab_cetak():
        return

    teks = cetak.jana(
        hasil_senarai, store.event(), nama, label_tahun,
        tarikh_hari_ini(), gaya=store.config().get("gaya", cetak.GAYA_LALAI),
    )

    # Print terus simpan ke sejarah.
    store.tambah_sejarah(_buat_rekod(hasil_senarai, label_tahun, nama))
    _papar_teks(teks, nota="disimpan ke sejarah")


def _buat_rekod(hasil_senarai, label_tahun, nama=""):
    ev = store.event()
    return {
        "tarikh": tarikh_hari_ini(),
        "masa": datetime.now().strftime("%H:%M"),
        "event": ev.get("nama", ""),
        "tarikh_event": ev.get("tarikh", ""),
        "tempat": ev.get("tempat", ""),
        "nama": nama,
        "tahun": label_tahun,
        "hasil": [h.ringkas() for h in hasil_senarai],
    }


def simpan_rekod(hasil_senarai, label_tahun):
    store.tambah_sejarah(_buat_rekod(hasil_senarai, label_tahun))
    print(ui.warna("  ✓ rekod disimpan", ui.W.HIJAU))
    ui.jeda()


# ----------------------------------------------------------------- qadha

def _bulanan_kepada_tahunan(v, bulanan):
    return v * 12 if bulanan else v


def _tahunan_kepada_input(v, bulanan):
    """Balik ke unit yang ditaip, supaya ENTER mengekalkan nilai lama.

    Darab 12 kemudian bahagi 12 semula adalah tepat dalam Decimal, jadi
    nombor yang dipaparkan semula sentiasa sama dengan yang ditaip.
    """
    return v / 12 if bulanan else v


def _tanya_satu_tahun(b, label):
    """Tanya satu tahun daripada senarai yang sedang dipilih."""
    while True:
        ui.bersih()
        print(ui.garis(label.upper(), LEBAR))
        print()
        print("  " + ", ".join(str(t) for t in b.tahun))
        print()
        t = ui.tanya_int("Tahun (0 = batal)", 0, tahun_semasa(), "")
        if t is None or t == 0:
            return None
        if t not in b.tahun:
            print(ui.warna("  ! tahun itu tiada dalam senarai", ui.W.MERAH))
            ui.jeda("  [ENTER] cuba lagi")
            continue
        return t


def _tahun_julat():
    """Julat tahun berturut, cth. 2018 hingga 2021."""
    ui.bersih()
    print(ui.garis("JULAT TAHUN", LEBAR))
    print()
    semasa = tahun_semasa()
    dari = ui.tanya_int(f"Dari tahun ({nisab.TAHUN_MULA}-{semasa})",
                        nisab.TAHUN_MULA, semasa, str(nisab.TAHUN_MULA))
    if dari is None:
        return None
    # Minimum ditetapkan pada `dari`, jadi "hingga sebelum dari" ditolak
    # oleh tanya_int sendiri — tiada semakan berasingan yang boleh
    # tertinggal.
    hingga = ui.tanya_int(f"Hingga tahun ({dari}-{semasa})",
                          dari, semasa, str(semasa))
    if hingga is None:
        return None
    return list(range(dari, hingga + 1))


def _tahun_manual():
    """Taip tahun satu-satu. Taip tahun yang sudah ada akan membuangnya.

    Toggle ini disengajakan: tanpa jalan keluar, tersilap taip bermakna
    tahun itu tersangkut dalam senarai sehingga app dimulakan semula.
    """
    semasa = tahun_semasa()
    tahun = []
    while True:
        ui.bersih()
        print(ui.garis("PILIH TAHUN — MANUAL", LEBAR))
        print()
        if tahun:
            for b in _balut("Terpilih: "
                            + ", ".join(str(t) for t in sorted(tahun)), DALAM):
                print("  " + b)
        else:
            print(ui.warna("  (belum ada tahun dipilih)", ui.W.MALAP))
        print()
        print(f"  Taip tahun {nisab.TAHUN_MULA}-{semasa} untuk tambah.")
        print(ui.warna("  Taip tahun yang sudah ada untuk membuangnya.",
                       ui.W.MALAP))
        print()

        # ui.tanya, bukan ui.tanya_int: tanya_int memetakan input kosong
        # kepada 0 dan gagal semakan minimum, jadi ia tak boleh
        # menyatakan "ENTER = siap". Gelung sendiri juga membolehkan
        # senarai dilukis semula antara pusingan.
        jawab = ui.tanya("Tahun (ENTER = siap)", "", boleh_kosong=True)
        if jawab is None:
            return None
        if jawab == "":
            return sorted(tahun)
        try:
            t = int(jawab)
        except ValueError:
            print(ui.warna("  ! tahun mesti nombor", ui.W.MERAH))
            ui.jeda("  [ENTER] cuba lagi")
            continue
        if not (nisab.TAHUN_MULA <= t <= semasa):
            print(ui.warna(f"  ! tahun mesti antara {nisab.TAHUN_MULA} "
                           f"dan {semasa}", ui.W.MERAH))
            ui.jeda("  [ENTER] cuba lagi")
            continue
        if t in tahun:
            tahun.remove(t)
        else:
            tahun.append(t)


def pilih_tahun():
    """Tanya tahun mana yang hendak dikira.

    Pulang senarai tahun menaik, [] kalau tiada tahun dipilih, atau None
    kalau dibatalkan sepenuhnya.
    """
    while True:
        ui.bersih()
        print()
        print(ui.warna("  PILIH TAHUN", ui.W.TEBAL))
        print()
        print("  [1]  Julat   — dari tahun berapa hingga tahun berapa")
        print("  [2]  Manual  — taip tahun satu-satu")
        print("  [0]  Kembali")
        print()
        pilih = ui.tanya_pilih({"1", "2", "0"}, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return None
        tahun = _tahun_julat() if pilih == "1" else _tahun_manual()
        if tahun is None:
            continue  # batal dalam submod — balik ke menu ini
        return tahun


def alir_bundle(cfg):
    """Kiraan qadha merentas beberapa tahun sekali gus.

    Susunan soalan: kaedah -> tolakan (B sahaja, sekali) -> kadar ->
    mod input (sekali) -> tahun mana -> isi gaji -> semak -> kira.

    Tolakan dan mod input ditanya sekali di hadapan dengan sengaja.
    Menanyakannya bagi setiap tahun menjadikan dua belas tahun sebagai
    dua belas soal selidik penuh, sedangkan tolakan seseorang jarang
    berubah dari tahun ke tahun.
    """
    ui.bersih()
    print()
    print(ui.warna("  KIRAAN BUNDLE — QADHA ZAKAT", ui.W.TEBAL))
    print()

    pilih = ui.tanya_pilih(
        {"1", "2"},
        "  Kaedah   [1] A — Tanpa Tolakan   [2] B — Dengan Tolakan\n  pilih ▸ ",
    )
    if pilih is None:
        return
    kaedah = "A" if pilih == "1" else "B"

    tolakan = []
    if kaedah == "B":
        lelaki = minta_jantina()
        if lelaki is None:
            return
        tolakan = minta_tolakan(cfg, lelaki)
        if tolakan is None:
            return
        print()
        print(ui.warna("  Tolakan ini dipakai oleh SEMUA tahun. Boleh diubah "
                       "bagi tahun tertentu kemudian.", ui.W.MALAP))

    print()
    print(ui.garis("KADAR", LEBAR))
    pilih = ui.tanya_pilih(
        {"1", "2"},
        f"  [1] Masihi {cfg['kadar_masihi']:.3f}%    "
        f"[2] Hijrah {cfg['kadar_hijrah']:.3f}%\n  pilih ▸ ",
    )
    if pilih is None:
        return
    # Senarai tahun sentiasa Masihi (nisab dikunci ikut tahun Masihi);
    # hanya KADAR yang boleh Masihi atau Hijrah.
    nama_kadar = "Masihi" if pilih == "1" else "Hijrah"
    kadar = Decimal(str(cfg["kadar_masihi"] if pilih == "1"
                        else cfg["kadar_hijrah"]))

    print()
    print(ui.garis("INPUT GAJI", LEBAR))
    pilih = ui.tanya_pilih(
        {"1", "2"},
        "  [1] Bulanan (didarab 12)   [2] Tahunan\n  pilih ▸ ",
    )
    if pilih is None:
        return
    bulanan = pilih == "1"

    tahun = pilih_tahun()
    if tahun is None:
        return
    if not tahun:
        print()
        print(ui.warna("  ! tiada tahun dipilih", ui.W.MERAH))
        ui.jeda()
        return

    b = qadha.Bundle(tahun, kaedah)
    b.tolakan_lalai = tolakan
    skrin_bundle(b, cfg, bulanan, kadar, nama_kadar)


def _ubah_tolakan_tahun(b, cfg):
    """Ubah tolakan bagi satu tahun sahaja."""
    t = _tanya_satu_tahun(b, "Tolakan tahun mana")
    if t is None:
        return

    if b.tolakan_diubah(t):
        ui.bersih()
        print(ui.garis(f"TOLAKAN {t}", LEBAR))
        print()
        print(ui.warna("  Tahun ini sudah ada tolakan sendiri.",
                       ui.W.MALAP))
        print()
        print("  [1] Ubah semula")
        print("  [2] Guna tolakan asal semula")
        print("  [0] Batal")
        print()
        pilih = ui.tanya_pilih({"1", "2", "0"}, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        if pilih == "2":
            b.buang_tolakan_khas(t)
            print()
            print(ui.warna(f"  ✓ {t} kembali guna tolakan asal", ui.W.HIJAU))
            ui.jeda()
            return

    lelaki = minta_jantina()
    if lelaki is None:
        return
    tolakan = minta_tolakan(cfg, lelaki)
    if tolakan is None:
        return
    b.set_tolakan(t, tolakan)
    print()
    print(ui.warna(f"  ✓ tolakan {t} diubah", ui.W.HIJAU))
    ui.jeda()


def _hapus_tahun(b):
    if len(b.tahun) <= 1:
        print()
        print(ui.warna("  ! ini tahun terakhir — tak boleh dihapus",
                       ui.W.MERAH))
        ui.jeda()
        return
    t = _tanya_satu_tahun(b, "Hapus tahun mana")
    if t is None:
        return
    b.hapus(t)
    print()
    print(ui.warna(f"  ✓ {t} dibuang dari kiraan", ui.W.HIJAU))
    ui.jeda()


def skrin_bundle(b, cfg, bulanan, kadar, nama_kadar):
    """Senarai tahun — isi pendapatan kasar, kemudian semak dan kira."""
    while True:
        ui.bersih()
        print()
        print(ui.warna("  KIRAAN BUNDLE — QADHA ZAKAT", ui.W.TEBAL))
        print(ui.warna(
            f"  Kaedah {b.kaedah}   Kadar {nama_kadar}   "
            f"Input {'bulanan' if bulanan else 'tahunan'}", ui.W.MALAP))
        print()

        L = []
        for t in b.tahun:
            tanda = " *" if b.tolakan_diubah(t) else ""
            nilai = b.kasar.get(t)
            if nilai is None:
                kanan = "(belum diisi)"
            elif bulanan:
                # Kedua-dua unit ditunjukkan: yang ditaip, dan yang
                # sebenarnya masuk ke dalam kiraan.
                kanan = (f"{ui.rm_pendek(_tahunan_kepada_input(nilai, True))}"
                         f" × 12 = {ui.rm_pendek(nilai)}")
            else:
                kanan = ui.rm_pendek(nilai)
            L.append(ui.baris_kv(f"{t}{tanda}", kanan, DALAM))
        print(ui.kotak(L, LEBAR))
        print()

        if any(b.tolakan_diubah(t) for t in b.tahun):
            print(ui.warna("  * tolakan tahun ini diubah", ui.W.MALAP))
            print()

        print("  Taip tahun untuk isi   [T] tolakan   [H] hapus   "
              "[K] semak & kira   [0] kembali")
        print()
        sah = {str(t) for t in b.tahun} | {"t", "h", "k", "0"}
        pilih = ui.tanya_pilih(sah, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        if pilih == "t":
            _ubah_tolakan_tahun(b, cfg)
            continue
        if pilih == "h":
            _hapus_tahun(b)
            continue
        if pilih == "k":
            hasil_baris = skrin_semak_bundle(b, cfg, bulanan, kadar, nama_kadar)
            if hasil_baris is None:
                continue
            skrin_hasil_qadha(hasil_baris)
            return

        t = int(pilih)
        lama = b.kasar.get(t)
        unit = "bulan" if bulanan else "tahun"
        lalai = ("" if lama is None
                 else str(_tahunan_kepada_input(lama, bulanan)))
        v = ui.tanya_duit(f"Pendapatan kasar {t} (RM/{unit})", lalai)
        if v is None:
            continue
        b.set_kasar(t, _bulanan_kepada_tahunan(v, bulanan))


def skrin_semak_bundle(b, cfg, bulanan, kadar, nama_kadar):
    """Paparan semak sebelum kiraan dijalankan.

    Pulang [(tahun, Hasil)] kalau pengguna menekan [K], atau None kalau
    dibatalkan.

    Semak ini bukan hiasan. Hasilnya nanti satu jumlah yang besar, dan
    satu angka yang tersalah taip pada satu tahun mudah hilang di dalam
    jadual hasil. Di sini setiap tahun berdiri sendiri.
    """
    while True:
        # Dibaca semula setiap pusingan: skrin nisab boleh mengubahnya.
        jadual = store.jadual_nisab()
        kosong = b.tahun_kosong()
        tanpa_nisab = b.tahun_tanpa_nisab(cfg, jadual)

        ui.bersih()
        print()
        print(ui.warna("  SEMAK SEBELUM KIRA", ui.W.TEBAL))
        print(ui.warna(
            f"  Kaedah {b.kaedah}   Kadar {nama_kadar} ({kadar:.3f}%)   "
            f"Input {'bulanan' if bulanan else 'tahunan'}", ui.W.MALAP))
        print(ui.warna(f"  {len(b.tahun)} tahun dipilih", ui.W.MALAP))
        print()

        L = []
        for t in b.tahun:
            nilai = b.kasar.get(t)
            L.append(ui.baris_kv(
                str(t), "(belum diisi)" if nilai is None else ui.rm(nilai),
                DALAM))
        print(ui.kotak(L, LEBAR))
        print()

        if b.kaedah == "B" and b.tolakan_lalai:
            # Tolakan tidak kelihatan di skrin hasil mahupun di cetakan
            # qadha (kedua-duanya per tahun, bukan per tolakan). Tanpa
            # baris di sini, satu KWSP yang tersalah taip langsung tiada
            # tempat untuk dilihat — sedangkan inilah skrin semaknya.
            TL = [ui.baris_kv("  " + t.label_kotak(), ui.rm(t.nilai), DALAM)
                  for t in b.tolakan_lalai]
            TL.append(ui.baris_kv("  Jumlah tolakan",
                                  ui.rm(b.jumlah_tolakan_lalai()), DALAM))
            print(ui.kotak(TL, LEBAR, tajuk="TOLAKAN SEMUA TAHUN"))
            print()

            khas = [t for t in b.tahun if b.tolakan_diubah(t)]
            if khas:
                print(ui.warna("  ⚠ Tolakan sendiri bagi: "
                               + ", ".join(str(t) for t in khas), ui.W.KUNING))
                for t in khas:
                    print("    " + ui.baris_kv(
                        str(t), ui.rm(b.jumlah_tolakan(t)), DALAM))
                print()

        # Tahun yang dipilih tetapi kosong BUKAN halangan keras — tahun
        # tanpa pendapatan memang sah dikecualikan. Tetapi ia mesti
        # kelihatan, kalau tidak tahun yang tertinggal hilang senyap.
        if kosong:
            print(ui.warna("  ⚠ Belum diisi: "
                           + ", ".join(str(t) for t in kosong), ui.W.KUNING))
            print(ui.warna("    Tahun itu akan dilangkau.", ui.W.MALAP))
            print()

        # Tahun tanpa nisab pula halangan KERAS: melangkaunya bermakna
        # menilai gaji tahun itu dengan nisab tahun lain.
        if tanpa_nisab:
            print(ui.warna("  ✗ Nisab belum diisi bagi: "
                           + ", ".join(str(t) for t in tanpa_nisab), ui.W.MERAH))
            print(ui.warna("    Setiap tahun dinilai dengan nisab tahun itu,",
                           ui.W.MALAP))
            print(ui.warna("    jadi kiraan tidak boleh diteruskan.",
                           ui.W.MALAP))
            print()
            print("  [T] Isi nisab    [0] Kembali")
            print()
            pilih = ui.tanya_pilih({"t", "0"}, "  pilih ▸ ")
            if pilih == "t":
                skrin_nisab_tahun()
                continue
            return None

        print("  [K] Kira    [0] Kembali ke senarai")
        print()
        pilih = ui.tanya_pilih({"k", "0"}, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return None
        hasil_baris = b.kira(cfg, jadual, kadar)
        if not hasil_baris:
            print()
            print(ui.warna("  ! tiada tahun yang boleh dikira", ui.W.MERAH))
            ui.jeda()
            return None
        return hasil_baris


def _baris_hasil_qadha(baris):
    tahun = [t for t, _ in baris]
    h0 = baris[0][1]

    L = [
        ui.baris_kv("Tahun",
                    f"{tahun[0]} – {tahun[-1]}" if len(tahun) > 1
                    else str(tahun[0]), DALAM),
        ui.baris_kv("Kaedah", f"{h0.kaedah}    Kadar {h0.kadar:.3f}%", DALAM),
        ui.baris_kv("Nisab", "ikut tahun masing-masing", DALAM),
        "",
    ]
    for t, h in baris:
        kiri = str(t) if h.cukup_nisab else f"{t}  ✗ bawah nisab"
        # Kaedah B: asas selepas tolakan ditunjukkan, sebab itulah angka
        # yang tolakan itu hasilkan. Tanpa ia, satu tolakan yang tersalah
        # taip langsung tiada kesan yang kelihatan sehingga zakatnya
        # berbeza — dan itu sudah terlambat.
        if h.kaedah == "B" and h.tolakan:
            kanan = f"{ui.rm(h.kena_zakat)} → {ui.rm(h.zakat_setahun)}"
        else:
            kanan = ui.rm(h.zakat_setahun)
        L.append(ui.baris_kv(kiri, kanan, DALAM))
    L.append(ui.baris_kv("", "─" * 12, DALAM))
    L.append(ui.baris_kv("JUMLAH WAJIB", ui.rm(qadha.jumlah(baris)), DALAM))
    if qadha.tahun_tak_cukup(baris):
        L.append(ui.baris_kv("", "✗ dikecualikan dari jumlah", DALAM))
    return L


def _buat_rekod_qadha(baris, nama=""):
    """Rekod sejarah bagi satu kiraan qadha.

    Setiap entri hasil membawa tahunnya sendiri. Hasil.dari_rekod cuma
    membaca kunci yang ia kenal, jadi kunci tambahan ini tidak
    mengganggu apa-apa — tetapi pencetak qadha boleh memasangkan tahun
    dengan hasilnya tanpa tatasusunan selari atau pengiraan semula.
    """
    ev = store.event()
    tahun = [t for t, _ in baris]
    return {
        "tarikh": tarikh_hari_ini(),
        "masa": datetime.now().strftime("%H:%M"),
        "event": ev.get("nama", ""),
        "tarikh_event": ev.get("tarikh", ""),
        "tempat": ev.get("tempat", ""),
        "nama": nama,
        "jenis": "qadha",
        "kaedah": baris[0][1].kaedah,
        "tahun": (f"{tahun[0]} – {tahun[-1]}" if len(tahun) > 1
                  else str(tahun[0])),
        "hasil": [dict(h.ringkas(), tahun=t) for t, h in baris],
    }


def _cetak_qadha(baris):
    ui.bersih()
    print(ui.garis("PRINT QADHA", LEBAR))
    print()
    nama = ui.tanya("Nama pembayar (kosongkan kalau tak perlu)", "",
                    boleh_kosong=True)
    if nama is None:
        return
    nama = nama.strip()

    if not _amaran_nisab_cetak():
        return

    teks = cetak.qadha(baris, store.event(), nama, baris[0][1].kaedah,
                       tarikh_hari_ini())
    store.tambah_sejarah(_buat_rekod_qadha(baris, nama))
    _papar_teks(teks, nota="disimpan ke sejarah")


def skrin_hasil_qadha(baris):
    while True:
        ui.bersih()
        print()
        print(ui.warna("  QADHA ZAKAT — HASIL", ui.W.TEBAL))
        print()
        print(ui.kotak(_baris_hasil_qadha(baris), LEBAR))
        print()
        print("  [P] Print / Salin    [S] Simpan    [0] Menu")
        print()
        pilih = ui.tanya_pilih({"p", "s", "0"}, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        if pilih == "p":
            _cetak_qadha(baris)
        else:
            store.tambah_sejarah(_buat_rekod_qadha(baris))
            print(ui.warna("  ✓ rekod disimpan", ui.W.HIJAU))
            ui.jeda()


def _jumlah_rekod_qadha(rekod):
    """Jumlah wajib bagi satu rekod qadha — untuk senarai sejarah."""
    baris = [(h.get("tahun"), Hasil.dari_rekod(h))
             for h in rekod.get("hasil", [])]
    return qadha.jumlah(baris)


def skrin_cetak_qadha(rekod):
    """Print semula rekod qadha daripada sejarah."""
    ui.bersih()
    print(ui.garis("PRINT REKOD — QADHA", LEBAR))
    print()
    print(f"  {rekod['tarikh']} {rekod.get('masa', '')}   "
          f"{rekod.get('nama') or '(tanpa nama)'}")
    print()

    nama = ui.tanya("Nama pembayar (kosongkan kalau tak perlu)",
                    rekod.get("nama", ""), boleh_kosong=True)
    if nama is None:
        return

    baris = []
    for h in rekod.get("hasil", []):
        try:
            baris.append((int(h.get("tahun", 0)), Hasil.dari_rekod(h)))
        except (TypeError, ValueError):
            continue
    if not baris:
        print(ui.warna("  ✗ rekod ini tiada tahun yang boleh dibaca",
                       ui.W.MERAH))
        ui.jeda()
        return
    baris.sort(key=lambda x: x[0])

    ev = {
        "nama": rekod.get("event", ""),
        "tarikh": rekod.get("tarikh_event", ""),
        "tempat": rekod.get("tempat", ""),
    }
    teks = cetak.qadha(baris, ev, nama.strip(),
                       rekod.get("kaedah") or baris[0][1].kaedah,
                       rekod.get("tarikh", tarikh_hari_ini()))
    _papar_teks(teks)


def menu_qadha(cfg):
    while True:
        ui.bersih()
        print()
        print(ui.warna("  QADHA ZAKAT", ui.W.TEBAL))
        print()
        print("  [1]  Kiraan Bundle")
        print(ui.warna("       Kira zakat tertunggak beberapa tahun sekali gus",
                       ui.W.MALAP))
        print()
        print("  [0]  Kembali")
        print()
        pilih = ui.tanya_pilih({"1", "0"}, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        alir_bundle(cfg)


# ------------------------------------------------------------------ menu

def menu_kira(cfg):
    """Pilih kaedah, kira, cetak."""
    ui.bersih()
    print()
    print(ui.warna("  PILIH KAEDAH KIRAAN", ui.W.TEBAL))
    print()
    print("  [1]  KAEDAH A — Tanpa Tolakan")
    print(ui.warna("       Pendapatan kasar x kadar", ui.W.MALAP))
    print()
    print("  [2]  KAEDAH B — Dengan Tolakan")
    print(ui.warna("       Pendapatan kasar - tolakan, kemudian x kadar", ui.W.MALAP))
    print()
    print("  [0]  Kembali")
    print()
    pilih = ui.tanya_pilih({"1", "2", "0"}, "  pilih ▸ ")
    if pilih is None or pilih == "0":
        return
    if pilih == "1":
        alir_kaedah_a(cfg)
    else:
        alir_kaedah_b(cfg)


def menu_daftar():
    ev = store.event()
    ui.bersih()
    print()
    print(ui.warna("  DAFTAR", ui.W.TEBAL))
    print()

    if ev.get("nama"):
        print(ui.kotak([
            ev["nama"],
            " — ".join(x for x in [ev.get("tarikh"), ev.get("tempat")] if x),
        ], LEBAR, tajuk="EVENT AKTIF"))
    else:
        print(ui.warna("  (tiada event didaftarkan)", ui.W.MALAP))

    print()
    print("  [1]  Daftar / ubah event")
    print("  [2]  Kosongkan event")
    print("  [0]  Kembali")
    print()
    pilih = ui.tanya_pilih({"1", "2", "0"}, "  pilih ▸ ")

    if pilih == "1":
        ui.bersih()
        print(ui.garis("DAFTAR EVENT", LEBAR))
        print()
        nama = ui.tanya("Nama event", ev.get("nama", ""))
        if nama is None:
            return
        tarikh = ui.tanya("Tarikh", ev.get("tarikh", tarikh_hari_ini()))
        if tarikh is None:
            return
        tempat = ui.tanya("Tempat", ev.get("tempat", ""))
        if tempat is None:
            return
        store.simpan_event({
            "nama": nama.strip(),
            "tarikh": tarikh.strip(),
            "tempat": tempat.strip(),
        })
        print()
        print(ui.warna("  ✓ event disimpan", ui.W.HIJAU))
        ui.jeda()
    elif pilih == "2":
        store.simpan_event({})
        print()
        print(ui.warna("  ✓ event dikosongkan", ui.W.HIJAU))
        ui.jeda()


MEDAN = [
    ("kadar_masihi", "Kadar Masihi (%)", "duit"),
    ("kadar_hijrah", "Kadar Hijrah (%)", "duit"),
    ("nisab", "Nisab (RM)", "duit"),
    ("tolakan_diri", "Tolakan diri (RM)", "duit"),
    ("tolakan_isteri", "Tolakan isteri (RM)", "duit"),
    ("isteri_maks", "Isteri maksimum (orang)", "int"),
    ("tolakan_anak_a", "Tolakan anak A (RM)", "duit"),
    ("tolakan_anak_b", "Tolakan anak B (RM)", "duit"),
]


def skrin_nisab_tahun():
    """Senarai nisab ikut tahun — 2015 hingga tahun semasa.

    Tahun semasa bukan sekadar satu baris dalam senarai ini: ia ditulis
    ke cfg["nisab"], sebab itulah nilai yang dipakai oleh kiraan harian
    dan oleh peringatan suku. Tahun-tahun lain masuk ke data/nisab.json.
    Satu kebenaran bagi setiap tahun, tiada cermin antara keduanya.

    Menyunting tahun SEMASA menandakan nisab sudah disahkan semula
    (tuan baru menyemaknya). Menyunting tahun LAMA tidak — peringatan
    suku hanya mengenai nisab semasa, dan menandanya daripada suntingan
    tahun 2015 akan memadamkan peringatan yang masih belum lulus.
    """
    while True:
        cfg = store.config()
        jadual = store.jadual_nisab()
        semasa = tahun_semasa()
        tahun_senarai = nisab.senarai_tahun()

        ui.bersih()
        print()
        print(ui.warna("  NISAB IKUT TAHUN", ui.W.TEBAL))
        print()

        L = []
        kosong = 0
        for t in tahun_senarai:
            nilai = nisab.untuk_tahun(cfg, jadual, t)
            label = f"{t}" + ("  (semasa)" if t == semasa else "")
            if nilai is None:
                kosong += 1
                L.append(ui.baris_kv(label, "(belum diisi)", DALAM))
            else:
                L.append(ui.baris_kv(label, ui.rm(nilai), DALAM))
        print(ui.kotak(L, LEBAR))
        print()

        if kosong:
            print(ui.warna(
                f"  {kosong} tahun belum diisi. Kiraan qadha memerlukan "
                f"nisab tahun itu.", ui.W.MALAP))
            print()

        print(f"  [{nisab.TAHUN_MULA}-{semasa}] taip tahun untuk isi/ubah"
              "   [0] kembali")
        print()
        pilih = ui.tanya_pilih({str(t) for t in tahun_senarai} | {"0"},
                               "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return

        t = int(pilih)
        lama = nisab.untuk_tahun(cfg, jadual, t)
        nilai = ui.tanya_duit(
            f"Nisab {t} (RM)", "" if lama is None else str(lama))
        if nilai is None:
            continue

        if t == semasa:
            cfg["nisab"] = float(nilai)
            nisab.tanda_dikemas(cfg)
            store.simpan_config(cfg)
            print()
            print(ui.warna(f"  ✓ nisab {t} disimpan — ditanda sudah "
                           f"disahkan juga", ui.W.HIJAU))
        else:
            jadual[str(t)] = float(nilai)
            store.simpan_jadual_nisab(jadual)
            print()
            print(ui.warna(f"  ✓ nisab {t} disimpan", ui.W.HIJAU))
            print(ui.warna("    (peringatan suku tak berubah — ia mengenai "
                           "nisab semasa)", ui.W.MALAP))
        ui.jeda()


def menu_kadar():
    while True:
        cfg = store.config()
        ui.bersih()
        print()
        print(ui.warna("  KADAR & TOLAKAN", ui.W.TEBAL))
        print()
        print(ui.kotak([
            ui.baris_kv("Kadar Masihi", f"{cfg['kadar_masihi']:.3f}%", DALAM),
            ui.baris_kv("Kadar Hijrah", f"{cfg['kadar_hijrah']:.3f}%", DALAM),
            "",
            ui.baris_kv("Nisab", ui.rm(cfg["nisab"]), DALAM),
            ui.baris_kv(
                "  dikemas kini",
                nisab.baca_tarikh(cfg).strftime("%d/%m/%Y")
                if nisab.baca_tarikh(cfg) else "(belum pernah)",
                DALAM),
            "",
            ui.baris_kv("Tolakan diri", ui.rm(cfg["tolakan_diri"]), DALAM),
            ui.baris_kv("Tolakan isteri", ui.rm(cfg["tolakan_isteri"]), DALAM),
            ui.baris_kv("  maksimum", f"{cfg['isteri_maks']} orang", DALAM),
            ui.baris_kv("Tolakan anak A", ui.rm(cfg["tolakan_anak_a"]), DALAM),
            ui.baris_kv("Tolakan anak B", ui.rm(cfg["tolakan_anak_b"]), DALAM),
        ], LEBAR))
        print()
        if nisab.perlu_kemas(cfg)[0]:
            print(ui.warna("  ⚠ " + nisab.mesej_ringkas(cfg), ui.W.KUNING))
            # Merujuk medan ke-3 dalam menu ini, BUKAN menu utama —
            # sebab itu disebut "medan", bukan "[3]" sahaja.
            print(ui.warna("    Sahkan nisab negeri tuan, kemas kini medan "
                           "[3] Nisab", ui.W.MALAP))
            print(ui.warna("    kalau berubah, kemudian tekan [N].", ui.W.MALAP))
            print()
        print("  [1-8] ubah   [T] nisab ikut tahun   [N] dah disahkan   "
              "[R] reset   [0] kembali")
        pilih = ui.tanya_pilih({str(i) for i in range(1, 9)}
                               | {"t", "n", "r", "0"}, "\n  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        if pilih == "t":
            skrin_nisab_tahun()
            continue
        if pilih == "n":
            # Nilai nisab selalunya tidak berubah — jadi pengesahan mesti
            # boleh dilakukan tanpa perlu menaip nilai semula.
            store.simpan_config(nisab.tanda_dikemas(cfg))
            print()
            print(ui.warna("  ✓ nisab ditanda sudah disahkan pada "
                           + tarikh_hari_ini(), ui.W.HIJAU))
            ui.jeda()
            continue
        if pilih == "r":
            store.reset_config()
            print(ui.warna("  ✓ ditetapkan semula", ui.W.HIJAU))
            print(ui.warna("    (tarikh nisab dikosongkan juga)", ui.W.MALAP))
            ui.jeda()
            continue

        kunci, label, jenis = MEDAN[int(pilih) - 1]
        if jenis == "int":
            nilai = ui.tanya_int(label, 0, 10, str(cfg[kunci]))
        else:
            nilai = ui.tanya_duit(label, str(cfg[kunci]))
        if nilai is None:
            continue
        cfg[kunci] = int(nilai) if jenis == "int" else float(nilai)
        if kunci == "nisab":
            # Mengubah nilai nisab bermakna tuan baru menyemaknya.
            nisab.tanda_dikemas(cfg)
        store.simpan_config(cfg)
        print(ui.warna("  ✓ disimpan", ui.W.HIJAU))
        ui.jeda()


def menu_gaya():
    while True:
        cfg = store.config()
        semasa = cfg.get("gaya", cetak.GAYA_LALAI)
        ui.bersih()
        print()
        print(ui.warna("  GAYA OUTPUT PRINT", ui.W.TEBAL))
        print()
        print(f"  Gaya semasa: {ui.warna(cetak.nama_gaya(semasa), ui.W.HIJAU)}")
        print()
        for i, (kunci, nama, nota) in enumerate(cetak.GAYA, 1):
            tanda = "*" if kunci == semasa else " "
            print(f"  {tanda} [{i}]  {nama}")
            print(ui.warna(f"          {nota}", ui.W.MALAP))
        print()
        print("  [0]  Kembali")
        print()

        sah = {str(i) for i in range(1, len(cetak.GAYA) + 1)} | {"0"}
        pilih = ui.tanya_pilih(sah, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        kunci = cetak.GAYA[int(pilih) - 1][0]

        ui.bersih()
        print()
        print(ui.warna(f"  PRATONTON — {cetak.nama_gaya(kunci)}", ui.W.TEBAL))
        print()
        hasil_contoh, ev_contoh = cetak.contoh()
        print(cetak.jana(hasil_contoh, ev_contoh, "Ahmad bin Ali",
                         "2026 (Masihi)", tarikh_hari_ini(), gaya=kunci))
        print()
        print("  [S] Simpan gaya ini    [0] Batal")
        pilih2 = ui.tanya_pilih({"s", "0"}, "\n  pilih ▸ ")
        if pilih2 == "s":
            cfg["gaya"] = kunci
            store.simpan_config(cfg)
            print()
            print(ui.warna(f"  ✓ gaya ditukar ke {cetak.nama_gaya(kunci)}", ui.W.HIJAU))
            ui.jeda()


def menu_tetapan():
    while True:
        cfg = store.config()
        ui.bersih()
        print()
        print(ui.warna("  TETAPAN", ui.W.TEBAL))
        print()
        print(ui.kotak([
            ui.baris_kv("Gaya output print",
                        cetak.nama_gaya(cfg.get("gaya", cetak.GAYA_LALAI)), DALAM),
            ui.baris_kv("Versi", versi.penuh(), DALAM),
            "",
            ui.baris_kv("Semak kemas kini",
                        "Ya" if cfg.get("semak_kemas", True) else "Tidak", DALAM),
            "",
            # Kunci yang app ini percaya. Tanpa baris ini ciri keselamatan
            # itu halimunan sepenuhnya — pengguna tiada cara mengaudit apa
            # yang sebenarnya melindunginya.
            ui.baris_kv("Kunci kemas kini", tandatangan.cap_jari(), DALAM),
        ], LEBAR))
        print()
        print("  [1]  Pilih gaya output print")
        print("  [2]  README — sejarah app ini")
        print(f"  [3]  Sumber kemas kini   {ui.warna(cfg.get('sumber_kemas', '') or '(kosong)', ui.W.MALAP)}")
        print(f"  [4]  Semak semasa buka   {ui.warna('Ya' if cfg.get('semak_kemas', True) else 'Tidak', ui.W.MALAP)}")
        print("  [5]  Eksport data ke fail teks")
        print("  [0]  Kembali")
        print()
        pilih = ui.tanya_pilih({"1", "2", "3", "4", "5", "0"}, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        if pilih == "1":
            menu_gaya()
        elif pilih == "2":
            skrin_readme()
        elif pilih == "3":
            print()
            print(ui.warna("  Contoh: http://10.94.149.204:8000", ui.W.MALAP))
            print(ui.warna("  Alamat folder yang ada versi.json dan taksiran.tar.gz.",
                           ui.W.MALAP))
            print()
            baharu = ui.tanya("Sumber kemas kini",
                              cfg.get("sumber_kemas", ""), boleh_kosong=True)
            if baharu is not None:
                cfg["sumber_kemas"] = baharu.strip()
                store.simpan_config(cfg)
                print(ui.warna("  ✓ disimpan", ui.W.HIJAU))
                ui.jeda()
        elif pilih == "4":
            cfg["semak_kemas"] = not cfg.get("semak_kemas", True)
            store.simpan_config(cfg)
            print()
            print(ui.warna(
                "  ✓ semak semasa buka: "
                + ("Ya" if cfg["semak_kemas"] else "Tidak"), ui.W.HIJAU))
            print()
            if not cfg["semak_kemas"]:
                print(ui.warna("  App tak akan semak sendiri lagi — guna "
                               "[6] Kemas Kini bila perlu.", ui.W.MALAP))
            ui.jeda()
        elif pilih == "5":
            skrin_eksport()


# ---------------------------------------------------------------- readme

def _balut(teks, lebar):
    """Pecah perenggan jadi baris-baris yang muat di terminal.

    Kata ganda Melayu banyak guna sengkang (berulang-ulang, sama-sama),
    jadi jangan pecah pada sengkang dan jangan potong perkataan di tengah.
    """
    return textwrap.wrap(teks, width=lebar,
                         break_on_hyphens=False,
                         break_long_words=False) or [""]


def skrin_readme():
    """Catatan pembinaan app — satu seksyen satu skrin.

    Ini bukan dokumentasi teknikal. Ia cerita. Jadi ia dipaparkan
    perlahan-lahan, seksyen demi seksyen, bukan dilonggokkan sekali.
    """
    jumlah = len(readme.SEKSYEN)

    ui.bersih()
    print()
    print(ui.kotak([
        ui.baris_kv("README", "sejarah app ini", DALAM),
        ui.baris_kv("Seksyen", str(jumlah), DALAM),
    ], LEBAR))
    print()
    print("  Catatan bagaimana app ini terbina — apa yang")
    print("  berlaku, apa yang silap, dan apa yang masih")
    print("  tergantung.")
    print()
    print(ui.warna("  Ini bukan panduan penggunaan.", ui.W.MALAP))
    print()
    try:
        input("  [ENTER] mula    [0] kembali ▸ ")
    except (EOFError, KeyboardInterrupt):
        print()
        return

    for i, (tajuk, baris) in enumerate(readme.SEKSYEN, 1):
        ui.bersih()
        print()
        print(ui.warna(f"  {tajuk.upper()}", ui.W.TEBAL))
        print(ui.warna(f"  seksyen {i} / {jumlah}", ui.W.MALAP))
        print()

        for jenis, teks in baris:
            if jenis == "b":
                for b in _balut(teks, DALAM - 2):
                    print("  " + ui.warna(b, ui.W.KUNING))
                print()
            elif jenis == "m":
                for b in _balut(teks, DALAM - 4):
                    print("    " + ui.warna(b, ui.W.MALAP))
                print()
            elif jenis == "q":
                for b in _balut(teks, DALAM - 8):
                    print("    " + ui.warna("│ ", ui.W.BIRU)
                          + ui.warna(b, ui.W.BIRU))
                print()
            elif jenis == "s":
                potong = _balut(teks, DALAM - 6)
                print(f"    • {potong[0]}")
                for b in potong[1:]:
                    print(f"      {b}")
                print()
            else:
                for b in _balut(teks, DALAM - 2):
                    print(f"  {b}")
                print()

        print()
        try:
            jawab = input("  [ENTER] teruskan    [0] keluar ▸ ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if jawab == "0":
            return

    ui.bersih()
    print()
    print(ui.warna("  Habis. Itu sahaja ceritanya.", ui.W.HIJAU))
    print()
    ui.jeda("  [ENTER] kembali")


def _papar_teks(teks, nota=None):
    """Tunjuk teks print, cuba salin ke clipboard."""
    ui.bersih()
    print()
    print(ui.warna("  SALIN TEKS DI BAWAH ↓", ui.W.MALAP))
    print()
    print(teks)
    print()
    if ui.salin_teks(teks):
        print(ui.warna("  ✓ disalin ke clipboard", ui.W.HIJAU))
    else:
        print(ui.warna("  (clipboard tak tersedia — pilih dan salin manual)", ui.W.MALAP))
    if nota:
        print(ui.warna(f"  ✓ {nota}", ui.W.HIJAU))
    print()
    ui.jeda("  [ENTER] kembali")


def skrin_cetak_rekod(rekod):
    """Print semula rekod sejarah."""
    ui.bersih()
    print(ui.garis("PRINT REKOD", LEBAR))
    print()
    print(f"  {rekod['tarikh']} {rekod.get('masa', '')}   "
          f"{rekod.get('nama') or '(tanpa nama)'}")
    if rekod.get("event"):
        print(ui.warna(f"  {rekod['event']}", ui.W.MALAP))
    print()

    nama = ui.tanya("Nama pembayar (kosongkan kalau tak perlu)",
                    rekod.get("nama", ""), boleh_kosong=True)
    if nama is None:
        return

    hasil = [Hasil.dari_rekod(r) for r in rekod["hasil"]]
    ev = {
        "nama": rekod.get("event", ""),
        "tarikh": rekod.get("tarikh_event", ""),
        "tempat": rekod.get("tempat", ""),
    }
    teks = cetak.jana(
        hasil, ev, nama.strip(), rekod.get("tahun", ""),
        rekod.get("tarikh", tarikh_hari_ini()),
        gaya=store.config().get("gaya", cetak.GAYA_LALAI),
    )
    _papar_teks(teks)


def menu_sejarah():
    while True:
        rekod = store.sejarah()
        ui.bersih()
        print()
        print(ui.warna("  SEJARAH KIRAAN", ui.W.TEBAL))
        print()

        if not rekod:
            print(ui.warna("  (tiada rekod)", ui.W.MALAP))
            print()
            ui.jeda()
            return

        tunjuk = rekod[:20]
        for i, r in enumerate(tunjuk, 1):
            siapa = r.get("nama") or "(tanpa nama)"
            ev = r.get("event") or ""
            tajuk = siapa + (f"  ({ev})" if ev else "")
            print(f"  [{i:>2}]  {r['tarikh']} {r.get('masa', '')}   {tajuk}")
            if r.get("jenis") == "qadha":
                # Rekod qadha ada berpuluh entri hasil. Menyenaraikan
                # setiap satunya menghasilkan dinding teks tanpa makna —
                # yang berguna di sini cuma julat tahun dan jumlahnya.
                nilai = (f"QADHA {r.get('tahun', '')}   "
                         f"{ui.rm(_jumlah_rekod_qadha(r))}")
            else:
                nilai = "   ".join(
                    f"{h['kaedah']} {ui.rm(h['zakat_setahun'])}"
                    for h in r["hasil"]
                )
            print(ui.warna(f"        {nilai}", ui.W.MALAP))
        print()
        print(f"  jumlah rekod: {len(rekod)}  (menunjuk {len(tunjuk)} terkini)")
        print()
        print("  no. untuk print    [K] kosongkan semua    [0] kembali")
        print()

        sah = {str(i) for i in range(1, len(tunjuk) + 1)} | {"k", "0"}
        pilih = ui.tanya_pilih(sah, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        if pilih == "k":
            store.kosongkan_sejarah()
            print()
            print(ui.warna("  ✓ sejarah dikosongkan", ui.W.HIJAU))
            ui.jeda()
            continue
        rekod_pilih = tunjuk[int(pilih) - 1]
        # Rekod lama tiada kunci "jenis" — ia dianggap kiraan biasa, jadi
        # cetakan semulanya tidak berubah langsung.
        if rekod_pilih.get("jenis") == "qadha":
            skrin_cetak_qadha(rekod_pilih)
        else:
            skrin_cetak_rekod(rekod_pilih)


# -------------------------------------------------------------- eksport

def skrin_eksport():
    """Simpan semua data ke satu fail teks — untuk backup."""
    ui.bersih()
    print()
    print(ui.warna("  EKSPORT DATA", ui.W.TEBAL))
    print(ui.garis(None, LEBAR))
    print()

    cfg = store.config()
    rekod = store.sejarah()
    ev = store.event()

    jumlah_nisab = sum(1 for t in nisab.senarai_tahun()
                       if nisab.untuk_tahun(cfg, store.jadual_nisab(), t)
                       is not None)
    print(f"  Tetapan, nisab {jumlah_nisab} tahun, event, dan")
    print(f"  {len(rekod)} rekod sejarah akan ditulis ke satu fail teks.")
    print()
    print(ui.warna("  Fail ini mengandungi nama pembayar.", ui.W.KUNING))
    print(ui.warna("  Simpan di tempat yang selamat.", ui.W.KUNING))
    print()
    print("  [E] Eksport    [0] Kembali")
    print()
    if ui.tanya_pilih({"e", "0"}, "  pilih ▸ ") != "e":
        return

    teks = eksport.jana(cfg, ev, rekod, store.jadual_nisab())
    laluan, ralat = eksport.tulis(teks)

    ui.bersih()
    print()
    print(ui.warna("  EKSPORT DATA", ui.W.TEBAL))
    print(ui.garis(None, LEBAR))
    print()

    if ralat:
        print(ui.warna("  ✗ Gagal menulis fail", ui.W.MERAH))
        print()
        print(f"  {ralat}")
        print()
        print(ui.warna("  Cuba salin ke clipboard pula …", ui.W.MALAP))
        print()
        if eksport.salin_ke_clipboard(teks):
            print(ui.warna("  ✓ disalin ke clipboard", ui.W.HIJAU))
        else:
            print(ui.warna("  ✗ clipboard pun tak tersedia", ui.W.MERAH))
        print()
        ui.jeda()
        return

    print(ui.warna("  ✓ fail disimpan", ui.W.HIJAU))
    print()
    print("  " + laluan)
    print()
    print(f"  {len(teks.splitlines())} baris, {len(teks) / 1024:.1f} KB")
    print()

    if eksport.salin_ke_clipboard(teks):
        print(ui.warna("  ✓ salinannya juga ada dalam clipboard", ui.W.HIJAU))
        print(ui.warna("    (boleh tampal ke e-mel atau nota)", ui.W.MALAP))
    print()
    print(ui.warna("  Untuk lihat isinya:", ui.W.MALAP))
    print(ui.warna(f"    cat {laluan}", ui.W.MALAP))
    print()
    ui.jeda()


# ---------------------------------------------------------------- kemas

# Berapa lama menu utama sanggup tunggu jawapan pelayan sebelum ia naik
# tanpa notis. Kalau pelayan jawab laju (biasanya dalam rangkaian sendiri),
# notis terus kelihatan. Kalau tidak, semakan diteruskan di latar dan
# notis muncul pada skrin berikutnya.
MASA_TUNGGU_MENU = 0.6


def semak_kemas_awal(cfg):
    """Semak versi baharu SEKALI sahaja, semasa app dibuka.

    Sengaja tidak diulang setiap kali kembali ke menu utama — kalau tidak,
    app akan tertunggu setiap kali keluar dari submenu.
    """
    global _KEMAS
    if not cfg.get("semak_kemas", True):
        return

    sumber = cfg.get("sumber_kemas", "")

    def kerja():
        global _KEMAS
        _KEMAS = kemas.semak(sumber)

    t = threading.Thread(target=kerja, daemon=True)
    t.start()
    t.join(MASA_TUNGGU_MENU)


def mula_semula():
    """Ganti proses ini dengan app yang baru dipasang.

    Python sudah memuat kod lama ke dalam memori, jadi kod baharu hanya
    berkuat kuasa selepas proses dimulakan semula.
    """
    try:
        os.execv(sys.executable,
                 [sys.executable, os.path.abspath(__file__)] + sys.argv[1:])
    except OSError:
        print()
        print(ui.warna("  Sila tutup dan buka semula app.", ui.W.MALAP))
        ui.jeda()


def skrin_kemas(cfg):
    """Semak dan pasang versi baharu — semuanya dari dalam app."""
    sumber = cfg.get("sumber_kemas", "")

    def kepala():
        ui.bersih()
        print()
        print(ui.warna("  KEMAS KINI", ui.W.TEBAL))
        print(ui.garis(None, LEBAR))
        print()

    if not sumber:
        kepala()
        print(ui.warna("  Sumber kemas kini belum ditetapkan.", ui.W.MERAH))
        print()
        print("  Tetapkan di  Tetapan ▸ [3] Sumber kemas kini.")
        print()
        ui.jeda()
        return

    kepala()
    print(ui.warna("  Menyemak …", ui.W.MALAP))
    hasil = kemas.semak(sumber)

    kepala()
    print(ui.baris_kv("Dipasang", versi.penuh(), DALAM))
    if hasil.get("ok"):
        print(ui.baris_kv(
            "Terkini", f"v{hasil['versi']} ({hasil['tarikh']})", DALAM))
    print(ui.baris_kv("Sumber", kemas._betulkan(sumber), DALAM))
    print()

    # --- pelayan tak dapat dihubungi ---
    if not hasil.get("ok"):
        print(ui.warna("  ✗ " + hasil["ralat"], ui.W.MERAH))
        print()
        print("  Kalau ini komputer sendiri, hidupkan pelayan:")
        print(ui.warna("    cd ~/serve-zakat", ui.W.MALAP))
        print(ui.warna("    python3 -m http.server 8000", ui.W.MALAP))
        print()
        print("  [C] Cuba lagi    [0] Kembali")
        print()
        if ui.tanya_pilih({"c", "0"}, "  pilih ▸ ") == "c":
            return skrin_kemas(cfg)
        return

    # --- sudah terkini ---
    if not hasil.get("ada"):
        print(ui.warna("  ✓ Tuan sudah guna versi terkini", ui.W.HIJAU))
        print()
        ui.jeda()
        return

    # --- ada versi baharu ---
    if hasil.get("nota"):
        print("  Apa yang berubah:")
        for n in hasil["nota"]:
            print(f"    • {n}")
        print()

    print("  [U] Muat turun & pasang    [0] Kembali")
    print()
    if ui.tanya_pilih({"u", "0"}, "  pilih ▸ ") != "u":
        return

    # --- muat turun dan pasang ---
    langkah = []

    def lapor(mesej):
        langkah.append(mesej)
        kepala()
        print(ui.baris_kv("Memasang", f"v{hasil['versi']}", DALAM))
        print()
        for b in langkah:
            print("  " + b)
        print()

    ok, mesej, berubah = kemas.pasang(sumber, hasil["versi"], lapor)

    kepala()
    if not ok:
        print(ui.warna("  ✗ Pemasangan gagal", ui.W.MERAH))
        print()
        print("  " + mesej)
        print()
        if berubah:
            # Pengekstrakan sudah bermula, jadi kod lama mungkin separuh
            # tertimpa. Mengaku "tiada apa-apa diubah" di sini adalah
            # pembohongan yang menenangkan pada saat paling salah.
            print(ui.warna(
                f"  Salinan kod lama ada dalam "
                f"{os.path.basename(kemas.DIR_SALINAN)}/ — jangan guna app ini",
                ui.W.MERAH))
            print(ui.warna(
                "  sehingga ia dipasang semula.", ui.W.MERAH))
        else:
            print(ui.warna("  Tiada apa-apa diubah — app masih versi lama.",
                           ui.W.HIJAU))
        print()
        # Kegagalan tandatangan ialah keputusan, bukan kemalangan: arkib itu
        # tidak akan berubah menjadi sah pada percubaan seterusnya. Sebut
        # cap jari supaya tuan boleh mengesahkannya sendiri.
        if mesej in _MESEJ_TANDA:
            print(ui.warna(f"  Kunci yang app ini percaya: "
                           f"{tandatangan.cap_jari()}", ui.W.MALAP))
            print(ui.warna("  Cuba lagi tidak akan menolong — arkib itu "
                           "memang bukan daripada tuan.", ui.W.MALAP))
            print()
        ui.jeda()
        return

    print(ui.warna(f"  ✓ v{hasil['versi']} dipasang", ui.W.HIJAU))
    print()
    print("  Data tuan tidak disentuh — rekod sejarah, event")
    print("  dan tetapan kekal seperti sedia ada.")
    print()
    ui.jeda("  [ENTER] mula semula app ▸ ")
    mula_semula()


def menu_utama():
    while True:
        cfg = store.config()
        ev = store.event()
        ui.bersih()
        print()
        print(ui.warna("  TAKSIRAN ZAKAT PENDAPATAN", ui.W.TEBAL))
        print()
        if ev.get("nama"):
            print(ui.warna(f"  Event: {ev['nama']}", ui.W.MALAP))
            print()

        if _KEMAS and _KEMAS.get("ok") and _KEMAS.get("ada"):
            print(ui.kotak([
                ui.baris_kv("Tuan guna", versi.penuh(), DALAM),
                ui.baris_kv("Terkini", f"v{_KEMAS['versi']}", DALAM),
                "",
                "[6] Kemas Kini",
            ], LEBAR, tajuk="KEMAS KINI TERSEDIA"))
            print()

        if nisab.perlu_kemas(cfg)[0]:
            print(ui.kotak([
                nisab.mesej_ringkas(cfg),
                "",
                "[7] Kadar & Tolakan",
            ], LEBAR, tajuk="NISAB PERLU DIKESAHKAN"))
            print()

        # Dua kumpulan: kerja harian, dan urusan app itu sendiri. Kadar &
        # Tolakan masuk APP sebab ia tetapan, bukan kerja harian — ia
        # jarang dibuka, sedangkan Qadha Zakat boleh jadi kerja harian
        # bila ada kes tertunggak.
        print(ui.warna("  ── KIRAAN " + "─" * (DALAM - 8), ui.W.MALAP))
        print()
        print("  [1]  Kira Zakat")
        print("  [2]  Daftar")
        print("  [3]  Qadha Zakat")
        print("  [5]  Sejarah Kiraan")
        print()
        print(ui.warna("  ── APP " + "─" * (DALAM - 5), ui.W.MALAP))
        print()
        print("  [4]  Tetapan")
        print("  [6]  Kemas Kini")
        print("  [7]  Kadar & Tolakan")
        print()
        print("  [0]  Keluar")
        print()
        print(ui.warna(f"  {versi.penuh()}", ui.W.MALAP))
        print()
        pilih = ui.tanya_pilih(
            {"1", "2", "3", "4", "5", "6", "7", "0"}, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            ui.bersih()
            print("\n  jumpa lagi.\n")
            return
        if pilih == "1":
            menu_kira(cfg)
        elif pilih == "2":
            menu_daftar()
        elif pilih == "3":
            menu_qadha(cfg)
        elif pilih == "4":
            menu_tetapan()
        elif pilih == "5":
            menu_sejarah()
        elif pilih == "6":
            skrin_kemas(store.config())
        elif pilih == "7":
            menu_kadar()


def main():
    # Berguna untuk semak versi mana yang ada pada telefon tanpa buka menu.
    if len(sys.argv) > 1 and sys.argv[1] in ("--versi", "-v"):
        print(versi.penuh())
        return 0
    semak_kemas_awal(store.config())
    try:
        menu_utama()
    except KeyboardInterrupt:
        print("\n\n  dibatalkan.\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

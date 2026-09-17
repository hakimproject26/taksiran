#!/usr/bin/env python3
"""Taksiran Zakat Pendapatan — CLI untuk Termux."""

import sys
import textwrap
from datetime import date, datetime
from decimal import Decimal

from zakat import cetak, readme, store, ui, versi
from zakat.kira import Hasil, Tolakan, kira_kaedah_a, kira_kaedah_b

LEBAR = 52
DALAM = LEBAR - 4  # lebar teks di dalam kotak


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


def alir_kaedah_b(cfg):
    ui.bersih()
    print()
    print(ui.warna("  KAEDAH B — DENGAN TOLAKAN", ui.W.TEBAL))
    print()

    jantina = ui.tanya_pilih(
        {"1", "2"},
        "  Jantina   [1] Lelaki   [2] Perempuan\n  pilih ▸ ",
    )
    if jantina is None:
        return
    lelaki = jantina == "1"
    print()

    pend = minta_pendapatan()
    if pend is None:
        return
    kasar, nota = pend

    # --- tolakan tahunan ---
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
            return
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
        return
    kadar_anak = kadar_a if pilih_kadar == "1" else kadar_b

    bil_anak = ui.tanya_int("Bilangan anak", 0, 30, "0")
    if bil_anak is None:
        return
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
            return
        tolakan.append(Tolakan(
            label, v * 12,
            nota=f"{v:,.0f} × 12",
            nota_penuh=f"{ui.rm_pendek(v)} × 12",
        ))

    thn = minta_tahun(cfg)
    if thn is None:
        return
    label_tahun, kadar = thn
    nisab = Decimal(str(cfg["nisab"]))

    hasil_b = kira_kaedah_b(kasar, kadar, nisab, tolakan, nota)
    hasil_a = kira_kaedah_a(kasar, kadar, nisab, nota)
    skrin_hasil([hasil_a, hasil_b], label_tahun)


# --------------------------------------------------------------- paparan

def _baris_hasil(hasil_senarai, label_tahun):
    h0 = hasil_senarai[0]
    L = [
        ui.baris_kv(f"Tahun {label_tahun}", f"Kadar  {h0.kadar:.3f}%", DALAM),
        ui.baris_kv("Nisab", ui.rm(h0.nisab), DALAM),
    ]
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

        L.append("  " + ("✓ cukup nisab" if h.cukup_nisab else "✗ tak cukup nisab"))
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
        print("  [P] Print / Salin    [S] Simpan    [0] Menu")
        pilih = ui.tanya_pilih({"p", "s", "0"}, "\n  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        if pilih == "p":
            skrin_cetak(hasil_senarai, label_tahun)
        else:
            simpan_rekod(hasil_senarai, label_tahun)


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
            "",
            ui.baris_kv("Tolakan diri", ui.rm(cfg["tolakan_diri"]), DALAM),
            ui.baris_kv("Tolakan isteri", ui.rm(cfg["tolakan_isteri"]), DALAM),
            ui.baris_kv("  maksimum", f"{cfg['isteri_maks']} orang", DALAM),
            ui.baris_kv("Tolakan anak A", ui.rm(cfg["tolakan_anak_a"]), DALAM),
            ui.baris_kv("Tolakan anak B", ui.rm(cfg["tolakan_anak_b"]), DALAM),
        ], LEBAR))
        print()
        print("  [1-8] ubah   [R] reset ke lalai   [0] kembali")
        pilih = ui.tanya_pilih({str(i) for i in range(1, 9)} | {"r", "0"},
                               "\n  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        if pilih == "r":
            store.reset_config()
            print(ui.warna("  ✓ ditetapkan semula", ui.W.HIJAU))
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
        ], LEBAR))
        print()
        print("  [1]  Pilih gaya output print")
        print("  [2]  README — sejarah app ini")
        print("  [0]  Kembali")
        print()
        pilih = ui.tanya_pilih({"1", "2", "0"}, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            return
        if pilih == "1":
            menu_gaya()
        elif pilih == "2":
            skrin_readme()


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
            nilai = "   ".join(
                f"{h['kaedah']} {ui.rm(h['zakat_setahun'])}" for h in r["hasil"]
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
        skrin_cetak_rekod(tunjuk[int(pilih) - 1])


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
        print("  [1]  Kira Zakat")
        print("  [2]  Daftar")
        print("  [3]  Kadar & Tolakan")
        print("  [4]  Tetapan")
        print("  [5]  Sejarah Kiraan")
        print("  [0]  Keluar")
        print()
        print(ui.warna(f"  {versi.penuh()}", ui.W.MALAP))
        print()
        pilih = ui.tanya_pilih({"1", "2", "3", "4", "5", "0"}, "  pilih ▸ ")
        if pilih is None or pilih == "0":
            ui.bersih()
            print("\n  jumpa lagi.\n")
            return
        if pilih == "1":
            menu_kira(cfg)
        elif pilih == "2":
            menu_daftar()
        elif pilih == "3":
            menu_kadar()
        elif pilih == "4":
            menu_tetapan()
        elif pilih == "5":
            menu_sejarah()


def main():
    # Berguna untuk semak versi mana yang ada pada telefon tanpa buka menu.
    if len(sys.argv) > 1 and sys.argv[1] in ("--versi", "-v"):
        print(versi.penuh())
        return 0
    try:
        menu_utama()
    except KeyboardInterrupt:
        print("\n\n  dibatalkan.\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

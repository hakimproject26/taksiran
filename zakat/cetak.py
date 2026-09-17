"""Jana teks print untuk dihantar ke WhatsApp.

Ada lima gaya output. WhatsApp guna font berkadar, jadi penjajaran lajur
hanya kekal kalau teks dibalut dalam blok monospace (```). Gaya "mono"
dan "kotak" buat begitu; "baris" dan "ringkas" sengaja tak bergantung
pada penjajaran langsung.

Fon monospace WhatsApp lebih LEBAR daripada fon biasa — jadi baris dalam
blok ``` mesti lebih pendek daripada baris biasa, kalau tidak ia
berlanggar dinding tepi. Semua gaya di sini dihadkan kepada
LEBAR_MAKS aksara.
"""

from decimal import ROUND_HALF_UP, Decimal

from . import store
from .kira import Tolakan, kira_kaedah_a, kira_kaedah_b
from .qadha import jumlah, tahun_tak_cukup
from .ui import rm, rm_pendek

# Siling lebar untuk mana-mana satu baris dalam blok monospace.
LEBAR_MAKS = 34

# Gaya kotak kena lebih sempit — aksara bingkai ═ ║ nampak lebih lebar
# daripada aksara biasa dalam fon monospace WhatsApp.
LEBAR_KOTAK = 30

# Lajur dalam gaya sempit. Label + duit mesti muat dalam content kotak
# (LEBAR_MAKS - 4) supaya tiada baris terlebih lebar.
LEBAR_LABEL = 18
LEBAR_DUIT = 12

GAYA = [
    ("mono", "Monospace", "lajur sejajar, dalam blok ```"),
    ("baris", "Baris biasa", "label: nilai, senarai bulet — paling penuh"),
    ("ringkas", "Ringkas", "nombor penting sahaja — paling pendek"),
    ("titik", "Lajur bertitik", "lajur bertitik ...... dalam blok ```"),
    ("kotak", "Kotak", "bergaris ╔══╗, dalam blok ```"),
    ("menegak", "Bertindan", "label di atas, nilai di bawah — paling selamat"),
]

GAYA_LALAI = "mono"


def nama_gaya(kunci):
    for k, nama, _ in GAYA:
        if k == kunci:
            return nama
    return kunci


def _blok(L):
    """Balut dalam blok monospace WhatsApp."""
    return "```\n" + "\n".join(L) + "\n```"


def _potong(teks, lebar=LEBAR_MAKS):
    """Potong teks yang terlalu panjang, tandakan dengan '…'."""
    if len(teks) <= lebar:
        return teks
    return teks[:lebar - 1] + "…"


def _duit_baris(label, nilai, lebar_label, lebar_duit):
    """Satu baris label + jumlah, sejajar. Label panjang dipotong.

    Guna bentuk duit pendek (RM 10,000 bukan RM 10,000.00) supaya lajur
    boleh dimuatkan dalam blok monospace yang sempit.
    """
    if len(label) > lebar_label:
        label = label[:lebar_label - 1] + "…"
    return f"{label:<{lebar_label}}{rm_pendek(nilai):>{lebar_duit}}"


def _tak_wajib(hs):
    """Adakah nota "tak cukup nisab" perlu keluar?

    Nisab dinilai pada PENDAPATAN KASAR, iaitu asas Kaedah A — bukan pada
    asas selepas tolakan. hs[0] sentiasa Kaedah A, dan kedua-dua kaedah
    berkongsi keputusan nisab yang sama.

    Jadi nota ini keluar SEKALI sahaja untuk seluruh cetakan, dan tidak
    pernah keluar semata-mata sebab Kaedah B jatuh bawah nisab selepas
    tolakan — dalam keadaan itu zakat tetap wajib.
    """
    return not hs[0].cukup_nisab


# ------------------------------------------------------------------ mono

def _mono(hs, ev, nama, label_tahun, tarikh):
    h0 = hs[0]
    L = ["TAKSIRAN ZAKAT PENDAPATAN"]

    if ev.get("nama"):
        L.append(_potong(ev["nama"]))
    if ev.get("tarikh"):
        L.append(_potong(ev["tarikh"]))
    if ev.get("tempat"):
        L.append(_potong(ev["tempat"]))
    L.append("")
    if nama:
        L.append(_potong(f"Nama : {nama}"))
    L.append(f"Tahun: {label_tahun}")
    L.append(f"Kadar: {h0.kadar:.3f}%")
    L.append(f"Nisab: {rm_pendek(h0.nisab)}")
    if _tak_wajib(hs):
        L.append("(tak cukup nisab — tak wajib)")
    L.append("")
    L.append("PENDAPATAN KASAR")
    if h0.sumber_kasar:
        L.append(_potong(h0.sumber_kasar))
    L.append(f"= {rm_pendek(h0.pendapatan_kasar)}")
    L.append("")

    for h in hs:
        L.append("KAEDAH A — TANPA TOLAKAN" if h.kaedah == "A"
                 else "KAEDAH B — DENGAN TOLAKAN")
        if h.tolakan:
            L.append(_duit_baris("Pendapatan kasar", h.pendapatan_kasar,
                                 LEBAR_LABEL, LEBAR_DUIT))
            for t in h.tolakan:
                L.append(_duit_baris(t.label_pendek(), -t.nilai,
                                     LEBAR_LABEL, LEBAR_DUIT))
            L.append(" " * LEBAR_LABEL + "─" * LEBAR_DUIT)
            L.append(_duit_baris("Jumlah tolakan", h.jumlah_tolakan,
                                 LEBAR_LABEL, LEBAR_DUIT))
            L.append("")
            L.append(_duit_baris("Kena zakat", h.kena_zakat,
                                 LEBAR_LABEL, LEBAR_DUIT))
        L.append(f"{rm_pendek(h.kena_zakat)} × {h.kadar:.3f}%")
        L.append(f"= {rm_pendek(h.zakat_setahun)}")
        L.append(f"Setahun: {rm_pendek(h.zakat_setahun)}")
        L.append(f"Sebulan: {rm_pendek(h.zakat_sebulan)}")
        L.append("")

    L.append("JUMLAH ZAKAT")
    for h in hs:
        L.append(f"Kaedah {h.kaedah}")
        L.append(f"  {rm_pendek(h.zakat_setahun)} setahun")
        L.append(f"  {rm_pendek(h.zakat_sebulan)} sebulan")
    L.append("")
    L.append(f"Dikira pada {tarikh}")
    return _blok(L)


# ----------------------------------------------------------------- baris

def _baris(hs, ev, nama, label_tahun, tarikh):
    h0 = hs[0]
    L = ["*TAKSIRAN ZAKAT PENDAPATAN*"]
    if ev.get("nama"):
        L.append(ev["nama"])
        baris_ev = " — ".join(x for x in [ev.get("tarikh"), ev.get("tempat")] if x)
        if baris_ev:
            L.append(baris_ev)
    L.append("")
    if nama:
        L.append(f"Nama: {nama}")
    L.append(f"Tahun: {label_tahun} | Kadar: {h0.kadar:.3f}%")
    L.append(f"Nisab: {rm(h0.nisab)}")
    if _tak_wajib(hs):
        L.append("⚠ Tak cukup nisab — zakat tidak wajib")
    L.append("")
    L.append("*PENDAPATAN KASAR SETAHUN*")
    if h0.sumber_kasar:
        L.append(f"{h0.sumber_kasar} = {rm(h0.pendapatan_kasar)}")
    else:
        L.append(rm(h0.pendapatan_kasar))
    L.append("")

    for h in hs:
        tajuk = ("*KAEDAH A — TANPA TOLAKAN*" if h.kaedah == "A"
                 else "*KAEDAH B — DENGAN TOLAKAN*")
        L.append(tajuk)
        if h.tolakan:
            L.append(f"Pendapatan kasar: {rm(h.pendapatan_kasar)}")
            L.append("Tolakan:")
            for t in h.tolakan:
                # Jumlah yang dah didarab sahaja — tiada formula. Isteri
                # dan anak bawa bilangan (cth. "Isteri 1"), bukan kadar
                # seunit (cth. bukan "1 orang × RM 4,000").
                L.append(f" • {t.pendek}: {rm(t.nilai)}")
            L.append(f"Jumlah tolakan: {rm(h.jumlah_tolakan)}")
            L.append("")
            L.append(f"{rm(h.pendapatan_kasar)} − {rm(h.jumlah_tolakan)}")
            L.append(f"= {rm(h.kena_zakat)}")
        L.append(f"{rm(h.kena_zakat)} × {h.kadar:.3f}%")
        L.append(f"= {rm(h.zakat_setahun)}")
        L.append(f"Setahun {rm(h.zakat_setahun)} | Sebulan {rm(h.zakat_sebulan)}")
        L.append("")

    L.append("*JUMLAH ZAKAT*")
    for h in hs:
        L.append(f"Kaedah {h.kaedah}: {rm(h.zakat_setahun)} setahun / "
                 f"{rm(h.zakat_sebulan)} sebulan")
    L.append("")
    L.append(f"Dikira pada {tarikh}")
    return "\n".join(L)


# --------------------------------------------------------------- ringkas

def _ringkas(hs, ev, nama, label_tahun, tarikh):
    h0 = hs[0]
    L = ["*TAKSIRAN ZAKAT PENDAPATAN*"]
    if ev.get("nama"):
        L.append(ev["nama"])
    L.append("")
    if nama:
        L.append(f"Nama: {nama}")
    L.append(f"Tahun {label_tahun} | Kadar {h0.kadar:.3f}%")
    L.append("")
    L.append(f"Pendapatan kasar: {rm(h0.pendapatan_kasar)}")
    hb = next((h for h in hs if h.tolakan), None)
    if hb:
        L.append(f"Tolakan: {rm(hb.jumlah_tolakan)}")
        L.append(f"Kena zakat: {rm(hb.kena_zakat)}")
    L.append("")
    if _tak_wajib(hs):
        L.append("⚠ Tak cukup nisab — zakat tidak wajib")
    for h in hs:
        L.append(f"*KAEDAH {h.kaedah}*")
        L.append(f"{rm(h.zakat_setahun)} setahun")
        L.append(f"{rm(h.zakat_sebulan)} sebulan")
        L.append("")
    L.append(f"Dikira pada {tarikh}")
    return "\n".join(L)


# ----------------------------------------------------------------- titik

def _titik_gaya(hs, ev, nama, label_tahun, tarikh):
    LEBAR = LEBAR_MAKS

    def titik(kiri, kanan):
        kiri = _potong(kiri, LEBAR_LABEL)
        jarak = LEBAR - len(kiri) - len(kanan)
        if jarak < 3:
            jarak = 3
        return kiri + " " + "." * (jarak - 2) + " " + kanan

    def garisan(ch="─"):
        return ch * LEBAR

    h0 = hs[0]
    L = [garisan("═"), "TAKSIRAN ZAKAT PENDAPATAN"]
    for baris_ev in [ev.get("nama"), ev.get("tarikh"), ev.get("tempat")]:
        if baris_ev:
            L.append(_potong(baris_ev))
    L.append(garisan())
    if nama:
        L.append(_potong(f"Nama  : {nama}"))
    L.append(f"Tahun : {label_tahun}")
    L.append(f"Kadar : {h0.kadar:.3f}%")
    L.append(f"Nisab : {rm_pendek(h0.nisab)}")
    if _tak_wajib(hs):
        L.append("(tak cukup nisab — tak wajib)")
    L.append(garisan("═"))
    L.append("")
    L.append("PENDAPATAN KASAR")
    if h0.sumber_kasar:
        L.append(_potong(h0.sumber_kasar))
    L.append(f"= {rm_pendek(h0.pendapatan_kasar)}")
    L.append("")

    for h in hs:
        L.append(garisan())
        L.append("KAEDAH A — TANPA TOLAKAN" if h.kaedah == "A"
                 else "KAEDAH B — DENGAN TOLAKAN")
        L.append(garisan())
        if h.tolakan:
            L.append(titik("Pendapatan kasar",
                           rm_pendek(h.pendapatan_kasar)))
            for t in h.tolakan:
                L.append(titik(t.label_pendek(), rm_pendek(-t.nilai)))
            L.append(" " * (LEBAR - LEBAR_DUIT) + "─" * LEBAR_DUIT)
            L.append(titik("Jumlah tolakan", rm_pendek(h.jumlah_tolakan)))
            L.append("")
            L.append(titik("Kena zakat", rm_pendek(h.kena_zakat)))
        L.append(f"{rm_pendek(h.kena_zakat)} × {h.kadar:.3f}%")
        L.append(f"= {rm_pendek(h.zakat_setahun)}")
        L.append(titik("Setahun", rm_pendek(h.zakat_setahun)))
        L.append(titik("Sebulan", rm_pendek(h.zakat_sebulan)))
        L.append("")

    L.append(garisan("═"))
    L.append("JUMLAH ZAKAT")
    L.append(garisan("═"))
    for h in hs:
        L.append(titik(f"Kaedah {h.kaedah} setahun",
                       rm_pendek(h.zakat_setahun)))
        L.append(titik(f"Kaedah {h.kaedah} sebulan",
                       rm_pendek(h.zakat_sebulan)))
    L.append(garisan("═"))
    L.append("")
    L.append(f"Dikira pada {tarikh}")
    return _blok(L)


# ----------------------------------------------------------------- kotak

def _kotak(hs, ev, nama, label_tahun, tarikh):
    # Kotak kena lebih sempit daripada gaya lain — aksara bingkai ═ ║
    # nampak lebih lebar dalam fon monospace WhatsApp.
    DALAM = LEBAR_KOTAK - 2
    KANDUNGAN = DALAM - 2
    LEBAR_LABEL, LEBAR_DUIT = 14, 12
    L = ["╔" + "═" * DALAM + "╗"]

    def baris(t):
        L.append("║ " + _potong(t, KANDUNGAN)
                 + " " * max(0, KANDUNGAN - len(_potong(t, KANDUNGAN))) + " ║")

    def tengah(t):
        t = _potong(t, KANDUNGAN)
        kiri = max(0, (KANDUNGAN - len(t)) // 2)
        L.append("║ " + " " * kiri + t
                 + " " * max(0, KANDUNGAN - len(t) - kiri) + " ║")

    def pisah():
        L.append("╟" + "─" * DALAM + "╢")

    h0 = hs[0]
    tengah("TAKSIRAN ZAKAT")
    tengah("PENDAPATAN")
    if ev.get("nama"):
        pisah()
        for baris_ev in [ev["nama"], ev.get("tarikh", ""), ev.get("tempat", "")]:
            if baris_ev:
                baris(baris_ev)
    pisah()
    if nama:
        baris(f"Nama  : {nama}")
    baris(f"Tahun : {label_tahun}")
    baris(f"Kadar : {h0.kadar:.3f}%")
    baris(f"Nisab : {rm_pendek(h0.nisab)}")
    if _tak_wajib(hs):
        # Dua baris pendek — kandungan kotak hanya 26 aksara.
        baris("TAK CUKUP NISAB")
        baris("ZAKAT TAK WAJIB")
    pisah()

    for h in hs:
        baris("KAEDAH " + h.kaedah)
        baris("TANPA TOLAKAN" if h.kaedah == "A" else "DENGAN TOLAKAN")
        pisah()
        if h.tolakan:
            baris(_duit_baris("Pendapatan", h.pendapatan_kasar,
                              LEBAR_LABEL, LEBAR_DUIT))
            for t in h.tolakan:
                baris(_duit_baris(t.label_pendek(), -t.nilai,
                                  LEBAR_LABEL, LEBAR_DUIT))
            baris(" " * LEBAR_LABEL + "─" * LEBAR_DUIT)
            baris(_duit_baris("Jumlah tolak", h.jumlah_tolakan,
                              LEBAR_LABEL, LEBAR_DUIT))
            pisah()
            baris(_duit_baris("Kena zakat", h.kena_zakat,
                              LEBAR_LABEL, LEBAR_DUIT))
        baris(_duit_baris("Setahun", h.zakat_setahun,
                          LEBAR_LABEL, LEBAR_DUIT))
        baris(_duit_baris("Sebulan", h.zakat_sebulan,
                          LEBAR_LABEL, LEBAR_DUIT))
        pisah()

    baris("JUMLAH ZAKAT")
    for h in hs:
        baris(_duit_baris(h.kaedah + " setahun", h.zakat_setahun,
                          LEBAR_LABEL, LEBAR_DUIT))
        baris(_duit_baris(h.kaedah + " sebulan", h.zakat_sebulan,
                          LEBAR_LABEL, LEBAR_DUIT))
    L.append("╚" + "═" * DALAM + "╝")
    L.append("")
    L.append(f"Dikira pada {tarikh}")
    return _blok(L)


# --------------------------------------------------------------- menegak

def _menegak(hs, ev, nama, label_tahun, tarikh):
    """Gaya bertindan — label satu baris, nilainya di baris bawah.

    Tiada lajur sejajar langsung. Sebab itu ia tak boleh berlanggar
    dinding tepi, walau sepanjang mana label atau nama pembayar.
    """
    h0 = hs[0]
    L = ["TAKSIRAN ZAKAT PENDAPATAN"]
    for b in (ev.get("nama"), ev.get("tarikh"), ev.get("tempat")):
        if b:
            L.append(_potong(b))
    L.append("")

    def pasang(label, nilai):
        L.append(_potong(f"  {label}"))
        L.append(_potong(f"    {nilai}"))

    if nama:
        pasang("Pembayar", nama)
    pasang("Tahun", label_tahun)
    pasang("Kadar", f"{h0.kadar:.3f}%")
    pasang("Nisab", rm_pendek(h0.nisab))
    if _tak_wajib(hs):
        L.append("  (tak cukup nisab — tak wajib)")
    L.append("")
    L.append("PENDAPATAN KASAR")
    if h0.sumber_kasar:
        L.append(_potong(f"  {h0.sumber_kasar}"))
    L.append(f"  = {rm_pendek(h0.pendapatan_kasar)}")
    L.append("")

    for h in hs:
        L.append("KAEDAH A — TANPA TOLAKAN" if h.kaedah == "A"
                 else "KAEDAH B — DENGAN TOLAKAN")
        if h.tolakan:
            pasang("Pendapatan kasar", rm_pendek(h.pendapatan_kasar))
            for t in h.tolakan:
                pasang(t.label_pendek(), rm_pendek(-t.nilai))
            pasang("Jumlah tolakan", rm_pendek(h.jumlah_tolakan))
            pasang("Kena zakat", rm_pendek(h.kena_zakat))
        L.append(_potong(f"  {rm_pendek(h.kena_zakat)} × {h.kadar:.3f}%"))
        L.append(f"  = {rm_pendek(h.zakat_setahun)}")
        pasang("Setahun", rm_pendek(h.zakat_setahun))
        pasang("Sebulan", rm_pendek(h.zakat_sebulan))
        L.append("")

    L.append("JUMLAH ZAKAT")
    for h in hs:
        pasang(f"Kaedah {h.kaedah} setahun", rm_pendek(h.zakat_setahun))
        pasang(f"Kaedah {h.kaedah} sebulan", rm_pendek(h.zakat_sebulan))
    L.append("")
    L.append(f"Dikira pada {tarikh}")
    return _blok(L)


# --------------------------------------------------------------- qadha

# Setiap tahun mengambil tiga baris: satu untuk tahun + nisabnya, satu
# untuk kasar + zakat, dan satu baris kosong sebagai pemisah. Bentuk ini
# dipilih kerana tiga lajur wang yang tepat sampai sen tidak muat dalam
# satu baris tanpa lajur bercantum.
_LEBAR_KASAR = 10   # muat sampai 999,999.99
_LEBAR_ZAKAT = 8    # muat sampai 99,999.99


def _sen(nilai):
    """'13644.28' -> '13,644.28'.

    Tepat sampai sen — tiada pembundaran ke ringgit. Jumlah di bawah
    jadual dikira daripada nilai yang SUDAH dikuantisasi ini, jadi ia
    sentiasa berjumlah dengan baris di atasnya.
    """
    d = Decimal(str(nilai)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{d:,.2f}"


def _pecah_senarai(item, lebar):
    """Susun item jadi baris 'a, b, c' yang muat dalam `lebar`."""
    baris, semasa = [], ""
    for x in item:
        calon = x if not semasa else semasa + ", " + x
        if len(calon) > lebar and semasa:
            baris.append(semasa)
            semasa = x
        else:
            semasa = calon
    if semasa:
        baris.append(semasa)
    return baris


def qadha(baris, ev, nama, kaedah, tarikh):
    """Cetakan qadha — tiga baris setiap tahun, satu jumlah.

    Bentuknya jauh berbeza daripada cetakan biasa: tiada tolakan
    dibentangkan (ia sama bagi setiap tahun), dan tiada "sebulan" (tiada
    makna dalam penyelesaian tunggakan). Yang penting di sini ialah
    setiap tahun dinilai dengan nisab TAHUN ITU, dan jumlahnya hanya
    mengira tahun yang cukup nisab.

    Angka dipaparkan TEPAT sampai sen — tiada pembundaran ke ringgit.
    Sebabnya bukan estetika: jumlah di bawah dikira daripada nilai yang
    sama, jadi kalau setiap tahun digenapkan dahulu, jumlah itu tidak
    akan berjumlah dengan baris di atasnya, dan pembaca yang menyemak
    dengan kalkulator akan nampak seolah-olah ada angka hilang.

    Itulah juga sebabnya setiap tahun mengambil dua baris: tiga lajur
    wang yang membawa sen tidak muat dalam satu baris tanpa lajur
    bercantum, dan lajur bercantum membaca sebagai satu nombor.

    Sengaja TIDAK dimasukkan ke dalam _PETA: gaya cetakan pilihan
    pengguna tidak sepatutnya boleh menghalakan kiraan qadha ke pencetak
    biasa, yang akan membentangkan dua belas blok kaedah berturutan.

    Wang tidak pernah melalui _potong — memotong '1,234,567' jadi
    '1,234,5…' membaca sebagai nombor yang berbeza.
    """
    if not baris:
        return _blok(["QADHA ZAKAT", "", "(tiada tahun dikira)"])

    kadar = baris[0][1].kadar
    tahun = [t for t, _ in baris]
    julat = (f"{tahun[0]}" if len(tahun) == 1
             else f"{tahun[0]} – {tahun[-1]}")

    L = ["QADHA ZAKAT — RINGKASAN"]
    if ev.get("nama"):
        L.append(_potong(ev["nama"]))
    if nama:
        L.append(_potong(f"Nama : {nama}"))
    L.append(f"Tahun: {julat} (Masihi)")
    L.append(f"Kadar: {kadar:.3f}%")
    L.append("Kaedah: A (tanpa tolakan)" if kaedah == "A"
             else "Kaedah: B (dengan tolakan)")
    L.append("")
    L.append("Semua nilai dalam RM.")
    L.append("")
    for t, h in baris:
        L.append(f"{t}  (nisab RM {_sen(h.nisab)})")
        L.append(f"kasar {_sen(h.pendapatan_kasar):>{_LEBAR_KASAR}}"
                 f" | zakat {_sen(h.zakat_setahun):>{_LEBAR_ZAKAT}}")
        L.append("")

    # Nota diletak betul-betul di sebelah jumlah, sebab di situlah
    # pembaca akan mengesani yang barisnya tak berjumlah.
    tak_cukup = tahun_tak_cukup(baris)
    if tak_cukup:
        label = "Tahun tak cukup nisab: "
        senarai = ", ".join(str(t) for t in tak_cukup)
        if len(label + senarai) <= LEBAR_MAKS:
            L.append(label + senarai)
        else:
            L.append("Tahun tak cukup nisab:")
            for b in _pecah_senarai([str(t) for t in tak_cukup],
                                    LEBAR_MAKS - 2):
                L.append("  " + b)
        L.append("  (dikecualikan dari jumlah)")
    L.append(f"{'Jumlah zakat':<20}RM {_sen(jumlah(baris))}")
    L.append("")
    L.append(f"Dikira pada {tarikh}")
    return _blok(L)


# --------------------------------------------------------------- pilih

_PETA = {
    "mono": _mono,
    "baris": _baris,
    "ringkas": _ringkas,
    "titik": _titik_gaya,
    "kotak": _kotak,
    "menegak": _menegak,
}


def jana(hasil_senarai, ev, nama, label_tahun, tarikh, gaya=GAYA_LALAI):
    """Pulang teks penuh untuk disalin ke WhatsApp."""
    fungsi = _PETA.get(gaya) or _PETA[GAYA_LALAI]
    return fungsi(hasil_senarai, ev, nama, label_tahun, tarikh)


# --------------------------------------------------------- contoh ujian

def contoh():
    """Kiraan contoh untuk pratonton gaya dalam menu Tetapan."""
    cfg = store.config()
    kadar = Decimal(str(cfg["kadar_masihi"]))
    nisab = Decimal(str(cfg["nisab"]))
    kasar = Decimal("96000")
    tolak = [
        Tolakan("Diri sendiri", 10000),
        Tolakan("Isteri", 4000, nota="1 × 4,000",
                nota_penuh="1 orang × RM 4,000", pendek="Isteri 1"),
        Tolakan("Anak", 6000, nota="3 × 2,000",
                nota_penuh="3 orang × RM 2,000", pendek="Anak 3"),
        Tolakan("KWSP", 13200, nota="1,100 × 12", nota_penuh="RM 1,100 × 12"),
        Tolakan("Tabung Haji", 1200, nota="100 × 12", nota_penuh="RM 100 × 12"),
        Tolakan("ILTAT", 0, nota="0 × 12", nota_penuh="RM 0 × 12"),
    ]
    hasil = [
        kira_kaedah_a(kasar, kadar, nisab, "RM 8,000 × 12"),
        kira_kaedah_b(kasar, kadar, nisab, tolak, "RM 8,000 × 12"),
    ]
    ev = {
        "nama": "Program Zakat Kampung Baru",
        "tarikh": "15/09/2026",
        "tempat": "Dewan Orang Ramai Kg Baru",
    }
    return hasil, ev

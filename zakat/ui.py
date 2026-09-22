"""Helper paparan terminal — kotak, warna, dan input."""

import os
import shutil
import subprocess
import textwrap
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class W:
    RESET = "\033[0m"
    TEBAL = "\033[1m"
    MALAP = "\033[2m"
    MERAH = "\033[31m"
    HIJAU = "\033[32m"
    KUNING = "\033[33m"
    BIRU = "\033[36m"


def warna(teks, kod):
    return f"{kod}{teks}{W.RESET}"


def bersih():
    os.system("clear")


def rm(nilai):
    """Format jadi 'RM 1,234.56'."""
    d = Decimal(str(nilai)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"RM {d:,.2f}"


def rm_pendek(nilai):
    """Format padat untuk nota — 'RM1,100' bukan 'RM 1,100.00'."""
    d = Decimal(str(nilai)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if d == d.to_integral_value():
        return f"RM {d:,.0f}"
    return f"RM {d:,.2f}"


def pad(teks, n):
    return teks + " " * max(0, n - len(teks))


def baris_kv(kiri, kanan, lebar):
    """Kiri di hujung kiri, kanan di hujung kanan."""
    jarak = lebar - len(kiri) - len(kanan)
    if jarak < 1:
        jarak = 1
    return kiri + " " * jarak + kanan


def kotak(baris, lebar=52, tajuk=None):
    """Lukis kotak sekeliling senarai baris (teks biasa).

    Baris yang terlalu panjang dibalut, bukan dibiarkan menembus dinding
    kotak. Tanpa ini, satu nama event yang panjang sudah cukup untuk
    merosakkan seluruh kotak.
    """
    dalam = lebar - 2
    if tajuk:
        atas = "╭─ " + tajuk + " " + "─" * max(0, dalam - len(tajuk) - 3) + "╮"
    else:
        atas = "╭" + "─" * dalam + "╮"
    bawah = "╰" + "─" * dalam + "╯"
    keluar = [atas]
    for b in baris:
        # break_long_words dibiarkan lalai (True). Ia hanya memotong
        # perkataan yang SENDIRI lebih panjang daripada lebar kotak —
        # perkataan biasa tak pernah dipotong. Tanpa ini, satu rentetan
        # panjang tanpa ruang (nama, alamat) akan menembus dinding.
        for serpihan in (textwrap.wrap(b, width=dalam - 2,
                                       break_on_hyphens=False) or [""]):
            keluar.append("│ " + pad(serpihan, dalam - 2) + " │")
    keluar.append(bawah)
    return "\n".join(keluar)


def garis(tajuk=None, lebar=52):
    if tajuk:
        return "── " + tajuk + " " + "─" * max(0, lebar - len(tajuk) - 4)
    return "─" * lebar


def tanya(label, lalai="", boleh_kosong=False):
    """Pulang teks, '' kalau kosong dibenarkan, None kalau dibatalkan."""
    petunjuk = f" [{lalai}]" if lalai != "" else ""
    while True:
        try:
            jawab = input(f"  {label}{petunjuk}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if jawab:
            return jawab
        if boleh_kosong:
            return ""
        if lalai != "":
            return str(lalai)
        print(warna("  ! tak boleh kosong", W.MERAH))


def tanya_duit(label, lalai=""):
    """Pulang Decimal, atau None kalau dibatalkan.

    Hulur lalai="0" untuk medan yang boleh dibiarkan kosong.
    """
    while True:
        j = tanya(label, lalai)
        if j is None:
            return None
        try:
            v = Decimal(j.replace(",", "").replace("RM", "").replace("rm", "").strip())
        except (InvalidOperation, ValueError):
            print(warna("  ! nombor tak sah", W.MERAH))
            continue
        if v < 0:
            print(warna("  ! tak boleh negatif", W.MERAH))
            continue
        return v


def tanya_int(label, minimum=0, maksimum=None, lalai=""):
    """Pulang int, atau None kalau dibatalkan.

    Kalau `lalai` diberi, tekan Enter sahaja akan guna nilai itu. Kalau
    tiada lalai, kosong dikira 0.
    """
    while True:
        # boleh_kosong hanya bila TIADA lalai — kalau ada lalai, biar
        # tanya() yang pulangkan lalai itu, bukan string kosong.
        j = tanya(label, lalai, boleh_kosong=(lalai == ""))
        if j is None:
            return None
        if j == "":
            j = "0"
        try:
            v = int(j)
        except ValueError:
            print(warna("  ! nombor bulat sahaja", W.MERAH))
            continue
        if v < minimum:
            print(warna(f"  ! minimum {minimum}", W.MERAH))
            continue
        if maksimum is not None and v > maksimum:
            print(warna(f"  ! maksimum {maksimum}", W.MERAH))
            continue
        return v


def tanya_pilih(sah, prompt="  pilih ▸ "):
    """Pulang kunci pilihan, atau None kalau dibatalkan."""
    while True:
        try:
            j = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if j in sah:
            return j
        print(warna("  ! pilihan tak sah", W.MERAH))


def jeda(mesej="  [ENTER] teruskan"):
    try:
        input(mesej)
    except (EOFError, KeyboardInterrupt):
        print()


# Berapa lama kita tunggu `termux-clipboard-set`. Ia bercakap dengan app
# Android melalui soket, jadi app yang tidak bertindak balas akan
# menggantung. Tanpa had, app kita yang menggantung.
MASA_TAMAT_SALIN = 5


def salin_teks(teks):
    """Salin ke clipboard Termux.

    Pulang (berjaya, sebab, cadangan). `sebab` dan `cadangan` ialah None
    kalau berjaya, dan pemanggil MESTI memaparkan `sebab` apabila gagal.

    Tiga kegagalan di bawah kelihatan sama dari luar — ketiga-tiganya
    bermakna "tak disalin" — tetapi puncanya berbeza dan pembetulannya
    berbeza. Digabungkan menjadi satu ayat, tuan akan cuba membetulkan
    benda yang salah: dia akan memeriksa clipboard, sedangkan yang tiada
    ialah jambatan ke Android.
    """
    if not shutil.which("termux-clipboard-set"):
        return False, "termux-api tidak dipasang", "pkg install termux-api"
    try:
        p = subprocess.run(
            ["termux-clipboard-set"],
            input=teks.encode("utf-8"),
            timeout=MASA_TAMAT_SALIN,
        )
    except subprocess.TimeoutExpired:
        return (False,
                f"termux-api menggantung ({MASA_TAMAT_SALIN}s)",
                "cuba lagi")
    except OSError:
        return False, "termux-clipboard-set gagal", "cuba lagi"
    if p.returncode != 0:
        return (False,
                "app Termux:API tidak menjawab",
                "semak app Termux:API")
    return True, None, None

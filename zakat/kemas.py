"""Enjin kemas kini — semak versi, muat turun, dan pasang sendiri.

App hubungi pelayan, bandingkan versi, dan kalau ada yang lebih baharu ia
muat turun arkib dan timpa fail kod yang lama. Semuanya dari dalam app;
pengguna tak perlu buka terminal dan taip apa-apa.

Yang SENGAJA tidak dibuat di sini:

  * Tiada pengesahan tandatangan. Sesiapa yang mengawal pelayan boleh
    menghantar apa-apa kod. Untuk pelayan dalam rangkaian sendiri ini
    memadai; kalau satu hari nanti ia diletak di internet, ini lubang
    sebenar dan kena difikir semula.
  * Tiada rollback automatik. Salinan lama disimpan dalam .backup/,
    tetapi memulihkannya masih kerja tangan.

Fail `data/` tidak pernah disentuh — arkib yang dibina memang
mengecualikannya, dan pengekstrakan hanya menimpa fail yang ada di dalam
arkib.
"""

import json
import os
import re
import socket
import tarfile
import tempfile
import urllib.error
import urllib.request

from . import versi

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_SALINAN = os.path.join(AKAR, ".backup")

NAMA_VERSI = "versi.json"
NAMA_ARKIB = "taksiran.tar.gz"

MASA_TAMAT = 3        # saat — semakan versi sahaja (fail kecil)
MASA_TAMAT_MUAT = 60  # saat — muat turun arkib penuh


# ------------------------------------------------------------------ bantu

def _betulkan(sumber):
    """Kemas URL yang ditaip pengguna.

    Terima '10.94.149.204:8000' sepatah — tambah 'http://' sendiri.
    """
    s = (sumber or "").strip().rstrip("/")
    if s and "://" not in s:
        s = "http://" + s
    return s


def _nombor(teks):
    """Tukar '1.2.3' jadi (1, 2, 3) supaya boleh dibandingkan.

    Bahagian yang bukan angka dikira 0 — versi cacat tak sepatutnya
    membuat app terhempas.
    """
    bahagian = []
    for keping in str(teks).split("."):
        try:
            bahagian.append(int(keping))
        except ValueError:
            bahagian.append(0)
    while len(bahagian) < 3:
        bahagian.append(0)
    return tuple(bahagian[:3])


def _ambil(url, masa_tamat):
    with urllib.request.urlopen(url, timeout=masa_tamat) as jawapan:
        return jawapan.read()


def _mesej_ralat(e):
    """Tukar ralat teknikal jadi ayat yang boleh difahami."""
    if isinstance(e, urllib.error.HTTPError):
        if e.code == 404:
            return "Pelayan hidup, tetapi fail itu tiada (404)."
        return f"Pelayan jawab dengan ralat {e.code}."
    if isinstance(e, urllib.error.URLError):
        sebab = getattr(e, "reason", None)
        if isinstance(sebab, (socket.timeout, TimeoutError)):
            return f"Tiada jawapan dalam {MASA_TAMAT} saat."
        if isinstance(sebab, ConnectionRefusedError):
            return "Pelayan menolak sambungan — ia mungkin tidak hidup."
        return f"Tak dapat hubungi pelayan ({sebab})."
    if isinstance(e, (socket.timeout, TimeoutError)):
        return f"Tiada jawapan dalam {MASA_TAMAT} saat."
    return f"Ralat: {e}"


# ------------------------------------------------------------------ semak

def semak(sumber):
    """Semak versi terkini di pelayan.

    Pulang dict. Dua bentuk:
        {"ok": True,  "ada": bool, "versi": str, "tarikh": str, "nota": [str]}
        {"ok": False, "ralat": str}

    Tidak pernah membaling ralat — semua kegagalan jadi "ok": False, supaya
    app boleh terus jalan walau pelayan mati.
    """
    sumber = _betulkan(sumber)
    if not sumber:
        return {"ok": False, "ralat": "Sumber kemas kini belum ditetapkan."}

    try:
        mentah = _ambil(f"{sumber}/{NAMA_VERSI}", MASA_TAMAT)
    except Exception as e:  # noqa: BLE001 — apa-apa pun, jangan hembuskan
        return {"ok": False, "ralat": _mesej_ralat(e)}

    try:
        data = json.loads(mentah.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {"ok": False, "ralat": f"{NAMA_VERSI} rosak atau bukan JSON."}

    jauh = str(data.get("versi", "")).strip()
    if not jauh:
        return {"ok": False, "ralat": f"{NAMA_VERSI} tiada nombor versi."}

    return {
        "ok": True,
        "ada": _nombor(jauh) > _nombor(versi.NOMBOR),
        "versi": jauh,
        "tarikh": str(data.get("tarikh", "")),
        "nota": [str(n) for n in data.get("nota", [])],
    }


# ----------------------------------------------------------------- pasang

def _sahkan(laluan, dijangka):
    """Periksa arkib SEBELUM ia menyentuh apa-apa.

    Pulang (ok, mesej). Kalau ini gagal, fail lama tak disentuh sama sekali.
    """
    try:
        with tarfile.open(laluan, "r:gz") as tf:
            nama = tf.getnames()

            # Jangan benarkan arkib menulis ke luar folder app.
            for n in nama:
                if n.startswith("/") or ".." in n.split("/"):
                    return False, f"Laluan tak selamat dalam arkib: {n}"

            # Arkib mesti ada satu folder akar sahaja (cth. 'taksiran/').
            akar = {n.split("/")[0] for n in nama if "/" in n}
            if len(akar) != 1:
                return False, "Arkib mesti ada tepat satu folder akar."
            awalan = akar.pop() + "/"

            for p in ("main.py", "zakat/versi.py"):
                if awalan + p not in nama:
                    return False, f"Arkib tak lengkap — {p} tiada."

            f = tf.extractfile(awalan + "zakat/versi.py")
            teks = f.read().decode("utf-8", "replace") if f else ""
    except (tarfile.TarError, OSError) as e:
        return False, f"Fail rosak atau bukan arkib yang sah ({e})."

    padan = re.search(r'^NOMBOR\s*=\s*["\']([^"\']+)["\']', teks, re.M)
    if not padan:
        return False, "Tak dapat baca nombor versi dalam arkib."
    jumpa = padan.group(1)
    if dijangka and jumpa != dijangka:
        return False, f"Arkib ini versi {jumpa}, bukan {dijangka} seperti dijangka."
    return True, ""


def simpan_salinan():
    """Simpan kod versi semasa ke .backup/ sebelum ia ditimpa.

    Bukan rollback automatik — cuma jaring keselamatan supaya kod lama
    masih boleh dipulihkan dengan tangan kalau sesuatu jadi tidak kena.
    """
    os.makedirs(DIR_SALINAN, exist_ok=True)
    laluan = os.path.join(DIR_SALINAN, f"taksiran-{versi.NOMBOR}.tar.gz")
    awalan = os.path.basename(AKAR) + "/"
    with tarfile.open(laluan, "w:gz") as tf:
        for item in ("main.py", "README.md", "CHANGELOG.md", "zakat"):
            p = os.path.join(AKAR, item)
            if os.path.exists(p):
                tf.add(p, arcname=awalan + item)
    return laluan


def _ekstrak(laluan, ke):
    """Ekstrak isi arkib TERUS ke dalam folder app.

    Komponen pertama setiap nama (cth. 'taksiran/') dibuang dahulu. Tanpa
    ini, arkib akan masuk ke 'taksiran/taksiran/…' — satu folder terlalu
    dalam. Ia juga bermakna folder app boleh dinamakan apa sahaja.
    """
    with tarfile.open(laluan, "r:gz") as tf:
        ahli = []
        for m in tf.getmembers():
            bahagian = m.name.split("/")[1:]
            if not bahagian or not any(bahagian):
                continue  # entri akar arkib — tiada isi
            m.name = "/".join(bahagian)
            ahli.append(m)

        try:
            # Python 3.12+ — tolak laluan tak selamat, buang setuid.
            tf.extractall(path=ke, members=ahli, filter="data")
        except TypeError:
            # Python lebih lama tiada parameter `filter`. Laluan sudah
            # diperiksa dalam _sahkan(), jadi ini selamat.
            tf.extractall(path=ke, members=ahli)


def pasang(sumber, versi_dijangka, lapor=None):
    """Muat turun dan pasang versi baharu.

    `lapor` ialah fungsi yang dipanggil dengan mesej kemajuan, supaya skrin
    boleh menunjuk langkah demi langkah.

    Pulang (ok, mesej_ralat).
    """
    if lapor is None:
        lapor = lambda m: None  # noqa: E731

    sumber = _betulkan(sumber)
    if not sumber:
        return False, "Sumber kemas kini belum ditetapkan."

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz")
    tmp.close()
    try:
        lapor(f"Memuat turun {NAMA_ARKIB} …")
        data = _ambil(f"{sumber}/{NAMA_ARKIB}", MASA_TAMAT_MUAT)
        with open(tmp.name, "wb") as f:
            f.write(data)
        lapor(f"  {len(data) / 1024:.0f} KB diterima")

        lapor("Menyemak fail …")
        ok, mesej = _sahkan(tmp.name, versi_dijangka)
        if not ok:
            return False, mesej
        lapor("  ✓ arkib sah")

        lapor("Menyimpan salinan lama …")
        simpan_salinan()
        lapor(f"  ✓ {os.path.basename(DIR_SALINAN)}/")

        lapor("Memasang …")
        _ekstrak(tmp.name, AKAR)
        lapor("  ✓ selesai")
        return True, ""
    except Exception as e:  # noqa: BLE001
        return False, _mesej_ralat(e)
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass

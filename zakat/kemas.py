"""Enjin kemas kini — semak versi, muat turun, sahkan, dan pasang sendiri.

App hubungi pelayan, bandingkan versi, dan kalau ada yang lebih baharu ia
muat turun arkib dan timpa fail kod yang lama. Semuanya dari dalam app;
pengguna tak perlu buka terminal dan taip apa-apa.

Setiap arkib mesti ditandatangani dengan kunci rahsia tuan, dan disahkan
terhadap kunci awam yang tersemat dalam `zakat/tandatangan.py` SEBELUM
apa-apa disentuh. Inilah yang menghalang pelayan yang diceroboh — atau
sesiapa yang memintas trafik — daripada menghantar kod sendiri. Ia perlu
di sini dan bukan di pelayan kerana alamat pelayan boleh disunting
pengguna (Tetapan ▸ [3]), jadi URL itu tidak boleh menjadi sempadan
kepercayaan.

Turutan dalam `pasang()` ialah keputusan keselamatan, bukan citarasa:
tandatangan disahkan DAHULU, baru struktur arkib diperiksa. Sebabnya
`_sahkan()` memanggil `tf.getnames()`, yang memaksa penyahmampatan gzip
penuh — jadi arkib bom meletup sebelum apa-apa disahkan kalau turutannya
terbalik. `_periksa()` memegang kedua-dua langkah itu dalam satu fungsi
supaya tiada siapa boleh menyelipkan pengekstrakan antara keduanya
kemudian.

Yang SENGAJA tidak dibuat di sini:

  * Tiada rollback automatik. Salinan lama disimpan dalam .backup/,
    tetapi memulihkannya masih kerja tangan.
  * Tiada suis untuk mematikan pengesahan tandatangan. Suis begitu ialah
    laluan pintas, dan laluan pintas ialah tempat penyerang menekan.

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

from . import tandatangan, versi

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_SALINAN = os.path.join(AKAR, ".backup")

NAMA_VERSI = "versi.json"
NAMA_ARKIB = "taksiran.tar.gz"
NAMA_SIG = NAMA_ARKIB + ".sig"

MASA_TAMAT = 3         # saat — semakan versi sahaja (fail kecil)
MASA_TAMAT_TANDA = 10  # saat — fail tandatangan (129 bait, talian boleh lembap)
MASA_TAMAT_MUAT = 60   # saat — muat turun arkib penuh

# Arkib sebenar ~45 KB. Had ini wujud kerana pengesahan berlaku SELEPAS
# muat turun — pelayan yang diceroboh boleh menghantar strim tanpa
# penghujung, dan tiada kripto boleh menolong selepas memori habis.
SAIZ_MAKS = 20 * 1024 * 1024

# Nombor versi yang sah. Diperiksa kerana `_nombor()` sangat pemaaf —
# `_nombor("9.9.evil")` memulangkan (9, 9, 0) tanpa aduan.
_RE_VERSI = re.compile(r"^\d+(\.\d+){0,2}$")

# Aksara kawalan terminal. Ini bukan kekemasan: medan `nota` dicetak ke
# skrin pada SETIAP kali app dibuka, sebelum sebarang pengesahan tandatangan
# berjalan. Pelayan yang diceroboh boleh menyelitkan "\x1b[2J\x1b[H" di situ
# dan melukis semula terminal — memalsukan "✓ tandatangan sah", atau
# menyembunyikan penolakan.
_RE_KAWAL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


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


def _bersih(teks):
    """Buang aksara kawalan terminal. Lihat _RE_KAWAL."""
    return _RE_KAWAL.sub("", str(teks))


def _ambil(url, masa_tamat, maks=SAIZ_MAKS):
    """Muat turun, dengan had saiz.

    Had ini bukan keselesaan. Pengesahan tandatangan berlaku SELEPAS muat
    turun, jadi pelayan yang diceroboh boleh menghantar strim tanpa
    penghujung dan menghabiskan memori telefon sebelum sebarang kripto
    berjalan. Tiada tandatangan boleh menolong selepas itu.
    """
    with urllib.request.urlopen(url, timeout=masa_tamat) as jawapan:
        dijangka = jawapan.headers.get("Content-Length")
        if dijangka and dijangka.isdigit() and int(dijangka) > maks:
            raise ValueError(
                f"fail itu {int(dijangka) / 1048576:.1f} MB, sedangkan had "
                f"ialah {maks // 1048576} MB"
            )
        # Baca maks + 1 bait, bukan maks. Kalau tidak, fail yang tepat-tepat
        # melebihi had akan kelihatan sama panjang dengan fail yang cukup.
        data = jawapan.read(maks + 1)
        if len(data) > maks:
            raise ValueError(
                f"fail itu melebihi had {maks // 1048576} MB — pelayan "
                "menghantar lebih daripada yang diminta"
            )
        return data


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

    jauh = _bersih(data.get("versi", "")).strip()
    if not jauh:
        return {"ok": False, "ralat": f"{NAMA_VERSI} tiada nombor versi."}
    if not _RE_VERSI.match(jauh):
        return {"ok": False,
                "ralat": f"{NAMA_VERSI} ada nombor versi yang tidak sah."}

    return {
        "ok": True,
        "ada": _nombor(jauh) > _nombor(versi.NOMBOR),
        "versi": jauh,
        "tarikh": _bersih(data.get("tarikh", "")),
        "nota": [_bersih(n) for n in data.get("nota", [])],
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


def _periksa(laluan, dijangka, teks_sig, data):
    """Gat tunggal: sahkan tandatangan DAHULU, kemudian struktur arkib.

    Kedua-duanya sengaja berada dalam satu fungsi. Turutannya ialah
    keputusan keselamatan — `_sahkan()` menyahmampatkan seluruh arkib untuk
    membaca senarai namanya, jadi arkib bom akan meletup sebelum apa-apa
    disahkan kalau turutannya terbalik. Menggabungkan keduanya di sini
    bermakna tiada sesiapa boleh menyelipkan pengekstrakan antara dua
    langkah itu kemudian.

    Pulang (ok, mesej).
    """
    ok, sebab = tandatangan.sahkan(teks_sig, data)
    if not ok:
        return False, sebab
    return _sahkan(laluan, dijangka)


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

    Pulang (ok, mesej_ralat, berubah).

    `berubah` ialah soalan ketiga yang berasingan daripada yang lain:
    adakah fail dalam folder app mungkin sudah tersentuh? Ia False untuk
    SEMUA kegagalan sebelum pengekstrakan — tandatangan tak padan, arkib
    rosak, muat turun gagal — dan dalam kes itu skrin boleh mengaku
    "Tiada apa-apa diubah" dengan jujur. Ia True apabila pengekstrakan
    bermula, kerana pengekstrakan menulis terus ke dalam folder app dan
    boleh berhenti separuh jalan.
    """
    if lapor is None:
        lapor = lambda m: None  # noqa: E731

    sumber = _betulkan(sumber)
    if not sumber:
        return False, "Sumber kemas kini belum ditetapkan.", False

    # Jaring keselamatan, bukan kawalan anti-replay. `semak()` hanya
    # menawarkan kemas kini apabila versi jauh LEBIH BESAR, dan `_sahkan()`
    # memerlukan NOMBOR dalam arkib sama dengan `dijangka` — jadi arkib lama
    # yang tulen tidak boleh dikitar semula untuk menurunkan versi. Ini
    # menjaga pemanggil `pasang()` pada masa depan, bukan hari ini.
    # Kekal `<`, jangan tukar ke `<=`: `<` membenarkan pembaikan versi
    # yang sama, dan itu lebih berguna daripada menolaknya.
    if versi_dijangka and _nombor(versi_dijangka) < _nombor(versi.NOMBOR):
        return False, (f"Arkib itu versi {versi_dijangka}, lebih lama "
                       f"daripada {versi.NOMBOR} yang sudah dipasang."), False

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz")
    tmp.close()
    try:
        lapor(f"Memuat turun {NAMA_ARKIB} …")
        data = _ambil(f"{sumber}/{NAMA_ARKIB}", MASA_TAMAT_MUAT)
        with open(tmp.name, "wb") as f:
            f.write(data)
        lapor(f"  {len(data) / 1024:.0f} KB diterima")

        lapor(f"Memuat turun {NAMA_SIG} …")
        try:
            teks_sig = _ambil(f"{sumber}/{NAMA_SIG}", MASA_TAMAT_TANDA)
            teks_sig = teks_sig.decode("ascii", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False, (f"{NAMA_SIG} tiada di pelayan — kemas kini "
                               f"dibatalkan. Pelayan ini tidak menyediakan "
                               f"tandatangan."), False
            raise

        # Baris ini keluar SEBELUM pengesahan, bukan selepas. Pengesahan
        # mengambil ~0.6 saat di laptop dan beberapa kali ganda di telefon;
        # skrin yang membeku tanpa petunjuk kelihatan seperti app hang.
        lapor("Mengesahkan tandatangan …")
        ok, mesej = _periksa(tmp.name, versi_dijangka, teks_sig, data)
        if not ok:
            # Gagal TERTUTUP. Mana-mana `except` di sekeliling pengesahan
            # tidak boleh berakhir dengan kod yang dipasang.
            return False, mesej, False
        lapor("  ✓ tandatangan sah, arkib utuh")

        lapor("Menyimpan salinan lama …")
        simpan_salinan()
        lapor(f"  ✓ {os.path.basename(DIR_SALINAN)}/")

        lapor("Memasang …")
        try:
            _ekstrak(tmp.name, AKAR)
        except Exception as e:  # noqa: BLE001
            # Berbeza daripada semua kegagalan di atas, yang berlaku sebelum
            # apa-apa disentuh. Pengekstrakan menulis TERUS ke dalam folder
            # app, jadi ia boleh berhenti separuh jalan — dan `berubah`
            # memberitahu skrin supaya tidak mengaku sebaliknya.
            return False, (f"Sebahagian fail sudah ditulis, kemudian gagal "
                           f"({e}). Salinan kod lama ada dalam "
                           f"{os.path.basename(DIR_SALINAN)}/ — pasang semula "
                           f"dari situ."), True
        lapor("  ✓ selesai")
        return True, "", True
    except Exception as e:  # noqa: BLE001
        return False, _mesej_ralat(e), False
    finally:
        # Arkib muat turun mesti dibuang dalam SEMUA jalan keluar, termasuk
        # setiap `return` di atas dan sebarang pengecualian. Tanpa ini,
        # setiap kemas kini meninggalkan ~50 KB dalam folder sementara.
        try:
            os.unlink(tmp.name)
        except OSError:
            pass

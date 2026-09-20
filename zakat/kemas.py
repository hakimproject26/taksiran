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

  * Tiada rollback automatik. Salinan lama disimpan dalam `~/.taksiran/backup/`,
    tetapi memulihkannya masih kerja tangan.
  * Tiada suis untuk mematikan pengesahan tandatangan. Suis begitu ialah
    laluan pintas, dan laluan pintas ialah tempat penyerang menekan.

Data pengguna tidak pernah disentuh, dan sejak v3.1.0 itu SIFAT, bukan janji:
`data/` dan `backup/` tinggal di `~/.taksiran/`, di luar folder app yang
ditimpa oleh pengekstrakan. Lihat `zakat/akar.py`. `bina.sh` masih
mengecualikan `data/` daripada arkib, tetapi itu kini tali pinggang kedua.
"""

import hashlib
import json
import os
import re
import socket
import ssl
import tarfile
import tempfile
import urllib.error
import urllib.request

from .akar import AKAR_KOD, DIR_SALINAN

# Di mana launcher itu tinggal, kalau ia sudah dipasang. Lihat `aether_aktif()`.
DIR_HKM = os.path.join(os.path.expanduser("~"), ".hkm")
from . import manifes, tandatangan, versi

AKAR = AKAR_KOD

NAMA_VERSI = "versi.json"
NAMA_ARKIB = "taksiran.tar.gz"
NAMA_SIG = NAMA_ARKIB + ".sig"

# Masa tamat ialah PARAMETER, bukan satu pemalar sejagat. Semakan yang
# berjalan di latar semasa app dibuka tidak patut menunggu selama skrin yang
# tuan sedang melihat dengan sengaja.
MASA_TAMAT = 3         # saat — semakan latar semasa app dibuka (fail kecil)
MASA_TAMAT_PAPAN = 10  # saat — skrin Kemas Kini, di mana tuan memang menunggu
MASA_TAMAT_TANDA = 10  # saat — fail tandatangan (129 bait, talian boleh lembap)
MASA_TAMAT_MUAT = 60   # saat — muat turun arkib penuh
#
# Kenapa 3 saat terlalu ketat untuk saluran GitHub, dan kenapa ia dibiarkan
# begitu untuk semakan latar: lima muat turun berturut-turut dari mesin
# berwayar mengambil 0.45 0.37 0.37 2.36 0.38 saat. Satu daripada lima
# menggunakan 79% belanjawan. Di telefon, melalui data mudah alih, dengan DNS
# sejuk dan DUA jabat tangan TLS (github.com, kemudian hos asetnya), 3 saat
# akan dilepasi dengan kerap.
#
# Itu tidak menggagalkan pelancaran — `semak_kemas_awal` hanya menunggu 0.6
# saat sebelum menu naik, jadi semakan yang lambat cuma tiba lewat. Yang
# benar-benar menunggu ialah skrin Kemas Kini, dan itulah sebabnya skrin itu
# memakai MASA_TAMAT_PAPAN.
#
# HAD: `timeout=` pada urlopen ialah masa tamat setiap OPERASI soket, bukan
# had masa dinding. Pelayan yang menitis satu bait setiap tujuh saat boleh
# memanjangkan satu bacaan jauh melebihi 10 saat. Had yang sebenar
# memerlukan pemeriksaan di dalam gelung baca dalam `_ambil`.

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

    Terima '100.78.29.8:8000' sepatah — tambah 'http://' sendiri. Saluran
    lalai ialah HTTPS dan sudah membawa skema, jadi ia melalui fungsi ini
    tanpa diubah.
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


def _mesej_ralat(e, masa_tamat=MASA_TAMAT):
    """Tukar ralat teknikal jadi ayat yang boleh difahami.

    `masa_tamat` dihulur masuk, bukan dibaca daripada pemalar modul. Versi
    lama memformat dengan `MASA_TAMAT` supaya masa tamat 60 saat yang luput
    pada muat turun arkib melaporkan "Tiada jawapan dalam 3 saat" — angka
    yang salah, di skrin yang tuan sedang baca untuk memutuskan apa nak buat.
    """
    if isinstance(e, urllib.error.HTTPError):
        if e.code == 404:
            return "Pelayan hidup, tetapi fail itu tiada (404)."
        return f"Pelayan jawab dengan ralat {e.code}."
    if isinstance(e, urllib.error.URLError):
        sebab = getattr(e, "reason", None)
        if isinstance(sebab, ssl.SSLCertVerificationError):
            # HTTPS menambah satu mod kegagalan yang tidak wujud semasa
            # saluran ini memakai http:// ke alamat LAN: stor sijil. Tanpa
            # mesej yang menyatakannya, ia kelihatan seperti "pelayan mati"
            # dan tuan akan membetulkan benda yang salah.
            return ("Sijil HTTPS tidak dapat diperiksa — stor sijil peranti "
                    "mungkin tiada. Cuba: pkg install ca-certificates")
        if isinstance(sebab, (socket.timeout, TimeoutError)):
            return f"Tiada jawapan dalam {masa_tamat} saat."
        if isinstance(sebab, ConnectionRefusedError):
            return "Pelayan menolak sambungan — ia mungkin tidak hidup."
        return f"Tak dapat hubungi pelayan ({sebab})."
    if isinstance(e, (socket.timeout, TimeoutError)):
        return f"Tiada jawapan dalam {masa_tamat} saat."
    return f"Ralat: {e}"


# ------------------------------------------------------------------ semak

def semak(sumber, masa_tamat=MASA_TAMAT):
    """Semak versi terkini di saluran kemas kini.

    Pulang dict. Dua bentuk:
        {"ok": True,  "ada": bool, "versi": str, "tarikh": str, "nota": [str]}
        {"ok": False, "ralat": str}

    Tidak pernah membaling ralat — semua kegagalan jadi "ok": False, supaya
    app boleh terus jalan walau pelayan mati.

    `masa_tamat` dihulur oleh pemanggil. Semakan latar semasa app dibuka
    memakai lalai yang pendek; skrin Kemas Kini, di mana tuan memang
    menunggu, memakai MASA_TAMAT_PAPAN. Lihat nota di MASA_TAMAT.
    """
    sumber = _betulkan(sumber)
    if not sumber:
        return {"ok": False, "ralat": "Sumber kemas kini belum ditetapkan."}

    try:
        mentah = _ambil(f"{sumber}/{NAMA_VERSI}", masa_tamat)
    except Exception as e:  # noqa: BLE001 — apa-apa pun, jangan hembuskan
        return {"ok": False, "ralat": _mesej_ralat(e, masa_tamat)}

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

def _hash_ahli(tf, ahli):
    """SHA-256 satu ahli arkib. Pemanggil sudah memastikan ia fail biasa."""
    f = tf.extractfile(ahli)
    if f is None:
        raise tarfile.TarError(f"tak dapat baca {ahli.name}")
    h = hashlib.sha256()
    while True:
        blok = f.read(1 << 20)
        if not blok:
            break
        h.update(blok)
    return h.hexdigest()


def _sahkan_manifes(tf, awalan, nama):
    """Bandingkan MANIFEST dalam arkib dengan isi arkib itu sendiri.

    Pulang (ok, mesej). Dipanggil SEBELUM apa-apa diekstrak.

    Ini pemeriksaan yang menghalang telefon daripada terkunci. Kalau
    MANIFEST yang dihantar basi — dijana sebelum satu fail terakhir
    disunting — maka Aether akan menolak app itu pada setiap kali dibuka
    selepas ia dipasang, dan alat kemas kini berada di dalam app itu.
    Menangkapnya di sini bermakna versi lama masih utuh dan masih boleh
    memuat turun pembaikan.
    """
    try:
        f = tf.extractfile(awalan + manifes.NAMA)
        teks_manifes = f.read().decode("utf-8", "replace") if f else ""
        f = tf.extractfile(awalan + manifes.NAMA_SIG)
        teks_sig = f.read().decode("ascii", "replace") if f else ""
    except (tarfile.TarError, OSError, UnicodeDecodeError) as e:
        return False, f"Tak dapat baca MANIFEST dalam arkib ({e})."

    # Tandatangan MANIFEST disemak walaupun arkib itu sendiri sudah
    # ditandatangani. Ia berlebihan untuk KESAHIHAN, tetapi bukan untuk
    # kebolehgunaan: `MANIFEST.sig` yang rosak akan mengunci telefon, dan
    # satu-satunya tempat ia boleh ditangkap ialah di sini.
    ok, sebab = tandatangan.sahkan(teks_sig, teks_manifes.encode("utf-8"))
    if not ok:
        return False, f"Tandatangan MANIFEST tidak sah — {sebab}"

    try:
        _kepala, entri = manifes.hurai(teks_manifes)
    except manifes.ManifesRalat as e:
        return False, f"MANIFEST tidak boleh dipercayai — {e}"

    cincang = {}
    for m in tf.getmembers():
        if not m.name.startswith(awalan):
            continue
        relatif = m.name[len(awalan):]
        if not relatif:
            continue
        # Folder dalam arkib hanyalah bekas; ia tidak dihantar sebagai fail
        # dan ia tidak disenaraikan.
        if m.isdir():
            continue
        # Symlink, peranti, fifo. Kita tidak pernah menghantar ini, dan
        # `data_filter` MEMBENARKAN symlink relatif dalam pokok — jadi ia
        # mesti ditolak di sini, sebelum apa-apa diekstrak.
        if not m.isfile():
            return False, (f"Arkib mengandungi {relatif} yang bukan fail "
                           f"biasa — kemas kini dibatalkan.")
        cincang[relatif] = _hash_ahli(tf, m)

    masalah = manifes.banding(entri, cincang)
    if masalah:
        senarai = "\n".join(f"         {m}" for m in masalah[:5])
        lagi = f"\n         … dan {len(masalah) - 5} lagi" if len(masalah) > 5 else ""
        return False, (
            "MANIFEST tidak menepati isi arkib — kemas kini dibatalkan.\n"
            "       Ini pepijat binaan, bukan serangan. Kalau ia dipasang,\n"
            "       app itu akan menolak dirinya sendiri setiap kali dibuka.\n"
            f"{senarai}{lagi}"
        )
    return True, ""


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

            # MANIFEST dan MANIFEST.sig WAJIB. Aether memerlukan kedua-duanya
            # untuk membuka app itu, jadi arkib tanpanya ialah telefon yang
            # terkunci — lebih baik ditolak di sini, semasa versi lama masih
            # boleh memuat turun pembaikan.
            for p in ("main.py", "zakat/versi.py",
                      manifes.NAMA, manifes.NAMA_SIG):
                if awalan + p not in nama:
                    return False, (
                        f"Arkib tak lengkap — {p} tiada.\n"
                        f"       Tanpa MANIFEST, app yang dipasang tidak akan "
                        f"boleh dibuka semula."
                    )

            ok, mesej = _sahkan_manifes(tf, awalan, nama)
            if not ok:
                return False, mesej

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
        # Dua sebab, dan kedua-duanya dinamakan. Yang pertama ialah serangan:
        # arkib atau tandatangannya ditukar dalam perjalanan. Yang kedua ialah
        # perlumbaan — arkib dan `.sig` dimuat turun dalam dua permintaan
        # BERASINGAN terhadap asas `latest/download` yang bergerak, jadi
        # menerbitkan dua versi berturut-turut semasa telefon di tengah-
        # tengah muat turun boleh memasangkannya silang.
        #
        # Mesej ini SENGAJA tidak menyuruh "cuba lagi". Mengajar seseorang
        # mengulang permintaan selepas tandatangan tidak padan bermakna
        # mengajar mereka menembusi percubaan serangan dengan mengulang.
        # Tuan yang tahu dia baru sahaja menerbitkan dua kali akan faham
        # sendiri; tuan yang tidak, tidak sepatutnya diberi galakan.
        return False, (
            f"{sebab}\n"
            f"       Arkib dan tandatangannya tidak sepadan. Ini boleh "
            f"bermakna fail itu diubah dalam perjalanan, atau saluran sedang "
            f"bertukar versi ketika ia dimuat turun. Jangan pasang kod ini "
            f"sebelum jelas yang mana satu."
        )
    return _sahkan(laluan, dijangka)


def aether_aktif():
    """Betulkah Aether sudah dipasang, dan sedang menjaga app ini?

    Kemas kini DALAM app tidak boleh memasangnya sendiri. Memasang launcher
    bermakna menulis `~/.hkm/aether.py` dan menukar baris alias dalam
    `.bashrc` — dua benda di luar folder app, dan dua benda yang app ini
    tidak patut sentuh tanpa disuruh. Itu kerja `pasang.sh`.

    Jadi keadaannya diperiksa, dan kalau ia belum dipasang, pengguna
    diberitahu DENGAN JELAS. Versi ini menghantar `aether/aether.py` ke
    cakera tetapi tidak menggunakannya, dan app yang kelihatan dilindungi
    sedangkan tidak ialah lebih buruk daripada app yang terang-terang tidak.
    """
    return os.path.isfile(os.path.join(DIR_HKM, "aether.py"))


def simpan_salinan():
    """Simpan kod versi semasa ke `~/.taksiran/backup/` sebelum ia ditimpa.

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


def _manifes_dalam_arkib(laluan):
    """Senarai laluan dalam MANIFEST arkib, atau None kalau ia tidak boleh dibaca."""
    try:
        with tarfile.open(laluan, "r:gz") as tf:
            nama = tf.getnames()
            akar = {n.split("/")[0] for n in nama if "/" in n}
            if len(akar) != 1:
                return None
            awalan = akar.pop() + "/"
            f = tf.extractfile(awalan + manifes.NAMA)
            teks = f.read().decode("utf-8", "replace") if f else ""
        _kepala, entri = manifes.hurai(teks)
        return {laluan for _, laluan in entri}
    except (tarfile.TarError, OSError, manifes.ManifesRalat):
        return None


def _fail_di_pokok(akar):
    """Setiap fail dalam pokok app, relatif kepada `akar`.

    Folder tidak dipulangkan. Symlink dipulangkan — ia mesti dikenal pasti
    dan dibuang, bukan dilangkau.
    """
    dijumpai = set()
    for asas, folder, fail in os.walk(akar, followlinks=False):
        for f in fail:
            penuh = os.path.join(asas, f)
            dijumpai.add(os.path.relpath(penuh, akar).replace(os.sep, "/"))
        # Jangan turun ke dalam folder yang bukan kod.
        folder[:] = [d for d in folder
                     if not manifes.abaikan(
                         os.path.relpath(os.path.join(asas, d), akar)
                         .replace(os.sep, "/"))]
    return dijumpai


def _bersihkan_asing(akar, baharu):
    """Selaraskan pokok app dengan MANIFEST yang bertandatangan.

    Pengekstrakan hanya MENULIS fail yang ada dalam arkib; ia tidak membuang
    apa-apa. Jadi pokok itu boleh mengandungi fail yang bukan sebahagian
    daripada kod bertandatangan:

      * Modul yang dipadamkan daripada kod pada versi baharu. Fail lama
        kekal, Aether melihatnya sebagai "dalam arkib, tiada dalam MANIFEST",
        dan app itu menolak dirinya sendiri setiap kali dibuka. Alat kemas
        kini berada DI DALAM app itu — jadi tiada jalan pulang.
      * Fail yang ditambah kemudian oleh sesiapa sahaja, atau oleh tuan
        sendiri secara tidak sengaja.

    Keselamatan fungsi ini bergantung pada satu perkara: ia memadam HANYA
    fail yang tidak disenaraikan dalam MANIFEST yang baru sahaja disahkan.
    Pokok app ini kod sahaja — data pengguna berada di `~/.taksiran/` sejak
    v3.1.0 — jadi apa-apa yang tidak ditandatangani memang bukan miliknya.
    """
    asing = []
    for laluan in sorted(_fail_di_pokok(akar)):
        if laluan in baharu or laluan in (manifes.NAMA, manifes.NAMA_SIG):
            continue
        if manifes.abaikan(laluan):
            continue
        asing.append(laluan)

    dibuang = []
    for laluan in asing:
        penuh = os.path.join(akar, laluan)
        try:
            os.unlink(penuh)
            dibuang.append(laluan)
        except OSError:
            pass
    return dibuang


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
    # Diperiksa SEMASA jalan. `except` di bawah membalut kedua-dua muat turun,
    # jadi ia tidak boleh tahu yang mana satu luput daripada pemboleh ubah
    # tempatan di dalam blok `try` — dan melaporkan "Tiada jawapan dalam 60
    # saat" untuk fail tandatangan 129 bait ialah ayat yang mengelirukan.
    tamat = MASA_TAMAT_MUAT
    try:
        lapor(f"Memuat turun {NAMA_ARKIB} …")
        data = _ambil(f"{sumber}/{NAMA_ARKIB}", tamat)
        with open(tmp.name, "wb") as f:
            f.write(data)
        lapor(f"  {len(data) / 1024:.0f} KB diterima")

        lapor(f"Memuat turun {NAMA_SIG} …")
        tamat = MASA_TAMAT_TANDA
        try:
            teks_sig = _ambil(f"{sumber}/{NAMA_SIG}", tamat)
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

        # SELEPAS salinan lama (supaya modul yang akan dibuang ada dalam
        # sandaran), dan SEBELUM pengekstrakan. Lihat `_bersihkan_asing()`.
        baharu = _manifes_dalam_arkib(tmp.name)
        if baharu is not None:
            dibuang = _bersihkan_asing(AKAR, baharu)
            if dibuang:
                lapor(f"  ✓ {len(dibuang)} fail lama/asing dibuang")

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
        return False, _mesej_ralat(e, tamat), False
    finally:
        # Arkib muat turun mesti dibuang dalam SEMUA jalan keluar, termasuk
        # setiap `return` di atas dan sebarang pengecualian. Tanpa ini,
        # setiap kemas kini meninggalkan ~50 KB dalam folder sementara.
        try:
            os.unlink(tmp.name)
        except OSError:
            pass

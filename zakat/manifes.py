"""Penghurai MANIFEST — pihak app.

MANIFEST ialah senarai setiap fail yang dihantar, dengan SHA-256 setiap satu.
Ia dibina oleh `~/HKM/aether/manifes.py` (kod sisi-bina, tidak pernah
dihantar) dan ditandatangani dua kali: sekali secara langsung
(`MANIFEST.sig`), dan sekali lagi secara tidak langsung kerana ia berada di
dalam arkib yang ditandatangani.

Fail ini menjawab SATU soalan sahaja, dan soalan itu mesti dijawab SEBELUM
pengekstrakan:

    Adakah MANIFEST ini benar-benar menerangkan arkib ini?

Kenapa ia mesti dijawab di sini, bukan di telefon selepas pemasangan:

  Kalau MANIFEST yang dihantar basi — dijana sebelum satu fail terakhir
  disunting, jadi hashnya tidak lagi padan — maka app yang dipasang akan
  DITOLAK oleh Aether pada setiap kali dibuka. Dan alat kemas kini berada
  DI DALAM app itu. Telefon itu terkunci, dan tiada jalan pulang melaluinya.

  Jadi arkib yang MANIFEST-nya tidak menepati isinya mesti ditolak semasa
  PEMASANGAN, ketika versi lama masih utuh dan masih boleh memuat turun
  pembaikan. Itulah gunanya fail ini.

PENGHURAI INI ADALAH SALINAN daripada `baca_manifes()` dalam
`~/HKM/aether/aether.py`, dan ia mesti kekal salinan. Aether tidak boleh
`import` daripada app — app ialah benda yang ia syak — jadi dua salinan itu
memang perlu. Yang memastikan kedua-duanya tidak menyimpang ialah
`bina.sh`, yang memeriksa setiap arkib yang dibina dengan pengesah DI SINI,
dan `skenario.sh` dalam HKM, yang memeriksa artifak yang SAMA dengan
pengesah Aether. Satu artifak, dua pemeriksa bebas.
"""

import os
import re

NAMA = "MANIFEST"
NAMA_SIG = NAMA + ".sig"
PENGEPALA = "hkm-manifes"
VERSI_FORMAT = "1"

# Dua senarai, dan PEMISAHANNYA ialah perkara penting dalam fail ini.
#
# `banding()` — yang membandingkan MANIFEST dengan ARKIB — tidak memakai
# senarai ini langsung. Arkib mesti mengandungi TEPAT fail yang disenaraikan,
# tiada lebih. Arkib dibina daripada pokok staging yang dibina daripada
# senarai masuk, jadi sifat itu boleh dituntut, bukan diharap. Melonggarkan
# `banding()` bermakna satu `__pycache__` yang terlepas ke dalam arkib akan
# dipasang, muncul di cakera, dan Aether menolak app itu setiap kali dibuka —
# dengan alat kemas kininya di dalam app itu.
#
# Senarai ini dipakai oleh `abaikan()`, yang berjalan atas pokok DI CAKERA.
# Di sana `__pycache__` dan `data/` memang wujud dan memang bukan kod.
#
# `data` dan `.backup` ada dalam senarai ini walaupun sejak v3.1.0 kedua-duanya
# tinggal di `~/.taksiran/`. Sebabnya pemasangan LAMA: telefon yang belum
# dibuka sejak kemas kini masih ada folder itu di dalam pokok, dan ia mesti
# tidak dikira sebagai fail asing. Ia akan berpindah keluar pada pembukaan
# pertama.
ABA_I_MANA = frozenset({"__pycache__", ".git"})
ABA_I_AKAR = frozenset({"data", ".backup", "alat", ".hkm"})

_RE_SAH = re.compile(r"^[A-Za-z0-9._][A-Za-z0-9._/-]*$")
_RE_CINCANG = re.compile(r"^[0-9a-f]{64}$")


class ManifesRalat(Exception):
    """MANIFEST tidak boleh dibaca, atau tidak boleh dipercayai."""


def hurai(teks):
    """Hurai teks MANIFEST. Pulang (kepala, [(cincang, laluan)]).

    Fail ini boleh ditulis penyerang, jadi penghurai ini menolak apa-apa yang
    boleh menjadikan laluan itu satu pembohongan: laluan mutlak, `..`,
    backslash, entri berulang, dan nama yang tidak sepadan corak sah.
    """
    kepala = {}
    entri = []
    dilihat = set()

    for no, baris in enumerate(teks.splitlines(), 1):
        baris = baris.rstrip("\r")
        if not baris:
            continue
        if baris.startswith("#"):
            isi = baris[1:].strip()
            if isi.startswith(PENGEPALA):
                sisa = isi[len(PENGEPALA):].strip()
                if sisa:
                    kepala[PENGEPALA] = sisa
            elif ":" in isi:
                k, _, v = isi.partition(":")
                kepala[k.strip()] = v.strip()
            continue

        bahagian = baris.split("  ", 1)
        if len(bahagian) != 2:
            raise ManifesRalat(f"baris {no}: bukan '<cincang>  <laluan>'.")
        cincang, laluan = bahagian[0].strip(), bahagian[1].strip()

        if not _RE_CINCANG.match(cincang):
            raise ManifesRalat(f"baris {no}: bukan SHA-256 hex.")
        if not _RE_SAH.match(laluan) or ".." in laluan.split("/"):
            raise ManifesRalat(f"baris {no}: laluan tak selamat: {laluan!r}")
        if "\\" in laluan:
            raise ManifesRalat(f"baris {no}: backslash dalam laluan.")
        if laluan in dilihat:
            raise ManifesRalat(f"baris {no}: entri berulang: {laluan}")
        dilihat.add(laluan)
        entri.append((cincang, laluan))

    if not entri:
        raise ManifesRalat("tiada entri fail.")
    if kepala.get(PENGEPALA) != VERSI_FORMAT:
        raise ManifesRalat(
            f"format tidak dikenali: {kepala.get(PENGEPALA, '(tiada)')!r}")
    return kepala, entri


def abaikan(laluan):
    """Betulkah laluan ini bukan kod, dan memang tiada dalam MANIFEST?

    HANYA untuk pokok di cakera. `banding()` tidak memakainya — lihat komen
    di atas senarai abaikan.
    """
    bahagian = laluan.split("/")
    if any(b in ABA_I_MANA for b in bahagian):
        return True
    return bahagian[0] in ABA_I_AKAR


def banding(entri, cincang):
    """Banding MANIFEST dengan isi arkib. Pulang senarai masalah.

    `cincang` memetakan setiap FAIL BIASA dalam arkib kepada sha256-nya.

    Dua arah, dan kedua-duanya perlu:

      * Ada dalam arkib, tiada dalam MANIFEST — fail yang tidak ditandatangani
        secara langsung. Ini menangkap `alat/` atau `data/` yang bocor masuk.
      * Ada dalam MANIFEST, tiada dalam arkib — MANIFEST yang basi. Ini
        menangkap pepijat binaan yang akan mengunci telefon.
    """
    masalah = []
    # `entri` ialah [(cincang, laluan)] — perhatikan turutannya.
    dijangka = {laluan: cincang for cincang, laluan in entri}
    ada = set(cincang)

    for laluan in sorted(ada):
        if laluan in (NAMA, NAMA_SIG):
            continue
        if laluan not in dijangka:
            masalah.append(f"{laluan}: dalam arkib, tiada dalam MANIFEST")
        elif cincang[laluan] != dijangka[laluan]:
            masalah.append(f"{laluan}: hash tidak padan")

    for laluan in sorted(dijangka):
        if laluan not in ada:
            masalah.append(f"{laluan}: dalam MANIFEST, tiada dalam arkib")

    return masalah

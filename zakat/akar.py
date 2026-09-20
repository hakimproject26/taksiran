"""Di mana data pengguna tinggal — DI LUAR folder app.

Sebelum v3.1.0, `data/` dan `.backup/` duduk di dalam folder app. Itu bukan
sekadar tidak kemas, dan dua sebabnya berasingan:

  * Setiap rekod yang disimpan kelihatan seperti PENGUBAHSUAIAN KEPADA KOD.
    Mana-mana alat yang menyemak pokok app akan menuduh app merosakkan
    dirinya sendiri setiap kali ia menyimpan — jadi alat itu sama ada tidak
    berguna, atau ia terpaksa diajar satu senarai pengecualian, dan senarai
    pengecualian ialah tempat lubang bersembunyi.
  * `kemas.pasang()` menulis ke dalam folder yang SAMA dengan data pembayar.
    Arkib yang dibina memang mengecualikan `data/`, tetapi "dikecualikan
    oleh skrip bina" ialah janji, bukan sifat. Satu `--exclude` yang
    tersalah taip memadamkan sejarah kiraan seseorang.

Selepas ini, `pasang()` boleh menimpa seluruh folder app tanpa menyentuh
satu rekod pun. Itu sifat, bukan janji.
"""

import os
import shutil

# Folder kod — tempat `main.py` dan `zakat/` berada.
AKAR_KOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Folder data pengguna. Di luar pokok kod dengan sengaja, supaya menimpa
# kod tidak boleh menyentuh data.
DIR_PENGGUNA = os.path.join(os.path.expanduser("~"), ".taksiran")
DIR_DATA = os.path.join(DIR_PENGGUNA, "data")
DIR_SALINAN = os.path.join(DIR_PENGGUNA, "backup")

# Lokasi LAMA, di dalam folder app. Hanya digunakan oleh `pindah()`.
_AKAR_KOD_LAMA = (
    ("data", os.path.join(AKAR_KOD, "data")),
    ("backup", os.path.join(AKAR_KOD, ".backup")),
)


class RalatAkar(Exception):
    """Data pengguna tidak dapat dipindahkan, dan meneruskan akan bermakna
    app mula dengan folder yang kosong."""


def pindah(lapor=None):
    """Pindahkan data dari lokasi lama ke lokasi baharu. Pulang senarai nama
    yang benar-benar dipindahkan.

    Dipanggil setiap kali app dibuka; ia tidak melakukan apa-apa selepas kali
    pertama. Kalau KEDUA-DUA lokasi wujud, yang lama DIBIARKAN: meninggalkan
    salinan yang tidak digunakan jauh lebih baik daripada memadam data
    pembayar berdasarkan tekaan tentang mana yang betul. Tuan boleh
    memadamnya sendiri apabila dia yakin.

    Gagal berpindah BUKAN sebab untuk teruskan secara senyap. App akan
    membaca folder kosong, menulis rekod baharu di sana, dan tuan akan
    menyangka sejarah kiraannya hilang — sedangkan ia ada, satu folder
    jauhnya. Jadi ia membaling, dan `main.py` menghentikan app dengan mesej
    yang boleh difahami.
    """
    if lapor is None:
        lapor = lambda m: None  # noqa: E731

    os.makedirs(DIR_PENGGUNA, exist_ok=True)
    dipindah = []
    for nama, lama in _AKAR_KOD_LAMA:
        baharu = os.path.join(DIR_PENGGUNA, nama)
        if not os.path.isdir(lama):
            continue
        if os.path.exists(baharu):
            lapor(f"  ! {nama}/ lama masih ada dalam folder app — "
                  f"yang baharu di {baharu} digunakan")
            continue
        try:
            # shutil.move cuba os.rename dahulu (satu filesystem, serta-merta)
            # dan jatuh ke salin+padam kalau tidak. Kedua-duanya betul.
            shutil.move(lama, baharu)
        except OSError as e:
            raise RalatAkar(
                f"Tak dapat pindahkan {lama}\n"
                f"                 ke {baharu}: {e}\n"
                f"       App dihentikan supaya ia tidak mula dengan folder "
                f"kosong.\n"
                f"       Data tuan masih selamat di lokasi lama."
            ) from e
        dipindah.append(nama)
        lapor(f"  → {nama}/ dipindahkan keluar dari folder app")

    if dipindah:
        lapor(f"    (kini di {DIR_PENGGUNA} — kemas kini kod tidak lagi "
              f"boleh menyentuhnya)")
    return dipindah

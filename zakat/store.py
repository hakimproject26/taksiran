"""Baca dan tulis data JSON — config, event, sejarah.

Lokasi `data/` ditentukan oleh `zakat/akar.py`, dan ia berada DI LUAR folder
app dengan sengaja. Lihat docstring di sana: kod dan data tidak boleh
berkongsi folder, kerana kemas kini menimpa folder itu sepenuhnya.
"""

import json
import os

from .akar import AKAR_KOD, DIR_DATA

# Masih dieksport kerana nama ini sudah lama wujud. `AKAR_KOD` ialah nama
# yang jujur: ia folder kod, bukan folder data.
AKAR = AKAR_KOD


CONFIG_LALAI = {
    "kadar_masihi": 2.577,
    "kadar_hijrah": 2.500,
    "nisab": 34000,
    "tolakan_diri": 10000,
    "tolakan_isteri": 4000,
    "isteri_maks": 4,
    "tolakan_anak_a": 2000,
    "tolakan_anak_b": 1000,
    "gaya": "mono",
    # Tarikh (YYYY-MM-DD) nisab kali terakhir disahkan dengan pihak zakat.
    # Kosong bermakna belum pernah — app akan mengingatkan setiap suku.
    "nisab_dikemas": "",
    # Saluran kemas kini. Boleh ditukar di Tetapan ▸ [3].
    #
    # `latest/download` TIDAK mengandungi nombor versi, jadi alamat ini kekal
    # sah untuk setiap versi seterusnya.
    #
    # Sejarah ringkas, sebab ia menerangkan kenapa ia kelihatan begini:
    # dahulu IP LAN rumah (berubah bila router memberi alamat baharu, dan
    # setiap kali ia berubah semakan kemas kini mati tanpa bunyi), kemudian
    # IP Tailscale mesin tuan, dan sekarang release GitHub. Yang terakhir ini
    # bukan sekadar lebih senang: ia HTTPS, jadi arkib tidak boleh ditukar
    # dalam perjalanan, dan mesin tuan tidak perlu hidup.
    #
    # Alamat Tailscale lama masih berfungsi kalau GitHub tidak dapat
    # dicapai — tukar di Tetapan ▸ [3] — tetapi ia kini sandaran, bukan
    # saluran utama.
    "sumber_kemas": (
        "https://github.com/hakimproject26/taksiran/releases/latest/download"
    ),
    # Semak versi baharu setiap kali app dibuka. Boleh dimatikan kalau
    # ia terasa lambat — lihat Tetapan ▸ [4].
    "semak_kemas": True,
}


def _laluan(nama):
    return os.path.join(DIR_DATA, nama)


def baca(nama, lalai):
    try:
        with open(_laluan(nama), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return lalai


def tulis(nama, data):
    os.makedirs(DIR_DATA, exist_ok=True)
    with open(_laluan(nama), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Alamat lalai yang PERNAH dihantar dalam versi yang sudah dipasang di
# telefon. Padan-tepat sahaja: apa-apa selain senarai ini ialah pilihan tuan
# sendiri, dan tidak boleh disentuh.
_SUMBER_LAMA = (
    "http://100.78.29.8:8000",     # Tailscale, v3.0.0 – v3.1.0
    "http://10.94.149.204:8000",   # LAN rumah, sebelum v3.0.0
)


def _pindah_sumber(d):
    """Tukar alamat kemas kini lalai yang LAMA kepada saluran GitHub.

    Kenapa ini perlu wujud sama sekali: `config()` menindih `config.json`
    yang disimpan DI ATAS `CONFIG_LALAI`, jadi menukar lalai di atas kertas
    tidak mengubah apa-apa pada telefon yang sudah dipasang. Ia kekal
    memegang alamat lama selama-lamanya, dan alamat itu kini sandaran yang
    mungkin tidak hidup.

    Dipanggil dengan config.json YANG DISIMPAN, bukan gabungan dengan lalai,
    kerana hanya fail itu yang boleh memberitahu kita apa yang tuan sebenarnya
    ada. Menulis hanya apabila ia benar-benar menukar sesuatu.

    Ia berlaku SEKALI sahaja. Penanda `sumber_dipindah` bermakna kalau tuan
    sengaja menetapkan semula alamat lama kemudian (kerana GitHub tidak
    dapat dicapai, contohnya), app tidak akan menentang pilihan itu pada
    setiap kali dibuka — penolakan berulang terhadap keputusan tuan ialah
    pepijat, bukan ketegasan.
    """
    if not isinstance(d, dict) or d.get("sumber_dipindah"):
        return None
    if d.get("sumber_kemas") not in _SUMBER_LAMA:
        return None
    d["sumber_kemas"] = CONFIG_LALAI["sumber_kemas"]
    d["sumber_dipindah"] = True
    tulis("config.json", d)
    return d["sumber_kemas"]


def config():
    d = baca("config.json", {})
    if isinstance(d, dict):
        _pindah_sumber(d)
    c = dict(CONFIG_LALAI)
    c.update(d)
    return c


def simpan_config(c):
    tulis("config.json", c)


def reset_config():
    tulis("config.json", dict(CONFIG_LALAI))
    return dict(CONFIG_LALAI)


def jadual_nisab():
    """Nisab ikut tahun — {"2015": 13644, ...}.

    Kunci ialah tahun sebagai teks, sebab JSON menjadikan kunci objek
    sebagai teks juga. Tahun SEMASA tiada di sini: ia dibaca daripada
    cfg["nisab"]. Lihat zakat/nisab.py — satu kebenaran bagi setiap
    tahun, bukan dua salinan yang dicermin.
    """
    d = baca("nisab.json", {})
    return d if isinstance(d, dict) else {}


def simpan_jadual_nisab(d):
    tulis("nisab.json", d)


def event():
    return baca("event.json", {})


def simpan_event(ev):
    tulis("event.json", ev)


def sejarah():
    return baca("sejarah.json", [])


def tambah_sejarah(rekod):
    s = sejarah()
    s.insert(0, rekod)
    tulis("sejarah.json", s[:200])


def kosongkan_sejarah():
    tulis("sejarah.json", [])

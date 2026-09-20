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
    # Alamat pelayan kemas kini. Boleh ditukar di Tetapan ▸ [3].
    #
    # Ini alamat Tailscale, sama seperti lalai dalam `pasang.sh`. Sebelum ini
    # ia IP LAN rumah, dan IP LAN berubah bila router memberi alamat baharu —
    # setiap kali ia berubah, semakan kemas kini mati tanpa bunyi. Alamat
    # Tailscale kekal, dan ia berfungsi dari mana-mana, bukan hanya WiFi rumah.
    "sumber_kemas": "http://100.78.29.8:8000",
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


def config():
    c = dict(CONFIG_LALAI)
    c.update(baca("config.json", {}))
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

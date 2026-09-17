"""Baca dan tulis data JSON — config, event, sejarah."""

import json
import os

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DATA = os.path.join(AKAR, "data")


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
    # Alamat pelayan kemas kini. Boleh ditukar di Tetapan ▸ [3].
    "sumber_kemas": "http://10.94.149.204:8000",
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

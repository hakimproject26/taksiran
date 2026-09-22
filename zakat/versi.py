"""Nombor versi app.

Format MAJOR.MINOR.PATCH — dipanggil semantic versioning.

    MAJOR  naik bila sesuatu yang lama TAK BERFUNGSI lagi.
           Pengguna terpaksa ubah cara guna.
    MINOR  naik bila ada TAMBAHAN baharu, tapi yang lama masih jalan.
    PATCH  naik bila BAIKI yang rosak sahaja.

Ukurannya bukan berapa banyak kerja, tapi berapa besar kesannya pada
pengguna. Buang satu feature = MAJOR, walaupun kerjanya sepuluh minit.

Setiap kali nombor ini naik, catat sebabnya dalam CHANGELOG.md.
"""

NOMBOR = "3.1.2"
TARIKH = "22/09/2026"

# Apa yang berubah pada versi SEMASA. Dipaparkan pada skrin Kemas Kini,
# dan dihantar ke app lain melalui versi.json di pelayan.
# Sejarah penuh ada dalam CHANGELOG.md.
NOTA = [
    "Clipboard berfungsi semula. Ia mati setiap kali app dibuka",
    "melalui Aether, kerana Aether membuang pemboleh ubah Android",
    "yang termux-api perlukan — dilancarkan terus dari shell ia",
    "berfungsi, dan itu sebabnya ia hanya muncul selepas Aether",
    "mengambil alih alias",
    "Bila salinan gagal, app kini menyebut puncanya, bukan",
    "menyalahkan clipboard",
]


def penuh():
    """Contoh: 'v1.1.0 (17/09/2026)'."""
    return f"v{NOMBOR} ({TARIKH})"

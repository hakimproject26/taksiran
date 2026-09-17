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

NOMBOR = "1.0.0"
TARIKH = "17/09/2026"

SEJARAH = [
    ("1.0.0", "17/09/2026", "Mula guna versi. Keadaan app setakat ini."),
]


def penuh():
    """Contoh: 'v1.0.0 (17/09/2026)'."""
    return f"v{NOMBOR} ({TARIKH})"

"""Kiraan qadha — zakat tertunggak merentas banyak tahun.

Kenapa ia berasingan daripada zakat/kira.py: dalam kiraan biasa, satu
nisab dipakai untuk satu kiraan. Dalam qadha, nisab BERBEZA bagi setiap
tahun (ia ikut harga emas), jadi gaji 2015 mesti dinilai dengan nisab
2015. Menilai semua tahun dengan nisab hari ini menghasilkan dua jenis
kesilapan sekaligus — tahun lama nampak tak cukup nisab padahal wajib,
dan tahun baru nampak wajib lebih awal daripada sepatutnya.

Setiap tahun menghasilkan satu `Hasil` yang sedia ada daripada kira.py,
jadi peraturan nisab v1.2.1 (dinilai pada pendapatan kasar) terpakai
secara automatik tanpa disalin semula di sini.

Modul ini enjin tulen: tiada import UI, tiada input, tiada cetak — sama
sifatnya dengan zakat/kira.py.

Keadaan bundle disimpan dalam MEMORI sahaja, tiada draf dalam store.py.
Termux boleh dimatikan bila-bila, tetapi inputnya hanya beberapa nombor,
dan draf separuh siap yang dimuatkan semula tanpa disedari lebih
berbahaya daripada kehilangan yang jelas kelihatan.
"""

from decimal import Decimal

from . import nisab as _nisab
from .kira import kira_kaedah_a, kira_kaedah_b


class Bundle:
    """Kumpulan tahun yang hendak dikira qadha."""

    def __init__(self, tahun_senarai, kaedah="B"):
        self.kaedah = kaedah
        # Susunan tahun ditentukan pengguna, jadi ia disimpan sebagai
        # senarai — cuma tanpa ulangan.
        self.tahun = list(dict.fromkeys(tahun_senarai))
        self.kasar = {}          # tahun -> Decimal (nilai TAHUNAN)
        self.tolakan_lalai = []  # dipakai oleh semua tahun (Kaedah B)
        self.tolakan_khas = {}   # tahun -> [Tolakan] yang mengatasi lalai

    # ------------------------------------------------------------- isi

    def set_kasar(self, tahun, nilai):
        """Simpan pendapatan kasar setahun.

        Sentiasa dalam bentuk TAHUNAN. Mod bulanan/tahunan cuma soal
        paparan dan prompt — enjin tidak perlu tahu bezanya.
        """
        self.kasar[tahun] = Decimal(str(nilai))

    def tolakan_untuk(self, tahun):
        return self.tolakan_khas.get(tahun, self.tolakan_lalai)

    def set_tolakan(self, tahun, tolakan):
        """Tolakan khas untuk tahun ini sahaja."""
        self.tolakan_khas[tahun] = list(tolakan)

    def buang_tolakan_khas(self, tahun):
        """Kembali kepada tolakan lalai bagi tahun ini."""
        self.tolakan_khas.pop(tahun, None)

    def tolakan_diubah(self, tahun):
        return tahun in self.tolakan_khas

    def jumlah_tolakan_lalai(self):
        return sum((t.nilai for t in self.tolakan_lalai), Decimal("0"))

    def jumlah_tolakan(self, tahun):
        return sum((t.nilai for t in self.tolakan_untuk(tahun)), Decimal("0"))

    def hapus(self, tahun):
        """Buang tahun ini daripada kiraan sepenuhnya."""
        if tahun in self.tahun:
            self.tahun.remove(tahun)
        self.kasar.pop(tahun, None)
        self.tolakan_khas.pop(tahun, None)

    # ----------------------------------------------------------- semak

    def tahun_kosong(self):
        """Tahun yang dipilih tetapi pendapatannya belum diisi."""
        return [t for t in self.tahun if t not in self.kasar]

    def tahun_tanpa_nisab(self, cfg, jadual, hari_ini=None):
        """Tahun yang ada pendapatan tetapi nisabnya belum diisi.

        Ini halangan KERAS. Melangkaunya secara senyap akan menilai
        gaji tahun itu dengan nisab tahun lain, dan jumlah akhir jadi
        salah tanpa sesiapa perasan.
        """
        return [t for t in self.tahun
                if t in self.kasar
                and _nisab.untuk_tahun(cfg, jadual, t, hari_ini) is None]

    # ------------------------------------------------------------ kira

    def kira(self, cfg, jadual, kadar, hari_ini=None):
        """Pulang [(tahun, Hasil), ...] — satu Hasil bagi setiap tahun.

        Satu kaedah sahaja, iaitu kaedah yang dipilih. Menyimpan kedua-
        dua kaedah akan menjadikan "berapa perlu dibayar" kabur: dua
        angka untuk satu hutang.

        Tahun yang nisabnya belum diisi mesti ditapis dulu oleh pemanggil
        (`tahun_tanpa_nisab`) — di sini ia tidak boleh dikira langsung.

        Tahun yang pendapatannya belum diisi dilangkau: ia memang sah
        dikecualikan, dan skrin semak sudah menunjukkannya.
        """
        baris = []
        for t in self.tahun:
            if t not in self.kasar:
                continue
            nilai_nisab = _nisab.untuk_tahun(cfg, jadual, t, hari_ini)
            if nilai_nisab is None:
                continue
            kasar = self.kasar[t]
            if self.kaedah == "A":
                h = kira_kaedah_a(kasar, kadar, nilai_nisab)
            else:
                h = kira_kaedah_b(kasar, kadar, nilai_nisab, self.tolakan_untuk(t))
            baris.append((t, h))
        return baris


def jumlah(baris):
    """Jumlah zakat yang perlu dibayar.

    Hanya tahun yang cukup nisab. Menjumlahkan semua baris akan
    melebihkan hutang — tahun di bawah nisab tiada zakat, walaupun
    angkanya tetap dipaparkan (doktrin v1.2.1: angka sebenar, bukan sifar
    yang menyembunyikan perbezaan antara hampir cukup dan jauh di bawah).
    """
    return sum((h.zakat_setahun for _, h in baris if h.cukup_nisab),
               Decimal("0"))


def tahun_tak_cukup(baris):
    """Tahun yang dipaparkan tetapi dikecualikan daripada jumlah."""
    return [t for t, h in baris if not h.cukup_nisab]

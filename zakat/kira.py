"""Enjin kiraan zakat pendapatan.

Kaedah A — tanpa tolakan:
    zakat = pendapatan kasar setahun x kadar

Kaedah B — dengan tolakan:
    zakat = (pendapatan kasar - jumlah tolakan) x kadar

Kedua-dua kaedah dikenakan nisab. Kalau asas yang dikenakan zakat
kurang daripada nisab, zakat ialah RM 0.00.
"""

from decimal import Decimal, ROUND_HALF_UP


def sen(d):
    """Bundar ke 2 tempat perpuluhan."""
    return Decimal(str(d)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Tolakan:
    """Satu baris tolakan.

    nota       — versi pendek untuk kotak terminal, cth. '3 x 2,000'
    nota_penuh — versi panjang untuk teks print, cth. '3 orang x RM2,000'
    """

    def __init__(self, label, nilai, nota="", nota_penuh=None, pendek=None):
        self.label = label
        self.nilai = Decimal(str(nilai))
        self.nota = nota
        self.nota_penuh = nota if nota_penuh is None else nota_penuh
        # versi paling pendek — untuk gaya cetak sempit
        self.pendek = label if pendek is None else pendek

    def label_kotak(self):
        return f"{self.label} ({self.nota})" if self.nota else self.label

    def label_cetak(self):
        return f"{self.label} ({self.nota_penuh})" if self.nota_penuh else self.label

    def label_pendek(self):
        return self.pendek


class Hasil:
    """Keputusan satu kaedah kiraan."""

    def __init__(self, kaedah, pendapatan_kasar, kadar, nisab,
                 tolakan=None, sumber_kasar=""):
        self.kaedah = kaedah
        self.pendapatan_kasar = Decimal(str(pendapatan_kasar))
        self.sumber_kasar = sumber_kasar
        self.tolakan = tolakan or []
        self.kadar = Decimal(str(kadar))
        self.nisab = Decimal(str(nisab))

        self.jumlah_tolakan = sum((t.nilai for t in self.tolakan), Decimal("0"))
        self.kena_zakat = self.pendapatan_kasar - self.jumlah_tolakan
        if self.kena_zakat < 0:
            self.kena_zakat = Decimal("0")

        self.cukup_nisab = self.kena_zakat >= self.nisab
        if self.cukup_nisab:
            self.zakat_setahun = sen(self.kena_zakat * self.kadar / 100)
        else:
            self.zakat_setahun = Decimal("0.00")
        self.zakat_sebulan = sen(self.zakat_setahun / 12)

    def ringkas(self):
        """Bentuk boleh-simpan. Cukup lengkap untuk dibina semula."""
        return {
            "kaedah": self.kaedah,
            "pendapatan_kasar": str(sen(self.pendapatan_kasar)),
            "sumber_kasar": self.sumber_kasar,
            "tolakan": [
                {
                    "label": t.label,
                    "nota": t.nota,
                    "nota_penuh": t.nota_penuh,
                    "pendek": t.pendek,
                    "nilai": str(sen(t.nilai)),
                }
                for t in self.tolakan
            ],
            "jumlah_tolakan": str(sen(self.jumlah_tolakan)),
            "kena_zakat": str(sen(self.kena_zakat)),
            "kadar": str(self.kadar),
            "nisab": str(sen(self.nisab)),
            "cukup_nisab": self.cukup_nisab,
            "zakat_setahun": str(self.zakat_setahun),
            "zakat_sebulan": str(self.zakat_sebulan),
        }

    @classmethod
    def dari_rekod(cls, r):
        """Bina semula Hasil daripada rekod sejarah.

        Nilai yang tersimpan dipulihkan terus, TIDAK dikira semula — supaya
        cetakan semula sentiasa sama dengan cetakan asal, dan rekod lama
        (yang tak simpan butiran tolakan) tetap keluar jumlah yang betul.
        """
        tolak = [
            Tolakan(t["label"], t["nilai"], t.get("nota", ""),
                    t.get("nota_penuh"), t.get("pendek"))
            for t in r.get("tolakan", [])
        ]
        h = cls(
            r["kaedah"], r["pendapatan_kasar"], r["kadar"], r["nisab"],
            tolak, r.get("sumber_kasar", ""),
        )
        for kunci in ("jumlah_tolakan", "kena_zakat", "zakat_setahun",
                      "zakat_sebulan"):
            if kunci in r:
                setattr(h, kunci, Decimal(str(r[kunci])))
        if "cukup_nisab" in r:
            h.cukup_nisab = bool(r["cukup_nisab"])
        return h


def kira_kaedah_a(pendapatan_kasar, kadar, nisab, sumber_kasar=""):
    return Hasil("A", pendapatan_kasar, kadar, nisab, [], sumber_kasar)


def kira_kaedah_b(pendapatan_kasar, kadar, nisab, tolakan, sumber_kasar=""):
    return Hasil("B", pendapatan_kasar, kadar, nisab, tolakan, sumber_kasar)

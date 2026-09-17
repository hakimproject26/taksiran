# Taksiran Zakat Pendapatan

Kalkulator zakat pendapatan berasaskan terminal untuk Termux (Android).

Dua kaedah kiraan, dan boleh keluarkan teks siap untuk dihantar ke WhatsApp.

---

## Pasang dalam Termux

```bash
pkg install python
```

Salin folder `taksiran` ke telefon, kemudian:

```bash
cd ~/taksiran
python main.py
```

Tak perlu `pip install` apa-apa — guna pustaka standard Python sahaja.

### Shortcut (pilihan)

Supaya boleh taip `zakat` sahaja:

```bash
echo "alias zakat='python ~/taksiran/main.py'" >> ~/.bashrc
source ~/.bashrc
```

Untuk butang di skrin utama, letak skrip dalam `~/.shortcuts/`:

```bash
mkdir -p ~/.shortcuts
printf '#!/data/data/com.termux/files/usr/bin/bash\ncd ~/taksiran && python main.py\n' > ~/.shortcuts/zakat
chmod +x ~/.shortcuts/zakat
```

(Kena pasang app **Termux:Widget** untuk butang ini.)

Untuk butang **Print** boleh auto-salin ke clipboard, pasang Termux:API:

```bash
pkg install termux-api
```

---

## Cara guna

### 1. Daftar (pilihan)

Isi nama event, tarikh, dan tempat. Info ini akan naik pada setiap print.
Kalau tak diisi, print tetap keluar tanpa blok event.

### 2. Kadar & Tolakan

Semua nilai boleh diubah di sini. **Nisab mesti dikemas kini** ikut harga
emas semasa dan negeri masing-masing — nilai lalai hanyalah placeholder.

### 3. Tetapan — gaya output print

WhatsApp guna **font berkadar**, bukan monospace. Jadi penjajaran lajur
hanya kekal kalau teks dibalut dalam blok ` ``` `. Sebab itu ada lima gaya:

| Gaya | Rupa | Had lebar |
|---|---|---|
| **Monospace** | Dalam blok ` ``` `, lajur sejajar tepat. Lalai. | 34 |
| **Baris biasa** | `Label: nilai` + senarai bulet. | bebas |
| **Ringkas** | Nombor penting sahaja. | bebas |
| **Lajur bertitik** | Lajur bertitik `......` dalam blok ` ``` `. | 34 |
| **Kotak** | Bergaris `╔══╗`, dalam blok ` ``` `. | 30 |
| **Bertindan** | Label di atas, nilai di bawah. | 34 |

Fon monospace WhatsApp lebih lebar daripada fon biasa, jadi baris dalam
blok ` ``` ` mesti lebih pendek — kalau tidak ia berlanggar dinding tepi.
Empat gaya pertama dihadkan seperti dalam jadual. Label yang terlalu
panjang dipotong dengan `…`.

**Kotak** dihadkan lebih ketat (30) sebab aksara bingkai `═ ║` nampak
lebih lebar daripada aksara biasa dalam fon monospace WhatsApp.

**Bertindan** meletakkan setiap nilai di baris bawah labelnya, jadi ia
tak bergantung pada lebar lajur langsung — paling selamat kalau gaya
lain masih sentuh tepi. Ia paling panjang ke bawah.

**Baris biasa** dan **Ringkas** tidak dibalut ` ``` ` — WhatsApp bungkus
sendiri ikut perkataan, jadi ia tak pernah berlanggar tepi.

Setiap gaya ada **pratonton** — tuan nampak dulu sebelum simpan.

### README di dalam app

Menu **Tetapan ▸ [2] README** membuka catatan pembinaan app ini — sembilan
seksyen, dipaparkan satu demi satu. Ia bukan panduan penggunaan (panduan
itu fail yang sedang tuan baca ini), tetapi cerita bagaimana app ini
terbina: apa yang diminta, apa yang bertambah, apa yang silap, dan apa
yang masih tergantung.

Teksnya ada dalam `zakat/readme.py`.

### 4. Kira Zakat

**Kaedah A** — tanpa tolakan:

```
zakat = pendapatan kasar setahun × kadar
```

**Kaedah B** — dengan tolakan:

```
zakat = (pendapatan kasar − jumlah tolakan) × kadar
```

Kadar:

| Tahun | Kadar |
|---|---|
| Masihi | 2.577% (lalai) |
| Hijrah | 2.500% |

Tolakan dalam Kaedah B:

| Tolakan | Nilai |
|---|---|
| Diri sendiri | RM10,000 (tetap) |
| Isteri | RM4,000 seorang, maksimum 4 — **lelaki sahaja** |
| Anak | RM2,000 (lalai) atau RM1,000 seorang |
| KWSP | ikut input |
| Tabung Haji | ikut input |
| ILTAT | ikut input |

Bagi pembayar perempuan, tiada tolakan untuk suami.

Pendapatan kasar, KWSP, Tabung Haji dan ILTAT boleh diisi secara
**bulanan** (akan didarab 12) atau **tahunan** terus.

Pada langkah **Tahun**, tekan Enter sahaja untuk guna tahun semasa
(contoh 2026 untuk Masihi, atau tahun Hijrah anggaran). Taip tahun lain
kalau nak kiraan tahun lain.

Kedua-dua kaedah dikenakan nisab. Kalau asas yang dikenakan zakat kurang
daripada nisab, zakat ialah **RM 0.00**.

Kalau pilih Kaedah A, hasil menunjuk Kaedah A sahaja.
Kalau pilih Kaedah B, hasil menunjuk **kedua-dua** Kaedah A dan B.

### 5. Print

Tekan `P` pada skrin hasil. Boleh isi nama pembayar — kalau dibiarkan
kosong, print keluar tanpa nama. Teks siap disalin ke clipboard (kalau
`termux-api` dipasang), sedia untuk tampal ke WhatsApp.

**Setiap print auto-simpan ke sejarah** — termasuk nama pembayar dan event.

### 6. Sejarah Kiraan

Senarai 20 kiraan terkini. Taip **nombor rekod** untuk print semula.
Cetakan semula keluar penuh dengan pecahan tolakan asal, dan guna gaya
output yang sedang aktif.

Cetakan semula **tidak** menambah rekod baru ke sejarah.

---

## Struktur

```
taksiran/
├── main.py              menu dan aliran
├── zakat/
│   ├── ui.py            kotak, warna, input
│   ├── store.py         baca/tulis JSON
│   ├── kira.py          enjin kiraan
│   └── cetak.py         jana teks WhatsApp
└── data/                terhasil sendiri
    ├── config.json      kadar, nisab, tolakan
    ├── event.json       event aktif
    └── sejarah.json     rekod kiraan
```

Semua data dalam folder `data/` — backup dengan salin folder itu sahaja.

---

## Nota

Aplikasi ini alat bantu kiraan, bukan rujukan agama. Kadar, nisab dan
tolakan yang dibenarkan berbeza ikut negeri dan pandangan mazhab.
Sahkan dengan pihak zakat negeri masing-masing sebelum digunakan untuk
pembayaran sebenar.

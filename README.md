# Taksiran Zakat Pendapatan

**Versi 1.1.0** (17/09/2026)

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

Untuk semak versi yang sedang dipasang, tanpa buka menu:

```bash
python ~/taksiran/main.py --versi
```

Versi juga tertera di kaki menu utama dan dalam **Tetapan**.

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

### 7. Kemas Kini

Menu **[6] Kemas Kini** mengemas kini app dari dalam app sendiri — tak perlu
buka terminal dan taip `curl` lagi.

Ia hubungi pelayan, bandingkan nombor versi, muat turun, semak, dan pasang.
Lepas siap, app **mula semula sendiri** (kod baharu hanya berkuat kuasa
selepas proses dimulakan semula).

Selain menu itu, app juga **semak sendiri setiap kali dibuka**. Kalau ada
versi baharu, satu notis naik di menu utama. Semakan ini tidak melambatkan
app — ia berjalan di latar, dan menu naik serta-merta.

Sebelum menimpa apa-apa, kod versi semasa disimpan ke `.backup/`. Fail
`data/` tidak pernah disentuh.

**Kalau pelayan mati**, app jalan seperti biasa tanpa notis. Menu `[6]` akan
menunjuk mesej ralat dan cara hidupkan pelayan.

**Tetapan berkaitan:**

| Menu | Guna |
|---|---|
| `Tetapan ▸ [3]` | Tukar alamat pelayan kemas kini |
| `Tetapan ▸ [4]` | Hidup/matikan semakan automatik |

**Sisi pelayan.** Untuk menghasilkan fail pemasangan, jalankan:

```bash
bash ~/serve-zakat/bina.sh
```

Ia menghasilkan dua fail: `taksiran.tar.gz` (kod) dan `versi.json` (nombor
versi + nota). Kedua-duanya dibaca daripada `zakat/versi.py` yang sama,
jadi nombornya tak akan tak selaras.

Kemudian hidupkan pelayan:

```bash
cd ~/serve-zakat && python3 -m http.server 8000 --bind 0.0.0.0 --directory .
```

> **Amaran keselamatan.** Tiada pengesahan tandatangan. Sesiapa yang boleh
> mengawal pelayan itu boleh menghantar apa-apa kod, dan telefon akan
> menjalankannya. Untuk pelayan dalam rangkaian sendiri ini memadai. Kalau
> ia diletak di internet, ini lubang sebenar dan perlu difikir semula.

---

## Struktur

```
taksiran/
├── main.py              menu dan aliran
├── README.md            fail ini
├── CHANGELOG.md         sejarah versi
├── zakat/
│   ├── ui.py            kotak, warna, input
│   ├── store.py         baca/tulis JSON
│   ├── kira.py          enjin kiraan
│   ├── cetak.py         jana teks WhatsApp
│   ├── readme.py        catatan pembinaan
│   ├── kemas.py         enjin kemas kini
│   └── versi.py         nombor versi
├── data/                terhasil sendiri
│   ├── config.json      kadar, nisab, tolakan
│   ├── event.json       event aktif
│   └── sejarah.json     rekod kiraan
└── .backup/             kod versi lama, sebelum ditimpa
```

Semua data dalam folder `data/` — backup dengan salin folder itu sahaja.

`data/` sengaja **tidak** dimasukkan ke dalam git — ia menyimpan nama
pembayar dan rekod sebenar.

---

## Versi

Nombor versi ada dalam `zakat/versi.py`, dan setiap perubahan penting
dicatat dalam `CHANGELOG.md`.

- **MAJOR** naik bila sesuatu yang lama tak berfungsi lagi (contoh: satu
  feature dibuang)
- **MINOR** naik bila ada tambahan baharu (contoh: satu gaya cetakan baharu)
- **PATCH** naik bila baiki yang rosak sahaja (contoh: satu bug dibetulkan)

Sebelum naikkan nombor, tanya dahulu: **adakah pengguna terpaksa ubah cara
guna?** Kalau ya — MAJOR. Kalau tidak, tetapi ada benda baharu — MINOR.
Kalau sekadar membaiki — PATCH.

---

## Nota

Aplikasi ini alat bantu kiraan, bukan rujukan agama. Kadar, nisab dan
tolakan yang dibenarkan berbeza ikut negeri dan pandangan mazhab.
Sahkan dengan pihak zakat negeri masing-masing sebelum digunakan untuk
pembayaran sebenar.

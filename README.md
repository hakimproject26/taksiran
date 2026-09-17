# Taksiran Zakat Pendapatan

**Versi 2.0.0** (18/09/2026)

Kalkulator zakat pendapatan berasaskan terminal untuk Termux (Android).

Dua kaedah kiraan, kiraan qadha merentas banyak tahun, dan boleh
keluarkan teks siap untuk dihantar ke WhatsApp.

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

Menu utama dibahagi dua kumpulan:

```
  ── KIRAAN ─────────────────
  [1]  Kira Zakat
  [2]  Daftar
  [3]  Qadha Zakat
  [5]  Sejarah Kiraan

  ── APP ────────────────────
  [4]  Tetapan
  [6]  Kemas Kini
  [7]  Kadar & Tolakan
```

**KIRAAN** ialah kerja harian — mengira dan mencetak. **APP** ialah urusan
app itu sendiri — tetapan, dan mengemas kini dirinya.

> **Nombor menu berubah pada 2.0.0.** `[3]` dulu Kadar & Tolakan; sekarang
> ia Qadha Zakat. Kadar & Tolakan pindah ke `[7]`, dan masuk kumpulan APP
> sebab ia tetapan, bukan kerja harian.

### Daftar (pilihan) — `[2]`

Isi nama event, tarikh, dan tempat. Info ini akan naik pada setiap print.
Kalau tak diisi, print tetap keluar tanpa blok event.

### Kadar & Tolakan — `[7]`

Semua nilai boleh diubah di sini. **Nisab mesti dikemas kini** ikut harga
emas semasa dan negeri masing-masing — nilai lalai hanyalah placeholder.

#### Peringatan nisab

Nisab berubah ikut harga emas, dan ia menentukan sama ada zakat wajib
dibayar langsung. Kalau nilai dalam app terlalu tinggi, app akan berkata
*"tak cukup nisab"* sedangkan zakat sebenarnya wajib. Itu bukan sekadar
angka salah — ia boleh menyebabkan seseorang terlepas membayar.

Sebab itu app menyimpan tarikh nisab kali terakhir disahkan, dan
mengingatkan setiap **suku** — Januari, April, Julai, Oktober.

Amaran muncul di tiga tempat:

| Di mana | Bila |
|---|---|
| Menu utama | Kotak amaran bila suku baharu bermula |
| Skrin hasil | Satu baris kuning di bawah kiraan |
| Sebelum cetak | Boleh dibatalkan sebelum teks keluar |

Untuk membersihkan amaran: sahkan nisab negeri tuan, kemas kini **medan
`[3] Nisab`** dalam menu ini kalau ia berubah, kemudian tekan **[N]**
untuk tanda sudah disahkan. Nisab selalunya tidak berubah, jadi `[N]` ada
supaya tuan tak perlu menaip nilai yang sama semula.

Tarikh pengesahan terakhir tertera dalam kotak menu ini.

#### Nisab ikut tahun — `[T]`

Menu ini memaparkan nisab **tahun semasa** sahaja. Untuk tahun-tahun lain,
tekan `[T]` — senarai nisab 2015 hingga tahun semasa akan naik, dan tuan
boleh taip mana-mana tahun untuk mengisi atau mengubah nilainya.

Tahun yang belum diisi jelas kelihatan sebagai `(belum diisi)`. Kiraan
qadha **memerlukan** nisab tahun itu — ia tidak akan meneka.

Dua perkara yang berbeza berlaku di sini:

| Tahun | Disimpan ke | Kesan pada peringatan suku |
|---|---|---|
| Tahun semasa | `data/config.json` | Ditanda sudah disahkan semula |
| Tahun-tahun lalu | `data/nisab.json` | Tiada — peringatan itu mengenai nisab semasa |

Satu nilai sahaja bagi setiap tahun. Tiada salinan cermin antara kedua-
dua fail, supaya `[R] reset` tidak memadamkan senarai nisab tahun lalu.

> **App tidak mereka angka nisab.** Nisab berbeza ikut negeri dan harga
> emas, dan ia angka agama serta kewangan. Tuan atau pihak zakat yang
> menentukannya — app hanya menyimpan apa yang tuan isi.

**Cetakan WhatsApp sengaja tidak diberi amaran nisab.** Setiap gaya
cetakan ada had aksara yang ketat (30–34), dan baris tambahan akan
terpotong atau merosakkan susun atur. Amaran diberi dalam app sebelum
cetak — di situ ia masih boleh dibatalkan.

### Tetapan — gaya output print  `[4]`

WhatsApp guna **font berkadar**, bukan monospace. Jadi penjajaran lajur
hanya kekal kalau teks dibalut dalam blok ` ``` `. Sebab itu ada enam gaya:

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

#### Menu Tetapan

| Menu | Guna |
|---|---|
| `[1]` | Pilih gaya output print (dengan pratonton) |
| `[2]` | README — catatan pembinaan app ini |
| `[3]` | Sumber kemas kini — alamat pelayan |
| `[4]` | Semak kemas kini semasa buka: Ya / Tidak |
| `[5]` | Eksport data ke fail teks |

### README di dalam app

Menu **Tetapan ▸ [2] README** membuka catatan pembinaan app ini — sembilan
seksyen, dipaparkan satu demi satu. Ia bukan panduan penggunaan (panduan
itu fail yang sedang tuan baca ini), tetapi cerita bagaimana app ini
terbina: apa yang diminta, apa yang bertambah, apa yang silap, dan apa
yang masih tergantung.

Teksnya ada dalam `zakat/readme.py`.

### Kira Zakat — `[1]`

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

#### Nisab dinilai pada pendapatan kasar

Nisab dikenakan pada **pendapatan kasar** — asas Kaedah A — bukan pada
asas selepas tolakan. Ia dinilai sekali sahaja, dan keputusan yang sama
dipakai untuk kedua-dua kaedah.

Ini penting pada satu keadaan: kasar sudah cukup nisab, tetapi asas
Kaedah B jatuh bawah nisab selepas tolakan. Dalam keadaan itu **zakat
tetap wajib** — nisab sudah dipenuhi oleh pendapatan itu sendiri. Kalau
nisab dinilai per kaedah, app akan berkata *"tak cukup nisab"* sedangkan
zakat sebenarnya wajib, dan pembayar terlepas membayar.

Sebaliknya, kalau kasar sendiri belum cukup nisab, maka tiada zakat
wajib — walau kaedah mana dipilih.

Angka zakat dipaparkan dalam kedua-dua keadaan, bukan dikosongkan. Satu
nota menyatakan sama ada ia wajib. Kalau angka dikosongkan jadi RM 0.00,
kiraan yang hampir cukup nisab kelihatan sama dengan kiraan yang jauh di
bawahnya.

| Keadaan | Wajib? | Contoh |
|---|---|---|
| Kasar ≥ nisab, asas B ≥ nisab | Ya | biasa |
| Kasar ≥ nisab, asas B < nisab | **Ya** | kasar 40,000 / nisab 34,000 / asas B 5,600 |
| Kasar < nisab | Tidak | kasar 30,000 / nisab 34,000 |

Kes kedua itulah yang dibetulkan pada 1.2.1.

Kalau pilih Kaedah A, hasil menunjuk Kaedah A sahaja.
Kalau pilih Kaedah B, hasil menunjuk **kedua-dua** Kaedah A dan B.

### Print

Tekan `P` pada skrin hasil. Boleh isi nama pembayar — kalau dibiarkan
kosong, print keluar tanpa nama. Teks siap disalin ke clipboard (kalau
`termux-api` dipasang), sedia untuk tampal ke WhatsApp.

**Setiap print auto-simpan ke sejarah** — termasuk nama pembayar dan event.

### Qadha Zakat — `[3]`

Untuk kes tertunggak: seseorang tidak tahu pendapatannya sudah melepasi
nisab, dan baru sekarang datang dengan gaji setiap tahun untuk dikira.

`[1] Kiraan Bundle` mengira beberapa tahun sekali gus dan memberi **satu
jumlah** yang perlu dibayar.

**Kenapa ia berasingan daripada kiraan biasa.** Nisab berubah setiap
tahun — ia ikut harga emas. Kiraan biasa memakai satu nisab, iaitu nisab
hari ini. Kalau gaji 2015 dinilai dengan nisab 2026, keputusannya salah
pada kedua-dua hujung:

| Keadaan | Kalau nisab hari ini dipakai | Yang sepatutnya |
|---|---|---|
| Nisab 2015 lebih rendah | Gaji 2015 nampak tak cukup nisab | Wajib — orang terlepas bayar |
| Nisab 2015 lebih tinggi | Gaji 2015 nampak cukup nisab | Tidak wajib — orang bayar lebih |

Sebab itu kiraan bundle menilai **setiap tahun dengan nisab tahun itu**,
dan ia berhenti kalau nisab mana-mana tahun belum diisi.

**Aliran soalan:**

```
kaedah A/B  →  tolakan (B sahaja, sekali)  →  kadar  →
input bulanan/tahunan (sekali)  →  pilih tahun  →  isi gaji  →
semak  →  kira
```

- **Tolakan** ditanya **sekali** dan dipakai semua tahun. Ia boleh diubah
  bagi tahun tertentu sahaja — tekan `[T]` dalam senarai tahun.
- **Input bulanan atau tahunan** juga ditanya sekali. Kalau pilih bulanan,
  senarai tahun menunjukkan `RM 3,000 × 12 = RM 36,000` supaya jelas apa
  yang masuk ke dalam kiraan.
- **Pemilihan tahun** ada dua cara: `[1] Julat` (2018 hingga 2021) atau
  `[2] Manual` (taip tahun satu-satu). Dalam mod manual, taip tahun yang
  sudah ada akan **membuangnya** — supaya tersilap pun boleh dibaiki.

**Paparan semak** naik sebelum kiraan berjalan. Setiap tahun berdiri
sendiri, dan jumlah tolakan dipaparkan, supaya satu angka yang tersalah
taip kelihatan sebelum ia menjadi sebahagian daripada jumlah besar.

Tahun yang dipilih tetapi belum diisi akan **dilangkau**, dan ia
dinyatakan dalam skrin semak. Tahun yang **nisabnya** belum diisi pula
menghalang kiraan — bukan dilangkau secara senyap.

**Cetakan qadha** lain bentuknya daripada cetakan biasa: satu jadual per
tahun, satu jumlah di bawahnya.

```
QADHA ZAKAT — RINGKASAN
Tahun: 2015 – 2026 (Masihi)
Kadar: 2.577%
Kaedah: B (dengan tolakan)

Semua nilai dalam RM,
dibundarkan ke ringgit terdekat.
─────────────────────────────────
TAHUN     KASAR    NISAB    ZAKAT
─────────────────────────────────
2015     36,000   13,644      928
...
Tahun tak cukup nisab: 2018
  (dikecualikan dari jumlah)
Jumlah zakat        RM 25,893
```

Baris kepala dipagari garis atas dan bawah. Ini **pengganti bold**: di
dalam blok monospace WhatsApp, `*TAHUN*` tidak menjadi tebal — asterisk
keluar sebagai aksara biasa, dan setiap sel bertambah dua aksara sehingga
penjajaran runtuh. Garis tidak menambah lebar, jadi had 34 aksara kekal.

Tahun di bawah nisab **tetap dipaparkan dengan angkanya** (doktrin yang
sama seperti 1.2.1 — angka sebenar, bukan RM 0.00), tetapi ia
**dikecualikan daripada jumlah**, dan nota itu diletak betul-betul di
sebelah jumlah supaya ketak-tambahan itu dijelaskan di tempat ia
disedari.

Rekod qadha masuk ke sejarah seperti biasa, tetapi dipaparkan sebagai
`QADHA 2015 – 2026   RM 25,893` — bukan satu blok bagi setiap tahun.

### Sejarah Kiraan — `[5]`

Senarai 20 kiraan terkini. Taip **nombor rekod** untuk print semula.
Cetakan semula keluar penuh dengan pecahan tolakan asal, dan guna gaya
output yang sedang aktif.

Cetakan semula **tidak** menambah rekod baru ke sejarah.

### Kemas Kini — `[6]`

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

### Eksport data — `Tetapan ▸ [5]`

`Tetapan ▸ [5] Eksport data` menulis **semua** tetapan, event dan rekod
sejarah ke satu fail teks yang boleh dibaca manusia — bukan JSON mentah,
supaya tuan boleh buka dan sahkan isinya sendiri.

Fail ditulis ke folder utama Termux (`$HOME`), **bukan** dalam folder app.
Ini disengajakan: kalau app dipasang semula atau folder app dipadam, fail
eksport masih selamat.

```
~/taksiran-eksport-20260917-2320.txt
```

Salinannya juga dimasukkan ke clipboard, jadi boleh terus tampal ke e-mel
atau nota.

> **Fail ini mengandungi nama pembayar sebenar.** Simpan di tempat yang
> selamat. Sebab itulah `data/` dan fail eksport tidak pernah masuk git.

**Import tidak disediakan.** Buat masa ini eksport untuk backup dan
rujukan sahaja. Kalau tuan perlukan import semula, beritahu.

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
│   ├── qadha.py         enjin kiraan qadha (nisab ikut tahun)
│   ├── cetak.py         jana teks WhatsApp
│   ├── readme.py        catatan pembinaan
│   ├── kemas.py         enjin kemas kini
│   ├── nisab.py         peringatan suku + nisab ikut tahun
│   ├── eksport.py       eksport data ke teks
│   └── versi.py         nombor versi
├── data/                terhasil sendiri
│   ├── config.json      kadar, nisab tahun semasa, tolakan
│   ├── nisab.json       nisab tahun-tahun lalu
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

# Taksiran Zakat Pendapatan

**Versi 3.1.0** (20/09/2026)

Kalkulator zakat pendapatan berasaskan terminal untuk Termux (Android).

Dua kaedah kiraan, kiraan qadha merentas banyak tahun, dan boleh
keluarkan teks siap untuk dihantar ke WhatsApp.

---

## Pasang dalam Termux

Cara biasa — satu baris, dan ia memasang Aether sekali:

```bash
curl -fsSL http://100.78.29.8:8000/pasang.sh | bash
```

Kalau pelayan di alamat lain, hulur sebagai argumen:

```bash
curl -fsSL http://<alamat>:8000/pasang.sh | bash -s http://<alamat>:8000
```

Tak perlu `pip install` apa-apa — guna pustaka standard Python sahaja.

Selepas ini, buka app dengan menaip:

```bash
zakat
```

### Pasang secara manual (kalau tiada pelayan)

```bash
pkg install python
```

Salin folder `taksiran` ke telefon, kemudian:

```bash
cd ~/taksiran
python main.py
```

Cara ini **tidak** memasang Aether, jadi tiada pemeriksaan dan tiada menolak.
Ia berguna untuk membetulkan sesuatu, bukan untuk kegunaan harian.

Untuk semak versi yang sedang dipasang, tanpa buka menu:

```bash
python ~/taksiran/main.py --versi
```

Versi juga tertera di kaki menu utama dan dalam **Tetapan**.

### Shortcut (pilihan)

`pasang.sh` sudah menulis alias ini sendiri, dan ia menulisnya melalui
Aether:

```bash
alias zakat='python ~/.hkm/aether.py taksiran'
```

Untuk butang di skrin utama, letak skrip dalam `~/.shortcuts/`:

```bash
mkdir -p ~/.shortcuts
printf '#!/data/data/com.termux/files/usr/bin/bash\nexec python ~/.hkm/aether.py taksiran\n' > ~/.shortcuts/zakat
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

**Cetakan qadha** lain bentuknya daripada cetakan biasa: satu blok kecil
setiap tahun, satu jumlah di bawahnya.

```
QADHA ZAKAT — RINGKASAN
Tahun: 2015 – 2026 (Masihi)
Kadar: 2.577%
Kaedah: B (dengan tolakan)

Semua nilai dalam RM.

2015  (nisab RM 13,644.28)
kasar  36,000.00 | zakat   927.72

...
Tahun tak cukup nisab: 2018
  (dikecualikan dari jumlah)
Jumlah zakat        RM 25,893.42
```

Setiap tahun mengambil **tiga baris** — tahun + nisabnya, kasar + zakat,
dan satu baris kosong sebagai pemisah. Ini bukan pilihan estetika: tiga
lajur wang yang membawa sen tidak muat dalam satu baris tanpa lajur
bercantum, dan lajur bercantum membaca sebagai satu nombor.

**Angka tepat sampai sen — tiada pembundaran ke ringgit.** Sebabnya juga
bukan estetika: jumlah di bawah dikira daripada nilai yang sama, jadi
kalau setiap tahun digenapkan dahulu, jumlah itu tidak akan berjumlah
dengan baris di atasnya, dan sesiapa yang menyemak dengan kalkulator
akan nampak seolah-olah ada angka hilang. Zakat itu sendiri tetap
digenapkan ke **sen terdekat** — 2.577% daripada 36,000 memang menghasilkan
pecahan sen, dan tiada cara menulisnya tanpa memilih.

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

Sebelum menimpa apa-apa, kod versi semasa disimpan ke `~/.taksiran/backup/`.
Fail data tidak pernah disentuh.

> **Satu langkah selepas kemas kini pertama ke v3.1.0.** Menu `[6]` tidak
> boleh menghidupkan Aether sendiri — ia menulis ke `~/.hkm/` dan mengubah
> baris `alias` dalam `.bashrc`, dan itu di luar folder app. Jadi selepas
> kemas kini, jalankan sekali:
>
> ```bash
> curl -fsSL http://100.78.29.8:8000/pasang.sh | bash
> ```
>
> App akan memberitahu tuan sendiri kalau langkah ini belum dibuat. Ia tidak
> berdiam, kerana app yang kelihatan dilindungi sedangkan tidak adalah lebih
> buruk daripada app yang terang-terang tidak.

Arkib itu membawa **MANIFEST** — senarai setiap fail yang dihantar, dengan
SHA-256 setiap satu — dan MANIFEST itu ditandatangani. Ia diperiksa
**sebelum** apa-apa diekstrak, dan sekali lagi **selepas** dipasang. Sebabnya
ada di bawah, di bahagian Aether: satu MANIFEST yang basi akan membuatkan
Aether menolak app itu pada setiap kali dibuka, dan alias `zakat` mati.

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

Ia menghasilkan **tiga** fail: `taksiran.tar.gz` (kod), `taksiran.tar.gz.sig`
(tandatangan bagi arkib itu), dan `versi.json` (nombor versi + nota).
`versi.json` dibaca daripada `zakat/versi.py` yang sama yang app guna, jadi
nombornya tak akan tak selaras.

Skrip ini **menanya frasa laluan kunci tandatangan**, jadi ia tidak boleh
dijalankan tanpa tuan hadir. Ia juga membatalkan binaan kalau pengesah
Python tidak bersetuju dengan openssl, atau kalau kunci dalam `pasang.sh`
tidak sama dengan kunci dalam app.

Kemudian hidupkan pelayan:

```bash
cd ~/serve-zakat && python3 -m http.server 8000 --bind 0.0.0.0 --directory .
```

#### Kunci tandatangan

Arkib kemas kini mesti ditandatangani, atau telefon akan menolaknya. Kunci
rawak dijana sekali sahaja:

```bash
cd ~/taksiran
python3 alat/tanda.py jana
```

Ia menanya frasa laluan (openssl yang menanya, jadi frasa itu tidak pernah
melalui argumen) dan menyimpan kunci rahsia di `~/.taksiran-kunci/kunci.pem`.
openssl menanya **tiga kali** — dua kali untuk menetapkan frasa, sekali lagi
untuk membaca kunci awam. Itu memang sepatutnya; kunci rahsia tidak pernah
wujud dalam bentuk tidak bersulit, walaupun seketika.
Kunci awamnya disimpan di sebelahnya dalam fail biasa — ia memang maklumat
awam, dan menyimpannya begini bermakna `bina.sh` menanya frasa laluan
**sekali** sahaja, bukan bagi setiap arahan.

Ia kemudian mencetak baris untuk ditampal ke dalam `KUNCI` di
`zakat/tandatangan.py`. Satu lagi arahan mencetak PEM untuk `pasang.sh`:

```bash
python3 alat/tanda.py pem     # tampal output ini ke dalam pasang.sh
```

Untuk memastikan kedua-duanya benar-benar padan — app dan `pasang.sh`:

```bash
python3 alat/tanda.py padan ~/serve-zakat/pasang.sh
```

`bina.sh` menjalankan pemeriksaan itu sendiri pada setiap binaan, dan
membatalkan binaan kalau kuncinya menyimpang. Sebabnya: kalau ia menyimpang,
arkib yang **sah** akan ditolak pada pemasangan pertama — iaitu kepada orang
yang belum ada app untuk membetulkannya.

> **Simpan frasa laluan itu.** Kalau ia hilang, kunci itu hilang, dan kunci
> baharu hanya boleh sampai ke telefon melalui kemas kini yang
> ditandatangani oleh kunci **lama**. Itu lingkaran mati. `KUNCI` ialah
> senarai supaya putaran kunci mungkin — tambah kunci baharu, terbitkan,
> kemudian buang yang lama — tetapi itu mesti dirancang **sebelum** kunci
> lama hilang, bukan selepas.

**Folder `alat/` tidak pernah dihantar ke telefon.** Ia memegang kod
menandatangani; sesiapa yang membongkar app itu boleh menggunakannya untuk
menandatangani arkib sendiri. `bina.sh` memeriksa pengecualian itu
benar-benar berlaku pada setiap binaan, dan membatalkan binaan kalau tidak.

#### Kalau kemas kini ditolak

Skrin kegagalan memaparkan cap jari kunci yang app itu percaya. Bandingkan
dengan `python3 alat/tanda.py cap`. Kalau ia berbeza, arkib itu ditandatangani
dengan kunci lain. Kalau ia sama, arkib itu memang rosak atau diubah.

Untuk memeriksa dengan tangan, tanpa app:

```bash
cd ~/serve-zakat
python3 ~/taksiran/alat/tanda.py sahkan taksiran.tar.gz
```

**Had yang mesti diketahui.** Pemeriksaan tandatangan melindungi daripada
**arkib yang ditukar**. Ia tidak melindungi daripada pelayan yang diceroboh
sepenuhnya semasa **pemasangan pertama**, kerana pada masa itu `pasang.sh`
sendiri datang dari pelayan yang sama — penyerang boleh menukar kedua-duanya
sekali gus. Sehingga `pasang.sh` dihoskan di tempat lain, perlindungan itu
hanya separa. Kunci tandatangan juga satu titik kegagalan: kalau ia dicuri
bersama frasa laluannya, penyerang boleh menandatangani kod.

### Eksport data — `Tetapan ▸ [5]`

`Tetapan ▸ [5] Eksport data` menulis **semua** tetapan, event dan rekod
sejarah ke satu fail teks yang boleh dibaca manusia — bukan JSON mentah,
supaya tuan boleh buka dan sahkan isinya sendiri.

Fail ditulis ke folder utama Termux (`$HOME`), **bukan** dalam folder app.
Ini disengajakan, dan sejak v3.1.0 ia juga **perlu**: Aether memeriksa
setiap fail dalam folder app, jadi fail eksport yang ditulis ke dalamnya
akan membuatkan app menolak dirinya sendiri selepas setiap eksport.

```
~/taksiran-eksport-20260917-2320.txt
```

Salinannya juga dimasukkan ke clipboard, jadi boleh terus tampal ke e-mel
atau nota.

> **Fail ini mengandungi nama pembayar sebenar.** Simpan di tempat yang
> selamat. Sebab itulah `~/.taksiran/` dan fail eksport tidak pernah masuk
> git.

**Import tidak disediakan.** Buat masa ini eksport untuk backup dan
rujukan sahaja. Kalau tuan perlukan import semula, beritahu.

---

## Aether — polis dalam app

Tandatangan di atas memeriksa **arkib semasa ia dimuat turun**. Selepas arkib
itu diekstrak, tiada apa-apa lagi yang diperiksa. Sesiapa yang boleh menulis
ke folder app — skrip lain, atau akses terus kepada telefon — boleh mengubah
`zakat/kira.py` dan app itu akan menjalankannya tanpa satu pun isyarat.

Aether menutup jurang itu. Ia menyemak **apa yang ada di cakera sekarang**,
setiap kali app dibuka, dan **Aether yang membuka app** — bukan app yang
memanggil Aether. Itu penting: app yang memanggil polis boleh melangkau
panggilan itu dengan membuang satu baris.

Ia dipasang di `~/.hkm/aether.py`, **di luar** folder app. Alat pembaikan
tidak boleh tinggal di dalam benda yang ia baiki: kalau folder app rosak,
`~/.hkm/aether.py` masih ada untuk menjalankannya.

### Apa yang diperiksa setiap kali `zakat` ditaip

1. Baca `MANIFEST` dan `MANIFEST.sig`
2. Sahkan tandatangan guna kunci tersemat — gagal = `TANDA_TIDAK_SAH`
3. Banding cap jari kunci dengan yang terakhir dilihat — `KUNCI_BAHARU`
4. Versi dalam MANIFEST lebih rendah daripada yang terakhir dilihat — `TURUN_VERSI`
5. Kira SHA-256 setiap fail tersenarai — tak padan = `MANIFEST_BERUBAH`
6. Kesan fail **tambahan**, dan tolak apa-apa yang bukan fail biasa
7. Semua lulus → app dibuka

Mana-mana kegagalan: **app tidak dibuka.** Tiada "teruskan juga".

### Kalau ia menolak, adakah app terkunci?

**Tidak.** Aether ialah **launcher**, bukan kurungan. Ia menolak untuk
**membuka** app; ia tidak menyentuh app itu sendiri. Tiada apa-apa di dalam
app memanggil Aether, jadi laluan terus sentiasa terbuka:

```bash
python ~/taksiran/main.py
```

Itu termasuk menu `[6]` Kemas Kini. Jadi walaupun pokok itu ditolak, tuan
masih boleh mengemas kini dari dalam app — dan `~/.hkm/aether.py --baiki`
tidak memerlukan app itu langsung, kerana ia tinggal di luar pokok.

Yang mati ialah **alias `zakat`**. Itu kemudahan yang hilang, bukan telefon
yang rosak. Tetapi ia cukup mengganggu, jadi ia tetap dianggap kerosakan
yang mesti dibaiki, bukan sesuatu untuk dibiar.

### Bila ia menolak

```bash
python ~/.hkm/aether.py --alert      # apa yang dicatat, dan bila
python ~/.hkm/aether.py --baiki taksiran   # muat turun semula dan pasang semula
```

`--baiki` mengambil semula daripada saluran bertandatangan. Ia **bukan**
pemulihan automatik dan ia tidak menyentuh `~/.taksiran/data/` — data tuan
tidak pernah menjadi sebahagian daripada soal ini.

Kalau app ditolak kerana ada fail yang bukan sebahagian daripada pokok
bertandatangan, `--baiki` membuang fail itu. Ia selamat kerana folder app
ialah **kod sahaja** sejak v3.1.0; tiada data pengguna di dalamnya.

### Had yang mesti diketahui — dan ia nyata

**Termux ialah satu app dengan satu UID.** Aether, app, dan sesiapa yang
boleh menulis ke telefon berkongsi keistimewaan yang sama. Aether bukan polis
yang berdiri di luar rumah; ia polis yang tinggal di dalam rumah yang sama.

Yang kita dapat bukan **halangan**, tetapi **jejak**. Setiap penolakan
dicatat dalam `~/.hkm/alert.jsonl` — app, kod alert, masa, versi, dan laluan
kod. Rekod-rekod itu dirantai dengan hash (`seq`, `prev_hash`, `hash`), jadi
memotong atau menyuntingnya meninggalkan bukti. Rekod itu **tidak pernah**
mengandungi nama pembayar, rekod kiraan, atau isi fail.

Harga privasi yang mesti ditulis, bukan disimpan dalam kepala: **cap masa
mendedahkan corak penggunaan.** Itu kos sebenar daripada janji "tiada data
pengguna".

**Aether tidak boleh menyemak dirinya sendiri.** Setiap fail yang boleh
dibandingkan dengan dirinya boleh ditulis oleh benda yang ia pertahankan.
`chmod 500` boleh dipulihkan oleh UID yang sama. Yang tinggal hanyalah
tripwire, dan Balai yang mengesahkannya kemudian. Aether **mengesan**; ia
tidak **menghalang**.

**Ia bukan sandbox.** `sitecustomize.py` dan fail `.pth` diimport sebelum
baris pertama `aether.py` berjalan. Sesiapa yang menaip
`python ~/taksiran/main.py` terus melangkau Aether sepenuhnya.

**Ada tetingkap masa.** Aether hash, kemudian menjalankan; penyerang dengan
UID yang sama boleh menukar fail dalam tetingkap itu. Tiada keatoman di sini.

**Kalau `--baiki` tidak menolong** — contohnya kalau kunci itu sendiri
tertukar, atau pelayan tidak dapat dihubungi — pasang semula terus:

```bash
curl -fsSL http://100.78.29.8:8000/pasang.sh | bash
```

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
│   ├── manifes.py       penghurai MANIFEST (sebelum ekstrak)
│   ├── akar.py          pindahkan data keluar folder app
│   ├── nisab.py         peringatan suku + nisab ikut tahun
│   ├── eksport.py       eksport data ke teks
│   └── versi.py         nombor versi
└── aether/              salinan launcher (dipasang ke ~/.hkm/)
```

Data **tidak** tinggal di sini lagi. Sejak v3.1.0 ia di luar folder app:

```
~/.taksiran/
├── data/
│   ├── config.json      kadar, nisab tahun semasa, tolakan
│   ├── nisab.json       nisab tahun-tahun lalu
│   ├── event.json       event aktif
│   └── sejarah.json     rekod kiraan
└── backup/              kod versi lama, sebelum ditimpa
```

Backup dengan salin `~/.taksiran/` sahaja.

Ini bukan kekemasan. Aether (di bawah) memeriksa **setiap fail** dalam folder
app terhadap senarai bertandatangan, jadi apa-apa yang app tulis sendiri ke
dalam folder itu akan kelihatan seperti pengubahsuaian — dan app akan menolak
dirinya sendiri. Memisahkan kod daripada data menjadikan folder app **kod
sahaja**, dan itu sifat yang boleh dituntut, bukan diharap.

Folder `~/.taksiran/` sengaja **tidak** dimasukkan ke dalam git — ia menyimpan
nama pembayar dan rekod sebenar.

Pemindahan berlaku sendiri pada kali pertama app dibuka selepas kemas kini:
folder lama dipindahkan, bukan disalin, dan kalau pemindahan gagal app
berhenti dengan ayat yang jelas daripada mula dengan data kosong.

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

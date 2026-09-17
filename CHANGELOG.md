# Changelog

Semua perubahan penting pada app ini dicatat di sini.

Format nombor versi: `MAJOR.MINOR.PATCH`

- **MAJOR** — sesuatu yang lama tak berfungsi lagi; pengguna terpaksa ubah cara guna
- **MINOR** — ada tambahan baharu; yang lama masih jalan
- **PATCH** — baiki yang rosak sahaja

Ukurannya bukan berapa banyak kerja, tapi berapa besar kesannya pada pengguna.

---

## [2.0.1] — 18/09/2026

Baris kepala jadual qadha dipagari garis atas dan bawah.

**Dibaiki:**

- **Baris kepala jadual qadha tidak dapat dibezakan daripada baris
  data.** `TAHUN KASAR NISAB ZAKAT` kelihatan sama seperti `2015 36,000
  13,644 928` — mata terpaksa berhenti dan mengira. Ia kini dipagari
  garis di atas dan di bawah

**Sengaja tidak dibuat: bold.** Di dalam blok monospace WhatsApp,
`*TAHUN*` **tidak** menjadi tebal — asterisk keluar sebagai aksara
biasa, dan setiap sel bertambah dua aksara sehingga penjajaran runtuh.
Garis tidak menambah lebar, jadi had 34 aksara kekal. Kalau tuan mahu
kontras lebih kuat, `═` boleh gantikan `─` pada baris kepala — beritahu.

**Nota versi:** ini PATCH, bukan MINOR — tiada keupayaan baharu dan
tiada cara guna yang berubah. Kalau tuan rasa ia layak MINOR, beritahu.

**Nota:** kenapa bukan 2.0.0? Versi 2.0.0 sudah pun dipasang di fon
sebelum perubahan ini. Melabelkannya semula 2.0.0 bermakna dua kod
berbeza berkongsi satu nombor, dan `kemas.semak()` akan berkata "sudah
terkini" — perubahan itu takkan sampai ke fon langsung.

---

## [2.0.0] — 18/09/2026

Qadha Zakat — kira zakat tertunggak merentas banyak tahun, dengan nisab
setiap tahun.

**Ditambah:**

- **Menu [3] Qadha Zakat ▸ [1] Kiraan Bundle** — kira beberapa tahun
  sekali gus, dan dapatkan satu jumlah yang perlu dibayar. Boleh pilih
  Kaedah A atau B, seperti kiraan biasa
- **Nisab ikut tahun.** Setiap tahun dinilai dengan nisab TAHUN ITU,
  bukan dengan nisab hari ini. Ini penting: harga emas berubah, jadi
  gaji 2015 yang dinilai dengan nisab 2026 akan salah pada kedua-dua
  hujungnya — tahun lama nampak tak wajib padahal wajib, dan tahun baru
  nampak wajib lebih awal daripada sepatutnya
- **`[7] Kadar & Tolakan ▸ [T]`** — senarai nisab 2015 hingga tahun
  semasa. Taip tahun untuk isi atau ubah. Tahun kosong jelas kelihatan
- Pemilihan tahun dalam bundle: **[1] Julat** (dari tahun ke tahun) atau
  **[2] Manual** (taip tahun satu-satu; taip tahun yang sudah ada akan
  membuangnya)
- **Paparan semak** sebelum kiraan dijalankan — setiap tahun berdiri
  sendiri, jadi angka yang tersalah taip kelihatan sebelum ia menjadi
  sebahagian daripada jumlah besar
- Tolakan diisi **sekali**, dipakai semua tahun; boleh diubah bagi tahun
  tertentu sahaja
- Cetakan qadha: satu jadual per tahun + jumlah keseluruhan, dengan
  baris kepala dipagari garis atas dan bawah

**Berubah — inilah sebabnya MAJOR:**

- **Menu utama bernombor semula.** `[3]` sekarang Qadha Zakat, dan
  Kadar & Tolakan pindah ke `[7]`. Kalau tuan biasa menekan `[3]` untuk
  membuka Kadar & Tolakan, ia kini membawa ke skrin yang berbeza

**Tidak berubah:**

- Rekod sejarah lama tiada penanda jenis, jadi ia tetap dianggap kiraan
  biasa — cetakan semulanya sama seperti asalnya
- `data/config.json` dan `data/sejarah.json` kekal boleh dibaca

**Fail baharu:** `data/nisab.json` — nisab bagi tahun-tahun lalu. Tahun
semasa kekal dalam `data/config.json` seperti biasa; tiada cermin antara
keduanya, supaya `[R] reset` tak memadamkan jadual tahun. Fail ini masuk
ke dalam eksport data.

**Nota:** tahun lain **kosong** — app tidak mereka angka nisab. Ia angka
agama dan kewangan yang berbeza ikut negeri dan harga emas, jadi ia
mesti datang daripada tuan atau pihak zakat.

---

## [1.2.1] — 17/09/2026

Nisab dinilai pada pendapatan kasar, bukan pada asas selepas tolakan.

**Dibaiki:**

- **Zakat dikatakan tak wajib sedangkan ia wajib.** Sebelum ini nisab
  dinilai berasingan bagi setiap kaedah. Akibatnya, apabila pendapatan
  kasar sudah cukup nisab tetapi asas Kaedah B jatuh bawah nisab selepas
  tolakan, app berkata *"tak cukup nisab — RM 0.00"* dan pembayar
  terlepas membayar zakat yang sebenarnya wajib. Sekarang nisab dinilai
  **sekali**, pada pendapatan kasar (asas Kaedah A), dan keputusan yang
  sama diberi kepada kedua-dua kaedah
- **Angka zakat dipaparkan walaupun tak cukup nisab.** Dulu hasilnya
  dikosongkan jadi RM 0.00. Sekarang angka sebenar keluar, dan satu nota
  menyatakan sama ada ia wajib — supaya kiraan yang hampir cukup nisab
  tidak kelihatan sama dengan kiraan yang jauh di bawahnya
- Nota "tak cukup nisab" keluar **sekali sahaja** bagi seluruh cetakan,
  dan tidak pernah keluar semata-mata sebab Kaedah B jatuh bawah nisab

**Tidak berubah:** rekod sejarah lama dicetak semula tepat seperti
asalnya, termasuk bendera nisab yang disimpan mengikut kaedah masing-
masing. Cetakan semula tidak senyap-senyap berubah.

**Nota versi:** ini PATCH, bukan MINOR — tiada keupayaan baharu dan tiada
cara guna yang berubah, cuma membetulkan keputusan yang salah. Kalau tuan
rasa perubahan angka ini cukup besar untuk dilabel MINOR, beritahu.

---

## [1.2.0] — 17/09/2026

Peringatan nisab, eksport data, dan menu utama yang tersusun.

**Ditambah:**

- **Peringatan nisab setiap suku** — Januari, April, Julai, Oktober. App
  menyimpan tarikh nisab kali terakhir disahkan, dan mengingatkan apabila
  suku baharu bermula
- Amaran nisab muncul di **menu utama**, di **skrin hasil**, dan sekali lagi
  **sebelum cetakan keluar** — di situ ia boleh dibatalkan
- `[3] Kadar & Tolakan ▸ [N]` — tanda nisab sudah disahkan tanpa perlu
  menaip nilai semula, kerana nisab selalunya tidak berubah
- **`Tetapan ▸ [5] Eksport data`** — tulis semua tetapan, event dan rekod
  sejarah ke satu fail teks dalam `$HOME` (bukan dalam folder app, supaya ia
  terselamat walau app dipasang semula). Salinannya juga masuk clipboard
- Menu utama dibahagi dua kumpulan: **KIRAAN** (1, 2, 3, 5) dan
  **APP** (4, 6). Nombornya tidak berubah

**Dibaiki:**

- **Kotak pecah bila teks terlalu panjang.** Satu nama event yang panjang
  sudah cukup untuk menembus dinding kotak — pepijat ini sudah ada sejak
  awal, bukan daripada perubahan ini. `ui.kotak()` sekarang membalut teks

**Sengaja tidak dibuat:** cetakan WhatsApp kekal tanpa amaran nisab. Setiap
gaya cetakan ada had aksara yang ketat (30–34), dan baris tambahan akan
terpotong atau merosakkan susun atur. Amaran diberi dalam app sebelum cetak
— di situ ia masih boleh dibatalkan. Kalau tuan mahu ia masuk ke cetakan
juga, beritahu.

---

## [1.1.0] — 17/09/2026

Kemas kini dari dalam app. Tuan tak perlu buka terminal dan taip `curl` lagi.

**Ditambah:**

- Menu **[6] Kemas Kini** — app hubungi pelayan, bandingkan versi, muat turun
  dan pasang sendiri
- Semakan automatik setiap kali app dibuka; kalau ada versi baharu, satu
  notis naik di menu utama
- `Tetapan ▸ [3]` — tukar alamat pelayan kemas kini
- `Tetapan ▸ [4]` — hidup/matikan semakan automatik
- Kod versi lama disimpan ke `.backup/` sebelum ditimpa
- Skrip `bina.sh` di sisi pelayan — hasilkan `taksiran.tar.gz` dan `versi.json`
  sekali gus, supaya nombor versi tak pernah tak selaras

**Nota keselamatan:** tiada pengesahan tandatangan. Sesiapa yang mengawal
pelayan itu boleh menghantar apa-apa kod. Untuk pelayan dalam rangkaian
sendiri ini memadai; kalau nanti diletak di internet, ia perlu difikir semula.

**Nota pemasangan:** versi 1.0.0 tiada fail `kemas.py`, jadi ia tak boleh
mengemas kini dirinya. Satu pemasangan manual yang terakhir diperlukan
sebelum ciri ini berfungsi:

```bash
curl -fsSL http://10.94.149.204:8000/pasang.sh | bash
```

Selepas itu, semua kemas kini seterusnya boleh dibuat dari dalam app.

---

## [1.0.0] — 17/09/2026

Mula guna versi. App sudah cukup lengkap untuk diberi nombor.

**Ada pada versi ini:**

- Dua kaedah kiraan — A (tanpa tolakan), B (dengan tolakan)
- Nisab dikenakan pada kedua-dua kaedah
- Input pendapatan, KWSP, Tabung Haji dan ILTAT secara bulanan atau tahunan
- Tolakan: diri sendiri, isteri (lelaki sahaja), anak, KWSP, Tabung Haji, ILTAT
- Enam gaya cetakan untuk WhatsApp, dengan pratonton sebelum simpan:
  monospace, baris biasa, ringkas, lajur bertitik, kotak, bertindan
- Daftar event — nama program, tarikh, tempat — naik pada kepala cetakan
- Auto-simpan setiap cetakan ke sejarah, dan cetak semula mana-mana rekod
- README dalam app (Tetapan ▸ [2]) — catatan bagaimana app ini terbina
- Pustaka standard Python sahaja; tiada `pip install`

**Nota:** tiada perubahan pada data. Kalau tuan sudah guna versi sebelum ini,
fail dalam `data/` kekal boleh dibaca.

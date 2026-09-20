# Changelog

Semua perubahan penting pada app ini dicatat di sini.

Format nombor versi: `MAJOR.MINOR.PATCH`

- **MAJOR** — sesuatu yang lama tak berfungsi lagi; pengguna terpaksa ubah cara guna
- **MINOR** — ada tambahan baharu; yang lama masih jalan
- **PATCH** — baiki yang rosak sahaja

Ukurannya bukan berapa banyak kerja, tapi berapa besar kesannya pada pengguna.

---

## [3.1.0] — 20/09/2026

Kod diperiksa setiap kali app dibuka, bukan hanya semasa ia dimuat turun.

**Sebab versi ini MINOR:** tiada apa-apa yang lama berhenti berfungsi. Data
tuan dipindahkan secara automatik, dan cara guna app tidak berubah.

**Ditambah:**

- **`MANIFEST` + `MANIFEST.sig` dalam arkib.** Senarai setiap fail yang
  dihantar, dengan SHA-256 setiap satu, ditandatangani dengan kunci yang
  sama. Ia membolehkan cakera diperiksa selepas pemasangan — tandatangan
  arkib hanya membuktikan apa kod itu semasa ia dimuat turun; ia tidak tahu
  apa-apa tentang fail itu kemudiannya
- **`aether/aether.py`** — polis app. Ia **melancarkan** app, bukan
  dipanggil oleh app: app yang memanggil polis boleh melangkau panggilan itu
  dengan membuang satu baris. Setiap kali app dibuka ia mengira semula hash
  setiap fail, menolak fail tambahan, dan menolak apa-apa yang bukan fail
  biasa
- **`pasang.sh` memasang Aether ke `~/.hkm/`** — di luar pokok app, kerana
  alat pembaikan tidak boleh tinggal di dalam benda yang ia baiki. Kalau
  pokok app rosak, `~/.hkm/aether.py --baiki taksiran` masih berfungsi
- **Rekod alert `~/.hkm/alert.jsonl`** — baris gilir append-only dengan
  rantaian hash. Ia hanya membawa laluan kod dan kod alert, **tidak pernah**
  nama pembayar atau isi fail
- **`kemas._sahkan()` memerlukan MANIFEST**, dan menyemak bahawa MANIFEST
  benar-benar menepati isi arkib. Ini menutup vektor penguncian: satu
  pepijat binaan yang meninggalkan MANIFEST basi akan membuatkan Aether
  menolak app itu pada setiap kali dibuka, dan alias `zakat` mati. Sekarang
  ia ditolak semasa pemasangan, ketika versi lama masih utuh.
  (`python ~/taksiran/main.py` kekal berfungsi — Aether menolak untuk
  MEMBUKA app, ia tidak menyentuh app — tetapi itu bukan sesuatu yang
  seorang pengguna patut terpaksa tahu)
- **Fail yang bukan sebahagian daripada pokok bertandatangan akan dibuang**
  semasa kemas kini, dan oleh `aether.py --baiki`. Ukurannya ialah MANIFEST
  yang baharu, bukan beza antara dua MANIFEST — membandingkan lama-lawan-baharu
  tidak menangkap fail yang tidak pernah berada dalam mana-mana MANIFEST, dan
  itulah yang paling senang terhasil. Tanpa ini, satu fail asing di dalam
  folder app menolaknya **selamanya**, kerana alat kemas kininya berada di
  dalam folder itu

**Diubah:**

- **Data tuan berpindah ke `~/.taksiran/`** — `data/` dan `backup/`, keluar
  daripada folder app. Sebelum ini setiap rekod yang disimpan kelihatan
  seperti pengubahsuaian kepada kod, dan `kemas.pasang()` menulis ke dalam
  folder yang sama dengan data pembayar. Pemindahan berlaku sendiri pada
  kali pertama app dibuka; salinan lama ditinggalkan, tidak dipadam
- **`bina.sh` membina pokok staging** daripada senarai masuk, bukan
  menapis dengan `--exclude`. `--exclude='data'` padan mana-mana komponen
  laluan, jadi satu `zakat/data/` pada masa depan akan digugurkan tanpa
  bunyi
- **`bina.sh` menyemak arkib dengan pengesah app sendiri** sebelum
  menerbitkannya — kod yang sama yang akan berjalan di telefon
- **`alat/tanda.py padan` menyemak TIGA salinan kunci**, bukan dua.
  Aether ialah salinan ketiga, dan ia yang paling mudah dilupakan

**Dibaiki:**

- **`pasang.sh` mengganti alias, bukan menambah-jika-tiada.** Versi lama
  hanya menulis alias `zakat` apabila tiada baris padan, jadi pemasangan
  semula tidak pernah menulis alias baharu — launcher itu senyap-senyap
  tidak pernah berkuat kuasa

**Had yang tidak berubah:** Aether mengesan, ia tidak menghalang. Termux
ialah satu app dengan satu UID, jadi Aether berkongsi keistimewaan dengan
benda yang ia periksa. Ia boleh memberi bukti; ia tidak boleh memberi
halangan.

---

## [3.0.0] — 19/09/2026

Setiap kemas kini kini ditandatangani dan diperiksa sebelum dipasang.

**Sebab versi ini MAJOR:** selepas app ini dipasang, pelayan yang tidak
menandatangani arkibnya **tidak berfungsi lagi**. Kemas kini akan ditolak.
Itu perubahan cara kerja, bukan sekadar tambahan.

**Ditambah:**

- **Tandatangan Ed25519.** Arkib kemas kini mesti ditandatangani dengan
  kunci rahsia tuan. App memegang kunci awam, jadi ia boleh mengesahkan
  tetapi tidak boleh mencipta tandatangan. Kunci rahsia tidak pernah
  sampai ke telefon
- **`zakat/tandatangan.py`** — pengesah Ed25519, pustaka standard sahaja.
  Ditulis dengan tangan kerana pustaka standard Python tiada kripto kunci
  awam, dan projek ini sengaja tiada `pip install`
- **`alat/tanda.py`** — alat menandatangani untuk tuan. Folder `alat/`
  **sengaja tidak dihantar**; `bina.sh` memeriksa pengecualian itu berlaku
  pada setiap binaan
- **`pasang.sh` memeriksa tandatangan juga** — jadi pemasangan pertama pun
  tidak boleh dipalsukan oleh tarball yang ditukar
- Cap jari kunci dipaparkan pada skrin `Tetapan` dan pada skrin kemas kini
  yang gagal, supaya sauh kepercayaan itu kelihatan, bukan tersembunyi
- Kunci awam dieksport bersama data — maklumat awam, berguna semasa
  menyiasat kenapa sesuatu kemas kini ditolak

**Keselamatan — tiga lubang yang ditutup sekali gus:**

- **Suntikan ANSI melalui `versi.json`.** Medan `nota` dicetak pada
  **setiap kali app dibuka**, sebelum sebarang pengesahan berjalan. Pelayan
  yang diceroboh boleh letak `\x1b[2J` di situ dan melukis semula skrin —
  memalsukan "✓ tandatangan sah" atau menyembunyikan penolakan. Aksara
  kawalan kini dibuang, dan nombor versi mesti padan `^\d+(\.\d+){0,2}$`
- **Muat turun tanpa had saiz.** Pengesahan berlaku **selepas** muat turun,
  jadi pelayan yang diceroboh boleh menghantar strim tanpa penghujung dan
  menghabiskan memori telefon sebelum sebarang kripto berjalan. Had kini
  20 MB, diperiksa daripada `Content-Length` dan semasa membaca
- **Turutan diperiksa dahulu, struktur kemudian.** Membaca senarai nama
  arkib memaksa seluruh gzip dinyahmampat, jadi arkib bom akan meletup
  sebelum apa-apa disahkan kalau turutannya terbalik. Kedua-duanya diletak
  dalam satu fungsi supaya invarian itu tidak boleh dipisahkan

**Diubah:**

- **Arkib lama tidak boleh dipasang.** Setiap arkib mesti ada fail
  `taksiran.tar.gz.sig` di sebelahnya. Pelayan yang tidak menyediakannya
  akan ditolak dengan ayat yang menyatakan sebabnya
- **`bina.sh` tidak lagi boleh dijalankan tanpa tuan hadir.** Ia menanya
  frasa laluan kunci, dan kini menghasilkan **tiga** fail, bukan dua
- **`bina.sh` menerbitkan secara atomik** dan menulis `versi.json`
  **terakhir**. Binaan yang mati di tengah jalan meninggalkan set fail lama
  yang lengkap, bukan tarball yang tiada siapa boleh pasang
- **Kegagalan separa dikatakan sejujurnya.** Dulu skrin gagal mencetak
  "Tiada apa-apa diubah" walaupun `_ekstrak()` mati separuh jalan. Sekarang
  ia memberitahu bahawa sebahagian fail sudah ditulis, dan salinan lama ada
  dalam `.backup/`
- **Pengawal turun-versi.** Arkib yang lebih lama daripada versi yang sudah
  dipasang ditolak

**Tidak berubah:**

- Tiada perubahan pada kiraan, nisab, atau data tuan. Fail `data/` tidak
  pernah disentuh oleh kemas kini, dahulu mahupun sekarang
- Tiada **suis** untuk mematikan pengesahan. Suis mati ialah laluan pintas,
  dan laluan pintas menjadikan ciri ini hiasan

**Had yang mesti diketahui:**

- **Kunci tandatangan ialah satu titik kegagalan.** Kalau ia dicuri bersama
  frasa laluannya, penyerang boleh menandatangani kod
- **Kunci tidak boleh dipulihkan kalau frasa laluan hilang.** Sebab itu
  `KUNCI` ialah senarai, bukan satu kunci — putaran kunci mungkin, tetapi
  memerlukan satu terbitan terakhir yang ditandatangani kunci lama
- **Tetingkap buta sekali sahaja.** Versi 2.x yang sedang berjalan tiada
  pengesah, jadi arkib pertama yang membawa `tandatangan.py` dihantar
  melalui saluran yang belum disahkan
- **90 baris kripto tulisan tangan ialah risiko terdekat.** Itulah sebabnya
  `bina.sh` menjalankan pengesah Python terhadap setiap arkib yang baru
  ditandatangani, dan membatalkan binaan kalau ia tidak bersetuju dengan
  openssl

---

## [2.0.2] — 18/09/2026

Cetakan qadha: angka tepat sampai sen, dan setiap tahun berdiri sendiri.

**Diubah:**

- **Pembundaran ke ringgit dibuang.** Dulu setiap tahun digenapkan ke
  ringgit terdekat, jadi jumlah di bawahnya tidak berjumlah dengan baris
  di atasnya — sesiapa yang menyemak dengan kalkulator nampak seolah-olah
  ada angka hilang. Sekarang angka tepat sampai sen, dan jumlah itu
  benar-benar jumlah
- **Bentuk jadual diganti.** Dahulu satu jadual empat lajur; sekarang
  setiap tahun mengambil tiga baris — tahun + nisabnya, kasar + zakat,
  dan baris kosong sebagai pemisah. Sebabnya ruang: tiga lajur wang yang
  membawa sen tidak muat dalam satu baris tanpa lajur bercantum, dan
  lajur bercantum membaca sebagai satu nombor. Nisab kini muncul pada
  baris tahunnya sendiri, jadi ia lebih jelas daripada satu lajur sempit
- Nota "dibundarkan ke ringgit terdekat" dibuang — ia sudah tak benar

**Tidak berubah:**

- Zakat masih digenapkan ke **sen** terdekat (`ROUND_HALF_UP`). Ini bukan
  pilihan reka bentuk — 2.577% daripada 36,000 memang menghasilkan
  pecahan sen, dan tiada cara menulisnya tanpa memilih
- Tahun di bawah nisab tetap dipaparkan dengan angkanya, dan tetap
  dikecualikan daripada jumlah
- Kiraan, tolakan, pemilihan tahun dan simpanan rekod: semuanya sama

**Nota versi:** ini PATCH. Tiada keupayaan baharu dan tiada cara guna
yang berubah — cuma rupa cetakan. Kalau tuan rasa ia layak MINOR,
beritahu.

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

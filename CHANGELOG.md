# Changelog

Semua perubahan penting pada app ini dicatat di sini.

Format nombor versi: `MAJOR.MINOR.PATCH`

- **MAJOR** — sesuatu yang lama tak berfungsi lagi; pengguna terpaksa ubah cara guna
- **MINOR** — ada tambahan baharu; yang lama masih jalan
- **PATCH** — baiki yang rosak sahaja

Ukurannya bukan berapa banyak kerja, tapi berapa besar kesannya pada pengguna.

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

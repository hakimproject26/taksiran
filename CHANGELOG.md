# Changelog

Semua perubahan penting pada app ini dicatat di sini.

Format nombor versi: `MAJOR.MINOR.PATCH`

- **MAJOR** — sesuatu yang lama tak berfungsi lagi; pengguna terpaksa ubah cara guna
- **MINOR** — ada tambahan baharu; yang lama masih jalan
- **PATCH** — baiki yang rosak sahaja

Ukurannya bukan berapa banyak kerja, tapi berapa besar kesannya pada pengguna.

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

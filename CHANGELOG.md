# Changelog

Semua perubahan penting pada app ini dicatat di sini.

Format nombor versi: `MAJOR.MINOR.PATCH`

- **MAJOR** — sesuatu yang lama tak berfungsi lagi; pengguna terpaksa ubah cara guna
- **MINOR** — ada tambahan baharu; yang lama masih jalan
- **PATCH** — baiki yang rosak sahaja

Ukurannya bukan berapa banyak kerja, tapi berapa besar kesannya pada pengguna.

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
curl -fsSL http://10.158.15.204:8000/pasang.sh | bash
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

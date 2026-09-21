# taksiran (zakat)

App kiraan zakat untuk telefon. TUI terminal, stdlib Python sahaja.
Rangka pembinaan: @~/HKM/HKMSTYLE.md

## Data

| | |
|---|---|
| Data pengguna | `~/.taksiran/` — **di luar pokok app** (HKMSTYLE §2.1) |
| Versi | `zakat/versi.py` → `NOMBOR` |
| Pelancar | `alias zakat='python ~/.hkm/aether.py taksiran'` |

Alias **mesti** melalui Aether, bukan `python ~/taksiran/main.py`.
`alat/pasang.sh` menggantikan alias, bukan menambah-jika-tiada — versi lama
skrip itu hanya menambah, jadi launcher senyap-senyap tidak pernah
berkuatkuasa.

## Struktur

```
main.py            titik masuk
zakat/             pakej app
  ui.py            paparan + input
  akar.py          memindahkan data keluar daripada pokok app
  kemas.py         enjin kemas kini kendiri
  tandatangan.py   pengesah Ed25519
  versi.py         nombor versi + nota
  store.py kira.py nisab.py qadha.py cetak.py eksport.py readme.py
alat/              sisi bina — TIDAK dihantar ke telefon
  bina.sh pasang.sh lepas.sh tanda.py
```

## Yang menyimpang daripada teras bersama

`ui.py` berkongsi 9 fungsi teras dengan `tasmik` (`kotak`, `garis`, `warna`,
`pad`, `baris_kv`, `tanya`, `tanya_int`, `jeda`, `bersih`). Selebihnya
memang berbeza domain, dan itu **disengajakan** — jangan paksa ia seragam:

- HANYA di sini: `rm`, `rm_pendek`, `tanya_duit`, `tanya_pilih`, `salin_teks`
- `tanya()` memulangkan `None` apabila input tamat (Ctrl+D).
  `tasmik` membaling `InputTamat`. Perbezaan ini sengaja.

## Amaran untuk kerja seterusnya

**App ini tiada ujian langsung.** `tasmik` ada tujuh fail dalam `ujian/`,
Aether ada tiga dalam `aether/ujian/` — projek ini tiada langsung, dan ia
yang paling lama. Setiap perubahan di sini dilakukan tanpa jaring.

Sebelum menambah ciri, pertimbangkan menulis ujian untuk kod yang akan
disentuh — mengikut urutan HKMSTYLE §4.6 (ujian sebelum pemindahan).

## Had yang mesti diketahui

Rujuk seksyen **"Had yang mesti diketahui"** dalam `CHANGELOG.md`. Jangan
salin ke sini — ia akan menjadi basi (corak #3, HKMSTYLE §5).

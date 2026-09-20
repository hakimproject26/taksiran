#!/bin/bash
# Bina fail keluaran untuk saluran kemas kini.
#
# Menghasilkan EMPAT fail dalam `alat/keluaran/`:
#   taksiran.tar.gz       kod app
#   taksiran.tar.gz.sig   tandatangan Ed25519 bagi arkib itu
#   versi.json            nombor versi + nota, dibaca oleh app untuk semak
#   pasang.sh             salinan pemasang, supaya `keluaran/` ialah cermin
#                         lengkap apa yang dilihat klien
#
# Guna:  bash alat/bina.sh
#
# Skrip ini menanya frasa laluan kunci tandatangan DUA kali — sekali untuk
# MANIFEST, sekali untuk arkib. Kedua-duanya mesti ditandatangani: arkib itu
# untuk telefon yang memuat turun, MANIFEST itu untuk Aether yang memeriksa
# cakera pada setiap kali app dibuka kemudian.
#
# Skrip ini TIDAK menerbitkan ke GitHub. Itu kerja `alat/lepas.sh`, yang
# memanggil skrip ini dahulu.
set -euo pipefail

AKAR="$HOME"
# Bina.sh kini tinggal di dalam pokok app, jadi ia tidak boleh lagi menganggap
# direktorinya sendiri ialah akar app. Ia menaik satu tingkat.
APP="$(cd "$(dirname "$0")/.." && pwd)"
#
# Keluaran dan pemasang kedua-duanya berada DI BAWAH `alat/`, dan itu bukan
# kekemasan. `zakat/manifes.ABA_I_AKAR` mengecualikan `alat/` daripada
# pemeriksaan fail asing Aether; `keluaran/` dan `pasang.sh` di akar pula
# TIDAK dikecualikan, jadi setiap arkib yang baru dibina akan menjadikan pokok
# ini "ada fail tambahan" dan app itu akan menolak dirinya sendiri.
#
# Alternatifnya ialah menambah dua nama itu ke senarai abaikan — iaitu
# melonggarkan pengawal keselamatan supaya binaan menjadi senang. Itu
# pertukaran yang salah. `alat/` sudah bermakna "bukan kod app", jadi benda
# yang bukan kod app diletakkan di situ.
TUJUAN="$APP/alat/keluaran"
SUMBER="$APP"
ARKIB="$TUJUAN/taksiran.tar.gz"
TANDA="$SUMBER/alat/tanda.py"
PASANG="$APP/alat/pasang.sh"
MANIFES="$AKAR/HKM/aether/manifes.py"
AETHER="$AKAR/HKM/aether/aether.py"

# Apa yang dihantar. SENARAI MASUK, bukan senarai keluar.
#
# Versi lama skrip ini menggunakan `tar --exclude`, dan itu gagal secara
# senyap: `--exclude='data'` padan mana-mana komponen laluan, jadi satu
# `zakat/data/` pada masa depan akan digugurkan tanpa bunyi. Dengan senarai
# masuk, apa yang tidak dinamakan di sini tidak dihantar — dan fail yang
# tidak dihantar tidak boleh menyelinap.
MASUK=(main.py README.md CHANGELOG.md zakat)

if [ ! -f "$SUMBER/main.py" ]; then
    echo "Ralat: tak jumpa $SUMBER/main.py" >&2
    exit 1
fi
for f in "$MANIFES" "$AETHER"; do
    if [ ! -f "$f" ]; then
        echo "Ralat: tak jumpa $f" >&2
        echo "       Penjana MANIFEST dan Aether ialah kod dalam ~/HKM/aether/." >&2
        exit 1
    fi
done

# Diperiksa SEBELUM membina apa-apa. Tiga tempat memegang kunci awam —
# zakat/tandatangan.py, pasang.sh, dan aether.py — dan kalau mana-mana
# menyimpang, arkib yang sah ditolak pada pemasangan pertama, iaitu kepada
# orang yang belum ada app untuk membetulkannya. Diperiksa di sini supaya
# hanyutan itu mustahil, bukan sekadar tidak mungkin berlaku.
#
# TIADA pembalut `-f`. Versi lama skrip ini hidup di dalam folder output, jadi
# `[ -f "$TUJUAN/pasang.sh" ]` kebetulan benar; sebaik ia berpindah ke alat/
# ujian itu menjadi palsu dan pengawal ini dilangkau TANPA BUNYI pada setiap
# binaan. Fail yang hilang mesti menjadi ralat keras, bukan langkauan.
if [ ! -f "$PASANG" ]; then
    echo "Ralat: tak jumpa $PASANG — pemeriksaan silang kunci tidak dapat dijalankan." >&2
    exit 1
fi
echo "Menyemak kunci dalam pasang.sh …"
python3 "$TANDA" padan "$PASANG"

VERSI="$(python3 -c "
import re,sys
t=open('$SUMBER/zakat/versi.py',encoding='utf-8').read()
m=re.search(r'^NOMBOR\s*=\s*[\"\']([^\"\']+)[\"\']',t,re.M)
sys.exit('Ralat: NOMBOR tiada') if not m else print(m.group(1))")"

# ---------------------------------------------------------------- staging
#
# Pokok staging dibina daripada senarai masuk, MANIFEST dijana DARIPADANYA,
# dan tar dibina daripada pokok yang SAMA. Jadi set fail dalam arkib dan set
# fail dalam MANIFEST sama SECARA BINAAN, bukan secara janji.
STAGING="$(mktemp -d)"
bersih() { rm -rf "$STAGING"; }
trap bersih EXIT

echo "Menyediakan pokok staging …"
mkdir -p "$STAGING/taksiran"
for item in "${MASUK[@]}"; do
    if [ ! -e "$SUMBER/$item" ]; then
        echo "Ralat: $SUMBER/$item tiada — senarai MASUK salah." >&2
        exit 1
    fi
    cp -r "$SUMBER/$item" "$STAGING/taksiran/"
done
# Aether dihantar DI DALAM arkib, dan `pasang.sh` menyalinnya keluar ke
# ~/.hkm/ selepas ini. Ia bukan kod app — ia polis app — tetapi ia mesti
# berada dalam arkib yang ditandatangani, kerana itulah satu-satunya saluran
# yang telefon percaya.
#
# Ia diletakkan SEBELUM MANIFEST dijana, jadi ia disenaraikan. Itu bermakna
# salinan dalam pokok app dan salinan dalam ~/.hkm/ boleh dibandingkan:
# Aether memeriksa pokok app, dan pokok app mengandungi Aether.
mkdir -p "$STAGING/taksiran/aether"
cp "$AETHER" "$STAGING/taksiran/aether/aether.py"

# Sisa pengkompil bukan kod, dan ia berbeza pada setiap mesin. Ia tidak
# boleh dihantar, dan ia tidak boleh disenaraikan.
find "$STAGING" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$STAGING" -name '*.pyc' -delete

echo "Menjana MANIFEST …"
python3 "$MANIFES" jana "$STAGING/taksiran" --app taksiran --versi "$VERSI"

echo "Menandatangani MANIFEST …"
python3 "$TANDA" tanda "$STAGING/taksiran/MANIFEST"

# ---------------------------------------------------------------- arkib
#
# Bina ke nama .new dahulu, dan terbitkan hanya di penghujung. Kalau binaan
# mati di tengah jalan, `keluaran/` masih memegang set fail LAMA yang lengkap.
#
# Nota: sejak saluran berpindah ke GitHub, keatoman yang dipakai klien bukan
# lagi turutan fail di sini — `versi.json` ditulis terakhir masih berguna,
# tetapi yang menjamin tiada klien nampak terbitan separuh siap ialah release
# DRAF dalam `lepas.sh`. Turutan di sini kekal kerana ia tidak merugikan.
rm -f "$ARKIB.new" "$ARKIB.new.sig"
mkdir -p "$TUJUAN"

echo "Membina arkib …"
tar czf "$ARKIB.new" -C "$STAGING" taksiran

# Pengecualian tar gagal secara SENYAP, jadi pokoknya diperiksa. Senarai
# masuk sepatutnya sudah menjamin ini; pemeriksaan ini mengesahkan bahawa
# jaminan itu benar-benar berlaku.
#
# Senarai dikumpulkan SEKALI ke dalam pemboleh ubah, tidak disalurkan terus
# ke `grep -q`. Dengan `set -o pipefail`, `tar tzf … | grep -q …` memulangkan
# kegagalan WALAUPUN padanan dijumpai: `grep -q` keluar sebaik ia menjumpai
# padanan, tar menerima SIGPIPE, dan pipefail menjadikan status paip itu
# status tar. Setiap pemeriksaan akan berbohong — yang "ada" dilaporkan
# tiada, dan yang "tiada" dilaporkan ada.
#
# `grep -v '/$'` membuang entri direktori: tar menyenaraikannya dengan garis
# miring di hujung, dan `find -type f` tidak. Tanpa ini perbandingan di bawah
# sentiasa gagal kerana sebab yang salah.
SENARAI="$(tar tzf "$ARKIB.new" | grep -v '/$' | sort)"
DIJANGKA="$(cd "$STAGING" && find . -type f | sed 's|^\./||' | sort)"

# Nama berbahaya dinamakan secara eksplisit. Kesamaan set di bawah sudah pun
# menangkapnya, tetapi ia gagal sebagai "set tidak sama" — dan mesej yang
# menyatakan BAHAYA itu lebih berguna daripada senarai beza.
#
# `pasang.sh` di sini bermakna DI AKAR arkib. Satu entri MASUK seperti
# `alat/pasang.sh` menghasilkan `taksiran/pasang.sh` — `cp` menyalin nama
# asas sahaja — jadi ia ditangkap oleh corak ini juga.
for p in pasang.sh alat/ data/; do
    if grep -q "^taksiran/$p" <<<"$SENARAI"; then
        echo "Ralat: $p masuk ke dalam arkib." >&2
        echo "       Nama ini tidak pernah boleh dihantar: pasang.sh membawa" >&2
        echo "       salinan kunci awam yang boleh hanyut, alat/ membawa kod" >&2
        echo "       menandatangani, dan data/ membawa rekod pembayar." >&2
        echo "       Semak senarai MASUK, dan apa-apa yang menulis ke pokok" >&2
        echo "       staging." >&2
        exit 1
    fi
done

# Inilah pengawal yang sebenar. Versi lama hanya menegaskan fail WAJIB ada,
# dan menegaskan dua corak terlarang — jadi apa-apa yang tidak dinamakan
# kedua-duanya (mis. satu `pasang.sh` di akar repo) akan melalui tanpa
# halangan. Kesamaan set menutup kelas itu sepenuhnya: arkib mesti mengandungi
# TEPAT apa yang ada dalam pokok staging, tiada lebih dan tiada kurang.
if [ "$SENARAI" != "$DIJANGKA" ]; then
    echo "Ralat: isi arkib tidak sama dengan pokok staging." >&2
    diff <(echo "$DIJANGKA") <(echo "$SENARAI") \
        | sed 's/^</  hanya dalam staging: /; s/^>/  hanya dalam arkib:   /' >&2
    exit 1
fi
echo "  ✓ isi arkib == pokok staging ($(wc -l <<<"$SENARAI") fail)"

echo "Menandatangani arkib …"
python3 "$TANDA" tanda "$ARKIB.new"

# Inilah ujian yang paling bernilai dalam projek ini. Ia membandingkan
# openssl dengan zakat/tandatangan.py pada setiap binaan, jadi penyimpangan
# antara kedua-duanya ditangkap di sini — bukan di telefon orang lain, di
# mana ia bermakna kemas kini yang ditolak tanpa sebab.
echo "Menyemak dengan kod yang akan dihantar …"
python3 "$TANDA" sahkan "$ARKIB.new"

# Dan inilah ujian yang paling bernilai KEDUA: kod yang akan berjalan di
# telefon itu sendiri, yang memutuskan sama ada ia mahu arkib ini. Kalau
# MANIFEST basi — dijana sebelum satu fail terakhir disunting — Aether akan
# menolak app itu pada setiap kali dibuka selepas pemasangan, dan alat kemas
# kini berada DI DALAM app itu. Telefon itu terkunci.
#
# Ditangkap di sini, versi lama masih utuh di telefon dan masih boleh
# memuat turun pembaikan.
echo "Menyemak dengan pengesah app sendiri …"
python3 - "$SUMBER" "$ARKIB.new" "$VERSI" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
from zakat import kemas

arkib, dijangka = sys.argv[2], sys.argv[3]
with open(arkib, "rb") as f:
    data = f.read()
with open(arkib + ".sig", encoding="ascii") as f:
    teks_sig = f.read()

ok, mesej = kemas._periksa(arkib, dijangka, teks_sig, data)
if not ok:
    sys.exit(f"Ralat: app sendiri akan MENOLAK arkib ini:\n       {mesej}")
print("  ✓ pengesah app menerima arkib ini")
PY

echo "Menerbitkan …"
mv "$ARKIB.new" "$ARKIB"
mv "$ARKIB.new.sig" "$ARKIB.sig"

# versi.json DITULIS TERAKHIR. Dalam `keluaran/` ia penanda terbitan lengkap;
# di GitHub penanda itu ialah release draf (lihat `lepas.sh`).
echo "Menulis versi.json …"
python3 - "$SUMBER" "$TUJUAN/versi.json" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1])
from zakat import versi
json.dump(
    {"versi": versi.NOMBOR, "tarikh": versi.TARIKH, "nota": versi.NOTA},
    open(sys.argv[2], "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=2,
)
print(f"  versi {versi.NOMBOR} ({versi.TARIKH})")
PY

# `keluaran/` mesti jadi cermin LENGKAP apa yang dilihat klien. Kalau
# pasang.sh hanya hidup di akar repo, sesiapa yang menguji terhadap
# `keluaran/` — termasuk `ujian/hujung.sh` — akan menguji folder yang tidak
# menyerupai release. Satu salinan di sini menghalangnya.
echo "Menyalin pasang.sh ke alat/keluaran/ …"
cp "$PASANG" "$TUJUAN/pasang.sh"

ls -l "$ARKIB" "$ARKIB.sig" "$TUJUAN/versi.json" "$TUJUAN/pasang.sh"
echo
echo "Cap jari kunci: $(python3 "$TANDA" cap)"
echo
echo "Sedia untuk diterbitkan. Seterusnya:"
echo "  bash alat/lepas.sh"
echo

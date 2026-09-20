#!/usr/bin/env bash
# Pemasang Taksiran Zakat Pendapatan untuk Termux.
#
# Guna:
#   curl -fsSL https://github.com/hakimproject26/taksiran/releases/latest/download/pasang.sh | bash
#
# Kalau hos lain, hulur sebagai argumen:
#   curl -fsSL <url>/pasang.sh | bash -s <url>
#
# Arkib mesti ditandatangani oleh kunci di bawah, dan tandatangan itu
# diperiksa SEBELUM apa-apa diekstrak.
#
# HAD YANG MESTI DIKETAHUI, bukan disimpan dalam kepala: skrip ini dan arkib
# kini datang melalui HTTPS dari GitHub, jadi
#   * penyadap tidak boleh menukar arkib dalam perjalanan, dan
#   * sijil TLS mengikat kedua-duanya kepada hos yang sebenar.
# Tetapi ia TIDAK menjadikan saluran ini tidak boleh dipalsukan. Sesiapa yang
# menguasai akaun GitHub tuan boleh menukar kedua-dua fail sekali gus — kunci
# di bawah, dan arkibnya. Dalam sistem ini, akses tulis ke repo adalah
# SETARA dengan pemilikan kunci tandatangan: release yang ditandatangani
# dengan kunci yang sama tidak boleh dibezakan daripada yang asli. Yang
# memutuskan kod itu kod tuan tetap tandatangan Ed25519, bukan hos.
# Sebab itu 2FA pada akaun GitHub bukan pilihan.

set -e

# Saluran lalai ialah release GitHub. `latest/download` TIDAK mengandungi
# nombor versi, jadi alamat ini kekal sah untuk setiap versi seterusnya.
#
# Versi lama menghala ke IP Tailscale mesin tuan sendiri. Itu bermakna mesin
# itu mesti hidup setiap kali telefon mahu menyemak kemas kini, dan arkibnya
# datang melalui HTTP tanpa penyulitan. Kalau GitHub tidak dapat dicapai,
# pelayan lama itu masih boleh dipakai:
#   bash pasang.sh http://100.78.29.8:8000
ASAS="${1:-https://github.com/hakimproject26/taksiran/releases/latest/download}"
DEST="$HOME/taksiran"
ARKIB="$HOME/.taksiran.tar.gz"
SIG="$ARKIB.sig"
PEM="$HOME/.taksiran-kunci-awam.pem"

bersih() { rm -f "$ARKIB" "$SIG" "$SIG.raw" "$PEM" "$HOME/.taksiran-manifes-lama"; }
# `.taksiran-manifes-lama` kekal dalam senarai bersih untuk pemasangan yang
# PERNAH dijalankan oleh versi skrip ini yang lama; ia tidak lagi ditulis.
trap bersih EXIT

echo
echo "  ── Taksiran Zakat Pendapatan ──"
echo

# --- 1. Python ---------------------------------------------------------
if command -v python >/dev/null 2>&1; then
    echo "  ✓ python dah ada — $(python --version 2>&1)"
else
    echo "  → memasang python..."
    pkg install -y python
fi

# --- 2. curl -----------------------------------------------------------
if ! command -v curl >/dev/null 2>&1; then
    echo "  → memasang curl..."
    pkg install -y curl
fi

# --- 2b. Sijil TLS -----------------------------------------------------
# Ini perubahan yang paling senang terlepas pandang, dan akibatnya paling
# memeningkan. Reka bentuk lama memakai `http://` kosong ke alamat LAN —
# tiada sijil, tiada stor sijil. Sekarang setiap muat turun ialah HTTPS, jadi
# Termux mesti ada stor CA. Kalau ia tiada, SETIAP semakan gagal selama-lamanya
# dengan mesej yang menyalahkan "pelayan", dan `curl` di bawah gagal sebelum
# ada app yang boleh mendiagnosisnya.
if ! pkg install -y ca-certificates >/dev/null 2>&1; then
    # Bukan ralat maut dengan sendirinya — stor sijil mungkin sudah ada
    # melalui jalan lain. Ujian sebenar ialah muat turun di langkah 4.
    echo "  ! ca-certificates tidak dapat dipasang — cuba teruskan"
fi

# --- 3. openssl --------------------------------------------------------
# CLI openssl ada dalam pakej openssl-tool, bukan dalam asas Termux.
# Ia diperlukan untuk mengesahkan tandatangan, jadi ketiadaannya ialah
# kegagalan, bukan amaran — kita gagal TERTUTUP. Memasang tanpa
# memeriksa tandatangan adalah lebih teruk daripada tidak memasang.
if ! command -v openssl >/dev/null 2>&1; then
    echo "  → memasang openssl-tool..."
    pkg install -y openssl-tool || true
fi
if ! command -v openssl >/dev/null 2>&1; then
    echo "  ✗ openssl tiada, jadi tandatangan tak dapat diperiksa." >&2
    echo "    Pemasangan dibatalkan. Cuba:  pkg install openssl-tool" >&2
    exit 1
fi

# --- 4. Muat turun -----------------------------------------------------
# Had masa dan cubaan-semula: reka bentuk lama menembak ke pelayan LAN, di
# mana kegagalan berlaku dalam milisaat. GitHub melibatkan DNS, dua jabat
# tangan TLS, dan dua hop redirect. `curl` tanpa `--max-time` boleh
# menggantung tanpa penghujung pada sambungan mudah alih yang tersekat.
ambil() {
    local kod=0
    curl -fsSL --max-time 120 --retry 2 --retry-delay 1 --retry-connrefused \
        "$1" -o "$2" || kod=$?
    case "$kod" in
        0) return 0 ;;
        60|77|58|35)
            echo "  ✗ Sijil TLS tidak dapat diperiksa (curl $kod)." >&2
            echo "    Termux tiada stor sijil atau ia rosak — bukan salah pelayan." >&2
            echo "    Cuba:  pkg install ca-certificates" >&2
            return "$kod" ;;
        6)
            echo "  ✗ Tak jumpa hos $1 — semak sambungan dan ejaan alamat." >&2
            return "$kod" ;;
        *)
            echo "  ✗ Gagal memuat turun $1 (curl $kod)." >&2
            return "$kod" ;;
    esac
}

echo "  → memuat turun dari $ASAS ..."
cd "$HOME"
ambil "$ASAS/taksiran.tar.gz" "$ARKIB" || exit 1
ambil "$ASAS/taksiran.tar.gz.sig" "$SIG" || exit 1

# --- 5. Sahkan tandatangan --------------------------------------------
# Sebelum APA-APA diekstrak, dan sebelum .bashrc disentuh. Kalau ini gagal,
# telefon masih tiada app baharu dan tiada fail lama disentuh.
cat > "$PEM" <<'PEM'
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAK+8YJeD/JuIu0CBry+RiLz1LMI6I7jKDR3cERKuGzJs=
-----END PUBLIC KEY-----
PEM

# .sig disimpan sebagai hex supaya ia tahan melalui sebarang pengendalian
# teks. openssl mahu bait mentah, jadi ia ditukar di sini — sekali gus
# memeriksa panjangnya, supaya fail rosak gagal dengan ayat yang jelas.
python3 - "$SIG" "$SIG.raw" <<'PY'
import binascii, sys
try:
    teks = open(sys.argv[1], encoding="ascii").read().strip()
    bait = binascii.unhexlify(teks)
except (ValueError, OSError, UnicodeDecodeError):
    sys.exit("Fail tandatangan rosak atau tidak boleh dibaca.")
if len(bait) != 64:
    sys.exit(f"Fail tandatangan {len(bait)} bait, sepatutnya 64.")
open(sys.argv[2], "wb").write(bait)
PY

echo "  → mengesahkan tandatangan ..."
if openssl pkeyutl -verify -pubin -inkey "$PEM" -rawin \
        -in "$ARKIB" -sigfile "$SIG.raw" >/dev/null 2>&1; then
    echo "  ✓ tandatangan sah"
else
    echo "  ✗ Tandatangan tidak sah — pemasangan dibatalkan." >&2
    echo "    Arkib ini bukan daripada tuan. Jangan teruskan." >&2
    exit 1
fi

# --- 6. Periksa laluan, kemudian ekstrak -------------------------------
# GNU tar sudah menolak '..' sendiri (keluar dengan kod 2), tetapi skrip
# ini tidak tahu sama ada tar di sini GNU tar pun. Diperiksa sendiri.
if tar tzf "$ARKIB" | grep -qE '^(/|.*\.\.)'; then
    echo "  ✗ Arkib mengandungi laluan tak selamat — dibatalkan." >&2
    exit 1
fi

mkdir -p "$DEST"
tar xzf "$ARKIB" -C "$HOME"
echo "  ✓ dipasang ke $DEST"

# --- 6b. Buang fail yang bukan sebahagian daripada pokok bertandatangan --
# Pengekstrakan hanya MENULIS fail yang ada dalam arkib; ia tidak membuang
# apa-apa. Jadi pokok itu boleh mengandungi fail yang tidak ditandatangani —
# sama ada modul yang dipadamkan daripada kod, atau fail yang ditambah
# kemudian oleh benda lain. Aether menolak app yang ada fail tambahan, dan ia
# menolaknya SETIAP kali app dibuka, dengan alat kemas kininya di dalam app
# itu.
#
# Jadi ukurannya ialah MANIFEST BAHARU, bukan beza antara dua manifest.
# Membandingkan lama-lawan-baharu tidak menangkap fail yang tidak pernah
# berada dalam mana-mana manifest — dan itulah fail yang paling mudah
# terhasil (mana-mana alat yang menulis ke dalam folder app).
#
# Keselamatan, dan hadnya yang mesti jelas:
#   * Yang dibuang hanya fail BIASA dalam pokok itu sendiri. Symlink dan
#     direktori dilangkau — memadam melalui symlink akan mengenai sasaran.
#   * Yang dikecualikan ialah senarai abaikan app (`__pycache__`, `data/`,
#     `.backup/`, `alat/`, `.git/`). Sejak v3.1.0 data pengguna berada DI
#     LUAR pokok app, jadi yang tinggal di sini ialah kod.
#   * Manifes baharu datang dari arkib yang tandatangannya baru diperiksa
#     di langkah 5. Kalau ia hilang atau rosak, kita TIDAK memadam apa-apa.
python3 - "$DEST" <<'PY'
import os, sys
dest = sys.argv[1]
sys.path.insert(0, dest)
try:
    from zakat import manifes as M
except ImportError:
    print("  ! manifes.py tiada — fail asing tidak diperiksa")
    sys.exit(0)

try:
    with open(os.path.join(dest, M.NAMA), encoding="utf-8") as f:
        _kepala, entri = M.hurai(f.read())
except (OSError, M.ManifesRalat):
    print("  ! MANIFEST tidak boleh dibaca — fail asing tidak diperiksa")
    sys.exit(0)

disenarai = {l for _, l in entri}
dibuang = []
for asas, folder, fail in os.walk(dest, followlinks=False):
    folder[:] = [d for d in folder
                 if not M.abaikan(os.path.relpath(os.path.join(asas, d), dest)
                                  .replace(os.sep, "/"))]
    for f in fail:
        rel = os.path.relpath(os.path.join(asas, f), dest).replace(os.sep, "/")
        if rel in disenarai or rel in (M.NAMA, M.NAMA_SIG) or M.abaikan(rel):
            continue
        penuh = os.path.join(asas, f)
        if not os.path.isfile(penuh) or os.path.islink(penuh):
            continue
        try:
            os.unlink(penuh)
            dibuang.append(rel)
        except OSError:
            pass
if dibuang:
    print(f"  ✓ {len(dibuang)} fail asing dibuang:")
    for l in sorted(dibuang)[:20]:
        print(f"      {l}")
    if len(dibuang) > 20:
        print(f"      … dan {len(dibuang) - 20} lagi")
PY

if [ -d "$DEST/data" ] || [ -d "$DEST/.backup" ]; then
    echo "  ✓ data lama dikekalkan (akan dipindahkan keluar folder app"
    echo "    secara automatik pada kali pertama app dibuka)"
fi

# --- 6c. Pindahkan alamat pelayan kemas kini ---------------------------
# Kenapa ini ada di sini, dan bukan di dalam app sahaja:
#
# `store.config()` menindih `config.json` yang disimpan DI ATAS nilai lalai.
# Jadi menukar lalai dalam kod TIDAK mengubah apa-apa pada telefon yang sudah
# dipasang — ia kekal memegang alamat lama selama-lamanya. Kod migrasi yang
# betul-betul menulis semula nilai itu hidup di dalam versi BAHARU, yang
# telefon hanya boleh dapat daripada saluran LAMA. Kalau mesin itu dimatikan
# sebelum telefon sempat dikemas kini, telefon tidak pernah menerima kod
# migrasi, dan setiap semakan selepas itu gagal menghubungi alamat yang sudah
# tiada.
#
# `pasang.sh` sentiasa datang daripada saluran BAHARU, jadi ia satu-satunya
# tempat yang boleh memutuskan kitaran itu.
#
# Ia menyentuh direktori data pembayar, jadi syaratnya ketat:
#   * PADAN TEPAT sahaja terhadap lalai lama yang diketahui. Sumber tersuai
#     yang tuan taip sendiri TIDAK PERNAH disentuh.
#   * Semua kunci lain dikekalkan; JSON dibaca dan ditulis semula, bukan
#     diganti.
#   * Tulis secara ATOMIK — fail sementara kemudian `os.replace`.
#   * Kalau fail itu tiada atau tidak boleh dibaca, berdiam dan jangan buat
#     apa-apa. Telefon baharu tiada fail itu, dan itu bukan kegagalan.
python3 - "$HOME/.taksiran/data/config.json" "$ASAS" <<'PY'
import json, os, sys

laluan, baru = sys.argv[1], sys.argv[2]
LAMA = ("http://100.78.29.8:8000", "http://10.94.149.204:8000")

if not os.path.isfile(laluan):
    sys.exit(0)
try:
    with open(laluan, encoding="utf-8") as f:
        cfg = json.load(f)
except (OSError, ValueError):
    print("  ! config.json tidak boleh dibaca — sumber tidak diubah")
    sys.exit(0)
if not isinstance(cfg, dict) or cfg.get("sumber_kemas") not in LAMA:
    sys.exit(0)  # tiada, atau sumber tersuai — bukan urusan kita

cfg["sumber_kemas"] = baru
sementara = laluan + ".baru"
with open(sementara, "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)
os.replace(sementara, laluan)
print(f"  ✓ alamat kemas kini dipindahkan ke {baru}")
PY

# --- 7. Aether ---------------------------------------------------------
# Aether ialah LAUNCHER, bukan callee. App yang memanggil polis boleh
# melangkau panggilan itu dengan membuang satu baris, jadi Aether yang
# membuka app — bukan sebaliknya.
#
# Ia dipasang KE LUAR pokok app, dan itu bukan kekemasan: alat pembaikan
# tidak boleh tinggal di dalam benda yang ia baiki. Kalau pokok app rosak,
# ~/.hkm/aether.py masih ada untuk menjalankan `--baiki`.
DIR_HKM="$HOME/.hkm"
mkdir -p "$DIR_HKM"
rm -f "$DIR_HKM/aether.py"
cp "$DEST/aether/aether.py" "$DIR_HKM/aether.py"
chmod 500 "$DIR_HKM/aether.py"
echo "  ✓ aether.py dipasang ke $DIR_HKM/"

# Daftar app. `kunci_dalam` memberitahu Aether di mana app menyimpan kunci
# awamnya sendiri, supaya kedua-dua salinan itu boleh dibandingkan.
python3 - "$DIR_HKM/app.json" "$DEST" "$ASAS" <<'PY'
import json, sys
laluan, dest, asas = sys.argv[1:4]
try:
    daftar = json.load(open(laluan, encoding="utf-8"))
    if not isinstance(daftar, dict):
        daftar = {}
except (OSError, ValueError):
    daftar = {}
daftar["taksiran"] = {
    "folder": dest,
    "utama": "main.py",
    "kunci_dalam": "zakat/tandatangan.py",
    "sumber": asas,
    "arkib": "taksiran.tar.gz",
}
with open(laluan, "w", encoding="utf-8") as f:
    json.dump(daftar, f, indent=2, ensure_ascii=False)
print(f"  ✓ taksiran didaftarkan dalam {laluan}")
PY

# --- 8. Ujian pelancaran, kemudian alias -------------------------------
# Alias dipindahkan kepada Aether HANYA kalau Aether benar-benar boleh
# membuka app ini PADA PERANTI INI. Bendera pelancaran (`-S`,
# `-X pycache_prefix`) diuji di Linux semasa Aether dibina, tetapi Termux
# ialah Python yang berbeza pada sistem fail yang berbeza. Kalau ia gagal di
# sini, menukar alias akan mengunci app itu — dan alat pembaikannya berada
# di dalam app itu.
#
# Jadi ia diukur, bukan diandaikan.
ALIAS_AETHER="alias zakat='python $DIR_HKM/aether.py taksiran'"
ALIAS_LAMA="alias zakat='python $DEST/main.py'"

if python3 "$DIR_HKM/aether.py" --cuba taksiran; then
    BARU="$ALIAS_AETHER"
    echo "  ✓ alias 'zakat' sekarang melalui Aether"
else
    BARU="$ALIAS_LAMA"
    echo "  ! Aether tidak dapat membuka app ini pada peranti ini." >&2
    echo "    Alias 'zakat' DIBIARKAN seperti dahulu — app masih boleh" >&2
    echo "    digunakan, tetapi tanpa pemeriksaan." >&2
fi

# GANTI, bukan tambah-jika-tiada. Versi lama skrip ini hanya menambah alias
# apabila tiada baris padan, jadi pemasangan semula TIDAK PERNAH menulis
# alias baharu — launcher itu senyap-senyap tidak pernah berkuat kuasa, dan
# tiada apa-apa yang menunjukkannya.
if grep -qs "^alias zakat=" "$HOME/.bashrc"; then
    python3 - "$HOME/.bashrc" "$BARU" <<'PY'
import sys
laluan, baru = sys.argv[1], sys.argv[2]
with open(laluan, encoding="utf-8") as f:
    baris = f.read().splitlines(True)
keluar, jumpa = [], False
for b in baris:
    if b.startswith("alias zakat="):
        if not jumpa:
            keluar.append(baru + "\n")
            jumpa = True
        continue
    keluar.append(b)
with open(laluan, "w", encoding="utf-8") as f:
    f.writelines(keluar)
print("  ✓ alias 'zakat' dikemas kini")
PY
else
    printf '%s\n' "$BARU" >> "$HOME/.bashrc"
    echo "  ✓ alias 'zakat' ditambah"
fi

# --- 9. termux-api (pilihan, jangan gagalkan pemasangan) ---------------
if ! command -v termux-clipboard-set >/dev/null 2>&1; then
    echo "  ! termux-api tak ada — butang print takkan auto-salin ke clipboard"
    echo "    (pilihan) pkg install termux-api"
fi

echo
echo "  Siap."
echo
echo "  Jalan sekarang:   cd ~/taksiran && python main.py"
echo "  Lain kali:        buka Termux, taip — zakat"
echo

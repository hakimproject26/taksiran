#!/usr/bin/env bash
# Terbitkan satu versi ke GitHub Releases.
#
# Guna:  bash alat/lepas.sh
#
# Skrip ini TIDAK menaikkan nombor versi, dan TIDAK commit. Itu kerja tuan,
# dan ia mesti dibuat dahulu:
#
#   1. sunting zakat/versi.py  (NOMBOR, TARIKH, NOTA)
#   2. sunting CHANGELOG.md
#   3. git commit -am "v3.1.1 — ..."
#   4. git tag v3.1.1 && git push && git push --tags
#   5. bash alat/lepas.sh
#
# Skrip ini mengesahkan langkah 3 dan 4 sudah berlaku, kemudian menerbitkan.
# Ia sengaja tidak melakukannya sendiri: menerbitkan saluran kemas kini
# telefon orang ialah tindakan yang patut melalui satu commit yang boleh
# dilihat, bukan kesan sampingan satu skrip.
set -euo pipefail

AKAR="$(cd "$(dirname "$0")/.." && pwd)"
KELUARAN="$AKAR/alat/keluaran"
REPO="${HKM_REPO:-hakimproject26/taksiran}"
URL="https://github.com/$REPO/releases/latest/download"

cd "$AKAR"

VERSI="$(python3 -c "
import re,sys
t=open('$AKAR/zakat/versi.py',encoding='utf-8').read()
m=re.search(r'^NOMBOR\s*=\s*[\"\']([^\"\']+)[\"\']',t,re.M)
sys.exit('Ralat: NOMBOR tiada') if not m else print(m.group(1))")"
TAG="v$VERSI"

echo
echo "  ── Terbit $TAG ke $REPO ──"
echo

# ---------------------------------------------------------------- 1. asal
# Kebolehsanan (provenance). Kalau pokok ini tidak sama dengan apa yang
# ditandakan oleh tag, maka yang diterbitkan bukan yang diuji.
if [ -n "$(git status --porcelain)" ]; then
    echo "Ralat: pokok git tidak bersih. Commit dahulu." >&2
    git status --short >&2
    exit 1
fi

if ! git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
    echo "Ralat: tag $TAG tiada." >&2
    echo "       git tag $TAG && git push origin $TAG" >&2
    exit 1
fi

KEPALA="$(git rev-parse HEAD)"
TAG_SHA="$(git rev-parse "$TAG^{commit}")"
if [ "$KEPALA" != "$TAG_SHA" ]; then
    echo "Ralat: tag $TAG menunjuk pada commit yang BUKAN HEAD." >&2
    echo "       HEAD    : $KEPALA" >&2
    echo "       $TAG: $TAG_SHA" >&2
    echo "       Release daripada commit lama membuat 'latest' salah — lihat" >&2
    echo "       nota created_at di bawah." >&2
    exit 1
fi

# Tag mesti ada di remote. `--verify-tag` di langkah 4 akan menolaknya
# kemudian, tetapi gagal di sini memberi mesej yang lebih berguna.
if ! git ls-remote --tags origin "refs/tags/$TAG" | grep -q .; then
    echo "Ralat: tag $TAG belum ditolak ke origin." >&2
    echo "       git push origin $TAG" >&2
    exit 1
fi
echo "  ✓ pokok bersih, $TAG == HEAD, tag ada di origin"

if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
    echo "Ralat: release $TAG sudah wujud." >&2
    echo "       Release TIDAK BOLEH dipadam atau ditulis semula." >&2
    echo "       Kalau aset ini rosak, naikkan versi — jangan ganti aset." >&2
    exit 1
fi

# ---------------------------------------------------------------- 2. bina
echo
bash "$AKAR/alat/bina.sh"

for f in taksiran.tar.gz taksiran.tar.gz.sig versi.json pasang.sh; do
    if [ ! -f "$KELUARAN/$f" ]; then
        echo "Ralat: $KELUARAN/$f tiada selepas bina." >&2
        exit 1
    fi
done

# bina.sh membaca versi dari kod; pastikan ia versi yang kita sangka.
if ! grep -q "\"$VERSI\"" "$KELUARAN/versi.json"; then
    echo "Ralat: versi.json tidak menyebut $VERSI." >&2
    exit 1
fi

# ---------------------------------------------------------------- 3. draf
# Release DRAF tidak dikembalikan oleh `releases/latest`, jadi sementara
# empat aset naik satu demi satu, telefon yang menyemak terus nampak release
# sebelumnya yang LENGKAP. Ini yang menggantikan keatoman `versi.json`
# ditulis-terakhir yang dahulu dipakai pada pelayan fail.
echo
echo "  ── Mencipta release draf ──"

# NOTA dikira DAHULU, bukan di dalam heredoc.
#
# `versi.NOTA` ialah senarai baris — app mencetaknya satu baris satu entri
# (lihat `kemas.py`, `"nota": [_bersih(n) for n in ...]`). `print(versi.NOTA)`
# akan menulis repr Python ke nota release, iaitu `['baris satu', 'baris dua']`.
# Dan di dalam heredoc, status keluar penggantian arahan itu tidak diperiksa,
# jadi kegagalan menghasilkan nota KOSONG sementara release tetap naik.
NOTA="$(python3 -c "
import sys
sys.path.insert(0, '$AKAR')
from zakat import versi
print('\n'.join(versi.NOTA))")"

if [ -z "$NOTA" ]; then
    echo "Ralat: nota release kosong — versi.NOTA tiada atau tidak boleh dibaca." >&2
    exit 1
fi

gh release create "$TAG" \
    --repo "$REPO" \
    --draft \
    --verify-tag \
    --title "$TAG" \
    --notes-file - <<NOTA
$NOTA
NOTA

echo "  → menaikkan aset …"
gh release upload "$TAG" \
    --repo "$REPO" \
    "$KELUARAN/taksiran.tar.gz" \
    "$KELUARAN/taksiran.tar.gz.sig" \
    "$KELUARAN/versi.json" \
    "$KELUARAN/pasang.sh"

# ---------------------------------------------------------------- 4. periksa
# Sebelum menerbitkan, pastikan keempat-empat benar-benar naik dan saiznya
# padan. Release yang diterbitkan dengan aset hilang ialah kegagalan yang
# hanya kelihatan di telefon, pada waktu yang paling teruk.
echo
echo "  ── Menyemak aset ──"
# SENARAI dikumpulkan dahulu, bukan disalurkan terus ke `while read`. Dalam
# paip, gelung itu berjalan dalam subshell — `exit 1` di dalamnya hanya
# menamatkan subshell, dan skrip ini akan terus menerbitkan release yang
# asetnya tidak lengkap. Itu kegagalan senyap yang sama kelas dengan
# `tar | grep -q` dalam bina.sh.
SENARAI_ASET="$(gh release view "$TAG" --repo "$REPO" --json assets \
    --jq '.assets[] | "\(.name) \(.size)"')"
while read -r nama saiz; do
    [ -n "$nama" ] || continue
    tempatan="$(stat -c%s "$KELUARAN/$nama" 2>/dev/null || echo 0)"
    if [ "$tempatan" != "$saiz" ]; then
        echo "  ✗ $nama: tempatan $tempatan bait, jauh $saiz bait" >&2
        exit 1
    fi
    echo "  ✓ $nama ($saiz bait)"
done <<<"$SENARAI_ASET"

JUMLAH="$(gh release view "$TAG" --repo "$REPO" --json assets --jq '.assets | length')"
if [ "$JUMLAH" != "4" ]; then
    echo "Ralat: $JUMLAH aset, sepatutnya 4. Release dibiarkan DRAF." >&2
    echo "       Betulkan, kemudian: gh release edit $TAG --draft=false --latest" >&2
    exit 1
fi

# ---------------------------------------------------------------- 5. terbit
# `--latest` EKSPLISIT. Lalai gh ialah "automatic based on date and version",
# dan GitHub menentukan release terakhir mengikut `created_at` — iaitu tarikh
# COMMIT, bukan tarikh ia diterbitkan. Kalau tuan pernah memotong release
# daripada commit yang lebih lama daripada release sebelumnya, lalai itu
# senyap-senyap mengekalkan penunjuk pada release LAMA sementara skrip ini
# melaporkan berjaya, dan telefon berkata "sudah terkini" selama-lamanya.
echo
echo "  ── Menerbitkan ──"
gh release edit "$TAG" --repo "$REPO" --draft=false --latest
echo "  ✓ diterbitkan dan ditandakan latest"

# ---------------------------------------------------------------- 6. sahkan
# Dari luar, melalui URL awam — bukan cakera tempatan. Inilah satu-satunya
# pemeriksaan yang menjawab soalan yang sebenar: apa yang telefon akan
# nampak?
echo
echo "  ── Mengesahkan melalui URL awam ──"

SAHKAN="$(gh api "repos/$REPO/releases/latest" --jq .tag_name)"
if [ "$SAHKAN" != "$TAG" ]; then
    echo "  ✗ releases/latest menunjuk pada $SAHKAN, bukan $TAG" >&2
    echo "    Ini perangkap created_at. Betulkan dengan:" >&2
    echo "      gh release edit $TAG --latest" >&2
    exit 1
fi
echo "  ✓ releases/latest = $TAG"

SEMENTARA="$(mktemp -d)"
trap 'rm -rf "$SEMENTARA"' EXIT

for f in taksiran.tar.gz taksiran.tar.gz.sig versi.json pasang.sh; do
    curl -fsSL --max-time 120 --retry 2 --retry-connrefused \
        "$URL/$f" -o "$SEMENTARA/$f" || {
        echo "  ✗ $f tidak dapat dimuat turun melalui URL awam" >&2
        exit 1
    }
    a="$(sha256sum < "$KELUARAN/$f" | cut -d' ' -f1)"
    b="$(sha256sum < "$SEMENTARA/$f" | cut -d' ' -f1)"
    if [ "$a" != "$b" ]; then
        echo "  ✗ $f: sha256 jauh berbeza daripada tempatan" >&2
        exit 1
    fi
    echo "  ✓ $f — dimuat turun, sha256 padan"
done

if ! grep -q "\"$VERSI\"" "$SEMENTARA/versi.json"; then
    echo "  ✗ versi.json di URL awam tidak menyebut $VERSI" >&2
    exit 1
fi

# Tandatangan diperiksa terhadap arkib yang BENAR-BENAR dimuat turun dari
# GitHub. Ini yang telefon akan buat.
echo "  → mengesahkan tandatangan arkib yang dimuat turun …"
python3 "$AKAR/alat/tanda.py" sahkan "$SEMENTARA/taksiran.tar.gz"

echo
echo "  Selesai. Telefon kini boleh memasang dengan:"
echo
echo "    curl -fsSL $URL/pasang.sh | bash"
echo
echo "  Cap jari kunci: $(python3 "$AKAR/alat/tanda.py" cap)"
echo

#!/usr/bin/env bash
# Build one category and photograph it:  bash library/check.sh <category-id>
# -> library/.check/<id>/k0-*.png ... k3-*.png: every figure frozen on its key 0..3 (fewer keys = repeats the last)
set -e
cd "$(dirname "$0")/.."
id="$1"; out="library/.check/$id"
rm -rf "$out"; mkdir -p "$out"
BLENDER="${BLENDER:-blender}"   # set BLENDER=/path/to/blender if it is not on PATH
"$BLENDER" -b -P library/build_library.py -- "$id" "$out" 2>&1 | grep -E "ERROR|WARNING|OK|Traceback|Error" || true
[ -f "$out/exercises.glb" ] || { echo "build failed"; exit 1; }
for k in 0 1 2 3; do
  timeout 120 env -u ELECTRON_RUN_AS_NODE ./node_modules/electron/dist/electron.exe . --user-data-dir="$TEMP/electron-check-$id" \n    --gallery="k=$k&lib=.check/$id/" --shot --out="$out/k$k" >/dev/null 2>&1 || echo "screenshot step timed out (k=$k)"
done
ls "$out"/*.png

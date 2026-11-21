#!/bin/bash
# lowercase_readme.sh ASSEMBLE_PY — a repo whose front page is readme.md, as
# NopSCADlib generates it, builds with that file as the home page, and a link to
# it goes to the home page.
set -uo pipefail
assemble=$1
here=$(dirname "$assemble")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

cp -r "$here/test/fixtures/model-only" "$work/repo"
mv "$work/repo/README.md" "$work/repo/readme.md"
printf '\n[Back to the top](readme.md#top)\n' >> "$work/repo/readme.md"

if ! python3 -B "$assemble" --repo "$work/repo" --theme "$here/../theme" --out "$work/src" \
     --render "$work/render" --site-dir "$work/site" --repository CameronBrooks11/engine-model-only >"$work/out.txt" 2>&1; then
  echo "FAIL readme.md: the build stopped:"; tail -3 "$work/out.txt"; exit 1
fi
failed=0
if grep -qF "Back to the top" "$work/src/index.md"; then
  echo "ok   readme.md is the home page"
else
  echo "FAIL readme.md is not the home page"; failed=1
fi
if grep -qF "[Back to the top](index.html#top)" "$work/src/index.md"; then
  echo "ok   a link to readme.md goes to the home page"
else
  echo "FAIL a link to readme.md was not rewritten:"; grep -F "Back to the top" "$work/src/index.md"; failed=1
fi
exit $failed

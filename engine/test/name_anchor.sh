#!/bin/bash
# name_anchor.sh CHECK_SITE_PY — a link to an <a name="..."> target resolves, as it
# does in a browser; NopSCADlib's generated readme.md marks its sections that way.
# A <meta name="..."> is not a link target.
set -uo pipefail
check=$1
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

mkdir "$work/site"
echo '{"base_path": "", "targets": [], "examples": []}' > "$work/summary.json"
printf '%s\n' '<meta name="viewport" content="width=device-width">' \
  '<a name="TOP"></a><a href="#TOP">Top</a>' > "$work/site/index.html"
if python3 -B "$check" "$work/site" "$work/summary.json" --no-models >"$work/out.txt"; then
  echo "ok   a link to <a name> resolves"; failed=0
else
  echo "FAIL a link to <a name> was refused:"; cat "$work/out.txt"; failed=1
fi

echo '<a href="#viewport">Viewport</a>' >> "$work/site/index.html"
if python3 -B "$check" "$work/site" "$work/summary.json" --no-models >"$work/out.txt"; then
  echo "FAIL a link to <meta name> was accepted"; failed=1
elif grep -qF "href=#viewport names no id" "$work/out.txt"; then
  echo "ok   a link to <meta name> is refused"
else
  echo "FAIL a link to <meta name> failed for another reason:"; cat "$work/out.txt"; failed=1
fi
exit $failed

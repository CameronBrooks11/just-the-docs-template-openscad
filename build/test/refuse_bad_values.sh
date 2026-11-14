#!/bin/bash
# refuse_bad_values.sh ASSEMBLE_PY — the engine must stop on a docs-site.yml value
# it doesn't know, rather than build as if the key weren't there.
set -uo pipefail
assemble=$1
here=$(dirname "$assemble")
failed=0

refuse() {  # refuse KEY BAD MESSAGE
  local key=$1 bad=$2 message=$3 work
  work=$(mktemp -d)
  cp -r "$here/test/fixtures/embed" "$work/repo"
  sed -i "/^$key:/d" "$work/repo/docs-site.yml"
  echo "$key: $bad" >> "$work/repo/docs-site.yml"
  if python3 -B "$assemble" --repo "$work/repo" --theme "$here/../theme" --out "$work/src" \
       --render "$work/render" --site-dir "$work/site" --repository CameronBrooks11/engine-embed >"$work/out.txt" 2>&1; then
    echo "FAIL $key: $bad was accepted"; failed=1; return
  fi
  if grep -q "$message" "$work/out.txt"; then
    echo "ok   $key: $bad is refused"
  else
    echo "FAIL $key: $bad stopped the build for another reason:"; tail -3 "$work/out.txt"; failed=1
  fi
}

refuse examples embedd "examples: embedd is not none or embed"
refuse color_scheme purple "color_scheme: purple is not auto, openscad-light or openscad-dark"
exit $failed

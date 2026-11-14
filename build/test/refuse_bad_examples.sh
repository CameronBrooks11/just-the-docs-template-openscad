#!/bin/bash
# refuse_bad_examples.sh ASSEMBLE_PY — the engine must stop on `examples: embedd`
# rather than build as if the key weren't there.
set -uo pipefail
assemble=$1
work=$(mktemp -d)
cp -r "$(dirname "$assemble")/test/fixtures/embed" "$work/repo"
sed -i 's/^examples: embed$/examples: embedd/' "$work/repo/docs-site.yml"
grep -q '^examples: embedd$' "$work/repo/docs-site.yml" || { echo "the fixture's examples line didn't change"; exit 1; }
if python3 -B "$assemble" --repo "$work/repo" --theme "$(dirname "$assemble")/../docs" --out "$work/src" \
     --render "$work/render" --site-dir "$work/site" --repository CameronBrooks11/engine-embed >"$work/out.txt" 2>&1; then
  echo "FAIL: examples: embedd was accepted"; exit 1
fi
grep -q 'examples: embedd is not none or embed' "$work/out.txt" || { echo "FAIL: stopped for another reason:"; tail -3 "$work/out.txt"; exit 1; }
echo "ok   examples: embedd is refused"

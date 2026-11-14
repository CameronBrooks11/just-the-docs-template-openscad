#!/usr/bin/env bash
# build_local.sh OUT_DIR
# Build the lite fixture's site as the engine does, without openscad-web, and
# run the checks. Gems install from docs/Gemfile.lock only (BUNDLE_FROZEN),
# into OUT_DIR/bundle, never globally. Needs Ruby 3.3, Bundler and OpenSCAD.
set -euo pipefail
out=${1:?usage: build_local.sh OUT_DIR}
here=$(cd "$(dirname "$0")" && pwd)
build=$(dirname "$here")
mkdir -p "$out"
out=$(cd "$out" && pwd)

python3 "$build/assemble.py" --repo "$here/fixtures/lite" --theme "$build/../docs" \
  --out "$out/src" --render "$out/render" --site-dir "$out/site" \
  --repository CameronBrooks11/engine-fixture
export BUNDLE_FROZEN=true BUNDLE_PATH="$out/bundle"
(cd "$out/src" && bundle install --quiet && JEKYLL_ENV=production bundle exec jekyll build --quiet \
  --destination "$out/site" --baseurl /engine-fixture 2>"$out/jekyll.log")
python3 "$build/check_site.py" "$out/site" "$out/render/summary.json" --no-models
python3 "$here/expect_lite.py" "$out/site" "$out/render/summary.json" --no-models

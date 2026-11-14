// Test the colour-scheme script in theme/_includes/head_custom.html against a
// stubbed browser: which stylesheet it picks, the toggle, and system changes.
// usage: node build/test/scheme_test.js
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const html = fs.readFileSync(path.join(__dirname, "../../theme/_includes/head_custom.html"), "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function run({ fixed, systemDark, stored, storageThrows }) {
  const source = script
    .replace("{{ '/assets/css/just-the-docs-' | relative_url }}", "/site/assets/css/just-the-docs-")
    .replace("{{ site.scheme_default | default: 'auto' }}", fixed);
  if (source.includes("{{")) throw new Error("a Liquid tag wasn't substituted");
  const link = { href: "/site/assets/css/just-the-docs-default.css", setAttribute(k, v) { this[k] = v; } };
  const attrs = {};
  const listeners = [];
  const media = { matches: systemDark, addEventListener: (e, fn) => listeners.push(fn) };
  const store = stored === undefined ? {} : { "openscad-docs-scheme": stored };
  const localStorage = {
    getItem(k) { if (storageThrows) throw new Error("blocked"); return k in store ? store[k] : null; },
    setItem(k, v) { if (storageThrows) throw new Error("blocked"); store[k] = v; },
  };
  const window = { matchMedia: () => media };
  const document = {
    querySelector: (sel) => (sel.includes("just-the-docs-default") ? link : null),
    documentElement: { setAttribute: (k, v) => { attrs[k] = v; }, getAttribute: (k) => attrs[k] },
  };
  window.localStorage = localStorage;
  vm.runInNewContext(source, { window, document, localStorage });
  const scheme = () => link.href.replace("/site/assets/css/just-the-docs-", "").replace(".css", "");
  return {
    scheme, attrs, store, window,
    systemChanges(dark) { media.matches = dark; listeners.forEach((fn) => fn()); },
  };
}

const cases = [];
function check(label, ok) { cases.push([label, ok]); }

check("auto, system dark: dark", run({ fixed: "auto", systemDark: true }).scheme() === "openscad-dark");
check("auto, system light: light", run({ fixed: "auto", systemDark: false }).scheme() === "openscad-light");
check("fixed dark, system light: dark", run({ fixed: "openscad-dark", systemDark: false }).scheme() === "openscad-dark");
check("fixed light, system dark: light", run({ fixed: "openscad-light", systemDark: true }).scheme() === "openscad-light");
check("a stored choice beats a fixed scheme",
  run({ fixed: "openscad-dark", systemDark: true, stored: "openscad-light" }).scheme() === "openscad-light");
check("an unknown stored value is ignored",
  run({ fixed: "auto", systemDark: true, stored: "purple" }).scheme() === "openscad-dark");
check("data-scheme matches the stylesheet",
  run({ fixed: "auto", systemDark: true }).attrs["data-scheme"] === "openscad-dark");
{
  const p = run({ fixed: "auto", systemDark: true });
  p.window.openscadDocsToggleScheme();
  check("the toggle switches dark to light", p.scheme() === "openscad-light");
  check("the toggle remembers the choice", p.store["openscad-docs-scheme"] === "openscad-light");
  p.window.openscadDocsToggleScheme();
  check("the toggle switches back", p.scheme() === "openscad-dark");
}
{
  const p = run({ fixed: "auto", systemDark: false });
  p.systemChanges(true);
  check("auto follows a system change", p.scheme() === "openscad-dark");
}
{
  const p = run({ fixed: "auto", systemDark: false, stored: "openscad-light" });
  p.systemChanges(true);
  check("a stored choice survives a system change", p.scheme() === "openscad-light");
}
{
  const p = run({ fixed: "auto", systemDark: true, storageThrows: true });
  check("blocked storage still follows the system", p.scheme() === "openscad-dark");
  p.window.openscadDocsToggleScheme();
  check("blocked storage still toggles", p.scheme() === "openscad-light");
}

let failed = 0;
for (const [label, ok] of cases) {
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${label}`);
}
console.log(failed ? `${failed} failed` : "all scheme checks pass");
process.exit(failed ? 1 : 0);

---
name: tool-web
description: Build a lightweight single-file web application with no external dependencies
argument-hint: <description of what to build>
---

# Lightweight Web Tool

Build a self-contained, single-file `.html` web application. Everything — HTML, CSS, JavaScript — lives in one file. No build step, no frameworks, no external dependencies.

## Core Rules

1. **Single `.html` file** — all CSS in `<style>`, all JS in `<script>`
2. **No frameworks** — no React, Vue, Angular, Svelte, Web Components, etc.
3. **No CSS frameworks** — no Bootstrap, Tailwind, Bulma, etc.
4. **No external dependencies** unless explicitly approved (see External Dependencies section)
5. **Fast loading** — with no deps, the page should render near-instantly
6. **Modern browsers only** — target current Chrome, Firefox, Safari, Edge. No IE, no polyfills
7. **Clean console** — zero warnings, zero errors, no stray `console.log`
8. **Works from `file:///`** where possible (see Compatibility section)
9. **Responsive** — must work well on mobile (320px minimum viewport)
10. **Add to Home Screen ready** — should work as a full-screen iOS/Android home screen app

Any of these rules may be broken with a good reason and explicit user approval.

## HTML Boilerplate

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Tool Name</title>
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Tool Name">
  <style>
    /* House Style — Section 1 (Reset), Section 2 (Typography), Section 3 (Color). See CSS section below. */
  </style>
</head>
<body>

  <!-- Markup here -->

  <script>
    /* JS here */
  </script>
</body>
</html>
```

Keep it minimal. No unnecessary meta tags, no favicon link (browsers handle the 404 silently).

### Add to Home Screen (iOS / Android)

The boilerplate above includes the meta tags needed for iOS "Add to Home Screen" to launch as a full-screen standalone app (no Safari chrome).

**Safe areas** — on notched/Dynamic Island iPhones, `viewport-fit=cover` lets the page extend edge-to-edge. Use `env()` to avoid content behind the notch or home indicator:

```css
body {
  padding-top: env(safe-area-inset-top);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
  padding-bottom: env(safe-area-inset-bottom);
}
```

Or apply selectively to specific containers — a full-bleed header might want to extend behind the status bar with its own internal padding.

**Status bar** — `black-translucent` makes the status bar overlay the page with white text. This looks best when the page has a dark or colored header. Use `default` for a standard light status bar, or `black` for a solid black bar.

**Touch behavior** — prevent rubber-band overscroll and accidental text selection in app-like UIs:

```css
html { overscroll-behavior: none; }
body { -webkit-user-select: none; user-select: none; }

/* Re-enable selection on content that should be selectable */
.selectable { -webkit-user-select: text; user-select: text; }
```

**Standalone detection** — detect if running as a home screen app:

```js
const isStandalone = window.navigator.standalone === true
  || window.matchMedia('(display-mode: standalone)').matches;
```

**Note:** Add to Home Screen requires the page to be served over HTTPS (or localhost). It will not work from `file:///` URLs. If the tool is intended for home screen use, mention this to the user.

## CSS

The CSS is a **House Style** in three sections — Reset (required), Typography (optional), Color (optional) — all in one inline `<style>` in `<head>`. Sections are independent: keep only Section 1, or 1+2, for a trivial output. Include all three by default.

**The only knobs you should turn:**

- `--hue` (0–360) — drives the entire accent. Match the doc: ~30 warm, ~140 green, ~220 blue, ~300 violet, ~330 magenta.
- `--font-body` / `--font-heading` — pick from `--sans-serif`, `--serif`, `--code`, `--slab`.

Heading weights are standardized (heavier as larger) — do not change. Theme auto-follows OS; force with `data-theme="light"` or `data-theme="dark"` on `<html>`.

**Embed note:** if mounted somewhere `:root`/`html`/`body` aren't the real root (shadow DOM, sandbox iframe), move the Section 3 `:root` blocks to a `.app` wrapper class, wrap the page in `<div class="app">`, and paint `--bg` on `.app` with `min-height: 100vh`. Normal pages: use as-is.

### Section 1 — Reset (required)

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; }
html { background: var(--bg, transparent); min-height: 100%; }
body { min-height: 100dvh; line-height: calc(1em + 0.5rem); -webkit-text-size-adjust: 100%; }
img, picture, svg, video { display: block; max-width: 100%; }
input, button, textarea, select { font: inherit; }
pre { overflow: auto; }
p, li, figcaption { text-wrap: pretty; }
h1, h2, h3, h4 { text-wrap: balance; }
.template { display: none !important; }
```

`.template` is required by the stamp pattern (see JavaScript section). `--bg` falls back to `transparent` so this section works without Section 3.

### Section 2 — Typography (optional)

```css
:root {
  --sans-serif: system-ui, sans-serif;
  --serif: 'Iowan Old Style', Palatino, 'Palatino Linotype', serif;
  --code: ui-monospace, 'Cascadia Code', Menlo, Consolas, monospace;
  --slab: Rockwell, 'Rockwell Nova', 'Sitka Small', Georgia, serif;
  --font-body: var(--sans-serif);
  --font-heading: var(--slab);
}
body { font-family: var(--font-body); font-weight: 400; }
h1, h2, h3, h4 { font-family: var(--font-heading); }
h1 { font-size: clamp(2.5rem, 8vw, 4.25rem);   font-weight: 900; line-height: 1.05; letter-spacing: -0.02em; }
h2 { font-size: clamp(1.85rem, 5vw, 2.6rem);   font-weight: 800; line-height: 1.12; letter-spacing: -0.015em; }
h3 { font-size: clamp(1.45rem, 3.5vw, 1.85rem); font-weight: 700; line-height: 1.2; }
h4 { font-size: clamp(1.2rem, 2.5vw, 1.4rem);   font-weight: 600; line-height: 1.25; }
code, pre { font-family: var(--code); }
```

Sizes are fluid via `clamp()` — no breakpoints needed for headings. System fonts only; no webfonts, no Google Fonts. For other stacks, see [modernfontstacks.com](https://modernfontstacks.com) and swap into the four named tokens.

### Section 3 — Color (optional)

```css
:root {
  --hue: 30;
  color-scheme: light dark;
  --bg:           light-dark(oklch(0.97 0.012 90),     oklch(0.17 0.02 280));
  --bg-muted:     light-dark(oklch(0.93 0.014 90),     oklch(0.23 0.02 280));
  --text-heading: light-dark(oklch(0.22 0.02 280),     oklch(0.96 0.012 90));
  --text-body:    light-dark(oklch(0.36 0.018 280),    oklch(0.84 0.015 90));
  --text-muted:   light-dark(oklch(0.52 0.016 280),    oklch(0.66 0.016 90));
  --border:       light-dark(oklch(0.80 0.015 90),     oklch(0.36 0.02 280));
  --field-text:   light-dark(oklch(0.28 0.02 280),     oklch(0.90 0.014 90));
  --link:         light-dark(oklch(0.52 0.13 var(--hue)),  oklch(0.74 0.13 var(--hue)));
  --link-hover:   light-dark(oklch(0.44 0.14 var(--hue)),  oklch(0.82 0.12 var(--hue)));
  --accent:       light-dark(oklch(0.62 0.15 var(--hue)),  oklch(0.70 0.15 var(--hue)));
  --on-accent:    light-dark(oklch(0.98 0.01 90),      oklch(0.17 0.02 280));
}
[data-theme="light"] { color-scheme: light; }
[data-theme="dark"]  { color-scheme: dark; }

body { background: var(--bg); color: var(--text-body); transition: background .2s, color .2s; }
h1, h2, h3, h4 { color: var(--text-heading); }
a { color: var(--link); text-underline-offset: 2px; }
a:hover { color: var(--link-hover); }
code, pre { background: var(--bg-muted); border-radius: 6px; }
code { color: var(--text-body); padding: 0.1rem 0.35rem; }
pre { border: 1px solid var(--border); padding: 1rem; }
input, textarea, select { background: var(--bg); color: var(--field-text); border: 1px solid var(--border); border-radius: 6px; padding: 0.55rem 0.75rem; }
::placeholder { color: var(--text-muted); opacity: 1; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }

@media (prefers-reduced-motion: reduce) {
  body { transition: none; }
}
```

**How the theme switch works.** `color-scheme: light dark` at `:root` tells the browser the page supports both modes and to use the user's OS preference. `light-dark(L, D)` returns `L` when the used color scheme is light, `D` when dark — so each token reads naturally with light value first. `[data-theme="light"]` / `[data-theme="dark"]` on `<html>` force the scheme, and every `light-dark()` value follows automatically. No duplicated palette, no second selector.

**About the body transition.** It only animates on *changes* after first paint — typically a user theme toggle or an OS-level preference flip — not on initial render. The `prefers-reduced-motion` block disables it for users with the OS reduce-motion preference set; it's an accessibility courtesy, not a flash mitigation.

**Browser support:** `oklch()` needs Chrome 111+ / Safari 15.4+ / Firefox 113+. `light-dark()` needs Chrome 123+ / Safari 17.5+ / Firefox 120+. The `oklch(from ...)` relative-color form (hover guidance, chart series) needs Chrome 119+ / Safari 16.4+ / Firefox 128+. All comfortably inside the modern-browsers target.

**Heading hue is fixed at 280 (cool)** regardless of `--hue` — by design, to pair cool text with a warm bg and a hue-driven accent. Changing `--hue` won't shift heading tint.

### Styling new elements — rules

Build everything from tokens. Never hardcode a color or px font size.

- **Surfaces:** page = `--bg`; any raised/inset element (card, sidebar, well, table header, input) = `--bg-muted`. No third surface — use a `--border` hairline for more separation.
- **Text tiers, in order:** titles/headings = `--text-heading`; body/content = `--text-body`; captions, metadata, eyebrows, helper text = `--text-muted`. Never mix tiers up.
- **Accent = action/emphasis only**, small areas: buttons, active/selected states, links, focus, badges, key data points. Text on accent fill = `--on-accent`. Never flood the reading area with accent.
- **Borders/dividers:** `--border`, 1px, sparingly. Prefer spacing over rules.
- **Hover:** links → `--link-hover`; accent surfaces → `oklch(from var(--accent) calc(l - 0.06) c h)`. Never remove `:focus-visible`.
- **Spacing:** `rem`, multiples of `0.25rem`; cap prose width at ~40rem; more space above a heading than below.
- **Radius/shadow:** ~6px small elements, ~10px cards; shadows subtle and tinted, never pure black; in dark mode, prefer a border over a shadow.
- **Charts:** rotate `--hue` for series (`oklch(0.62 0.15 calc(var(--hue) + 60))`, `+120`, …); gridlines `--border`, labels `--text-muted`, highlight `--accent`.
- **Self-test:** every addition must read correctly in light *and* dark. It will if you used tokens; if it breaks in one theme, you hardcoded something.
- **Restraint:** whitespace and hierarchy over decoration. One accent. No gradients or multi-color schemes unless asked.

### Layout responsive breakpoints

Heading sizes are already fluid via `clamp()` — no media queries needed for type. For container layout, use mobile-first `min-width` breakpoints:

```css
.container { padding: 1rem; max-width: 100%; }
@media (min-width: 640px)  { .container { padding: 2rem; } }
@media (min-width: 1024px) { .container { max-width: 960px; margin: 0 auto; } }
```

Use `clamp()` for any other fluid sizing. Test at 320px minimum viewport — no horizontal scrolling at any size.

## JavaScript

### Configuration

Put user-configurable values (colors, sizes, defaults, thresholds) in a clear config object at the top of `<script>` with comments explaining each option:

```js
const CONFIG = {
  maxItems: 50,           // Maximum items to display
  refreshMs: 5000,        // Auto-refresh interval
  defaultTheme: 'light',  // 'light' or 'dark'
};
```

This makes it easy for users to customize behavior without digging through code.

### Helper Functions

Include these at the top of `<script>` (after config):

```js
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function el(tag, ...args) {
  const e = document.createElement(tag);
  for (const arg of args) {
    if (typeof arg === 'string') e.append(arg);
    else if (arg instanceof Node) e.appendChild(arg);
    else if (arg && typeof arg === 'object') {
      for (const [k, v] of Object.entries(arg)) {
        if (typeof v === 'function' && k.startsWith('on')) {
          e.addEventListener(k.slice(2), v);
        } else {
          e.setAttribute(k, v);
        }
      }
    }
  }
  return e;
}
```

**`$` and `$$`** mirror browser devtools conventions. `$$` returns a real Array (not NodeList), so `.map()`, `.filter()`, `.find()` all work. The second argument scopes the search:

```js
$('.sidebar')                              // first match in document
$$('.item')                                // all matches → Array
$$('.item').map(i => i.textContent)         // chainable
$('.name', card)                           // scoped to a parent element
$$('.tag', card)                           // all .tag within card
```

**`el()`** takes a tag name, then any mix of strings (text content), objects (attributes), and Nodes (children):

```js
el('hr')
el('input', { type: 'text', placeholder: 'Search...' })
el('p', 'Hello world')
el('div', { class: 'card' },
  el('h2', 'Title'),
  el('p', 'Description')
)
el('ul', ...items.map(item => el('li', item.name)))  // spread for arrays
```

**Event listeners** — keys starting with `on` whose value is a function are bound via `addEventListener` instead of being set as attributes:

```js
el('button', { class: 'primary', onclick: () => save() }, 'Save')

el('input', {
  type: 'text',
  oninput: e => filter(e.target.value),
  onfocus: e => e.target.select(),
})
```

This mirrors HTML inline-handler syntax (`onclick`, `oninput`) but uses `addEventListener` under the hood, so multiple listeners stack instead of overwriting. For event-listener options (`{ once: true }`, `{ passive: true }`), bind on the returned element directly. Prefer event delegation (see below) for dynamic/stamped content — keep `on*` handlers for one-off elements created with `el()`.

### Template / Stamp Pattern

Templates are real HTML elements hidden by the `.template` class. Clone them to create instances. This keeps markup in the HTML where it's visible and editable — no template strings, no innerHTML.

**HTML:**
```html
<ul id="people">
  <li class="template person">
    <span class="name"></span> — <span class="role"></span>
  </li>
</ul>
```

**JS:**
```js
function stamp(selector, { parent, position = 'append' } = {}) {
  const tmpl = $(selector);
  const clone = tmpl.cloneNode(true);
  clone.classList.remove('template');
  const container = parent || tmpl.parentNode;
  if (position === 'prepend') container.prepend(clone);
  else if (position === 'before') tmpl.before(clone);
  else if (position === 'after') tmpl.after(clone);
  else container.appendChild(clone);
  return clone;
}

const people = {};

function addPerson(id, name, role) {
  const p = stamp('.person.template');
  $('.name', p).textContent = name;
  $('.role', p).textContent = role;
  p.dataset.id = id;
  people[id] = p;
}

function removePerson(id) {
  people[id].remove();
  delete people[id];
}

function updatePerson(id, name, role) {
  const p = people[id];
  $('.name', p).textContent = name;
  $('.role', p).textContent = role;
}
```

**Why this pattern works:**
- Templates are visible in source — easy to read, style, inspect
- No string building, no innerHTML, no XSS surface
- Clone + populate is predictable, zero magic
- Registry object makes removal and updates trivial
- Scoped `$('.name', p)` reads naturally
- `stamp()` options: `parent` targets a different container, `position` controls insertion (`'append'`, `'prepend'`, `'before'`, `'after'`)

### Hash State

Encode meaningful UI state in `location.hash` so the page can be refreshed, deep-linked, and shared:

```js
function getHash() {
  return Object.fromEntries(new URLSearchParams(location.hash.slice(1)));
}

function setHash(params) {
  location.hash = new URLSearchParams(params).toString();
}

window.addEventListener('hashchange', render);
window.addEventListener('DOMContentLoaded', render);

function render() {
  const state = getHash();
  // update DOM based on state
}
```

Flat key=value pairs only. `URLSearchParams` handles encoding/decoding automatically.

Examples: `#view=settings`, `#q=search+term&page=2`, `#tab=history&id=42`.

### Event Delegation

Prefer delegating events to a container rather than attaching listeners to every element. This works automatically for stamped elements without re-attaching listeners:

```js
$('#people').addEventListener('click', e => {
  const person = e.target.closest('.person');
  if (!person) return;
  const id = person.dataset.id;
  // handle click
});
```

### Prefer Native Elements

Use HTML's built-in interactive elements before building custom ones:
- `<details>` / `<summary>` for collapsible sections
- `<dialog>` for modals (with `.showModal()`)
- `<input type="date|time|color|range">` for pickers
- `<progress>` and `<meter>` for progress/gauges
- `<datalist>` for autocomplete suggestions
- `<fieldset>` / `<legend>` for grouped form controls

## Worked Example

A complete, copy-pasteable file showing all three House Style sections, the stamp pattern, and `el()` event binding. Save as `notes.html` and open it — works from `file:///`. Try toggling your OS dark mode, or set `data-theme="dark"` on `<html>`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Notes</title>
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-title" content="Notes">
  <style>
    /* Section 1 — Reset */
    *, *::before, *::after { box-sizing: border-box; margin: 0; }
    html { background: var(--bg, transparent); min-height: 100%; }
    body { min-height: 100dvh; line-height: calc(1em + 0.5rem); -webkit-text-size-adjust: 100%; }
    img, picture, svg, video { display: block; max-width: 100%; }
    input, button, textarea, select { font: inherit; }
    pre { overflow: auto; }
    p, li, figcaption { text-wrap: pretty; }
    h1, h2, h3, h4 { text-wrap: balance; }
    .template { display: none !important; }

    /* Section 2 — Typography */
    :root {
      --sans-serif: system-ui, sans-serif;
      --serif: 'Iowan Old Style', Palatino, 'Palatino Linotype', serif;
      --code: ui-monospace, 'Cascadia Code', Menlo, Consolas, monospace;
      --slab: Rockwell, 'Rockwell Nova', 'Sitka Small', Georgia, serif;
      --font-body: var(--sans-serif);
      --font-heading: var(--slab);
    }
    body { font-family: var(--font-body); font-weight: 400; }
    h1, h2, h3, h4 { font-family: var(--font-heading); }
    h1 { font-size: clamp(2.5rem, 8vw, 4.25rem); font-weight: 900; line-height: 1.05; letter-spacing: -0.02em; }
    h2 { font-size: clamp(1.45rem, 3.5vw, 1.85rem); font-weight: 700; line-height: 1.2; }
    code, pre { font-family: var(--code); }

    /* Section 3 — Color */
    :root {
      --hue: 220;
      color-scheme: light dark;
      --bg:           light-dark(oklch(0.97 0.012 90),     oklch(0.17 0.02 280));
      --bg-muted:     light-dark(oklch(0.93 0.014 90),     oklch(0.23 0.02 280));
      --text-heading: light-dark(oklch(0.22 0.02 280),     oklch(0.96 0.012 90));
      --text-body:    light-dark(oklch(0.36 0.018 280),    oklch(0.84 0.015 90));
      --text-muted:   light-dark(oklch(0.52 0.016 280),    oklch(0.66 0.016 90));
      --border:       light-dark(oklch(0.80 0.015 90),     oklch(0.36 0.02 280));
      --field-text:   light-dark(oklch(0.28 0.02 280),     oklch(0.90 0.014 90));
      --link:         light-dark(oklch(0.52 0.13 var(--hue)),  oklch(0.74 0.13 var(--hue)));
      --link-hover:   light-dark(oklch(0.44 0.14 var(--hue)),  oklch(0.82 0.12 var(--hue)));
      --accent:       light-dark(oklch(0.62 0.15 var(--hue)),  oklch(0.70 0.15 var(--hue)));
      --on-accent:    light-dark(oklch(0.98 0.01 90),      oklch(0.17 0.02 280));
    }
    [data-theme="light"] { color-scheme: light; }
    [data-theme="dark"]  { color-scheme: dark; }
    body { background: var(--bg); color: var(--text-body); transition: background .2s, color .2s; }
    h1, h2, h3, h4 { color: var(--text-heading); }
    code, pre { background: var(--bg-muted); border-radius: 6px; }
    code { color: var(--text-body); padding: 0.1rem 0.35rem; }
    input, textarea { background: var(--bg); color: var(--field-text); border: 1px solid var(--border); border-radius: 6px; padding: 0.55rem 0.75rem; }
    ::placeholder { color: var(--text-muted); opacity: 1; }
    :focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
    @media (prefers-reduced-motion: reduce) { body { transition: none; } }

    /* Page — composed entirely from tokens */
    .page { max-width: 40rem; margin: 0 auto; padding: 2rem 1rem; }
    .meta { color: var(--text-muted); font-size: 0.875rem; }
    .card {
      background: var(--bg-muted);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.25rem 1.5rem;
      margin-top: 1.25rem;
      list-style: none;
    }
    .card h2 { margin-bottom: 0.25rem; }
    .row { display: flex; gap: 0.5rem; margin-top: 1.25rem; }
    .row input { flex: 1; }
    .btn {
      background: var(--accent); color: var(--on-accent);
      border: 0; border-radius: 6px;
      padding: 0.55rem 1rem; font-weight: 600; cursor: pointer;
    }
    .btn:hover { background: oklch(from var(--accent) calc(l - 0.06) c h); }
    .del {
      background: transparent; color: var(--text-muted);
      border: 0; cursor: pointer; padding: 0.25rem 0.5rem; margin-left: auto;
    }
    .del:hover { color: var(--text-body); }
    .note-head { display: flex; align-items: baseline; gap: 0.5rem; }
  </style>
</head>
<body>
  <main class="page">
    <h1>Notes</h1>
    <p class="meta">A small demo. Toggle your OS theme, or set <code>data-theme="dark"</code> on &lt;html&gt;.</p>

    <ul id="notes">
      <li class="template card note">
        <div class="note-head">
          <h2 class="title"></h2>
          <button class="del" type="button" aria-label="Delete">×</button>
        </div>
        <p class="meta when"></p>
      </li>
    </ul>

    <form class="row" id="add-form">
      <input id="add-input" type="text" placeholder="New note…" required>
      <button class="btn" type="submit">Add</button>
    </form>
  </main>

  <script>
    const $ = (sel, ctx = document) => ctx.querySelector(sel);

    function stamp(selector) {
      const tmpl = $(selector);
      const clone = tmpl.cloneNode(true);
      clone.classList.remove('template');
      tmpl.parentNode.appendChild(clone);
      return clone;
    }

    function addNote(title) {
      const n = stamp('.note.template');
      $('.title', n).textContent = title;
      $('.when',  n).textContent = new Date().toLocaleString();
    }

    // Delegated delete — works for current and future notes.
    $('#notes').addEventListener('click', e => {
      const del = e.target.closest('.del');
      if (del) del.closest('.note').remove();
    });

    $('#add-form').onsubmit = e => {
      e.preventDefault();
      const input = $('#add-input');
      const v = input.value.trim();
      if (v) addNote(v);
      input.value = '';
    };

    addNote('Welcome');
  </script>
</body>
</html>
```

**What to notice.** Page-specific CSS never names a color or px font size — every value is a token (`--bg-muted`, `--text-muted`, `--accent`, `--on-accent`, `--border`). The button hover uses the relative-color trick. The `.note` template lives in the DOM behind `.template { display: none }`, stamped to create each card. Delete uses delegation on `#notes`, so newly added notes work without re-binding. Open the file, flip your OS theme, and everything reads correctly in both — that's the self-test.

## External Dependencies

### Policy

**Default: no external dependencies.** The page should require zero network requests beyond itself.

If a dependency is genuinely needed (non-trivial feature unreasonable to reimplement), it must be:
- **Minimal** — small, focused, single-purpose
- **Standalone** — zero transitive dependencies
- **Mature** — stable API, several years old, widely used
- **Reputable** — known maintainers, active maintenance
- **Secure** — no known vulnerabilities
- **Permissive license** — MIT, BSD, ISC, Apache 2.0
- **Explicitly approved** — always ask the user before adding any dependency

### Approved CDNs

If a dependency is approved, load from one of these:
- `cdn.jsdelivr.net` — reliable, serves npm packages, supports SRI
- `unpkg.com` — serves npm packages directly
- `cdnjs.cloudflare.com` — Cloudflare-backed, curated set
- `esm.sh` — ESM module CDN, great for modern-browser-only targets

Always pin the version and use SRI hashes:
```html
<script src="https://cdn.jsdelivr.net/npm/marked@14.1.0/marked.min.js"
        integrity="sha384-..." crossorigin="anonymous"></script>
```

### Acceptable Libraries (examples — still require explicit approval)

| Library | Size | Purpose | Why acceptable |
|---------|------|---------|----------------|
| `marked` | ~40KB | Markdown → HTML | Complex parser, mature, zero deps |
| `DOMPurify` | ~20KB | HTML sanitization | Security-critical, hard to DIY safely |
| `highlight.js` | ~30KB core | Syntax highlighting | Complex grammars, unreasonable to rewrite |
| `Papa Parse` | ~25KB | CSV parsing | Edge cases (nested quotes, streaming) |
| `Sortable` | ~40KB | Drag-and-drop sorting | Touch support, animations, edge cases |

### Never Use

| Library/Category | Reason |
|------------------|--------|
| React, Vue, Angular, Svelte, htm | Frameworks / framework-like — defeats the entire purpose |
| jQuery | Unnecessary — modern DOM APIs cover everything |
| Bootstrap, Tailwind, Bulma | CSS frameworks — violates no-framework rule |
| Lodash / Underscore | Native JS covers it all: `Array.prototype.*`, `Object.entries`, `structuredClone`, etc. |
| Axios | `fetch()` is built-in |
| Moment.js | Deprecated, enormous; use `Intl.DateTimeFormat` or native `<input type="date">` |
| D3 (full bundle) | Massive (~240KB); if charting needed, build simple SVG charts by hand or use a tiny focused lib |
| Any library with transitive dependencies | Pulls in a tree of unknowns — violates standalone rule |

## Images and Icons

- Prefer inline SVGs — they're scalable, styleable with CSS, and require no network requests
- Keep SVGs minimal: run through an optimizer mentally, remove unnecessary attributes
- For simple shapes, consider CSS-only solutions (borders, gradients, clip-path)
- Never use icon fonts (Font Awesome, etc.) — they're external deps and heavy

## Design Principles

- **Minimal, clean, no clutter** — every element earns its place
- **Strong visual hierarchy** — heading / body / muted text tiers should be immediately obvious; use the `--text-*` tokens, don't invent new tiers
- **Generous whitespace** — when in doubt, add more space
- **Subtle interactions** — small transitions (150–200ms) on hover/focus. No flashy animations
- **Dark mode is built in** — Section 3 handles auto-follow-OS plus `data-theme` override. Test every change in both themes
- **Accessibility basics** — semantic HTML, visible focus states (`:focus-visible` is pre-wired), sufficient color contrast (tokens are tuned for AA)

## `file:///` Compatibility

The page should work when opened directly as a file. This means:

**Works from `file:///`:**
- All inline CSS and JS
- `location.hash` for state
- `localStorage` / `sessionStorage`
- Inline SVGs, `<canvas>`
- Most Web APIs (`crypto`, `Intl`, `Web Audio`, etc.)

**Does NOT work from `file:///`:**
- `fetch()` to relative paths — CORS restriction on file: origins
- ES module `import` — blocked by CORS in some browsers
- Service Workers
- `SharedArrayBuffer` / COOP/COEP headers

If the tool requires HTTP-only features, tell the user and suggest:
```
python3 -m http.server 8000
```

## Testing

Test with [rodney](https://github.com/simonw/rodney), a Chrome automation CLI:

```bash
# Start visible browser
rodney start --show

# Open the page (file:// or http://)
rodney open file:///path/to/tool.html

# Verify basics
rodney title
rodney waitidle
rodney exists ".expected-element"
rodney visible "#main"

# Test interactions
rodney click ".button"
rodney input "#search" "test query"
rodney text ".result"

# Run JS assertions
rodney js "document.querySelectorAll('.item').length"
rodney assert "document.title !== ''"

# Check accessibility tree
rodney ax-tree

rodney stop
```

Write a brief test sequence and run it to verify the tool works after building it.


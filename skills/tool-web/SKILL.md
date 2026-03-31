---
name: tool-web
description: Build a lightweight single-file web application with no external dependencies
user_invocable: true
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
    /* CSS here */
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

### Minimal Reset

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { min-height: 100dvh; -webkit-font-smoothing: antialiased; }
img, svg { display: block; max-width: 100%; }
input, button, textarea, select { font: inherit; }
```

### Template Hiding

```css
.template { display: none !important; }
```

### Typography

Use system font stacks from [modernfontstacks.com](https://modernfontstacks.com). No web fonts, no Google Fonts.

**Recommended pairings — pick a readable stack for body, something with more character for headings:**

Body/UI (prioritize readability):
- **System UI**: `system-ui, sans-serif`
- **Neo-Grotesque**: `Inter, Roboto, 'Helvetica Neue', 'Arial Nova', 'Nimbus Sans', Arial, sans-serif`
- **Humanist**: `Seravek, 'Gill Sans Nova', Ubuntu, Calibri, 'DejaVu Sans', source-sans-pro, sans-serif`

Headings (more character):
- **Geometric Humanist**: `Avenir, Montserrat, Corbel, 'URW Gothic', source-sans-pro, sans-serif`
- **Classical Humanist**: `Optima, Candara, 'Noto Sans', source-sans-pro, sans-serif`
- **Old Style**: `'Iowan Old Style', 'Palatino Linotype', 'URW Palladio L', P052, serif`
- **Transitional**: `Charter, 'Bitstream Charter', 'Sitka Text', Cambria, serif`
- **Didone**: `Didot, 'Bodoni MT', 'Noto Serif Display', 'URW Palladio L', P052, Sylfaen, serif`

Code:
- **Monospace Code**: `ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace`

All available stacks for reference:
- **System UI**: `system-ui, sans-serif`
- **Transitional**: `Charter, 'Bitstream Charter', 'Sitka Text', Cambria, serif`
- **Old Style**: `'Iowan Old Style', 'Palatino Linotype', 'URW Palladio L', P052, serif`
- **Humanist**: `Seravek, 'Gill Sans Nova', Ubuntu, Calibri, 'DejaVu Sans', source-sans-pro, sans-serif`
- **Geometric Humanist**: `Avenir, Montserrat, Corbel, 'URW Gothic', source-sans-pro, sans-serif`
- **Classical Humanist**: `Optima, Candara, 'Noto Sans', source-sans-pro, sans-serif`
- **Neo-Grotesque**: `Inter, Roboto, 'Helvetica Neue', 'Arial Nova', 'Nimbus Sans', Arial, sans-serif`
- **Monospace Slab Serif**: `'Nimbus Mono PS', 'Courier New', monospace`
- **Monospace Code**: `ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace`
- **Industrial**: `Bahnschrift, 'DIN Alternate', 'Franklin Gothic Medium', 'Nimbus Sans Narrow', sans-serif-condensed, sans-serif`
- **Rounded Sans**: `ui-rounded, 'Hiragino Maru Gothic ProN', Quicksand, Comfortaa, Manjari, 'Arial Rounded MT', 'Arial Rounded MT Bold', Calibri, source-sans-pro, sans-serif`
- **Slab Serif**: `Rockwell, 'Rockwell Nova', 'Roboto Slab', 'DejaVu Serif', 'Sitka Small', serif`
- **Antique**: `Superclarendon, 'Bookman Old Style', 'URW Bookman', 'URW Bookman L', 'Georgia Pro', Georgia, serif`
- **Didone**: `Didot, 'Bodoni MT', 'Noto Serif Display', 'URW Palladio L', P052, Sylfaen, serif`
- **Handwritten**: `'Segoe Print', 'Bradley Hand', Chilanka, TSCu_Comic, casual, cursive`

### Font Weight ↔ Size Relationship

As fonts get larger, decrease weight so perceived line thickness stays roughly constant:

```css
h1 { font-size: 2.5rem; font-weight: 300; }
h2 { font-size: 1.75rem; font-weight: 400; }
h3 { font-size: 1.25rem; font-weight: 500; }
body { font-size: 1rem; font-weight: 400; }
small { font-size: 0.875rem; font-weight: 450; }
```

Adjust to taste — the principle is visual consistency of stroke width across sizes, not exact numbers.

### Responsive Design

Mobile-first. Use `min-width` breakpoints:

```css
.container { padding: 1rem; max-width: 100%; }

@media (min-width: 640px) { .container { padding: 2rem; } }
@media (min-width: 1024px) { .container { max-width: 960px; margin: 0 auto; } }
```

Use `clamp()` for fluid sizing: `font-size: clamp(1rem, 2.5vw, 1.25rem);`

Test at 320px minimum viewport width. No horizontal scrolling at any size.

### Visual Hierarchy

- Use spacing (margin/padding) more than decoration (borders, backgrounds) to create structure
- Limit to 2-3 font sizes plus one accent color
- Primary text: `#111`. Secondary: `#555`. Tertiary: `#999`
- One accent color max. Derive hover/active states with opacity
- When in doubt, add more whitespace

## JavaScript

### Helper Functions

Include these at the top of `<script>`:

```js
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function el(tag, ...args) {
  const e = document.createElement(tag);
  for (const arg of args) {
    if (typeof arg === 'string') e.append(arg);
    else if (arg instanceof Node) e.appendChild(arg);
    else if (arg && typeof arg === 'object') {
      for (const [k, v] of Object.entries(arg)) e.setAttribute(k, v);
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

`el()` is deliberately simple — no event binding, no style objects, no special-casing. Attach listeners on the returned element: `myBtn.onclick = handler` or `myBtn.addEventListener('click', handler)`.

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
- **Strong visual hierarchy** — primary, secondary, tertiary levels should be immediately obvious
- **Generous whitespace** — when in doubt, add more space
- **Subtle interactions** — small transitions (150–200ms) on hover/focus. No flashy animations
- **Dark mode** — consider `@media (prefers-color-scheme: dark)` if appropriate for the tool
- **Accessibility basics** — semantic HTML, visible focus states, sufficient color contrast

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


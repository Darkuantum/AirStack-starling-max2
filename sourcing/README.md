# Printable parts-sourcing sheet

`parts-sourcing.pdf` — 6 pages, A4, for carrying to Sim Lim Tower / Sim Lim Square.
One page per item with a diagram, the exact spec, a "do not buy" list, and a blank
table for writing quotes in so shops can be compared before buying.

Key English terms are paired with Chinese, since most Sim Lim Tower component shops
are Mandarin-speaking.

| Page | Contents |
|---|---|
| 1 | Checklist with tick boxes + the two buildings |
| 2 | LED strip — WS2812B/SK6812, 5 V, 30 LED/m, chipsets to avoid |
| 3 | Fan — 25×25×7 mm, 5 V, **2 wires only**, with a wire-count diagram |
| 4 | JST SH 1.0 mm connector, resistors, wire, optional BEC |
| 5 | Propellers — 7 × 3.7 × 3, with the pitch warning |
| 6 | Shop addresses and fallbacks |

## Regenerating

Edit `parts-sourcing.html`, then:

```sh
google-chrome --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=parts-sourcing.pdf "file://$PWD/parts-sourcing.html"
```

All diagrams are inline SVG — no external assets, no network needed.

## Specs come from

`reports/Starling Max 2 modification stack.md` § *What to order*. If a spec changes
there, change it here too. Shop details were web-sourced 2026-10-14 and some
directory listings were already ~2 years old — **call before travelling**.

# Printable parts-sourcing sheet

`parts-sourcing.pdf` — 6 pages, A4, for carrying to Sim Lim Tower / Sim Lim Square.
One page per item: a photo of the real part, the exact spec, a "do not buy" list, and a
blank table for writing quotes in so shops can be compared before buying.

Key English terms are paired with Chinese, since most Sim Lim Tower component shops are
Mandarin-speaking.

| Page | Contents |
|---|---|
| 1 | Checklist with tick boxes + the two buildings |
| 2 | LED strip — WS2812B/SK6812, 5 V, 30 LED/m, chipsets to avoid |
| 3 | Fan — "2507", 5 V, **2 wires only**, with a wire-count diagram |
| 4 | JST SH 1.0 mm connector, resistors, wire, optional BEC |
| 5 | Propellers — 7 × 3.7 × 3, with the pitch warning |
| 6 | Shop addresses and fallbacks |

## Images and attribution

| File | Source | Licence |
|---|---|---|
| `img/led-strip.jpg`, `img/led-strip-detail.jpg` | Cytron Technologies, product DS-6812-WS-601M | vendor product photo |
| `img/prop.webp` | OddityRC / Gemfan 7037-3 listing | vendor product photo |
| `img/jst-sh.jpg` | Christopher.nunez via Wikimedia Commons | CC BY-SA 3.0 |
| `img/fan-sunon.jpg` | Rico Shen via Wikimedia Commons | CC BY-SA 4.0 |

The **fan page keeps a drawn diagram as its primary illustration** rather than a photo.
No openly-licensed photo of a 25×25×7 mm ("2507") 5 V 2-wire fan was findable, and the two
things that actually matter — the dimensions and the wire count — are conveyed better by the
dimensioned drawing and the 2/3/4-wire comparison than by a photo of a different fan. The
Sunon range photo is included as supporting context only.

⚠️ Two of these are **third-party vendor photos in a public repository**. If that is a problem,
delete `sourcing/img/` and `parts-sourcing.pdf`, keep the HTML, and re-fetch locally when
printing.

## Regenerating

Edit `parts-sourcing.html`, then:

```sh
google-chrome --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=parts-sourcing.pdf "file://$PWD/parts-sourcing.html"
```

Diagrams are inline SVG; photos live in `img/`. Nothing is fetched at render time.

## Specs come from

`reports/Starling Max 2 modification stack.md` § *What to order*. If a spec changes there,
change it here too. Shop details were web-sourced 2026-10-14 and some directory listings were
already ~2 years old — **call before travelling**.

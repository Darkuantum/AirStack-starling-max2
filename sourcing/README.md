# Printable parts-sourcing sheet

`parts-sourcing.pdf` — 6 pages, A4, for carrying to Sim Lim Tower / Sim Lim Square.
One page per item: a large photo of the real part, the exact spec, a "do not buy" list, and a
blank table for writing quotes in so shops can be compared before buying.

Photos print large on purpose — they are the reason the sheet exists. Source images were
auto-cropped of their white borders (40–45% of each file), so the part fills the frame.

| Page | Contents |
|---|---|
| 1 | Checklist with tick boxes + the two buildings |
| 2 | LED strip — WS2812B/SK6812, 5 V, 60 LED/m (4 px per ~75 mm arm), chipsets to avoid |
| 3 | Fan — "2507", 5 V, **2 wires only**, with a wire-count diagram |
| 4 | JST SH 1.0 mm connector, resistors, wire, optional BEC |
| 5 | Propellers — 7 × 3.7 × 3, with the pitch warning |
| 6 | Shop addresses and fallbacks |

## Images and attribution

| File | Source | Licence |
|---|---|---|
| `img/led-strip.jpg`, `img/led-strip-detail.jpg` | Cytron Technologies, product DS-6812-WS-601M | vendor product photo |
| `img/prop.webp` | OddityRC / Gemfan 7037-3 listing | vendor product photo |
| `img/prop2.webp` | OddityRC / Gemfan 7037-3 listing | vendor product photo |
| `img/jst-sh.jpg` | Christopher.nunez via Wikimedia Commons | CC BY-SA 3.0 |

**The fan page has no photo, deliberately.** No openly-licensed photo of a 25×25×7 mm
("2507") 5 V 2-wire fan was findable, and two candidates were rejected for being actively
misleading: a Commons "small fan" image that turned out to be a bracket of THREE-wire server
fans, and a Sunon trade-show display of 8×8 to 30×30 mm micro-blowers — the wrong form factor
entirely. The page uses a dimensioned drawing plus a 2/3/4-wire comparison, which convey the
only two things that matter (size and wire count) better than a photo of a different fan, and
leads with the size code **"2507"**, which is what shops actually recognise.

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

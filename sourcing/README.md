# Printable parts-sourcing sheet

`parts-sourcing.pdf`: 9 pages, A4, to carry to Sim Lim Tower (components) and Sim Lim Square (propellers).
Quantities cover **both** drones.

| Page | Contents |
|---|---|
| 1 | Shopping list with tick boxes and thumbnails, grouped by building; what to bring; why the buck module and chip |
| 2 | 1 · LED strip |
| 3 | 2 · Cooling fan (3010 square fan + backup blower) |
| 4 | 3 · 5 V buck module · 4 · 74HCT125 level shifter |
| 5 | 5 · resistors · 6 · capacitors (470 µF + 100 nF) |
| 6 | 7 · silicone wire · 8 · Kapton tape + heat-shrink |
| 7 | 9 · Propellers (Sim Lim Square) |
| 8 | Price log: two rows per item, to compare shops |
| 9 | Where to go: Tower and Square shops, prop and fan fallbacks |

Every item card has the same layout:
- a photo;
- **Ask for**: a sentence to read out at the counter;
- a spec table where each row says what it must be and why;
- **Do not buy** and **Check** lines (the checks use the printed reference pieces: prop gauge, 30 × 30 × 10 fan block).

Where a photo differs from the spec (wrong pin count, thickness), a bold note under it says what to buy instead.

## Editing and rebuilding

All item data (specs, quantities, photos, shops) lives in `build_sheet.py`, so pages can't drift apart. Edit it, then:

```sh
python3 build_sheet.py
google-chrome --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=parts-sourcing.pdf "file://$PWD/parts-sourcing.html"
```

Check the page count afterwards (`pdfinfo parts-sourcing.pdf`): cards never split across pages, so an overfull page pushes a card onto an extra page.

Specs come from `docs/MODIFICATIONS.md` (§① cooling, §② LED strip incl. scenario B, §③ propellers). If a spec changes there, change it here too. Shop details were web-sourced 2026-10-14/22, partly from a ~2-year-old directory: **call before travelling**.

## Photo credits

Credits are printed under each photo; the source list is `img/CREDITS.tsv`.

| File | Credit |
|---|---|
| `img/led-strip-bare.jpg` | John McMaster, Wikimedia Commons, CC BY 4.0 |
| `img/fan-3010-axial.jpg` | Adafruit (product 3368) |
| `img/fan-3010-blower.jpg` | The Pi Hut |
| `img/resistor.jpg` | oomlout, Wikimedia Commons, CC BY-SA 2.0 |
| `img/capacitor-470uf.jpg` | Elcap, Wikimedia Commons, CC0 |
| `img/wire-silicone.jpg` | Adafruit (product 1970) |
| `img/kapton-tape.jpg` | Jérôme, Wikimedia Commons, CC BY-SA 3.0 |
| `img/ic-dip14.jpg` | Stefan Riepl, Wikimedia Commons, public domain |
| `img/buck-mini360.jpg` | Kunkune |
| `img/buck-mp1584.jpg` | Kunkune |
| `img/prop.webp` | OddityRC, Gemfan 7037-3 listing |
| `img/prop2.webp` | OddityRC, Gemfan 7037-3 listing |

Wikimedia Commons photos are used under their stated licences. The others are manufacturer or retailer product photos, used here for internal reference with attribution. If that is a problem in a public repository, delete them from `img/` and the sheet prints "(photo pending)" in their place.

## 3D-printed size reference

`print/prop-gauge-7037.stl`: a flat size gauge for the 7 × 3.7 × 3 prop (preview: `print/prop-gauge-7037.svg`).

| Feature | Size | Use |
|---|---|---|
| Ring | outer edge Ø 178 mm | Lay a shop prop on it: its tips should reach the outer edge |
| Blades | 3, approximate planform, 2 mm thick | Blade count and rough shape |
| Hub | Ø 14 × 7 mm, bore 5.2 mm | Hub thickness; M5 + 0.2 mm clearance. Push onto a motor shaft (prop nut off) to confirm M5 |

Not a flyable prop, and it can't show pitch: read pitch off the prop's label ("7037" = 7 in, 3.7 pitch). Print flat side down, no supports, ~11 cm³, bed ≥ 180 × 180 mm. Regenerate with `print/gen_prop_gauge.py OUT_DIR` (needs `trimesh`, `shapely`, `mapbox-earcut`, `manifold3d`).

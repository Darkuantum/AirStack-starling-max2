#!/usr/bin/env python3
"""Build the printable parts-sourcing sheet (parts-sourcing.html → PDF).

All item data lives in ITEMS below; every page is rendered from the same card
template, so specs, photos and layout stay consistent. Photos are in img/ with
their credits in PHOTO_CREDITS (also listed in README.md).

Usage:  build_sheet.py            (writes parts-sourcing.html)
        then: google-chrome --headless=new --no-pdf-header-footer \
              --print-to-pdf=parts-sourcing.pdf file://$PWD/parts-sourcing.html
"""
import html, os

HERE = os.path.dirname(os.path.abspath(__file__))
TOWER, SQUARE = "Sim Lim Tower", "Sim Lim Square"
E = html.escape

# ----------------------------------------------------------------------------- photo credits
PHOTO_CREDITS = {}          # filled by load_credits(); file -> (credit, note)


def load_credits():
    path = os.path.join(HERE, "img", "CREDITS.tsv")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.strip() and not line.startswith("#"):
                f, credit, *note = line.rstrip("\n").split("\t")
                PHOTO_CREDITS[f] = (credit, note[0] if note else "")


# ----------------------------------------------------------------------------- items
# spec rows: (what, must be, why)
ITEMS = [
 dict(key="led", short="WS2812B-2020-V6, 60 LED/m, bare, 3 wires", n=1, phase=1, name="Addressable LED strip", where=TOWER, qty="1 metre",
      qty_note="covers both drones (2 × 16 LEDs) with spares",
      photos=["led-strip-bare"],
      ask="“Do you have WS2812B V6 addressable LED strip, the version that runs on 3.3 volts? The narrow kind with 2020 size LEDs, 60 per metre, no silicone sleeve.”",
      specs=[
        ("Chip", "<b>WS2812B V6</b>: 5050 (WS2812B-B-V6), 3535 (Mini-V6) or 2020", "Their datasheets support a <b>3.3 V supply</b>: in spec on the drone's 3.3 V pad. Test: all LEDs off draws only µA"),
        ("Wires", "<b>3</b>: +5 V, data, ground", "4-wire strips need a clock line the drone doesn't have"),
        ("Voltage", "Sold as a “5 V” strip; the chip must be <b>V6</b>", "WS2812C and older WS2812B (3.7 V min) and SK6812 (3.5 V) run below spec at 3.3 V; 12 V strips won't light at all"),
        ("LED spacing", "<b>60 LEDs per metre</b> (16.7 mm apart)", "4 LEDs fit on each ~75 mm arm"),
        ("Width", "<b>10 mm or less</b>; 2020 strips are ~4–5 mm", "The arms are about 10 mm wide"),
        ("Finish", "<b>Bare</b> (IP30), no silicone sleeve or tube", "A sleeve makes it ~14.5 mm wide and heavier"),
        ("Colours", "<b>RGB</b>", "The RGBW strips use SK6812, not rated for 3.3 V"),
      ],
      dont=["WS2812C, SK6805 or SK6812 strips (not rated for 3.3 V)", "APA102, DotStar, SK9822 or WS2801 (4 wires)", "WS2815 (12 V)", "Non-addressable RGB strip (whole strip one colour)",
            "Silicone-sleeved or tube “waterproof” strip", "30 LEDs per metre (only 2 fit per arm)"],
      check="Hold the strip against a ruler: 10 LEDs should span ~167 mm, and the width must be ≤ 10 mm.",
      alt="Not in any Tower shop's online catalogue (checked 2026-10-25): call Sun-Light and 123 LED Lighting first. Online fallback (check the receipt suits the Concur claim): the listing must name the V6 chip. Any WS2812B or WS2812C still works on 3.3 V, below spec.",
      layout="full"),
 dict(key="fan", short="30×30×10 mm, 5 V, 2 wires, ≤ 0.15 A", n=2, phase=1, name="Cooling fan", where=TOWER, qty="2 (one per drone)",
      photos=["fan-3010-axial"],
      ask="“A 30 by 30 by 10 millimetre DC fan, 5 volt, two wires only.”",
      specs=[
        ("Size", "<b>30 × 30 × 10 mm</b> (“3010”)", "Fits the 36 mm-wide board stack; pushes through the 2 mm gaps in a shroud"),
        ("Voltage", "<b>5 V DC</b>", "It runs from the VOXL 2's fan port (J2), which gives 5 V"),
        ("Wires", "<b>Exactly 2</b>: red (+) and black (−)", "J2 switches the ground for speed control; 3- and 4-wire fans stutter"),
        ("Current", "<b>0.15 A (150 mA) or less</b>", "J2 is limited to ~0.4 A including start-up"),
        ("Bearing", "<b>Ball</b> or fluid / hydraulic (“FDB”)", "It will vibrate; plain sleeve bearings wear out"),
        ("Plug", "Any", "Cut off: soldered to a JST SH plug (item 3) for J2"),
        ("Noise", "A <b>100 nF</b> ceramic across the fan leads (item 5)", "No large capacitor: J2 switches the fan's ground"),
        ("Reference part", "Sunon MF30100V1-1000U-A99 (5.5 CFM, 0.12 A)", "Any brand matching the rows above"),
      ],
      dont=["12 V or 24 V fans (those are phase 2, item 14)", "3- or 4-wire fans", "Sleeve-bearing fans"],
      alt="Sun-Light #03-09 online (2026-10-29): its 30×30×10 fan is 12 V, not this one. Ask around the Tower; if no shop has a 5 V one, DigiKey MF30100V1-1000U-A99-ND.",
      check="Compare against your printed 30 × 30 × 10 mm reference block.",
      layout="full"),
 dict(key="jst", short="JST SH 1.0 mm, 2-pin, pre-crimped wires", n=3, phase=1, name="JST SH plug with wires (for J2)", where=TOWER, qty="4",
      qty_note="2 drones + spares; easy to damage",
      photos=["jst-sh-pigtail"],
      ask="“JST SH, 1.0 millimetre pitch, 2-pin female plug, with the wires already crimped in.”",
      specs=[
        ("Family", "<b>JST SH</b>, <b>1.0 mm</b> pitch, <b>2-pin</b> (housing SHR-02V-S)", "Mates with the VOXL 2's fan port J2"),
        ("Wires", "Pre-crimped, ~10–15 cm", "Hand-crimping 1.0 mm contacts needs a special tool"),
        ("If none", "Any pre-made JST SH 1.0 cable to cut or de-pin (FPV shops at Sim Lim Square)", ""),
      ],
      dont=["SM02B-SRSS-TB (the board-side header)", "JST PH / XH / ZH / GH sizes"],
      alt="Sun-Light #03-09 online (2026-10-29): none. If no shop has one, DigiKey 455-3013-ND.",
      layout="compact"),
 dict(key="res", short="330 Ω (or 470 Ω), 1/4 W", n=4, phase=1, name="Resistors", where=TOWER, qty="10",
      qty_note="they cost cents",
      photos=["resistor"],
      ask="“330 ohm resistors, quarter watt.” (470 ohm is also fine.)",
      specs=[
        ("Value", "<b>330 Ω</b> (bands orange-orange-brown) or <b>470 Ω</b> (yellow-violet-brown)", "Protects the LED data line; anything 300–500 Ω works"),
        ("Rating", "1/4 W, carbon or metal film, through-hole", "Ordinary, smallest common size"),
      ],
      dont=["SMD chip resistors (too small to hand-solder onto wires)"],
      alt="Sun-Light #03-09 online (2026-10-29): 330 Ω 0.5 W, S$0.03 each.",
      layout="compact"),
 dict(key="cap", short="470 µF 10–16 V electrolytic + 100 nF ceramic", n=5, phase=1, name="Capacitors", where=TOWER, qty="4 × 470 µF + 6 × 100 nF",
      photos=["capacitor-470uf"],
      ask="“470 microfarad electrolytic capacitors, 10 or 16 volt, small size. And 100 nanofarad ceramic capacitors, code 104.”",
      specs=[
        ("470 µF", "10–16 V radial electrolytic, ≤ 8 mm wide", "Across + / GND at the start of each LED strip; stripe = negative leg"),
        ("100 nF", "Ceramic, marked “104”", "Across the fan leads (motor noise); spares for phase 2"),
      ],
      dont=["Large 25 V+ cans (heavy)"],
      alt="Sun-Light #03-09 online (2026-10-29): leaded 0.1 µF 25 V, S$0.20; no 470 µF (DigiKey P14394-ND if no shop has one).",
      layout="compact"),
 dict(key="wire", short="26 AWG silicone, stranded, 3 colours", n=6, phase=1, name="Silicone hook-up wire", where=TOWER, qty="~2 m each, 3 colours",
      qty_note="red, black and one other colour",
      photos=["wire-silicone"],
      ask="“26 AWG silicone wire, stranded, in red, black and one other colour.”",
      specs=[
        ("Gauge", "<b>26 AWG</b>", "Enough for the LED current; thin enough for the ESC's small solder pads"),
        ("Insulation", "<b>Silicone</b>", "Doesn't melt back while soldering; flexes with vibration"),
        ("Core", "<b>Stranded</b> (many fine strands)", "Solid core cracks with vibration"),
      ],
      dont=["PVC hook-up wire", "Solid-core wire"],
      alt="Sun-Light #03-09 online (2026-10-29): 30 AWG silicone only, S$20.00 (acceptable).",
      layout="compact"),
 dict(key="tape", short="Kapton ~10 mm; heat-shrink 1.5–6 mm", n=7, phase=1, name="Kapton tape + heat-shrink", where=TOWER, qty="1 roll + assortment",
      photos=["kapton-tape"],
      ask="“Kapton tape, the amber polyimide kind, about 10 millimetres wide. A small heat-shrink assortment, 1.5 to 6 millimetres.”",
      specs=[
        ("Kapton width", "<b>~10 mm</b> (6–12 mm OK), polyimide, amber", "Wraps the strip ends onto the 10 mm arms; heat-proof, holds under vibration"),
        ("Heat-shrink", "<b>1.5–6 mm</b> assortment", "Every solder joint; carbon fibre conducts"),
        ("Phase 2", "20 cm of <b>15–20 mm clear</b> heat-shrink", "Only with the buck module: insulates it and the chip"),
      ],
      dont=["Electrical PVC tape (adhesive creeps)", "Heat-shrink in large sizes only (> 10 mm)"],
      alt="Sun-Light #03-09 online (2026-10-29): Kapton 12 mm × 30 m S$7.00; 580-piece heat-shrink kit S$16.90.",
      layout="compact"),
 dict(key="conn", short="JST-SM 3-pin LED connector pairs", n=8, phase=1, name="LED strip connector", where=TOWER, qty="3 pairs",
      photos=["conn-jst-sm"],
      ask="“3-pin JST SM LED strip connector pairs, plug and socket with wires.”",
      specs=[
        ("Type", "<b>JST-SM 3-pin</b>, latching (the plug LED strips come with)", "The whole LED ring unplugs from the ESC lead"),
      ],
      dont=["Dupont jumpers (shake loose)"],
      alt="Sun-Light #03-09 online (2026-10-29): 2-pin pairs only (S$2.50); ask around for 3-pin.",
      layout="compact"),
 dict(key="prop", short="Gemfan 7037-3: 7 in, 3.7 pitch, 3 blades, 5 mm hole", n=9, phase=1, name="Propellers", where=SQUARE, qty="at least 2 sets of 4",
      qty_note="each set is 2 clockwise + 2 counter-clockwise; props are consumables",
      photos=["prop.webp", "prop2.webp"],
      ask="“Gemfan 7037, three-blade, 7 inch, 5 millimetre centre hole.”",
      specs=[
        ("Diameter", "<b>7 inch</b> (178 mm)", "Same as the drone's stock props"),
        ("Pitch", "<b>3.7</b> (3.5 acceptable) — <b>never higher</b>", "Higher pitch overheats the small motors and the ESC"),
        ("Blades", "<b>3</b>", "Matches stock"),
        ("Centre hole", "<b>5 mm</b> (M5)", "Fits the motor shaft"),
        ("Hub", "~7 mm thick", "Fits the prop nut"),
        ("Rotation", "Set must include both <b>CW and CCW</b>", "Two motors spin each way"),
        ("Label", "“7037-3” or “7×3.7×3”", "First number = diameter, second = pitch"),
      ],
      dont=["7040, 7042, 7045 or any “freestyle” prop (pitch too high)", "Two-blade props (e.g. 7035-2)", "6 or 8 inch props", "Props without a 5 mm centre hole"],
      check="Lay it on your printed prop gauge: tips reach the outer ring; the hole fits the gauge's 5 mm hub.",
      alt="Genuine ModalAI part: MRP-D0012-1-00 (US$29.99 / 4), online only.",
      layout="full"), dict(key="buck", short="MP1584 (or Mini-360), 5 V out, ≥ 1 A", n=10, phase=2, name="5 V step-down (buck) module", where=TOWER, qty="2 (+1 spare)",
      qty_note="one per drone: powers the LED strip and the fan",
      photos=["buck-mp1584", "buck-mini360"],
      ask="“An MP1584 step-down buck converter module. A Mini-360 is also fine.”",
      specs=[
        ("Output", "<b>5.0 V</b>, <b>1 A or more</b> (MP1584 ~3 A)", "Powers the LED strip and fan, separately from the flight computer"),
        ("Input", "Accepts <b>≥ 17 V</b> (MP1584 28 V, Mini-360 23 V max)", "Runs from the 4S battery, up to 16.8 V"),
        ("Size", "MP1584 ~22 × 17 mm; Mini-360 ~17 × 11 mm", "Light; mounts at an arm root"),
        ("Adjustable?", "Trim screw: <b>set 5.0 V with a multimeter</b> before use", "Often shipped at another voltage"),
      ],
      dont=["Linear 7805 regulators (would burn ~6 W as heat)", "Big LM2596 boards (heavy)"],
      layout="compact"),
 dict(key="hct", short="74HCT125, DIP-14", n=11, phase=2, name="Level-shifter chip", where=TOWER, qty="2 (+1 spare)",
      photos=["ic-dip14"],
      ask="“74HCT125, the quad buffer chip, in DIP-14.” (The letter T matters.)",
      specs=[
        ("Part", "<b>74HCT125</b> (or 74AHCT125)", "Raises the drone's 3.3 V LED data signal to 5 V for the strip"),
        ("Package", "DIP-14 (through-hole)", "Easy to hand-solder onto a scrap of perfboard"),
        ("With it", "a <b>100 nF</b> ceramic capacitor (item 6) and a small perfboard scrap", "Standard decoupling for logic chips; keeps the assembly tidy"),
      ],
      dont=["74HC125 or 74LS125 (wrong input levels)"],
      check="If there's no 74HCT125 anywhere: RS Singapore / element14 Singapore stock it online.",
      layout="compact"),
 dict(key="bus", short="XT30 pairs + XT30 1-to-2 splitter; 20 AWG silicone", n=12, phase=2, name="Peripheral power bus", where=SQUARE,
      qty="XT30 parts · wire · JST-PH",
      qty_note="4 XT30 male + female pairs; 2 × 1-to-2 parallel splitters; 20 AWG silicone, 0.5 m each of red and black; 6 JST-PH 2-pin pairs",
      check="The splitter's single side plugs into the bus pigtail from the ESC; its two sides feed the LED/fan buck and (later) the companion. Both outputs must carry the same + and −.",
      photos=["xt30-splitter", "xt30-pigtail"],
      ask="“XT30 connectors, male and female pairs, and XT30 one-to-two splitter leads. Also 20 AWG silicone wire, red and black.”",
      specs=[
        ("XT30", "The small <b>yellow</b> FPV battery plug (half the size of an XT60); male + female", "Rated ~15 A; the standard small drone power plug"),
        ("Splitter", "<b>1 × XT30 in → 2 × XT30 out</b>, parallel", "Branch 1: LED/fan buck. Branch 2: future companion"),
        ("Wire", "<b>20 AWG silicone</b>, red + black", "Battery-side bus, sized for a future companion (~1.5 A)"),
        ("Plugs", "<b>JST-PH 2.0 mm 2-pin</b> pre-crimped pairs × 6", "Fan ↔ supply; ESC LED pads ↔ level shifter"),
      ],
      dont=["XT60 (too big)", "Series splitters (must be parallel)"],
      layout="full"),
 dict(key="ptc", short="PTC fuses 0.5 A, 0.65 A, 0.2 A hold, ≥ 30 V", n=13, phase=2, name="Resettable fuses (PTC)", where=TOWER,
      qty="2 each: 0.5 A, 0.65 A, 0.2 A",
      photos=["ptc-fuse"],
      ask="“Resettable PTC fuses, radial: 0.5 amp, 0.65 amp and 0.2 amp hold current, 30 volt or more.”",
      specs=[
        ("LEDs only", "<b>0.5 A hold</b> (trips ~1 A), e.g. MF-R050 / RXEF050", "LED strip at the brightness cap 80/255 (~0.32 A)"),
        ("LEDs + fan", "<b>0.65 A hold</b> (trips ~1.3 A), e.g. MF-R065 / RXEF065", "Both on one fuse (~0.44 A)"),
        ("Fan only", "<b>0.2 A hold</b> (trips ~0.4 A), e.g. MF-R020 / RXEF020", "5 V fan (0.12 A), or a 12/24 V fan on the battery"),
        ("Voltage", "<b>30 V or more</b> (MF-R: 60 V)", "A fan on the raw battery sees up to 16.8 V"),
      ],
      dont=["One-shot glass or blade fuses (not resettable)"],
      note="For tapping a shared 5 V rail, or a fan straight off the battery.",
      layout="compact"),
 dict(key="fanalt", short="12 V or 24 V 3010 fan for the battery; 3010 blower", n=14, phase=2, name="Fan alternatives", where=TOWER, qty="1 each, only if needed",
      photos=["fan-3010-blower"],
      ask="“A 30 by 30 by 10 fan, 12 volt, two wires, whose label says it runs up to about 17 volts. Or a 24 volt one. And a 30 millimetre blower fan.”",
      specs=[
        ("12 V fan", "3010, 2 wires; <b>label range must reach ~17 V</b>", "Runs straight off the 4S battery (12–16.8 V) via the power bus; full charge is 40 % over a plain 12 V rating"),
        ("24 V fan", "3010, 2 wires; starts at ≤ 12 V", "In spec across the whole 4S range, just slower"),
        ("Blower", "30 × 30 × 10 mm “snail shell”, 2 wires", "Pushes harder into a single narrow gap"),
        ("Fuse", "0.2 A PTC, 30 V+ (item 13)", "Any fan on the raw battery must be fused"),
      ],
      dont=["Plain 12 V fans rated to 13.8 V only (overvolted on a full pack)"],
      layout="compact"),
]

# ----------------------------------------------------------------------------- rendering
CSS = """
@page { size: A4; margin: 11mm 12mm 11mm 12mm; }
* { box-sizing: border-box; }
body { font-family: "DejaVu Sans", Helvetica, Arial, sans-serif; color: #15202b; margin: 0; font-size: 9.6pt; line-height: 1.38; }
.page { page-break-after: always; position: relative; }
.page:last-child { page-break-after: auto; }
.top { display: flex; justify-content: space-between; align-items: center; border-bottom: 2.5px solid #15202b; padding-bottom: 2mm; margin-bottom: 4mm; }
.top h1 { font-size: 19pt; margin: 0; letter-spacing: -0.3px; }
.top .meta { font-size: 8.5pt; color: #5b6673; text-align: right; }
.tag { display: inline-block; font-size: 8pt; font-weight: bold; padding: 0.6mm 2.2mm; border-radius: 2mm; color: #fff; }
.tag.tower { background: #1f4e79; } .tag.square { background: #2e7d32; } .tag.kit { background: #8a6d00; }
.card { border: 1.4px solid #c9d1db; border-radius: 3mm; padding: 2.6mm 3.4mm; margin-bottom: 2.6mm; break-inside: avoid; }
.card h2 { font-size: 13.5pt; margin: 0 0 1.6mm; display: flex; align-items: center; gap: 2.5mm; }
.num { display: inline-flex; width: 7.5mm; height: 7.5mm; border-radius: 50%; background: #15202b; color: #fff; font-size: 10.5pt; align-items: center; justify-content: center; flex: none; }
.qty { margin-left: auto; font-size: 9.5pt; font-weight: bold; background: #eef2f6; border-radius: 2mm; padding: 0.8mm 2.4mm; white-space: nowrap; }
.qtynote { font-size: 8.3pt; color: #5b6673; margin: -0.6mm 0 1.6mm 10mm; }
.grid { display: grid; grid-template-columns: 62mm 1fr; gap: 4mm; }
.grid.compact { grid-template-columns: 38mm 1fr; }
.grid.nophoto { grid-template-columns: 1fr; }
.photos img { width: 100%; max-height: 56mm; object-fit: contain; border: 1px solid #d5dbe2; border-radius: 1.5mm; background: #fff; display: block; margin-bottom: 1.4mm; }
.grid.compact .photos img { max-height: 27mm; }
.pnote { font-size: 7.8pt; font-weight: bold; color: #5b6673; line-height: 1.25; margin: -0.4mm 0 0.4mm; }
.credit { font-size: 6.3pt; color: #8a939d; line-height: 1.2; margin-bottom: 1.2mm; }
.ask { background: #fff8e1; border-left: 3.5px solid #b8860b; padding: 1.5mm 2.4mm; font-size: 9.8pt; margin-bottom: 1.6mm; }
.ask b { color: #8a6d00; font-size: 8pt; text-transform: uppercase; letter-spacing: 0.4px; display: block; }
table { width: 100%; border-collapse: collapse; font-size: 8.8pt; }
th, td { border-bottom: 1px solid #e1e6ec; padding: 1.1mm 1.6mm; text-align: left; vertical-align: top; }
th { color: #5b6673; font-size: 7.8pt; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1.4px solid #c9d1db; }
td.w { font-weight: bold; white-space: nowrap; width: 22mm; }
td.why { color: #5b6673; font-size: 8.2pt; }
.dont { margin-top: 1.8mm; font-size: 8.6pt; color: #8b1a1a; }
.dont b { color: #c53030; }
.check { margin-top: 1.4mm; font-size: 8.6pt; background: #eef6ee; border-radius: 1.5mm; padding: 1.2mm 2.2mm; }
.alt { margin-top: 1.2mm; font-size: 8.4pt; color: #5b6673; }
.quote { margin-top: 2mm; }
.quote td { height: 5.6mm; border: 1px solid #c9d1db; }
.prices td { height: 7.4mm; }
.quote th { border: 1px solid #c9d1db; background: #f4f6f8; }
.list td, .list th { border-bottom: 1px solid #e1e6ec; }
.list td.tick { font-size: 13pt; width: 7mm; }
.list { table-layout: fixed; }
.list td { padding-top: 0.6mm; padding-bottom: 0.6mm; }
.list img { height: 8.5mm; width: 13mm; object-fit: contain; display: block; }
.section { font-size: 11pt; font-weight: bold; margin: 3mm 0 1mm; display: flex; gap: 2.5mm; align-items: center; }
.box { border: 1.4px solid #c9d1db; border-radius: 3mm; padding: 2.6mm 3.4mm; margin-top: 3mm; font-size: 9pt; }
.box h3 { margin: 0 0 1.2mm; font-size: 10.5pt; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.kitnote { border: 1.4px dashed #b8860b; border-radius: 3mm; padding: 2.4mm 3.4mm; margin-bottom: 3.5mm; font-size: 9pt; background: #fffdf5; }
"""


def img_src(name):
    """Resolve a photo key to a file in img/ (any extension)."""
    if os.path.exists(os.path.join(HERE, "img", name)):
        return name
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        if os.path.exists(os.path.join(HERE, "img", name + ext)):
            return name + ext
    return None


def photos_html(item):
    out = []
    for p in item["photos"]:
        f = img_src(p)
        if f:
            out.append(f"<img src='img/{E(f)}' alt='{E(item['name'])}'>")
            credit, note = PHOTO_CREDITS.get(f, ("", ""))
            if note:
                out.append(f"<div class='pnote'>{E(note)}</div>")
            if credit:
                out.append(f"<div class='credit'>{E(credit)}</div>")
    return "".join(out) or "<div class='credit'>(photo pending)</div>"


def tag(where, kit=False):
    cls = "tower" if where == TOWER else "square"
    t = f"<span class='tag {cls}'>{E(where)}</span>"
    return t + (" <span class='tag kit'>Phase 2 · only if needed</span>" if kit else "")


def card(item, quote=True):
    compact = item["layout"] == "compact"
    nophoto = not item["photos"]
    rows = "".join(f"<tr><td class='w'>{w}</td><td>{m}</td><td class='why'>{y}</td></tr>" for w, m, y in item["specs"])
    dont = (f"<div class='dont'><b>✗ Do not buy:</b> {' · '.join(E(d) for d in item['dont'])}</div>" if item.get("dont") else "")
    extra = ""
    if item.get("check"): extra += f"<div class='check'><b>✓ Check:</b> {E(item['check'])}</div>"
    if item.get("note"): extra += f"<div class='alt'><b>Note:</b> {E(item['note'])}</div>"
    if item.get("alt"): extra += f"<div class='alt'>{E(item['alt'])}</div>"
    qt = ("<table class='quote'><tr><th style='width:34%'>Shop / unit</th><th style='width:30%'>Item seen</th>"
          "<th style='width:14%'>Price S$</th><th>Bought?</th></tr>" + "<tr><td></td><td></td><td></td><td></td></tr>" * 2 + "</table>") if quote else ""
    qn = f"<div class='qtynote'>{E(item['qty_note'])}</div>" if item.get("qty_note") else ""
    return f"""
<div class='card'>
  <h2><span class='num'>{item['n']}</span>{E(item['name'])} {tag(item['where'], item.get('phase') == 2)}<span class='qty'>Buy: {E(item['qty'])}</span></h2>{qn}
  <div class='grid{" compact" if compact else ""}{" nophoto" if nophoto else ""}'>
    {"" if nophoto else f"<div class='photos'>{photos_html(item)}</div>"}
    <div>
      <div class='ask'><b>Ask for</b>{E(item['ask'])}</div>
      <table><tr><th>Spec</th><th>Must be</th><th>Why</th></tr>{rows}</table>
      {dont}{extra}{qt}
    </div>
  </div>
</div>"""


def header(title, meta):
    return f"<div class='top'><h1>{E(title)}</h1><div class='meta'>{meta}</div></div>"


def page_list():
    def rows(items):
        out = []
        for it in items:
            f = img_src(it["photos"][0]) if it["photos"] else None
            im = f"<img src='img/{E(f)}' alt=''>" if f else ""
            out.append(f"<tr><td class='tick'>☐</td><td>{im}</td><td><b>{it['n']}. {E(it['name'])}</b></td>"
                       f"<td>{E(it['qty'])}</td><td>{E(it['short'])}</td></tr>")
        return "".join(out)
    p1t = [i for i in ITEMS if i["phase"] == 1 and i["where"] == TOWER]
    p1s = [i for i in ITEMS if i["phase"] == 1 and i["where"] == SQUARE]
    p2 = [i for i in ITEMS if i["phase"] == 2]
    head = ("<colgroup><col style='width:7mm'><col style='width:15mm'><col style='width:52mm'><col style='width:38mm'><col></colgroup>"
            "<tr><th></th><th></th><th>Item</th><th>Qty</th><th>Key spec</th></tr>")
    return f"""
<div class='page'>
  {header("Shopping list", "Quantities cover <b>both</b> drones<br>Each item has its own card on the following pages")}
  <div class='section'>PHASE 1 · buy now &nbsp; {tag(TOWER)} 10 Jalan Besar · components</div>
  <table class='list'>{head}{rows(p1t)}</table>
  <div class='section'>PHASE 1 · buy now &nbsp; {tag(SQUARE)} 1 Rochor Canal Road · hobby / FPV</div>
  <table class='list'>{head}{rows(p1s)}</table>
  <div class='section' style='color:#8a6d00'>PHASE 2 · don't buy yet — only if phase 1 fails</div>
  <table class='list'>{head}{rows(p2)}</table>
  <div class='two'>
    <div class='box'><h3>Bring</h3>This sheet · the <b>printed prop gauge</b> and <b>30 × 30 × 10 fan block</b> · a ruler or calipers</div>
    <div class='box'><h3>Every purchase</h3>Ask each shop for a quote, and for an <b>itemised receipt</b> with the shop's name and GST number when you buy.</div>
  </div>
</div>"""


def page_items(items, title, intro=""):
    body = "".join(card(i, quote=False) for i in items)
    return f"<div class='page'>{header(title, 'Starling 2 Max parts')}{intro}{body}</div>"


def page_shops():
    return f"""
<div class='page'>
  {header("Where to go", "Call ahead: stock and unit numbers change")}
  <div class='section'>{tag(TOWER)} 10 Jalan Besar — electronic components</div>
  <table class='list'>
    <tr><th>Shop</th><th>Unit</th><th>Try here for</th></tr>
    <tr><td><b>J.C.W. Electronic</b></td><td>—</td><td>Fans — <b>call first</b>; LED strip</td></tr>
    <tr><td><b>Sun-Light Electronics</b></td><td>#03-09</td><td>LED strip — <b>call first</b>, 6299 8803. Online it lists only a 30 LED/m 5050 WS2812B (no V6): a bench stopgap</td></tr>
    <tr><td><b>123 LED Lighting</b></td><td>#03-41</td><td>LED shop — <b>call first</b>, 8793 9683. Online catalogue is 12 / 24 / 230 V lighting strip only; ask for WS2812B V6 (5050), 5 V</td></tr>
        <tr><td><b>Davjones Technology</b></td><td>#B1-47/11</td><td>Phase 2: buck modules, 74HCT125, PTC fuses</td></tr>
    <tr><td><b>Continental Electronic Enterprise</b></td><td>#B1-25</td><td>Resistors, capacitors, JST connectors, wire, tape, heat-shrink</td></tr>
  </table>
  <div class='alt'>From a shop directory about two years old. No online listing confirms the fans, blower or 74HCT125 in stock anywhere in Sim Lim — call first.</div>

  <div class='section'>{tag(SQUARE)} 1 Rochor Canal Road — hobby / FPV</div>
  <table class='list'>
    <tr><th>Shop</th><th>Unit</th><th>Try here for</th></tr>
    <tr><td><b>Hobby Square</b></td><td>#02-60</td><td><b>Propellers</b>; phase 2 XT30 bus parts; also silicone wire and JST SH cables if the Tower has none. Listed hours Mon–Sat 12:30–7:30 pm</td></tr>
  </table>

  <div class='section'>If Hobby Square has no 7037 props</div>
  <table class='list'>
    <tr><th>Shop</th><th>Where</th><th>Notes</th></tr>
    <tr><td><b>Sky Hobbies</b></td><td>Jalan Sultan</td><td>skyhobbies.com.sg · large HQProp stockist</td></tr>
    <tr><td><b>Helicopter Smartfly</b></td><td>Queensway Shopping Centre</td><td>smartfly.com.sg · Mon–Sat 12–7 pm, Sun 3–7 pm, closed Wednesday</td></tr>
    <tr><td><b>Rotor Hobby</b></td><td>Kitchener Complex, French Road</td><td>shop.rotor.com.sg · +65 6296 3686</td></tr>
    <tr><td><b>OddityRC</b></td><td>Paya Lebar Square (pickup)</td><td>oddityrc.com · stocks Gemfan 7037-3 online; allow 5–8 days</td></tr>
  </table>

  <div class='section'>Other fallbacks</div>
  <table class='list'>
    <tr><td><b>Fans</b></td><td>Amicus, 8 Ubi Road 2 #03-13 Zervex · +65 6980 6783 · 5 V fans by order; call first</td></tr>
    <tr><td><b>Online, Singapore</b></td><td>Cytron SG and Kuriosity.sg (LED strip, buck modules) · RS Singapore and element14 Singapore (74HCT125, Sunon fans; fast delivery) · DigiKey (a few days)</td></tr>
    <tr><td><b>Online, blower</b></td><td>3D-printer parts sellers and local Shopee sellers (“3010 blower 5V”)</td></tr>
  </table>
</div>"""


def build():
    load_credits()
    by = {i["key"]: i for i in ITEMS}
    p2_intro = ("<div class='kitnote'><b>Phase 2 — only if phase 1 fails.</b> If the LED strip misbehaves on the drone's 3.3 V pad, "
                "it moves to its own 5 V buck module with a 74HCT125 on the peripheral power bus. If the fan causes trouble on J2, "
                "a 12 V or 24 V fan can run straight off the battery through the bus with a 0.2 A fuse.</div>")
    pages = [
        page_list(),
        page_items([by["led"]], "1 · LED strip"),
        page_items([by["fan"]], "2 · Cooling fan"),
        page_items([by["jst"], by["res"], by["cap"]], "3–5 · J2 plug, resistors, capacitors"),
        page_items([by["wire"], by["tape"], by["conn"]], "6–8 · Wire, tape, LED connector"),
        page_items([by["prop"]], "9 · Propellers"),
        page_items([by["buck"], by["hct"]], "10–11 · Buck module, level shifter", p2_intro),
        page_items([by["bus"]], "12 · Peripheral power bus"),
        page_items([by["ptc"], by["fanalt"]], "13–14 · Fuses, fan alternatives"),
        page_shops(),
    ]
    doc = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Parts Sourcing</title>"
           f"<style>{CSS}</style></head><body>{''.join(pages)}</body></html>")
    open(os.path.join(HERE, "parts-sourcing.html"), "w", encoding="utf-8").write(doc)


if __name__ == "__main__":
    build()

#!/usr/bin/env python3
"""Board-level wiring SVG for the Starling 2 Max.

Every board is drawn as seen from ABOVE with the drone's FRONT TO THE RIGHT, so the
four panels line up with the airframe drawing. Faces that point down are drawn
"seen through the board" (x-ray), so a connector appears where it really is.

Source geometry (5 px = 1 mm), traced from ModalAI's VOXL 2 connector drawing and the
labelled M0129 photo:
  VOXL 2 top face    — ModalAI's top drawing as-is (J2 edge = front, J4/J9 edge = rear)
  VOXL 2 bottom face — ModalAI's bottom drawing mirrored left-right (x-ray view)
  ESC power face     — photo rotated so the J1 / VREG edge faces the rear
  ESC MCU face       — photo rotated the same way and mirrored (x-ray view)
Orientation per the owner (J4, J9, ESC J1, VREG and LED pads face the rear); the ESC's
power-face-up choice is the only one where each ESC corner sits next to its own motor.

Usage: gen_board_level_wiring.py OUT.svg
"""
import sys

W, H = 1360, 980
S = 5
out = []
add = out.append
FONT = "font-family='Helvetica, Arial, sans-serif'"
C = dict(pwr="#d62828", gnd="#222222", uart="#1d5fbf", i2c="#0f8a8a", usb="#7b3fb5",
         mod="#e07b00", b2b="#888888", board="#1f4e79", boardfill="#dbe7f3",
         conn="#f2f2f2", connstroke="#555", unused="#c4c4c4", text="#111", sub="#555", pad="#f6d36b")


def text(x, y, s, size=12, anchor="start", weight="normal", fill=None, italic=False):
    st = " font-style='italic'" if italic else ""
    add(f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' "
        f"font-weight='{weight}' fill='{fill or C['text']}' {FONT}{st}>{s}</text>")


def lines(x, y, rows, size=11.5, gap=14.5, **kw):
    for i, r in enumerate(rows):
        text(x, y + i * gap, r, size, **kw)


def rect(x, y, w, h, fill="none", stroke="#000", sw=1.2, rx=0, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<rect x='{x:.1f}' y='{y:.1f}' width='{w:.1f}' height='{h:.1f}' rx='{rx}' fill='{fill}' "
        f"stroke='{stroke}' stroke-width='{sw}'{d}/>")


def rect2(p, q, **kw):
    x0, x1 = sorted((p[0], q[0])); y0, y1 = sorted((p[1], q[1]))
    rect(x0, y0, x1 - x0, y1 - y0, **kw)
    return x0, y0, x1, y1


def wire(pts, color, sw=2.2, dash=None):
    """Polyline with a white halo underneath, so crossings read as over/under."""
    p = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<path d='{p}' fill='none' stroke='#fff' stroke-width='{sw + 4}' stroke-linejoin='round'/>")
    add(f"<path d='{p}' fill='none' stroke='{color}' stroke-width='{sw}' stroke-linejoin='round' "
        f"stroke-linecap='round'{d}/>")


def dot(x, y, r=3, fill="#000"):
    add(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r}' fill='{fill}'/>")


def pad(x, y, r=4.5, fill=None):
    add(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r}' fill='{fill or C['pad']}' stroke='#8a6d00'/>")


def hole(x, y):
    add(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5.5' fill='#fff' stroke='{C['board']}' stroke-width='1.2'/>")


def exit_arrow(x, y, d, col="#444"):
    """Small filled triangle showing which way the cable leaves a connector."""
    s = 6
    pts = {"R": [(x, y - s), (x, y + s), (x + s * 1.4, y)], "L": [(x, y - s), (x, y + s), (x - s * 1.4, y)],
           "U": [(x - s, y), (x + s, y), (x, y - s * 1.4)], "D": [(x - s, y), (x + s, y), (x, y + s * 1.4)]}[d]
    add("<polygon points='" + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f"' fill='{col}'/>")


def conn(p, q, label="", unused=False, size=11, exit=None):
    x0, y0, x1, y1 = rect2(p, q, fill=C["unused"] if unused else C["conn"], stroke=C["connstroke"])
    if label:
        text((x0 + x1) / 2, (y0 + y1) / 2 + 4, label, size, "middle", "bold", "#666" if unused else C["text"])
    if exit:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        exit_arrow(*{"R": (x1 + 2, my), "L": (x0 - 2, my), "U": (mx, y0 - 2), "D": (mx, y1 + 2)}[exit], exit)
    return x0, y0, x1, y1


def board(x, y, w, h, title, subtitle):
    rect(x, y, w, h, C["boardfill"], C["board"], 2, rx=4)
    text(x, y - 24, title, 14, weight="bold", fill=C["board"])
    text(x, y - 8, subtitle, 11, fill=C["sub"])


def box(x, y, w, h, title, rows, color="#333", dash=None, size=11.5, gap=14.5):
    rect(x, y, w, h, "#fff", color, 1.6, rx=6, dash=dash)
    text(x + 10, y + 19, title, 12.5, weight="bold", fill=color)
    lines(x + 10, y + 37, rows, size, gap)


add(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>")
rect(0, 0, W, H, "#ffffff", "none", 0)

# ---- header ----------------------------------------------------------------
text(20, 32, "Starling 2 Max — board-level wiring, every board seen from above, front → right", 19, weight="bold")
lines(20, 54, [
    "Outlines and connector positions traced from ModalAI's VOXL 2 connector drawing and M0129 photo (5 px = 1 mm, ±1 mm). "
    "Downward faces are drawn seen through the board.",
    "Connections per ModalAI's REV4 compute diagram, the 2026-10-14 bench session and the owner's hardware check (2026-10-20). "
    "▶ = side a cable leaves from.",
], 11.5, 15, fill=C["sub"])
text(W - 24, 36, "FRONT ▶", 20, "end", "bold", "#1f4e79")
for i, (col, lab, dash) in enumerate([
        (C["pwr"], "+ power", None), (C["gnd"], "ground", None), (C["uart"], "UART / serial", None),
        (C["i2c"], "I²C", None), (C["usb"], "USB", None), (C["b2b"], "board-to-board", "6 4"),
        (C["mod"], "planned mod", "7 4")]):
    x = 20 + i * 160
    wire([(x, 92), (x + 34, 92)], col, 3, dash)
    text(x + 42, 96, lab, 12)

# ---- VOXL 2 top face (faces up): ModalAI top drawing as-is ------------------
TX, TY = 310, 150
def T(x, y): return TX + x * S, TY + y * S
board(TX, TY, 70 * S, 36 * S, "VOXL 2 (M0054-1) — top face, facing up",
      "J2 · J3 · J5 · J10 · J19 · the add-on board stacks on this face")
for hx, hy in [(2.7, 2.2), (64.9, 2.2), (2.7, 33.3), (64.9, 33.3)]:
    hole(*T(hx, hy))
rect2(T(31.9, 5.9), T(59.2, 21.0), fill="#2a2f36", stroke="#111")
text(*T(45.5, 14.5), "shield over the SIP", 10.5, "middle", fill="#ddd")
conn(T(5.2, 1.9), T(24.4, 7.0), "J5 · 120-pin B2B")
conn(T(5.5, 27.6), T(28.4, 35.9), "J3 · 60-pin B2B")
conn(T(28.8, 30.0), T(48.1, 36.4), "J19", exit="D")
conn(T(49.2, 31.6), T(63.5, 36.4), "J10 · empty", unused=True, exit="D")
conn(T(64.5, 26.2), T(71.2, 31.4), "J2", size=10.5, exit="R")
dot(*T(30.0, 34.6), 2.6, "#e00"); dot(*T(66.0, 27.4), 2.6, "#e00")

# ---- VOXL 2 bottom face (faces down), x-ray: bottom drawing mirrored -------
BX, BY = 310, 560
def B(xb, yb): return BX + (70 - xb) * S, BY + yb * S
board(BX + 90, BY, 0, 0, "VOXL 2 — bottom face, facing down (seen through)",
      "QRB5165 SIP · J4 · J6–J9 · J18 · the M0173 camera board sits under this face")
rect(BX, BY, 70 * S, 36 * S, C["boardfill"], C["board"], 2, rx=4)
for hx, hy in [(4.9, 2.2), (67.4, 2.2), (4.9, 33.3), (67.4, 33.3)]:
    hole(*B(hx, hy))
x0, y0, x1, y1 = rect2(B(16.9, 7.0), B(32.4, 19.9), fill="#c9ccd1", stroke="#666", rx=2)
lines((x0 + x1) / 2, y0 + 20, ["QRB5165 SIP", "Linux CPUs +", "SLPI = PX4"], 11, 13, anchor="middle", weight="bold")
j6 = conn(B(9.0, 1.0), B(12.9, 14.6))
j7 = conn(B(9.0, 20.9), B(12.9, 34.8))
text(j6[0] - 6, (j6[1] + j6[3]) / 2 + 4, "J6", 12, "end", "bold")
text(j7[0] - 6, (j7[1] + j7[3]) / 2 + 4, "J7", 12, "end", "bold")
j8 = conn(B(51.0, 21.2), B(54.5, 34.8), unused=True)
text(j8[2] + 5, (j8[1] + j8[3]) / 2, "J8", 12, weight="bold", fill="#777")
text(j8[2] + 5, (j8[1] + j8[3]) / 2 + 13, "empty", 10, fill="#777", italic=True)
j18 = conn(B(55.5, 0.3), B(64.3, 4.7), "J18", size=10.5, exit="U")
j9 = conn(B(61.2, 8.5), B(71.2, 17.4), "J9", size=10.5, exit="L")
j4 = conn(B(64.3, 18.7), B(72.5, 31.0), "J4", size=10.5, exit="L")
dot(*B(63.3, 3.6), 2.6, "#e00"); dot(*B(65.5, 30.0), 2.6, "#e00")

# ---- ESC power face (faces up): photo rotated, J1/VREG edge to the rear ----
EX, EY = 870, 560
def E(x, y): return EX + y * S, EY + (36.5 - x) * S
board(EX, EY, 36.5 * S, 36.5 * S, "M0129 ESC — power face up", "J1, VREG and LED pads face the rear")
for hx, hy in [(2.2, 2.2), (34.3, 2.2), (2.2, 34.3), (34.3, 34.3)]:
    hole(*E(hx, hy))
j1 = conn(E(5.8, 3.8), E(15.0, 8.6), exit="L")
text(j1[0], j1[1] - 6, "J1 UART", 10.5, weight="bold")
vp = rect2(E(24.4, 3.4), E(27.9, 6.3), fill=C["pad"], stroke="#8a6d00")
vm = rect2(E(28.0, 3.4), E(31.5, 6.3), fill=C["pad"], stroke="#8a6d00")
text(vp[2] + 4, (vp[1] + vp[3]) / 2 + 4, "+", 11, weight="bold"); text(vm[2] + 4, (vm[1] + vm[3]) / 2 + 4, "−", 11, weight="bold")
text(vp[0], vp[3] + 13, "VREG OUT 5 V", 10, weight="bold")
bp = rect2(E(14.2, 31.7), E(17.5, 35.0), fill=C["pad"], stroke="#8a6d00")
bm = rect2(E(20.0, 31.7), E(23.4, 35.0), fill=C["pad"], stroke="#8a6d00")
text(bm[0] - 4, (bm[1] + bm[3]) / 2 + 4, "BATT −", 10, "end", weight="bold")
text(bp[0] - 4, (bp[1] + bp[3]) / 2 + 4, "BATT +", 10, "end", weight="bold")
for idn, (xs, yc, m, where) in {"ID0": (31.3, 15.0, "M2", "rear-left"), "ID1": (31.3, 26.4, "M3", "front-left"),
                                "ID3": (3.8, 15.0, "M4", "rear-right"), "ID2": (3.8, 26.4, "M1", "front-right")}.items():
    for dy in (-3.9, 0, 3.8):
        rect2(E(xs, yc + dy - 1.2), E(xs + 2.4, yc + dy + 1.2), fill=C["pad"], stroke="#8a6d00")
    cx, cy = E(xs + 1.2, yc)
    inside = 22 if xs > 20 else -14
    text(cx, cy + inside, f"{idn} ▸ {m}", 11, "middle", "bold")

# ---- ESC MCU face (faces down), x-ray -----------------------------------
FX, FY = 1135, 560
def F(xb, yb): return FX + yb * S, FY + (36.5 - xb) * S
board(FX, FY, 36.5 * S, 36.5 * S, "M0129 — MCU face down", "seen through · same orientation")
for hx, hy in [(2.2, 2.2), (34.3, 2.2), (2.2, 34.3), (34.3, 34.3)]:
    hole(*F(hx, hy))
gpad, opad, vpad = F(6.4, 4.3), F(10.9, 4.3), F(13.1, 4.3)
for p in (gpad, opad, vpad):
    pad(*p)
text(gpad[0] + 10, vpad[1] - 8, "NeoPixel pads", 10, weight="bold")
text(gpad[0] + 10, vpad[1] + 4, "VAUX", 9.5, fill=C["sub"])
text(gpad[0] + 10, opad[1] + 4, "⬇ OUT", 9.5, fill=C["sub"])
text(gpad[0] + 10, gpad[1] + 4, "GND", 9.5, fill=C["sub"])
for xmm in (23.6, 25.4, 27.2, 28.9, 30.9):
    pad(*F(xmm, 4.3), 3.4, C["unused"])
text(*F(32.5, 7.0), "AUX PWM · unused", 9.5, fill="#777")
lines(*F(26.0, 13.0), ["AUX reg: 3.3 V default,", "500–600 mA; 5 V select", "disabled in firmware"], 9.5, 12, fill=C["sub"])

# ---- power: ESC VREG -> VOXL J4 ------------------------------------------
j4y = (j4[1] + j4[3]) / 2
vpy, vmy = (vp[1] + vp[3]) / 2, (vm[1] + vm[3]) / 2
wire([(j4[0], j4y - 4), (284, j4y - 4), (284, 772), (842, 772), (842, vpy), (vp[0], vpy)], C["pwr"], 2.6)
wire([(j4[0], j4y + 4), (290, j4y + 4), (290, 766), (836, 766), (836, vmy), (vm[0], vmy)], C["gnd"], 2.6)
text(300, 762, "ESC VREG 5 V → J4-1 · GND → J4-2 · J4-3/4 not wired", 11, weight="bold", fill=C["pwr"])

# ---- UART: VOXL J18 <-> ESC J1 ---------------------------------------------
j18x = (j18[0] + j18[2]) / 2
j1y = (j1[1] + j1[3]) / 2
for off, col in [(-5, C["uart"]), (0, C["uart"]), (5, C["gnd"])]:
    wire([(j18x + off, j18[1]), (j18x + off, 510 + off), (856 + off, 510 + off), (856 + off, j1y + off), (j1[0], j1y + off)], col, 1.9)
text(560, 500, "UART 3.3 V · J18-2 TX → J1-2 RX · J18-3 RX ← J1-3 TX · pin 4 GND", 11, weight="bold", fill=C["uart"])

# ---- J9 -> laptop ----------------------------------------------------------
j9y = (j9[1] + j9[3]) / 2
wire([(j9[0], j9y), (262, j9y)], C["usb"], 2.4)
box(172, j9y - 22, 90, 44, "Laptop", ["ADB only"], C["usb"])

# ---- battery ---------------------------------------------------------------
bpy, bmy = (bp[1] + bp[3]) / 2, (bm[1] + bm[3]) / 2
wire([(bm[2], bmy), (1076, bmy), (1076, 850)], C["gnd"], 2.6)
wire([(bp[2], bpy), (1060, bpy), (1060, 836), (920, 836), (920, 850)], C["pwr"], 2.6)
box(990, 850, 100, 48, "2S pack", ["18650 · XT30"], C["pwr"])
box(870, 850, 100, 48, "2S pack", ["18650 · XT30"], C["pwr"])
wire([(970, 880), (990, 880)], C["pwr"], 2.6)
text(870, 918, "packs in series → 12–16.8 V (read 16.07–16.09 V)", 11, fill=C["sub"])

# ---- J19 -> GNSS + RC ------------------------------------------------------
j19c = T(38.4, 36.6)
split = (j19c[0], 360)
wire([j19c, split], "#555", 4)
dot(*split, 4, "#555")
wire([split, (420, 360), (420, 385)], C["i2c"], 2.4)
wire([split, (640, 360), (640, 385)], C["uart"], 2.4)
box(318, 385, 205, 100, "GNSS + mag (M10-5883)", [
    "J19-1 +5 V · J19-6 GND", "J19-2 TX → GNSS RX", "J19-3 RX ← GNSS TX", "J19-4/5 mag SCL/SDA (I²C)"], C["i2c"])
box(540, 385, 240, 100, "RC receiver", [
    "Starling 1: ELRS · Starling 2: Ghost", "J19-11 RX ← receiver TX", "J19-10 TX → receiver RX (ELRS only)",
    "J19-1 +5 V (shared) · J19-12 GND"], C["uart"])

# ---- J2 -> fan (planned) ---------------------------------------------------
j2 = T(71.2, 28.8)
wire([j2, (700, j2[1]), (700, 300)], C["mod"], 2.6, "7 4")
box(678, 300, 220, 84, "① Fan (planned · J2 empty)", [
    "25 × 25 × 7 mm · 5 V · 2 wires", "plug SHR-02V-S (JST SH 1.0)", "pin 1 +5 V always on",
    "pin 2 PWM-switched GND ≤ 400 mA"], C["mod"], "7 4")

# ---- J3/J5 -> add-on board -------------------------------------------------
rect(TX - 4, TY - 3, 70 * S + 8, 36 * S + 7, "none", C["b2b"], 1.8, rx=6, dash="6 4")
box(20, 150, 268, 205, "Stacked on J3 + J5 (both aircraft)", [
    "Starling 2: Sparrow WiFi board",
    "  M0213-class (REV4 says M0141)",
    "  → mlan0 · 2 × U.FL WiFi antennas",
    "Starling 1: M0090-class 5G carrier",
    "  own USB hub · J11 USB 3 free",
    "  ├ EM9291 5G modem (M.2, unused)",
    "  └ J12 USB 2 → TX20U dongle → wlan0",
    "No room left for an M0062",
    "Ethernet add-on on either drone"], C["b2b"], "6 4")
wire([(288, 250), (TX - 4, 250)], C["b2b"], 2, "6 4")

# ---- J6/J7 -> M0173 --------------------------------------------------------
box(670, 588, 161, 136, "M0173 camera board", [
    "under the VOXL 2, on J6 + J7", "C29, five sensors:", "2 × AR0144 tracking", "2 × IMX412 hi-res",
    "IRS2975 ToF · ⚪ VL53L1CX", "cabling as REV4 drawing"], C["b2b"], "6 4", 10.5, 13.5)
for jj, yy in ((j6, 610), (j7, 690)):
    wire([(jj[2], (jj[1] + jj[3]) / 2), (650, (jj[1] + jj[3]) / 2), (650, yy), (670, yy)], C["b2b"], 2, "6 4")

# ---- NeoPixel -> LED chain (planned) --------------------------------------
lx = 1105
wire([(vpad[0] - 5, vpad[1]), (lx + 14, vpad[1]), (lx + 14, 800), (1214, 800)], C["pwr"], 2, "7 4")
wire([(opad[0] - 5, opad[1]), (lx + 4, opad[1]), (lx + 4, 806)], C["mod"], 2.2, "7 4")
rect(lx - 2, 754, 12, 22, "#fff", C["mod"], 1.6)
wire([(lx + 4, 808), (lx + 4, 810), (1214, 810)], C["mod"], 2.2, "7 4")
wire([(gpad[0] - 5, gpad[1]), (lx - 6, gpad[1]), (lx - 6, 820), (1214, 820)], C["gnd"], 2, "7 4")
text(lx - 12, 770, "330–470 Ω", 10, "end", "bold", C["mod"])
sx = 1218
for arm in range(4):
    for p in range(4):
        rect(sx + arm * 33 + p * 7.5, 805, 6, 10, "#fff4e0", C["mod"], 1)
text(sx, 845, "② LED chain · 16 px", 11.5, weight="bold", fill=C["mod"])
lines(sx, 859, ["4 arms × 4 px, 60 LED/m", "returns via the hub", "470–1000 µF at strip", "5 V BEC only if VAUX = 3.3 V"], 10, 12.5)

# ---- stack note + footnote -------------------------------------------------
box(20, 800, 268, 118, "Stack, top to bottom", [
    "add-on board (J3 + J5)", "VOXL 2, top face up", "M0173 cameras (J6 + J7)",
    "ESC, power face up — LED pads", "underneath, reached below J18"], "#1f4e79", None, 11, 14)
text(20, 952, "Motors: PX4 Quad X (M1 front-right, M2 rear-left, M3 front-left, M4 rear-right). "
     "ESC ID → motor from VOXL_ESC_FUNC1–4 = 102,103,101,104 on both aircraft; with the power face up, "
     "each ESC corner sits next to its own motor. ESC ID0 also drives the NeoPixel pad.", 10.5, fill=C["sub"])
text(20, 968, "⚪ = drawn by ModalAI, not inspected on our aircraft.", 10.5, fill=C["sub"])

add("</svg>")
open(sys.argv[1], "w").write("\n".join(out))

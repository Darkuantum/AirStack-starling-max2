#!/usr/bin/env python3
"""Board-level wiring SVG for the Starling 2 Max. Connector positions are traced
from ModalAI's VOXL 2 connector drawing and the M0129 labelled photo (5 px/mm)."""
import sys

W, H = 1340, 960
S = 5  # px per mm
out = []
def add(s): out.append(s)

FONT = "font-family='Helvetica, Arial, sans-serif'"
C = dict(pwr="#d62828", gnd="#222222", uart="#1d5fbf", i2c="#0f8a8a", usb="#7b3fb5",
         mod="#e07b00", b2b="#888888", board="#1f4e79", boardfill="#dbe7f3",
         conn="#f2f2f2", connstroke="#555", unused="#bbbbbb", text="#111", sub="#555")

def rect(x, y, w, h, fill="none", stroke="#000", sw=1.2, rx=0, dash=None, op=1):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<rect x='{x:.1f}' y='{y:.1f}' width='{w:.1f}' height='{h:.1f}' rx='{rx}' fill='{fill}' "
        f"stroke='{stroke}' stroke-width='{sw}'{d} opacity='{op}'/>")

def text(x, y, s, size=12, anchor="start", weight="normal", fill=None, italic=False):
    st = " font-style='italic'" if italic else ""
    add(f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' "
        f"font-weight='{weight}' fill='{fill or C['text']}' {FONT}{st}>{s}</text>")

def lines(x, y, rows, size=11.5, gap=14.5, **kw):
    for i, r in enumerate(rows):
        text(x, y + i * gap, r, size, **kw)

def poly(pts, color, sw=2.2, dash=None, hop=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    p = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    add(f"<path d='{p}' fill='none' stroke='{color}' stroke-width='{sw}' "
        f"stroke-linejoin='round' stroke-linecap='round'{d}/>")

def dot(x, y, r=3, fill="#000"):
    add(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r}' fill='{fill}'/>")

def hole(x, y):
    add(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5.5' fill='#fff' stroke='{C['board']}' stroke-width='1.2'/>")

def conn(x0, y0, x1, y1, label, pos="in", fill=None, stroke=None, size=12, unused=False):
    rect(x0, y0, x1 - x0, y1 - y0, fill or (C["unused"] if unused else C["conn"]),
         stroke or C["connstroke"], 1.2)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if pos == "in":
        text(cx, cy + 4, label, size, "middle", "bold", "#666" if unused else C["text"])

def board(x, y, w, h, title, subtitle=None):
    rect(x, y, w, h, C["boardfill"], C["board"], 2, rx=4)
    text(x, y - 24 if subtitle else y - 9, title, 14, weight="bold", fill=C["board"])
    if subtitle:
        text(x, y - 8, subtitle, 11, fill=C["sub"])

def box(x, y, w, h, title, rows, color="#333", dash=None, fill="#fff"):
    rect(x, y, w, h, fill, color, 1.6, rx=6, dash=dash)
    text(x + 10, y + 19, title, 12.5, weight="bold", fill=color)
    lines(x + 10, y + 37, rows)

add(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>")
rect(0, 0, W, H, "#ffffff", "none", 0)

# ---- title + legend --------------------------------------------------------
text(20, 32, "Starling 2 Max — board-level wiring, connectors at their real positions", 19, weight="bold")
lines(20, 54, [
    "Board outlines and connector positions traced from ModalAI's VOXL 2 connector drawing and M0129 photo (5 px = 1 mm, ±1 mm). Connections confirmed by the owner's hardware check, 2026-10-20.",
    "Wiring per ModalAI's D0012 REV4 compute diagram + our 2026-10-14 bench session.   ⚪ = drawn by ModalAI, not inspected on our aircraft.",
], 11.5, 15, fill=C["sub"])
lx, ly = 20, 92
for i, (col, lab, dash) in enumerate([
        (C["pwr"], "+ power", None), (C["gnd"], "ground", None), (C["uart"], "UART / serial", None),
        (C["i2c"], "I²C", None), (C["usb"], "USB", None), (C["b2b"], "board-to-board stack", "6 4"),
        (C["mod"], "planned mod", "7 4")]):
    x = lx + i * 170
    poly([(x, ly), (x + 34, ly)], col, 3, dash)
    text(x + 42, ly + 4, lab, 12)

# ---- VOXL 2 top face -------------------------------------------------------
TX, TY = 310, 150
def T(x, y): return TX + x * S, TY + y * S
board(TX, TY, 70 * S, 36 * S, "VOXL 2 (M0054-1) — top face",
      "ModalAI's \"top\": J2 · J3 · J5 · J10 · J19")
for hx, hy in [(2.7, 2.2), (64.9, 2.2), (2.7, 33.3), (64.9, 33.3)]:
    hole(*T(hx, hy))
conn(*T(5.2, 1.9), *T(24.4, 7.0), "J5  120-pin B2B")
conn(*T(5.5, 27.6), *T(28.4, 35.9), "J3  60-pin B2B")
conn(*T(28.8, 30.0), *T(48.1, 36.0), "J19")
conn(*T(49.2, 31.6), *T(63.5, 36.0), "J10 · empty", unused=True)
conn(*T(64.5, 26.2), *T(71.0, 31.4), "J2", size=11)
dot(*T(30.0, 34.8), 2.6, "#e00")  # pin-1 marks
dot(*T(66.0, 27.4), 2.6, "#e00")

# ---- VOXL 2 bottom face ----------------------------------------------------
BX, BY = 310, 560
def B(x, y): return BX + x * S, BY + y * S
board(BX, BY, 70 * S, 36 * S, "VOXL 2 — bottom face (as ModalAI draws it)",
      "QRB5165 SIP · J4 · J6–J9 · J18")
for hx, hy in [(4.9, 2.2), (67.4, 2.2), (4.9, 33.3), (67.4, 33.3)]:
    hole(*B(hx, hy))
rect(*B(16.9, 7.0), 15.5 * S, 12.9 * S, "#c9ccd1", "#666", 1.2, rx=2)
lines(B(24.6, 0)[0], B(0, 11.6)[1], ["QRB5165 SIP", "Linux CPUs +", "SLPI = PX4"], 11, 13,
      anchor="middle", weight="bold")
conn(*B(9.0, 1.0), *B(12.9, 14.6), "", )
conn(*B(9.0, 20.9), *B(12.9, 34.8), "")
conn(*B(51.0, 21.2), *B(54.5, 34.8), "", unused=True)
text(*B(14.2, 8.5), "J6", 12, weight="bold"); text(*B(14.2, 28.5), "J7", 12, weight="bold")
text(*B(45.0, 28.5), "J8", 12, weight="bold", fill="#777")
text(*B(43.5, 32.5), "empty", 10, fill="#777", italic=True)
conn(*B(55.5, 0.5), *B(64.3, 4.7), "J18", size=11)
conn(*B(61.2, 8.5), *B(71.0, 17.4), "J9", size=11)
conn(*B(64.3, 18.7), *B(72.5, 31.0), "J4", size=11)
dot(*B(63.3, 4.0), 2.6, "#e00"); dot(*B(65.5, 30.0), 2.6, "#e00")

# ---- M0129 ESC top ---------------------------------------------------------
EX, EY = 855, 560
def E(x, y): return EX + x * S, EY + y * S
board(EX, EY, 36.5 * S, 36.5 * S, "M0129 ESC — top", "feeds VOXL 2 power")
for hx, hy in [(2.2, 2.2), (34.3, 2.2), (2.2, 34.3), (34.3, 34.3)]:
    hole(*E(hx, hy))
conn(*E(5.8, 3.8), *E(15.0, 8.6), "J1 UART", size=11)
conn(*E(24.4, 3.4), *E(27.9, 6.3), "+", size=11, fill="#f6d36b")
conn(*E(28.0, 3.4), *E(31.5, 6.3), "−", size=11, fill="#f6d36b")
text(*E(28.0, 9.4), "VREG OUT 5 V", 9.5, "middle", weight="bold")
conn(*E(14.2, 31.7), *E(17.5, 35.0), "+", size=11, fill="#f6d36b")
conn(*E(20.0, 31.7), *E(23.4, 35.0), "−", size=11, fill="#f6d36b")
text(*E(18.8, 30.4), "BATT", 9.5, "middle", weight="bold")
motor_map = {"ID3": ("L", 15.0, "M4"), "ID2": ("L", 26.4, "M1"),
             "ID0": ("R", 15.0, "M2"), "ID1": ("R", 26.4, "M3")}
for idn, (side, yc, m) in motor_map.items():
    xs = 3.8 if side == "L" else 31.3
    for dy in (-3.9, 0, 3.8):
        rect(*E(xs, yc + dy - 1.2), 2.4 * S, 2.4 * S, "#f6d36b", "#8a6d00", 1)
    if side == "L":
        text(E(0, 0)[0] - 6, E(0, yc)[1] + 4, f"{m} ◂ {idn}", 11.5, "end", "bold")
    else:
        text(E(36.5, 0)[0] + 6, E(0, yc)[1] + 4, f"{idn} ▸ {m}", 11.5, "start", "bold")
text(E(36.5, 0)[0] + 6, E(0, 10.5)[1], "ID ▸ motor", 10, fill=C["sub"])
text(E(0, 0)[0] - 6, E(0, 10.5)[1], "motor ◂ ID", 10, "end", fill=C["sub"])
text(20, 948, "Motor numbers: PX4 Quad X (M1 front-right, M2 rear-left, M3 front-left, M4 rear-right). ESC ID → motor from VOXL_ESC_FUNC1–4 = 102,103,101,104, read off both aircraft. ESC ID0 also drives the NeoPixel pad.", 11, fill=C["sub"])

# ---- M0129 ESC bottom ------------------------------------------------------
FX, FY = 1112, 560
def F(x, y): return FX + x * S, FY + y * S
board(FX, FY, 36.5 * S, 36.5 * S, "M0129 — bottom", "seen from below (mirrored)")
for hx, hy in [(2.2, 2.2), (34.3, 2.2), (2.2, 34.3), (34.3, 34.3)]:
    hole(*F(hx, hy))
for xmm, lab in [(6.4, "G"), (10.9, "⬇"), (13.1, "➕")]:
    add(f"<circle cx='{F(xmm,0)[0]:.1f}' cy='{F(0,4.3)[1]:.1f}' r='5' fill='#f6d36b' stroke='#8a6d00'/>")
text(*F(15.5, 10.8), "◂ NeoPixel pads (reachable)", 10, "start", "bold")
text(*F(15.5, 13.2), "G · OUT · VAUX", 9.5, "start", fill=C["sub"])
for xmm in (23.6, 25.4, 27.2, 28.9, 30.9):
    add(f"<circle cx='{F(xmm,0)[0]:.1f}' cy='{F(0,4.3)[1]:.1f}' r='3.6' fill='{C['unused']}' stroke='#888'/>")
text(*F(25.0, 8.0), "AUX PWM (unused)", 9.5, "middle", fill="#777")
rect(*F(20.0, 17.0), 9 * S, 4 * S, "#c9ccd1", "#666", 1, rx=2)
text(*F(24.5, 20.0), "AUX reg", 9.5, "middle", "bold")
lines(F(27.0, 0)[0], F(0, 25.5)[1], ["AUX reg: 3.3 V default,", "500–600 mA (5 V select", "disabled in firmware)"],
      9.5, 12, anchor="middle", fill=C["sub"])
text(*F(1.6, 7.4), "0", 11, weight="bold"); text(*F(33.3, 7.4), "3", 11, weight="bold")
text(*F(1.6, 33.0), "1", 11, weight="bold"); text(*F(33.3, 33.0), "2", 11, weight="bold")

# ---- wires: ESC VREG -> VOXL J4 (power) ------------------------------------
vp, vm = E(26.1, 3.4), E(29.7, 3.4)
j4x, j4y = B(72.5, 24.8)
poly([vp, (vp[0], 512), (770, 512), (770, j4y - 4), (j4x, j4y - 4)], C["pwr"], 2.6)
poly([vm, (vm[0], 518), (776, 518), (776, j4y + 4), (j4x, j4y + 4)], C["gnd"], 2.6)
text(680, 712, "5 V → J4-1", 11, weight="bold", fill=C["pwr"])
text(680, 726, "GND → J4-2", 11, weight="bold")
text(680, 740, "J4-3/4 not wired", 10, fill=C["sub"])

# ---- wires: J18 <-> ESC J1 (UART) ------------------------------------------
j18 = B(64.3, 2.6)
j1 = E(5.8, 6.2)
for off, col in [(-5, C["uart"]), (0, C["uart"]), (5, C["gnd"])]:
    poly([(j18[0], j18[1] + off), (740 + off, j18[1] + off), (740 + off, j1[1] + off), (j1[0], j1[1] + off)], col, 2)
# hop marks where the UART bundle crosses the power pair
for yy in (j18[1] - 5, j18[1], j18[1] + 5):
    pass
text(650, 512, "UART 3.3 V", 11, weight="bold", fill=C["uart"])
lines(650, 525, ["J18-2 TX → J1-2 RX", "J18-3 RX ← J1-3 TX", "J18-4 GND — J1-4"], 10, 12)

# ---- J9 -> laptop -----------------------------------------------------------
j9 = B(71.0, 12.9)
poly([j9, (682, j9[1])], C["usb"], 2.4)
box(682, 606, 80, 42, "Laptop", ["ADB only"], C["usb"])

# ---- battery ---------------------------------------------------------------
bp, bm = E(15.85, 35.0), E(21.7, 35.0)
box(838, 850, 92, 52, "Pack A", ["2S 18650"], C["pwr"])
box(960, 850, 92, 52, "Pack B", ["2S 18650"], C["pwr"])
poly([bp, (bp[0], 850)], C["pwr"], 2.6)
poly([bm, (bm[0], 790), (1030, 790), (1030, 850)], C["gnd"], 2.6)
poly([(930, 885), (960, 885)], C["pwr"], 2.6)
text(838, 922, "XT30 × 2 in series → 12–16.8 V (read 16.07–16.09 V)", 11, fill=C["sub"])

# ---- J19 -> GNSS + RC ------------------------------------------------------
j19c = T(38.4, 36.0)
split = (j19c[0], 365)
poly([j19c, split], "#555", 4)
dot(*split, 4, "#555")
poly([split, (420, 365), (420, 390)], C["i2c"], 2.4)
poly([split, (640, 365), (640, 390)], C["uart"], 2.4)
box(318, 390, 205, 100, "GNSS + mag (M10-5883)", [
    "J19-1 +5 V · J19-6 GND", "J19-2 TX → GNSS RX", "J19-3 RX ← GNSS TX", "J19-4/5 mag SCL/SDA (I²C)"], C["i2c"])
box(540, 390, 240, 100, "RC receiver", [
    "Starling 1: ELRS · Starling 2: Ghost", "J19-11 RX ← receiver TX", "J19-10 TX → receiver RX (ELRS only)",
    "J19-1 +5 V (shared) · J19-12 GND"], C["uart"])

# ---- J2 -> fan (planned) ---------------------------------------------------
j2 = T(71.0, 28.8)
poly([j2, (705, j2[1]), (705, 300)], C["mod"], 2.6, "7 4")
box(680, 300, 215, 84, "① Fan (planned · J2 empty)", [
    "25 × 25 × 7 mm · 5 V · 2 wires", "plug SHR-02V-S (JST SH 1.0)", "pin 1 +5 V always on",
    ], C["mod"], "7 4")
text(690, 378, "pin 2 PWM-switched GND ≤ 400 mA", 11.5)

# ---- J3/J5 -> stacked boards ----------------------------------------------
box(20, 140, 270, 205, "Plugs onto J3 + J5 (both aircraft)", [
    "Starling 2: Sparrow WiFi board",
    "  M0213-class (REV4 says M0141)",
    "  → mlan0 · 2 × U.FL WiFi antennas",
    "Starling 1: M0090-class 5G carrier",
    "  own USB hub · J11 USB 3 free",
    "  ├ EM9291 5G modem (M.2, unused)",
    "  └ J12 USB 2 → TX20U dongle → wlan0",
    "Starling 2 board also sits on J5 (owner",
    "check), though M0213 docs list J3 only"], C["b2b"], "6 4")
j3 = T(5.5, 31.7)
j5 = T(5.2, 4.4)
poly([(290, 230), (305, 230), (305, j3[1]), j3], C["b2b"], 2.2, "6 4")
poly([(290, 190), (300, 190), (300, j5[1]), j5], C["b2b"], 2.2, "6 4")
text(150, 362, "No room for an M0062 Ethernet add-on", 11, "middle", fill=C["sub"], italic=True)

# ---- J6/J7/J8 -> M0173 ----------------------------------------------------
box(20, 560, 270, 190, "Plugs onto J6 + J7: M0173", [
    "\"Starling front end\" camera board",
    "Our C29 config, 5 sensors:",
    "  AR0144 tracking — front, down",
    "  IMX412 hi-res — front, down",
    "  IRS2975 ToF (via M0171 + M0177 flex)",
    "  ⚪ VL53L1CX rangefinder (M0157)",
    "Micro-coax MCBL-00084-xx per camera",
    "Cabling matches ModalAI's REV4 drawing"], C["b2b"], "6 4")
j6, j7, j8 = B(9.0, 7.8), B(9.0, 27.8), B(51.0, 28.0)
poly([(290, 640), (300, 640), (300, j6[1]), j6], C["b2b"], 2.2, "6 4")
poly([(290, 680), (300, 680), (300, j7[1]), j7], C["b2b"], 2.2, "6 4")

# ---- NeoPixel -> LED chain (planned) --------------------------------------
sx = 1186
gx, ox, vx = F(6.4, 0)[0], F(10.9, 0)[0], F(13.1, 0)[0]
py = F(0, 4.3)[1]
ly0 = 812
poly([(gx, py + 5), (gx, ly0 + 8), (sx, ly0 + 8)], C["gnd"], 2, "7 4")
poly([(ox, py + 5), (ox, 772)], C["mod"], 2.2, "7 4")
rect(ox - 6, 772, 12, 22, "#fff", C["mod"], 1.6)
text(ox + 10, 787, "330–470 Ω", 10.5, weight="bold", fill=C["mod"])
poly([(ox, 794), (ox, ly0), (sx, ly0)], C["mod"], 2.2, "7 4")
poly([(vx, py + 5), (vx, ly0 - 8), (sx, ly0 - 8)], C["pwr"], 2, "7 4")
# strip: 4 arms x 4 px
sx = 1186
for arm in range(4):
    x0 = sx + arm * 33
    for p in range(4):
        rect(x0 + p * 7.5, ly0 - 5, 6, 10, "#fff4e0", C["mod"], 1)
text(sx, ly0 + 30, "② LED chain · 16 px", 11.5, weight="bold", fill=C["mod"])
lines(sx, ly0 + 44, ["4 arms × 4 px, 60 LED/m", "returns via the hub", "470–1000 µF at strip"], 10.5, 13)
box(sx, 896, 140, 48, "5 V BEC", ["only if VAUX = 3.3 V"], C["mod"], "7 4")

add("</svg>")
open(sys.argv[1], "w").write("\n".join(out))

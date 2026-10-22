#!/usr/bin/env python3
"""Top-down airframe layout for the Starling 2 Max, FRONT TO THE RIGHT (same convention
as board-level-wiring.svg). Traced from ModalAI's plan-view product photo, scaled by the
datasheet's 322 mm motor diagonal (0.22 mm/px in the photo).

Model coordinates are in mm: x = drone right (+), y = drone rear (+). P() maps them to
screen with the front pointing right.

Usage: gen_airframe_layout.py OUT.svg
"""
import math, sys

W, H = 1320, 1070
K = 1.9
CX, CY = 470, 548
out = []
add = out.append
FONT = "font-family='Helvetica, Arial, sans-serif'"
MOD = "#e07b00"


def P(x, y): return CX - y * K, CY + x * K


def text(x, y, s, size=12, anchor="start", weight="normal", fill="#111", italic=False):
    st = " font-style='italic'" if italic else ""
    add(f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' "
        f"fill='{fill}' {FONT}{st}>{s}</text>")


def rect_mm(x0, y0, x1, y1, fill, stroke="none", sw=1, rx=3, op=1):
    (a, b), (c, d) = P(x0, y0), P(x1, y1)
    a, c = sorted((a, c)); b, d = sorted((b, d))
    add(f"<rect x='{a:.1f}' y='{b:.1f}' width='{c-a:.1f}' height='{d-b:.1f}' rx='{rx}' fill='{fill}' "
        f"stroke='{stroke}' stroke-width='{sw}' opacity='{op}'/>")


def line(p, q, color, sw, dash=None, cap="round", op=1):
    ds = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<line x1='{p[0]:.1f}' y1='{p[1]:.1f}' x2='{q[0]:.1f}' y2='{q[1]:.1f}' stroke='{color}' "
        f"stroke-width='{sw}' stroke-linecap='{cap}' opacity='{op}'{ds}/>")


def callout(pt_mm, tx, ty, rows, color="#333"):
    p = P(*pt_mm)
    line(p, (tx - 8, ty - 4), "#b4b4b4", 1.0)
    add(f"<circle cx='{p[0]:.1f}' cy='{p[1]:.1f}' r='3' fill='{color}'/>")
    for j, r in enumerate(rows):
        text(tx, ty + j * 15, r, 12.5 if j == 0 else 11.5, weight="bold" if j == 0 else "normal",
             fill=color if j == 0 else "#333")


add(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>")
add(f"<rect x='0' y='0' width='{W}' height='{H}' fill='#ffffff'/>")
add("<defs><marker id='arr' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='7' markerHeight='7' "
    "orient='auto-start-reverse'><path d='M0,0 L10,5 L0,10 z' fill='#6b7785'/></marker></defs>")
text(20, 32, "Starling 2 Max — airframe layout, seen from above, front → right", 19, weight="bold")
text(20, 52, "Traced from ModalAI's top-down product photo, scaled to the datasheet's 322 mm motor diagonal (±5 mm). "
     "Same orientation as the board-level wiring drawing.", 11.5, fill="#555")
text(20, 67, "Connections confirmed by the owner's hardware check (2026-10-20); the outline of our C29 camera cluster may "
     "differ from the photo.", 11.5, fill="#555")
text(W - 24, 36, "FRONT ▶", 20, "end", "bold", "#1f4e79")

motors = {"FL": (-129, -96, "M3", "ID1", "CW"), "FR": (129, -96, "M1", "ID2", "CCW"),
          "RL": (-129, 96, "M2", "ID0", "CCW"), "RR": (129, 96, "M4", "ID3", "CW")}
corner = {"FL": (-27, -36), "FR": (27, -36), "RL": (-27, 36), "RR": (27, 36)}

for k, (x, y, *_) in motors.items():
    cx, cy = P(x, y)
    add(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{89*K:.1f}' fill='#f3f5f7' stroke='#c3c8ce' "
        f"stroke-width='1.2' stroke-dasharray='5 4'/>")
for k, (x, y, *_) in motors.items():
    line(P(*corner[k]), P(x, y), "#3a3a3a", 10 * K, cap="butt")
    line(P(corner[k][0] * 0.3, corner[k][1] * 0.3), P(*corner[k]), "#3a3a3a", 10 * K, cap="butt")

rect_mm(-31, -43, 31, 43, "#2b2b2b", rx=6)
rect_mm(-50, -36, -30, 33, "#9be15d", "#5c9c2a", 1.5, rx=8)
rect_mm(30, -36, 50, 33, "#9be15d", "#5c9c2a", 1.5, rx=8)
rect_mm(-18, -36, 18, 34, "#2f6db5", "#cfe0f5", 1.5, rx=3, op=0.92)
rect_mm(-52, -9, 52, 9, "#141414", rx=3, op=0.9)
rect_mm(-22, -67, 22, -43, "#555", rx=6)
rect_mm(-11, 43, 19, 63, "#2f6db5", rx=5, op=0.85)
rect_mm(-20, 64, 19, 94, "#555", rx=5)
rect_mm(-11, 70, 11, 90, "#c9a66b", rx=2)
# rear-facing connectors on the VOXL 2 and ESC (owner check): tick marks on the rear edge
for xm in (-14, -6, 6, 14):
    a = P(xm, 34); b = P(xm, 39)
    line(a, b, "#ffd34d", 3)

for k, (x, y, m, esc, rot) in motors.items():
    cx, cy = P(x, y)
    add(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{14*K:.1f}' fill='#1b1b1b' stroke='#888' stroke-width='1.5'/>")
    r = 44 * K
    c = -90 if x < 0 else 90           # put the spin arrow on the outboard side
    a0, a1 = math.radians(c - 40), math.radians(c + 40)
    p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0)); p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
    if rot == "CW":
        d = f"M{p0[0]:.1f},{p0[1]:.1f} A{r:.1f},{r:.1f} 0 0 1 {p1[0]:.1f},{p1[1]:.1f}"
    else:
        d = f"M{p1[0]:.1f},{p1[1]:.1f} A{r:.1f},{r:.1f} 0 0 0 {p0[0]:.1f},{p0[1]:.1f}"
    add(f"<path d='{d}' fill='none' stroke='#6b7785' stroke-width='2' marker-end='url(#arr)'/>")
    text(cx, cy + 5, m, 15, "middle", "bold", "#fff")
    ly = cy - r - 14 if x < 0 else cy + r + 26
    text(cx, ly, f"{m} · {rot} · ESC {esc}", 12.5, "middle", "bold", "#333")

order = ["RL", "FL", "FR", "RR"]   # ring from the arm nearest the LED pads (rear-left), clockwise
pitch = 16.7
for i, k in enumerate(order):
    (x, y, *_), (cx0, cy0) = motors[k], corner[k]
    L = math.hypot(x - cx0, y - cy0)
    ux, uy = (x - cx0) / L, (y - cy0) / L
    nx, ny = -uy, ux
    a = (cx0 + ux * 12, cy0 + uy * 12)
    b = (cx0 + ux * (12 + 4 * pitch), cy0 + uy * (12 + 4 * pitch))
    line(P(*a), P(*b), MOD, 6 * K, cap="butt", op=0.9)
    for p in range(4):
        q = P(a[0] + ux * pitch * (p + 0.5), a[1] + uy * pitch * (p + 0.5))
        add(f"<rect x='{q[0]-5:.1f}' y='{q[1]-5:.1f}' width='10' height='10' fill='#fff4c2' stroke='#8a4b00' stroke-width='1.2'/>")
    off = 6.5
    line(P(b[0] + nx * off, b[1] + ny * off), P(cx0 + nx * off, cy0 + ny * off), MOD, 1.8, "5 3")
    lab = P(b[0] + ux * 8 - nx * 13, b[1] + uy * 8 - ny * 13)
    text(lab[0], lab[1] + 4, f"px {4*i}–{4*i+3}", 12.5, "middle", "bold", MOD)
line(P(-10, 30), P(-27, 36), MOD, 1.8, "5 3")   # LED pads (rear-left) to the first arm

fx, fy = motors["FR"][:2]; c0 = corner["FR"]
L = math.hypot(fx - c0[0], fy - c0[1])
TXC = 905
callout((0, -60), TXC, 140, ["Front camera cluster", "tracking + hi-res (+ ToF on C29)", "→ M0173 under the VOXL 2"])
callout((0, -22), TXC, 215, ["VOXL 2 stack, long axis fore-aft", "add-on board on J3 + J5 on top",
                              "ESC M0129 underneath, power face up"], "#2f6db5")
callout((14, 36), TXC, 300, ["Rear edge (yellow ticks)", "VOXL J4 + J9, ESC J1, VREG and",
                             "the NeoPixel pads all face the rear"], "#b8860b")
callout(((c0[0] + fx) / 2 + 4, (c0[1] + fy) / 2 + 3), TXC, 385,
        ["Arm: ~10 mm wide", f"~{L - 14:.0f} mm clear by photo scale", "(owner measured ~75 mm — re-check:",
         "at ≥ 100 mm, 6 px at 60/m fits)"], MOD)
callout((-8, 0), TXC, 485, ["① Fan: 3010 in a shroud at one stack end", "powered from the LED buck (J2 stays empty)"], MOD)
callout((-40, 20), TXC, 545, ["Battery: 2 × 2S 18650 packs", "XT30 each, wired in series (4S)"], "#3f7d1c")
callout((4, 53), TXC, 605, ["Hi-res down camera"], "#2f6db5")
callout((0, 80), TXC, 650, ["GNSS + mag on rear mast", "fitted, unused indoors"], "#555")

text(20, 990, "② LED chain (planned, orange): one data line, 16 px, a ring from the arm nearest the pads (rear-left): M2 → M3 → M1 → M4, "
     "skipping the crowded rear edge. If the pads turn out rear-right, mirror it. Each run starts ~12 mm out from the plate; 4 px = 67 mm.", 12, fill="#333")
text(20, 1006, "Dashed = plain 3-wire return to the hub. Motor positions assume PX4 Quad X: confirm from CA_ROTOR* parameters.", 12, fill="#333")
text(20, 1026, "Motors: PX4 Quad X numbering and spin (M1 FR CCW, M2 RL CCW, M3 FL CW, M4 RR CW). ESC ID → motor from "
     "VOXL_ESC_FUNC1–4 = 102,103,101,104. Verify spin against your props before relying on it.", 12, fill="#333")
sx0, sy0 = 40, 1052
line((sx0, sy0), (sx0 + 50 * K, sy0), "#111", 3, cap="butt")
line((sx0, sy0 - 6), (sx0, sy0 + 6), "#111", 2); line((sx0 + 50 * K, sy0 - 6), (sx0 + 50 * K, sy0 + 6), "#111", 2)
text(sx0 + 50 * K + 10, sy0 + 5, "50 mm", 12, weight="bold")
text(240, sy0 + 5, "Motor centres 258 mm apart side to side, 193 mm front to back (322 mm diagonal) · 7\" props, "
     "89 mm radius", 11.5, fill="#555")

add("</svg>")
open(sys.argv[1], "w").write("\n".join(out))

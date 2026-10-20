#!/usr/bin/env python3
"""Top-down airframe layout for the Starling 2 Max, traced from ModalAI's plan-view
product photo. Scale set by the datasheet's 322 mm motor diagonal (0.22 mm/px in
the photo); front is up."""
import math, sys

W, H = 1260, 1010
K = 2.0                  # px per mm
CX, CY = 470, 505
out = []
add = out.append
FONT = "font-family='Helvetica, Arial, sans-serif'"
MOD = "#e07b00"

def P(x, y): return CX + x * K, CY + y * K

def text(x, y, s, size=12, anchor="start", weight="normal", fill="#111", italic=False):
    st = " font-style='italic'" if italic else ""
    add(f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' "
        f"fill='{fill}' {FONT}{st}>{s}</text>")

def rect_mm(x0, y0, x1, y1, fill, stroke="none", sw=1, rx=3, op=1, dash=None):
    (a, b), (c, d) = P(x0, y0), P(x1, y1)
    ds = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<rect x='{a:.1f}' y='{b:.1f}' width='{c-a:.1f}' height='{d-b:.1f}' rx='{rx}' fill='{fill}' "
        f"stroke='{stroke}' stroke-width='{sw}' opacity='{op}'{ds}/>")

def line(p, q, color, sw, dash=None, cap="round", op=1):
    ds = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<line x1='{p[0]:.1f}' y1='{p[1]:.1f}' x2='{q[0]:.1f}' y2='{q[1]:.1f}' stroke='{color}' "
        f"stroke-width='{sw}' stroke-linecap='{cap}' opacity='{op}'{ds}/>")

def leader(p, q, color="#555"):
    line(p, q, color, 1.2)
    add(f"<circle cx='{p[0]:.1f}' cy='{p[1]:.1f}' r='2.5' fill='{color}'/>")

add(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>")
add(f"<rect x='0' y='0' width='{W}' height='{H}' fill='#ffffff'/>")
text(20, 32, "Starling 2 Max — airframe layout, top view (front up)", 19, weight="bold")
text(20, 52, "Traced from ModalAI's top-down product photo, scaled to the datasheet's 322 mm motor diagonal (±5 mm).", 11.5, fill="#555")
text(20, 67, "Connections confirmed by the owner's hardware check (2026-10-20); exact outline of our C29 camera cluster may differ from the photo.", 11.5, fill="#555")

motors = {  # name: (x, y, PX4 motor, ESC ID, rotation)
    "FL": (-129, -96, "M3", "ID1", "CW"),
    "FR": (129, -96, "M1", "ID2", "CCW"),
    "RL": (-129, 96, "M2", "ID0", "CCW"),
    "RR": (129, 96, "M4", "ID3", "CW"),
}
corner = {"FL": (-27, -36), "FR": (27, -36), "RL": (-27, 36), "RR": (27, 36)}

# props
for k, (x, y, *_ ) in motors.items():
    cx, cy = P(x, y)
    add(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{89*K:.1f}' fill='#f3f5f7' stroke='#c3c8ce' stroke-width='1.2' stroke-dasharray='5 4'/>")

# arms (10 mm wide carbon) + motor-wire bundles
for k, (x, y, *_ ) in motors.items():
    line(P(*corner[k]), P(x, y), "#3a3a3a", 10 * K, cap="butt")
    line(P(corner[k][0] * 0.3, corner[k][1] * 0.3), P(*corner[k]), "#3a3a3a", 10 * K, cap="butt")

# centre plate, batteries, strap
rect_mm(-31, -43, 31, 43, "#2b2b2b", rx=6)
rect_mm(-50, -36, -30, 33, "#9be15d", "#5c9c2a", 1.5, rx=8)
rect_mm(30, -36, 50, 33, "#9be15d", "#5c9c2a", 1.5, rx=8)
rect_mm(-18, -36, 18, 34, "#2f6db5", "#cfe0f5", 1.5, rx=3, op=0.92)
rect_mm(-52, -9, 52, 9, "#141414", rx=3, op=0.9)
# nose + tail
rect_mm(-22, -67, 22, -43, "#555", rx=6)
rect_mm(-11, 43, 19, 63, "#2f6db5", rx=5, op=0.85)
rect_mm(-20, 64, 19, 94, "#555", rx=5)
rect_mm(-11, 70, 11, 90, "#c9a66b", rx=2)

# motors
for k, (x, y, m, esc, rot) in motors.items():
    cx, cy = P(x, y)
    add(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{14*K:.1f}' fill='#1b1b1b' stroke='#888' stroke-width='1.5'/>")
    # rotation arrow arc
    r = 44 * K
    sweep = (1 if rot == "CW" else 0) if y < 0 else (0 if rot == "CW" else 1)
    a0, a1 = (-130, -50) if y < 0 else (130, 50)
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    if rot == "CCW":
        x0, y0, x1, y1 = x1, y1, x0, y0
    add(f"<path d='M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 0 {sweep} {x1:.1f},{y1:.1f}' fill='none' "
        f"stroke='#6b7785' stroke-width='2' marker-end='url(#arr)'/>")
    text(cx, cy + 5, m, 15, "middle", "bold", "#fff")
    lx = cx + (-1 if x < 0 else 1) * 0
    ly = cy + (y / abs(y)) * 125 * K / 2.6
    text(cx, cy + (44 if y > 0 else -54) * K / 1.0 + (16 if y > 0 else 0), f"{m} · {rot} · ESC {esc}", 12.5, "middle", "bold", "#333")
add("<defs><marker id='arr' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'>"
    "<path d='M0,0 L10,5 L0,10 z' fill='#6b7785'/></marker></defs>")

# LED segments: 4 px at 60/m (16.7 mm pitch) starting 12 mm outboard of the plate corner
order = ["FL", "FR", "RR", "RL"]
pitch = 16.7
for i, k in enumerate(order):
    (x, y, *_), (cx0, cy0) = motors[k], corner[k]
    L = math.hypot(x - cx0, y - cy0)
    ux, uy = (x - cx0) / L, (y - cy0) / L
    nx, ny = -uy, ux
    s0 = 12
    a = (cx0 + ux * s0, cy0 + uy * s0)
    b = (cx0 + ux * (s0 + 4 * pitch), cy0 + uy * (s0 + 4 * pitch))
    line(P(*a), P(*b), MOD, 6 * K, cap="butt", op=0.9)
    for p in range(4):
        px = (a[0] + ux * pitch * (p + 0.5), a[1] + uy * pitch * (p + 0.5))
        q = P(*px)
        add(f"<rect x='{q[0]-5:.1f}' y='{q[1]-5:.1f}' width='10' height='10' fill='#fff4c2' stroke='#8a4b00' stroke-width='1.2'/>")
    # return wire back to the hub, offset to one side
    off = 6.5
    r0 = (b[0] + nx * off, b[1] + ny * off)
    r1 = (cx0 + nx * off, cy0 + ny * off)
    line(P(*r0), P(*r1), MOD, 1.8, "5 3")
    lab = P(b[0] + ux * 6 - nx * 14, b[1] + uy * 6 - ny * 14)
    text(lab[0], lab[1] + 4, f"px {4*i}–{4*i+3}", 12.5, "middle", "bold", MOD)

# hub-side feed, schematic
line(P(0, -6), P(-27, -36), MOD, 1.8, "5 3")
text(*P(-16, -27), "", 10)

# callouts
def callout(pt_mm, tx, ty, rows, color="#333", anchor="start", bold_first=True):
    p = P(*pt_mm)
    leader(p, (tx - (6 if anchor == "start" else -6), ty - 4), color)
    for j, r in enumerate(rows):
        text(tx, ty + j * 15, r, 12.5 if j == 0 else 11.5, anchor, "bold" if (j == 0 and bold_first) else "normal",
             color if j == 0 else "#333")

callout((0, -60), 940, 150, ["Front camera cluster", "tracking + hi-res (+ ToF on C29)", "→ M0173 under the VOXL 2"], "#333")
callout((0, -20), 940, 222, ["VOXL 2 stack (long axis fore-aft)", "+ J3/J5 add-on (WiFi / M0090 modem)", "ESC M0129 under the VOXL 2 — LED pads", "reachable below the J18 cable"], "#2f6db5")
callout((-40, 20), 270, 620, ["Battery: 2 × 2S 18650 packs", "XT30 each, wired in series (4S)"], "#3f7d1c", "end")
callout((10, 53), 940, 760, ["Hi-res down camera"], "#2f6db5")
callout((0, 82), 940, 800, ["GNSS + mag on rear mast", "fitted, unused indoors"], "#555")
callout((-8, 0), 270, 410, ["① Fan on VOXL J2", "position TBD: needs 25 × 25 × 7 mm", "clearance over the SIP side"], MOD, "end")

# arm dimension note on FR arm
fx, fy = motors["FR"][0], motors["FR"][1]
c0 = corner["FR"]
L = math.hypot(fx - c0[0], fy - c0[1])
text(*P(c0[0] + (fx - c0[0]) * 0.55 + 14, c0[1] + (fy - c0[1]) * 0.55 + 16), "", 10)
callout(((c0[0] + fx) / 2 + 4, (c0[1] + fy) / 2 + 3), 940, 330,
        ["Arm: ~10 mm wide", f"~{L - 14:.0f} mm clear by photo scale", "(owner measured ~75 mm — re-check:", "at ≥ 100 mm, 6 px at 60/m fits)"], MOD)

# LED chain note
text(20, 900, "② LED chain (planned, orange): one data line, 16 px. ESC ⬇ OUT → arm FL px 0–3 → back to hub → FR 4–7 → RR 8–11 → RL 12–15.", 12, fill="#333")
text(20, 916, "Each run starts ~12 mm out from the plate; 4 px × 16.7 mm = 67 mm. Dashed = plain 3-wire return to the hub. Order is a suggestion — fix it before soldering.", 12, fill="#333")
text(20, 940, "Motors: PX4 Quad X numbering and spin (M1 FR CCW, M2 RL CCW, M3 FL CW, M4 RR CW). ESC ID → motor from VOXL_ESC_FUNC1–4 = 102,103,101,104 on both aircraft.", 12, fill="#333")
text(20, 956, "Verify spin directions against the props on your aircraft before relying on them.", 12, fill="#555", italic=True)

# front arrow + scale bar
text(CX, 98, "▲ FRONT", 14, "middle", "bold", "#333")
sx0, sy0 = 40, 985
line((sx0, sy0), (sx0 + 50 * K, sy0), "#111", 3, cap="butt")
line((sx0, sy0 - 6), (sx0, sy0 + 6), "#111", 2); line((sx0 + 50 * K, sy0 - 6), (sx0 + 50 * K, sy0 + 6), "#111", 2)
text(sx0 + 50 * K + 10, sy0 + 5, "50 mm", 12, weight="bold")
text(260, sy0 + 5, "Motor centres 258 mm apart side-to-side, 193 mm front-to-back (322 mm diagonal) · 7\" props, 89 mm radius", 11.5, fill="#555")

add("</svg>")
open(sys.argv[1], "w").write("\n".join(out))

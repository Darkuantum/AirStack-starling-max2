#!/usr/bin/env python3
"""16:9 slide images replacing the Mermaid charts in
the hardware docs (docs/HARDWARE.md, reports/Starling 2 Max hardware investigation.md). Plain SVG, no dependencies.

Usage: gen_slides.py OUT_DIR    (writes slide-*.svg)
"""
import os, sys

W, H = 1600, 900
FONT = "font-family='Helvetica, Arial, sans-serif'"
PAL = {
    "hw":   ("#e7f1ff", "#2b6cb0"),   # existing hardware / software
    "ok":   ("#e6f6ec", "#22863a"),   # exists in the tree
    "new":  ("#fff3cd", "#b8860b"),   # new work / planned modification
    "warn": ("#ffe3e3", "#c53030"),   # safety / gap
    "grey": ("#f1f1f1", "#8a8a8a"),   # deferred / unused
    "lane": ("#f7f9fc", "#d6dde8"),
}
INK, SUB = "#14202e", "#56606d"
COL = {"pwr": "#d62828", "data": "#2b6cb0", "b2b": "#8a8a8a", "mod": "#b8860b", "warn": "#c53030",
       "ok": "#22863a", "ink": "#3d4752"}


class Slide:
    def __init__(self, title, subtitle, footer):
        self.o = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>",
                  "<defs>" + "".join(
                      f"<marker id='a-{k}' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' "
                      f"orient='auto-start-reverse'><path d='M0,0 L10,5 L0,10 z' fill='{v}'/></marker>"
                      for k, v in COL.items()) + "</defs>",
                  f"<rect width='{W}' height='{H}' fill='#ffffff'/>",
                  f"<rect width='{W}' height='8' fill='#1f4e79'/>"]
        self.text(56, 74, title, 38, weight="bold")
        self.text(56, 110, subtitle, 20, fill=SUB)
        self.o.append(f"<line x1='56' y1='{H-50}' x2='{W-56}' y2='{H-50}' stroke='#e2e6ec'/>")
        self.text(56, H - 22, footer, 14, fill=SUB)
        self.text(W - 56, H - 22, "Starling 2 Max · modification stack", 14, "end", fill=SUB)

    def text(self, x, y, s, size=16, anchor="start", weight="normal", fill=INK, italic=False):
        st = " font-style='italic'" if italic else ""
        s = str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.o.append(f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' "
                      f"font-weight='{weight}' fill='{fill}' {FONT}{st}>{s}</text>")

    def box(self, x, y, w, h, title, rows=(), kind="hw", badge=None, dash=False, tsize=19, rsize=15):
        fill, stroke = PAL[kind]
        d = " stroke-dasharray='8 5'" if dash else ""
        self.o.append(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='12' fill='{fill}' stroke='{stroke}' "
                      f"stroke-width='2.2'{d}/>")
        tx = x + 16
        if badge:
            self.o.append(f"<circle cx='{x+26}' cy='{y+27}' r='15' fill='{stroke}'/>")
            self.text(x + 26, y + 33, badge, 17, "middle", "bold", "#fff")
            tx = x + 50
        self.text(tx, y + 34, title, tsize, weight="bold", fill=stroke if kind != "hw" else "#1f4e79")
        for i, r in enumerate(rows):
            self.text(x + 16, y + 62 + i * (rsize + 6), r, rsize, fill=INK)
        return (x, y, w, h)

    def arrow(self, pts, col="data", label=None, lpos=None, dash=False, both=False, sw=2.6, lsize=14, lanchor="middle"):
        c = COL[col]
        p = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        d = " stroke-dasharray='8 5'" if dash else ""
        ms = f" marker-start='url(#a-{col})'" if both else ""
        self.o.append(f"<path d='{p}' fill='none' stroke='{c}' stroke-width='{sw}' stroke-linejoin='round'{d}"
                      f" marker-end='url(#a-{col})'{ms}/>")
        if label:
            lx, ly = lpos if lpos else ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2 - 8)
            for j, line in enumerate(label.split("\n")):
                w = 0.56 * lsize * len(line)
                bx = lx - w / 2 if lanchor == "middle" else (lx if lanchor == "start" else lx - w)
                yy = ly + j * (lsize + 4)
                self.o.append(f"<rect x='{bx-4:.1f}' y='{yy-lsize+1:.1f}' width='{w+8:.1f}' height='{lsize+5}' "
                              f"rx='3' fill='#ffffff' opacity='0.92'/>")
                self.text(lx, yy, line, lsize, lanchor, "bold", c)

    def note(self, x, y, w, h, s_rows, kind="warn", size=17):
        fill, stroke = PAL[kind]
        self.o.append(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='10' fill='{fill}' stroke='{stroke}' stroke-width='1.6'/>")
        for i, r in enumerate(s_rows):
            self.text(x + 18, y + 30 + i * (size + 8), r, size, weight="bold" if i == 0 else "normal",
                      fill=stroke if i == 0 else INK)

    def lane(self, x, y, w, h, title):
        fill, stroke = PAL["lane"]
        self.o.append(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='14' fill='{fill}' stroke='{stroke}' stroke-width='1.5'/>")
        self.text(x + 18, y + 30, title, 17, weight="bold", fill=SUB)

    def legend(self, x, y, items):
        for i, (kind, lab) in enumerate(items):
            fill, stroke = PAL[kind]
            xx = x + i * 230
            self.o.append(f"<rect x='{xx}' y='{y-14}' width='26' height='18' rx='4' fill='{fill}' stroke='{stroke}' stroke-width='2'/>")
            self.text(xx + 36, y, lab, 15, fill=SUB)

    def save(self, path):
        self.o.append("</svg>")
        open(path, "w").write("\n".join(self.o))


def slide_hardware(path):
    s = Slide("The aircraft, and the five places you modify it",
              "Every board on the Starling 2 Max and what connects them. Numbered boxes are the five workstreams.",
              "Sources: ModalAI REV4 compute diagram · bench session 2026-10-14 · owner hardware check 2026-10-20")
    s.box(56, 210, 270, 170, "Battery", ["2 × 2S 18650 packs", "wired in series → 4S", "12–16.8 V · XT30 × 2"])
    s.box(420, 180, 360, 230, "M0129 ESC, 4-in-1", ["drives 4 motors; PX4 talks to it", "over one UART (J18 ↔ J1)",
                                                    "VREG 5 V output powers the VOXL 2", "LED pads: 3.3 V, 500–600 mA,",
                                                    "max 32 pixels"])
    s.box(880, 150, 380, 270, "VOXL 2 (M0054-1)", ["Apps CPU: Linux, ROS 2 Foxy,", "camera + MPA services",
                                                   "SLPI DSP: the whole PX4 v1.14", "J19: GNSS + RC receiver",
                                                   "J6 + J7: M0173 camera board", "throttles at ~95 °C"])
    s.box(1340, 150, 220, 270, "J3 + J5 add-on", ["Starling 1:", "5G carrier + EM9291", "+ USB WiFi dongle",
                                                  "", "Starling 2:", "Sparrow WiFi board"], "grey")
    s.arrow([(326, 295), (420, 295)], "pwr", "12–16.8 V", (373, 280))
    s.arrow([(780, 245), (880, 245)], "pwr", "5 V", (830, 232))
    s.arrow([(780, 345), (880, 345)], "data", "UART: motors\n+ LED colours", (830, 318), both=True)
    s.arrow([(1260, 285), (1340, 285)], "b2b", "B2B", (1300, 270), both=True)
    s.box(56, 520, 240, 150, "Companion", ["planned · ≤ ~170 g", "USB (J9 / J11) or WiFi", "own 5 V BEC"], "new", "⑤", dash=True, rsize=14)
    s.box(330, 520, 300, 150, "Motors + props", ["4 × 1500 kV motors", "7 × 3.7 × 3 props", "S1: 2203.5 · S2: 2204"], "new", "③")
    s.box(670, 520, 300, 150, "LED strip", ["16 px on one data line", "solder to ESC pads", "330–470 Ω in series"], "new", "②")
    s.box(1010, 520, 280, 150, "Cooling fan", ["VOXL 2 J2 header", "25 × 25 × 7 mm, 5 V", "2 wires only"], "new", "①")
    s.box(1330, 520, 230, 150, "Livox Mid-360", ["265 g · deferred", "does not fit: ESC", "rated < 750 g total"], "grey", "④", dash=True)
    s.arrow([(520, 410), (520, 520)], "mod", "3-phase × 4", (575, 470), lanchor="middle")
    s.arrow([(700, 410), (760, 520)], "mod", "solder pads", (775, 465))
    s.arrow([(1070, 420), (1120, 520)], "mod", "J2 · 5 V PWM", (1150, 470))
    s.note(56, 720, 1504, 100, ["⚠  The ESC that would power the LEDs is also the VOXL 2's power supply",
                               "A full-white strip command could brown out the flight computer. Cap the LED current in "
                               "software, not just the brightness setting."])
    s.save(path)


def slide_control(path):
    s = Slide("The control path that flies today",
              "Mocap pose goes INTO PX4's estimator; the pose AirStack plans against comes back OUT of PX4.",
              "Source: this repo's launch files and RUNBOOK · PX4 v1.14 over uXRCE-DDS, domain 1")
    s.lane(40, 140, 290, 580, "HANGAR")
    s.lane(350, 140, 720, 580, "GROUND LAPTOP · ROS 2 JAZZY")
    s.lane(1090, 140, 470, 580, "DRONE · VOXL 2")
    A, B, w = 380, 790, 250
    s.box(60, 190, 250, 90, "OptiTrack", ["8 cameras"], "grey")
    s.box(60, 340, 250, 110, "Motive PC", ["192.168.9.124", "NatNet broadcast 50 Hz"], "grey")
    s.arrow([(185, 280), (185, 340)], "ink")
    s.box(A, 190, w, 90, "./mocap.sh", ["motion_capture_tracking"])
    s.box(B, 620, w, 80, "QGroundControl", ["the ONLY arming display"], "warn", tsize=18)
    s.box(A, 340, w, 90, "mocap_bridge", ["ENU → NED"])
    s.box(B, 340, w, 90, "MicroXRCEAgent", ["udp4 :8888"])
    s.box(A, 490, w, 90, "odometry_conversion", ["restamps frames · TF"], tsize=18)
    s.box(B, 490, w, 90, "px4_interface", ["commands · ACK log"])
    s.box(A, 620, w, 80, "swarm_commander", ["trajectory + CBF + fence"], "new", tsize=18)
    s.box(1120, 190, 200, 90, "PX4 EKF2", ["EV_CTRL = 11"], "ok")
    s.box(1340, 190, 200, 90, "Estimator inputs", ["no GPS · mag · baro"], "ok", tsize=17)
    s.box(1120, 340, 420, 90, "PX4 control loops", ["on the SLPI DSP inside the QRB5165"], "ok")
    s.box(1120, 490, 200, 90, "voxl-mavlink-server", ["apps CPU"], "ok", tsize=16)
    s.box(1340, 490, 200, 90, "ESC → motors", ["M0129 over J18"], "ok")
    s.box(1120, 745, 420, 80, "RC transmitter", ["ch8 KILL · ch6 MANUAL"], "warn")
    # hangar -> laptop
    s.arrow([(310, 395), (340, 395), (340, 235), (A, 235)], "ink", "NatNet\nUDP", (340, 300))
    s.arrow([(505, 280), (505, 340)], "data", "/drone_1/pose", (515, 316), lanchor="start")
    s.arrow([(A + w, 385), (B, 385)], "data", "fmu/in/vehicle_\nvisual_odometry", (710, 352), lsize=12)
    s.arrow([(B + w, 385), (1080, 385), (1080, 235), (1120, 235)], "data", "uXRCE-DDS\nover WiFi", (1080, 296), both=True)
    s.arrow([(880, 430), (880, 490)], "data", "fmu/out/vehicle_odometry", (870, 466), lanchor="end", lsize=13)
    s.arrow([(960, 490), (960, 430)], "data", "fmu/in/trajectory_setpoint", (970, 466), lanchor="start", lsize=13)
    s.arrow([(B, 535), (A + w, 535)], "data", "interface/\nodometry", (710, 505), lsize=13)
    s.arrow([(505, 580), (505, 620)], "data", "odometry_conversion/\nodometry", (495, 596), lanchor="end", lsize=12)
    s.arrow([(A + w, 660), (710, 660), (710, 560), (B, 560)], "mod", "trajectory_command", (710, 688), lsize=13)
    # drone internals
    s.arrow([(1220, 280), (1220, 340)], "ok")
    s.arrow([(1440, 430), (1440, 490)], "ok")
    s.arrow([(1220, 430), (1220, 490)], "ok", both=True)
    s.arrow([(1220, 580), (1220, 660), (B + w, 660)], "warn", "MAVLink udp 14550", (1130, 650), lsize=13, both=True)
    s.arrow([(1330, 745), (1330, 430)], "warn", "KILL or MANUAL only", (1340, 640), lanchor="start", lsize=13)
    s.text(1340, 658, "POSCTL / ALTCTL still obey setpoints", 12, fill=COL["warn"])
    s.note(40, 745, 1050, 85, ["Two seams, and a LiDAR estimator has to fill both",
                              "① pose INTO PX4 (mocap_bridge → EKF2 external vision)   ② odometry OUT of PX4 into AirStack "
                              "(px4_interface → odometry_conversion)"], "hw", 16)
    s.save(path)


def slide_lidar(path):
    s = Slide("What the LiDAR goal actually changes",
              "LiDAR → map already exists in the tree. LiDAR → pose and LiDAR → local avoidance are the gaps.",
              "Source: vendored AirStack tree (global_bringup/config/vdb_params.yaml, local.launch.xml, px4_interface.launch.xml)")
    s.note(56, 132, 1488, 46, ["Deferred: no LiDAR fits under the M0129's 750 g rating. This is the software picture for a future airframe."], "grey", 17)
    s.legend(56, 216, [("ok", "already in your tree"), ("new", "you would build"), ("warn", "unsolved gap")])
    bw, xs = 180, [290, 496, 702, 908, 1114, 1320]
    s.box(56, 250, 200, 300, "Livox Mid-360", ["265 g", "0.1 m min range", "100BASE-TX", "built-in IMU"], "new")
    r1 = [("livox_ros_driver2", ["you supply it:", "AirStack vendors", "no LiDAR driver"], "new"),
          ("Raw cloud", ["sensors/ouster/", "point_cloud_raw"], "ok"),
          ("Cloud filter", ["lidar_point_", "cloud_filter", "near_range 0.75 m"], "ok"),
          ("Clean cloud", ["sensors/ouster/", "point_cloud"], "ok"),
          ("vdb_mapping", ["sources: [lidar]"], "ok"),
          ("Global planner", ["random_walk", "(exploration in", "tree, not launched)"], "ok")]
    for x, (t, rows, k) in zip(xs, r1):
        s.box(x, 250, bw, 130, t, rows, k, tsize=17, rsize=14)
    s.arrow([(256, 315), (290, 315)], "mod")
    for a, b in zip(xs[:-1], xs[1:]):
        s.arrow([(a + bw, 315), (b, 315)], "ok" if a > 290 else "mod")
    r2 = [("FAST-LIO2", ["LiDAR-inertial", "odometry"], "new"),
          ("Your estimator", ["perception/<est>/", "odometry"], "new"),
          ("odometry_conversion", ["edit its", "odometry_in remap"], "ok"),
          ("Canonical odometry", ["odometry_conversion/", "odometry: every", "consumer reads it"], "ok")]
    for x, (t, rows, k) in zip(xs[:4], r2):
        s.box(x, 440, bw, 120, t, rows, k, tsize=15 if len(t) > 14 else 17, rsize=14)
    s.arrow([(256, 500), (290, 500)], "mod")
    for a, b in zip(xs[:3], xs[1:4]):
        s.arrow([(a + bw, 500), (b, 500)], "mod" if a < 600 else "ok")
    s.box(290, 625, 290, 115, "OptiTrack mocap", ["flying today", "new job: ground-truth scorer"], "ok")
    s.box(702, 625, 260, 115, "PX4 EKF2", ["external vision input", "(one channel only)"], "ok")
    s.box(1114, 625, 386, 115, "droan_gl local planner", ["disparity-only: no LiDAR path", "CPU planner disabled (<?ignore?>)"], "warn")
    s.arrow([(580, 670), (702, 670)], "ok", "mocap_bridge", (641, 656), lsize=13)
    s.arrow([(586, 560), (586, 598), (800, 598), (800, 625)], "mod", "visual_odometry_in: unused today", (690, 590),
            dash=True, lsize=12)
    s.arrow([(330, 740), (330, 770), (1050, 770), (1050, 560)], "ok", "compare drift: the new job", (690, 762), dash=True, lsize=13)
    s.arrow([(1040, 380), (1040, 410), (1250, 410), (1250, 625)], "warn", "needs the CPU planner re-enabled\n+ a cost_map_interface plugin",
            (1262, 470), dash=True, lanchor="start", lsize=13)
    s.save(path)


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    slide_hardware(os.path.join(outdir, "slide-1-hardware.svg"))
    slide_control(os.path.join(outdir, "slide-2-control-path.svg"))
    slide_lidar(os.path.join(outdir, "slide-3-lidar.svg"))


if __name__ == "__main__":
    main(sys.argv[1])

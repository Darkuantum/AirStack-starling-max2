# Starling 2 Max — modifications: what to do

Status, open checks, and step-by-step instructions for each workstream, as of **2026-10-20**.

| Looking for… | Go to |
|---|---|
| Boards, connectors, wiring, limits | [HARDWARE.md](HARDWARE.md) |
| Why each instruction is what it is, sources | [hardware investigation report](../reports/Starling%202%20Max%20hardware%20investigation.md) |
| Shopping sheet to print for Sim Lim | [sourcing/parts-sourcing.pdf](../sourcing/parts-sourcing.pdf) |
| Companion computer research in full | [Onboard compute alternatives](../reports/Onboard%20compute%20alternatives%202026-10-20.md) |

---

## Status

| # | Workstream | Status | Waiting on | Next action |
|---|---|---|---|---|
| ① | **Cooling** | ⏳ Undecided. Cutting CPU load comes first and costs nothing | still-air thermal soak | [Stop the two unused services](#step-1--cut-the-load-free) on Starling 1, then soak |
| ② | **LED strip** | 🛒 Parts list ready; build blocked | multimeter reading of the ESC LED pad | Buy the parts; [measure the pad](#before-soldering) when the aircraft is open |
| ③ | **Propellers** | ✅ Ready to buy | — | Gemfan 7037-3 locally, or genuine MRP-D0012-1-00 |
| ④ | **LiDAR** | ❌ Does not fit this airframe | ModalAI's answer on the 750 g limit | Email ModalAI (see ④ below); otherwise it needs a different airframe |
| ⑤ | **Companion computer** | 🔍 Researched, nothing bought | the list of algorithms to run onboard; a link bench test | [Write the algorithm list](#step-1--decide-what-it-must-run), then [test the USB link](#step-2--prove-the-link-before-buying) with the laptop |

## Open checks

Do these at the next teardown. Each one unblocks a decision.

| # | Check | How | Decides |
|---|---|---|---|
| 1 | **Voltage on the ESC `➕ VAUX` LED pad** | Multimeter, aircraft powered, between `➕` and `G` | 3.3 V strip, or the 5 V backup kit |
| 2 | **Still-air temperatures, idle and loaded** | `scripts/thermal_soak.sh <label> 30` then `--load`; no fan blowing on it | Whether to fit a fan |
| 3 | **Clear arm length** | Ruler, plate edge to motor mount | 4 LEDs per arm (≈ 75 mm) or 6 (≥ 100 mm) |
| 4 | **Side photo of the board stack** | Photo | Confirms which way up the VOXL 2 and ESC sit |
| 5 | **Fan clearance on `J2`** | Fit a 25 × 25 × 7 mm dummy | Whether a fan fits at all |
| 6 | **Is the LED rail separate from the VOXL 2's 5 V?** | Continuity / inspection | How hard to cap LED current |
| 7 | Starling 1's carrier part number | Read under the glue | Only matters when ordering a spare |
| 8 | **Mounting space for a companion** | Measure the free area on the top plate and above the stack | Which companion boards physically fit |

Questions for ModalAI, in one email: the M0129's real all-up limit on a D0012 (decides ④ and the Jetson option in ⑤), and whether the 5 V AUX select can be enabled.

---

## ① Cooling

**The problem is CPU load, not airflow.** Two services you don't use burn ~1.4 cores and hold the board at 95 °C+ before any work starts. Fix the load first; a fan is an add-on for bench and pre-arm time.

### Step 1 — cut the load (free)

On **Starling 1** (Starling 2 already runs without VIO):

1. Confirm VIO is off for the mocap setup: `"en_vio": false` in `/etc/modalai/voxl-vision-hub.conf` ([CONFIG.md](CONFIG.md) §voxl-vision-hub).
2. Stop the two services and watch the temperature drop:
   ```sh
   systemctl stop voxl-qvio-server voxl-camera-server
   voxl-inspect-cpu        # temperatures and clocks
   ```
3. If nothing you need broke, make it stick: `systemctl disable voxl-qvio-server voxl-camera-server`.
   Stopping the camera server also stops the **ToF** pipes. Nothing in the mocap flight stack uses them.
4. **Never leave `voxl-portal` open in a browser during a session.** It heats the board too.

Optional: pin full clock speed with `normal_cpu_mode: performance` in `/etc/modalai/voxl-cpu-monitor.conf`. It runs hotter for the same work.

### Step 2 — measure in still air

`scripts/thermal_soak.sh <label> 30`, then again with `--load`. **No fan or desk fan blowing on it**: every 2026-10-14 reading had one, so none of them counts.

Reading the log:
- Ignore the `soc` zone. It always reads 50.0.
- A core below max clock is only throttling **if the temperature is also high**. Low clock at 44 °C is normal demand scaling.

### Step 3 — fit a fan (only if step 2 says so)

| Must match | Spec | Why |
|---|---|---|
| Size | 25 × 25 mm, ≤ 7 mm thick ("2507") | Clearance unverified, see open check 5 |
| Voltage | **5 V** | Most 25 mm fans are 12 V |
| Wires | **2 only** | `J2` switches the ground side. 3- and 4-wire fans stutter or won't start |
| Current | ≤ 150 mA running | `J2` return is limited to ~400 mA including inrush |
| Plug | JST SH 1.0 2-pin (SHR-02V-S) | Most fans ship with bare leads or JST PH 2.0: re-terminate |
| Bearing | ball, not sleeve | Vibration |

Known-good part: **Sunon MC25060V1-000U-A99** (ModalAI's own choice for VOXL 2).

- **`J2` only.** `J19` shares its 5 V with GNSS and the RC receiver; the ESC pads are 16.8 V.
- Aim the air at the **memory side** of the board. No bare heatsink: without airflow it just stores heat.
- Mount on soft standoffs on the frame, not on the board.
- **Control:**
  - Starling 1 has `"fan_mode": "auto"` in `voxl-cpu-monitor.conf`; try that first.
  - Starling 2's newer SDK has no fan setting; how to drive it there is not worked out.
- **After fitting:** compare PX4 vibration metrics (`VIBE`) fan-on vs fan-off on identical hovers before trusting it.

---

## ② LED strip

**Design:** 16 pixels on one data line, 4 per arm, driven from the ESC's LED pads. PX4 forwards the colours to the ESC over the motor UART.

```
ESC ⬇ OUT ─▶ arm FL px 0–3 ─▶ (back to hub) ─▶ FR px 4–7 ─▶ RR px 8–11 ─▶ RL px 12–15
```

- **One chain, not four.** The ESC has a single LED output. Each pixel regenerates the signal, so every pixel is still individually addressable.
- Between arms the chain returns to the hub over **plain 3-wire returns**, not LEDs.
- The order above is a suggestion. Fix it before soldering, because the software segment map depends on it.

### Parts

Full list with photos and "do not buy" warnings: [sourcing/parts-sourcing.pdf](../sourcing/parts-sourcing.pdf).

| Part | Spec |
|---|---|
| Strip | **WS2812B or SK6812**, 5 V, **60 LED/m**, ≤ 10 mm wide (5 mm ideal), no silicone sleeve. Buy 1 m |
| Resistor | 330–470 Ω, at the ESC end of the data line |
| Capacitor | 470 µF, ≥ 6.3 V, across + / GND at the strip start |
| Wire | thin stranded, 3 colours |
| Tape | ~10 mm Kapton or clear heat-shrink |
| **Backup kit** (all three or none) | 5 V BEC ≥ 1 A · **74HCT125 / 74AHCT125** · XT30 Y-lead |

**Do not buy:** APA102 / DotStar / SK9822 / WS2801 (4-wire); WS2815 (12 V); non-addressable strip; 74HC125 / 74LS125.

### Before soldering

1. **Measure `➕ VAUX` to `G`** with the aircraft powered (open check 1). Expect 3.3 V.
2. Choose the power option:

| Option | When | Wiring |
|---|---|---|
| **A · ESC pad (default)** | Strip lights correctly at 3.3 V | `VAUX` → strip +; `G` → strip GND; `⬇ OUT` → 330 Ω → strip DIN. No extra parts. Dimmer and warmer, which is good for mocap |
| **B · 5 V backup kit** | Option A is too dim, colour-shifted, or glitches on the far arms | BEC from the 4S (XT30 Y-lead) → strip +; **grounds tied**; `⬇ OUT` → **74HCT125** → 330 Ω → DIN. Leave `VAUX` unconnected |

Without the 74HCT125, option B runs the data line under-voltage: it can work on the bench and fail in flight.

### Build

1. Tack a 3-wire pigtail to the ESC's `G` / `⬇ OUT` / `➕` pads (MCU face, rear edge). Strain-relieve it; there is no connector.
2. Put the resistor at the ESC end of the data wire.
3. Cut the strip **only on the copper pads between pixels**: 4 pixels = 67 mm at 60/m.
4. Stick each run along the arm starting ~12 mm out from the plate, then **overwrap the ends with Kapton**. The adhesive alone lets go on vibrating carbon.
5. Solder the capacitor across + / GND at pixel 0.
6. Run DOUT of each arm back to the hub and on to the next arm's DIN.

### Current budget

| Case | 16 px | vs the 500–600 mA pad |
|---|---|---|
| One colour @ brightness 80/255 | ~40 mA | fine |
| Full white @ 80/255 | ~190 mA | fine |
| Full white @ 255 | ~640 mA | **over** |

**The ESC that feeds the LEDs also powers the VOXL 2.** Cap the commanded LED sum in software, not just the brightness setting, so no ground command can brown out the flight computer.

### Software

1. Install the onboard daemon: `scripts/voxl_push_led.sh drone_N <DRONE_IP>` from the `svg_ground_control` package ([DRONE_SETUP.md](DRONE_SETUP.md) §8b). It is not installed on either aircraft yet. Use `LED_EXTRA_ARGS="--rgb"` for an RGB strip.
2. Set the pixel count to 16. The daemon is configured for 11 and caps at 32.
3. **Code change needed for per-arm colours.** The daemon's UDP protocol carries one colour for the whole strip. Add a `segments` field or a per-pixel array in both `svg_led_daemon.py` and `led_controller.py`, plus an arm → pixel-range map. The packet builder already takes per-pixel data.
4. Decide what the arms mean (heading, drone identity, CBF push direction): that decides whether the map is body-fixed or world-fixed.

### Check under mocap

Cycle the strip off / red / green / blue / white while watching Motive's camera view. White pixels may show up as ghost markers. If they do, use saturated colours and keep pixels off the marker plane.

---

## ③ Propellers

| | Part | Price |
|---|---|---|
| Genuine | ModalAI **MRP-D0012-1-00**, set of 4 | US$29.99 |
| Local equivalent | **Gemfan 7037-3**: 7 in, 3.7 pitch, 3 blades, M5 bore, 8.7 g (OddityRC, or Hobby Square at Sim Lim Square) | ~US$3.50 per prop |

- Same prop on both aircraft.
- **Never go up in pitch.** The motors are deliberately small for 7 in props; a high-pitch "freestyle" prop is the easiest way to burn a motor or the ESC.
- Keep one genuine set as the known-good reference.
- First flight after any prop change: log `VIBE` and `estimator_innovations`. With mocap feeding the EKF, a vibration problem shows up there first, not as position drift.
- Keep spares in stock: a replacement airframe is a 60-business-day order.

---

## ④ LiDAR (deferred)

**Does not fit.** The ESC's < 750 g rating leaves ~184 g; a Livox Mid-360 alone is 265 g, and the lighter LiDARs (Hesai JT16, Unitree L1) are still over. Both aircraft's `J3`/`J5` are also taken, so there's no room for the Ethernet add-on.

1. Ask ModalAI whether the M0129 is really limited to 750 g on a D0012.
2. If it is, onboard LiDAR SLAM needs a different airframe: [Onboard compute alternatives](../reports/Onboard%20compute%20alternatives%202026-10-20.md) §5.
3. The software side (driver, FAST-LIO2, the two injection points, validation against mocap) is in the [investigation report](../reports/Starling%202%20Max%20hardware%20investigation.md#lidar-research-deferred).

---

## ⑤ Companion computer

**Goal:** run heavier algorithms onboard. **A Jetson can't replace the VOXL 2**: PX4 runs inside the VOXL 2's chip, so a companion rides *alongside* it. Full research, sources and prices: [Onboard compute alternatives](../reports/Onboard%20compute%20alternatives%202026-10-20.md).

**The constraint is mass, not compute.** The ESC is rated for < 750 g all-up:

| | Mass | Running total |
|---|---|---|
| Stock aircraft | 566 g | 566 g |
| LED strip + fan (①②) | ~15 g | ~581 g |
| **Left for a companion** (board, carrier, cooling, BEC, mount, cables) | | **~170 g** |

### Step 0 — reclaim the VOXL 2 first (free)

Do [① step 1](#step-1--cut-the-load-free): stopping the camera and VIO services frees ~1.4 CPU cores. The VOXL 2's CPU is already roughly an Orin Nano's. Measured on this chip: an MPC controller at 150 Hz, and LiDAR-inertial odometry at ~78 ms per frame. Re-check whether you still need a companion afterwards.

### Step 1 — decide what it must run

| Algorithm class | Where it runs | Companion needed? |
|---|---|---|
| MPC, CBF, planners, estimators | VOXL 2 (Humble in Docker if Foxy blocks you) | No |
| Same, but native ROS 2 Humble/Jazzy or more CPU | **Pi CM5** on a small carrier | Light |
| Small neural nets (MobileNet-SSD, YOLOv5n) | VOXL 2 GPU, `voxl-tflite-server` | No |
| Mid-size neural nets (~20–26 TOPS) | **Pi 5 + Hailo AI HAT+** | Light |
| Large neural nets, CUDA / TensorRT | Jetson Orin | **Over the mass limit** unless ModalAI clears the ESC |
| LiDAR SLAM | — | Different airframe (④) |

### Step 2 — prove the link before buying

`J3` and `J5` are taken on both aircraft, so the Ethernet add-on is out. Bench-test the link first, with the laptop standing in for the companion:

| Link | Starling 1 | Starling 2 | Notes |
|---|---|---|---|
| **USB networking (NCM) over `J9`** | ✓ | ✓ | ModalAI staff recipe: add `ncm.0` to `/sbin/usb/compositions/901D`; the VOXL 2 becomes `usb0` at 192.168.7.2. Only proven with a Linux PC as host; it shares the port with ADB |
| USB-Ethernet adapter on the carrier's free **`J11`** (USB 3) | ✓ | — | Best wired option on Starling 1 |
| Both on the lab WiFi | ✓ | ✓ | No hardware; adds airtime and jitter. Fine for perception outputs, not tight loops |
| UART MAVLink | ✓ | ✓ | Setpoints only; too slow for ROS 2 topics |

Run the same ROS 2 traffic the companion would, Foxy on the VOXL 2 against Humble on the laptop, and check it actually arrives.

### Step 3 — choose the board

| Board | Compute | Installed mass | Power | Price (USD) | Fits? |
|---|---|---|---|---|---|
| **Pi CM5 + ARK Just A Pi** | 4 × A76, no NPU | ~40–50 g | ~3–9 W | ~$475 | ✓ (Ethernet is 10/100 only) |
| **Pi 5 + AI HAT+** | 4 × A76 + 26 TOPS | ~80–90 g | ~9–16 W | ~$285 | ✓ (Hailo ROS 2 integration is manual) |
| Khadas Edge2 (RK3588S) | 8 cores + 6 TOPS | ~35–45 g | ~1–10 W | ~$200–370 | ✓ (USB-C power, no RJ45) |
| Jetson Orin Nano / NX + light carrier | 67–157 TOPS, CUDA | ~170–200 g | 7–25 W+ | ~$1,100–1,700 | ✗ at or over 750 g |

Estimated flight time: ~33 min at +50 g, ~30 min at +80 g, ~23 min for a Jetson (stock ~40 min). These are calculated from published figures, not measured.

### Step 4 — power and mount

1. **Power from the battery** through its own 5 V BEC (5 A; the Matek BEC12S-PRO is 5 g) on an XT30 Y-lead. **Never** from the ESC's 5 V output (it feeds the VOXL 2) or a VOXL 5 V connector (~1 A).
2. Mount near the centre of mass, stiffly, with its own cooling airflow.
3. Weigh the aircraft complete: stay under 750 g.

### Step 5 — software

- Run **ROS 2 Humble** on the companion (Ubuntu 22.04 / JetPack 6.2), not Jazzy: talking to Foxy across distros is unofficial, and Jazzy adds risk.
- Use the same RMW and domain on both sides, or keep the VOXL 2 ↔ companion boundary to MAVLink or plain UDP, as the LED daemon does.

---

## Ordering from ModalAI

- Order **by part number from a direct link**. Store search mixes up the Starling 2 Max, Starling 2 and the older Starling.
- **Each order ships the selected part only**: consolidate, or pay freight per part.
- Ships from San Diego in USD, ~10 business days for parts, 60 for an airframe. No Asia-Pacific distributor.
- Export class EAR99: an ordinary shipment to a civil lab.
- 9 % GST on essentially every import into Singapore.

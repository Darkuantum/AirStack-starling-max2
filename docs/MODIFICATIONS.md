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
| ① | **Cooling** | ⏳ A fan is needed (services stay on). Plan: 3010 square fan in a shroud at the stack end | gap count; still-air soak | Buy the fans; print the shroud; run the [fan test](#step-3--fit-a-fan) |
| ② | **LED strip** | 🛒 Parts list ready. Plan: scenario B (own 5 V buck + 74HCT125; fan on the same buck) | — | Buy the parts; build per [scenario B](#power-and-data-scenario-b-chosen-2026-10-22) |
| ③ | **Propellers** | ✅ Ready to buy | — | Gemfan 7037-3 locally, or genuine MRP-D0012-1-00 |
| ④ | **LiDAR** | ❌ Does not fit this airframe | ModalAI's answer on the 750 g limit | Email ModalAI (see ④ below); otherwise it needs a different airframe |
| ⑤ | **Companion computer** | 🔍 Researched, nothing bought | the list of algorithms to run onboard; a link bench test | [Write the algorithm list](#step-1--decide-what-it-must-run), then [test the USB link](#step-2--prove-the-link-before-buying) with the laptop |

## Open checks

Do these at the next teardown. Each one unblocks a decision.

| # | Check | How | Decides |
|---|---|---|---|
| 1 | ~~Voltage on the ESC `➕ VAUX` LED pad~~ | — | **No longer needed:** scenario B doesn't use the 3.3 V pad |
| 2 | **Still-air temperatures, idle and loaded**, all services running | `scripts/thermal_soak.sh <label> 30` then `--load`; no fan blowing on it | The no-fan baseline the fan test compares against |
| 3 | **Clear arm length** | Ruler, plate edge to motor mount | 4 LEDs per arm (≈ 75 mm) or 6 (≥ 100 mm) |
| 4 | **Side photo of the board stack** | Photo | Confirms which way up the VOXL 2 and ESC sit |
| 5 | **How many ~2 mm gaps one end of the stack exposes**, and room for a 30 mm fan + shroud there | Look end-on at the stack; calipers | Shrouded 3010 fan (2+ gaps) or blower (1 gap) |
| 6 | **Is the LED rail separate from the VOXL 2's 5 V?** | Continuity / inspection | How hard to cap LED current |
| 7 | Starling 1's carrier part number | Read under the glue | Only matters when ordering a spare |
| 8 | **Mounting space for a companion** | Measure the free area on the top plate and above the stack | Which companion boards physically fit |
| 9 | **Motor positions** | QGC → Parameters: `CA_ROTOR0–3_PX/PY` | Confirms the motor layout in HARDWARE.md (currently PX4's standard Quad X, assumed). Not urgent |

Questions for ModalAI, in one email: the M0129's real all-up limit on a D0012 (decides ④ and the Jetson option in ⑤), and whether the 5 V AUX select can be enabled.

---

## ① Cooling

**The camera and VIO services stay enabled** (owner decision, 2026-10-22: they may be needed). With them running, Starling 1 sat at **95 °C before any extra load**. There's no prop wash on the bench or before arming, so **plan on a fan**. In flight, prop wash does most of the work.

### Step 1 — keep the heat down without disabling anything (free)

1. **Keep `"en_vio": false`** in `/etc/modalai/voxl-vision-hub.conf` ([CONFIG.md](CONFIG.md) §voxl-vision-hub). This is a **flight-safety** setting so EKF2 flies on mocap. It stops VIO from feeding PX4; it doesn't stop the service.
2. **Never leave `voxl-portal` open in a browser during a session.** It loads the board and heats it.
3. Watch temperatures and clocks with `voxl-inspect-cpu`.
4. Leave the CPU governor on its default. `normal_cpu_mode: performance` in `/etc/modalai/voxl-cpu-monitor.conf` pins full clocks and runs hotter.

If heat ever becomes the blocker, the camera server's own config can lower frame rates or turn off individual cameras you aren't using, without disabling the service. That's an option for later, not a plan.

### Step 2 — measure in still air

`scripts/thermal_soak.sh <label> 30`, then again with `--load`, **with all services running as you'd fly**. **No fan or desk fan blowing on it**: every 2026-10-14 reading had one, so none of them counts.

Reading the log:
- Ignore the `soc` zone. It always reads 50.0.
- A core below max clock is only throttling **if the temperature is also high**. Low clock at 44 °C is normal demand scaling.

### Step 3 — fit a fan

The boards are stacked with **~2 mm gaps** (owner, 2026-10-22), so air must be pushed **in from the side, through the gaps**. It can't blow onto a board face.

**Shrouded fan (planned): a 3010 square fan in a 3D-printed shroud at one end of the stack.** A partner university runs this on their Starlings. The shroud seals the fan against the stack end, so all its air goes through the gaps. The 36 mm-wide stack end suits a 30 mm fan.
**Blower (backup): a 3010 blower** aimed into the gaps. It holds up better if the shroud can only feed one gap.

Modelled airflow at 2 mm gaps (straight-line fan curves; gaps as parallel-plate channels; details in the [investigation report](../reports/Starling%202%20Max%20hardware%20investigation.md#fan-airflow-model)):

| Gaps the shroud feeds | 3010 axial (Sunon MF30100V1) | 3006 axial | 4 mm blower |
|---|---|---|---|
| 1 | 4.4 W per 10 °C ⚠️ near stall | 4.0 W | 3.1 W |
| 2 | **8.1 W per 10 °C** | 7.2 W | 3.7 W |
| 3 | **11.0 W per 10 °C** | 9.9 W | 3.9 W |

The VOXL 2 draws up to ~7 W, so the shrouded fan carries the full load **if the shroud reaches two or more gaps**. With only one gap, try the blower.

| Must match | Spec | Why |
|---|---|---|
| Size · type | **30 × 30 × 10 mm ("3010") square fan**; backup a 3010 blower | Thicker = more pressure into the gaps |
| Voltage | **5 V** | It runs from the LED buck module's 5 V (scenario B). Most small fans are 12 V |
| Wires | **2 only** | Simple +/− on the buck output; 3- and 4-wire fans add tacho/PWM wires with nothing to connect to |
| Current | ≤ 150 mA running | Leaves the buck plenty of margin for the LEDs |
| Plug | none needed: **wired to the LED buck module**, always on (scenario B) | Fans ship with bare leads, JST PH or XH: cut the plug off, solder to the buck output, heat-shrink each joint |
| Bearing | ball or fluid ("FDB / hydraulic"), not plain sleeve | Vibration |

Reference part: **Sunon MF30100V1-1000U-A99** (5.5 CFM, 49.8 Pa, 120 mA). At Sim Lim Tower, buy any 5 V 2-wire 3010 that matches; see [sourcing/parts-sourcing.pdf](../sourcing/parts-sourcing.pdf).

**Build:**
1. Count how many gaps one end of the stack exposes (open check 5): that picks the shrouded fan or the blower.
2. Print a shroud that seals the fan's face to the stack end. Leave the **opposite end open** so the air can leave.
3. Mount the fan on the frame through the shroud with soft standoffs, not on a board.

**Test it before committing (about 20 minutes per fan):**
1. All services running, as you'd fly. Run `scripts/thermal_soak.sh <label> 20 --load` in still air, no fan: the worst case.
2. Repeat with the fan in its shroud.
3. **Pass:** under ~85 °C at full 8-core load (margin below the 90 °C warning and ~95 °C throttle), and under ~60 °C at normal load.
4. If it fails, try the blower, or a fan at each end, before anything bigger.

- **Power: the LED buck module's 5 V, always on** ([scenario B](#power-and-data-scenario-b-chosen-2026-10-22)). Not `J19` (shares its 5 V with GNSS and the RC receiver) and never the ESC battery pads (16.8 V). `J2` stays empty.
- No bare heatsink: without airflow it just stores heat.
- **No speed control:** the fan runs at constant speed whenever the battery is in. Starling 1's `fan_mode: auto` would need it on `J2` instead; not used.
- **After fitting:** compare PX4 vibration metrics (`VIBE`) fan-on vs fan-off on identical hovers before trusting it.

---

## ② LED strip

**Design:** 16 pixels on one data line, 4 per arm, driven from the ESC's LED pads. PX4 forwards the colours to the ESC over the motor UART.

```
pads at rear-left:  ESC ⬇ OUT ─▶ M2 ─▶ M3 ─▶ M1 ─▶ M4   (clockwise from above)
pads at rear-right: ESC ⬇ OUT ─▶ M4 ─▶ M1 ─▶ M3 ─▶ M2   (counter-clockwise)
                    4 pixels per arm: 0–3, 4–7, 8–11, 12–15 in wiring order
```

- **One chain, not four.** The ESC has a single LED output. Each pixel regenerates the signal, so every pixel is still individually addressable.
- Between arms the chain returns to the hub over **plain 3-wire returns**, not LEDs.
- **Ring order, starting at the arm nearest the LED pads, going round away from the rear edge.** Each jump is between neighbouring arms, and the crowded rear edge (`J4`/`J9` cables, GNSS mast, fan shroud) is skipped.
- **Where the pads are:** on the ESC's underside, directly behind the VREG OUT pads that feed the VOXL 2 (from ModalAI's photos, ±1–2 mm). That puts them at the rear-left. The owner first placed them at the rear-right; either way, the rule above picks the order.
- Arms are still named by motor number. **Fill in the software's 4-entry segment table after wiring**, in the order actually wired.
- ⏳ Motor positions assume PX4's standard Quad X layout; confirm them from the `CA_ROTOR*` parameters (open check 9).

### Parts

Full list with photos and "do not buy" warnings: [sourcing/parts-sourcing.pdf](../sourcing/parts-sourcing.pdf).

| Part | Spec |
|---|---|
| Strip | **WS2812B or SK6812**, 5 V, **60 LED/m**, ≤ 10 mm wide (5 mm ideal), no silicone sleeve. Buy 1 m |
| Resistor | 330–470 Ω, at the ESC end of the data line |
| Capacitor | 470 µF, ≥ 6.3 V, across + / GND at the strip start |
| Wire | **26 AWG silicone-insulated stranded**, 3 colours, for LED power, data, returns and the buck input. Not PVC, not solid-core. The fan keeps the pigtail's 28 AWG |
| Tape / sleeving | ~10 mm Kapton; small heat-shrink for joints; **15–20 mm clear heat-shrink** to insulate the buck module and chip |
| **Buck module** | MP1584 (preferred) or Mini-360, set to 5.0 V. Powers the strip and the fan |
| **Level shifter** | **74HCT125** (DIP-14) + a **100 nF** ceramic capacitor; small perfboard scrap |
| **Connectors** | pre-crimped pairs: **JST-PH 2.0 mm 4-pin** (ESC ↔ driver), **JST-SM 3-pin** (driver ↔ strips), **JST-PH 2-pin** (fan) |

**Do not buy:** APA102 / DotStar / SK9822 / WS2801 (4-wire); WS2815 (12 V); non-addressable strip; 74HC125 / 74LS125.

### Before soldering

1. Set the buck module to **5.0 V** with a multimeter, powered from a bench supply or the battery, **before** connecting the strip, fan or chip.
2. Check continuity: no short between the buck output's + and − once everything is wired.

### Power and data: scenario B (chosen 2026-10-22)

The **LED strip and the fan both run from their own 5 V buck module** off the battery, and the data line always goes through a **74HCT125**. Nothing depends on the strip's chip version, finding a JST SH plug, or the 3.3 V pad. A short in the LED wiring only collapses the buck module, never the flight computer's supply. (Scenarios A and C were considered; see the [investigation report](../reports/Starling%202%20Max%20hardware%20investigation.md#led-supply-voltage).)

```
ESC battery pads (12–16.8 V) ──▶ MP1584 buck, set to 5.0 V ──┬──▶ LED strip +5 V  (470 µF across + / GND at the strip)
                                                              ├──▶ fan red (+)
                                                              └──▶ 74HCT125 pin 14 (VCC), 100 nF to pin 7
ESC ⬇ OUT ──▶ 74HCT125 pin 2 (1A) │ pin 1 (1OE) → GND │ pin 3 (1Y) ──▶ 330 Ω ──▶ strip DIN
ESC G pad ─── common ground: buck GND, chip pin 7, strip GND, fan black
Unused channels: pins 4, 10, 13 (OE) → 5 V   ·   pins 5, 9, 12 (inputs) → GND
VAUX: not connected

Disconnects (so nothing needs desoldering to take parts off):
  ESC pads ─[JST-PH 4-pin: batt +, GND, data, spare]─ LED driver (buck + 74HCT125)
  LED driver ─[JST-SM 3-pin: 5 V, data, GND]─ strip harness (the 4-arm ring)
  buck 5 V ─[JST-PH 2-pin]─ fan
```

- **Buck module:** MP1584 preferred (~3 A rated); a Mini-360 also works. Worst-case load is ~0.8 A: full-white LEDs plus the fan.
- **Fan:** always on, constant speed (good for vibration filtering). Starling 1 loses `fan_mode: auto`; Starling 2 has no fan control anyway.
- **Unused chip inputs must be tied** as shown: floating logic inputs can oscillate and draw current.

**Mounting:**
1. **Insulate everything: carbon fibre conducts.** Clear heat-shrink over the buck module and the chip assembly, or a Kapton wrap.
2. Mount near the ESC's LED pads, at the **rear-left arm root**: on the underside of the centre plate, or on top of the arm beside the motor wires. That stays clear of the battery packs (sides), the camera (front), and the `J4`/`J9` cables and fan shroud (rear end).
3. Put the chip, 100 nF capacitor and 330 Ω resistor on a scrap of perfboard (or glue the chip upside down and wire it directly). Fix with foam tape plus a zip tie.
4. Keep the `⬇ OUT` → chip wire **under 5 cm**; twist the buck module's input pair.
5. **Disconnects** at three points only (ESC ↔ driver, driver ↔ strips, fan ↔ buck). The runs between arms stay soldered. Mark polarity on each pair; after mating, secure with Kapton or a zip tie (a dab of hot glue on the JST-PH ones).

**After building:** run the LEDs at their capped maximum with the fan spinning, and confirm the VOXL 2 doesn't reboot or throttle. Keep the **software current cap** on the LEDs.

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
- Take the printed size gauge to the shop (`sourcing/print/prop-gauge-7037.stl`, see `sourcing/README.md`). Test-fit its M5 hub on a motor shaft first.
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

### Step 0 — measure the VOXL 2's spare capacity

The camera and VIO services stay enabled, so ~1.4 of the 8 cores are already in use. Run `top` (or `voxl-inspect-cpu`) during a normal session to see what's left. The VOXL 2's CPU is roughly an Orin Nano's, and this chip has been shown running an MPC controller at 150 Hz and LiDAR-inertial odometry at ~78 ms per frame. If your algorithm fits in what's left, you may not need a companion.

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

1. **Power from the battery** through its own 5 V regulator rated ≥ 5 A (a buck module, or an FPV BEC such as the 5 g Matek BEC12S-PRO), from the ESC battery pads or an XT30 Y-lead. **Never** from the ESC's 5 V output (it feeds the VOXL 2) or a VOXL 5 V connector (~1 A).
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

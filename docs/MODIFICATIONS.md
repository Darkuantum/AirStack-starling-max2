# Starling 2 Max — modifications: what to do

Status, open checks, and step-by-step instructions for each workstream, as of **2026-10-22**.

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
| ① | **Cooling** | ⏳ A fan is needed (services stay on). [Phase 1](#phases): 5 V 3010 fan on `J2`, in a shroud at the stack end | gap count; still-air soak | Buy the phase 1 parts; print the shroud; run the [fan test](#step-3--fit-a-fan) |
| ② | **LED strip** | 🛒 [Phase 1](#phases): strip on the ESC's 3.3 V pad, data direct | VAUX voltage (open check 1) | Buy the phase 1 parts; build per [phase 1](#phase-1-power-and-data-scenario-a) |
| ③ | **Propellers** | ✅ Ready to buy | — | Gemfan 7037-3 locally, or genuine MRP-D0012-1-00 |
| ④ | **LiDAR** | ❌ Does not fit this airframe | ModalAI's answer on the 750 g limit | Email ModalAI (see ④ below); otherwise it needs a different airframe |
| ⑤ | **Companion computer** | 🔍 Researched, nothing bought | the list of algorithms to run onboard; a link bench test | [Write the algorithm list](#step-1--decide-what-it-must-run), then [test the USB link](#step-2--prove-the-link-before-buying) with the laptop |

## Open checks

Do these at the next teardown. Each one unblocks a decision.

| # | Check | How | Decides |
|---|---|---|---|
| 1 | **Voltage on the ESC `➕ VAUX` LED pad**, idle and with the strip lit | Multimeter, battery in, props off | Phase 1 LED supply: 3.3 V expected. If it sags well below ~3.0 V with the strip lit, go to phase 2 |
| 2 | **Still-air temperatures, idle and loaded**, all services running | `scripts/thermal_soak.sh <label> 30` then `--load`; no fan blowing on it | The no-fan baseline the fan test compares against |
| 3 | **Clear arm length** | Ruler, plate edge to motor mount | 4 LEDs per arm (≈ 75 mm) or 6 (≥ 100 mm) |
| 4 | **Side photo of the board stack** | Photo | Confirms which way up the VOXL 2 and ESC sit |
| 5 | **How many ~2 mm gaps one end of the stack exposes**, and room for a 30 mm fan + shroud there | Look end-on at the stack; calipers | Shrouded 3010 fan (2+ gaps) or blower (1 gap) |
| 6 | **Is the LED rail separate from the VOXL 2's 5 V?** | Continuity / inspection | How hard to cap LED current |
| 7 | Starling 1's carrier part number | Read under the glue | Only matters when ordering a spare |
| 8 | **Mounting space for a companion** | Measure the free area on the top plate and above the stack | Which companion boards physically fit |
| 9 | **Motor positions** | QGC → Parameters: `CA_ROTOR0–3_PX/PY` | Confirms the motor layout in HARDWARE.md (currently PX4's standard Quad X, assumed). Not urgent |
| 10 | **Does `J2` power a fan on each aircraft?** | Plug the fan in, power up | Phase 1 fan. Starling 2's SDK has no fan control, so its `J2` switch state is unknown. If it won't spin, go to phase 2 |

Questions for ModalAI, in one email: the M0129's real all-up limit on a D0012 (decides ④ and the Jetson option in ⑤), whether the 5 V AUX select can be enabled (would put the phase 1 strip in spec), and whether Starling 2's `J2` is switched on by default.

---

## Phases

**Start with the fewest parts; step up only if a test fails** (owner's senior colleague, 2026-10-22). Buy phase 1 now. Phase 2 parts are on the [shopping sheet](../sourcing/parts-sourcing.pdf) but marked "don't buy yet". The LED and the fan step up **independently**.

| Phase | LED strip (②) | Fan (①) | Parts | Step up when |
|---|---|---|---|---|
| **1 (now)** | ESC `➕ VAUX` 3.3 V pad; data straight from `⬇ OUT` through 330 Ω ([scenario A](#phase-1-power-and-data-scenario-a)) | 5 V 3010 on VOXL 2 `J2`, JST SH plug, 100 nF across the leads | strip, fan, JST SH plug, passives, wire, JST-SM 3-pin | **LED:** flicker, wrong colours, or dead pixels down the chain (check 1). **Fan:** `J2` won't run it (check 10), the VOXL 2 resets or logs errors with the fan running, or `VIBE`/IMU noise rises |
| 2 (only if needed) | own 5 V buck + 74HCT125 on the peripheral power bus ([scenario B](#phase-2-power-and-data-scenario-b)) | the 5 V fan moves to that buck, **or** a 12 V / 24 V 3010 fan runs straight off the battery through the bus with a 0.2 A PTC | buck, 74HCT125, XT30 bus, JST-PH, PTCs, fan alternatives | — |
| 3 | — | — | companion computer on bus branch 2 (⑤) | — |

**Phase 1 risk, accepted:** both phase-1 loads hang off the flight computer's supplies. The 3.3 V pad is below every LED chip's rating (they may dim or glitch), and `J2`'s 5 V is the VOXL 2's own rail, so fan motor noise lands on it. The tests below are there to catch both.

**12 V fans on the raw battery:** a 4S pack runs 12–16.8 V, so a full pack is **40 % over** a plain 12 V fan's rating. Buy one whose datasheet range reaches ~17 V, or a **24 V** fan that starts at ≤ 12 V (in spec across the whole range, just slower). Fuse it with a PTC rated for **≥ 30 V** (the MF-R series is 60 V).

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
| Voltage | **5 V** | Phase 1 runs it from VOXL 2 `J2`. Most small fans are 12 V (phase 2 option, see [Phases](#phases)) |
| Wires | **2 only** | `J2` switches the ground; 3- and 4-wire fans add tacho/PWM wires with nothing to connect to |
| Current | ≤ 150 mA running | `J2` is limited to ~400 mA, including start-up |
| Plug | **JST SH 1.0 mm 2-pin** (housing SHR-02V-S), pre-crimped pigtail | Fans ship with bare leads, JST PH or XH: cut the plug off, solder to the pigtail (red → pin 1, +5 V), heat-shrink each joint |
| Noise | **100 nF** ceramic across the fan leads, at the fan | Keeps motor noise off the VOXL 2's 5 V. **No large capacitor:** `J2` switches the fan's ground, and a big one would surge through that switch |
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

- **Power, phase 1: VOXL 2 `J2`.** Not `J19` (shares its 5 V with GNSS and the RC receiver) and never the ESC battery pads (16.8 V) for a 5 V fan.
- **Speed control:** Starling 1's `fan_mode: auto` drives `J2` thermostatically, so the fan may sit off when the board is cool. Starling 2's SDK has no fan control; whether its `J2` is on by default is open check 10. For the test, Starling 1 can use `fan_mode: max`.
- **Noise check (phase 1):** with the fan running, watch for VOXL 2 resets, `dmesg` errors, and compare PX4 vibration/IMU noise (`VIBE`) fan-on vs fan-off on identical hovers. Any of those failing → phase 2.
- **Phase 2 power:** the LED buck module's 5 V (always on), or a 12 V / 24 V fan straight off the peripheral bus with a 0.2 A PTC ([Phases](#phases)).
- No bare heatsink: without airflow it just stores heat.

---

## ② LED strip

**Design:** 16 pixels on one data line, 4 per arm, driven from the ESC's LED pads. PX4 forwards the colours to the ESC over the motor UART. Phase 1 powers it from the pads' own 3.3 V; phase 2 (only if that fails) gives it a 5 V buck and a level shifter ([Phases](#phases)).

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

| Phase | Part | Spec |
|---|---|---|
| 1 | Strip | **WS2812B V6**, 5050 (WS2812B-B-V6), 3535 (Mini-V6) or 2020: the only chips whose datasheets support a 3.3 V supply. **60 LED/m**, ≤ 10 mm wide (~4–5 mm), no silicone sleeve. Buy 1 m. Fallback: any WS2812B or WS2812C, below spec at 3.3 V |
| 1 | Resistor | 330–470 Ω, at the ESC end of the data line |
| 1 | Capacitor | 470 µF, ≥ 6.3 V, across + / GND at the strip start |
| 1 | Wire | **26 AWG silicone-insulated stranded**, 3 colours. Not PVC, not solid-core |
| 1 | Tape / sleeving | ~10 mm Kapton; small heat-shrink for joints |
| 1 | Connector | **JST-SM 3-pin** pre-crimped pair (ESC pigtail ↔ strip harness) |
| 2 | Buck module | MP1584 (preferred) or Mini-360, set to 5.0 V. Powers the strip and the fan |
| 2 | Level shifter | **74HCT125** (DIP-14) + a **100 nF** ceramic capacitor; small perfboard scrap; **15–20 mm clear heat-shrink** over both |
| 2 | Connectors | pre-crimped **JST-PH 2.0 mm 2-pin** pairs (ESC LED pads ↔ driver; fan) |
| 2 | Peripheral bus | **XT30** male/female pairs + **XT30 1-to-2 splitter**; **20 AWG** silicone red/black, ~10 cm (Hobby Square) |

**Do not buy:** APA102 / DotStar / SK9822 / WS2801 (4-wire); WS2815 (12 V); non-addressable strip; 74HC125 / 74LS125.

### Phase 1 power and data: scenario A

The strip runs from the ESC's own LED pads: power from `➕ VAUX` (3.3 V AUX regulator, ~500–600 mA), data straight from `⬇ OUT`. No extra regulator, no level shifter.

```
ESC ➕ VAUX (3.3 V) ──────────────────[JST-SM 3-pin]──▶ strip +   (470 µF across + / GND at the strip)
ESC ⬇ OUT ──▶ 330 Ω ─────────────────[JST-SM 3-pin]──▶ strip DIN
ESC G ───────────────────────────────[JST-SM 3-pin]──▶ strip GND
```

- **In spec only with a V6 chip** (colleague's tip, 2026-10-25): the **WS2812B-B-V6** (5050), **WS2812B-Mini-V6** (3535) and **WS2812B-2020-V6** datasheets support a 3.3 V supply. V6 can be recognised by its idle draw (≤ 1 µA per LED with all LEDs off, vs ~0.5–1 mA for older chips), and its DIN/DOUT pins are interchangeable. WorldSemi's family page is unreliable: it links wrong datasheets to some rows and claims 3.3 V for the WS2812C. The **WS2812C** is **not** rated for 3.3 V: its datasheet says 3.7–5.3 V, though the family page claims 3.3 V. Older WS2812B (3.7 V min) and SK6812/SK6805 (3.5–3.7 V) also run below spec, with blue and green dimming first. The 3.3 V data matches the 3.3 V supply (V6 reads high above 0.55 × VDD ≈ 1.8 V), so no level shifter is needed.
- **No margin below 3.3 V:** the V6 datasheet's absolute range starts at 3.3 V, so a sagging pad or long thin wires take even a V6 out of spec. Keep the supply run short and measure the far end (open check 1).
- **A short only collapses the ESC's AUX regulator,** not the VOXL 2's 5 V rail (open check 6 confirms the rails are separate).
- **Pass test:** all 16 pixels show the right colour, with no flicker, on the bench **and in a hover with motors running**, at the software brightness cap. Measure `VAUX` with the strip lit (open check 1). Wrong colours or dead pixels **further down the chain** = supply too low → phase 2.

### Phase 2 power and data: scenario B

**Only if phase 1 fails.** The **LED strip and the fan both run from their own 5 V buck module** off the battery, and the data line goes through a **74HCT125**. Nothing depends on the strip's chip version or the 3.3 V pad. A short in the LED wiring only collapses the buck module, never the flight computer's supply. (Scenario C was also considered; see the [investigation report](../reports/Starling%202%20Max%20hardware%20investigation.md#led-supply-voltage).)

**Before soldering:**
1. Set the buck module to **5.0 V** with a multimeter, powered from a bench supply or the battery, **before** connecting the strip, fan or chip.
2. Check continuity: no short between the buck output's + and − once everything is wired.

```
ESC battery pads (12–16.8 V) ── 20 AWG pigtail ──[XT30]── 1-to-2 XT30 splitter = PERIPHERAL POWER BUS
                                                              ├─ branch 1 ─▶ MP1584 buck (below)
                                                              └─ branch 2 ─▶ capped: future companion regulator (add a fuse then)

bus branch 1 ──▶ MP1584 buck, set to 5.0 V ──┬──▶ LED strip +5 V  (470 µF across + / GND at the strip)
                                                              ├──▶ fan red (+)
                                                              └──▶ 74HCT125 pin 14 (VCC), 100 nF to pin 7
ESC ⬇ OUT ──▶ 74HCT125 pin 2 (1A) │ pin 1 (1OE) → GND │ pin 3 (1Y) ──▶ 330 Ω ──▶ strip DIN
ESC G pad ─── common ground: buck GND, chip pin 7, strip GND, fan black
Unused channels: pins 4, 10, 13 (OE) → 5 V   ·   pins 5, 9, 12 (inputs) → GND
VAUX: not connected

Disconnects (so nothing needs desoldering to take parts off):
  ESC battery pads ─[XT30]─ peripheral bus splitter ─[XT30]─ LED driver power
  ESC LED pads ─[JST-PH 2-pin: data, GND]─ LED driver (74HCT125)
  LED driver ─[JST-SM 3-pin: 5 V, data, GND]─ strip harness (the 4-arm ring)
  buck 5 V ─[JST-PH 2-pin]─ fan
```

- **Peripheral power bus:** the only thing soldered to the ESC's battery pads, **once**. Every battery-powered add-on, now and later, plugs into it with its own regulator. The ESC's 5 V stays dedicated to the VOXL 2. The pigtail is **20 AWG**, sized for a future companion (~1–1.5 A at battery voltage).
- **Buck module:** MP1584 preferred (~3 A rated); a Mini-360 also works. Worst-case load is ~0.8 A: full-white LEDs plus the fan. Don't upsize it to feed a companion later: that gets its own regulator on branch 2.
- **Fan:** always on, constant speed (good for vibration filtering). Starling 1 loses `fan_mode: auto`; Starling 2 has no fan control anyway. A 12 V / 24 V fan skips the buck and takes its own fused bus branch instead.
- **Unused chip inputs must be tied** as shown: floating logic inputs can oscillate and draw current.

**Mounting (phase 2):**
1. **Insulate everything: carbon fibre conducts.** Clear heat-shrink over the buck module and the chip assembly, or a Kapton wrap.
2. Mount near the ESC's LED pads, at the **rear-left arm root**: on the underside of the centre plate, or on top of the arm beside the motor wires. That stays clear of the battery packs (sides), the camera (front), and the `J4`/`J9` cables and fan shroud (rear end).
3. Put the chip, 100 nF capacitor and 330 Ω resistor on a scrap of perfboard (or glue the chip upside down and wire it directly). Fix with foam tape plus a zip tie.
4. Keep the `⬇ OUT` → chip wire **under 5 cm**; twist the buck module's input pair.
5. **Disconnects** at four points only (battery bus XT30, ESC LED pads ↔ driver, driver ↔ strips, fan ↔ buck). The runs between arms stay soldered. Mark polarity on each pair; after mating, secure with Kapton or a zip tie (a dab of hot glue on the JST-PH ones).

**Fallback, scenario C** (if you ever tap the ESC's 5 V instead of the buck): fuse the strip with a **0.5 A-hold PTC** at the current brightness cap 80/255, or **0.65 A** if the fan shares it, and a **0.2 A** PTC for the fan alone. Full sizing table for other caps: [investigation report](../reports/Starling%202%20Max%20hardware%20investigation.md#led-supply-voltage).

**After building (either phase):** run the LEDs at their capped maximum with the fan spinning, and confirm the VOXL 2 doesn't reboot or throttle. Keep the **software current cap** on the LEDs.

### Build

1. Tack a 3-wire pigtail to the ESC's `G` / `⬇ OUT` / `➕` pads (underside, behind the VREG pads) and end it in the **JST-SM 3-pin** plug. Strain-relieve it at the pads.
2. Put the resistor at the ESC end of the data wire (phase 2: after the 74HCT125).
3. Cut the strip **only on the copper pads between pixels**: 4 pixels = 67 mm at 60/m.
4. Stick each run along the arm starting ~12 mm out from the plate, then **overwrap the ends with Kapton**. The adhesive alone lets go on vibrating carbon.
5. Solder the capacitor across + / GND at pixel 0.
6. Run DOUT of each arm back to the hub and on to the next arm's DIN.

### Current budget

Phase 1 (the 3.3 V pad); at 3.3 V the real draw is somewhat lower than these 5 V figures.

| Case | 16 px | vs the 500–600 mA pad |
|---|---|---|
| One colour @ brightness 80/255 | ~40 mA | fine |
| Full white @ 80/255 | ~190 mA | fine |
| Full white @ 255 | ~640 mA | **over** |

**The ESC that feeds the LEDs also powers the VOXL 2.** Cap the commanded LED sum in software, not just the brightness setting, so no ground command can brown out the flight computer. In phase 2 the buck carries the LEDs instead, but keep the cap.

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

1. **Power from branch 2 of the peripheral power bus** (② phase 2; build the bus now if phase 2 never happened) through its own fused 5 V regulator rated ≥ 5 A (a buck module, or an FPV BEC such as the 5 g Matek BEC12S-PRO), or straight into a carrier that takes battery voltage. No new soldering on the ESC. **Never** from the ESC's 5 V output (it feeds the VOXL 2) or a VOXL 5 V connector (~1 A).
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

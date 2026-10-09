# Addressable LED strips for the Starling Max 2 (hardware, wiring, power, sourcing)

Scope note: the software side is already done and verified locally in this repo
(`AirStack/robot/ros_ws/src/svg_ground_control/scripts/svg_led_daemon.py`,
`scripts/voxl_setup_led.sh`, `test/test_led_packet.py`). These notes cover only the
hardware choice, electrical compatibility, mounting, power and Singapore sourcing.

---

## Q1. What exactly is the "LED output" on ModalAI's ESC — connector, pin, signal, logic voltage, level shifter?

### Takeaway
It is **not a connector** — on both the full-size Modal ESC and the VOXL Mini ESC the NeoPixel
output is a bare **solder test point** carrying a single-wire 3.3 V NeoPixel data signal straight
off an ESC STM32 GPIO, with **no level shifter on board**. There is a second solder pad that
supplies LED power, but on the Mini ESC that pad is documented as **3.3 V**, not 5 V — which is
the single most important electrical fact for this build.

### Cited Findings
- Full-size Modal ESC: "two independent Neopixel RGB LED outputs … up to 32 LEDs each", data pins at **3.3 V logic levels**, with a separate supply rail for the LED array — [ModalAI Modal ESC datasheet](https://docs.modalai.com/modal-esc-datasheet)
- On that board the LED outputs are **test points labelled `IO_0` and `IO_3`** in the AUX IO section, wired to ESC `ID0 PB8` and `ID3 PB8`; the AUX power output is **5.0 V, resistor-adjustable, 500 mA**, and the VAUX connector is listed as **"N/A (solder pads)"** — [ModalAI Modal ESC datasheet](https://docs.modalai.com/modal-esc-datasheet)
- VOXL **Mini** ESC (the family used on Starling-class vehicles): "**Single** Neopixel RGB LED output … up to 32 LEDs". Data is on **ESC ID0, MCU pin PB6**, 3.3 V logic, exposed as a test point marked ⬇ in the (unused) AUX UART section. A second test point marked ➕ provides **3.3 V for the LED array**. The AUX regulator is "3.3 V or 5.0 V at 500 mA, **defaulting to 3.3 V**, software-controlled", and the GPIO table shows `AUX_VREG_ADJUST (CH0 PC14)` marked **"(disabled)"** — [ModalAI VOXL Mini ESC datasheet](https://docs.modalai.com/voxl-mini-esc-datasheet/)
- ModalAI staff on the forum: "VAUX regulator is dedicated for this output and can handle **500-600 mA**. Its default output voltage is 3.3 V, and a 5.0 V option exists, but the **control feature is disabled at the moment**" — [ModalAI forum, Neopixel GPIO control on VOXL2 SPI port](https://forum.modalai.com/topic/3702/neopixel-gpio-control-on-voxl2-spi-port)
- The only true connector on the Mini ESC is **J1 (UART), BM04B-GHS-TBT** (mate GHR-04V-S); motor connections and the 3.8 V main power output are **solder pads only** — [ModalAI VOXL Mini ESC datasheet](https://docs.modalai.com/voxl-mini-esc-datasheet/)
- Starling 2 Max ESC identity: a ModalAI forum reply states "since Starling 2 Max uses a VOXL2, the ESC part number will be either **M0129-5 or M0129-65**", and that the Mini ESC "also acts as a power source for VOXL2 inside the Starling 2 Max", rated for 4S — [ModalAI forum, Starling 2 Max main voltage](https://forum.modalai.com/topic/4334/starling-2-max-main-voltage/3)
- Starling 2 Max is 4S-only: "two 2S Li-Ion battery packs, which are connected in series inside the vehicle" — [ModalAI forum, Starling 2 Max main voltage](https://forum.modalai.com/topic/4334/starling-2-max-main-voltage/3)

### Inferences
- Fitting the strip is a **soldering job on the ESC PCB**, not a plug-in. Expect to tack a 3-wire
  pigtail (DATA / +V / GND) onto the ⬇ and ➕ test points plus a ground point (`G` test point),
  then strain-relieve it. There is no documented JST option, so a connector has to be added by hand.
- The daemon's in-code comment says "its RGB_OUT pin drives the strip on **M0138**". The forum says
  the Starling 2 Max ESC is **M0129-5/-65**. These disagree; one of them is wrong or M0138 is a
  newer/variant SKU not yet in the docs. **This must be settled by reading the silkscreen on the
  actual board.**
- Because the data pin is a raw 3.3 V STM32 GPIO, the strip is also directly exposed to ESC MCU
  damage if the strip's power is back-fed into it. A series resistor (330–470 Ω) at the ESC end of
  the data line is cheap insurance and is standard NeoPixel practice.

### Gaps
- No ModalAI document gives a connector part number, pad pitch, or physical location photo for the
  NeoPixel test points on the Mini ESC. **Only physical inspection of the board (and ideally a
  multimeter reading on the ➕ pad with the vehicle powered) can confirm the actual pad voltage and
  which pad is which on their specific unit.**
- Whether the Starling 2 Max's internal harness already breaks these pads out anywhere is
  undocumented — inspect the vehicle.

---

## Q2. Which LED chipsets does the ESC LED driver support? Does the packet carry a white channel?

### Takeaway
It is a **single-wire WS2812/NeoPixel-protocol output**, so **WS2812B and SK6812 (including SK6812
RGBW) are the right families**; clocked two-wire parts like APA102/SK9822 are **not** supported.
RGBW is explicitly supported by the packet format — ModalAI staff confirm 3 bytes/LED for RGB and
4 bytes/LED for RGBW, which matches the local code exactly.

### Cited Findings
- ModalAI staff (Alex Kushleyev): the packet-builder takes "number of LEDs you are controlling, **LED type (RGB or RGBW)**, array of LED colors (**3 bytes for each LED in case of RGB, or 4 bytes per LED for RGBW**)" — [ModalAI forum, Neopixel integration with PX4](https://forum.modalai.com/topic/4724/neopixel-integration-with-px4)
- Same thread: colour channels are bytes 0–255; worked example of three LEDs at 50 % red/green/blue is `[127,0,0, 0,127,0, 0,0,127]`; the builder "will create a packet with checksum and send it to PX4, and PX4 will forward the packet to the ESC" — [ModalAI forum, Neopixel integration with PX4](https://forum.modalai.com/topic/4724/neopixel-integration-with-px4)
- Path confirmed: `voxl-send-neopixel-cmd` "creates a data packet (using the specific format for ESC) and sends it to a special process **modal-io-bridge** via mpa pipe. The bridge then publishes the data on a uORB topic, and the **voxl_esc** driver on the DSP forwards it to the ESC" — [ModalAI forum, Neopixel integration with PX4](https://forum.modalai.com/topic/4724/neopixel-integration-with-px4)
- The ModalAI docs name the output "**Neopixel** RGB LED output" on both ESC datasheets and ship a `voxl-esc-neopixel-test.py` bench script — [Modal ESC datasheet](https://docs.modalai.com/modal-esc-datasheet), [VOXL Mini ESC datasheet](https://docs.modalai.com/voxl-mini-esc-datasheet/)
- Local ground truth (this repo, `svg_led_daemon.py`): `ESC_PACKET_TYPE_LED_RGB_ARRAY_CMD = 25`, `ESC_PACKET_TYPE_LED_RGBW_ARRAY_CMD = 26`, packet `[0xAF, len, type, esc_id, <3n or 4n bytes>, crc16-LE]`, CRC-16/MODBUS.
- The published ModalAI docs for both ESCs describe the output only as **RGB**; RGBW is not mentioned in either datasheet — [Modal ESC datasheet](https://docs.modalai.com/modal-esc-datasheet), [VOXL Mini ESC datasheet](https://docs.modalai.com/voxl-mini-esc-datasheet/) — contradicted (in the user's favour) by the staff forum post above and by their own ESC fw 39.21 working on the bench.
- SK6812 vs WS2812B are protocol-compatible in practice: Cytron's own strip listing says the product "**may ship with either WS2812B or SK6812-based LEDs**. They are the same brightness, color, and protocol" — [Cytron SG, SK6812 60 LED Silicon Strip 1 m](https://sg.cytron.io/p-sk6812-60-led-silicon-strip-1m)
- SK6812 RGBW adds a fourth channel: "Instead of 3 channels of color (24 bit), it takes a fourth channel for white, for 32 bits per LED" — [Adafruit SK6812 RGBW product documentation](https://cdn-shop.adafruit.com/product-files/2824/SJ-10030-SC-6812RGBW.pdf) (via retailer summaries; see Gaps)

### Inferences
- Buy **SK6812 RGBW** if they want to keep the existing default (daemon defaults `rgbw=True`,
  `--num-leds 11`); buy **WS2812B** and add `--rgb` if they want the cheaper, far more commonly
  stocked part. Both work with the shipped software; the `--rgb` flag exists precisely for this.
- Do **not** buy APA102/DotStar/SK9822/WS2801 — those need a clock line the ESC does not provide.
- Do **not** buy WS2815 (12 V) unless they add a separate 12 V rail; it is a different voltage
  domain even though the protocol matches. (A forum user was specifically planning WS2815 and
  ModalAI steered them to the ESC output rather than solving the voltage problem — see Q6.)

### Gaps
- No ModalAI document states which chipsets were validated against the ESC firmware's bit timing.
  The ESC bit-bangs WS2812-family timing; SK6812 timing is close but not identical, so an SK6812
  RGBW strip should be **bench-tested before it is flown** (the user can already do this with their
  daemon in `--dry-run` off / strip connected on the bench).
- Whether ESC fw 39.21 specifically implements packet type 26 (RGBW) is not documented publicly —
  the user's own bench result is the best evidence available.

---

## Q3. Maximum pixel count

### Takeaway
**32 LEDs per output** is a real documented firmware/protocol limit, stated identically on both ESC
datasheets and in the ModalAI forum. Their `MAX_NEOPIXELS = 32` constant matches it; the 11 they use
is purely their own choice.

### Cited Findings
- "Two independent Neopixel RGB LED outputs are available, **up to 32 LEDs each**" — [ModalAI Modal ESC datasheet](https://docs.modalai.com/modal-esc-datasheet)
- "Single Neopixel RGB LED output is available, **up to 32 LEDs**" — [ModalAI VOXL Mini ESC datasheet](https://docs.modalai.com/voxl-mini-esc-datasheet/)
- ModalAI staff: "A single string with **up to 32 LEDs** is supported" — [ModalAI forum, Neopixel GPIO control on VOXL2 SPI port](https://forum.modalai.com/topic/3702/neopixel-gpio-control-on-voxl2-spi-port)
- Local ground truth: `MAX_NEOPIXELS = 32` with `raise ValueError('num leds should be between 1 and %d')` — `svg_led_daemon.py`.

### Inferences
- With RGBW that is 32 × 4 = 128 colour bytes + 5 framing bytes ≈ 133 bytes per packet, well inside
  a single `modal_io_bridge` write — so the 32 limit is almost certainly an ESC-side buffer, not a
  transport limit.
- 32 pixels is the practical ceiling for the whole aircraft on this path. A 4-arm ring of 8 pixels
  per arm (32) is the maximum symmetric layout. Their 11 leaves lots of headroom.
- The full-size Modal ESC's **two** outputs would allow 64, but the Mini ESC on the Starling 2 Max
  documents only one — so 32 is the number to design to.

### Gaps
- Whether exceeding 32 fails gracefully (ESC rejects the packet) or corrupts the ESC's buffer is
  undocumented. Their code already guards against it.

---

## Q4. Power: voltage, current, where to tap, brown-out risk

### Takeaway
The ESC's own LED pad is a **3.3 V / 500–600 mA** rail on the Mini ESC — too low for a 5 V strip to
reach full brightness and far too small to power a long strip, but it is **exactly the right rail
for a small strip and it solves the 3.3 V logic-level problem for free**. For 11 pixels at their
current brightness it is fine; anything beyond that should get its own BEC, with grounds tied.

### Cited Findings
- NeoPixel worst case: "each NeoPixel draws up to **60 mA** at full-brightness white"; Adafruit's rule of thumb for mixed colours and animations is "**20 mA per pixel**, about one-third of the maximum" — [Adafruit NeoPixel Überguide, Powering NeoPixels](https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels)
- Nominal supply is **5 V DC**; "Lower voltages are safe but make the LEDs dimmer. Below some threshold, the LEDs fail to light or show the wrong color." Excess voltage damages them (6 V from 4×AA is called out as too high) — [Adafruit NeoPixel Überguide, Powering NeoPixels](https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels)
- Cytron's 60 LED/m SK6812/WS2812B strip: **5 VDC, do not exceed 6 VDC, no polarity protection**, "up to 60 mA per LED at full white" — [Cytron SG, SK6812 60 LED Silicon Strip 1 m](https://sg.cytron.io/p-sk6812-60-led-silicon-strip-1m)
- A 30 LED/m SK6812 RGBW strip is quoted at **7.5 W per metre at full white (1.5 A @ 5 V)**, i.e. ~50 mA/pixel — [SuperLightingLED SK6812 RGBW strip listings](https://www.superlightingled.com/sk6812-rgbw-led-strip-c-5_120_707.html)
- Per-channel currents for one OPSCO SK6812 RGBW part: R/G/B 8 mA each, W 16.5 mA (≈40 mA/pixel full white) — [OPSCO SKC6812RGBW-BW datasheet (LCSC)](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2308161144_OPSCO-Optoelectronics-SKC6812RGBW-BW_C5181320.pdf)
- ESC AUX/LED rail: **3.3 V default on the Mini ESC, 500 mA**, 5 V option software-controlled but the adjust GPIO is "(disabled)" — [ModalAI VOXL Mini ESC datasheet](https://docs.modalai.com/voxl-mini-esc-datasheet/); staff put the capability at "**500-600 mA**" — [ModalAI forum](https://forum.modalai.com/topic/3702/neopixel-gpio-control-on-voxl2-spi-port)
- The full-size Modal ESC's AUX is **5.0 V, resistor-adjustable, 500 mA** — [ModalAI Modal ESC datasheet](https://docs.modalai.com/modal-esc-datasheet)
- The Mini ESC also exposes a **3.8 V main power output** solder pad — [ModalAI VOXL Mini ESC datasheet](https://docs.modalai.com/voxl-mini-esc-datasheet/)
- The Mini ESC "**also acts as a power source for VOXL2** inside the Starling 2 Max" — [ModalAI forum, Starling 2 Max main voltage](https://forum.modalai.com/topic/4334/starling-2-max-main-voltage/3)

### Inferences
- **Budget for their current setup (11 pixels, brightness 80/255, mostly single-colour green/red/blue):**
  roughly 11 × (80/255) × 20 mA ≈ **70 mA** typical. Even "all white at 80/255" is ~11 × 25 mA ≈
  280 mA. That fits inside the 500 mA LED rail with margin. **But a `255,255,255,255` command
  would ask for 11 × ~60–80 mA = 0.7–0.9 A and overrun the rail.** The daemon's `--brightness`
  clamp is therefore a *safety* feature, not just an aesthetic one — consider hard-capping the
  total commanded sum in software so no ground operator can brown out the rail from a ROS topic.
- **Brown-out risk is real and is the main hazard here**, precisely because the Mini ESC is also
  VOXL2's power source. Overloading an ESC-internal regulator on a board that feeds the flight
  computer is the worst place on the aircraft to put a 1 A transient. Recommendation: either keep
  the strip small and dim and feed it from the ESC LED pad, **or** power the strip from its own
  5 V BEC off the 4S main pack, with the BEC ground bonded to the ESC ground and only the data
  wire going to the ESC pad.
- **The 3.3 V LED pad is a blessing in disguise**: running an SK6812/WS2812B at 3.3–3.8 V (either
  the ➕ LED pad or the 3.8 V main-power pad) puts VIH = 0.7 × VDD at ~2.3–2.7 V, so the ESC's
  3.3 V data line is comfortably above threshold and **no level shifter is needed**. Cost: the
  strip is visibly dimmer and whites/blues skew (blue and white dice have the highest forward
  voltage). For an indoor mocap lab this is usually acceptable and is actively desirable (see Q7).
- If they do want full 5 V brightness, they need **both** a 5 V BEC **and** a level shifter
  (or a 3.3 V→5 V buffer such as a 74AHCT125) on the data line — see Q5.
- Add a **bulk capacitor (470–1000 µF, ≥6.3 V) across the strip's +V/GND at the strip end** and the
  330–470 Ω series data resistor. Both are standard NeoPixel practice from the Adafruit guide's
  best-practice section and matter more here because the supply is a small shared regulator.

### Gaps
- No source gives measured current for an **SK6812 RGBW** pixel at a specified PWM level; the
  40–60 mA/pixel figures are full-white maxima from different vendors and disagree by ~50 %.
  Measure the actual strip in-line with a meter before trusting any budget.
- Whether the Starling 2 Max's specific ESC build has the 5 V AUX option enabled in fw 39.21
  cannot be determined from docs — **measure the ➕ pad**.

---

## Q5. Logic level: will the ESC's 3.3 V data drive a 5 V strip?

### Takeaway
**Not reliably.** WS2812B/SK6812 want VIH ≥ 0.7 × VDD, i.e. ~3.5 V on a 5 V strip — above the ESC's
3.3 V output. This is the classic NeoPixel marginal-logic failure: it often *appears* to work on a
short strip at room temperature and then glitches in flight.

### Cited Findings
- "the manufacturer recommends a signal of at least **70 % of the NeoPixel supply voltage**" — for 5 V that is ~3.5 V. Remedies given: "lower the pixel supply voltage closer to the microcontroller's level (for example, a LiPo battery at about 3.7 V), or **use a logic level shifter** on the first pixel's data input" — [Adafruit NeoPixel Überguide, Powering NeoPixels](https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels)
- OPSCO SK6812 RGB datasheet: `VIH min = 0.7 × VDD`, `VIL max = 0.3 × VDD` at VDD = 5.0 V — [OPSCO SK6812 datasheet (LCSC)](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2306280930_OPSCO-Optoelectronics-SK6812RGBP8_C7423115.pdf)
- An SK6812 **RGBW**-specific spec sheet lists **VIH 3.4 V min** at VDD = 5.0 V and VIL 1.6 V max — still above 3.3 V — [Ledyi SK6812 RGBW LED specification](https://www.ledyilighting.com/wp-content/uploads/2022/02/SK6812-RGBW-LED-specification.pdf)
- ModalAI documents the ESC NeoPixel data pin as **3.3 V logic levels** with no mention of a level shifter — [Modal ESC datasheet](https://docs.modalai.com/modal-esc-datasheet), [VOXL Mini ESC datasheet](https://docs.modalai.com/voxl-mini-esc-datasheet/)

### Inferences
- Two clean options, in order of preference for this vehicle:
  1. **Run the strip at 3.3–3.8 V from the ESC's own LED/main pad.** VIH drops to 2.3–2.7 V, 3.3 V
     data is fine, no extra parts, no extra weight. Dimmer, slightly warm-shifted colour. Best fit
     for a mocap lab.
  2. **Run the strip at 5 V from a separate BEC + a 74AHCT125 / SN74LVC1T45 / TXS0108-style shifter**
     powered from that same 5 V. ~1–2 g extra, more wiring, full brightness.
- The bidirectional TXS-type shifters are weak for fast edges; a 74AHCT125 (push-pull, 5 V supply,
  TTL inputs — recognises 3.3 V as high) is the standard recommended part for NeoPixel data and is
  what Adafruit's own level-shifter guidance points at.
- A commonly-cited field hack — insert one "sacrificial" WS2812 running at 3.3 V ahead of the 5 V
  strip so its 3.3 V-referenced DOUT is re-driven — is not a documented ModalAI recommendation and
  is not reliable; prefer a real buffer.

### Gaps
- Nobody has published a test of ESC-driven 3.3 V data into a 5 V strip at the Starling's wire
  lengths. Keep the data run short (<15–20 cm) whatever they choose.

---

## Q6. Alternatives if the ESC path proves limiting

### Takeaway
**ModalAI explicitly recommends against driving NeoPixels from VOXL 2 GPIO/SPI** and points users
back to the ESC. A small dedicated MCU is the only credible alternative, and it costs ~3–8 g plus a
whole new software interface they do not currently need.

### Cited Findings
- A user asked about repurposing VOXL 2 SPI pins as GPIO for WS2815 data, noting the `gpi-mod` kernel driver means "we would not be able to access the GPIO to facilitate the neopixel driver signal in user space". ModalAI's Alex Kushleyev replied: "**i dont think you can easily use SPI on VOXL2 for Neopixel**" and pointed at the ESC NeoPixel output instead — [ModalAI forum, Neopixel GPIO control on VOXL2 SPI port](https://forum.modalai.com/topic/3702/neopixel-gpio-control-on-voxl2-spi-port)
- Same thread, for context on what VOXL 2 does expose: SPI11 on the J5 B2B connector, SPI14 on J10 External SPI; "GPIOs are exported to /sys/class/gpio by default from System Image 1.7.3 onward, with an offset of 1100" — [ModalAI forum / VOXL 2 Linux user guide](https://docs.modalai.com/voxl2-linux-user-guide/)
- Known friction even on the supported path: a user reported `voxl-esc led -l 0x001` failing under PX4 "due to the **modal_io_bridge priority**", and that the python test script cannot run while PX4 is running — [ModalAI forum, Neopixel integration with PX4](https://forum.modalai.com/topic/4724/neopixel-integration-with-px4)
- An unresolved forwarding problem exists on a different FC: "the current way will not work for forwarding the Neopixel LED packet to the FC V2" (Flight Core V2, Feb 2025) — [ModalAI forum, Flight Core V2 – VOXL ESC 4in1 Integration](https://forum.modalai.com/topic/4182/flight-core-v2-voxl-esc-4in1-integration.md). Not applicable to the Starling 2 Max (no Flight Core V2), but it shows the LED packet path is not uniformly supported across ModalAI FCs.

### Inferences
- **Why Linux userspace bit-banging fails here:** the WS2812 bit cell is ~1.25 µs with ~±150 ns
  tolerance and a >50 µs reset gap. A non-RT Linux userspace thread on a Qualcomm SoC cannot hold
  that; a scheduling hiccup mid-frame produces visible corruption or a latched wrong colour. The
  usual escapes (SPI MOSI as a 3× or 4× oversampled bit stream, or DMA+PWM as on a Pi) both need
  a dedicated, correctly-clocked peripheral exposed to userspace — which is exactly what ModalAI
  says is not easily available. This is why ModalAI put the bit-banger in the **ESC's STM32**.
- **Dedicated MCU option (RP2040 / Seeed XIAO RP2040 / ATtiny / tiny STM32):** genuinely solves
  timing — RP2040 PIO is the gold standard for WS2812 and is jitter-free. Tradeoffs: ~2–5 g board
  + ~1 g wiring, a 5 V or 3.3 V supply, a new UART/I²C/USB link to VOXL 2, a new firmware artefact
  to version and flash, and a new failure mode (MCU hangs → lights stuck on, possibly bright white).
  It also bypasses the whole packet/bridge/`voxl_esc` stack they have already debugged, including
  the `px4-qshell voxl_esc -l 0 led` mute workaround. **Not worth it unless they need >32 pixels,
  a second independent strip, or per-pixel animation faster than the ~20 Hz bridge passthrough.**
- **Recommendation: stay on the ESC path.** The 32-pixel ceiling and the 500 mA rail are the only
  two real limits, and both are generous relative to 11 pixels. The software is written, tested,
  and already works around the PX4 status-LED repaint.

### Gaps
- No source quantifies the ESC LED refresh rate achievable through `modal_io_bridge` → uORB →
  `voxl_esc`. The repo's own notes observe a **20 Hz passthrough rate** for motor commands, which
  is the likely practical cap. Not independently confirmed in ModalAI docs.
- No weight figure published for any specific RP2040 board in a drone-LED role; estimates above are
  inference, not cited.

---

## Q7. Mocap / OptiTrack interaction — does a bright strip break tracking?

### Takeaway
Visible-light RGB LEDs are not the main hazard; the hazards are (a) **IR leakage from high-power
white/warm-white dice being seen as spurious markers**, and (b) the reverse problem — the mocap
cameras' own 850 nm strobe disturbing onboard optical sensors. Keep the strip dim, prefer saturated
colours over white, and keep it off the marker plane.

### Cited Findings
- NaturalPoint/OptiTrack support guidance: other IR light sources hitting the camera can cause false detections; operators should watch the camera view for "tracking dots turning red or red blobs in the background", and a band-pass filter tuned to the marker wavelength helps — [NaturalPoint forums](https://forums.naturalpoint.com/viewtopic.php?p=87957)
- Mocap strobing disturbs onboard sensors: a PX4Flow pointed at an OptiTrack camera saw the 850 nm IR LEDs flashing at 100 Hz; position hold degraded from ~10 cm oscillation (mocap LEDs off) to ~5 m drift (LEDs on) — [PX4 discuss, PX4Flow disturbed by IR pulses of MOCAP](https://discuss.px4.io/t/px4flow-disturbed-by-ir-pulses-of-mocap/3490)
- "the rapid flashing of the motion capture cameras **cannot be disabled** in the commonly used OptiTrack motion capture system"; passive markers on other drones "show up as bright white circles" in onboard imagery, and IR filters "did not fully remove the striping" — [Virtual Omnidirectional Perception for Downwash Prediction (arXiv:2303.03898)](https://arxiv.org/pdf/2303.03898)
- Older OptiTrack cameras (e.g. S250) can be set to continuous rather than strobe lighting; newer Prime 13/17 cannot — [NaturalPoint forums](https://forums.naturalpoint.com/viewtopic.php?p=87902)
- Active-marker practice: active markers are "860 nm IR LEDs with different strobe patterns", which improves labelling and marker sensitivity — [SDU UAS Test Center motion capture lab](https://www.sdu.dk/en/forskning/sduuascenter/aboutsduuascenter/sduuastestcenter/motioncapturelab)

### Inferences
- Practical rules for this lab: keep `led_controller.brightness` at or below its current 80/255
  default; avoid full white (white dice and warm-white phosphors have the most IR tail); **do not
  mount pixels within ~3–5 cm of, or on the same plane as, the retroreflective markers**, where a
  bright pixel can wash out a marker's contrast in the camera's thresholded image.
- If after fitting they see new ghost markers in Motive, the diagnostic is to run the strip through
  off → red → green → blue → white in Motive's **grayscale/camera view** and watch for blobs. This
  distinguishes IR leakage from a genuine tracking problem.
- A side benefit of the dim 3.3 V supply option (Q4/Q5): less IR leakage, less chance of
  contaminating the volume.

### Gaps
- **No source found** that measures IR emission from WS2812B/SK6812 dice, or that documents OptiTrack
  interference from visible RGB LED strips specifically. The guidance above is inference from
  general IR-contamination advice. Treat it as a hypothesis to test in their own volume, not a
  measured fact.

---

## Q8. Physical: form factor, weight, mounting, heat

### Takeaway
A 1 m, 60 LED/m 5 V strip cut to length is the standard article; silicone-jacketed versions are
tougher but heavier. Reliable published **weight-per-metre figures were not found** — this is the
weakest-sourced part of these notes.

### Cited Findings
- Cytron's SK6812/WS2812B 60 LED/m strip is **14.5 mm wide and 4 mm thick with the silicone jacket**, 5050 package, with a **3-pin JST SM connector on each end**, separated power and ground wires, 5 VDC, no polarity protection — [Cytron SG, SK6812 60 LED Silicon Strip 1 m](https://sg.cytron.io/p-sk6812-60-led-silicon-strip-1m)
- Common densities for 5 V SK6812 RGBW are **30, 60 and 144 LEDs/m**; a 30 LED/m version has **32.2 mm pixel spacing** — [SuperLightingLED SK6812 RGBW strip range](https://www.superlightingled.com/sk6812-rgbw-led-strip-c-5_120_707.html)
- Bare (non-jacketed) strips are available on black or white PCB; a silicone-tube waterproof version is "12.5 mm width, 4 mm thick" — [SuperLightingLED SK6812 RGBW strip range](https://www.superlightingled.com/sk6812-rgbw-led-strip-c-5_120_707.html)
- A 144 LED/m SK6812 RGBW strip is listed as **12 mm wide** — [SuperLightingLED 144 LED/m SK6812 RGBWWWA](https://www.superlightingled.com/sk6812-rgbwwwa-144ledsm-dc5v-12mmwide-digital-intelligent-addressable-led-strip-lights-1m328ft-per-roll-p-2394.html)

### Inferences
- **For 11 pixels, 60 LED/m is the natural density**: 11 pixels ≈ 183 mm of strip — about one arm's
  length on a Starling-class frame, or a short bar under the body. 144/m would pack 11 pixels into
  ~76 mm (very compact, but 144/m strips have poor thermal spreading and higher current density).
  30/m spreads 11 pixels over ~354 mm, useful if they want pixels distributed around the frame.
- **Mounting:** the factory 3M adhesive backing on bare strips is unreliable on a vibrating airframe
  and on textured/curved carbon. Prefer: (a) clean the surface with IPA, (b) use the adhesive as a
  tack only, then (c) overwrap with clear heat-shrink or two small zip ties / Kapton at each end.
  On arms, run the strip along the **top** of the arm (shields it from prop wash and from landing
  impacts) and route the 3-wire pigtail inside the arm channel if one exists.
- **Avoid the landing gear** for the first fit: it takes the landing shock and the wires fatigue at
  the flex point. Body/arm mounting is more durable.
- **Heat** is a non-issue at 11 pixels and 80/255 brightness (sub-100 mA total, <0.5 W). It only
  matters at full white on a dense strip against a thermally isolated silicone jacket — which this
  build will not reach.
- **Cutting:** 5 V addressable strips cut on the marked pad boundaries between pixels; cut to 11
  and keep the arrow (data-direction) pointing **away** from the ESC. Getting the arrow backwards is
  the single most common "the strip is dead" cause.
- **Balance/CG:** keep the strip and its wiring symmetric about the CG, or at least compensate.
  A ~20 cm strip plus pigtail is small but not negligible on a Starling-class vehicle.

### Gaps
- **No reliable published weight-per-metre** for 5 V WS2812B/SK6812 strips was found in any source
  consulted (vendor pages give dimensions but not mass). Commonly quoted hobby figures are roughly
  20–35 g/m for bare 60/m strip and 50–80 g/m with a silicone jacket, but **I could not verify these
  against a primary source and they should not be reported as fact.** The user should weigh the
  strip on a kitchen scale before fitting and subtract it from payload.
- No source addresses vibration-induced solder-joint failure rates on strips fitted to multirotors.

---

## Q9. Sourcing in Singapore

### Takeaway
Cytron's Singapore site is the best first stop (S$13.21 for a 1 m 60 LED silicone strip, in stock);
Kuriosity.sg is the local hobby retailer; Sim Lim Tower shops stock the parts but at a markup. For
**SK6812 RGBW specifically** no confirmed Singapore-stocking retailer was found — RGBW will likely
have to come from Shopee/Lazada cross-border or AliExpress.

### Cited Findings
- **Cytron Singapore** (sg.cytron.io): "SK6812 60 LED Strip with Silicon Jacket – 1 m", **S$13.21** (S$11.89 at 10+, S$10.57 at 50+), **availability 20**, 5 VDC, 60 LEDs/m, 5050, 3-pin JST SM connectors both ends, 14.5 × 4 mm silicone. Listed as **RGB (24-bit), not RGBW**, and "may ship with either WS2812B or SK6812-based LEDs" — [Cytron SG](https://sg.cytron.io/p-sk6812-60-led-silicon-strip-1m)
- **Kuriosity.sg** (Singapore online hobby retailer, "fast local delivery"): "Neopixel WS2812B WS2815 LED Strip Light" **from S$8.60**, options 1 m 5 V white strip, 1 m 5 V black strip, 1 m 12 V strip; "LED Ring Light WS2812 7/8/12/16/24 LED Neopixel" **from S$4.60**. Intro text mentions 30/60/144 LED/m. **No SK6812 RGBW products listed** — [Kuriosity.sg NeoPixel collection](https://kuriosity.sg/collections/led-neopixel)
- **Sun-Light Electronics, Sim Lim Tower #03-09** (10 Jalan Besar, tel +65 6299 8803, sales@sun-light.com.sg): 1 m 120-LED WS2812B strip at **S$32.70**; WS2812B 24-bit ring at **S$15.00** — [Sun-Light product search, tag WS2812B](http://sun-light.com.sg/index.php?route=product/search&tag=WS2812B)
- **Amicus Singapore**: 5 m WS2812B, 300 LEDs, 60/m, IP65/IP67 at **SGD $68.00** (listing calls the IC "SK2812B", likely a typo — confirm before ordering) — [Amicus SG](https://amicus.com.sg/products/digital-rgb-led-weatherproof-strip-sk6812-100cm-1096662955/)
- Other Sim Lim Tower LED shops (general LED, not confirmed addressable stock): **Sunlight LED Pte Ltd** #02-46 / #02-08, tel +65 6391 9293 — [Facebook page](https://www.facebook.com/sunlightled2014/); **123 LED Lighting** #03-41, tel 8793 9683, also on Qoo10/Shopee/Carousell — [123 LED Lighting](https://123ledlighting.sg/blog/unique-sim-lim-tower-light-shop/); **Wit's Lighthouse** #03-11 and #03-40, Mon–Fri 9am–6pm — [Wit's Lighthouse](https://witslighthouse.com/); **LED Lighting Pte Ltd** #02-09, Mon–Fri 9am–6pm, Sat 9am–5pm, tel 9817 4097 — [FSL store locations](https://www.fsl.sg/shop/index.php?route=information/information&information_id=7)
- Regional/overseas SK6812 RGBW options that ship to SG: SuperLightingLED 1 m 144 LED/m RGBW from **US$16.98** (free shipping only over US$299) — [SuperLightingLED](https://www.superlightingled.com/sk6812-rgbwwwa-144ledsm-dc5v-12mmwide-digital-intelligent-addressable-led-strip-lights-1m328ft-per-roll-p-2394.html); eBay sellers ship SK6812 from Shenzhen with ~US$12.99 SpeedPAK, import duties included — [eBay listing](https://www.ebay.de/itm/296482319364)
- Solarbotics (Canada) lists SK6812 RGBW 60/m at **CAD $37.79** but it was **out of stock** — [Solarbotics](https://www.solarbotics.com/product/60560/)
- A longstanding local tip: "Sim Lim Tower has dozens of shops selling [LED strips]", plus light shops along Jalan Besar and Balestier — [MyCarForum thread](https://www.mycarforum.com/topic/2702313-where-to-buy-cheap-led-strip/) (≈7 years old; stock and tenants will have changed)

### Inferences
- **Recommended buy for this project:** one Cytron SG 1 m 60 LED/m 5 V strip at **S$13.21**, cut to
  11 pixels, run it as **RGB** with the daemon's existing `--rgb` flag. It is local, in stock, cheap,
  already has JST pigtails (less soldering at the strip end), and the silicone jacket survives
  handling. Buy two so there is a spare after the inevitable first miscut.
- **If RGBW is wanted:** no local stock found — order SK6812 RGBW from Shopee/Lazada SG sellers
  (cross-border, ~1–3 weeks) or AliExpress. Expect roughly S$15–30/m. Keep the daemon's default
  (RGBW, no `--rgb` flag) in that case.
- Sim Lim Tower is viable for same-day pickup but Sun-Light's S$32.70/m is ~2.5× Cytron's price.
  Worth it only if they need the strip today. **Phone ahead** — most Sim Lim Tower LED shops sell
  generic non-addressable 12 V RGB strip, which will not work at all.
- Also buy at the same time: 470 µF/6.3 V electrolytic, 330 Ω resistors, a 74AHCT125 (only if going
  the 5 V route), 28–30 AWG silicone wire, heat-shrink, and a 3-pin JST SM pigtail to mate the
  Cytron strip. All available at Sim Lim Tower / Cytron.

### Gaps
- **Shopee and Lazada Singapore listings could not be retrieved** by the search tools, so no
  specific local-seller SKUs or prices for SK6812 RGBW can be cited. The user should search both
  directly for "SK6812 RGBW 5V" filtered to "ships from Singapore".
- Element14 SG / RS Singapore were not reachable in search results; both are plausible stockists of
  Adafruit-branded NeoPixel parts at a premium and are worth checking directly.
- Cytron SG's Singapore shipping terms and lead time were not on the product page.
- Prices quoted are as retrieved on 2026-10-08 and several source pages carry no date.

---

## Consolidated open items that only physical inspection can settle

- **Which ESC is actually fitted** — read the silkscreen. Docs/forum say M0129-5/-65 (VOXL Mini ESC);
  the repo's own daemon comment says M0138. They cannot both be right.
- **The voltage on the ➕ LED test point** — datasheet says 3.3 V on the Mini ESC, 5.0 V on the
  full-size ESC, and the 5 V select is documented as disabled. Measure it. This single measurement
  decides whether they need a level shifter and a separate BEC, or neither.
- **Which pad is the NeoPixel data test point (⬇)** and whether it is reachable without
  disassembling the vehicle.
- **Whether the ESC's AUX/LED rail is shared with anything that feeds VOXL 2** — the Mini ESC is
  documented as VOXL2's power source, so confirm the LED rail is an independent regulator before
  loading it.
- **Measured strip weight and measured current** at their actual brightness, before first flight.

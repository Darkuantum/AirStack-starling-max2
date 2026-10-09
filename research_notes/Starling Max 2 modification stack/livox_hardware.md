# Livox LiDAR as a Physical Payload on a ModalAI Starling Max 2 — Hardware, Electrical, Mechanical

Scope note: this file covers sensor selection, weight/power budget, mounting, vibration, time sync, extrinsic calibration and the physical/electrical interface. Software (drivers, SLAM, EKF2 plumbing) is out of scope except where it forces a hardware choice.

## Sensor selection: Livox Mid-360 primary specs

### Takeaway
The Mid-360 is the only Livox unit in the family that is plausibly carryable by a Starling 2 Max: 265 g, 6.5 W, 9–27 V input, 360° x (-7°..+52°) FOV, 0.1 m minimum range, built-in ICM40609 IMU, IP67, standard 100BASE-TX Ethernet. Every other Livox listed (Mid-70 580 g, Avia 498 g, HAP ~1120 g, Mid-40 ~710 g) is roughly 2x–4x heavier and would exceed the airframe's stated 500 g payload on its own or with cabling.

### Cited Findings
- Mid-360 weight **265 g**; dimensions **65 x 65 x 60 mm** — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)
- Power **6.5 W average**; in self-heating mode (ambient -20 °C to 0 °C) **peak may reach 14 W**; input **9–27 V DC** — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)
- FOV **360° horizontal, -7° to +52° vertical** (asymmetric, biased upward) — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)
- **Minimum detection range 0.1 m**; objects at 0.1–0.2 m are detected but precision is not guaranteed — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)
- Detection range at 100 klx: **40 m @ 10% reflectivity, 70 m @ 80%** — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)
- Point rate **200,000 pts/s** (first return); **IP67** — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)
- Built-in IMU: **ICM40609** — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)
- Interface: **100BASE-TX Ethernet** (i.e. ordinary Ethernet, *not* 100BASE-T1 automotive). Time sync: **IEEE 1588-2008 (PTPv2) and GPS** — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs); the Livox wiki adds **gPTP** as a third method — [Livox wiki Mid-360](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/mid360.html)
- Operating temperature -20 °C to 55 °C — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)
- IMU default output rate reported as **200 Hz** — [OpenELAB MID-360L listing](https://openelab.io/products/livox-mid-360l-3d-lidar) (reseller, and for the MID-360L variant — see Gaps)

### Inferences
- The 0.1 m blind zone is excellent for indoor flight: there is effectively no useful-range penalty near walls, pallets or hangar structure. This is the single biggest reason to prefer the Mid-360 over the long-range Livox units, whose minimum ranges are not published and whose optics are tuned for 90–450 m.
- The **-7°/+52° asymmetry is the main indoor liability**: mounted upright, the sensor sees only 7° below horizontal, so the floor is invisible beyond ~a few metres and there is a large blind cone directly beneath the aircraft. For indoor SLAM over a feature-poor hangar floor, that argues for mounting the sensor **inverted** (so the 52° cone looks *down* and the 7° looks up) or tilted, depending on whether floor geometry or ceiling trusses are the better feature source. In a hangar, ceiling trusses/lights are usually the richer feature set, which argues for keeping it upright; a flat empty floor gives almost nothing to a LIO front-end either way.
- 100BASE-TX is good news: no automotive-Ethernet media converter is needed, unlike some HAP/automotive Livox parts.

### Gaps
- Could not retrieve the Mid-360 FAQ answer text (the page renders questions only), so the IMU output rate, startup/inrush current and connector type are not confirmed from Livox primary sources. The 200 Hz IMU figure is reseller-sourced and tagged to the MID-360L variant.
- No published **inrush / startup current** figure for the Mid-360 was found from Livox. Livox publishes startup power for Avia (16 W) and HAP (26 W) but the Mid-360 spec page gives only the 14 W cold self-heating peak.
- No official pin-by-pin pinout for the Mid-360's **M12 12-pin** connector was found; a DigiKey forum thread reports Livox declines to document internal connectors — [DigiKey forum](https://forum.digikey.com/t/identification-of-unknow-mezzanine-connector/49380)
- Mass of the Livox breakout cable harness is not published anywhere I found. This matters at this weight budget.

## Sensor selection: alternatives (Livox and non-Livox)

### Takeaway
Within Livox, nothing else is competitive for this airframe. Outside Livox, the Hesai JT16 (~200 g, 4.3 W) and Unitree 4D L1 (~230 g, 6 W) are lighter and lower-power than the Mid-360 with comparable or better vertical coverage, and are worth serious consideration; the Ouster OS0 (377–447 g, 14–20 W) is out of budget.

### Cited Findings
Livox family:
- **Mid-70**: 580 g, 97 x 64 x 62.7 mm, 8 W average, 10–15 V DC (9–30 V with Converter 2.0), **70.4° circular FOV**, 100k pts/s single return, IP67, 100 Mbps Ethernet, sync via PTPv2 / PPS / GPS. No minimum range published; no IMU mentioned — [Livox Mid-70 specs](https://www.livoxtech.com/mid-70/specs)
- **Avia**: 498 g (without cables), 91 x 61.2 x 64.8 mm, 9 W repetitive / 8 W non-repetitive, **startup 16 W**, 10–15 V DC (9–30 V with Converter 2.0) — [Livox Avia specs](https://livoxtech.com/avia/specs)
- **HAP**: ~1120 g, 12 W typical, **startup 26 W**, 9–18 V DC, 105 x 131.6 x 65 mm, IP67, 120° x 25° FOV, 150 m @ 10% — [Livox HAP specs](https://livoxtech.com/hap/specs)
- **Mid-40**: ~710 g, ~10 W typical — reported in a third-party review, not confirmed against a Livox datasheet (see Gaps)

Non-Livox:
- **Unitree 4D LiDAR L1**: ~230 g, 6 W, 75 x 75 x 65 mm, 360° x 90° hemispherical FOV, 20 m @ 90% / 10 m @ 10% reflectivity (one listing says 30 m — sources conflict) — [Generation Robots L1](https://generationrobots.com/en/404133-unitree-4d-lidar-l1.html)
- **Unitree 4D LiDAR L2**: ~230 g, 10 W, 75 x 75 x 65 mm, 360° x 96°, 30 m @ 90% / 15 m @ 10% — [RobotShop L2](https://www.robotshop.com/products/unitree-4d-lidar-l2)
- **Hesai JT16**: under 200 g (retailer spec sheet: 199.7 g), 4.3 W, Φ62 x H64 mm, **360° x 40°** FOV, 30 m @ 10% reflectivity (100 m max) — [Hesai JT16](https://www.hesaitech.com/product/jt16/); the JT series is marketed with a 360° x 187° hyper-hemispherical FOV across the family — [New Equipment Digest](https://www.newequipment.com/product-directory/automation/robots/vision-systems/product/55377876/hesai-technology-mini-lidar-delivers-187-vertical-fov)
- **Ouster OS0**: 377 g without cap / 447 g with radial cap; **14–20 W, 23 W peak at startup**; 90° (±45°) vertical FOV; 45 m @ 80% reflectivity in 100 klx — [Ouster OS0 datasheet via RobotShop](https://cdn.robotshop.com/rbm/1452f63b-45fa-4c16-b9a5-44447596ee17/9/926a2a4b-0ddc-418d-846e-6e4dcc5a9173/85f35666_209129079.pdf)

### Inferences
- The Unitree L1/L2's symmetric ±45°/±48° hemispherical FOV is a materially better fit for **indoor** flight than the Mid-360's -7°/+52°: it sees the floor and the ceiling without needing a clever mounting angle. Its 10–15 m range at low reflectivity is irrelevant indoors where the hangar walls are inside 30 m anyway. Against it: far less mature SLAM ecosystem, and the Livox/FAST-LIO toolchain (and LI-Init support) is built around Livox non-repetitive scan patterns.
- Hesai JT16's 40° vertical FOV is narrower than the Mid-360's 59° total, so it trades coverage for 65 g and 2.2 W. For an aircraft this marginal, 65 g is roughly 12% of the empty takeoff weight — not nothing.
- The Ouster OS0's 14–20 W continuous is ~20–30% of the whole aircraft's estimated hover power (see power budget below), which on top of 450 g of mass rules it out.

### Gaps
- Mid-40 figures (710 g / 10 W) are from a secondary review, not a Livox datasheet. Treat as indicative. Also the Mid-40 is EOL-era hardware with no built-in IMU as far as I could establish.
- Mid-70 minimum range is not published by Livox; for a sensor specified for 90–260 m detection, the near-field behaviour is unknown and probably poor for indoor use.
- Unitree L1/L2 figures are all retailer-sourced; I found no Unitree primary datasheet. The range figures conflict between listings (20 m vs 30 m for L1).
- No data found on whether the Unitree or Hesai units expose a usable IMU and sync mechanism comparable to the Mid-360's.

## Starling 2 Max payload capacity, MTOW, flight time and the realistic budget

### Takeaway
ModalAI states 566 g takeoff weight and 500 g additional payload capacity, but the datasheet's own arithmetic is inconsistent (it cites a "total takeoff weight ~930 g" example). A Mid-360 installation realistically lands in the 420–480 g range all-in — within the stated capacity but at the top of it — and ModalAI's own engineer says a 500 g payload will **at best halve** flight time and in practice do worse.

### Cited Findings
- Takeoff weight **566 g**; payload capacity **500 g**, noted as affecting flight time "with total takeoff weight ~930 g" — [Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- Flight time **~55 min with Amprius cells, ~40 min with Li-Ion** — [Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- Battery: **Sony VTC6 3000 mAh 2S**, or any 2S 18650 Li-Ion pack with XT30; **two 2S packs wired in series for 4S, max 16.8 V** — [Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- Motors **2203.5, 1500 kV**; props **180 mm tri-blade**; diagonal 512 mm, height 120 mm, 260 mm motor-to-motor (width axis) and 190 mm motor-to-motor (length axis) — [Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- ESC: **ModalAI 4-in-1 Mini ESC with integrated power module** — [Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- ModalAI's Alex Kushleyev on payload: the Starling 2 Max **cannot carry 3–4 lb (1.36–1.81 kg)** and ModalAI has no platform for that; for a proposed **250 g** payload he calls the ~50% increase "quite substantial" — [ModalAI forum: adding payload to Max2](https://forum.modalai.com/topic/5272/adding-payload-to-max2)
- Same engineer, on 500 g: weight increases 2x so "in ideal world, the flight time will be cut in half," and motor/battery efficiency decrease under 2x load means the real loss is worse — [ModalAI forum / search summary of staff reply](https://forum.modalai.com/topic/5272/adding-payload-to-max2)

### Inferences
**Mass budget (Mid-360 build):**

| Item | Mass | Confidence |
|---|---|---|
| Livox Mid-360 | 265 g | published |
| Livox breakout harness (M12 → RJ45 + power), shortened | ~40–80 g | **estimate, unverified** |
| Damped mount plate + isolators + standoffs | ~50–80 g | **estimate, unverified** |
| M0062 Ethernet/USB hub add-on *or* USB-Ethernet dongle | ~20–60 g | **estimate, unverified** |
| Step-down/BEC if not tapping 4S directly | 0–15 g | estimate |
| **Total** | **~375–500 g** | |

That fits the stated 500 g capacity only at the low end of the estimates, and only if the harness is cut down to length. All-up weight becomes roughly **950–1070 g, i.e. 1.7x–1.9x the 566 g base**.

**Flight-time estimate (modelled, not measured):** 4S x 3000 mAh ≈ 43 Wh. At 40 min Li-Ion endurance the baseline average draw is ~65 W. Hover power scales roughly as W^1.5 at fixed disc area, so 1.8x mass → ~2.4x power → ~155 W → **~17 min**, before subtracting the LiDAR's own 6.5 W and any added compute. Call it **12–18 min realistic**, versus 40 min stock. This matches the ModalAI engineer's "worse than half" qualitatively. *This is my calculation from published figures, not a ModalAI or measured number.*

**Discharge check:** 155 W at ~14.4 V ≈ 10.8 A ≈ 3.6C on a 3000 mAh pack. VTC6 cells are rated well above that continuously, so the pack will deliver it, but usable capacity and voltage sag both worsen at 3.6C versus the ~1.5C baseline, which is exactly the "battery efficiency decrease" the ModalAI engineer flagged — so the 17 min figure is optimistic.

**Honest summary:** a Mid-360 will physically fly on this airframe, but it consumes essentially the entire published payload budget, cuts endurance to roughly a third, and leaves no margin for a companion computer. If a companion computer (even a Pi 5 / Orin Nano class board at 60–250 g plus 5–25 W) proves necessary because the VOXL 2 cannot run the LIO stack, the aircraft is over budget and the honest answer is **"not on this airframe."** A JT16 or Unitree L1 saves 35–65 g and 2–4 W and is the better choice if the software ecosystem can be made to work.

### Gaps
- The datasheet's 566 g + 500 g = 1066 g does not reconcile with its own "~930 g total takeoff weight" phrasing. ModalAI has not published a single unambiguous MTOW. Flag for the report.
- No published hover-power or thrust-curve data for the Starling 2 Max, so the flight-time estimate above is modelled, not sourced.
- Masses of the M0062 board, the Livox harness and any mount are not published; these are my estimates and should be weighed physically before committing.

## Power: voltage, current, rails and regulation

### Takeaway
The Mid-360's 9–27 V input range **spans the Starling 2 Max's 4S battery rail (12–16.8 V) directly**, so no step-down regulator is needed — tap the battery/ESC power module pass-through, never the VOXL 2's 5 V rails, which are tightly budgeted and already carry a 6 A inrush requirement of their own.

### Cited Findings
- Mid-360 input **9–27 V DC**, 6.5 W average — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)
- Starling 2 Max runs **two 2S packs in series for 4S, 16.8 V max** — [Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- VOXL 2 main power input **J4 is 5 V DC** (±5%, ModalAI power module set to 5.08 V no-load) and **requires at least 6 A of in-rush support at power-on** — [VOXL 2 connectors](https://docs.modalai.com/voxl2-connectors/)
- VOXL 2 cable-connector 5 V outputs are **rated 1 A each, and not all can supply 1 A simultaneously**; the fan output J2 return is limited to ~400 mA — [VOXL 2 connectors](https://docs.modalai.com/voxl2-connectors/)
- ModalAI's power module is a DC regulator accepting roughly **5.5 V to 28 V in, up to 6 A out at 5 V**, and **passes the input voltage through** so ESCs and other devices can be daisy-chained from it — ModalAI staff, [forum](https://forum.modalai.com/topic/2818/voxl2-mini-power-requirements)
- ModalAI staff warn the 5 V payload supply is **shared** — using the fan connector or USB can starve other 5 V loads — [forum](https://forum.modalai.com/topic/2818/voxl2-mini-power-requirements)
- Livox warns: check voltage range and polarity of power and function cables, and **do not connect any PoE device to the RJ-45 port** — [Livox wiki Mid-360](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/mid360.html)
- Third-party Mid-360 harnesses terminate the power lead in an **XT30** connector — [eBay listing, M12 12-pin to RJ45 + XT30](https://www.ebay.de/itm/356767235144); a 1-to-3 Livox splitter is rated 12 V DC and lists Mid-360 compatibility — [OpenELAB splitter](https://openelab.com/products/livox-aviation-connector-splitter-cable)
- DJI/Livox state the three-wire breakout cable is "only applicable for debugging and verification" and advise custom wiring for high-reliability scenarios — [DJI store, Livox three-wire aviation connector](https://store.dji.com/product/livox-three-wire-aviation-connector)

### Inferences
- **Recommended wiring:** XT30 tee off the main battery (or the ESC power module's pass-through) straight into the Mid-360's power lead. The battery is 2S x 2 in series, so the airframe already uses XT30 — the Livox harness's XT30 termination is a lucky match. Add an inline fuse (1–2 A) since the LiDAR draws <0.6 A at 14.4 V and a short on an unfused tap would take down the whole aircraft.
- **No BEC needed** for the Mid-360 specifically. A BEC *would* be needed for the Avia or Mid-70 (10–15 V without Converter 2.0 — a fully charged 4S at 16.8 V exceeds that), which is another mark against them.
- **Inrush is the open risk.** Livox does not publish Mid-360 inrush, and its siblings show 2x typical power at startup (Avia 8→16 W, HAP 12→26 W). A 2x inrush on 6.5 W is only ~13 W / ~0.9 A, which the pack will shrug off; the real concern is a capacitive inrush transient on the shared battery rail disturbing the ESC power module during the 6 A VOXL 2 boot inrush. Powering the LiDAR after VOXL 2 has booted, or adding a soft-start/inrush limiter, is the conservative approach. *This is engineering judgement, not a sourced recommendation.*
- **Do not** power the LiDAR from any VOXL 2 5 V output: 6.5 W at 5 V would be 1.3 A, above the 1 A per-connector rating, and the rails are already shared with the fan and USB.

### Gaps
- Mid-360 inrush current is unpublished (see above).
- No source found for the Starling 2 Max's spare power-tap connectors (whether a payload XT30 pigtail exists on the harness) — the datasheet does not list vehicle-side connectors, only the add-on board's I2C/UART/GPIO/USB.

## Physical integration: mounting, CG and FOV occlusion

### Takeaway
There is no documented Mid-360 mount for the Starling 2 Max, and the geometry is hostile: a 65 x 65 x 60 mm sensor with a 360° horizontal FOV must sit above or below the 512 mm-diagonal prop disc on a standoff tall enough to clear props and landing gear, while ModalAI's own advice is to keep added mass as close to the geometric centre as possible.

### Cited Findings
- ModalAI's Alex Kushleyev: mount new mass "as close as possible to the geometrical center" to limit added moment of inertia; off-centre mass makes the vehicle imbalanced at hover and more so during acceleration — [ModalAI forum](https://forum.modalai.com/topic/5272/adding-payload-to-max2)
- Same thread: expect **flight controller retuning** (attitude and height controllers) starting from the stock Starling 2 Max tune; no ESC retune expected; test with a dummy weight first if a payload step doesn't work well — [ModalAI forum](https://forum.modalai.com/topic/5272/adding-payload-to-max2)
- Airframe geometry: diagonal 512 mm, height 120 mm, 180 mm tri-blade props, 260 x 190 mm motor-to-motor — [Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- Mid-360 mounting hardware: **M3 mounting holes**, plus a locating hole that "can improve positioning accuracy when designing a fixed bracket" — Livox Mid-360 user manual, as summarised in [LIVOX Mid-360 User Manual mirror](https://aifitlab-wiki.super.site/382d4c79856d806687bbda2a0255859b)
- Livox warns against overlapping FOVs with other Mid-360s: "if the laser beams are pointed right at each other, irreversible damage may be caused" — [Livox wiki Mid-360](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/mid360.html)
- Vendor integration guidance: the **upper part of the Mid-360's vertical FOV has a shorter effective range and the lower part a longer one**, so sensor tilt determines which part of the scene gets the longer range; apply the -7°/+52° limits in the sensor frame in the mechanical model — [OpenELAB Mid-360S integration guide](https://openelab.io/blogs/learn/livox-mid-360s-amr-integration-guide)
- A quadrotor study using the Mid-360 reports its point-cloud FOV as 360° horizontal, 7° down, 52° up — [arXiv 2512.14340, UAV lidar field evaluation](https://arxiv.org/pdf/2512.14340)

### Inferences
- **Top-centre mast is the only viable location.** Mounting below risks the landing gear and ground strikes on a 60 mm-tall sensor, and the drone lands on it. A top mast puts the sensor's horizontal scan plane above the prop disc (props sit near the 120 mm airframe height), so the 360° ring is clear of blade shadow. Expect ~40–70 mm of standoff and accept the CG rise.
- **CG rise is the dominant handling penalty**, not CG offset. 265 g at ~80–100 mm above the existing CG on a 566 g airframe shifts the combined CG up by roughly 25–35 mm and raises the pitch/roll moment of inertia substantially. On a small quad this reads as sluggish attitude response and lower achievable rate-loop gains — consistent with ModalAI's "expect to retune the attitude controller".
- **Arm/prop occlusion in the horizontal ring is unavoidable** on a top mast: the four arms and the mast itself will cast narrow shadow sectors in the 360° scan. A LIO front-end tolerates this (it is static in the body frame and the scan is non-repetitive), but the occluded sectors must be masked or they will be learned as persistent close returns. *Inference, no source.*
- **Orientation decision for the hangar:** upright gives 52° of upward coverage (ceiling trusses, lights, roof structure — the feature-rich part of a bare hangar) and only 7° down. Inverted gives 52° down over a featureless floor. Upright is probably right for an empty hangar, but it means almost no ground-plane observability, which is exactly what a LIO altitude estimate wants. A compromise is mounting the sensor **tilted ~20–25° nose-down or pitched**, which costs horizontal symmetry. This tradeoff is not resolved by any source I found and should be decided empirically.

### Gaps
- No published Mid-360 mount, bracket or STL for any ModalAI airframe, and no forum report of anyone having flown one on a VOXL 2 platform.
- Mid-360 exact mounting-hole pattern dimensions were not retrieved (they are in the manual's "mounting dimensions" section, which I could not extract).
- No data on prop-wash effects on the Mid-360's optical window or on point-cloud quality from rotor-induced airflow.

## Vibration isolation

### Takeaway
Livox publishes only an automotive random-vibration qualification for the Mid-360 and sells a shock-absorption accessory, but no quantitative isolation guidance exists for multirotors; and on a 566 g airframe, soft-mounting a 265 g mass creates a pendulum whose resonance will sit uncomfortably close to the flight controller's own vibration band.

### Cited Findings
- The Mid-360 manual states the sensor meets the random-vibration testing requirements of **GB/T 28046.3-2011 §4.1.2.4** (mainland China) / **ISO 16750-3:2007** (elsewhere) — a qualification standard for the sensor, not in-flight isolation guidance — [LIVOX Mid-360 User Manual mirror](https://aifitlab-wiki.super.site/382d4c79856d806687bbda2a0255859b)
- The Livox wiki has a page titled "Introduction to shock absorption and cooling accessories" with installation dimensions, listed under the Mid-360 section — [Livox wiki Mid-360](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/mid360.html) (page content not retrieved)
- Mount attachment is via **M3 screws** into the sensor's mounting holes, with a locating hole for repeatable positioning — [LIVOX Mid-360 User Manual mirror](https://aifitlab-wiki.super.site/382d4c79856d806687bbda2a0255859b)

### Inferences
- **The isolation requirement is driven by the sensor's internal IMU, not the laser.** The ICM40609 sits inside the sealed housing with no user access to its own damping, so whatever vibration reaches the housing reaches the IMU. A LIO front-end integrating a saturated or aliased IMU will diverge, and the Mid-360's IMU is a consumer-grade part with a modest full-scale range.
- **A soft mount is a two-edged tool here.** Standard practice for FC/IMU isolation is a gel or wire-rope mount tuned so the isolator's natural frequency sits well below the prop's blade-pass frequency. 2203.5 motors on 180 mm tri-blades at hover run on the order of 100–150 Hz fundamental (3x that for blade pass), so a 15–25 Hz isolator corner is the usual target. But 265 g on a soft mount atop a 40–70 mm mast is a pendulum with a rigid-body rocking mode potentially in the 5–15 Hz range — squarely inside the attitude control bandwidth of a small quad. That produces a structural mode the rate loop can excite, which is the classic cause of "it flies fine until you push the gains" on soft-mounted heavy payloads. *Engineering reasoning, not sourced.*
- Practical recommendation: start with a **stiff mount** (rigid standoffs, well-balanced props, blade-tracked), measure the Mid-360 IMU's spectrum in situ, and only add isolation if the spectrum shows saturation — and if isolation is added, use a short, stiff-in-shear mount (damped elastomer washers, not gel pads on a tall mast) so the rocking mode stays above ~30 Hz. Also log PX4's own vibration metrics before and after fitting, since the added mass changes the airframe's structural modes whether or not the LiDAR is isolated.

### Gaps
- Could not retrieve the content of Livox's shock-absorption accessory page, so the official accessory's isolator type, durometer and rated load are unknown.
- Found **no quantitative study** of Mid-360 IMU noise floor or saturation on a multirotor. The resonance figures above are my reasoning from standard multirotor practice, not measurements.
- No sourced guidance on how a soft-mounted LiDAR mass interacts with PX4's rate-loop tuning on this airframe.

## Time synchronisation (the hard problem)

### Takeaway
The Mid-360 supports PTPv2, gPTP and GPS/PPS; with no GPS indoors the only option is **PTP with the VOXL 2 (or a companion) as grandmaster**, and since the VOXL 2 has no native Ethernet MAC, the link runs over a USB-Ethernet path that almost certainly cannot do hardware timestamping — leaving software PTP at tens-of-microseconds-to-milliseconds accuracy. The saving grace is that the Mid-360's internal IMU and its points share the sensor's own clock, so LIO's tightest sync requirement is met inside the sensor regardless.

### Cited Findings
- Mid-360 supports **3 methods: PTP (IEEE 1588v2.0 over UDP/IP), gPTP (automotive Ethernet, Layer 2), and GPS (PPS + GPRMC)**. PTP v2.1 is **not** supported; mixing 1588v2.0 and gPTP on one network is discouraged — [Livox time sync instructions](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/common/time_sync.html) and [Livox wiki Mid-360](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/mid360.html)
- "PTP v2 and gPTP can be used for time synchronization between Livox LiDAR and other devices **without GPS and PPS hardware signals**" — [Livox time sync instructions](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/common/time_sync.html)
- The sensor **automatically synchronises to a PTP master** when one is present on the network; only one master clock is needed in the whole network — [Livox time sync instructions](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/common/time_sync.html)
- Verification: presence of `Sync` and `Follow_Up` messages on the network confirms a working master; the point-cloud packet header's **`timestamp_type` = 1 indicates PTP sync** — [Livox time sync instructions](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/common/time_sync.html)
- When PTP and GPS are both available, **PTP takes priority** — [Livox time sync instructions](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/common/time_sync.html)
- On residual sync error: a paper reports "the map accuracy is limited by the inaccurate internal synchronization in FAST-LIO2," and after estimating a temporal offset from the first 20 s of data, "the odometry end-to-end drift is only 0.0102 m over a 11.3627 m trajectory for our method while 0.246 m for the LIO's internal time synchronization" — [arXiv 2409.04961](https://arxiv.org/pdf/2409.04961)
- LI-Init calibrates "the temporal offset, extrinsic, gravity vector, and IMU bias" on the fly, which includes the LiDAR–IMU time offset — [arXiv 2202.11006, Robust Real-time LiDAR-inertial Initialization](https://arxiv.org/pdf/2202.11006)

### Inferences
- **Three distinct sync problems, with very different tolerances.** (1) LiDAR-point-to-internal-IMU: handled inside the sensor, sub-millisecond, and residual offset is estimable by LI-Init. Needs microsecond-class accuracy and gets it. (2) LiDAR/LIO-pose-to-PX4-EKF2: the LIO pose must be timestamped on a clock EKF2 understands, same as the current mocap `vehicle_visual_odometry` path. EKF2's external-vision delay parameter (`EV_DELAY_MS`) absorbs a constant offset; jitter is what hurts. Millisecond-class is workable here, matching what the existing mocap bridge already tolerates. (3) LiDAR-to-mocap, for ground-truth comparison during bring-up: millisecond-class is enough for offline evaluation.
- Because (1) is solved internally, **the PTP problem is less severe than it first looks for this application**. Running software PTP (`linuxptp`/`ptp4l` in software-timestamping mode) on the VOXL 2 as grandmaster, giving the Mid-360 a monotonic clock tied to the host's, is sufficient for (2) and (3). What PTP buys is a common epoch, not sub-microsecond alignment.
- **The grandmaster must be on the aircraft.** With no GPS indoors and the LiDAR on a point-to-point link to the VOXL 2, the VOXL 2's own CLOCK_REALTIME becomes the time reference. That clock is itself unsynchronised to anything (no NTP indoors unless the lab network provides it), so absolute time is arbitrary — fine for onboard LIO, a nuisance for post-flight comparison against OptiTrack logs. Running an NTP/PTP source on the ground station over the lab WiFi, with the VOXL 2 as a boundary clock, is the clean fix.
- **USB-Ethernet kills hardware timestamping.** PTP's sub-microsecond accuracy depends on MAC-level hardware timestamps. A USB-attached NIC adds non-deterministic USB bus latency on both directions of every Sync/Delay_Req exchange. Expect software-PTP-class accuracy (tens of µs best case on a quiet link, worse under load). Whether the M0062's Ethernet PHY supports hardware timestamping is unknown and worth asking ModalAI directly — if it does, that is a real argument for the M0062 over a dongle. *Inference; see Gaps.*
- A practical fallback if PTP proves unreliable: run the LiDAR on its free-running internal clock and estimate the host-to-sensor offset online, as the arXiv 2409.04961 authors did. The 0.246 m vs 0.0102 m drift figures show the cost of getting this wrong is real but bounded.

### Gaps
- **Unknown whether the M0062's Ethernet interface supports IEEE 1588 hardware timestamping.** This is the single most important unanswered question in this section and determines whether PTP is microsecond- or millisecond-class on this platform. Not documented; ask ModalAI.
- No source found on PTP daemon configuration on the VOXL 2 specifically, or whether ModalAI's VOXL SDK kernel ships `linuxptp`/`CONFIG_PTP_1588_CLOCK`.
- No published figure for what LIO *requires* in LiDAR-host sync accuracy as an absolute threshold; the arXiv result shows sensitivity but does not give a spec.

## Extrinsic calibration (LiDAR-to-IMU, LiDAR-to-body)

### Takeaway
Two mature open-source options exist and both explicitly handle Livox: **LI-Init** (HKU MARS, online/targetless, integrated with FAST-LIO2, explicitly supports Livox Avia/Mid360) and **LI-Calib / lidar_IMU_calib** (APRIL-ZJU, offline continuous-time batch). LI-Init is the better fit for a Mid-360 because it initialises gravity, which is where LI-Calib reportedly fails on Livox data.

### Cited Findings
- LI-Init "can automatically detect the degree of excitation of the collected data and calibrate, on-the-fly, the **temporal offset, extrinsic, gravity vector, and IMU bias**," which then seed the LIO state — [arXiv 2202.11006](https://arxiv.org/pdf/2202.11006)
- LI-Init "supports both mechanical spinning LiDAR (Hesai, Velodyne, Ouster) and solid-state LiDAR (**Livox Avia/Mid360**)"; `livox_ros_driver` must be installed and sourced first; depends on ceres-solver (tested with 2.0.0); Docker option available; published at IROS 2022 — [hku-mars/LiDAR_IMU_Init](https://gitee.com/T_O_P/LiDAR_IMU_Init) (mirror of the HKU repo) and [arXiv 2202.11006](https://arxiv.org/pdf/2202.11006)
- LI-Init is "integrated into a state-of-the-art LiDAR-inertial odometry system FAST-LIO2" — [arXiv 2202.11006](https://arxiv.org/pdf/2202.11006)
- LI-Calib is a **targetless, offline** method calibrating the full 6-DOF LiDAR–IMU transform, using a **continuous-time B-spline trajectory** ("more suitable for fusing high-rate or asynchronous measurements") and planar-segment data association from a cell-decomposed map — [arXiv 2007.14759](https://arxiv.org/pdf/2007.14759); code at [APRIL-ZJU/lidar_IMU_calib](https://github.com/APRIL-ZJU/lidar_IMU_calib)
- On Livox data specifically, a benchmark paper reports "LI-Calib's refinement fails and calibration result diverges due to ignorance of gravity vector initialization," and reports its own method achieving **0.2472 ± 0.2043 degrees** rotation error on a Livox Mid360 — [arXiv 2409.04961](https://arxiv.org/pdf/2409.04961)

### Inferences
- **Recommended workflow for this project:** (1) measure the nominal LiDAR→body transform from CAD/mount geometry to get a starting guess; (2) run LI-Init on a hand-carried or flown dataset with good excitation in all axes to refine the LiDAR→(internal) IMU extrinsic and time offset; (3) obtain the LiDAR→PX4-body transform either by composing the above with a separately-calibrated Mid-360-IMU→PX4-IMU rotation, or — and this is the lab's advantage — **by using OptiTrack as ground truth**: rigid-body mark the airframe, fly a trajectory, and solve the hand-eye problem between the mocap-reported body pose and the LIO-reported LiDAR pose. The existing mocap setup makes this considerably easier than for teams without one.
- LI-Init's requirement for **sufficient excitation** is a safety consideration: it needs vigorous rotation about all three axes, which is easier and safer to provide by hand-carrying the powered aircraft than by flying it.
- Note LI-Init is ROS 1; the AirStack stack is ROS 2, so expect either a bridge or a port. (Flagged as a software issue, out of scope here, but it affects the calibration workflow.)

### Gaps
- Could not confirm the current state of either repo's README, Livox-specific parameter settings, or whether a maintained ROS 2 port of LI-Init exists.
- **Livox's own calibration tooling** was not found. Livox publishes a multi-LiDAR calibration tool and a camera-LiDAR calibration tool historically, but I found no official Livox LiDAR-to-IMU extrinsic tool for the Mid-360 (the internal IMU extrinsic is presumably factory-set and published in the manual — I could not retrieve that section).
- No published factory value for the Mid-360's internal IMU-to-LiDAR-origin offset was retrieved, though one is normally given in the manual's coordinate-system section.

## Interface: connector, link type, and whether the VOXL 2 can talk to it at all

### Takeaway
This is the feasibility crux and the answer is **yes, but only with an add-on board**. The Mid-360 is standard 100BASE-TX Ethernet over an RJ45 breakout — not automotive 100BASE-T1 — but the **VOXL 2 has no native Ethernet port**. ModalAI sells the M0062 Ethernet + USB hub add-on which enumerates as `eth0`, and ModalAI staff have separately suggested a USB-to-Ethernet adapter. Neither path has been confirmed working with a Mid-360 by anyone.

### Cited Findings
- Mid-360 interface is **100BASE-TX Ethernet** — [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs). (Note: gPTP is listed as an option, which is an automotive-Ethernet protocol, but the physical layer is TX, not T1.)
- The sensor-side connector is an **M12 12-pin (A-coded) female**; standard breakout cables split it into **RJ45 + power** — [MyBotShop Livox connector cable Mid360](https://www.mybotshop.de/Livox-connector-cable-Mid360-AVIA2-1m_1), [eBay M12 12-pin to RJ45 + XT30](https://www.ebay.de/itm/356767235144)
- **VOXL 2 has no native Ethernet port.** The connector list covers J9 (USB-C, ADB), J4 (5 V power in), J2 (fan), J3/J5 (B2B expansion), J6/J7/J8 (camera MIPI), J10 (SPI), J18 (ESC UART), J19 (GNSS/mag/RC) — no RJ45 and no Ethernet MAC exposed — [VOXL 2 connectors](https://docs.modalai.com/voxl2-connectors/)
- The only USB-C port is **J9 (ADB)**; USB1 is available as B2B signals on J3, not a standard port — [VOXL 2 connectors](https://docs.modalai.com/voxl2-connectors/)
- **M0062 "VOXL 2 Ethernet and USB Hub Add-on"**, $259.99, adds wired Ethernet **enumerating as `eth0`** (DHCP or static, then SSH/voxl-portal/RTSP over IP), a USB3 host port (10-pin ModalAI format, 1 A VBUS), a USB2 host port (4-pin), a USB2 Type-A port, uSD/UFS socket, and FTDI debug console; compatible with VOXL 2, Sentinel, VOXL 2 Flight Deck; **not** compatible with VOXL 2 Mini — [ModalAI M0062-2 product page](https://www.modalai.com/collections/expansion-board/products/m0062-2) and [M0062-2 docs](https://docs.modalai.com/m0062-2/)
- Known M0062 issue: the Type-A connector **J10 is unreliable** — "not working consistently on this board for USB3 speeds and may only work in USB2 mode"; ModalAI says use J11, with MCBL-00022-2 to get a Type-A on J11 — [M0062-2 docs](https://docs.modalai.com/m0062-2/)
- ModalAI staff on Mid-360 specifically: "We haven't used this sensor before but if you use an ethernet to USB adapter, you should be able to get a network connection to the sensor from VOXL 2"; they advised against the side USB-C and suggested an add-on giving a USB-A connector — [ModalAI forum, integrating lidar sensor](https://forum.modalai.com/topic/4660/integrating-lidar-sensor)
- "The VOXL2 will act as the host for whatever USB device you plug in there. So you can use a WiFi dongle, ethernet adapter, UVC camera, etc." — ModalAI staff, [same thread](https://forum.modalai.com/topic/4660/integrating-lidar-sensor)
- An earlier (Feb 2025) thread asked exactly this question for Mid-360 on Starling 2 Max; ModalAI staff replied they have **"no experience with this sensor"** and pointed at the VOXL 2 connector docs. The original poster planned to use the extension board's Ethernet port; no follow-up confirms success — [ModalAI forum, Mid-360 compatibility with VOXL 2 on Starling 2 Max](https://forum.modalai.com/topic/4196/clarification-on-livox-mid-360-lidar-compatibility-with-voxl-2-on-starling-2-max-outdoor-drone)
- ModalAI's Eric Katzfey: ModalAI uses **time-of-flight sensors indoors, stereo cameras outdoors, and single-point LiDAR for height** — i.e. no scanning-LiDAR precedent on their platforms — [same thread](https://forum.modalai.com/topic/4196/clarification-on-livox-mid-360-lidar-compatibility-with-voxl-2-on-starling-2-max-outdoor-drone)
- Livox warns: **do not connect any PoE device to the RJ-45 port** — [Livox wiki Mid-360](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/mid360.html)

### Inferences
- **The M0062 is the right answer over a USB dongle**, despite the $260 and the added mass, because: it gives a real `eth0` that ModalAI supports and documents; it avoids the ADB-shared USB-C port; and it is the only path with any chance of hardware PTP timestamping. The counter-argument is mass and the fact that it occupies the expansion stack.
- **Bandwidth is not a constraint.** 200k pts/s at ~16 bytes/point plus IMU is on the order of 5–10 Mbit/s — trivial for 100BASE-TX even over USB2.
- **Two independent "no precedent" signals.** ModalAI staff have twice said they have no experience with this sensor, and two separate forum threads asking about Mid-360 + VOXL 2 both end without a confirmed working integration. Treat this as genuinely unexplored territory on this platform: budget significant bring-up time, and expect to be the first to debug it.
- The Mid-360's default IP addressing is per-device and must be configured against the host's static `eth0` address; the Livox SDK2 discovery is broadcast-based, so the host must be on the same subnet with broadcast enabled. (Software detail, flagged because it affects whether the M0062's `eth0` static config is adequate.)

### Gaps
- **No one has publicly flown or even bench-integrated a Livox Mid-360 on a VOXL 2.** No confirmed working configuration, no driver port, no reported point-cloud throughput.
- M0062 mass, power draw and dimensions are not published anywhere I found — material for a weight budget this tight.
- Whether the M0062's Ethernet PHY supports IEEE 1588 hardware timestamping is undocumented.
- Whether the M0062 physically fits on a Starling 2 Max (as opposed to a bare VOXL 2 or a Sentinel) alongside the existing add-on board is not addressed in any source. The compatibility table lists "VOXL 2, Sentinel, VOXL 2 Flight Deck" and does not mention Starling 2 Max by name.

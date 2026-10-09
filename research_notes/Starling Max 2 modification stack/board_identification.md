# Starling Max 2 / VOXL 2 board and airframe identification

Scope note: the user's two airframes are tagged `m0054` and `D0012`. Research below confirms
`D0012` is ModalAI's airframe code for the **Starling 2 Max** and `M0054` is the original
full-size **VOXL 2** compute board. Everything here is organised around telling two vintages
of that airframe apart at a bench.

---

## Q1. Naming: "Starling 2", "Starling 2 Max", "Starling Max 2"

### Takeaway
The official ModalAI product name is **"Starling 2 Max"** (airframe code **D0012**); the smaller
sibling is **"Starling 2"** (airframe code **D0014**). "Starling Max 2" is not a name ModalAI
uses anywhere in its own docs or store — it is a transposition, and the repo's internal use of it
should be read as meaning Starling 2 Max.

### Cited Findings
- ModalAI's datasheet is titled "Starling 2 Max Datasheet" and lives at `docs.modalai.com/starling-2-max-datasheet/` — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/)
- A separate "Starling 2 Datasheet" exists for the smaller 230mm-diagonal aircraft (3mm carbon fibre frame, 230mm diagonal) — [ModalAI docs](https://docs.modalai.com/starling-2-datasheet/)
- The Starling 2 Max replacement-parts page uses SKU templates `D0012-4-V3-CXX-MXX-TX` and `D0012-4-V4-CXX-MXX-TX`, and explicitly marks "Starling 2 (D0014)" as incompatible with those parts — [ModalAI store](https://www.modalai.com/products/starling-2-max-replacement-parts)
- A forum user quotes a real unit SKU as `MRB-D0012-4-V2-C28-T8-M11-X0` — [forum.modalai.com thread 5246](https://forum.modalai.com/topic/5246/starling-2-max-not-detecting-wifi-hardware.md)
- The Starling 2 Max datasheet's own wiring-diagram asset is named `D0012-V1-compute-wiring`, while the Starling 2 datasheet's is `D0014-V1-compute-wiring` — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/); [ModalAI docs](https://docs.modalai.com/starling-2-datasheet/)
- The older "Starling" (v1, pre-"2") is documented by PX4 as the "VOXL 2 Starling PX4 Development Drone" — [PX4 v1.14 docs](https://docs.px4.io/v1.14/en/complete_vehicles/modalai_starling.html)

### Inferences
- The user's `D0012` tag positively identifies the airframe family as Starling 2 Max, not Starling 2.
- SKU grammar appears to be `MRB-D00xx-<rotors>-V<airframe rev>-C<camera config>-T<radio>-M<modem/wifi>-X<extra>`.
  `C28`/`C29` are confirmed camera configs and `T8`/`T9` confirmed radio options (below); the `M11`
  and `X0` fields are inferred from position only.

### Gaps
- No official ModalAI page decoding the SKU grammar field-by-field was found. The `M##` field is
  the most interesting one here (likely the datalink/modem option) but is unconfirmed.

---

## Q2. Part numbers: which M-number is which board?

### Takeaway
**M0054 = VOXL 2 (original full-size), M0154 = VOXL 2 (refreshed full-size, same board),
M0104 = VOXL 2 Mini, M0204 = VOXL 2 Mini (current refresh).** The user's `m0054` tag therefore
means "full-size VOXL 2, original part number" — **not** a Mini. Starling 2 Max ships the
full-size VOXL 2, so neither of the user's two aircraft should be a Mini.

### Cited Findings
- ModalAI's VOXL 2 / VOXL 2 Mini system image page states support for "VOXL 2 (M0054)" and "VOXL 2 Mini (M0104)" — [ModalAI docs](https://docs.modalai.com/voxl2-voxl2-mini-system-image/)
- The SDK 1.4 support matrix lists: `VOXL 2 | M0054-1, M0054-2, M0154-1, M0154-2` and `VOXL 2 Mini | M0104-1` — [ModalAI SDK 1.4 release notes](https://docs.modalai.com/sdk-1.4-release-notes/)
- "M0054-1 and M0154-1 are functionally equivalent; M0154-1 refreshes some non-logic EOL components on M0054-1." — [ModalAI VOXL 2 product page](https://www.modalai.com/products/voxl-2)
- "M0054-2 and M0154-2 have identical performance characteristics and capabilities to M0054-1 and M0154-1, except the -2 assemblies only support up to 4 cameras concurrently." — [ModalAI VOXL 2 product page](https://www.modalai.com/products/voxl-2)
- Current full-size dev-kit SKUs: `MDK-M0154-1-00` (board only, `MCCA-M0154-1-T` = 1x CCA VOXL 2, tested) and `MDK-M0154-1-01` (no-image-sensor dev kit, adds VOXL Power Module v3 + 12V 3A supply) — [ModalAI VOXL 2 product page](https://www.modalai.com/products/voxl-2)
- Current Mini dev-kit SKU is `MDK-M0204-1-00` — [ModalAI VOXL 2 Mini product page](https://www.modalai.com/products/voxl-2-mini)
- The Mini connector doc contains a revision note "J6 pin 26: unique to M0104, shared on M0204", confirming M0204 is the Mini's successor part — [ModalAI docs](https://docs.modalai.com/voxl2-mini-connectors/)
- A system-image changelog entry adds "support for M0104-2 via var02 variant", so the Mini also has dash revisions — [ModalAI docs](https://docs.modalai.com/voxl2-voxl2-mini-system-image/)
- The Starling 2 Max datasheet's critical-components table names the flight controller / companion computer as **"VOXL 2, M0154, San Diego, CA, USA"** — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/)

### Other M-numbers that appear in the Starling 2 Max BOM / ecosystem
- `M0184` — Gemini 915MHz ELRS radio ("T8" radio option) — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/)
- `M0161`, `M0166` — ModalAI camera modules listed in the Starling 2 Max camera row — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/)
- `M0151` (written `M00151` by the forum poster) — USB3.0 / UART Expansion Adapter, the carrier the Alfa USB WiFi dongle hung off on older Starling 2 Max units — [forum.modalai.com post 25386 / thread 4704 area](https://forum.modalai.com/post/25386)
- `M0213` — VOXL 2 WiFi Addon (Sparrow module), 500mW dual-band — [ModalAI docs](https://docs.modalai.com/m0213/); [ModalAI wifi-modems](https://docs.modalai.com/wifi-modems/)
- `M0141` — the board M0213 directly replaces (ModalAI staff: "the M0213 was a direct replacement for the M0141 board") — [forum.modalai.com thread 5309](https://forum.modalai.com/topic/5309/m0213-wifi-board-pinout-and-availability.md)
- `M0078-2` — USB Debug add-on; `M0090` — PCIe/5G Modem Carrier add-on; both expose a USB 2.0 hub used for WiFi dongles — [ModalAI beta docs, voxl2 wifi dongle guide](https://beta-docs.modalai.com/voxl2-wifidongle-user-guide)
- `M0188` — VOXL 2 Mini Camera Break-out — [ModalAI store](https://www.modalai.com/products/m0188)
- `M0135` — VOXL 2 Dual Image Sensor Expander — [ModalAI store](https://www.modalai.com/en-tw/products/mdk-m0135)
- `M0076` / `M0084` — VOXL 2 Mini camera adapters — [forum.modalai.com thread 3101](https://forum.modalai.com/topic/3101/voxl-2-mini-w-camera-adapter-m0076-m0084-are-there-any-versions-that-have-smaller-fr4-footprints.md)
- Mechanical parts use a different `M1000xxxx` series: frame V4 `M10001459`, frame V1–V3 (T-Motor) `M10000929`, V3 frame `M10000868`, V3 gold motor 2203.5 1500kV `M10000073`, V4 black motor 2204 1500kV `M10001367`, V4 feet `M10001460`, prop nuts `M10001405`, prop set `MRP-D0012-1-00`, V4 power train `MSA-D0012-3-01-T`, ToF upgrade kit (C28→C29) `MRP-D0012-1-06` — [ModalAI store](https://www.modalai.com/products/starling-2-max-replacement-parts)

### Inferences
- Since the Starling 2 Max BOM names M0154, a *newer* Starling 2 Max is likely to report
  `hw platform: M0154`, while the user's older `m0054`-tagged unit reports `M0054`. That single
  line in `voxl-version` is the cleanest discriminator available.
- M0054 vs M0154 is a component-refresh respin of the *same* VOXL 2 design, so the difference is
  not functionally interesting except for camera count on `-2` assemblies.

### Gaps
- No source found that states which VOXL 2 part number shipped in which Starling 2 Max airframe
  revision (V1/V2/V3/V4). The mapping M0054→older airframe, M0154→newer airframe is an inference.

---

## Q3. VOXL 2 vs VOXL 2 Mini: concrete differences

### Takeaway
Same SoC and same software stack; the Mini is a 42×42mm / 11g board with 1S (3.8V nominal) power,
4 concurrent cameras and no legacy B2B expansion, while the full VOXL 2 is 70×36mm / 16g with
5V power, 6–7 concurrent cameras, a 60-pin legacy B2B and a 120-pin high-speed B2B. **Neither has
WiFi integrated on the compute board.**

### Cited Findings (feature matrix — [ModalAI docs](https://docs.modalai.com/voxl2-mini-feature-matrix/))
| Feature | VOXL 2 Mini | VOXL 2 |
|---|---|---|
| Dimensions | 42 × 42 mm | 70 × 36 mm |
| Weight | 11 g | 16 g |
| MIPI image sensors | 4 concurrent | 6 concurrent |
| CPU | QRB5165, 8 cores to 3.091 GHz, 8GB LPDDR5, 128GB flash | same |
| OS | Ubuntu 18.04, kernel 4.19 | same |
| GPU / NPU | Adreno 650 (1024 ALU) / 15 TOPS | same |
| Embedded flight controller | **PX4 or ArduPilot** on the Sensors DSP | **PX4 only** on the Sensors DSP |
| Integrated sensors | 2× ICM-42688P IMU, 1× ICP-10100 baro | same |
| Power consumption | 0.5–8 W | same |
| **Built-in WiFi** | **No** | **No** |
| Add-on connectivity | USB3 port, WiFi, 5G, 4G/LTE, Microhard | add-on board, WiFi, 5G, 4G/LTE, Microhard |
| NDAA '20 §848 | Yes, assembled in USA | Yes, assembled in USA |

- The Mini requires **Platform Release 1.0 or newer** — [ModalAI docs](https://docs.modalai.com/voxl2-mini-feature-matrix/)
- VOXL 2 product page claims "seven simultaneous MIPI inputs" (marketing) against the feature matrix's "6 concurrent"; `-2` assemblies are capped at 4 — [ModalAI VOXL 2 product page](https://www.modalai.com/products/voxl-2); [ModalAI docs](https://docs.modalai.com/voxl2-mini-feature-matrix/)
- Mini press launch: 42mm × 42mm, 11 grams — [BusinessWire / ModalAI release](https://www.businesswire.com/news/home/20230502005109/en/5436246/ModalAI-Launches-11g-VOXL%C2%AE-2-Mini-to-Advance-the-Industry-Towards-the-Smallest-AI-Drones)

#### VOXL 2 (M0054/M0154) connectors — [ModalAI docs](https://docs.modalai.com/voxl2-connectors/)
| Des. | Type | Function |
|---|---|---|
| J2 | 2-pin R/A header | 5V fan, PWM controlled |
| **J3** | **60-pin legacy B2B receptacle** | plug-in board power, JTAG/debug, QUP expansion, GPIO, USB3.1 Gen2 (USB1). Intended for LTE / Microhard / **WiFi** add-ons |
| J4 | 4-pin R/A | prime power input, 5V DC + GND + I2C @5V for power monitor |
| J5 | 120-pin high-speed B2B socket | 3.8V/3.3V/1.8V rails, 5V "SOM mode" input, QUP, GPIO, SDCC, secondary UFS, 2-lane PCIe Gen3, AMUX, SPMI |
| J6 / J7 / J8 | 60-pin B2B plugs | Camera groups 0/1/2 — each: 2× 4-lane MIPI CSI, CCI, camera control, 8 power rails 1.05–5V, dedicated SPI (QUP) |
| J9 | USB-C 24-pin R/A | ADB with re-driver + DisplayPort alt-mode (USB0) |
| J10 | 8-pin header | SPI @3.3V, 2 chip selects, 32kHz clock out. **On M0154 it can be switched to UART mode via GPIO_67** |
| J18 | 4-pin header | ESC UART @3.3V — PX4 talks to the VOXL ESC here in factory config |
| J19 | 12-pin header | GNSS UART @3.3V, mag I2C @3.3V, 5V out, RC UART, spare I2C |
| SW1 | momentary button | force Fastboot |
| SW2 | switch | EDL (factory flashing) — leave OFF |

Power: 5V ±5% (≈4.75–5.25V) on J4; VOXL Power Module is set to 5.08V no-load; needs ~6A in-rush
support at power-on — [ModalAI docs](https://docs.modalai.com/voxl2-connectors/)

#### VOXL 2 Mini (M0104) connectors — [ModalAI docs](https://docs.modalai.com/voxl2-mini-connectors/)
| Des. | Type | Function |
|---|---|---|
| J1 | 4-pin | power input, **3.8V nominal, 1S range 3.3–4.25V**, + I2C @3.8V power monitor |
| J2 | 2-pin | 5V fan out, PWM |
| J3 | 10-pin | USB3 port with 5V VBUS out |
| J4 | 4-pin | Linux debug console @3.3V, debug kernel builds only |
| J6 / J7 | 60-pin B2B | Camera groups 0/1 — 2× 4-lane MIPI CSI each, CCI, rails 1.05–5V; J6 adds SPI, J7 adds I2C |
| J9 | USB-C | ADB, OTG/host, **no DisplayPort** |
| J10 | 8-pin | **UART by default**, SPI only with a kernel rebuild; 32kHz clock option; 3.3V CMOS; GPI_40, GPO_41, GPI_46, interrupt GPI_64 |
| J19 | 12-pin | ESC / GNSS / mag / RC — UARTs + I2C @3.3V, 5V, switchable 3.3V RC power |

Mini power budget: J2 + J3 + J19 outputs share a **900mA total** limit — it cannot supply 1A on
every connector at once. Known Mini hardware issues: USB3 SuperSpeed TX lines lack AC-coupling
caps (links may drop to USB2; fix planned for a future spin; workaround = add radial caps to
MCBL-00022-2 TX lines); some Ethernet devices enumerate as USB3 but run ~8–12 Mbps, cured by
removing the USB3 wires or using MCBL-00080 (restores USB2 HS 480 Mbps) — [ModalAI docs](https://docs.modalai.com/voxl2-mini-connectors/)

### Inferences
- The Mini has **no 60-pin legacy B2B (J3) and no 120-pin J5**, so the M0213 WiFi add-on's J1
  60-pin QTH B2B cannot mate to a Mini the way it does on full VOXL 2 — despite the M0213 page
  listing both as compatible. Treat "compatible with VOXL 2 Mini" as needing a cable/adapter.
- SLPI/DSP: the matrix row "Embedded flight controller … on the Sensors DSP" is the only published
  SLPI difference — Mini supports PX4 **or** ArduPilot on SLPI, full VOXL 2 is PX4-only. The DSP
  hardware itself is the same QRB5165 Hexagon/SLPI on both.

### Gaps
- No Ethernet connector exists on either board in the published connector lists; Ethernet is only
  ever USB-attached (`usb-eth0`, added in SDK 1.6.3 per a ModalAI staff forum reply —
  [forum.modalai.com thread 5099](https://forum.modalai.com/topic/5099/station-mode-issue-with-voxl-suite-1-6-3.md)).
- Thermal design (heatsink part numbers, fan requirements, throttling thresholds) was not found on
  any page fetched. The only thermal-adjacent data is the J2 fan header on both boards and the
  0.5–8W power envelope.
- Board dimensions are not on the connector pages; the feature matrix is the cited source. The
  VOXL 2 "Mechanical Drawings" page was not fetched.

---

## Q4. Starling 2 Max production revisions, and the WiFi change

### Takeaway
There are at least **four airframe revisions V1–V4** in the SKU string, plus an R1/R2 split in the
published CAD. The WiFi difference the user sees is an **airframe/accessory-level change, not a
compute-board change**: older units shipped a USB3.0/UART expansion adapter (M0151) with an
external **Alfa AWUS036EACS USB dongle**; newer units ship a **WiFi adapter board built around the
Bots Unlimited SP-01-100 "Sparrow" LGA module** (the M0213 VOXL 2 WiFi Addon) that bolts to the
VOXL 2's 60-pin legacy B2B connector. Both still run on a full-size VOXL 2.

### Cited Findings
- Starling 2 Max 3D STEP files are published per revision: **R1 = April–September 2024, R2 = October 2024 onward** — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/)
- SKU airframe revisions seen in the wild / in store templates: `V1`, `V2` (`MRB-D0012-4-V2-C28-T8-M11-X0`), `V3` (`D0012-4-V3-CXX-MXX-TX`), `V4` (`D0012-4-V4-CXX-MXX-TX`) — [forum.modalai.com thread 5246](https://forum.modalai.com/topic/5246/starling-2-max-not-detecting-wifi-hardware.md); [ModalAI store](https://www.modalai.com/products/starling-2-max-replacement-parts)
- **Frame/motor split at V4:** "the two carbon fiber frames are not interchangeable." V1–V3 use carbon frame `M10000929` (T-Motor version, smaller motor-mount spacing, black-and-gold motors, V3 gold motor `M10000073` 2203.5 1500kV, feet `M10000868`); V4 uses carbon frame `M10001459` (wider spacing), black motor `M10001367` 2204 1500kV, feet `M10001460` — [ModalAI store](https://www.modalai.com/products/starling-2-max-replacement-parts)
- **The WiFi/radio change, from a buyer with both vintages:** a newly received Starling 2 Max shipped with "a new ELRS receiver (M0184) and a Wi-Fi adapter board built around the Sparrow LGA Long Range Wi-Fi Module", "as opposed to my other relatively older Starling 2 Max units that came with the USB3.0 / UART Expansion Adapter (M00151) with AWUS036EACS and ELRS Nano RX." The same poster could not find the new WiFi board documented on docs.modalai.com at the time — [forum.modalai.com post 25386](https://forum.modalai.com/post/25386)
- The published datasheet still lists the datalink as **Alfa Network AWUS036EACS, FCC ID 2AB878811** — i.e. the datasheet documents the older configuration — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/)
- The datasheet's CEC table lists radio options "T8 = M0184 (USA)" and "T9 = Ghost Atto Rx (Croatia)", with handsets "T8 iFlight Commando 8 Rx (China)" / "T9 Ghost Atto Rx" — so the `T#` SKU field is the radio — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/)
- Camera configs: **C28** = dual IMX412 + dual AR0144; **C29** = C28 plus a ToF sensor — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/)
- Some SKUs ship with **no WiFi at all**: a `MRB-D0012-4-V2-C28-T8-M11-X0` owner found no wireless interface; ModalAI staff identified the device present as "a Microhard modem, not a WiFi dongle" — [forum.modalai.com thread 5246](https://forum.modalai.com/topic/5246/starling-2-max-not-detecting-wifi-hardware.md)
- Another buyer comparing V2 and V4 SKUs asked ModalAI directly whether WiFi hardware differs between them and whether "some units use an external Alfa USB adapter while others use an onboard module" — the thread shows no official answer — [forum.modalai.com thread 5246](https://forum.modalai.com/topic/5246/starling-2-max-not-detecting-wifi-hardware.md)
- Starling 2 Max airframe specs (unchanged across revisions as published): 566g take-off weight, 500g payload, ~930g AUW, 15 m/s cruise / 20 m/s dash, 15 m/s gust tolerance, 4000m MSL ceiling, ~55 min (Amprius) or ~40 min (Li-Ion), 180mm tri-blade props, ModalAI 4-in-1 Mini ESC, UBlox M10 GPS, 2S Sony VTC6 3000mAh (two 2S packs in series, 16.8V max), 512mm diagonal / 450×380×120mm — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/)

### Inferences
- The user's observation maps as: **OLDER unit = V1–V3-era build, M0151 USB3.0/UART expansion
  adapter, USB WiFi (Alfa AWUS036EACS from the factory; the user has substituted a TP-Link Archer
  TX20U Nano / RTL8852BU) → `wlan0`.** **NEWER unit = later build with the Sparrow-based WiFi
  adapter board (M0213 family) on the VOXL 2 legacy B2B → a non-USB netdev.**
- Because M0213's predecessor is M0141, there may be *three* WiFi generations in the field
  (USB dongle → M0141 → M0213). A unit could carry M0141 rather than M0213.
- The "integrated WiFi on the VOXL board" the user describes is almost certainly this B2B-mounted
  daughterboard, not silicon on the VOXL 2 itself — ModalAI's own feature matrix says built-in
  WiFi: **No** for both VOXL 2 and VOXL 2 Mini.

### Gaps
- **No official ModalAI changelog of Starling 2 Max revisions exists in public docs.** The R1/R2
  CAD split and the V1–V4 SKU field are the only published revision markers, and neither is
  cross-referenced to the WiFi change. The WiFi-generation story rests on a single (detailed,
  self-consistent) customer forum post.
- Which airframe revision first shipped Sparrow is unconfirmed.
- Whether the Sparrow board in Starling 2 Max is literally M0213 or an unreleased sibling is
  unconfirmed — the buyer who received one said it was undocumented on docs.modalai.com at the
  time, and the M0213 doc page itself still has a "TODO" for the board outline.

---

## Q5. Identifying the board and revision from a shell on the drone

### Takeaway
`voxl-version` is the one command that matters: it prints `hw platform:` (M0054 / M0154 / M0104),
`mach.var:` (which dash-revision), and `SKU:` (the whole airframe config string). The same data is
readable raw from two sysfs files exported by the `voxl-platform-mod` kernel driver.

### Cited Findings
- `voxl-version` example output fields — [ModalAI docs](https://docs.modalai.com/voxl-version/):
  ```
  system-image: 1.8.2-M0054-14.1a-perf
  kernel:       #1 SMP PREEMPT, Mon Apr 13 2026, 4.19.125
  hw platform:  M0054
  mach.var:     1.2.0
  SKU:          MRB-D0014-4-V1-C27-T7
  voxl-suite:   1.7.0
  Packages:     repo http://voxl-packages.modalai.com/
                path ./dists/qrb5165/sdk-1.7/binary-arm64/
                last updated 2026-06-02 12:58:23
                (then a list of libs: libmodal-cv 0.3.1, libmodal-json 0.4.3, …)
  ```
  Note the **system-image string itself embeds the board part number** (`1.8.2-M0054-14.1a-perf`),
  and the `SKU:` line is the airframe SKU — on the user's aircraft this should start `MRB-D0012-…`.
- Flags: `-q` / `--quiet` suppresses the package list; `-j` / `--json` emits JSON — [ModalAI docs](https://docs.modalai.com/voxl-version/)
- `voxl-suite` is the SDK version; the system image is separate firmware and ModalAI recommends running matched pairs — [ModalAI docs](https://docs.modalai.com/voxl-version/)
- **M0054 dash-revision table** — [ModalAI docs](https://docs.modalai.com/m0054-versions/):

  | HW version | SIP cover silkscreen | Min SDK | `mach.var` | platform-id variant |
  |---|---|---|---|---|
  | M0054-1 | **"QRB5165M"** | any | `1.0` | `m0054`, VOXL2 `(1 0 0)` |
  | M0054-2 | **"QSM8250"** | 1.1.3+ | `1.2` | `m0054`, var02 "VOXL2 - 8250" `(1 2 0)` |

  A third variant `var01` "VOXL2 - no combo mode J6/J8" `(1 1 0)` is listed without a stated
  hardware mapping.
- Raw sysfs, populated by the `voxl-platform-mod` kernel driver:
  `/sys/module/voxl_platform_mod/parameters/machine` and
  `/sys/module/voxl_platform_mod/parameters/variant` — [ModalAI docs](https://docs.modalai.com/m0054-versions/)
- Each M0054 revision needs its own kernel and TrustZone config; the SDK installer is supposed to
  auto-detect, and the versions page exists for when it does not — [ModalAI docs](https://docs.modalai.com/m0054-versions/)
- ModalAI staff guidance: always include `voxl-version` output (and your SDK version) when asking
  for help on the forum — [ModalAI docs](https://docs.modalai.com/m0054-versions/)
- WiFi-side identification: `/data/misc/wifi/wpa_supplicant.conf` holds the generated `ssid`/`psk`;
  the same directory contains `station_interface` and `station_band` files that record which
  interface and band were selected — [forum.modalai.com thread 5099](https://forum.modalai.com/topic/5099/station-mode-issue-with-voxl-suite-1-6-3.md)
- `voxl-wifi` is the configuration tool; it requires a reboot after changes. Modes include
  `voxl-wifi station <ssid> <password>`, `voxl-wifi softap <ssid> [password]` (2.4GHz, ch6,
  default password `1234567890`), `voxl-wifi softap5 <ssid> [password]` (5GHz, ch149), and a
  factory mode that sets SSID `VOXL-{MAC}` — [ModalAI docs](https://docs.modalai.com/voxl-2-wifi-setup/); [ModalAI docs (0.9 era)](https://docs.modalai.com/voxl-wifi-0_9)
- On SDK 1.6.3, `voxl-wifi` logs the interface it picked, e.g. `Detected WiFi interface: wlan0` and
  `NetworkManager not installed, using legacy wpa_supplicant/hostapd` — a direct way to see which
  netdev the tool believes it owns — [forum.modalai.com thread 5099](https://forum.modalai.com/topic/5099/station-mode-issue-with-voxl-suite-1-6-3.md)
- For a dongle that produces no interface, ModalAI staff direct users to unplug/replug the adapter
  with the board powered and read `dmesg`; `lsusb` shows the USB controller even when no netdev is
  created — [forum.modalai.com thread 5246](https://forum.modalai.com/topic/5246/starling-2-max-not-detecting-wifi-hardware.md); [forum.modalai.com](https://forum.modalai.com/topic/2823/device-wlan0-does-not-exist)
- ModalAI reply on a missing dongle netdev: the driver should already ship on VOXL 2, but an older
  system image may lack it; try `insmod` of the module manually and check `ifconfig` for `wlan0`;
  upgrade to platform release 1.3.1+ — [forum.modalai.com](https://forum.modalai.com/topic/2823/device-wlan0-does-not-exist)
- A board with only a Microhard modem will have no `wlan0` at all — expect `usb0` or `eth0`
  instead — [forum.modalai.com thread 5246](https://forum.modalai.com/topic/5246/starling-2-max-not-detecting-wifi-hardware.md)

### Suggested bench procedure (assembled from the above)
```sh
voxl-version                                        # hw platform, mach.var, SKU, system-image
voxl-version -j                                     # same, machine-readable
cat /sys/module/voxl_platform_mod/parameters/machine
cat /sys/module/voxl_platform_mod/parameters/variant
ls /sys/class/net ; ip -br link                     # wlan0 (USB) vs mlan0 (B2B module) vs usb0/eth0
lsusb                                               # Realtek RTL8852BU present => USB dongle unit
dmesg | grep -iE 'wlan|mlan|rtl88|usb .*new|mwifiex|moal'
cat /data/misc/wifi/station_interface               # which iface voxl-wifi targeted
cat /data/misc/wifi/wpa_supplicant.conf
systemctl status 'wpa_supplicant@*'                 # @wlan0 vs @mlan0
```

### Gaps
- **`voxl-platform` was not confirmed.** The `m0054-versions` page refers to the variant tuple as
  the "platform-id", which strongly implies a `voxl-platform` / `voxl-platform-id` helper exists in
  `voxl-utils`, but no fetched page documents the command or its output. Verify on the drone.
- **`/etc/version` and `/etc/modalai/` were not documented on any page fetched.** ModalAI's
  `voxl-version` page does not mention them. Their contents (and whether `/etc/modalai/` holds a
  SKU or hw-id file) need to be checked on the hardware.
- No published `mach.var` value for M0104/M0204 (Mini) was found, so the Mini's expected
  `voxl-version` shape is unknown. Not needed for Starling 2 Max, which is full-size VOXL 2.
- No command was found that reports the *airframe* revision (V1–V4) beyond the `SKU:` string —
  and the SKU string is a flashed/provisioned value, so a reflashed or re-provisioned unit could
  report something stale. Treat `SKU:` as strong but not conclusive evidence.

---

## Q6. Physical silkscreen and label locations

### Takeaway
The one documented physical marking is on the **SIP (system-in-package) cover of the QRB5165**:
`QRB5165M` means M0054-1, `QSM8250` means M0054-2. No ModalAI page found documents where the
`M00xx` part number itself is silkscreened, or what the serial/label sticker looks like.

### Cited Findings
- "M0054-1 | Any | 'QRB5165M' printed on SIP cover" and "M0054-2 | SDK 1.1.3+ | 'QSM8250' printed on SIP cover" — [ModalAI docs](https://docs.modalai.com/m0054-versions/)
- A forum thread exists specifically on the QRB5165M vs QSM8250 distinction — [forum.modalai.com thread 3217](https://forum.modalai.com/topic/3217/qrb5165m-vs-qsm8250.md)
- Board-level silkscreen that *is* documented is connector designators (J1…J19, SW1, SW2, H1/H2 mounting holes, S1 fastboot switch on M0213) — [ModalAI docs](https://docs.modalai.com/voxl2-connectors/); [ModalAI docs](https://docs.modalai.com/voxl2-mini-connectors/); [ModalAI docs](https://docs.modalai.com/m0213/)
- The M0213 doc page contains no images and no silkscreen detail; its board outline is marked TODO — [ModalAI docs](https://docs.modalai.com/m0213/)

### Inferences
- Because M0054-1 and M0154-1 are the same design with refreshed passives, the **SIP cover marking
  does not distinguish M0054 from M0154** — it only distinguishes the `-1` (QRB5165M) from the `-2`
  (QSM8250) silicon generation. The M0054-vs-M0154 call has to come from `voxl-version` or from a
  board-edge silkscreen/label that ModalAI has not documented.

### Gaps
- **Requires physical inspection:** location of the `M0054-x` / `M0154-x` silkscreen on the PCB,
  the format of the serial-number label, and whether a date code is printed. None of this is in
  ModalAI's public docs.
- **Requires physical inspection:** the identity of the WiFi daughterboard in the newer airframe —
  read the silkscreen on the board that mates to VOXL 2 J3 and look for `M0213`, `M0141`, or an
  undocumented part number, plus the `SP-01-100` marking on the 22×22mm LGA module.

---

## Q7. WiFi chipset on the newer "integrated WiFi" boards, and the interface name

### Takeaway
The newer Starling 2 Max WiFi board is built on the **Bots Unlimited SP-01-100 "Sparrow"** LGA
module — dual-band 802.11ac, 2×2 MIMO, 500mW, BT 5.3 (BT not supported in the SDK). I could
**not** confirm the silicon inside Sparrow, and I found **no ModalAI source anywhere that uses the
interface name `mlan0`** — every ModalAI doc and forum post found says `wlan0`.

### Cited Findings
- M0213 VOXL 2 WiFi Addon is "built around the Bots Unlimited SP-01-100 'Sparrow' LGA module", dual-band 802.11ac 2×2 MIMO, Bluetooth 5.3 listed but "not supported in the current SDK"; module package is 22×22mm LGA — [ModalAI docs](https://docs.modalai.com/m0213/)
- M0213 connectors: **J1 = 60-pin QTH-030-01-X-D-A legacy B2B to VOXL 2**; J3 = 12-pin SM12B-GHS-TB legacy peripheral (SPI, I2C, UART, 2 spare GPIO @3.3V); J2 = BT U.FL antenna; J4 = WiFi path A U.FL; J5 = WiFi path B U.FL; S1 = fastboot switch; H1/H2 mounting holes — [ModalAI docs](https://docs.modalai.com/m0213/)
- Compatible with VOXL 2 and VOXL 2 Mini per the doc page — [ModalAI docs](https://docs.modalai.com/m0213/)
- ModalAI classes M0213 as a "500mW dual-band WiFi radio targeted for UAS use" — [ModalAI wifi-modems](https://docs.modalai.com/wifi-modems/)
- Staff: M0213 is a direct replacement for M0141; its 12-pin J3 matches the J5 connector in the USB2 Type-A breakout docs; "the M0213 board is not meant to plug into any other board than VOXL 2 directly" (so it cannot be stacked with the 5G modem add-on) — [forum.modalai.com thread 5309](https://forum.modalai.com/topic/5309/m0213-wifi-board-pinout-and-availability.md)
- A user running M0213 reported "much better signal strength and better multi-mesh access point transition than an ALFA dongle" — [forum.modalai.com thread 5309](https://forum.modalai.com/topic/5309/m0213-wifi-board-pinout-and-availability.md)
- On the USB-dongle side, ModalAI's guide states the VOXL 2 "by itself doesn't have Wi-Fi or a LAN port to keep the core size and weight low", and WiFi is added over USB via the M0078-2 USB Debug add-on or the M0090 PCIe/5G modem carrier, with a list of dongles tested on system image 1.1.2+ — [ModalAI beta docs](https://beta-docs.modalai.com/voxl2-wifidongle-user-guide)
- "the voxl's linux kernel is built with very limited wifi drivers" — other dongles may not work — [forum.modalai.com thread 5246](https://forum.modalai.com/topic/5246/starling-2-max-not-detecting-wifi-hardware.md)
- Dongles named as working in ModalAI material/forums: Alfa AWUS036EACS / AWUS036ACS, TP-Link AC600 — [ModalAI docs](https://docs.modalai.com/starling-2-max-datasheet/); [forum.modalai.com thread 5099](https://forum.modalai.com/topic/5099/station-mode-issue-with-voxl-suite-1-6-3.md)

### Inferences
- `mlan0` (with its usual companion `uap0`) is the canonical netdev naming of the
  **NXP / Marvell `mwifiex` / `moal` driver family**, not of Qualcomm's `wlan0` or of the Realtek
  `rtl8852bu` out-of-tree driver. Combined with "802.11ac 2×2 MIMO + Bluetooth 5.3" in a 22×22mm
  LGA package, the strong hypothesis is that Sparrow wraps an **NXP (ex-Marvell) 88W-series
  combo chip** — e.g. 88W9098-class silicon. **This is an inference from driver-naming convention
  only; I found no datasheet or teardown confirming it.**
- Consistent with the above: the user's older unit presenting `wlan0` is the RTL8852BU USB dongle
  (Realtek drivers name interfaces `wlan0`), and the newer unit presenting `mlan0` driven by
  `wpa_supplicant@mlan0` is the B2B WiFi daughterboard with a Marvell/NXP-lineage driver.
  `wpa_supplicant@<iface>` templated units are also how ModalAI's legacy (non-NetworkManager)
  WiFi path is wired up.
- Because M0213 occupies the VOXL 2's 60-pin legacy B2B (J3) and that connector is also what the
  LTE/Microhard/5G carriers use, a unit cannot carry both M0213 and a legacy-B2B modem board.

### Gaps
- **Bots Unlimited SP-01-100 "Sparrow" silicon is unconfirmed.** A direct search for the part
  returned nothing — no vendor page, no datasheet, no FCC filing in the results. The chipset,
  its Linux driver name, and the netdev name it creates all remain unverified from sources.
  Checking `dmesg`, `ethtool -i mlan0`, `lsmod`, and `readlink /sys/class/net/mlan0/device/driver`
  on the newer drone would settle it in one step.
- **No ModalAI source uses `mlan0`.** Either it is undocumented, or the user's newer unit carries
  a module ModalAI has not written up. The user's observation should be treated as ground truth
  here; the docs simply have not caught up (consistent with the buyer who reported the new WiFi
  board being absent from docs.modalai.com).
- Antenna/RF details (gain, which U.FL path is which) and the FCC ID of the Sparrow-based board
  were not found.

---

## Cross-cutting: what the user should actually do at the bench

### Takeaway
Three checks separate the two aircraft definitively, two from software and one from a screwdriver.

### Cited Findings / procedure
1. `voxl-version` on each: compare `hw platform:` (`M0054` vs `M0154`), `mach.var:` (`1.0` = `-1`
   silicon, `1.2` = `-2` 4-camera-max silicon) and the `SKU:` string's `V#` field — [ModalAI docs](https://docs.modalai.com/voxl-version/); [ModalAI docs](https://docs.modalai.com/m0054-versions/)
2. `ip -br link` + `lsusb` + `dmesg`: a Realtek RTL8852BU in `lsusb` with `wlan0` = USB-dongle
   airframe; `mlan0` with nothing matching in `lsusb` = B2B WiFi daughterboard airframe — [forum.modalai.com thread 5246](https://forum.modalai.com/topic/5246/starling-2-max-not-detecting-wifi-hardware.md)
3. Open the top plate and look at what sits on VOXL 2's J3 60-pin legacy B2B: a USB3.0/UART
   Expansion Adapter (M0151) feeding an external dongle = older build; a small board with a 22×22mm
   LGA can marked `SP-01-100` and two or three U.FL antenna pigtails = Sparrow/M0213-class build.
   Also check the RC receiver: ELRS Nano RX = older, Gemini M0184 = newer — [forum.modalai.com post 25386](https://forum.modalai.com/post/25386); [ModalAI docs](https://docs.modalai.com/m0213/)
4. Frame check for V4 vs V1–V3: V4 has **wider motor-mount spacing** and **black** 2204 1500kV
   motors; V1–V3 have narrower spacing and **black-and-gold** 2203.5 1500kV T-Motor units — [ModalAI store](https://www.modalai.com/products/starling-2-max-replacement-parts)

### Inferences
- If both units report `hw platform: M0054`, the compute boards are the same generation and the
  entire observed difference is accessory-level (WiFi board + RC receiver), which matches the
  forum evidence better than a board swap.

### Gaps
- The user's PX4 v1.14 / px4_msgs arming-state mismatch and ROS 2 Foxy stack are software-side and
  orthogonal to board ID; nothing in the sources ties a px4_msgs version to a board revision.
- ModalAI publishes no serial-number lookup tool, so a definitive revision answer for a specific
  aircraft ultimately means emailing ModalAI support with the serial — as staff repeatedly steer
  forum users to do.

# Active cooling for the VOXL 2 on a Starling Max 2 (indoor mocap, Singapore ~30 °C ambient)

Scope note: all figures below come from ModalAI documentation and the ModalAI support forum
(staff replies are flagged as such). Qualcomm's own QRB5165 thermal datasheet could not be
located publicly — see Gaps under Q1. Nothing here was measured on the user's airframe.

## Q1 — What are the VOXL 2's documented thermal limits?

### Takeaway
ModalAI has no published junction-temperature table; the operative number staff repeat is
**~95 °C, where the SoC's thermal control loop begins gradually reducing core frequencies**.
Throttling is explicitly described by ModalAI as *normal and by design*, not a fault — the
QRB5165 cannot run at full clock indefinitely without cooling. 60–75 °C is stated by staff to
be unremarkable for this board.

### Cited Findings
- "The VOXL2 SoC is not designed to run at full power for a long time without cooling. The maximum operating temperature is around 95 deg C, at which point, the CPU will begin automatically throttling (reducing) operating frequency." — ModalAI staff — [ModalAI forum, VOXL2 thermal throttling thread](https://forum.modalai.com/topic/5103/voxl2-thermal-throttling-and-heat-dissipation-methods)
- "It is normal for the CPU to throttle. It cannot run full speed indefinitely without turning down." — ModalAI staff — [ModalAI forum](https://forum.modalai.com/topic/1271/cpu-overheating-on-voxl-2)
- Staff reply to a user seeing 60 °C at idle: "60C is not an issue for embedded devices", throttling limit "around 95C" — [ModalAI forum, temperature issue with voxl 2](https://forum.modalai.com/topic/4484/temperature-issue-with-voxl-2.md)
- Staff (Alex Kushleyev) on a user whose Position mode dropped out above 75 °C: "75C is normal, the CPU will not start throttling itself until about 95C"; with `voxl-set-cpu-mode perf` "all cores will be fixed to max frequency, with thermal management engaging only above about 95 °C" — [ModalAI forum](https://forum.modalai.com/post/18723)
- **Conflicting threshold figures.** One staff post gives "about 95C is when the temperature control loop will kick in and start reducing the maximum core frequencies (gradually)"; an earlier staff reply gives "about 90C....+/- a few degrees depending on its prediction algo and hysteresis settings" — [ModalAI forum, CPU Temperature Throttling](https://forum.modalai.com/post/18723) / [related post](https://forum.modalai.com/post/18776)
- A VOXL 1-era staff post says the system tries to stay under 100 °C and "beyond that the PMIC will start removing power and shutting off cores" — [ModalAI forum](https://forum.modalai.com/post/3941). Treat as VOXL 1, not confirmed for VOXL 2.
- The `cpu_stats_t` struct published by `voxl-cpu-monitor` carries a flag set when **max core temperature exceeds 90 °C**, and a separate overload flag at 80 % total CPU — [ModalAI docs, voxl-cpu-monitor](https://docs.modalai.com/voxl-cpu-monitor-0_9/). This 90 °C software warning is distinct from the ~95 °C hardware throttle point.
- Heat source and the cooling bottleneck, per ModalAI staff: "It is certainly the QRB5165 module on Voxl 2 that will be the predominate power source"; "The LPDDR5 SDRAM tends to be the limiting factor. Although not the source of the heat, it sits above the CPUs so it is the most accessible for thermal dissipation." Board layout deliberately puts the B2B connectors J3/J5 on the secondary side "so that plug-in boards would not block airflow over the memory side." — [ModalAI forum, VOXL2 thermal management](https://forum.modalai.com/topic/2233/voxl2-thermal-management)
- Power draw context from staff: "some nominal use cases only need 3-4W, and some more AI intensive with multiple cameras pull 7-8W on the voxl2 board alone"; the power module is rated 30 W total system power — [ModalAI forum, VOXL2 Max Power Draw](https://forum.modalai.com/topic/2031/voxl2-max-power-draw.md)
- ModalAI's own thermal design page states airflow is "the single biggest factor for improved thermal performance" — [docs.modalai.com, VOXL 2 thermal performance](https://docs.modalai.com/voxl2-thermal-performance/)

### Inferences
- The absence of an official junction-temp / thermal-resistance table means there is no way to compute a margin analytically for 30 °C ambient. The only defensible approach is empirical: log core temps during a representative hover and see where they sit relative to 90/95 °C.
- The 7–8 W figure for an AI/multi-camera workload is the realistic VOXL 2-only dissipation to design around; a 25 mm fan is more than adequate for that wattage *if* air actually reaches the SIP.
- Because the DDR stack sits on top of the CPU die and is the thermal bottleneck, cooling effort should be aimed at the memory-side face of the SIP, not at the board generally.

### Gaps
- No public Qualcomm QRB5165 datasheet with Tj max, thermal resistance (θJA/θJC) or case-temperature limits was found. Searches returned only unrelated parts (TI LM5165). ModalAI has published no VOXL 2 skin-temperature limit either.
- No ModalAI-published ambient-vs-board-temperature curve or sustained-load thermal test data. The `voxl2-thermal-performance` page is qualitative design guidance only — no numbers at all.
- The 90 °C vs 95 °C discrepancy is unresolved; it may be the difference between the `cpu_stats_t` warning flag and the actual kernel thermal-zone trip point.
- VOXL 2 operating-temperature range is not stated on the Starling 2 Max datasheet, and `docs.modalai.com/voxl2-datasheet/` returns 404.

## Q2 — Does ModalAI sell or recommend cooling accessories?

### Takeaway
**A fan: yes. A heatsink: no.** ModalAI sells a 25 × 25 mm 5 V "VOXL Cooling Fan"
(Sunon **MC25060V1-000U-A99**, mating connector **SHR-02V-S**) that plugs straight into the
VOXL 2 fan header, and they fit it to their own Flight Deck / m500 / Sentinel builds. As of
March 2026 ModalAI explicitly stated they have **no heatsink recommendation** for VOXL 2 and no
thermal plate product comparable to the Qualcomm RB5 dev-kit plate.

### Cited Findings
- "we sell a very convenient small 25mm x25mm 5V fan on our website … that will plug directly into Voxl, Voxl-Flight, Voxl2, and Voxl2-Mini." Product URL given as `https://www.modalai.com/collections/accessories/products/voxl-cooling-fan` — [docs.modalai.com, VOXL 2 thermal performance](https://docs.modalai.com/voxl2-thermal-performance/)
- Part number and connector, from staff: "Cooling fan (MC25060V1-000U-A99) with connector (SHR-02V-S) ready to be used with VOXL J6. This is what we install on the VOXL Flight Deck and m500." For VOXL 2 the same fan "can connect to VOXL2 J2." Staff also note the connector is a separate part "so you may find the fan cheaper elsewhere." — [ModalAI forum, CPU Overheating on Voxl 2](https://forum.modalai.com/topic/1271/cpu-overheating-on-voxl-2)
- Same thread: ModalAI use this fan when building VOXL 2 into assemblies such as the **Sentinel** reference drone — [ModalAI forum](https://forum.modalai.com/topic/1271/cpu-overheating-on-voxl-2)
- MC25060V1-000U-A99 is a **Sunon** part: 25 × 25 × 6.9 mm, 5 V, ~13 000 RPM, ~3.0 CFM, 0.22 inH2O static pressure, ~31 dB, **~5.0 g** — distributor listings — [IBS Electronics](https://ibselectronics.com/products/sunon-fans/mc25060v1-000u-a99); Newegg reseller listings quote ~USD 16–28. Variant suffixes (-A99, -F99, -U-A99) differ in bearing/lead style — verify before buying.
- Official "no heatsink" position (Alex Kushleyev, 2026-03-18), replying to a user whose enclosed VOXL 2 throttled at 95 °C and who asked about the RB5 thermal plate / Thundercomm heatsink-fan: "We do not have a heat sink recommendation for VOXL2, however you can try off-the-shelf components, just be careful not to apply excessive mechanical stress to the QRB5165 SIP while mounting the heat spreader to it." He also offered to help reduce system load — [ModalAI forum, topic 5103](https://forum.modalai.com/topic/5103/voxl2-thermal-throttling-and-heat-dissipation-methods)
- ModalAI's design page warns against a bare heatsink: without airflow "the heatsink will effectively become a large thermal capacitor", delaying throttling but sustaining the degradation longer; if used, pair it with a fan and keep it passive and electrically non-conductive to avoid EMC problems — [docs.modalai.com](https://docs.modalai.com/voxl2-thermal-performance/)
- EMC guidance from the same page: "The biggest thing to manage is unplanned radiators or antennas"; "Do not use grounded or metal hardware (screws/washers/spacers)"; "Do not lay cables directly above or over any PCB, IC, or power circuit." — [docs.modalai.com](https://docs.modalai.com/voxl2-thermal-performance/)
- No ModalAI thermal pad, cooling plate or heat-spreader part number exists in any source found. The topic-5103 thread mentions no thermal interface material at all — [ModalAI forum](https://forum.modalai.com/topic/5103/voxl2-thermal-throttling-and-heat-dissipation-methods)

### Inferences
- The ~5 g fan mass is negligible against a 566 g take-off weight and 500 g payload capacity, so mass is not the objection to fitting one; mounting, vibration and airflow effectiveness are.
- ModalAI's "no mechanical stress on the SIP" warning is the real constraint on any DIY heatsink: the QRB5165 is a system-in-package soldered to the board, and spring-clip or screw-down coolers risk cracking solder joints under flight vibration. Adhesive thermal tape is the lower-risk attachment.
- Because ModalAI ships the Sentinel with this fan but apparently not the Starling 2 / 2 Max, the Starling's thermal design assumes prop-wash is the cooling mechanism.

### Gaps
- Could not load `modalai.com/collections/accessories/products/voxl-cooling-fan` directly to confirm current price, stock, or whether a VOXL 2-ready cable is included; the docs URL is quoted from ModalAI's own page.
- Whether a Starling 2 Max ships with the fan fitted, or whether J2 is physically reachable on an assembled Starling 2 Max, is **not documented**. The Starling 2 hardware quickstart says nothing about fans, airflow, VOXL 2 orientation or J2. One older forum report (for the original Starling) says a frame screw hole sits directly over the fan connector, obstructing it — [ModalAI forum](https://forum.modalai.com/post/15692) (thread partially deleted; could not verify in full, and it may not apply to the Max).

## Q3 — What do real users report? Is throttling real or theoretical?

### Takeaway
**Real, and reported specifically on Starling 2 Max hardware.** The single most relevant data
point: a Starling 2 Max owner measured **~104 °C CPU / ~98 °C GPU at 96 % CPU utilisation while
sitting idle on a desk**, and a desk fan dropped it to ~80 °C. Crucially, in almost every thread
the root cause ModalAI identifies is **software load (camera server, VIO, portal), not inadequate
hardware cooling** — and in that Starling 2 Max case the heat was associated with an
**accelerometer-bias preflight failure**, i.e. a flight-safety symptom.

### Cited Findings
- **Starling 2 Max, 2026-07-21 (user "jk"):** ~104 °C CPU idle on a table; desk fan → ~80 °C. Log shows CPU 102–105 °C, GPU ~98 °C, 96 % total CPU utilisation, flags "CPU OVERHEAT CRIT" and "CPU OVERLOAD WARN". Top processes: `voxl-camera-server` ~184 %, `voxl-qvio-server` ~96 %, `px4` ~90 %. Also seeing "Preflight Fail: High Accelerometer Bias" and "Preflight Fail: Yaw Estimate Error". — [ModalAI forum, Questions on Starling 2 Max](https://forum.modalai.com/topic/5330/questions-on-starling-2-max.md)
- Staff reply (Eric Katzfey, same day): the high temperatures **may be causing the accelerometer bias error**; recommended a fan blowing on the VOXL 2 board whenever it sits on the desktop during development; later recommended **recalibrating the IMU with airflow over the unit** and testing `EKF2_EV_CTRL=0` to isolate the yaw error. No staff statement that 104 °C is normal. — [ModalAI forum](https://forum.modalai.com/topic/5330/questions-on-starling-2-max.md)
- **Throttling during flight with a fan fitted:** a user reported "with the fan and the flight propellers running the temperatures seem to still reach 75 deg C and there is also throttling happening at some 100-500 millisecond differences", and that above 75 °C "the position mode starts to turn off automatically showing it isn't ready to fly even when the starling is in flight", slowing ROS message delivery. Staff response: 75 °C is normal and throttling starts ~95 °C, so the dropout likely has another cause; check per-core frequencies with `voxl-inspect-cpu`. — [ModalAI forum](https://forum.modalai.com/post/18723)
- **Enclosed VOXL 2 throttling at 95 °C** (the topic-5103 originator) — enclosure, not ambient, was the trigger — [ModalAI forum](https://forum.modalai.com/topic/5103/voxl2-thermal-throttling-and-heat-dissipation-methods)
- **Hot-ambient report:** a 2022 user running at ~34 °C ambient reported throttling; staff pointed to the VOXL cooling fan — [ModalAI forum](https://forum.modalai.com/topic/1271/cpu-overheating-on-voxl-2). This is the closest published analogue to Singapore conditions.
- **Starling 2 "idle" at >80 °C:** staff found the board was not actually idle — `voxl-portal` was consuming CPU and `voxl-camera-server` "an excessive amount"; opening voxl-portal in a browser heated the board quickly. Staff asked which camera views were displayed and whether the board was enclosed. — [ModalAI forum](https://forum.modalai.com/topic/4484/temperature-issue-with-voxl-2.md)
- **Camera server at 88–90 °C:** user saw +30–40 °C on starting the camera server; staff said the camera server itself is probably not the main heat source, its frame consumers are, and recommended `top`, and disabling the mapper / OpenVINS / high-res image processing — [ModalAI forum](https://forum.modalai.com/topic/4484/temperature-issue-with-voxl-2.md)
- **voxl-px4 CPU usage:** a thread reports `voxl-px4` at 120–130 % CPU in voxl-inspect-services with cpu-monitor overheat warnings; no resolution shown — [ModalAI forum](https://forum.modalai.com/post/22485)
- **Boot-time shutdowns:** a user's board became unresponsive minutes after boot at ~50–55 °C; staff suspected software load and recommended putting a fan on the board just so it could boot long enough to debug — [ModalAI forum](https://forum.modalai.com/topic/1271/cpu-overheating-on-voxl-2)
- **DIY heatsink result (anecdotal):** a generic Raspberry Pi RAM heatsink (14 × 10 mm) plus a fan, mounted on the **underside of the SIP** (the side opposite where the main board connects to the Ethernet/USB board), "brought my temps down by at least 10-20 degrees even under intense load" (2026-04-13) — [ModalAI forum](https://forum.modalai.com/topic/5103/voxl2-thermal-throttling-and-heat-dissipation-methods)

### Inferences
- For this user's setup the question "is cooling needed?" is substantially a question about **what software is running**. The 104 °C Starling 2 Max case was at 96 % CPU with camera-server + QVIO + PX4 all active. Under OptiTrack mocap, QVIO/VIO and most camera pipelines are *not needed for navigation* — disabling them is likely worth more than any fan.
- The accelerometer-bias link is the most safety-relevant finding: ModalAI staff themselves attribute an IMU preflight failure to board temperature. On a flight controller, thermal drift of the IMU is a flight-quality issue, not just a performance one. If the user has seen intermittent accel-bias or yaw-estimate preflight failures, that is evidence for a thermal problem.
- Bench/desk operation is clearly the worst case — worse than hover, because hover at least supplies some downwash. Indoor mocap sessions typically involve long periods of the drone sitting armed/powered on the floor between flights; that is when 100 °C is plausible.
- Singapore's 28–33 °C ambient is close to the 34 °C case where throttling was reported, so the published anecdote does transfer.

### Gaps
- No published report of a **Starling 2 Max in hover** with logged temperatures. Everything above is bench/desk or non-Max hardware.
- Several relevant threads (post/15692 Starling fan attachment, the Starling 2 idle thread) are marked deleted in the cache and could not be read in full.
- No quantified comparison of hover-downwash cooling vs. still air on this airframe exists publicly.

## Q4 — How do you monitor and log temperature in software?

### Takeaway
`voxl-inspect-cpu` is the tool; it reads the `cpu_monitor` MPA pipe published at 1 Hz by the
`voxl-cpu-monitor` service. It has a **`-j` JSON mode**, which is the practical route to a flight
log — pipe it to a timestamped file on the drone. There is **no confirmed PX4/QGC path** for CPU
temperature on voxl-px4, and `voxl-logger` reportedly did *not* capture the temperature values.

### Cited Findings
- `voxl-cpu-monitor` "checks the current state of the CPU, GPU, and memory including statistics such as clock speeds, usage, and temperatures"; it is "the resource monitor for MPA" and "publishes data once per second to the `cpu_monitor` pipe" — [docs.modalai.com, voxl-cpu-monitor](https://docs.modalai.com/voxl-cpu-monitor-0_9/)
- Data is **not JSON on the wire**: it publishes a `cpu_stats_t` struct defined in `cpu_monitor_interface.h` (currently in the voxl-cpu-monitor package, eventually moving to `modal_pipe_interfaces.h`). Flags include max-core-temp > 90 °C and >80 % total CPU. — [docs.modalai.com](https://docs.modalai.com/voxl-cpu-monitor-0_9/)
- `voxl-list-pipes -t` shows the pipe under type `cpu_stats_t` — [docs.modalai.com](https://docs.modalai.com/voxl-cpu-monitor-0_9/)
- `voxl-inspect-cpu` flags: `-f/--full` (top CPU + memory consumers), **`-j/--json`** (JSON output), `-k/--json_human`, **`-t/--test` (print a single sample and exit)**, `-h` — [docs.modalai.com, voxl-inspect-cpu](https://docs.modalai.com/voxl-inspect-cpu)
- Sample `voxl-inspect-cpu` output format (per-core MHz / Temp / Util for cpu0–cpu7, a Total row, a 10 s average, GPU MHz/Temp/Util, memory use, plus "Governor:" and "Pitmode:" status lines) — [docs.modalai.com](https://docs.modalai.com/voxl-inspect-cpu). There is **no documented file/CSV option**; shell redirection of `-j` is the only route.
- If `voxl-inspect-cpu` shows no data, confirm the `voxl-cpu-monitor` systemd service is running (`voxl-inspect-services`) — [docs.modalai.com](https://docs.modalai.com/voxl-inspect-cpu)
- `voxl-perfmon` (Python, in `voxl-utils`) showed CPU/GPU usage and per-core temperatures but is **deprecated** in favour of `voxl-inspect-cpu` — [docs.modalai.com, Thermal and Performance](https://docs.modalai.com/thermal-and-performance)
- Staff first suggested `voxl-logger` to capture voxl-cpu-monitor output, but the user found the resulting logs contained only startup config and client connections — **no temperature or utilisation values**; staff then fell back to `voxl-inspect-cpu`. A later poster asked whether voxl-logger can record and replay this for post-flight graphs in voxl-portal; **the thread has no answer**. — [ModalAI forum, CPU Temperature Logging](https://forum.modalai.com/post/19919)
- `voxl-portal` "is just publishing data from the voxl-cpu-monitor service. If you open a terminal window and run `voxl-inspect-cpu` you can see the same data." — [ModalAI forum](https://forum.modalai.com/post/3947). voxl-portal shows it live only, with no export.
- Sysfs (documented by ModalAI for frequency, not temperature):
  - `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq` — current clock, the direct evidence of throttling
  - `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor` / `scaling_min_freq` / `scaling_max_freq`
  - `cat /sys/devices/system/cpu/cpu3/cpufreq/scaling_available_frequencies`
  - `cat /sys/class/kgsl/kgsl-3d0/devfreq/cur_freq` (GPU)
  — [docs.modalai.com, Thermal and Performance](https://docs.modalai.com/thermal-and-performance)
- PX4 does define an `OnboardComputerStatus` uORB/MAVLink message carrying board temperature and **per-core CPU temperatures in °C** (signed int8, so it cannot express >127 °C), plus fan speeds, type field 3 = compute node — [PX4 docs, OnboardComputerStatus](https://docs.px4.io/main/en/msg_docs/OnboardComputerStatus.html)

### Inferences
- **Recommended logging recipe** (all inference from the documented flags, not a published ModalAI procedure):
  `while true; do echo -n "$(date -Is) "; voxl-inspect-cpu -j -t; sleep 1; done >> /data/thermal_$(date +%F_%H%M).jsonl`
  run over SSH or as a background job during a full mocap session. Capture the whole session —
  power-on, idle-on-floor, arm, hover, land, idle — because the desk/idle phase is likely the hottest.
- Log **core frequency alongside temperature**. Temperature alone does not prove throttling; a
  core pinned below its max frequency while hot does. This is exactly what ModalAI staff advise.
- Record ambient temperature in the hangar at the same time, otherwise the data cannot be
  generalised across sessions.
- Because the PX4 path is unconfirmed, do not plan on seeing CPU temperature in QGC. Treat the
  on-board JSONL log as the authoritative record and correlate it with PX4 ulog timestamps afterwards.

### Gaps
- **Could not confirm whether voxl-px4 actually populates/streams `ONBOARD_COMPUTER_STATUS`.** No source found either way. This must be checked on hardware (QGC MAVLink Inspector, or `grep -r ONBOARD_COMPUTER_STATUS` in the voxl-px4 source). If it is streamed, QGC MAVLink Inspector would give a zero-effort in-flight temperature readout.
- The exact kernel thermal-zone sysfs paths that `voxl-cpu-monitor` reads are not documented anywhere found. On hardware, enumerate with `for z in /sys/class/thermal/thermal_zone*; do echo "$z $(cat $z/type) $(cat $z/temp)"; done` and look for QRB5165 zone names (e.g. `cpu-0-0`, `gpuss-*`, `ddr`). Unverified.
- `docs.modalai.com/voxl-cpu-monitor-0_9/` was reachable only via search snippet in this session (a later direct fetch 404'd); field-by-field `cpu_stats_t` contents are therefore not fully enumerated here.
- Whether `/etc/modalai/voxl-cpu-monitor.conf` exposes fan thresholds (as opposed to only `normal_cpu_mode`) is unconfirmed.

## Q5 — POWER: where to tap 5 V on a Starling Max 2

### Takeaway
**Use J2 on the VOXL 2 — it is a purpose-built 5 V fan header and the correct answer; do not
improvise.** Pin 1 is protected 5 V, pin 2 is a PWM-switched return limited to **~400 mA**.
The Sunon fan draws far less than that. Other 5 V taps exist (J19, camera B2B, the ESC main
power pads) but all carry real risk to the flight controller or sensors.

### Cited Findings
- **J2 — "5VDC Fan Control"**: board-side MPN `SM02B-SRSS-TB(LF)(SN)`, mating MPN `SHR-02V-S`, 2-pin right-angle cable header. Pin 1 = `VDC_5V_LOCAL`, "5V protected power output"; Pin 2 = "FAN RETURN (GND)", "Return limited to ~400mA". Summary line: "5V DC for FAN + PWM Controlled FAN-Return (GND)". — [docs.modalai.com, VOXL 2 Connectors](https://docs.modalai.com/voxl2-connectors/)
- General rating note on the same page: cable-connector power outputs are rated **1 A**, but "the system can't supply 1A on all connectors at once" — [docs.modalai.com](https://docs.modalai.com/voxl2-connectors/)
- Other 5 V sources on VOXL 2: **J19** (external sensors — GNSS/mag/RC/I2C) pin 1 `VDC_5V_LOCAL`; **J3** legacy B2B pins 2/4/6 `VDC_5V_LOCAL` and pin 16 `VDC_5V_LOCAL_USB1`; **J6/J7/J8** camera-group B2B pins 56/58 `VDC_5V_LOCAL`. **J4** (power in) pin 1 `VDCIN_5V` and **J5** high-speed B2B `VDCIN_5V` are *inputs* from the power module (raw, unprotected). **J18** (ESC UART) and **J10** (external SPI) are 3.3 V, not 5 V. — [docs.modalai.com, VOXL 2 Connectors](https://docs.modalai.com/voxl2-connectors/)
- On VOXL 2 Mini the same J2 pin 2 is likewise "the fan return, limited to about 400mA" — [docs.modalai.com, VOXL 2 Mini Connectors](https://docs.modalai.com/voxl2-mini-connectors/)
- **Starling 2 Max power architecture:** power module is integrated with the ModalAI 4-in-1 Mini ESC; two 2S 18650 packs in series = 4S, 16.8 V max, XT30. The Mini ESC "also acts as a power source for VOXL2 inside the Starling 2 Max", supplying **5 V for VOXL2** (3.8 V for VOXL2 Mini); the ESC part number is **M0129-5 or M0129-65**. Staff: "you could tap off the power at the ESC main power pads." — [docs.modalai.com, Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/) and [ModalAI forum, Starling 2 Max Accessories and Cables](https://forum.modalai.com/topic/4950/starling-2-max-accessories-and-cables.md)
- Starling 2 Max add-on board provides **I2C, UART, GPIOs and USB**; pinouts are in the USB2 Type A Breakout datasheet — [docs.modalai.com, Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- Mass budget: Starling 2 Max take-off weight **566 g**, payload capacity **500 g** (≈930 g all-up, with reduced endurance); flight time ~40 min on Li-ion, ~55 min on Amprius — [docs.modalai.com, Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/)

### Inferences
- The Sunon MC25060V1 at 5 V draws well under 400 mA (25 mm 5 V fans of this class are typically 100–200 mA; **exact current not confirmed from a datasheet** — see Gaps), so J2's return limit is not a constraint for the sanctioned fan.
- **Risk ranking of taps:** J2 (designed for this, protected, current-limited — negligible risk) ≪ a spare 5 V on the add-on board (plausible, but that rail is shared with USB/peripherals) < J19 (shares the regulated 5 V with GNSS and the RC receiver — a fan's inductive switching noise or an inrush brownout here could disturb GNSS/RC, i.e. flight-critical) < ESC main power pads (unregulated 16.8 V, needs its own buck, and any fault there is on the main power bus feeding the ESC and the autopilot). Only J2 should be considered for a flight article.
- Because all the 5 V rails on VOXL 2 are `VDC_5V_LOCAL` derived from the same ESC-supplied input, adding a fan anywhere adds the same ~1 W to the same regulator; J2 just adds protection and current limiting around it.
- ~5 g of fan plus wiring against 566 g AUW and 500 g payload is ~1 % — irrelevant to endurance.

### Gaps
- **The Sunon MC25060V1-000U-A99 rated current / power was not found** in any source retrieved; distributor listings give RPM, CFM, pressure, noise and weight but no amperage. Confirm from the Sunon datasheet before relying on the 400 mA headroom.
- **Whether J2 is physically accessible on an assembled Starling 2 Max is unconfirmed**, and one older forum report (for the original Starling) claims a frame screw sits over the fan connector. This must be checked on the actual airframe.
- No Starling 2 Max connector/pinout table was found; `docs.modalai.com/voxl2-datasheet/` 404s, and the Max datasheet does not enumerate spare connectors beyond the add-on board.
- Total 5 V budget headroom on the Starling 2 Max's M0129 ESC regulator is not published.

## Q6 — CONTROL: always-on vs PWM vs thermostatic

### Takeaway
**The hardware supports PWM control and ModalAI ships a tool for it, but the documentation is
contradictory about whether VOXL 2's fan output is controllable.** The design intent is clear:
`voxl-fan {on|slow|off}` drives a 25 kHz PWM on the fan return, and `voxl-cpu-monitor` is stated
to adjust the fan with temperature — i.e. thermostatic control is built in. Older forum replies
say VOXL 2's fan output is uncontrollable and always on. **Simplest reliable approach: fit the
fan, leave the default behaviour alone, and verify on hardware whether `voxl-fan` works.**

### Cited Findings
- The VOXL 2 J2 description explicitly says "**PWM Controlled** FAN-Return (GND)" — the low side is switched, the 5 V is permanent — [docs.modalai.com, VOXL 2 Connectors](https://docs.modalai.com/voxl2-connectors/)
- `voxl-fan` (in `voxl-utils` ≥ v0.5.8) supports exactly three commands: `voxl-fan on` (full speed), `voxl-fan slow` (half speed), `voxl-fan off`. The fan runs at full speed at boot / whenever the board is powered on. — [docs.modalai.com, How to Control Fan on VOXL](https://docs.modalai.com/voxl-fan-control/)
- Direct sysfs PWM control, from the same page (25 kHz, 50 % duty):
  ```
  PWM_DEVICE=/sys/class/pwm/pwmchip0
  echo 0 >     ${PWM_DEVICE}/export
  echo 40000 > ${PWM_DEVICE}/pwm0/period
  echo 20000 > ${PWM_DEVICE}/pwm0/duty_cycle
  echo 1 >     ${PWM_DEVICE}/pwm0/enable
  ```
  Supported frequencies: **12.5, 15.00, 18.75, 25, 30.00, 37.5 and 50 kHz**; a requested period is rounded/truncated to the nearest. — [docs.modalai.com, voxl-fan-control](https://docs.modalai.com/voxl-fan-control/)
- "voxl-cpu-monitor monitors CPU temperature and adjusts fan control accordingly" — so you may need to **stop that service** to take manual control — [docs.modalai.com, voxl-fan-control](https://docs.modalai.com/voxl-fan-control/)
- **Contradiction:** the voxl-fan-control page is marked as documenting a **legacy product** and tells you to connect the fan to **J6**, which on VOXL 2 is a camera-group B2B connector, not a fan header. The page is almost certainly written for VOXL 1. — [docs.modalai.com, voxl-fan-control](https://docs.modalai.com/voxl-fan-control/) vs [VOXL 2 Connectors](https://docs.modalai.com/voxl2-connectors/)
- **Contradicting forum statements (2022):** "We can't control it yet so it's just on, but we plan on offering control"; and separately "On VOXL2, the fan output is always on, and there is currently no way to control it." — [ModalAI forum](https://forum.modalai.com/topic/1271/cpu-overheating-on-voxl-2) and [ModalAI forum](https://forum.modalai.com/post/15692)
- `voxl-inspect-cpu`'s output includes a live "Pitmode: / Auto Pitmode:" status line alongside "Governor:", indicating a built-in reduced-power mode — [docs.modalai.com, voxl-inspect-cpu](https://docs.modalai.com/voxl-inspect-cpu)
- CPU mode is settable with `voxl-set-cpu-mode perf` (all cores pinned to max frequency; "the cpu will consume more power (and heat up a bit more)"). It does not persist across reboot; to persist, run `voxl-configure-cpu-monitor factory_enable` then set `normal_cpu_mode` to `performance` in `/etc/modalai/voxl-cpu-monitor.conf` — [ModalAI forum, Suggested CPU mode on VOXL2](https://forum.modalai.com/topic/3271/suggested-cpu-mode-on-voxl2.md)
- Core topology: cores 0–3 are low-power, 4–6 medium, core 7 is the fastest — [ModalAI forum](https://forum.modalai.com/topic/3271/suggested-cpu-mode-on-voxl2.md)

### Inferences
- The 2022 "can't control it" posts predate the current docs by years; the J2 connector description and the existence of `voxl-fan` suggest control is now available, but **this is exactly the kind of thing that must be verified on the actual SDK version**. Test: `voxl-fan off` and listen / feel for the fan stopping.
- **Recommended control strategy, in order of preference:**
  1. **Default (thermostatic via voxl-cpu-monitor)** — do nothing, let the stock service manage it. Fewest moving parts, no custom code to fail in flight.
  2. **Always-on** — if `voxl-fan` turns out not to work on this build, the fan simply runs at full speed from power-up. Acceptable: ~1 W, ~5 g, constant known vibration signature (easier to notch-filter than a variable one, see Q7).
  3. **Custom thermostatic script** — only if you need a different setpoint. Avoid: a script that can wedge and leave the fan off is strictly worse than always-on.
- A **constant-speed** fan is actually preferable to a thermostatic one for EKF purposes, because a fixed-RPM fan produces a single stationary vibration peak that a PX4 static notch filter can remove; a variable-speed fan sweeps the peak across frequencies and defeats a static notch (PX4's dynamic notch tracks ESC/gyro-derived rotor frequencies, not a cooling fan). **This is engineering inference, not a cited finding.**
- No tach/RPM feedback is possible on J2: it is a 2-pin header (5 V + switched return) with no sense line. A 3- or 4-wire PC-style fan's tach and PWM-input pins have nowhere to go without an extra GPIO and a level-shift. The PX4 `OnboardComputerStatus` message has fan-speed fields, but nothing on this hardware can fill them.

### Gaps
- Whether `voxl-fan` exists and works on the user's current voxl-utils / SDK version — **hardware check required** (`which voxl-fan; voxl-fan --help`).
- Whether `pwmchip0`/`pwm0` is the correct PWM channel for J2 on VOXL 2 (the documented example is from the VOXL 1-era page) — **hardware check required** (`ls /sys/class/pwm/`).
- The temperature setpoints / hysteresis `voxl-cpu-monitor` uses for fan control are not published.
- No confirmation that J2's 5 V is switched at all (the docs say only the return is PWM'd), so `voxl-fan off` may leave the fan unpowered-but-connected rather than truly off — immaterial in practice.

## Q7 — MECHANICAL: mounting a fan on a flying multirotor

### Takeaway
This is the weakest-sourced area: **no ModalAI or published multirotor-engineering source
specifically addresses cooling-fan vibration coupling into a flight-controller IMU.** What is
documented is that (a) ModalAI's own measured experience is that **prop-wash routing beat
vapor chambers and heatsinks**, (b) ModalAI warns against mechanical stress on the SIP and
against grounded metal hardware for EMC, and (c) IMU vibration on this exact airframe is
already a live issue (the accelerometer-bias failures in Q3). Most of the mechanical guidance
below is inference and is labelled as such.

### Cited Findings
- ModalAI's design page, reporting a customer project whose data they cannot share: "simply using the drone's prop wash [was] the most effective solution compared to high-end vapor chambers, heatsinks", better by "many degrees C" — [docs.modalai.com, VOXL 2 thermal performance](https://docs.modalai.com/voxl2-thermal-performance/)
- "Airflow is the single biggest factor for improved thermal performance" — [docs.modalai.com](https://docs.modalai.com/voxl2-thermal-performance/)
- Mechanical warning on heatsink attachment: "be careful not to apply excessive mechanical stress to the QRB5165 SIP while mounting the heat spreader to it" — [ModalAI forum](https://forum.modalai.com/topic/5103/voxl2-thermal-throttling-and-heat-dissipation-methods)
- EMC/mechanical: "Do not use grounded or metal hardware (screws/washers/spacers)"; "Do not lay cables directly above or over any PCB, IC, or power circuit"; a heatsink, if used, should be "passive and electrically non-conductive" — [docs.modalai.com](https://docs.modalai.com/voxl2-thermal-performance/)
- Board layout: J3/J5 B2B connectors were placed on the secondary side specifically so add-on boards don't block airflow over the **memory side** — the face to aim air at — [ModalAI forum, VOXL2 thermal management](https://forum.modalai.com/topic/2233/voxl2-thermal-management)
- Fan mass: ~5.0 g for the MC25060V1 class — [IBS Electronics](https://ibselectronics.com/products/sunon-fans/mc25060v1-000u-a99); against 566 g AUW / 500 g payload — [docs.modalai.com, Starling 2 Max datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- General flight-controller vibration practice (not fan-specific): silicone rather than foam isolators (Holybro Pixhawk 6X Pro "novel vibration isolation design utilizes durable silicone isolation material instead of conventional foam"); added mass helps because "the heavier the mass the more force is required to accelerate it" — [FlyingTech, Pixhawk 6X Pro](https://www.flyingtech.co.uk/product/holybro-pixhawk-6x-pro/)
- Failure modes reported by builders: over-soft mounting can make Z-axis vibration *worse* ("there might be too much double-sided foam under the flight controller"); unsecured wiring defeats isolation ("the wiring will just be transferring and amplifying vibrations to the flight controller"); excessive vibration causes sensor clipping ("there is clipping in the isolated IMUs so dont fly again until you are sure Z axis vibrations are improved"); harmonic notch filtering is the software complement — [ArduPilot forum, Cube without internal damping](https://discuss.ardupilot.org/t/cube-without-internal-damping/100364)
- ModalAI staff link board temperature to IMU error on this exact platform: high temperatures "may be causing the accelerometer bias error"; recalibrate the IMU **with airflow over the unit** — [ModalAI forum, Questions on Starling 2 Max](https://forum.modalai.com/topic/5330/questions-on-starling-2-max.md)

### Inferences
*(All of this section is engineering inference, not cited fact.)*
- **The VOXL 2 *is* the flight controller.** Unlike a companion-computer fan, anything bolted to the VOXL 2 couples directly into the PX4 IMUs with no isolation stage between. A 13 000 RPM fan has a blade-pass excitation at roughly 216 Hz fundamental (13000/60) times blade count — well above the ~0–100 Hz band that matters most for EKF attitude estimation, and above typical prop fundamentals, but small fans also have low-frequency imbalance components at the shaft rate. The honest position is: unknown until measured in a PX4 ulog FFT.
- **Mount the fan to the frame, not to the board.** A short standoff from a carbon-fibre frame member, blowing across the SIP, keeps the rotating mass off the PCB and avoids any stress on the SIP. Soft-mounting the fan itself (small silicone grommets or a thin VHB pad) breaks the metal-to-metal path. Do not soft-mount the *autopilot* further — the board mounting is ModalAI's design and loosening it is a worse risk than the fan.
- **Secure the fan cable.** The ArduPilot finding about wiring transmitting vibration applies directly; a 2-wire pigtail flapping in downwash is both a vibration path and an FOD/prop-strike hazard. Route and tie it clear of props.
- **Effectiveness in hover is genuinely doubtful.** A hovering multirotor already sits in its own downwash; a 3.0 CFM fan is small compared to rotor-induced flow. ModalAI's own finding that prop-wash routing beat heatsinks and vapor chambers suggests that **in flight the existing downwash may already be the dominant cooling mechanism, and the fan adds little.** The fan's real value is the **non-flying** phases: powered-on-the-bench, pre-arm, between flights, IMU calibration — which, per Q3, are exactly when 104 °C was observed.
- **Dust/FOD:** an indoor mocap hangar is a relatively clean environment, but a 25 mm fan with no filter will accumulate dust on the blades (imbalance → vibration growth over time) and could ingest debris. Inspect and clean it; do not add a filter (it would kill the already-small flow).
- **Prop-wash interaction:** a fan mounted so it blows *against* the downwash will stall; mounted so it blows *with* the local flow it adds little. Orient it to pull air through whatever shadowed pocket the SIP sits in — which requires looking at the actual airframe.
- **Verification is mandatory, not optional.** After fitting any fan: fly the same hover profile as before and compare PX4 vibration metrics (`VIBE` / `vehicle_imu_status` accel vibration levels and the FFT of raw accel) with the fan on vs. off. If the fan introduces a new spectral peak, either remove it or add a static notch at that frequency. Given the user's Iron Rule 5 (software is blind to arming state) and the existing accel-bias reports in the wider Starling 2 Max community, this is a flight-safety check, not a nicety.

### Gaps
- **No source found** on cooling-fan vibration coupling into a flight-controller IMU, for any platform. The whole vibration argument above is inference from general FC isolation practice.
- No published measurement of whether a Starling 2 Max's own downwash reaches the VOXL 2, nor of hover temperature vs. bench temperature on this airframe.
- No documented fan mounting point, bracket, or ModalAI-supplied mount for the Starling 2 Max. Whether there is physical clearance for a 25 × 25 × 7 mm fan over the SIP is unknown.
- Fan blade count (hence blade-pass frequency) for the MC25060V1 is not in the retrieved listings.

## Q8 — Passive alternatives: would any beat a fan?

### Takeaway
**Yes — for this user, reducing CPU load almost certainly beats a fan, and it is free.** The
104 °C Starling 2 Max report was at 96 % CPU with `voxl-camera-server` (184 %), `voxl-qvio-server`
(96 %) and `px4` (90 %) all running. Under OptiTrack mocap, VIO and most of the camera pipeline
are **not needed for navigation**. ModalAI's own first suggestion in nearly every thermal thread
is to find and kill the load. After that, airflow (prop-wash ducting or a fan) is second, and a
bare heatsink is explicitly discouraged.

### Cited Findings
- Staff: "optimizing your code or reducing the processing workload" offered as the alternative to hardware cooling — [ModalAI forum](https://forum.modalai.com/topic/1271/cpu-overheating-on-voxl-2)
- Staff: "look at the output of `top` to see rough CPU usage of each process", and try "disabling the mapper, OpenVINS, or high-res image processing" — [ModalAI forum](https://forum.modalai.com/topic/4484/temperature-issue-with-voxl-2.md)
- Staff diagnosing an "idle" Starling 2 at >80 °C: the board "wasn't really idling" — `voxl-portal` was using CPU and `voxl-camera-server` "an excessive amount"; the board heated rapidly when voxl-portal was open in a browser — [ModalAI forum](https://forum.modalai.com/topic/4484/temperature-issue-with-voxl-2.md)
- Staff asked whether the board was **enclosed in a box**, since enclosure affects cooling — [ModalAI forum](https://forum.modalai.com/topic/4484/temperature-issue-with-voxl-2.md). (The two throttling-at-95 °C cases found were both enclosed.)
- **Underclocking is documented and supported.** Cap a core's max frequency: `echo 1785600 > /sys/devices/system/cpu/cpu3/cpufreq/scaling_max_freq`, described by ModalAI as "a way to limit heat". Governors available: `performance`, `powersave`, `userspace`, `ondemand`, `conservative`. GPU cap: `echo 560000000 > /sys/class/kgsl/kgsl-3d0/devfreq/max_freq`. Cores can also be taken offline: `echo 0 > /sys/devices/system/cpu/cpu2/online`. — [docs.modalai.com, Thermal and Performance](https://docs.modalai.com/thermal-and-performance)
- Conversely, `voxl-set-cpu-mode perf` **increases** heat ("the cpu will consume more power (and heat up a bit more)") — do not leave the board in perf mode for thermal reasons — [ModalAI forum](https://forum.modalai.com/topic/3271/suggested-cpu-mode-on-voxl2.md)
- **Prop-wash ducting is ModalAI's top-rated passive option**: routing the drone's prop-wash over circuit areas was "the most effective solution compared to high-end vapor chambers, heatsinks" — [docs.modalai.com](https://docs.modalai.com/voxl2-thermal-performance/)
- **Bare heatsink is discouraged**: without airflow it "will effectively become a large thermal capacitor", delaying throttling but sustaining the degradation longer; if used, pair with a fan, and keep it passive and non-conductive — [docs.modalai.com](https://docs.modalai.com/voxl2-thermal-performance/)
- ModalAI has **no heatsink or thermal-pad part recommendation** for VOXL 2 — [ModalAI forum](https://forum.modalai.com/topic/5103/voxl2-thermal-throttling-and-heat-dissipation-methods)
- The one data point for heatsink+fan: 14 × 10 mm Pi RAM heatsink on the underside of the SIP plus a fan gave "at least 10-20 degrees" improvement under heavy load — [ModalAI forum](https://forum.modalai.com/topic/5103/voxl2-thermal-throttling-and-heat-dissipation-methods)
- Test-first guidance from ModalAI: "A 10-20 minute test can open your eyes much more than weeks of design and analysis"; log temperatures, frame rates and RSSI and correlate them — [docs.modalai.com](https://docs.modalai.com/voxl2-thermal-performance/)

### Inferences
- **Load-reduction candidates specific to this stack** (each needs verification that nothing downstream depends on it): stop `voxl-qvio-server` (mocap supplies pose, so VIO is redundant); reduce or stop `voxl-camera-server` streams not actually consumed; never leave `voxl-portal` open in a browser during a session; check what the ROS 2 Foxy graph is subscribing to. Based on the Q3 log, camera-server + QVIO alone were ~280 % of one core's worth of CPU.
- A thermal pad from the SIP to the carbon-fibre frame is a poor idea: carbon fibre has low through-thickness conductivity, the pad would mechanically couple the board to the frame (vibration path), and ModalAI warns against mechanical stress on the SIP and against conductive hardware near the board.
- **Decision order for this user:** (1) measure, (2) cut load, (3) re-measure, (4) only then fan. If after load reduction the hover temperature sits below ~85 °C, no fan is needed for flight — though a **bench/desk fan during development and IMU calibration is free, risk-free and already recommended by ModalAI staff** for exactly this airframe.
- Underclocking is the last resort: PX4 on a throttled core is worse than PX4 on a hot core, and the Q3 report of Position-mode dropouts and delayed ROS messages suggests this stack is already latency-sensitive.

### Gaps
- No quantified comparison of (load reduction) vs (fan) vs (heatsink+fan) on a VOXL 2 exists publicly. The only number anywhere is the anecdotal "10-20 degrees" for heatsink+fan.
- Whether `voxl-qvio-server` and the camera pipeline can be safely disabled without breaking the user's AirStack/ROS 2 stack is a repo question, not a web-research question, and was not investigated here.
- No data on thermal performance of the Starling 2 Max specifically with vs without airflow in flight.

## What must be confirmed on the actual hardware

These could not be settled from documentation and are the hardware checklist:

1. **Baseline temperature.** Run `voxl-inspect-cpu` (or the `-j -t` logging loop in Q4) through a complete session: cold power-on, idle on the floor, armed, hover, land, idle. Record hangar ambient. This is the single measurement that decides everything else.
2. **Is it throttling, or just hot?** Log `scaling_cur_freq` per core alongside temperature. Hot without frequency reduction = no action needed.
3. **What is actually consuming CPU?** `voxl-inspect-cpu -f` or `top` during hover. Compare against the Q3 Starling 2 Max profile (camera-server 184 %, QVIO 96 %, px4 90 %).
4. **Is J2 physically reachable** on the assembled Starling 2 Max, and is there clearance for a 25 × 25 × 7 mm fan over the memory side of the SIP?
5. **Does `voxl-fan` exist and work** on this SDK version? `which voxl-fan; voxl-fan --help; voxl-fan off` and check. Also `ls /sys/class/pwm/` to confirm the pwmchip number.
6. **Thermal zones:** `for z in /sys/class/thermal/thermal_zone*; do echo "$z $(cat $z/type) $(cat $z/temp)"; done` to find the real sysfs paths and the kernel trip points (`cat $z/trip_point_*_temp`) — this would resolve the 90 vs 95 °C ambiguity definitively.
7. **Does voxl-px4 stream `ONBOARD_COMPUTER_STATUS`?** Check QGC MAVLink Inspector. If yes, temperature is already in the QGC/ulog telemetry and no custom logging is needed.
8. **If a fan is fitted:** re-fly the identical hover profile and compare PX4 vibration metrics and raw-accel FFT, fan on vs fan off, before trusting it for autonomous flight.
9. **MC25060V1 current draw** against J2's ~400 mA return limit — from the Sunon datasheet or a bench measurement.

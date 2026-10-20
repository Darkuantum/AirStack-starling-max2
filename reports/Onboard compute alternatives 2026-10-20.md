# The ESC's 750 g rating, not compute, decides what can ride on a Starling 2 Max

*Research brief, 2026-10-20. Plan: [docs/MODIFICATIONS.md](../docs/MODIFICATIONS.md) ⑤; hardware facts: [docs/HARDWARE.md](../docs/HARDWARE.md). Question: how do we run more powerful algorithms onboard, in whatever form that takes? Inputs: three parallel web-research passes (VOXL 2 headroom, companion computers, replacement architectures and airframes) plus this repo's own measurements. Markers: **[I]** = our inference or arithmetic, not a sourced figure. **[U]** = found but not verified.*

There are five ways to get more onboard compute. They are ranked below by how much they disturb the aircraft you already fly:

| # | Option | Compute gained | Added mass | Cost (USD) | Verdict |
|---|---|---|---|---|---|
| 1 | **Reclaim the VOXL 2** (stop unused services, perf mode, Docker for newer ROS 2) | ~1.4 cores freed, out of thermal throttling | 0 g | 0 | **Do first, regardless** |
| 2 | **Light companion** (Pi CM5, Pi 5 + Hailo, RK3588) beside the VOXL 2 | Modern Ubuntu/ROS 2, 4 more A76 cores, up to 26 TOPS | +40–90 g | ~$300–500 | **Fits.** Best next step if (1) is not enough |
| 3 | **Jetson companion** (Orin Nano/NX) beside the VOXL 2 | 67–157 TOPS, CUDA/TensorRT | +170–200 g | ~$1,100–1,700 | **At or over the ESC's 750 g rating.** Not on this airframe |
| 4 | **Replace the VOXL 2** with a flight controller + Jetson | as (3) | net +50–175 g | ~$1,000–1,500 + rework | **No.** Loses all cameras, and the ESC driver path is unproven |
| 5 | **Different airframe** built for a Jetson / LiDAR | anything | n/a | ~$2–4k per drone [I] | **The only route to onboard LiDAR SLAM** |

**The constraint that dominates everything:** ModalAI says the M0129 ESC is "Designed for vehicles under 750 g (under 500 g in FPV use)" ([ModalAI M0129 product page](https://www.modalai.com/products/voxl-esc-mini)). The Starling 2 Max takes off at 566 g ([datasheet](https://docs.modalai.com/starling-2-max-datasheet/)), which leaves **~184 g of ESC-rated margin**, not the datasheet's "500 g payload". That datasheet figure also contradicts itself: it says "total takeoff weight ~930 g", and 566 + 500 is not 930. Until ModalAI says otherwise, treat 750 g as the ceiling. The LED strip and fan from the modification stack spend ~10–15 g of that margin [I].

## 1 · Reclaim the VOXL 2 first: it is already roughly an Orin Nano's CPU

**What the chip is.** The QRB5165 has 8 Kryo 585 cores: 4 × A55 at 1.8 GHz, 3 × A77 at 2.42 GHz and 1 × A77 at 2.84 GHz ([ModalAI staff, forum post 18776](https://forum.modalai.com/post/18776)). It also has an Adreno 650 GPU (~1.2 TFLOPS FP32 [I], from 1024 ALUs × 587 MHz), 8 GB LPDDR5, and a 0.1–7 W envelope ([ModalAI VOXL 2](https://www.modalai.com/products/voxl-2)).
- For multithreaded CPU work it is roughly on par with an Orin Nano (6 × A78) [I].
- On neural networks it is **2–5× behind in usable throughput**, and it has no CUDA/TensorRT [I]. The "15 TOPS" is Qualcomm's combined marketing figure ([QRB5165 brief](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/qrb5165-soc-product-brief_87-28730-1-b_0.pdf)). ModalAI documents **no Hexagon delegate** for it, so most of that number is unreachable (see the tflite table below).

**Where the headroom went.** On 2026-10-14 we measured `voxl-camera-server` at ~95 % CPU and `voxl-qvio-server` at ~48 %, with the board at 95–102 °C. That is already inside ModalAI's throttling band of ~90–95 °C ([forum post 18776](https://forum.modalai.com/post/18776)). A user found that disabling camera-server alone keeps a stationary board "cool indefinitely" ([forum post 22727](https://forum.modalai.com/post/22727)). We fly on mocap, so VIO is dead weight. **Stopping both services frees ~1.4 cores and should pull the board out of throttling.**
- Pin performance mode persistently: `normal_cpu_mode: performance` in `/etc/modalai/voxl-cpu-monitor.conf` ([forum](https://forum.modalai.com/topic/3126/new-sdk-performance-mode); [forum post 15428](https://forum.modalai.com/post/15428)).
- Watch throttling with `voxl-inspect-cpu`.
- Check that `voxl-vision-hub` and the ToF pipeline don't need camera-server before disabling it.

**What has actually been run on this chip:**

| Workload | Result | Source |
|---|---|---|
| acados NMPC, 1 s horizon, N = 10 | **150 Hz onboard VOXL 2**, alongside a 500 Hz UKF | [HPA-MPC, arXiv 2411.11982](https://arxiv.org/html/2411.11982) |
| FAST-LIVO2 (LiDAR + visual + inertial) | **78 ms/frame on an RB5** (same QRB5165). Real-time at 10 Hz | [arXiv 2408.14035](https://arxiv.org/html/2408.14035), Table III |
| FAST-LIO2 (LiDAR-inertial only) | 46–66 ms/scan on a *weaker* A73 board; ~30–50 ms expected on A77 [I] | [FAST-LIO2 paper](https://arxiv.org/pdf/2107.06829) |
| YOLOv5 at 320 px | 23 ms on GPU delegate, 88 ms on CPU | [voxl-tflite-server docs](https://docs.modalai.com/voxl-tflite-server/) |
| YOLOv8/v11 | GPU and NNAPI delegates reject ops and fall back to CPU (Oct 2025 report, no fix posted) | [forum topic 4789](https://forum.modalai.com/topic/4789/voxl2-mini-qrb5165-yolo-on-npu-nnapi-or-gpu-keeps-falling-back-to-cpu-looking-for-a-known-good-export-runtime-path-or-qnn-htp) |

So **MPC, CBF and planning fit on the VOXL 2 today.** LiDAR-inertial odometry is plausible on its CPU, but its sensor does not fit the airframe (see §4). Neural perception is limited to small TFLite models.

**The OS is the hard ceiling.**
- VOXL 2 is **Ubuntu 18.04, kernel 4.19 → ROS 2 Foxy**. ModalAI says 22.04 is not possible ([forum post 22798](https://forum.modalai.com/post/22798)). SDK 1.8.0 (2026-10-12) still ships 18.04 for VOXL 2 [I, from the [release notes](https://docs.modalai.com/sdk-1.8-release-notes/) mentioning no rebase].
- ModalAI's answer for Humble is Docker ([forum post 13560](https://forum.modalai.com/post/13560)). Inside a container you get **no MIPI cameras and no DSP access**, and GPU only via a hand-copied `libOpenCL` ([forum post 24434](https://forum.modalai.com/post/24434)).
- Our ground stack is DDS-only, so a Humble container on the VOXL is viable for nodes that need no camera.

**VOXL 3 is now documented** ([M0254 feature matrix](https://docs.modalai.com/m0254-feature-matrix/), page dated 2026-10-12):
- QCS6490, 12 TOPS, Ubuntu 24.04 on a mainline kernel, PX4 still on the sensors DSP, 16 g.
- **It is an OS upgrade, not a compute upgrade.** It has fewer TOPS than VOXL 2, and Jazzy would run natively.
- It is billed as a drop-in for the M0154 outline, but power moves to direct 2S–6S battery input on a relocated J4, the IMUs change, and **no availability date** is given.
- Not plug-and-play for our M0054-1 Starlings [I]. Worth watching if Foxy is the real pain.

## 2 · A light companion fits, if you can get a link to it

These all stay well under 750 g. Masses are flight-ready (board + carrier + cooling), plus ~10–20 g for BEC, mount and cables [I].

| Companion | Compute | Mass | Power | Input | Ethernet | OS / ROS 2 | Price (USD) |
|---|---|---|---|---|---|---|---|
| **Pi CM5 on ARK Just A Pi** | 4 × A76 @ 2.4 GHz, no NPU | **~40–50 g** [I] (carrier 19.5 g) | ~3–9 W | 5 V ≥ 2 A, needs BEC | 2 × **10/100** only | Pi OS / Ubuntu 24.04 → Jazzy | $335 carrier; $475 with CM5 Lite 2 GB ([CNX](https://www.cnx-software.com/2026/08/31/ark-just-a-pi-a-tiny-ndaa-compliant-raspberry-pi-cm5-carrier-board-for-drones-and-robots/)) |
| **Pi 5 + AI HAT+ (Hailo-8, 26 TOPS)** | 4 × A76 + 26 TOPS INT8 | **~75–80 g** | 3 W idle → ~9–16 W | 5 V / 5 A, needs BEC | GbE | Ubuntu 24.04 possible. **No official Hailo ROS 2 package**; HailoRT on Ubuntu is manual ([Hailo community](https://community.hailo.ai/t/is-there-an-official-ros2-package-for-running-yolo-on-raspberry-pi-5-with-ai-hat/12539)) | Pi 5 8 GB $175 + HAT $110 ([BGR](https://www.bgr.com/2150106/raspberry-pi-cost-ram-crisis/); [Tom's HW](https://tomshardware.com/raspberry-pi/raspberry-pi-release-higher-performance-ai-hat-13-and-26-tops-variants)) |
| Pi 5 + AI HAT+ 2 (Hailo-10H) | 40 TOPS INT4 / 20 INT8 | ~80 g | +~2.5 W | as above | GbE | as above | HAT $130 ([heise](https://heise.de/-11136612)) |
| **Khadas Edge2 (RK3588S)** | 4 × A76 + 4 × A55, 6 TOPS NPU | **25 g board**, ~11 mm thick with fan | ~1–10 W | USB-C PD | none (USB-C) [I] | Ubuntu 22.04 → Humble | $199–369 (2022 pricing) ([CNX](https://www.cnx-software.com/2022/09/13/khadas-edge2-ultra-thin-sbc-is-powered-by-rockchip-rk3588s-processor/)) |
| Radxa Rock 5C / Orange Pi 5 (RK3588S) | as Edge2 | 46–85 g | ~3–7 W | 5 V | GbE | Ubuntu 22.04 | $50–200 |

**Endurance [I].** Assumptions: the 4S 3 Ah pack is ~43 Wh, 40 min stock implies ~55 W hover, and hover power scales with mass^1.5.
- +50 g → ~33 min
- +80 g → ~30 min
- These include the companion's own few watts.

**Power.** Never take power from the ESC's 5 V main output: it is rated 5 A and already feeds the VOXL 2, which needs ~6 A at inrush ([M0129 page](https://www.modalai.com/products/voxl-esc-mini)). Tee the 4S battery into a small 5 V / 5 A BEC. The Matek BEC12S-PRO is 5 g ([GetFPV](https://www.getfpv.com/drone-brands/maytek-systems/mateksys-12s-pro-bec-9-55v-to-5v-8v-12v-5a.html)).

**The link to the VOXL 2 is the real obstacle, not the computer.** VOXL 2 has no Ethernet. The M0062 Ethernet add-on needs J3 + J5, and both are occupied on both aircraft: Starling 2's WiFi board and Starling 1's M0090 5G carrier each connect to J3 and J5 (owner check 2026-10-20). The options:

| Link | Starling 1 | Starling 2 | Status |
|---|---|---|---|
| **USB NCM over the VOXL 2's USB-C (J9).** A ModalAI staff recipe (Feb 2026) adds `ncm.0` to `/sbin/usb/compositions/901D`; VOXL becomes `usb0` at 192.168.7.2 ([forum post 25777](https://forum.modalai.com/post/25777)) | ✓ | ✓ | Works with a Linux PC as host. **Untested with a Pi/Jetson as host, and J9 is also the adb port.** Bench-test with the laptop first |
| USB-Ethernet adapter on the M0090's free `J11` (USB 3, 10-pin; the dongle uses `J12`, owner check 2026-10-20) | ✓ plausible [I] | — | Shares the carrier's hub with the WiFi dongle. Best wired option on Starling 1 |
| Both on the lab WiFi (Pi 5 / CM5 have WiFi) | ✓ | ✓ | Zero hardware. Doubles airtime per drone and adds jitter, so fine for perception outputs, not for tight loops [I] |
| UART MAVLink ([forum](https://forum.modalai.com/topic/3672/companion-computer-to-voxl-2-over-uart/1)) | ✓ | ✓ | Too slow for ROS 2 topics; OK for setpoints |

**Cross-distro DDS.** The VOXL is on Foxy, a companion on Humble/Jazzy. This is officially unsupported. Foxy ↔ Humble has been reported working with the same RMW and unchanged message types ([ROS Discourse](https://discourse.openrobotics.org/t/ros-cross-distribution-communication/27335)). Jazzy adds type-description hashes, which adds risk ([ROS Discourse](https://discourse.openrobotics.org/t/incompatability-between-distributions/43747)). Pick **Humble** on the companion, pin one RMW, or keep the VOXL ↔ companion boundary to MAVLink / plain UDP. The LED daemon already uses UDP for exactly this reason.

## 3 · A Jetson companion is at the ESC's limit

- Jetson flight-ready mass is ~150–175 g on any carrier: module ~25–28 g, plus 52–65 g of heatsink and fan ([PX4 ARK PAB docs](https://docs.px4.io/main/en/companion_computer/ark_jetson_pab_carrier); [Holybro weight table](https://docs.holybro.com/autopilot/pixhawk-baseboards/pixhawk-jetson-baseboard/dimension-and-weight)). Installed, that is **~170–200 g** [I].
- 566 + 15 (LED, fan) + 170–200 g puts the aircraft at **~750–780 g**: at or over the ESC rating, at ~23 min estimated endurance [I].
- The TU Delft Orin NX + DAMIAO carrier is lighter at 62 g ([repo](https://github.com/tudelft/event_orin_drone)). That would land ~645 g, but it is a research build with no off-the-shelf heatsink figure [U].
- **Prices rose in July 2026.** Orin Nano module $299 → $399, Orin NX 16 GB $599 → $999 ([CNX](https://cnx-software.com/2026/07/22/nvidia-increases-the-price-of-jetson-modules-and-devkits-by-up-to-101)). The lightest sensible carriers that take 4S directly are ARK Just A Jetson ($680, 5.5–75 V, [ARK](https://arkelectron.com/product/ark-just-a-jetson/)) and ConnectTech Hadron-DM ($410–522, 9–60 V, [WDL](https://www.wdlsystems.com/connect-tech-ngx027)). Avoid the WeAct N006: it needs 16–28 V, which a 4S pack cannot supply ([CNX](https://www.cnx-software.com/2026/06/30/weact-n006-a-compact-nvidia-jetson-orin-nx-carrier-board-designed-for-robots-and-uavs/)).
- Run JetPack 6.2 (Ubuntu 22.04 / Humble) rather than 7.2 (24.04 / Jazzy), for the Foxy bridge above.

**Only consider this if you need CUDA/TensorRT-class perception and ModalAI confirms the M0129 is fine at ~780 g.** Otherwise the Jetson belongs on a different airframe (§5).

## 4 · Replacing the VOXL 2 with a flight controller + Jetson: don't

- **The M0129 speaks a ModalAI UART protocol.**
  - Upstream PX4 builds the `voxl_esc` driver only for ModalAI boards (`fc-v1`, `fc-v2`, `voxl2`; checked in PX4 `main` @ 30d778e, 2026-10-20).
  - The one public Pixhawk 6X attempt never spun the motors ([forum topic 3774](https://forum.modalai.com/topic/3774/voxl-esc-mini-integration-with-px4-on-pixhawk6x-and-kakuteh7.md)).
  - Its PWM input is disabled in stock firmware ([forum post 16006](https://forum.modalai.com/post/16006)).
  - ModalAI's Flight Core v2 does drive it, but its product URL now lands on an end-of-life page [U].
- **You lose every camera.** The M0173 front-end only mates with VOXL 2 camera connectors ([M0173 docs](https://docs.modalai.com/M0173/)), so the four cameras and the ToF become dead weight.
- **Your provisioning dies too.** The LED path, `voxl-px4`, MPA and the setup scripts all go.
- **You can't flash the VOXL firmware onto a Jetson** (the colleague's question): the image is a Qualcomm board support package, and PX4 lives on the Hexagon DSP, which a Jetson does not have.
- **The best-case result is still at the 750 g limit**, for more money and more work than option 3.

## 5 · A different airframe is the only honest route to onboard LiDAR SLAM

A Livox Mid-360 is 265 g ([Livox](https://www.livoxtech.com/mid-360/specs)). On a Starling that means ~850 g+ before a mount, and the lighter LiDARs (Hesai JT16 < 200 g, Unitree L1 ~230 g) still exceed 750 g [I]. **No LiDAR fits this ESC's rating.** The previous report treated LiDAR as a payload-budget question against 500 g; the 750 g ESC rating settles it, unless ModalAI says otherwise.

Platforms that do carry Jetson/NUC + Mid-360, at sizes that could fit a mocap volume:

| Platform | All-up | Size | Compute + sensor | Cost | PX4 | Fit for an indoor mocap swarm |
|---|---|---|---|---|---|---|
| **HKU MaRS SUPER** ([open BOM](https://github.com/hku-mars/SUPER-Hardware)) | ~1.5 kg ([Nanowerk](https://www.nanowerk.com/news2/robotics/newsid=66982.php)) | 280 mm, 7" props | NUC 12 + Mid-360; Orin NX swap possible [I] | DIY | NxtPX4 (PX4) | **Best match.** Same 7" class as the Starling; the lab behind FAST-LIO and [Swarm-LIO2](https://arxiv.org/html/2409.17798v1) |
| HEPP (HKU) | 1.31 kg | 200 mm | NUC + Mid-360 | DIY | — | Small, but no BOM found [U] |
| **Holybro X500 V2 + Pixhawk Jetson Baseboard** | ~0.8 kg + battery; 1.5 kg payload | ~500 mm class [U] | Orin NX + Pixhawk 6X; Mid-360 fits [I] | $508 + $1,430 ([Holybro](https://holybro.com/products/pixhawk-jetson-baseboard)) | Yes | Simplest to buy; large for a multi-drone mocap volume [I] |
| TU Delft Event-Orin | 822 g | 5" props | Orin NX 16 GB + D435i + event camera | DIY | PX4 (Kakute H7) | Camera-based, not LiDAR |
| ModalAI Stinger Vision / Sentinel / PX4 Autonomy Kit | 265 g – 1.35 kg | 220–480 mm | **same QRB5165** | $2.7–5k | Yes | **No compute gain.** Skip for this goal |
| Chinese turnkey Orin NX + Mid-360 kits ("P600") | — | — | Orin NX + Mid-360 | ~$17k listing [U] | — | Opaque specs, very expensive |

Two checks come before buying any LiDAR airframe:
- **Mid-360 vs OptiTrack.** The Mid-360 emits at 905 nm ([Livox](https://www.livoxtech.com/news/mid360_launch)) and OptiTrack strobes in the near-IR. No report either way was found. **Bench-test one sensor in the volume** before buying a fleet.
- **Volume size against a 280–500 mm airframe** for multi-drone CBF squeeze scenarios.

## Offloading is what you already do, and it should stay that way for slow layers

- WiFi 6/6E reaches < 30 ms end-to-end at 20 m in a swarm study ([NTU](https://tdr.lib.ntu.edu.tw/handle/123456789/101008?locale=en)), but ROS 2 over WiFi has long latency tails under load ([Padua](https://thesis.unipd.it/handle/20.500.12608/109286)). That is fine for the CBF and setpoints at tens of Hz (today's design). It is not fine for inner loops, or for streaming several drones' point clouds.
- **5G:** a Starling owner's EM9291 would only connect on LTE ([forum topic 4882](https://forum.modalai.com/topic/4882/em9291-on-starling-2-voxl-2-only-connecting-on-lte-no-5g-nr-bands-detected-firmware-issue.md)). Indoors without a private cell it is worse than lab WiFi.
- **Tethers:** commercial units are big outdoor systems (~AUD 20k, [D1 Store](https://Www.d1store.Com.au/products/elistair-ligh-t-4-tether-station)), and they are incompatible with a swarm.

## Decision tree: pick by the algorithm, not the hardware

```
What do you want to run onboard?
│
├─ MPC / CBF / planners / estimators (CPU, no camera)
│     → Option 1: stop camera-server + qvio, perf mode. Humble in Docker if Foxy blocks you.
│       acados NMPC already runs at 150 Hz on VOXL 2.          Cost: $0
│
├─ Same, but you need native Humble/Jazzy or more CPU
│     → Option 2: Pi CM5 on ARK Just A Pi (~45 g), linked by USB NCM or WiFi.
│       Watch VOXL 3 (Ubuntu 24.04 natively) as a longer-term fix.   ~$500
│
├─ Neural perception
│   ├─ small models (MobileNet-SSD, YOLOv5n) → VOXL 2 GPU via voxl-tflite-server     $0
│   ├─ mid models, 20–26 TOPS               → Option 2: Pi 5 + AI HAT+ (~80 g); budget Hailo/ROS 2 integration   ~$300
│   └─ CUDA/TensorRT, big models            → Option 3 only if ModalAI clears the M0129 at ~780 g;
│                                              otherwise Option 5
│
└─ LiDAR SLAM (FAST-LIO2 + Mid-360)
      → Option 5. No LiDAR fits under the M0129's 750 g rating.
        Start from HKU's SUPER BOM (280 mm, 7") with Orin NX, after the OptiTrack-interference bench test.
```

## Next steps, cheapest first

1. **Stop `voxl-camera-server` and `voxl-qvio-server`** on Starling 1 and re-run `scripts/thermal_soak.sh`. This is free and measures how much CPU and thermal margin comes back.
2. **Email ModalAI support:** what is the M0129's real all-up limit on a D0012 (the 750 g rating vs the datasheet's "~930 g")? That one answer decides whether option 3 exists.
3. **Bench-test USB NCM** on J9 with the laptop as USB host, running the same Foxy ↔ Humble DDS traffic a companion would.
4. **Write down the algorithm list.** The decision tree turns on it, and nothing should be bought before it exists.
5. If LiDAR stays a goal: **borrow a Mid-360 and test it inside the OptiTrack volume** before costing any airframe.

## Contradictions and open items

- **Datasheet payload vs ESC rating.** 500 g payload / "~930 g" takeoff vs "under 750 g" on the M0129 page. Ask ModalAI.
- **Fan control on J2.** One 2024 forum thread says the VOXL 2's J2 fan header is "always on", with no software control ([forum topic 3228](https://forum.modalai.com/topic/3228/starling-fan-attachment-and-optimization)). The connector docs describe pin 2 as a PWM-switched return, and that is what the modification-stack report follows. Unresolved. It only changes whether a fan can be thermostatic.
- **Thermal shutdown.** A moderator says the board shuts down at 90 °C ([forum post 13482](https://forum.modalai.com/post/13482)); staff elsewhere say it throttles at 90–95 °C. We measured 102 °C without a shutdown, so the "shutdown at 90 °C" claim looks wrong for current firmware [I].
- **Throttling and PX4.** Whether apps-CPU throttling affects PX4 on the SLPI was not found. It is likely independent, since the SLPI is a separate DSP [I]. A thermal shutdown would still take PX4 down with the board.
- **Starling 1's J3 board.** Resolved 2026-10-20: an M0090-class 5G carrier, with the WiFi dongle on its `J12` (USB 2) and `J11` (USB 3) free. The companion research had assumed an M0151 USB adapter.
- **Singapore prices.** Mostly unverified: Cytron SG blocked automated fetches. Get quotes for any shortlisted part.

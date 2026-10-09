# Livox LiDAR-Inertial SLAM Software & Protocol Stack for PX4 Position Feed

Scope: driver + protocol, SLAM algorithm + compute target, and the PX4 v1.14 external-vision
fusion path, for a ModalAI Starling Max 2 (VOXL 2 / QRB5165, voxl-px4 on PX4 v1.14, ROS 2 Foxy
onboard, ROS 2 Jazzy ground) currently flown on OptiTrack mocap.

---

## Q1. How does a Livox Mid-360 stream data? SDK2, the Ethernet/UDP protocol, and livox_ros_driver2 distro support

### Takeaway
The Mid-360 is a pure Ethernet/UDP device with a documented, open wire protocol (six fixed UDP
ports, 14 bytes/point, ~22 Mbit/s of point data), and `livox_ros_driver2` officially builds on
ROS 2 Foxy, Humble **and** Jazzy — so the Foxy/Jazzy split is *not* a driver-availability problem.
The sensor is 100BASE-TX only, which matters because the VOXL 2 has no native Ethernet.

### Cited Findings
- Mid-360 official spec: **200,000 points/s (first return)**, 360° × (-7°…52°) FOV, 40 m range @10%
  reflectivity / 70 m @80%, **265 g**, 65×65×60 mm, **6.5 W average** (9–27 V DC; up to 14 W peak in
  sub-0 °C self-heating mode), built-in **ICM40609** IMU, **100BASE-TX Ethernet**, PTPv2 (IEEE
  1588-2008) and GPS time sync, Class 1 eye-safe @905 nm, -20…55 °C —
  [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)
- UDP port map (LiDAR side → host side): 56000 discovery (broadcast, cmd 0x0000 only); 56100 control
  commands (host 56101); 56200 push messages (host 56201); **56300 point cloud (host default 56301)**;
  **56400 IMU (host default 56401)**; 56500 log (host 56501). Control/push/log are unicast; point
  cloud and IMU default to unicast with multicast supported on Mid-360 and Mid-360S (but *not* on the
  360L variant) —
  [Livox Mid-360 Ethernet protocol](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/livox_eth_protocol_mid360.html)
- Point packet format: little-endian, **36-byte header** (version, length, `time_interval` in 0.1 µs
  units, `dot_num`, `udp_cnt`, `frame_cnt`, `data_type`, `time_type`, CRC-32, 8-byte ns timestamp).
  Timestamp marks the *first* point in the packet; points are evenly spaced across `time_interval`.
  Timestamp source can be free-running from power-on, gPTP/PTP, or GPS —
  [Livox Mid-360 Ethernet protocol](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/livox_eth_protocol_mid360.html)
- Point payload sizes: **data_type 1 (default) = 14 bytes/point** (32-bit Cartesian in mm +
  reflectivity + tag); data_type 2 = 8 bytes/point (16-bit, 10 mm resolution); data_type 3 = 10
  bytes/point (spherical). **96 points per UDP packet** for types 1–3. data_type 0 is IMU —
  [Livox Mid-360 Ethernet protocol](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/livox_eth_protocol_mid360.html)
- IMU packets (data_type 0): 3 gyro (rad/s) + 3 accel (g) as 32-bit floats = **24 bytes/sample**;
  rate configurable via `imu_sensor_cfg` to **200 / 500 / 100 / 50 Hz**; enable/disable via
  `imu_data_en` —
  [Livox Mid-360 Ethernet protocol](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/livox_eth_protocol_mid360.html)
- Control frames start with a 0xAA byte, 24-byte header (sequence, command ID, CRC), then data.
  Command IDs: 0x0000 discovery, 0x0100/0x0101/0x0102 configure/query/push parameters, 0x0200 reboot,
  0x0201 factory reset, 0x0202 set GPS timestamp, 0x0300–0x0303 logs, 0x0400–0x0403 firmware upgrade —
  [Livox Mid-360 Ethernet protocol](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/livox_eth_protocol_mid360.html)
- `livox_ros_driver2` official OS/distro matrix: Melodic/18.04; **Noetic/20.04** (`./build.sh ROS1`);
  **ROS 2 Foxy/20.04** (`./build.sh ROS2`); **ROS 2 Humble/22.04** (`./build.sh humble`);
  **ROS 2 Jazzy/24.04** (`./build.sh jazzy`). README recommends Noetic for ROS 1 and "foxy or humble"
  for ROS 2 —
  [livox_ros_driver2 README](https://raw.githubusercontent.com/Livox-SDK/livox_ros_driver2/master/README.md)
- The driver requires **Livox-SDK2** to be built and installed first, must be cloned into
  `ws_livox/src/livox_ros_driver2` (building outside a `src/` folder errors), and may need
  `/usr/local/lib` on `LD_LIBRARY_PATH` for `liblivox_sdk_shared.so` —
  [livox_ros_driver2 README](https://raw.githubusercontent.com/Livox-SDK/livox_ros_driver2/master/README.md)
- `xfer_format` output options: **0 (default)** = Livox-flavoured `PointCloud2` with
  `PointXYZRTLT` (x, y, z, intensity, tag, line, **per-point timestamp**); **1** = Livox custom
  message (header, `timebase`, `point_num`, `lidar_id`, then per-point `offset_time`, x, y, z,
  reflectivity, tag, line) — this is the `CustomMsg` that LIO packages want; **2** = standard
  `PointCloud2` (`pcl::PointXYZI`), **ROS 1 only** —
  [livox_ros_driver2 README](https://raw.githubusercontent.com/Livox-SDK/livox_ros_driver2/master/README.md)
- Upstream explicitly calls the driver a debugging tool, "limited to test scenarios" and **not
  recommended for mass production** —
  [livox_ros_driver2 README](https://raw.githubusercontent.com/Livox-SDK/livox_ros_driver2/master/README.md)
- `multi_topic`: 0 = all LiDARs on one topic, 1 = per-LiDAR topics —
  [livox_ros_driver2 README](https://raw.githubusercontent.com/Livox-SDK/livox_ros_driver2/master/README.md)
- Release-note claim (secondary source): Mid-360**S** support landed in `livox_ros_driver2` 1.2.6 —
  [OpenELab Mid-360S guide](https://openelab.com/blogs/learn/livox-mid-360s-fast-lio2-slam-real-time-mapping-workflow-ros2)

### Inferences
- **Point-cloud bandwidth (computed from the cited protocol numbers, not quoted from a source):**
  200,000 pts/s × 14 B/pt = 2.8 MB/s = **22.4 Mbit/s of payload**. Add UDP/IP/Ethernet framing:
  96 points/packet → 2083 packets/s; 36 B header + 1344 B payload + 42 B UDP/IP/Eth = 1422 B/packet
  → ~2.96 MB/s ≈ **23.7 Mbit/s on the wire**. IMU at 200 Hz × 24 B is negligible (<0.1 Mbit/s).
  Switching to `data_type 2` (8 B/pt, 10 mm quantisation) roughly halves this to ~14 Mbit/s.
- 23.7 Mbit/s sits comfortably inside the sensor's own 100BASE-TX link but is a meaningful load on an
  open 2.4/5 GHz WiFi link shared with telemetry and video — see Q2(c).
- Because the driver builds on Foxy *and* Jazzy from the same upstream tree, the Foxy/Jazzy problem is
  entirely about **DDS interoperability between the two domains**, not about having a driver.
  (Foxy and Jazzy are not RMW-compatible for general use in practice; the repo's own convention of
  speaking plain UDP for onboard add-ons is the right instinct here.)
- The per-point `offset_time` in `CustomMsg` (and the per-point timestamp in `xfer_format 0`) is what
  every LIO package uses for motion de-skew; any custom non-ROS path must preserve it.

### Gaps
- No official Livox figure for Mid-360 point-cloud **bitrate** in Mbit/s; the number above is derived.
  The Mid-360L variant has a `pc_freq_mod` parameter selecting 80k/50k/100k pts/s, but the Mid-360
  proper is specified only at 200k pts/s first-return — one secondary retailer page quoted 100,000
  pts/s, which conflicts with the Livox spec page; treat the Livox page as authoritative.
- The protocol page does not state the Mid-360's **default** IMU rate (only the configurable set).
- Livox-SDK2's own README/API surface was not fetched directly; the ROS-free API details for
  architecture (d) are therefore unverified beyond "it exists and the driver depends on it."

---

## Q2. Architecture options given the Foxy-onboard / Jazzy-ground split

### Takeaway
(a) onboard-Foxy-plus-UDP-pose is the only option that is both low-latency and consistent with the
repo's existing "no ROS on the air link" convention, but it depends on the VOXL 2 having spare CPU
and a working Ethernet path — which it does not natively have. (c) streaming raw points to the ground
is viable on paper (~24 Mbit/s) but adds a WiFi round-trip into the EKF's position loop and is the
worst option for flight safety. (b) a companion computer is the most robust and the most expensive in
weight/power/integration. (d) is the cleanest fit to the existing UDP convention but is real work.

### Cited Findings
- **VOXL 2 has no native Ethernet jack.** Wired Ethernet comes from the **M0062** add-on ("VOXL 2
  Ethernet Expansion and USB Hub"), which plugs into VOXL 2's J3 & J5 and enumerates as `eth0` —
  [M0062 user guide](https://docs.modalai.com/m0062-user-guide/);
  [M0062 product page](https://docs.modalai.com/m0062-2/)
- ModalAI staff on the M0062: it is a **USB-to-Ethernet bridge** that exposes "a full RJ45 jack with
  Gb speeds (but limited to a **USB2 backhaul**)". The RJ45 has integrated magnetics to save space,
  which staff note "makes them more vulnerable to shock failure than typical RJ45's" —
  [ModalAI forum: M0062 datasheet thread](https://forum.modalai.com/topic/2944/datasheet-for-voxl2-ethernet-expansion-and-usb-hub-addon.md)
- Reported M0062 reliability issues: a 2024 user saw no network connection on one of two units (staff
  noted the board has **no link LEDs**, so link state can't be confirmed in hardware, and suggested
  SDK 1.3.3); a 2025 user reported intermittent failures suspected to be power-related —
  [eth0 RJ45 not creating a network connection](https://forum.modalai.com/topic/3844/add-on-ethernet-hat-eth0-rj45-port-not-creating-a-network-connection.md);
  [Ethernet Expansion and HUB power issue](https://forum.modalai.com/topic/4247/voxl-2-ethernet-expansion-and-hub-power-issue.md)
- On the same board, USB-A J10 "is not working consistently … for USB3 speeds and may only work in
  USB2 mode" — use J11 for USB3 —
  [M0062 user guide](https://docs.modalai.com/m0062-user-guide/)
- VOXL 2 stock OS is **Ubuntu 18.04 with Linux 4.19**. ModalAI staff: an Ubuntu 20 image upgrade was
  "looking at" but unscheduled (2023–2025 posts), and **"it is not possible to update to Ubuntu 22.04
  on the VOXL 2 autopilot"** —
  [VOXL 2 feature matrix](https://docs.modalai.com/voxl2-feature-matrix/);
  [Sentinel VOXL2 Ubuntu 18.04→20.04 thread](https://forum.modalai.com/topic/2664/sentinel-voxl2-update-ubuntu-from-18-04-to-20-04.md)
- ModalAI's ROS 2 guidance: ROS 2 Foxy installs natively via `apt-get install voxl-ros2-foxy`; "we
  usually run ROS2 inside a docker container"; "you can't directly use ROS2 humble on the VOXL because
  it requires Ubuntu 22.04." A user reported repeatable `colcon build --symlink-install` failures
  running Humble in Docker on the 18.04 base —
  [Options for running ROS2 Humble](https://forum.modalai.com/post/13560)
- VOXL 2 feature matrix lists "ROS 1 & 2" support and a power envelope of **0.5–8 W** —
  [VOXL 2 feature matrix](https://docs.modalai.com/voxl2-feature-matrix/)

### Inferences
These are my architecture comparisons, built on the findings above and in Q3/Q4. Treat the
qualitative ratings as reasoning, not as sourced claims.

**(a) Driver + SLAM onboard the VOXL 2 under Foxy; ship pose off-board only.**
- Latency: best possible. No air link in the estimation loop. Pose reaches PX4 over the local
  uORB/uXRCE path, not WiFi.
- Bandwidth: ~24 Mbit/s stays entirely inside the airframe (sensor → M0062 → VOXL). Off-board traffic
  is just a pose stream (<50 kbit/s at 50 Hz).
- Reliability: single point of failure is CPU headroom on a board that is already running PX4,
  voxl-px4's DSP drivers, cameras and MPA. The M0062 USB-Ethernet bridge is a second risk (shock
  sensitivity, intermittent-power reports, no link LEDs).
- Complexity: `livox_ros_driver2` *does* build on Foxy upstream, so the driver is a non-issue; the
  hard part is that the mature LIO packages (FAST-LIO2, Point-LIO) are **ROS 1 catkin** projects
  (see Q3), so onboard-Foxy means using a third-party ROS 2 port or doing the port yourself.
- Foxy/Jazzy constraint: satisfied by construction — keep ROS entirely on-vehicle and emit pose over
  plain UDP (or straight into `/fmu/in/vehicle_visual_odometry` over the existing uXRCE-DDS agent,
  which is already domain 1 and already a separate domain from the Jazzy tooling).

**(b) Companion computer running a modern ROS 2 (Humble/Jazzy); VOXL stays flight control.**
- Latency: near-best. LiDAR→companion is direct Ethernet; companion→PX4 pose can go over a wired
  link (USB/UART MAVLink, or Ethernet + uXRCE-DDS into the VOXL's agent).
- Bandwidth: 24 Mbit/s on a dedicated wire. No WiFi involvement.
- Reliability: best estimation reliability (dedicated CPU, no contention with PX4), worst
  *mechanical/electrical* reliability — more connectors, more mass, more power.
- Complexity: highest BOM and integration cost, but lowest *software* risk: Humble/Jazzy is where
  `livox_ros_driver2`, GLIM, and the maintained FAST-LIO ROS 2 forks actually live.
- Foxy/Jazzy constraint: this is the clean way to get a modern ROS 2 in the air. **It must be said
  explicitly that this adds a third ROS domain.** Keep it on its own DDS domain and bridge only pose.

**(c) Stream raw points to the ground station; run SLAM on Jazzy there.**
- Bandwidth: ~24 Mbit/s sustained, plus IMU. On a clean 5 GHz link this is achievable; on the lab's
  open 2.4 GHz `StarlingMax2`/`motive` SSIDs shared with mocap and telemetry it is marginal and
  bursty. UDP point packets are 1422 B — near-MTU, so any fragmentation or retry hurts.
- Latency: worst. Every pose update carries an uplink + processing + downlink. WiFi jitter in the tens
  of ms directly becomes EKF2_EV_DELAY jitter, which the EKF cannot compensate for (EKF2_EV_DELAY is a
  single constant, see Q5).
- Reliability: a WiFi dropout becomes a position-estimate dropout *in flight*. This is a safety
  argument against (c), independent of whether the bandwidth fits.
- Complexity: lowest development effort; everything runs on the Jazzy machine where the tooling
  already works.
- **Verdict: viable as a bench/validation and dataset-recording path, not as a flight position
  source.** Even for recording, prefer logging raw UDP to disk onboard and offloading after the
  flight.

**(d) Bypass ROS entirely: Livox SDK2 directly in a custom process.**
- Latency/bandwidth: identical to (a) minus ROS serialisation overhead.
- Reliability: fewest moving parts at runtime; no DDS discovery on the vehicle at all.
- Complexity: you must reimplement de-skewing and the LIO front-end plumbing that
  `livox_ros_driver2` + FAST-LIO2 give for free, or link FAST-LIO2's core as a library and feed it
  SDK2 callbacks directly (FAST-LIO2's estimator core is ROS-independent; only its I/O is ROS).
- Foxy/Jazzy constraint: **perfectly aligned with the repo's existing convention** (onboard add-ons
  speak plain UDP, not ROS). This is the option that creates zero new DDS surface.

**Recommended shape:** prototype on (c) or on a bench rig to pick the algorithm and tune it against
mocap; then move to (a) if VOXL CPU headroom measurements allow, or (b) if they don't; and consider
(d) as the hardening step once the algorithm is frozen. The sequencing matters because (c) is cheap
to try and answers "does this algorithm work in our hangar" before any airframe work.

### Gaps
- **No measured VOXL 2 CPU headroom figure** while running voxl-px4 + the existing stack. Without
  that, "(a) is feasible" cannot be asserted — it must be measured (`voxl-inspect-cpu` / `top`).
- The M0062's **actual sustained throughput** over its USB 2.0 backhaul is not published. USB 2.0's
  480 Mbit/s nominal is far above 24 Mbit/s, but USB-Ethernet bridges under a 4.19 kernel with a
  loaded CPU are worth measuring rather than assuming.
- Whether the Mid-360 can be powered from the Starling Max 2's existing rails (9–27 V, 6.5 W) was not
  researched; the ModalAI forum thread on exactly this question got no answer on power.
- No source found on whether anyone has successfully run `livox_ros_driver2` on VOXL 2's Foxy build.

---

## Q3. ModalAI LiDAR support in the VOXL SDK / MPA

### Takeaway
There is **no ModalAI-supported Livox (or any 3D spinning/solid-state LiDAR) driver** in the VOXL SDK
or MPA. ModalAI staff have said outright they have no experience with the Mid-360; the only known
path is writing your own MPA pipe.

### Cited Findings
- A Starling 2 Max owner asked ModalAI directly whether VOXL 2 supports the Livox Mid-360 and whether
  an adapter/cable exists. ModalAI's **Eric Katzfey: "We have no experience with this sensor."** A
  moderator replied that the Starling 2 Max is built on VOXL 2, "an open development platform," and
  linked the VOXL 2 I/O connector docs. Katzfey added that ModalAI uses **time-of-flight sensors for
  indoor depth, stereo cameras outdoors, and single-point lidar for height sensing**, and asked
  whether the integration would use a PX4 driver. The asker said the plan was ROS, over the extension
  board's Ethernet port. A follow-up asking whether it ever worked went unanswered —
  [ModalAI forum: Livox Mid 360 compatibility with VOXL 2 on Starling 2 Max](https://forum.modalai.com/topic/4196/clarification-on-livox-mid-360-lidar-compatibility-with-voxl-2-on-starling-2-max-outdoor-drone.md)
- A community workaround for getting external point clouds into ModalAI's mapper: "grab the point
  cloud from whatever api/sdk exists for your lidar and get it into the correct struct so it can pass
  through the MPA and stream to voxl-mapper" —
  [Probing Intel Realsense LIDAR with voxl-mapper](https://forum.modalai.com/topic/2306/probing-intel-realsense-lidar-with-voxl-mapper/11)
- Another user asked about connecting a Unitree LiDAR L1 to a VOXL 2 Sentinel for voxl-mapper; no
  answer appears in the search results —
  [ModalAI forum](https://forum.modalai.com/topic/2306/probing-intel-realsense-lidar-with-voxl-mapper/11)

### Inferences
- ModalAI's perception stack (voxl-mapper, VOA) is built around ToF + stereo depth, not LiDAR. If you
  want the LiDAR cloud to also drive obstacle avoidance, you would write an MPA pipe publisher; if you
  only want *pose* into PX4, you can skip MPA entirely.
- The "open development platform / here are the connector docs" response is the standard ModalAI
  answer for unsupported peripherals — expect zero vendor support on this integration.

### Gaps
- `voxl-mpa-tools` / `libmodal-pipe` source was not searched directly for any `pointcloud` pipe type.
  There *is* a point-cloud concept in MPA (voxl-mapper consumes one), but the exact struct and whether
  it can carry 200k pts/s was not verified.

---

## Q4. LiDAR-inertial odometry algorithm comparison

### Takeaway
FAST-LIO2 is the right default: it is the only one of these with **published ARM benchmarks**, it
handles Livox non-repetitive patterns natively, and it is the lightest. Its cost is no loop closure
and ROS 1 upstream. Point-LIO adds kHz-rate output and aggressive-motion robustness but is also ROS 1
and has no Mid-360 config upstream. GLIM is the most accurate and the only one with real loop closure,
but is reported to need GPU acceleration for real-time. FAST-LIVO2 costs ~10 ms/frame more than
FAST-LIO2 for the visual front-end.

### Cited Findings — FAST-LIO2
- Benchmark hardware: Intel = **DJI Manifold 2-C, 1.8 GHz quad-core i7-8550U, 8 GB RAM**
  ("a lightweight UAV onboard computer"); ARM = **Khadas VIM3, 2.2 GHz quad-core Cortex-A73, 4 GB RAM** —
  [FAST-LIO2 paper (ar5iv)](https://ar5iv.labs.arxiv.org/html/2107.06829)
- **Table VI — average total ms per scan, Intel (1000 m config) vs ARM** (spinning-LiDAR and Livox
  Horizon datasets):

  | Sequence | Intel (ms) | ARM (ms) |
  |---|---|---|
  | lili_6 | 12.56 | 45.58 |
  | lili_7 | 17.61 | 65.89 |
  | lili_8 | 15.31 | 57.29 |
  | utbm_8 | 22.05 | 100.00 |
  | utbm_9 | 25.44 | 91.05 |
  | utbm_10 | 22.48 | 94.62 |
  | ulhk_4 | 20.14 | 91.12 |
  | ulhk_5 | 23.90 | 68.04 |
  | ulhk_6 | 31.56 | 92.38 |
  | nclt_4 | 15.72 | 69.09 |
  | nclt_5 | 16.60 | 68.95 |
  | nclt_6 | 15.84 | 66.64 |
  | nclt_7 | 16.87 | 70.24 |
  | nclt_8 | 14.25 | 57.03 |
  | nclt_9 | 13.65 | 54.82 |
  | nclt_10 | 21.79 | 89.65 |
  | liosam_1 | 14.77 | 60.60 |
  | liosam_2 | 11.47 | 45.27 |
  | liosam_3 | 16.64 | 44.26 |

  (lili_* were recorded with a **Livox Horizon**.) —
  [FAST-LIO2 paper (ar5iv)](https://ar5iv.labs.arxiv.org/html/2107.06829)
- **Table VII — Livox Avia handheld sequence, 756 points/scan, mean ms:** state estimation Intel 1.66
  / **ARM 4.75**; mapping Intel 0.13 / **ARM 0.43**; total Intel 1.82 / **ARM 5.23** —
  [FAST-LIO2 paper (ar5iv)](https://ar5iv.labs.arxiv.org/html/2107.06829)
- The paper states FAST-LIO2 **"can also achieve 10 Hz real-time performance"** on the ARM platform,
  and that no prior work had demonstrated this on an ARM-based platform. For the small-scan Avia case
  it notes ARM processing "occasionally exceeds the sampling period 10 ms" but only rarely, with the
  average well below 10 ms, and that these occasional overruns usually don't affect a downstream
  controller because the IMU-propagated state covers the gap —
  [FAST-LIO2 paper (ar5iv)](https://ar5iv.labs.arxiv.org/html/2107.06829)
- FAST-LIO2 is explicitly **"an odometry without any loop detection or correction."** For the
  benchmark, the loop-closure modules of LILI-OM and LIO-SAM were deactivated for fairness —
  [FAST-LIO2 paper (ar5iv)](https://ar5iv.labs.arxiv.org/html/2107.06829)
- ikd-Tree-only per-scan cost on Intel (Table III) ranged **9.57–25.77 ms** across sequences;
  max tree size ~2×10⁶ points (utbm) and 3.6×10⁶ points (nclt) —
  [FAST-LIO2 paper (ar5iv)](https://ar5iv.labs.arxiv.org/html/2107.06829)
- Abstract: "up to 100 Hz odometry and mapping in large outdoor environments," applicable to "Intel
  and ARM-based processors" —
  [FAST-LIO2 arXiv abstract](https://web3.arxiv.org/abs/2107.06829)
- Upstream FAST_LIO is a **ROS 1 / catkin_make** project. For Livox sensors it "only supports the data
  collected by the `livox_lidar_msg.launch`" because only that path's `CustomMsg` carries the
  per-point timestamps needed for motion de-skew; `livox_lidar.launch` "can not produce it right now."
  Config needs point-cloud topic, IMU topic, and `extrinsic_T` / `extrinsic_R` (rotation matrix only) —
  [FAST_LIO fork README](https://forgejo.ikko-lab.k.hosei.ac.jp/kasai/FAST_LIO);
  [OpenELab Mid-360S + FAST-LIO2 guide](https://openelab.com/blogs/learn/livox-mid-360s-fast-lio2-slam-real-time-mapping-workflow-ros2)

### Cited Findings — Point-LIO
- "Robust High-Bandwidth Lidar-Inertial Odometry," HKU MARS, published in *Advanced Intelligent
  Systems*. Claims odometry output at **4k–8 kHz** (it updates state per LiDAR point rather than per
  scan). Claims robustness "to IMU saturation and severe vibration, and other aggressive motions
  (75 rad/s in our test)" —
  [Point-LIO GitHub](https://github.com/hku-mars/Point-LIO)
- **ROS 1 only** (catkin_make, tested Ubuntu 20.04 / Noetic; requires Eigen, `livox_ros_driver`,
  `pcl-conversions`). No ROS 2 support mentioned. Main Livox example is the **Avia**; the README says
  the Livox serial line "theoretically" supports mid-70 and mid-40 — **the Mid-360 is not named**.
  Velodyne (16/32/64) and Ouster are covered. Livox data must come from `livox_lidar_msg.launch` —
  [Point-LIO GitHub](https://github.com/hku-mars/Point-LIO)
- README calls the system "computationally efficient" but gives **no CPU/memory/hardware figures**.
  **Loop closure is not mentioned** — odometry and mapping only. Requires LiDAR/IMU time sync;
  saturation values, accel units and extrinsics must be set in YAML —
  [Point-LIO GitHub](https://github.com/hku-mars/Point-LIO)
- Maintenance signal: the repo page showed 17 commits on the `point-lio-with-grid-map` branch,
  **67 open issues**, 1 open PR; last-commit date not shown —
  [Point-LIO GitHub](https://github.com/hku-mars/Point-LIO)
- A 2026 embedded-drone-LIO paper characterises Point-LIO as updating state per LiDAR point, raising
  output rate to ~kHz, but says it doesn't address executor concurrency on embedded hardware —
  [arXiv:2607.22145](https://arxiv.org/pdf/2607.22145) *(this preprint was not independently verified;
  treat with caution)*

### Cited Findings — GLIM
- Officially "tested on Ubuntu 22.04 / 24.04 with CUDA 12.2 / 12.6 / 13.1, and **NVIDIA Jetson Orin
  (JetPack 6.1)**." **CUDA is optional** — the PPA ships non-CUDA packages (e.g.
  `ros-jazzy-glim-ros`) alongside CUDA variants; source builds enable it with `BUILD_WITH_CUDA=ON` —
  [GLIM installation docs](https://koide3.github.io/glim/installation.html)
- **ROS 2 only** in the docs: **Humble (22.04) and Jazzy (24.04)**. ROS 1 not mentioned —
  [GLIM installation docs](https://koide3.github.io/glim/installation.html)
- Independent benchmark on MCD VIRAL: GLIM had **the best average ATE (0.508 m)** "owing to its robust
  sliding window optimization. **However, it required GPU acceleration for real-time processing.**"
  GLIM's global mapping uses scan-matching-based loop detection and pose-graph trajectory
  optimization (loop closure was disabled for the odometry-only comparison). In the same comparison
  SLICT had better ATE (0.638 m) but "was computationally intensive and failed to achieve real-time
  processing" —
  [arXiv:2505.01017](https://arxiv.org/pdf/2505.01017)

### Cited Findings — FAST-LIVO2
- FAST-LIVO2 (LiDAR-inertial-**visual**) reports that **FAST-LIO2's average per-frame processing time
  is ~10.35 ms *less* than FAST-LIVO2's**, because FAST-LIO2 doesn't process image measurements —
  [FAST-LIVO2 paper](https://arxiv.org/pdf/2408.14035)
- FAST-LIVO2 runs on CPU; no GPU requirement surfaced in the sources found —
  [FAST-LIVO2 paper](https://arxiv.org/pdf/2408.14035)

### Inferences
- **Scaling the ARM benchmark to the VOXL 2.** Khadas VIM3 = 4× Cortex-A73 @2.2 GHz. VOXL 2's QRB5165
  is 8 cores up to 3.091 GHz ([VOXL 2 feature matrix](https://docs.modalai.com/voxl2-feature-matrix/)),
  with substantially newer big cores. FAST-LIO2 is largely single-threaded in its hot path, so the
  relevant comparison is single-core: a ~3 GHz modern core should beat an A73 @2.2 GHz by roughly
  1.5–2.5×. Applying that to the Table VI figures (45–100 ms/scan) gives ~20–65 ms/scan — i.e. it
  should fit a 10 Hz budget with margin, but **not** with the headroom you'd want while PX4, the
  camera pipelines and MPA are also running. This is extrapolation, not a measurement.
- The Mid-360 at 200k pts/s and 10 Hz framing gives ~20,000 points/scan — between the Avia handheld
  case (756 pts/scan, 5.23 ms ARM) and the 64-beam spinning datasets (~100 ms ARM). The Livox Horizon
  `lili_*` rows (45–66 ms ARM) are the closest analogue in the table.
- **Loop closure is probably irrelevant for this use case.** In a single hangar with short flights and
  mocap available as truth, drift accumulation over a few minutes matters more than global
  consistency, and loop closure introduces discontinuous pose jumps that PX4's EKF handles badly
  (see Q6 on `reset_counter`). FAST-LIO2's lack of loop closure is a feature here, not a defect.
- **Maturity ranking for this project:** FAST-LIO2 (most deployed, best-documented ARM story, no loop
  closure, ROS 1 upstream) > GLIM (best accuracy, native ROS 2 Humble/Jazzy, but GPU-hungry and
  heavier) > Point-LIO (great for aggressive flight, ROS 1 only, no Mid-360 config, 67 open issues) >
  FAST-LIVO2 (adds a camera you don't need and ~10 ms/frame) > LIO-SAM (designed for spinning LiDARs
  with ring/time fields; Livox support requires forks).
- **The ROS 2 port problem is the real decision driver.** FAST-LIO2 and Point-LIO are ROS 1; GLIM is
  ROS 2. If you want ROS 2 onboard, GLIM is the only first-party option — and GLIM wants Humble/Jazzy,
  which VOXL 2 cannot run natively. That pushes GLIM toward architecture (b).

### Gaps
- **No published CPU/RAM figures for Point-LIO** at all — neither the README nor the sources found.
- **No benchmark of FAST-LIO2 or Point-LIO on a Jetson Orin Nano** was found, nor any on a QRB5165.
- **LIO-SAM** was not researched directly in this pass; its Livox support status is asserted here from
  the FAST-LIO2 paper's framing only (it appears as a baseline with loop closure disabled).
- **Livox's own mapping packages** (`livox_mapping`, `LIO-Livox`, `livox_horizon_loam`) were not
  researched. They are generally considered superseded by FAST-LIO2 but this was not verified.
- GLIM's **CPU-only real-time throughput** is unquantified; the docs don't discuss performance and the
  one benchmark found says GPU was required.
- Super-LIO ([arXiv:2509.05723](https://arxiv.org/pdf/2509.05723v1)) reportedly compares FAST-LIO2,
  Faster-LIO and iG-LIO per-frame time and CPU on both x86 and ARM, but the tables were not extracted;
  this is the single best next source for ARM numbers.

---

## Q5. Companion computer candidates, if needed

### Takeaway
Jetson Orin Nano / Orin NX are the standard answers and are the only ones that make GLIM's CUDA path
available; Raspberry Pi 5 is the cheap CPU-only option. Power is well documented (7–15 W Orin Nano,
10–40 W Orin NX); **module weight is not published** by NVIDIA in any source found.

### Cited Findings
- **Orin Nano** series: configurable **7 W–15 W**, up to 40 TOPS. 8 GB module 7–15 W; 4 GB variant
  7–10 W. JetPack 6.2 added 25 W and uncapped MAXN SUPER reference modes for Orin Nano —
  [NVIDIA Jetson Orin Nano datasheet](https://static6.arrow.com/aropdfconversion/b4f120a8c52d5dd5e59875b129c4f94b77c7c3b6/jetson-orin-nano-datasheet-web.pdf);
  [NVIDIA JetPack 6.2 Super Mode blog](https://developer.nvidia.com/blog/nvidia-jetpack-6-2-brings-super-mode-to-nvidia-jetson-orin-nano-and-jetson-orin-nx-modules/)
- **Orin NX**: 8 GB module reference modes 10 W / 15 W / 20 W + MAXN; 16 GB module 10 W / 15 W / 25 W
  + MAXN; JetPack 6.2 adds a 40 W mode with MAXN SUPER —
  [NVIDIA JetPack 6.2 Super Mode blog](https://developer.nvidia.com/blog/nvidia-jetpack-6-2-brings-super-mode-to-nvidia-jetson-orin-nano-and-jetson-orin-nx-modules/);
  [ConnectTech Orin module comparison](https://connecttech.com/orin-module-comparison/)
- GLIM is explicitly tested on **NVIDIA Jetson Orin with JetPack 6.1** —
  [GLIM installation docs](https://koide3.github.io/glim/installation.html)
- For reference, the VOXL 2 itself draws **0.5–8 W** —
  [VOXL 2 feature matrix](https://docs.modalai.com/voxl2-feature-matrix/)
- The Mid-360 alone adds **265 g and 6.5 W** —
  [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs)

### Inferences
- A companion computer must be budgeted at roughly **(module + carrier + heatsink + cabling)**, not
  the bare module. Typical Orin Nano/NX carrier-board solutions for drones land in the 80–150 g range
  with cooling; this is from general knowledge, **not sourced here**.
- Power budget for the full add-on: Mid-360 (6.5 W) + Orin Nano (7–15 W) ≈ **14–22 W** continuous,
  plus 265 g of sensor plus ~100 g of compute. On a Starling-class airframe that is a material hit to
  endurance and will change the thermal picture.
- **Raspberry Pi 5** (quad Cortex-A76 @2.4 GHz) is architecturally in the same class as the Khadas
  VIM3 used in the FAST-LIO2 paper but about a generation faster per core; it should run FAST-LIO2 at
  10 Hz for a Mid-360 and is the cheapest way to get a modern ROS 2 (Humble/Jazzy on 24.04) airborne.
  It has native gigabit Ethernet, which neatly solves the Mid-360 interface problem. **No benchmark
  source was found for FAST-LIO2 on a Pi 5** — this is extrapolation.
- If GLIM is the chosen algorithm, the companion must be a Jetson (CUDA). If FAST-LIO2 is chosen, a
  Pi 5 or small x86 (N100-class) is sufficient and avoids JetPack's integration overhead.
- **The strongest argument for the companion route is not compute — it is the ROS version.** It is the
  only way to run Humble/Jazzy in the air, and it keeps SLAM failures from being able to starve PX4 of
  CPU on the flight-control board.

### Gaps
- **No published module weight** for Orin Nano or Orin NX in any source found; the only weight figure
  was a retailer's 0.3 kg for a *developer kit* (carrier board included), which is not the module.
- No sourced benchmark of any LIO package on Raspberry Pi 5 or on an N100-class x86.
- Mounting/vibration isolation for a 265 g LiDAR on a Starling-class frame was not researched.

---

## Q6. PX4 v1.14 fusion path: how SLAM pose gets into EKF2

### Takeaway
There is exactly **one** external-vision input to EKF2 in PX4 v1.14 — the `vehicle_visual_odometry`
uORB topic — and `vehicle_mocap_odometry` exists as a topic name but is **not subscribed by EKF2**.
So mocap and SLAM cannot be fused simultaneously; they contend for the same single channel.

### Cited Findings
- **EKF2 subscribes only to `vehicle_visual_odometry`** in v1.14. From `EKF2.hpp`:
  `uORB::Subscription _ev_odom_sub{ORB_ID(vehicle_visual_odometry)};` — there is no mocap subscription —
  [PX4 v1.14.0 EKF2.hpp](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/EKF2.hpp)
- PX4 docs confirm: "EKF2 subscribes only to `vehicle_visual_odometry`," which receives
  `VISION_POSITION_ESTIMATE` and `ODOMETRY` (with `MAV_FRAME_LOCAL_FRD`). **`ODOMETRY` is the only
  message that carries linear velocities** —
  [PX4 v1.14 external position estimation](https://docs.px4.io/v1.14/en/ros/external_position_estimation.html)
- **`VehicleOdometry.msg` (v1.14.0), complete:**
  ```
  uint64 timestamp         # time since system start (microseconds)
  uint64 timestamp_sample
  uint8 POSE_FRAME_UNKNOWN = 0
  uint8 POSE_FRAME_NED     = 1  # NED earth-fixed frame
  uint8 POSE_FRAME_FRD     = 2  # FRD world-fixed frame, arbitrary heading reference
  uint8 pose_frame
  float32[3] position      # meters, frame per pose_frame. NaN if invalid/unknown
  float32[4] q             # quaternion FRD body -> reference frame. First value NaN if invalid
  uint8 VELOCITY_FRAME_UNKNOWN  = 0
  uint8 VELOCITY_FRAME_NED      = 1
  uint8 VELOCITY_FRAME_FRD      = 2
  uint8 VELOCITY_FRAME_BODY_FRD = 3
  uint8 velocity_frame
  float32[3] velocity           # m/s, frame per velocity_frame. NaN if invalid
  float32[3] angular_velocity   # body-fixed rad/s. NaN if invalid
  float32[3] position_variance
  float32[3] orientation_variance
  float32[3] velocity_variance
  uint8 reset_counter
  int8 quality
  # TOPICS vehicle_odometry vehicle_mocap_odometry vehicle_visual_odometry
  # TOPICS estimator_odometry
  ```
  Note the header comment: "Fits ROS REP 147 for aerial vehicles." —
  [PX4 v1.14.0 VehicleOdometry.msg](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/msg/VehicleOdometry.msg)
- **`EKF2_EV_CTRL`** (v1.14 source, default **15**): "Set bits in the following positions to enable:
  0 : Horizontal position fusion; 1 : Vertical position fusion; 2 : 3D velocity fusion; 3 : Yaw."
  min 0, max 15 —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- **`EKF2_AID_MASK` is fully deprecated in v1.14**: bits 3, 4, 6, 8 say "Deprecated, use EKF2_EV_CTRL
  instead"; bit 7 "use EKF2_GPS_CTRL"; bit 5 "use EKF2_DRAG_CTRL". Default 0, all bits marked unused —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- **`EKF2_HGT_REF`** (default 1 = GPS): value 0 Barometric pressure, 1 GPS, 2 Range sensor,
  **3 Vision**. "When multiple height sources are enabled at the same time, the height estimate will
  always converge towards the reference height source selected by this parameter." Warning in source:
  "The range sensor and vision options should only be used when for operation over a flat surface as
  the local NED origin will move up and down with ground level." —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- **`EKF2_GPS_CTRL`** (default 7): bit 0 Lon/lat, bit 1 Altitude, bit 2 3D velocity, bit 3 Dual antenna
  heading. **`EKF2_BARO_CTRL`** (default 1): boolean barometric height aiding —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- **`EKF2_EV_DELAY`** (default **0** ms; min 0, max 300 ms, `@reboot_required true`): "Vision Position
  Estimator delay relative to IMU measurements" —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- **`EKF2_EV_NOISE_MD`** (default 0): "If set to 0 (default) the measurement noise is taken from the
  vision message and the EV noise parameters are used as a **lower bound**. If set to 1 the
  observation noise is set from the parameters directly." —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- **`EKF2_EV_QMIN`** (default 0, range 0–100): "External vision will only be started and fused if the
  quality metric is above this threshold. The quality metric is a completely **optional** field
  provided by some VIO systems." —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- Noise and gate defaults: **`EKF2_EVP_NOISE` 0.1** (position, m), **`EKF2_EVV_NOISE` 0.1** (velocity),
  **`EKF2_EVA_NOISE` 0.1** (angle), **`EKF2_EVP_GATE` 5.0**, **`EKF2_EVV_GATE` 3.0**.
  **`EKF2_EV_POS_X/Y/Z`** all default 0.0 — position of the vision sensor / mocap markers relative to
  the body frame —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c);
  [PX4 v1.14 external position estimation](https://docs.px4.io/v1.14/en/ros/external_position_estimation.html)
- **Message rate**: stream external vision at **30–50 Hz** ("30 Hz minimum if covariances are
  included"). Lower rates can prevent EKF2 from fusing them —
  [PX4 v1.14 external position estimation](https://docs.px4.io/v1.14/en/ros/external_position_estimation.html)
- **Frames**: PX4 uses **FRD** body and **NED or FRD** world; ROS uses FLU/ENU. For OptiTrack the docs
  give the axis swap `x_mav = x_mocap`, `y_mav = z_mocap`, `z_mav = -y_mocap`, with the quaternion `w`
  unchanged and `x,y,z` swapped the same way —
  [PX4 v1.14 external position estimation](https://docs.px4.io/v1.14/en/ros/external_position_estimation.html)
- **Reboot the flight controller after changing these parameters** —
  [PX4 v1.14 external position estimation](https://docs.px4.io/v1.14/en/ros/external_position_estimation.html)
- EKF2_EV_DELAY guidance: it is "the offset between the vision timestamp and the actual capture time
  on the IMU clock." It can be 0 with accurate timestamping and time sync (e.g. NTP), but usually
  needs empirical tuning. **Estimate it from logs by comparing IMU and EV rates (enable bit 7 of
  `SDLOG_PROFILE`), then tune to minimise EKF innovations during dynamic manoeuvres** —
  [PX4 v1.14 external position estimation](https://docs.px4.io/v1.14/en/ros/external_position_estimation.html)

### Inferences
- The repo's current config (`EKF2_EV_CTRL=11`) decodes as bits 0+1+3 = **horizontal position +
  vertical position + yaw**, with **3D velocity fusion OFF** (bit 2 clear). That is exactly right for
  a pose-only mocap feed with NaN velocities. A SLAM source *can* provide velocity, in which case
  `EKF2_EV_CTRL=15` becomes available — but see the migration note below about not changing two things
  at once.
- Their `EKF2_EV_DELAY=50` is a deliberate deviation from the 0 default, consistent with a
  ground-side mocap bridge over WiFi. **A SLAM pipeline will have a completely different delay** and
  this parameter must be re-measured, not inherited.
- With `EKF2_EV_NOISE_MD=0` (default), a SLAM node that publishes real `position_variance` gets its
  own uncertainty respected, with 0.1 m as the floor. This is the correct mode for SLAM, because SLAM
  covariance is genuinely informative (it blows up during degeneracy) whereas mocap covariance is
  constant. **Switching to `EKF2_EV_NOISE_MD=0` with honest covariances is one of the cheapest safety
  wins available** — the EKF will automatically de-weight the SLAM solution when it is uncertain.
- `EKF2_EV_QMIN` + the `quality` field is the designed-in hook for a SLAM health signal. The repo
  already sends `quality=100` from the mocap bridge. A SLAM bridge should map a real degeneracy metric
  (e.g. the minimum eigenvalue of the registration Hessian, see Q8) onto `quality` 0–100 and set
  `EKF2_EV_QMIN` to a non-zero threshold.
- `reset_counter` in `VehicleOdometry` is the mechanism for telling EKF2 "my estimate just jumped
  discontinuously" (loop closure, re-localisation). A SLAM bridge **must** increment it on any pose
  discontinuity, or EKF2 will treat a loop-closure jump as a huge innovation and reject or diverge.
- The `# TOPICS vehicle_odometry vehicle_mocap_odometry vehicle_visual_odometry` line means
  `vehicle_mocap_odometry` is still a *published* topic name in v1.14 (MAVLink `ATT_POS_MOCAP` lands
  there) but, per `EKF2.hpp`, **nothing in EKF2 reads it**. This is the key structural fact for Q7.

### Gaps
- **Where the v1.14 → v1.15/v1.16 external-vision interface changed was not researched in this pass.**
  I know the v1.13→v1.14 break (`EKF2_AID_MASK` → `EKF2_EV_CTRL`/`EKF2_GPS_CTRL`, and the
  `VehicleOdometry` message restructure to `pose_frame`/`velocity_frame`) from the source above, but I
  did not verify what newer PX4 changed. **The report writer should flag this as unverified.** The
  practical warning stands regardless: copy-pasted configs from PX4 main/v1.15 docs will not match
  v1.14, and px4_msgs must be pinned to the v1.14 release branch for uXRCE-DDS to work at all — which
  is already a known pain point in this repo (iron rule 5 cites a v1.14 px4_msgs mismatch).
- The exact uXRCE-DDS topic name/QoS for `fmu/in/vehicle_visual_odometry` in v1.14's `dds_topics.yaml`
  was not re-verified here; the repo already has this working for mocap, so it is known-good locally.

---

## Q7. Running LiDAR SLAM alongside mocap, and the migration path

### Takeaway
**EKF2 in PX4 v1.14 cannot take two external-vision sources — there is one subscription,
`vehicle_visual_odometry`, and whoever publishes to it wins.** The sane migration path is therefore
not "fuse both" but "run SLAM in parallel as a *passive observer* scored against mocap, then cut over
in stages." The mocap volume is a near-ideal SLAM validation rig and should be used that way.

### Cited Findings
- Single EV subscription in v1.14: `uORB::Subscription _ev_odom_sub{ORB_ID(vehicle_visual_odometry)};`
  — no second EV or mocap subscription exists in `EKF2.hpp` —
  [PX4 v1.14.0 EKF2.hpp](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/EKF2.hpp)
- PX4 docs state the same from the user side: "EKF2 subscribes only to `vehicle_visual_odometry`" —
  [PX4 v1.14 external position estimation](https://docs.px4.io/v1.14/en/ros/external_position_estimation.html)
- The PX4 v1.14 docs page on external position estimation **does not cover switching between, or
  combining, multiple external sources** —
  [PX4 v1.14 external position estimation](https://docs.px4.io/v1.14/en/ros/external_position_estimation.html)
- `EKF2_EV_QMIN` exists precisely so EV fusion can be started/stopped on a quality metric —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- Height sources *can* be multiplexed independently of EV: `EKF2_HGT_REF` selects which of
  baro/GPS/range/vision is the reference when several are enabled —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)

### Inferences — the proposed migration path
This is my synthesis, not a sourced procedure. It is structured so that nothing is ever trusted in
flight before it has been measured on the ground against mocap.

**Stage 0 — Offline, no flight, no PX4 changes.**
Mount the Mid-360 on the airframe (or a handheld rig carrying the same mocap markers). Record
synchronised bags: raw Livox UDP/`CustomMsg` + IMU, and the OptiTrack pose stream, on a common clock.
Run FAST-LIO2 offline on a workstation. Compute ATE/RPE of the SLAM trajectory against mocap. This is
the single highest-value experiment available and costs nothing but bag storage.
- Critical detail: solve the **LiDAR-to-marker-frame extrinsic** here (hand-eye calibration against
  mocap), because `EKF2_EV_POS_X/Y/Z` must later describe the LiDAR's offset from the body origin, and
  a wrong extrinsic shows up as motion-correlated position error that is easy to mistake for drift.

**Stage 1 — Online shadow mode, mocap still flying the aircraft.**
Run the SLAM pipeline live during ordinary mocap flights, publishing **nowhere near** PX4 — to a
separate UDP port / topic only. Log SLAM pose and mocap pose together, every flight. Build a track
record: drift rate per minute, behaviour during yaw-only rotations, behaviour near the hangar's empty
walls, recovery after an occlusion. Measure the end-to-end latency here too (Q8).
- This stage costs nothing in risk and is where almost all the learning happens. Run it for weeks.

**Stage 2 — Height only.**
If `EKF2_HGT_REF` behaviour is being changed at all, note that vision height and vision horizontal
position both ride the same EV message, so there is no clean "SLAM for Z only" split without a
synthetic message. **Probably skip this stage**; it is listed only to flag that height cannot be
separated from position across *two different* EV sources.

**Stage 3 — Bench cutover.**
On a tethered/props-off aircraft, switch the publisher on `fmu/in/vehicle_visual_odometry` from the
mocap bridge to the SLAM bridge. Verify in QGC that EKF2 accepts it, local position becomes valid,
and `estimator_innovations` for EV position stay inside the gates (`EKF2_EVP_GATE` 5.0). Re-tune
`EKF2_EV_DELAY` against the measured SLAM latency, and re-check innovations during hand-held
dynamic motion.

**Stage 4 — Switchable publisher, mocap as the safety net.**
Build a single "EV mux" process that owns the `vehicle_visual_odometry` publication and selects
between mocap and SLAM. Because EKF2 has one input, the arbitration has to live outside PX4. Design
notes:
- Switch on the **ground**, not in flight. An in-flight source swap injects a step into the EV
  position, which EKF2 sees as an enormous innovation. If an in-flight swap is ever needed, the mux
  must align the SLAM frame to the mocap frame (apply the rigid transform measured at the switch
  instant) **and** increment `reset_counter`.
- Keep mocap running in parallel the whole time as the *logged* ground truth, even when SLAM is
  driving. Mocap is then your post-flight scorer for every SLAM flight.
- Publish a real `quality` from the SLAM node (degeneracy metric) and set `EKF2_EV_QMIN` above zero so
  PX4 itself will stop fusing a sick SLAM solution.

**Stage 5 — SLAM-only, outside the mocap volume.**
Only after Stage 4 has accumulated flights with bounded, characterised SLAM-vs-mocap error.

**Why not "fuse both":** even if EKF2 could take two EV sources, fusing mocap and SLAM would mask
exactly the SLAM failures you are trying to detect. The value of the mocap volume is as an
*independent* scorer, and that requires keeping it out of the loop.

### Gaps
- I did not verify whether any PX4 version (v1.15+) added a second EV instance or an EV source
  selector. If the report writer wants to recommend a newer PX4, this needs checking.
- No source found describing anyone's published procedure for mocap-validated SLAM cutover on PX4.
  The staged plan above is engineering judgement, not a cited best practice.

---

## Q8. Latency, EKF2_EV_DELAY, and measuring true end-to-end delay

### Takeaway
PX4's own guidance is to estimate the delay from logs and then tune it to minimise EKF innovations
during dynamic manoeuvres — and a mocap volume makes this far easier than PX4 assumes, because you can
cross-correlate SLAM pose against mocap pose directly.

### Cited Findings
- `EKF2_EV_DELAY` is "the offset between the vision timestamp and the actual capture time on the IMU
  clock." It "can be 0 with accurate timestamping and time sync (e.g., NTP), but usually needs
  empirical tuning." PX4's method: estimate from logs by comparing IMU and EV rates (**enable bit 7 of
  `SDLOG_PROFILE`**), then tune to minimise EKF innovations during dynamic manoeuvres —
  [PX4 v1.14 external position estimation](https://docs.px4.io/v1.14/en/ros/external_position_estimation.html)
- Range: 0–300 ms, default 0, **reboot required** to take effect —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- The `VehicleOdometry` message carries both `timestamp` and a separate **`timestamp_sample`** field —
  [PX4 v1.14.0 VehicleOdometry.msg](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/msg/VehicleOdometry.msg)
- Mid-360 supports **IEEE 1588-2008 (PTPv2)** and GPS time sync, and its UDP packets carry an 8-byte
  nanosecond timestamp for the first point in the packet —
  [Livox Mid-360 specs](https://www.livoxtech.com/mid-360/specs);
  [Livox Mid-360 Ethernet protocol](https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/livox_eth_protocol_mid360.html)

### Inferences
- **The delay budget for an onboard FAST-LIO2 pipeline**, built from the cited numbers:
  LiDAR scan accumulation (half a 100 ms frame if 10 Hz framing = ~50 ms, or much less with
  higher `publish_freq`) + UDP transport (<1 ms on wire) + driver assembly + LIO processing
  (~20–65 ms extrapolated for QRB5165; 45–66 ms measured on A73 for Livox Horizon) + bridge/uORB
  publish (~1–5 ms). Plausible total: **70–130 ms**. That is well inside `EKF2_EV_DELAY`'s 300 ms
  range but is **much larger than their current mocap value of 50 ms**, and large enough that getting
  it wrong meaningfully degrades attitude/velocity estimates during aggressive manoeuvres.
- **Scan accumulation is the dominant and most controllable term.** Raising `publish_freq` in the
  Livox driver (smaller, more frequent scans) cuts accumulation latency at the cost of fewer points
  per registration. FAST-LIO2's Table VII shows it handles 756-point scans in 5.23 ms on ARM, so small
  frequent scans are computationally viable — this is a real lever.
- **How to measure the true delay, using the mocap volume** (my procedure, not sourced):
  1. Fly or hand-carry an aggressive, broadband-excitation motion (sharp lateral translations, not
     smooth circles) inside the mocap volume.
  2. Log SLAM pose and mocap pose on a common clock (PTP, or NTP plus a measured offset).
  3. **Cross-correlate the two position signals** and find the lag that maximises correlation. That
     lag *is* the end-to-end pipeline delay, measured directly, with no EKF in the loop.
  4. Set `EKF2_EV_DELAY` to that value, reboot, then refine by minimising `estimator_innovations` EV
     position innovations during the same manoeuvre — PX4's documented method, now starting from a
     correct initial guess instead of a blind search.
  This is strictly better than PX4's innovation-minimisation alone, and it is only possible because
  they have mocap. It is a concrete reason the mocap rig is valuable even after SLAM works.
- `timestamp_sample` should carry the **LiDAR scan time**, not the publish time. If the bridge sets
  both fields to "now," `EKF2_EV_DELAY` has to absorb the entire pipeline; if `timestamp_sample` is set
  correctly from the Livox packet timestamp, `EKF2_EV_DELAY` only has to cover the residual clock
  offset. Doing this properly requires PTP-syncing the Mid-360 to the compute board's clock, which the
  sensor supports natively.
- Jitter, not mean delay, is the real enemy: `EKF2_EV_DELAY` is a single constant, so variance in the
  pipeline delay is unmodelled noise. This is the strongest technical argument against architecture
  (c) (SLAM on the ground over WiFi).

### Gaps
- No source quantifies the actual latency of a Livox + FAST-LIO2 pipeline end-to-end; the budget above
  is assembled from component figures.
- Whether PTP sync between a Mid-360 and a Linux host is straightforward in practice (PHC support on
  the NIC, `ptp4l`/`phc2sys` config) was not researched — and note that the M0062's USB-Ethernet
  bridge almost certainly lacks hardware timestamping, which would make PTP software-only and much
  less precise. This is another point in favour of a companion computer with a real NIC.

---

## Q9. Known failure modes and safety configuration

### Takeaway
LIO degeneracy in geometrically poor indoor spaces is a well-documented, actively-researched failure
mode, and a large empty hangar is close to the worst case. PX4 gives you two hooks —
`EKF2_EV_QMIN`/`quality` and `reset_counter` — and the research literature gives you a detection
metric (minimum eigenvalue / Hessian condition number) that maps directly onto `quality`.

### Cited Findings — degeneracy
- Definition and cause: "Degeneracy in LiDAR SLAM occurs when the optimization becomes
  ill-conditioned, typically in environments with repetitive or sparse geometric features, such as
  **corridors or open fields**. This leads to ambiguous pose estimation and unreliable mapping
  results." —
  [D²-LIO, arXiv:2508.14355](https://arxiv.org/pdf/2508.14355)
- Tuning is scene-dependent: "the parameters of LiDAR (-inertial) odometry are mostly set for open
  space; thus, if the same parameters suitable for the open space are applied in a corridor-like
  scene, it results in **divergence** of odometry methods." —
  [AdaLIO, as quoted in arXiv:2508.14355](https://arxiv.org/pdf/2508.14355)
- Empirical detection signal from an underground-tunnel study: "as the robot entered long corridor
  sections with insufficient features, the **minimum eigenvalue (λ3) was observed to decrease**. This
  indicates that geometric constraints are relatively insufficient in long corridor sections." —
  [KNS underground tunnel LiDAR study](https://www.kns.org/files/pre_paper/55/26S-497-심수곤.pdf)
- Detection method families: *geometric* (X-ICP "incorporates a geometry-aware detection scheme that
  evaluates degeneracy in both rotational and translational subspaces without requiring prior maps");
  *optimization-based* (Hessian condition number); *data-driven* (SVM, entropy-based — "often require
  extensive training and incur high computational costs") —
  [D²-LIO, arXiv:2508.14355](https://arxiv.org/pdf/2508.14355)
- Mitigation families: *passive* — "introduce complementary sensors like IMUs or visual odometry to
  provide external constraints when degeneracy is detected"; *active* — "solution remapping redirects
  the solver toward well-conditioned directions, while regularization terms or hard constraints are
  introduced to stabilize optimization" —
  [D²-LIO, arXiv:2508.14355](https://arxiv.org/pdf/2508.14355)
- AdaLIO's approach: "we first check the degeneracy by checking whether the surroundings are
  corridor-like environments. If so, the parameters relevant to **voxelization and normal vector
  estimation** are adaptively changed to increase the number of correspondences." —
  [as quoted in arXiv:2508.14355](https://arxiv.org/pdf/2508.14355)
- Recent degeneracy-aware LIO variants: **ALIVE-LIO** (neural net predicts body-frame velocity, fused
  into the ESKF "only when degeneracy is detected, providing effective state updates along degenerate
  directions"); **LODESTAR** (degeneracy-aware Schmidt-Kalman filter, classifies states active/fixed,
  prunes measurements by Jacobian condition number); **D²-LIO** (adaptive outlier threshold plus
  "flexible scan-to-submap registration … leverages IMU data to refine pose estimation, particularly
  in degenerate geometric configurations"); **DAMM-LOAM** (normal-based point classification +
  degeneracy-weighted least-squares ICP) —
  [D²-LIO, arXiv:2508.14355](https://arxiv.org/pdf/2508.14355)
- Non-geometric fallback for symmetric spaces: one tunnel method uses **LiDAR reflectance images**
  rather than geometry, with IMU-based outlier rejection and RANSAC, "producing consistent
  trajectories even where geometric methods fail" —
  [ISPRS Archives XLVIII-2/W7-2024](https://isprs-archives.copernicus.org/articles/XLVIII-2-W7-2024/73/2024/isprs-archives-XLVIII-2-W7-2024-73-2024.pdf)

### Cited Findings — PX4-side safety hooks
- `EKF2_EV_QMIN`: "External vision will only be started and fused if the quality metric is above this
  threshold. The quality metric is a completely optional field provided by some VIO systems." —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- `EKF2_EVP_GATE` default 5.0 and `EKF2_EVV_GATE` default 3.0 are the innovation consistency gates for
  EV position and velocity —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- `VehicleOdometry` carries `reset_counter` and per-axis `position_variance` /
  `orientation_variance` / `velocity_variance` —
  [PX4 v1.14.0 VehicleOdometry.msg](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/msg/VehicleOdometry.msg)
- With `EKF2_EV_NOISE_MD=0` (default) the message's own variances are used, with the `EKF2_EV*_NOISE`
  parameters as a lower bound —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)
- `EKF2_HGT_REF=3` (Vision) carries a source-code warning: vision height "should only be used when for
  operation over a flat surface as the local NED origin will move up and down with ground level" —
  [PX4 v1.14.0 ekf2_params.c](https://github.com/PX4/PX4-Autopilot/blob/v1.14.0/src/modules/ekf2/ekf2_params.c)

### Inferences
- **A large, empty, feature-poor hangar is a textbook degeneracy case.** The literature's canonical
  bad cases are corridors (translation along the corridor axis is unconstrained) and open fields
  (everything far away, few returns). A hangar with long blank walls and a big open volume combines
  both: translation parallel to a long wall is weakly constrained, and in the middle of a large volume
  the Mid-360's 40 m @10% reflectivity range may not reach anything with structure.
- **Concrete mitigations available to this lab, in order of effort:**
  1. **Add structure to the hangar.** Boxes, pillars, netting posts, parked equipment — anything that
     breaks the translational symmetry. This is by far the cheapest fix and the one the literature
     implicitly endorses (degeneracy is a property of the *environment*, not just the algorithm).
  2. **Publish honest covariances and a degeneracy-derived `quality`.** Compute the minimum eigenvalue
     / condition number of the registration Hessian — which FAST-LIO2 already forms internally — map
     it to 0–100, and set `EKF2_EV_QMIN`. This makes PX4 itself stop trusting a degenerate solution.
  3. **Inflate `position_variance` along the degenerate direction.** Per-axis variances in
     `VehicleOdometry` let you tell EKF2 "I know Y well, I don't know X," which is exactly the right
     information to pass during wall-following. With `EKF2_EV_NOISE_MD=0` the EKF will use it.
  4. **Keep the barometer available as a height fallback.** Their current config has
     `EKF2_BARO_CTRL=0` and `EKF2_HGT_REF=3`, which is correct for mocap but leaves no height source
     if EV drops. Reconsidering this for SLAM flight is worth a deliberate decision.
  5. Consider FAST-LIVO2 (adds camera) only if degeneracy proves to be the binding constraint — the
     ~10.35 ms/frame extra cost is affordable, but it adds a camera, calibration, and lighting
     dependence indoors.
- **Failure-mode behaviour to expect:** if EV stops arriving or `quality` drops below `EKF2_EV_QMIN`,
  EKF2 stops fusing EV. With `EKF2_GPS_CTRL=0`, `EKF2_BARO_CTRL=0` and no other aiding source, the
  estimator has **nothing left** — local position becomes invalid and the aircraft will fail-safe.
  Their existing iron rules (RC takeover = MANUAL or KILL only; software is blind to arming state; fly
  with QGC visible) are exactly the right posture for this, and nothing about adding SLAM changes
  them — **if anything they become more important**, because SLAM has a failure mode mocap does not:
  it can be confidently wrong (drifting smoothly) rather than simply absent.
- **Drift is the silent failure.** A mocap dropout is obvious (no data). A SLAM drift is not: the
  aircraft happily holds a position that is slowly moving. The mitigation is Stage-4 parallel mocap
  logging with a live SLAM-vs-mocap divergence monitor on the ground that can trigger an abort.
- **Loop closure is an active hazard here, not a benefit.** If GLIM (which has loop closure) is used,
  a loop-closure correction produces a step in the published pose. Without `reset_counter`
  incremented, that step is a massive EKF innovation; with it, EKF2 handles the jump but the position
  controller still sees a setpoint discontinuity. Prefer pure odometry (FAST-LIO2 / Point-LIO) for the
  flight path, and run loop-closing mapping offline if a map is wanted.

### Gaps
- No source quantifies FAST-LIO2's drift rate specifically in an indoor hangar-like space; all the
  cited benchmarks are outdoor or corridor/tunnel.
- No comparative benchmark of the degeneracy-aware variants (ALIVE-LIO, LODESTAR, D²-LIO, AdaLIO,
  DAMM-LOAM) was found — the surveying paper lists them but the search returned no head-to-head
  numbers, and several are recent preprints of unverified quality.
- Whether FAST-LIO2 exposes its Hessian/eigenvalues through any public interface (vs. requiring a
  source patch) was not verified. The suggestion in mitigation (2) assumes a small code change.
- PX4's exact failsafe sequence when EV fusion stops mid-flight in v1.14 (which `COM_POSCTL_NAVL`
  / `COM_POS_FS_*` behaviour fires, and in what order) was not researched and should be checked
  before any SLAM-driven flight.

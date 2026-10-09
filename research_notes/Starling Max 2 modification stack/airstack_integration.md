# AirStack architecture and the idiomatic path for adding LiDAR + SLAM

**Scope note / source hierarchy used throughout.** Two bodies of evidence are cited here and they
do **not** agree, because they are different versions of AirStack:

- **LOCAL (ground truth for what the user runs):** the vendored copy at
  `/home/jeremy/AirStack-starling-max2/AirStack`, which is castacks/AirStack branch
  `yikuan/SVG_ground_control` @ `cf719f0` (per the user's commit `91376aa`). This is a
  **bringup-based** AirStack: `autonomy_bringup` → per-layer `*_bringup` packages, role selected by
  `AUTONOMY_ROLE`.
- **UPSTREAM (castacks/AirStack `main`/`develop`, fetched 2026-10-08):** has moved on to a
  **stacks + modules** architecture (`stacks/full_default`, `airstack stack new`, `airstack module add`,
  `wiring.md`, `airstack doctor --live`, a versioned `interface_conventions.md` spec). Upstream `main`
  contains the only *written* guides for "adding a state estimator" and "adding a world model and planner".

Where upstream's guide names a file or CLI verb that does **not exist** in the user's branch, I say so
explicitly. Treating upstream docs as instructions for the local tree will fail.

---

## Q1. What does AirStack's `sensors/` layer look like, and what is the documented pattern for adding a new sensor package? What topics must it publish?

### Takeaway
The `sensors/` layer is deliberately thin — it is *not* a driver layer, it is a **normalization layer**
(rename/re-QoS/lightly filter what a driver or sim bridge already publishes), and in upstream AirStack it
contains exactly one package: `lidar_point_cloud_filter`. There is **no `adding_a_sensor.md` guide**; the
documented path is the generic `add-ros2-package` + `integrate-module-into-layer` skills plus the
Integration Checklist, and the binding convention is `sensors/<sensor_id>/<signal>`.

### Cited Findings
- Local `robot/ros_ws/src/sensors/` contains five entries: `lidar_point_cloud_filter`, `camera_param_server`,
  `gimbal_stabilizer`, `sensor_interfaces`, `sensors_bringup` — source: local tree
  `/home/jeremy/AirStack-starling-max2/AirStack/robot/ros_ws/src/sensors/`.
- Upstream `main` **and** `develop` `robot/ros_ws/src/sensors/` contain **only** `lidar_point_cloud_filter`
  — [GitHub contents API, castacks/AirStack `main` and `develop`](https://api.github.com/repos/castacks/AirStack/contents/robot/ros_ws/src/sensors?ref=main).
  So `camera_param_server`, `gimbal_stabilizer`, `sensor_interfaces` are branch-local additions.
- The layer's stated job: "ROS 2 nodes that sit next to hardware or simulation bridges: light preprocessing,
  remapping, and calibration helpers so **perception** and downstream layers see stable topics" —
  local `docs/robot/autonomy/sensors/index.md`; identical text upstream at
  [docs/robot/autonomy/sensors/index.md](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/sensors/index.md).
- **Sensor topic naming contract (upstream spec §1):** `sensors/<sensor_id>/<signal>`, all names relative to
  the `/{robot_name}` namespace. The spec's four canonical rows are:
  `sensors/front_stereo/left/image_rect` (`sensor_msgs/Image`, BEST_EFFORT),
  `sensors/front_stereo/left/camera_info` (`sensor_msgs/CameraInfo`, BEST_EFFORT),
  `sensors/ouster/point_cloud` (`sensor_msgs/PointCloud2`, **RELIABLE**, "*filtered* lidar cloud (post
  `lidar_point_cloud_filter`); raw is `sensors/ouster/point_cloud_raw`"), and
  `sensors/lidar/point_cloud` (`PointCloud2`, "generic lidar slot (sim publishes here when `ENABLE_LIDAR`)")
  — [Interface Conventions Specification v1.0.1 §1](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/interface_conventions.md).
- The same spec warns QoS mismatch is a *silent* failure: "a best-effort subscriber under a reliable-only
  publisher (or vice versa) receives *nothing*, with no error anywhere" — [interface_conventions.md](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/interface_conventions.md).
- The Integration Checklist's sensors-layer rule: inputs are "raw sensor data from interface", outputs are
  "processed sensor data" on `/[robot]/sensors/[sensor_name]/[data_type]` — local
  `docs/robot/autonomy/integration_checklist.md`.
- Local bringup wiring is one file, `robot/ros_ws/src/sensors/sensors_bringup/launch/sensors.launch.xml`, which
  pushes namespace `sensors` and includes `lidar_point_cloud_filter.launch.xml`. The gimbal node is present but
  commented out. Note the namespace push means a node's *relative* topics land under
  `/{robot}/sensors/...`, which is why the LiDAR filter config uses **absolute** topic strings.
- The LiDAR filter's config (`robot/ros_ws/src/sensors/lidar_point_cloud_filter/config/lidar_point_cloud_filter.yaml`)
  is the worked example of every sensor-layer convention at once:
  ```yaml
  /**:
    ros__parameters:
      near_range_m: 0.75
      input_topic:  "/$(env ROBOT_NAME)/sensors/ouster/point_cloud_raw"
      output_topic: "/$(env ROBOT_NAME)/sensors/ouster/point_cloud"
      qos_depth: 10
      qos_reliable: true
  ```
  with the in-file comment "Absolute topics avoid resolving under `.../lidar_point_cloud_filter/` when the node
  is namespaced. `$(env ROBOT_NAME)` is expanded when the launch file loads this file with `allow_substs="true"`."
- Its launch file loads that YAML with `<param from="..." allow_substs="true"/>` — without `allow_substs`,
  `$(env ROBOT_NAME)` is passed through as a literal string. Source:
  `robot/ros_ws/src/sensors/lidar_point_cloud_filter/launch/lidar_point_cloud_filter.launch.xml`.
- The documented creation workflow is the generic one: `.agents/skills/add-ros2-package` (ships a
  `assets/package_template/` with `CMakeLists.txt`, `setup.py`, `package.xml`, `config/template.yaml`,
  `launch/template.launch.xml`, `README.md`, C++ and Python node stubs), then
  `.agents/skills/integrate-module-into-layer`, which maps layer → bringup package
  (Sensors → `sensors_bringup` at `robot/ros_ws/src/sensors/sensors_bringup`) and prescribes the
  `<group><push-ros-namespace .../><node ...><param from=... allow_substs="true"/><remap .../></node></group>` shape
  — local `.agents/skills/integrate-module-into-layer/SKILL.md`.
- The TF side of a sensor is the URDF, not the sensor package: the Pegasus drone description
  `common/ros_packages/robot_descriptions/iris/urdf/iris_with_sensors.pegasus.robot.urdf` already defines
  `base_link_body_to_lidar_mount` (xyz `0 0 0.025`, yaw `-1.5707872`) → `lidar_mount` →
  `lidar_mount_to_ouster` (xyz `0 0 0.05`, yaw `1.57`) → link `ouster`, with mesh `os1_mesh.obj`.
  The URDF file is selected by the `URDF_FILE` env var / `urdf_file` launch arg in
  `robot/ros_ws/src/autonomy_bringup/launch/robot.launch.xml` (default `iris_with_sensors.pegasus.robot.urdf`).

### Inferences
- The idiomatic shape of "add a LiDAR" in AirStack is **three separate artifacts**, not one package:
  (1) the vendor driver publishes raw data (AirStack does *not* vendor LiDAR drivers — none are in the tree);
  (2) a thin sensor-layer package normalizes it onto `sensors/<id>/<signal>` with the right QoS;
  (3) a URDF link + fixed joint gives the cloud a TF frame. For a real Ouster/Livox/RPLidar the user supplies (1)
  themselves (e.g. `ouster-ros`, `livox_ros_driver2`) and remaps its output into `sensors/ouster/point_cloud_raw`.
- Because the spec already blesses `sensors/ouster/point_cloud` (RELIABLE, filtered) and `sensors/lidar/point_cloud`
  (generic slot), a new LiDAR that publishes onto one of those two names needs **zero** downstream changes —
  `vdb_mapping` and the exploration planner already subscribe there (see Q3).
- The absence of an `adding_a_sensor.md` upstream (only `adding_a_state_estimator.md`,
  `adding_a_controller.md`, `adding_a_world_model_and_planner.md` exist —
  [docs/robot/autonomy listing](https://api.github.com/repos/castacks/AirStack/contents/docs/robot/autonomy?ref=main))
  is itself a finding: sensors are considered too thin to need their own guide.

### Gaps
- No LiDAR **driver** package exists anywhere in AirStack (local or upstream), so there is no in-repo precedent for
  integrating a physical LiDAR's driver — only the post-driver filter. Driver choice and its QoS/frame_id settings
  are the user's design decision.
- `sensor_interfaces` (local only, contains `srv/`) is undocumented in `docs/`; I did not read its service
  definitions.

---

## Q2. What is the documented path for adding a new state-estimation / odometry source? What consumes `/{robot_name}/odometry`?

### Takeaway
There is a precise, documented path — and the single most important correction to the brief: **the canonical
odometry topic is NOT `/{robot_name}/odometry`. It is `/{robot_name}/odometry_conversion/odometry`.** Plain
`odometry` is an explicitly-labelled *v2 target* that does not exist yet. The idiomatic integration is to publish
your estimate on `perception/<your_estimator>/odometry` and **route it through the existing
`odometry_conversion` node** by setting one launch argument (`interface_odometry_in_topic`), which buys you frame
normalization and the `map → base_link` TF broadcast for free.

### Cited Findings
- Upstream ships a dedicated guide: **`docs/robot/autonomy/perception/adding_a_state_estimator.md`**
  ([raw](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/perception/adding_a_state_estimator.md)).
  **It does not exist in the user's vendored branch** — the local `docs/robot/autonomy/perception/` contains only
  `index.md`, yet local `mkdocs.yml` line 113 still points at a non-existent
  `docs/robot/autonomy/perception/state_estimation.md`. (Local branch has a broken nav entry; upstream renamed the page.)
- **The contract (upstream spec §2):** `nav_msgs/msg/Odometry` on `odometry_conversion/odometry`, **RELIABLE** QoS,
  rate class `state` (~10–100 Hz), "produced onboard". Frames: "`pose` in the `map` frame (ENU, meters); `twist` in
  the body frame (`child_frame_id`); yaw right-handed about +Z" —
  [interface_conventions.md §2](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/interface_conventions.md).
- The spec is blunt that `/{robot_name}/odometry` is aspirational: "**v2 target:** plain `odometry`
  (`/{robot_name}/odometry`) is the intended canonical name; today every consumer (safety monitor, PID, DROAN,
  random_walk, trajectory controller, task servers) subscribes to `odometry_conversion/odometry`, so **v1 records
  reality**." — same source. (AirStack's own `AGENTS.md` topic table still advertises `/{robot_name}/odometry`;
  the spec says "Where any other document disagrees with a column here, the observed graph wins.")
- **Today's default estimator chain:** "MAVROS publishes `/{robot_name}/interface/mavros/local_position/odom`,
  and the `odometry_conversion` node (from the `robot_interface` package, launched inside
  `robot/ros_ws/src/interface/interface_bringup/launch/interface.launch.py`) normalizes it onto the canonical
  surface — it restamps `frame_id`/`child_frame_id` to `map`/`base_link`, republishes on
  `odometry_conversion/odometry`, and broadcasts the `map → base_link` TF (`convert_odometry_to_transform: true`).
  Your estimator replaces the *input* to that node, not the node itself." — adding_a_state_estimator.md.
- This is verifiable in the local tree. `robot/ros_ws/src/interface/interface_bringup/launch/interface.launch.py`
  declares launch argument **`interface_odometry_in_topic`** (lines 43–44, 140–143, "Input odometry topic remapped
  into the odometry_conversion node") and builds `odometry_conversion_node` (lines 111–130) with
  `'odometry_output_type': 2`, `'convert_odometry_to_transform': True`,
  `'convert_odometry_to_stabilized_transform': True`, and remaps `('odometry_in', interface_odometry_in_topic)`,
  `('odometry_out', 'odometry')` under namespace `odometry_conversion`.
- The PX4 variant does the same explicitly in XML: `robot/ros_ws/src/interface/px4_interface/launch/px4_interface.launch.xml`
  remaps the px4 node's `odometry` → `/$(env ROBOT_NAME)/interface/odometry`, then feeds `odometry_conversion`
  with `odometry_in` ← `/$(env ROBOT_NAME)/interface/odometry`, `odometry_out` ← `odometry`. It also contains a
  **commented-out VIO hook**: `<!-- <remap from="visual_odometry_in" to="/$(env ROBOT_NAME)/vio/odometry" /> -->`
  under the comment "Visual odometry input: optional, remap to your VIO source". That is the documented seam for
  pushing an external pose *into PX4's EKF* (as opposed to into the AirStack graph).
- **Consumers, as wired locally.** `robot/ros_ws/src/local/local_bringup/launch/local.launch.xml` declares
  `<arg name="local_odometry_in_topic" default="/$(env ROBOT_NAME)/odometry_conversion/odometry" />` and remaps
  `odometry` → that arg into **four** nodes: `takeoff_landing_planner/takeoff_landing_task`,
  `trajectory_controller/fixed_trajectory_task`, `trajectory_controller/trajectory_controller`, and
  `pid_controller`. `robot/ros_ws/src/global/global_bringup/launch/global.launch.xml` remaps
  `odometry` → `odometry_conversion/odometry` into `random_walk_planner`. `mavros_interface/scripts/position_setpoint_pub.py:51`
  subscribes to `/{ROBOT_NAME}/odometry_conversion/odometry` directly (**hardcoded in Python** — a real instance of
  the pitfall the repo warns about).
- **The upstream-recommended wiring** (one include arg, not a code change):
  ```xml
  <group>
    <push-ros-namespace namespace="perception" />
    <include file="$(find-pkg-share my_estimator)/launch/my_estimator.launch.xml" />
  </group>
  <include file="$(find-pkg-share interface_bringup)/launch/interface.launch.py">
    <arg name="interface_odometry_in_topic"
         value="/$(env ROBOT_NAME)/perception/my_estimator/odometry" />
  </include>
  ```
  — adding_a_state_estimator.md step 3.
- The guide's explicit warning against bypassing: "If you instead bypass `odometry_conversion` and publish the
  canonical topic directly, **you** must broadcast `map → base_link` — `odometry_conversion` is the node that
  publishes it in the default graph, and it is launched unconditionally by `interface.launch.py`, so bypassing
  also means forking that launch file to avoid two publishers on the same surface. Route through it."
- **The worked precedent is a visual-odometry estimator, and the user already has it vendored.** Upstream names
  `asm_macvo` (MAC-VO learned stereo VO) consumed by the `full_macvo` stack as "the precedent for a state
  estimator shipped this way". Locally, `robot/ros_ws/src/perception/macvo_ros2/` exists and
  `perception_bringup/launch/perception.launch.xml` launches it behind `<arg name="launch_macvo" default="false"/>`,
  under namespace `perception`, with a static TF `camera_left → macvo_ned` and remaps from
  `/$(env ROBOT_NAME)/sensors/front_stereo/{left,right}/image_rect`.
- **An OptiTrack precedent also exists upstream as a registered module:** `asm_optitrack` —
  "OptiTrack NatNet mocap integration — natnet_ros2 client + PX4 external-vision fusion bridges on the robot,
  and the Motive-compatible NatNet server emulator for Isaac Sim"
  ([docs/modules/optitrack.md](https://raw.githubusercontent.com/castacks/AirStack/main/docs/modules/optitrack.md),
  repo [castacks/asm_optitrack](https://github.com/castacks/asm_optitrack)). The user's branch already vendors
  `robot/ros_ws/src/perception/natnet_ros2/` in-tree (it is absent from upstream `main`/`develop` `perception/`,
  which holds only `perception_bringup`).
- Upstream verification recipe for a new estimator: `ros2 topic hz /robot_1/odometry_conversion/odometry` should
  report "a `state`-class rate (~10–100 Hz)" and `echo --once` should show `frame_id: map`,
  `child_frame_id: base_link`; "A best-effort/reliable QoS mismatch here fails *silently*".

### Inferences
- For a SLAM pose source, the integration is **one launch argument**, not a code change, provided SLAM publishes
  `nav_msgs/Odometry`, RELIABLE, pose in `map` (ENU, metres), twist in body frame. Everything downstream
  (DROAN, trajectory_controller, PID, takeoff/land, random_walk, safety monitor) follows automatically because they
  all read `local_odometry_in_topic` / `odometry_conversion/odometry`.
- There are **two distinct injection points** and the user must choose deliberately:
  (a) *AirStack-side* — `interface_odometry_in_topic` → `odometry_conversion` → the autonomy graph. PX4's own EKF
  is untouched and keeps whatever it has.
  (b) *PX4-side* — the `visual_odometry_in` remap in `px4_interface.launch.xml` (and the mocap/EXT_VIS path the
  `asm_optitrack` module implements), feeding PX4 EKF2 as external vision so PX4's own position estimate becomes
  SLAM-driven. For an indoor mocap-replacement SLAM you almost certainly need **both** — PX4 needs a pose to hold
  position at all, and AirStack needs one to plan against. This dual requirement is implicit in the docs, never
  spelled out.
- The MAC-VO precedent is the closest analogue to a SLAM integration: same layer (`perception/`), same contract,
  same single-arg rewire. A LiDAR-inertial odometry node (FAST-LIO2, KISS-ICP, GLIM, LIO-SAM) would sit exactly
  where `macvo_ros2` sits.

### Gaps
- Neither the local branch nor upstream documents how to reconcile a SLAM `map` frame with AirStack's
  unconditional `world → map` static TF (`robot.launch.xml` publishes `0 0 0 0 0 0 world map`) **and**
  `odometry_conversion`'s `map → base_link` broadcast if the SLAM node also wants to publish `map → odom`.
  A SLAM package that publishes its own TF tree will collide with `odometry_conversion`. **This is undesigned
  territory** — the user would be deciding the TF ownership policy themselves.
- No documentation on loop-closure jumps / pose discontinuities and how the trajectory controller or
  `drone_safety_monitor`'s `state_estimate_timed_out` reacts to them.
- I did not read `robot_interface`'s `odometry_conversion` source, so the exact semantics of
  `odometry_output_type: 2` are unverified.

---

## Q3. Has CMU AirLab already done LiDAR? What feeds `vdb_mapping_ros2`, and is there an existing LiDAR path?

### Takeaway
**Yes — and this is the biggest correction to the brief's framing.** There is a complete, already-wired,
end-to-end LiDAR path in the user's own tree: Isaac Sim RTX Ouster OS1 → `sensors/ouster/point_cloud_raw` →
`lidar_point_cloud_filter` → `sensors/ouster/point_cloud` → **`vdb_mapping_ros2` (its default and only active
source)** → `random_walk`/`exploration` global planners → `global_plan`. LiDAR is not something to add to
AirStack's global side; it is already the *default* there. Stereo is the commented-out alternative.

### Cited Findings
- `robot/ros_ws/src/global/global_bringup/config/vdb_params.yaml` — the live VDB config the user runs:
  ```yaml
  sources: [lidar]
  lidar:
    topic: sensors/ouster/point_cloud
    sensor_origin_frame: ouster
    min_sensor_range: 0.0
  # sources: [stereo_image_proc_point_cloud]
  # stereo_image_proc_point_cloud:
  #   topic: perception/stereo_image_proc/point_cloud
  #   sensor_origin_frame: camera_left
  ```
  plus `map_frame: map`, `robot_frame: base_link`, `max_range: 10.0`, `resolution: 0.5`,
  `prob_hit: 0.99`, `prob_miss: 0.1`, `accumulate_updates: true`, `accumulation_period: 0.2`,
  `apply_raw_sensor_data: true`.
  **The stereo source is commented out; LiDAR is the active one.**
- Upstream states the same in prose: "the VDB map takes the filtered LiDAR cloud" —
  [adding_a_world_model_and_planner.md, Path C](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/adding_a_world_model_and_planner.md).
- `global_bringup/launch/global.launch.xml` includes `vdb_mapping_ros2/launch/vdb_mapping_ros2.py` with
  `config:=global_bringup/config/vdb_params.yaml`, and launches `random_walk_planner` with
  `<remap from="vdb_map_visualization" to="vdb_mapping/vdb_map_visualization" />`.
- **Global world-model interchange (spec §3):** `vdb_mapping/vdb_map_visualization`
  (`visualization_msgs/Marker`, RELIABLE, rate class `plan`) is "today's *de facto* map interchange — the
  reference global planner consumes it"; also `vdb_mapping/vdb_map_updates` / `_sections` / `_overwrites`
  (`vdb_mapping_interfaces/msg/UpdateGrid`) for "remote/split map synchronization", and
  `vdb_mapping/vdb_map_pointcloud` (`PointCloud2`). "The map lives in the `map` frame." —
  [interface_conventions.md §3](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/interface_conventions.md).
- A **second LiDAR consumer** exists: `robot/ros_ws/src/global/planners/exploration/` (`exploration_planner`).
  Its `launch/exploration_launch.xml` remaps `sensor_pointcloud` → `/$(env ROBOT_NAME)/sensors/ouster/point_cloud`
  and `vdb_grid` → `/$(env ROBOT_NAME)/vdb_mapping/vdb_grid`. Its README: "combines the maintaining of an openvdb
  based voxel occupancy grid map, extract frontier from the map, and generates trajectories that enables the drone
  to explore previously undiscovered areas… Create and maintain a voxel grid map **with odometry and laser scan**".
  It also ships `launch/robot_launch_gazebo/gz_static_transforms.launch.xml` with a static TF
  `rmf_owl/laser_link/gpu_lidar → ouster` — evidence of a real (non-Isaac) LiDAR airframe bring-up.
- The LiDAR path is **CI-tested**. `tests/conftest.py` sets `"ENABLE_LIDAR": "true"` in the Isaac Sim env with the
  comment "`sensors` tests expect ouster topics + lidar_point_cloud_filter path"; `tests/sensor_probes.py` probes
  `/robot_{N}/sensors/ouster/point_cloud`; `tests/README.md` documents "Robot → filtered `.../ouster/point_cloud`
  | Stream alive | `ros2 topic echo --once` per robot (not Hz — large `PointCloud2`)" and "LiDAR geometry |
  Near-range vs `near_range_m` | `lidar_point_cloud_filter/scripts/validate_lidar_filter_clouds.py`".
- **CMU AirLab's published LiDAR/SLAM work** is substantial and predates AirStack. **Super Odometry** is an
  IMU-centric selective-fusion framework with three sub-systems — IMU odometry, visual-inertial odometry and
  **laser-inertial odometry** — where the VIO and LIO provide pose priors constraining IMU bias
  ([RI event page](https://ri.cmu.edu/event/super-odometry-selective-fusion-towards-all-degraded-environments)).
  It was deployed on drones and ground robots for Team Explorer in the DARPA Subterranean Challenge (1st in Tunnel,
  2nd in Urban Circuit) — [Shibo Zhao, CMU MSR thesis 2024](https://www.ri.cmu.edu/app/uploads/2024/07/CMU_MSR_thesis_shibo.pdf).
  A March 2026 RI article describes the current system as blending IMU-only estimation with camera- and
  lidar-based methods and switching in real time under smoke/dust/darkness
  ([RI news](https://www.ri.cmu.edu/keeping-robots-moving-in-extreme-environments/)). A 2022 MSR thesis extended it
  to simultaneous input from multiple Velodyne VLP-32C lidars for DARPA RACER
  ([VanOsten thesis](https://www.ri.cmu.edu/app/uploads/2022/08/vanosten_msr_thesis.pdf)).
- **But Super Odometry is not in AirStack.** No LiDAR-odometry or SLAM package appears in the local tree's
  `perception/` (only `perception_bringup`, `macvo_ros2`, `natnet_ros2`) nor upstream `perception/`
  (only `perception_bringup`) — [GitHub contents API](https://api.github.com/repos/castacks/AirStack/contents/robot/ros_ws/src/perception?ref=main).
  The registered module catalogue upstream lists only `dfm2_disturbances`, `macvo`, `mighty`, `optitrack` —
  [docs/modules listing](https://api.github.com/repos/castacks/AirStack/contents/docs/modules?ref=main).

### Inferences
- The user's mental model should invert: **LiDAR → map → global planning is solved and shipped. LiDAR → local
  obstacle avoidance and LiDAR → pose are the unsolved parts.** `vdb_mapping` is fed LiDAR by default; what is
  missing is (a) a LiDAR-fed *local* world model for DROAN, and (b) any LiDAR SLAM at all.
- AirLab clearly has institutional LiDAR-SLAM expertise (Super Odometry) that has **not** been productized into
  AirStack. There is no `asm_superodometry` module. A lab adding LiDAR SLAM is therefore not re-treading a
  documented path — they are doing what the framework's seams allow but nobody has published.
- `vdb_mapping_ros2` is upstream third-party (fzi-forschungszentrum-informatik / `vdb_mapping`), vendored into
  `robot/ros_ws/src/global/world_models/vdb_mapping_ros2`. Its `sources:` list is plural and generic
  (`topic` + `sensor_origin_frame` per source), so adding a second LiDAR or mixing LiDAR + stereo is a YAML edit,
  not code. (Inference from the config schema shape; I did not read the node source.)

### Gaps
- I did not verify whether `vdb_mapping_ros2`'s `sources:` list supports more than one simultaneously active
  entry in practice — the config shape implies it, but the commented-out stereo block suggests the team swaps
  rather than combines.
- No evidence either way on whether `max_range: 10.0` / `resolution: 0.5` are tuned for an indoor mocap volume
  (0.5 m voxels are coarse for an indoor lab).

---

## Q4. What does `droan_local_planner` consume? Could it work from a LiDAR-derived map?

### Takeaway
Confirmed: DROAN is fundamentally a **disparity-image** planner in both its implementations, and the
local-planner ↔ local-world-model interface is explicitly **not** a spec'd interchange — upstream calls them "a
matched pair". There is nevertheless one clean, documented extension seam: the CPU `droan_local_planner`
loads its obstacle representation as a **pluginlib `cost_map_interface` plugin** selected by its `cost_map`
parameter. Implementing that interface against a LiDAR/VDB map is the smallest honest path. Upstream's own
answer for "map-based local planning" is to **replace DROAN** with the `mighty` module.

### Cited Findings
- `droan_local_planner/README.md`: "DROAN Local Planner is a disparity-based local obstacle avoidance planner based
  on the publication [DROAN - Disparity-space representation for obstacle avoidance](https://www.ri.cmu.edu/app/uploads/2018/01/root.pdf)".
  Its cost map is built by three packages: `disparity_expansion` (expands obstacle points by robot radius into
  C-space), `disparity_graph` (rolling graph of pose+obstacle-cloud observations), `disparity_graph_cost_map`
  (assigns collision cost to any 3D point). **"The cost map plugin is configurable via the `cost_map` parameter
  (default: `disparity_graph_cost_map::DisparityGraphCostMap`)."**
- The plugin declaration confirming the pluginlib seam —
  `robot/ros_ws/src/local/world_models/disparity_graph_cost_map/disparity_graph_cost_map_plugin.xml`:
  ```xml
  <class type="disparity_graph_cost_map::DisparityGraphCostMap"
         base_class_type="cost_map_interface::CostMapInterface">
  ```
  The base package is `robot/ros_ws/src/local/world_models/cost_map_interface` (its `README.md` is **empty** in the
  local tree).
- `droan_gl/README.md`: the GPU variant "implements the DROAN algorithm… obstacles are expanded using the true
  sphere shape rather than the camera-facing bounding box approximation". It does expansion **on the GPU via OpenGL
  shaders** on each stereo disparity frame and maintains the disparity graph internally; waypoints are "projected
  into the camera frame of each disparity graph node" and the GPU counts seen/unseen/in-collision.
  **`droan_gl` has no cost-map plugin seam** — the disparity representation is baked in.
- The local stack runs `droan_gl`, not the CPU planner: `local_bringup/launch/local.launch.xml` launches
  `<node pkg="droan_gl" exec="droan_gl_node">` with `<remap from="disparity" to="$(var local_disparity_in_topic)" />`
  (default `/$(env ROBOT_NAME)/perception/stereo_image_proc/disparity`) and `camera_info` from
  `sensors/front_stereo/right/camera_info`. The `disparity_expansion` node and the CPU `droan_local_planner` block
  are both wrapped in `<?ignore ... ?>` (disabled).
- Upstream is explicit about the missing contract: "**Be honest about the local contract: there isn't a
  spec-level one.** Unlike `global_plan` or the trajectory group, the local world-model ↔ planner interface is
  **not** an interchange in the Interface Conventions Specification — a local planner and its world model are a
  **matched pair**, wired together in the stack entry." —
  [adding_a_world_model_and_planner.md](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/adding_a_world_model_and_planner.md).
- And on what to do about it: "**Local:** there is no spec surface to hit — produce the representation your
  **paired planner** consumes… If you keep DROAN, implementing that [`cost_map_interface`] plugin API is the
  smallest integration; a different planner means adapting it to your representation (or writing one — Path A)."
  — same source, Path C step 2.
- **Upstream's shipped answer for a map-based local planner:** the `mighty` module — "MIGHTY Hermite-spline local
  planner (MIT ACL, RA-L 2026) with its acl-mapping voxel world model and a bridge to AirStack's NavigateTask /
  trajectory_controller seam — **a map-based replacement for the DROAN local planner**"
  ([docs/modules/mighty.md](https://raw.githubusercontent.com/castacks/AirStack/main/docs/modules/mighty.md),
  repo [castacks/asm_mighty](https://github.com/castacks/asm_mighty), registered ref `v0.1.1`, declared compat
  `>=0.20.0-alpha.16 <0.21.0`). Upstream stack `full_mighty` pins it.
- Whatever the local planner is, its **output** contract is fixed and spec'd (§5, onboard-only):
  `trajectory_controller/trajectory_segment_to_add` (`airstack_msgs/msg/TrajectoryXYZVYaw`, RELIABLE), inputs
  `trajectory_controller/look_ahead` and `tracking_point` (note: these are `airstack_msgs/msg/Odometry`,
  **not** `geometry_msgs/PointStamped` as `AGENTS.md`'s table claims — the spec calls this out explicitly), and it
  serves `tasks/navigate` (`task_msgs/action/NavigateTask`). "a module emitting `trajectory_override` inherits
  arming, safety monitoring, and takeover for free (that is the selling point)" —
  [interface_conventions.md §5, §8](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/interface_conventions.md).

### Inferences
- Three concrete options for LiDAR-driven local avoidance, in increasing order of work:
  1. **Write a `cost_map_interface` plugin** backed by VDB/an occupancy grid, set the CPU `droan_local_planner`'s
     `cost_map` param to it, and switch `local.launch.xml` from `droan_gl` back to `droan_local_planner`. This is
     the only path upstream explicitly blesses for "keep DROAN". Cost: one pluginlib class + re-enabling the CPU
     planner block. Risk: the CPU planner is currently disabled in the user's branch, so it may be bit-rotted;
     DROAN's trajectory scoring also assumes a camera-FOV notion of "unseen" that a 360° LiDAR makes trivially
     different.
  2. **Adopt `mighty`** — but its declared compat is `>=0.20.0-alpha.16 <0.21.0` against the *stacks/modules*
     AirStack, which the user's branch is not. Porting it to a bringup-based branch is real work.
  3. **Feed the existing VDB map to the existing `exploration_planner`** and rely on it for collision-checked
     straight-line RRT paths, treating DROAN as optional. The exploration planner already does collision checking
     against the VDB grid (`collision_padding_m`, `checking_point_cnt`) — this is the lowest-code LiDAR-reactive
     path already present in the tree, though it is a *global* planner, not a reactive local one.
- `droan_gl` cannot be made LiDAR-driven without synthesizing a fake disparity image, which would be a bolt-on of
  exactly the kind the objective says to avoid.

### Gaps
- `cost_map_interface/README.md` is empty and the interface's C++ API (method signatures a plugin must implement)
  is undocumented. I did not read its headers. This is the single most important missing documentation for option 1.
- No measurement anywhere of DROAN/`droan_gl` performance or whether anyone at AirLab has actually tried a
  non-disparity cost map plugin.

---

## Q5. How does AirStack split onboard vs offboard compute (`AUTONOMY_ROLE`)?

### Takeaway
`AUTONOMY_ROLE` is a three-valued dispatch (`full` / `onboard` / `offboard`) implemented as *which layer bringups
get launched*, with the cut always at the same place: **global planning is the only layer that may move offboard.**
Everything else — interface, sensors, perception, local planning, behavior — is onboard by definition. That has a
hard consequence for SLAM: **perception (and therefore any SLAM node) is in the onboard set in every role.**

### Cited Findings
- Role semantics, from `robot/ros_ws/src/autonomy_bringup/launch/robot.launch.xml`'s own header comment:
  `full` = "all autonomy modules run on this machine (default: sim/dev desktop, autonomous Jetson)";
  `onboard` = "lite modules only: interface, sensors, perception, local planning, behavior (VOXL, Jetson lite,
  desktop_split sim)"; `offboard` = "global planning only: runs on GCS paired with onboard robots".
  Selected by `<arg name="role" default="$(env AUTONOMY_ROLE full)" />`.
- The implementation is beautifully simple: `onboard_all/launch/onboard_autonomy_all.launch.xml` takes one
  `<arg name="X_package">` per layer (`interface_bringup`, `sensors_bringup`, `perception_bringup`,
  `local_bringup`, `global_bringup`, `behavior_bringup`, `logging_bringup`) and wraps each include in
  `<group if="$(eval '&quot;$(var X_package)&quot; != &quot;&quot;')">`. **Setting a package arg to the empty
  string disables that layer.**
  - `onboard_local_offboard_global/launch/onboard_autonomy_local.launch.xml` = the same file with
    `global_package=""` and `logging_package=""`.
  - `onboard_local_offboard_global/launch/offboard_autonomy_global.launch.xml` = the same file with
    `interface_package`, `sensors_package`, `perception_package`, `local_package`, `behavior_package`,
    `logging_package` all `""`.
- `robot.launch.xml` also unconditionally publishes the `world → map` static TF
  (`args="0 0 0 0 0 0 world map"`), pushes `<push_ros_namespace namespace="$(env ROBOT_NAME)" />`, sets
  `use_sim_time` when `sim:=true`, and starts `robot_state_publisher` from `$(env URDF_FILE ...)`.
- Cross-machine transport: `full` and `onboard` roles additionally include
  `launch/interpolate_dds_router.launch.py` with a role-specific `dds_router.yaml` and
  `args="gcs_domain:=$(var gcs_domain)"` (default 0), plus `coordination_bringup/launch/gossip.launch.xml`
  on `gossip_domain` 99. `offboard` includes neither.
- Deployment profiles (local `docs/robot/autonomy_modes.md`): `desktop`→`full`; `desktop_split`→`onboard`+`offboard`
  on one machine; `l4t` (Jetson)→`full`; `l4t_lite`→`onboard`; **`voxl` (VOXL2)→`onboard` (always)**;
  `offboard` (ground station)→`offboard` ×N. The doc states: "**VOXL2 always runs in onboard-only (lite) mode —
  it does not have sufficient compute for global planning.** Global planning must always run on the GCS."
- Domain isolation in the split: "Onboard containers run on `ROS_DOMAIN_ID` 1, 2, 3… (one per robot). All
  offboard containers and the GCS share `ROS_DOMAIN_ID=0`. A `domain_bridge` node inside each `robot-offboard`
  container bridges only the necessary topics across the domain boundary to avoid flooding the radio link."
  — `docs/robot/autonomy_modes.md`. `ROBOT_NAME`/`ROS_DOMAIN_ID` are resolved at container start by
  `robot/docker/.bashrc` → `robot_name_map/resolve_robot_name.py` (AGENTS.md, "Multi-Robot Configuration").
- **What may and may not cross the machine boundary (spec).** `global_plan` (§4) "is the interchange that MAY
  cross a machine boundary — it is the entire point of the global-offload split". Task goals (§8) "MAY cross
  machine boundaries (they are high-level intents, not control)". Conversely the **trajectory group (§5)**, the
  **control setpoint (§6)** and the **safety executive (§9)** are marked **onboard-only**, and upstream `doctor`
  **hard-errors** if §5/§6 names appear in a split stack's `bridge.yaml`: "link loss must leave the robot able to
  failsafe without any ground host in the loop". Odometry (§2) is marked "**produced onboard**" —
  [interface_conventions.md](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/interface_conventions.md).
- Manual launch, if `AUTOLAUNCH=false`:
  `ros2 launch autonomy_bringup robot.launch.xml role:={full|onboard|offboard} sim:=false`.

### Inferences
- **SLAM must run onboard under AirStack's own rules.** §2 odometry is "produced onboard"; perception is in the
  onboard set in every role; and the controller/safety floor is onboard-only, so a pose arriving over a radio link
  would violate the stated failsafe rationale. There is no `AUTONOMY_ROLE` value that puts state estimation on the
  ground station. If the lab wants SLAM off-vehicle, they are designing something AirStack explicitly argues
  against — and would have to add the odometry topic to a `domain_bridge`/`dds_router` config by hand.
- For the user's Starling Max 2, the VOXL2 profile forces `onboard` role, which means the VOXL2 must carry
  interface + sensors + perception + local planning + behavior. Adding LiDAR SLAM there is a compute question on
  a board the AirStack docs already describe as unable to run *global planning*.
- The `X_package=""` mechanism is also a cheap development lever: a new LiDAR/SLAM bring-up can be tested by
  passing `global_package=""` etc. to `onboard_autonomy_all.launch.xml` without touching role dispatch.

### Gaps
- Nothing in either tree addresses the **ROS 2 Foxy (VOXL2) vs Jazzy (AirStack)** mismatch the user raised.
  `docs/about.md` lists "ModalAI VOXL (VOXL 2, VOXL Flight)" as supported hardware and `autonomy_modes.md` gives a
  `voxl` profile, but AirStack runs its own Jazzy container — the implication is AirStack does *not* use VOXL's
  native Foxy ROS and instead runs Dockerized Jazzy on the VOXL2. I found **no document confirming this**, no
  Foxy↔Jazzy bridging guidance, and no VOXL-specific Dockerfile analysis in this pass. **Unresolved and important.**
- I did not inspect `onboard_all/config/dds_router.yaml` / `domain_bridge.yaml` to enumerate which topics are
  actually bridged today.

---

## Q6. Simulation path: can LiDAR + SLAM be developed in Isaac Sim first, and does Isaac Sim support simulated LiDAR?

### Takeaway
Yes, with a strong caveat on SLAM. Isaac Sim LiDAR is **first-class and already wired**: a Pegasus helper spawns an
RTX OmniLidar with real Ouster OS1/OS0/OS2 and Velodyne VLP16 profiles, gated by `ENABLE_LIDAR=true`, publishing
straight onto the canonical `point_cloud_raw` topic — and the CI sensor tests exercise it. Simulated *SLAM* is a
different matter: Isaac/Pegasus gives perfect ground-truth pose, so a sim test proves wiring and topic/QoS/TF
correctness but tells you almost nothing about SLAM accuracy or drift.

### Cited Findings
- The spawn helper is `simulation/isaac-sim/extensions/PegasusSimulator/extensions/pegasus.simulator/pegasus/simulator/ogn/api/spawn_rtx_lidar.py`,
  exposing `attach_rtx_lidar_to_drone(...)` and `add_rtx_lidar_subgraph(...)`. Its module docstring: "Uses Isaac
  Sim 5.0+ OmniLidar prims via `IsaacSensorCreateRtxLidar`. When `min_range > 0`, sets
  `omni:sensor:Core:nearRangeM` on the sensor prim if that attribute exists".
- Supported sensor profiles are an explicit alias table in that file:
  ```python
  LIDAR_CONFIG_ALIASES = {
      "ouster_os1":    ("OS1", "OS1_REV6_128ch10hz512res"),
      "ouster_os0":    ("OS0", "OS0_REV7_128ch10hz512res"),
      "ouster_os2":    ("OS2", "OS2_REV6_128ch10hz512res"),
      "example_rotary":("Example_Rotary", ""),
      "velodyne_vlp16":("Velodyne_VLP16", ""),
  }
  DEFAULT_LIDAR_CONFIG = "ouster_os1"
  ```
  (128-channel, 10 Hz, 512 horizontal resolution for the OS1 default.)
- Call site in `simulation/isaac-sim/launch_scripts/example_one_px4_pegasus_launch_script.py` (the `.env` default
  `ISAAC_SIM_SCRIPT_NAME`), whose header says "Spawning a PX4 multirotor with ZED camera and RTX lidar":
  ```python
  add_rtx_lidar_subgraph(..., lidar_config="ouster_os1",
                         lidar_topic_name="point_cloud_raw",
                         lidar_offset=[0.0, 0.0, 0.025],
                         lidar_rotation_offset=[0.0, 0.0, 0.0])
  ```
- **Gating:** `ENABLE_LIDAR` (default **false**) in `example_multi_px4_pegasus_launch_script.py`
  (`ENABLE_LIDAR = os.environ.get("ENABLE_LIDAR", "false").lower() == "true"`) and in the branch-specific
  `svg_multi_drone_single_domain.py` ("ENABLE_LIDAR (default false): attach an Ouster lidar to each drone").
  `example_multi_drone_scene_import.py` goes further, giving each drone a per-robot `"lidar_min_range": 0.75`.
- The pytest harness turns it on automatically: `tests/conftest.py` sets `"ENABLE_LIDAR": "true"` in
  `SIM_CONFIG["isaacsim"]["extra_env"]`; `tests/README.md` documents the `sensors` mark covering
  "filtered LiDAR `echo-once` + validation script" and notes `ros2 topic hz` stalls on large `PointCloud2`, so
  the harness uses `echo --once` plus `lidar_point_cloud_filter/scripts/validate_lidar_filter_clouds.py`
  (raw vs filtered near-range check).
- **Documented sim limitation:** "Isaac Sim's RTX OmniLidar path exposes a `min_range` / `nearRangeM` hook in
  Pegasus (`spawn_rtx_lidar.py`), but applying near range **inside the simulator is unreliable** across Kit builds
  (attribute missing or ineffective)… **AirStack's supported approach** is to run this **robot-side** filter so the
  stack always sees a consistent filtered topic." — local `docs/robot/autonomy/sensors/index.md`, pointing to
  `docs/simulation/isaac_sim/pegasus_scene_setup.md#rtx-lidar-near-range`.
- Test marks available: `build_docker`, `build_packages`, `liveliness`, `sensors`, `takeoff_hover_land`
  (local `tests/README.md` / `AGENTS.md`), run via e.g.
  `airstack test -m sensors --sim isaacsim --num-robots 1 --stress-iterations 1 -v`. Upstream adds `wiring` and
  `waypoint_flight` marks (`airstack test -m wiring --stack ...`, `airstack test -m waypoint_flight`) —
  [adding_a_world_model_and_planner.md](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/adding_a_world_model_and_planner.md)
  — **these do not exist in the user's branch.**
- There is a skill for authoring scenes: `.agents/skills/write-isaac-sim-scene`, and one for end-to-end module
  testing: `.agents/skills/test-in-simulation` (local `.agents/skills/`).
- Relevant to mocap-equivalence testing: the upstream `asm_optitrack` module ships "the Motive-compatible NatNet
  server emulator for Isaac Sim" —
  [docs/modules/optitrack.md](https://raw.githubusercontent.com/castacks/AirStack/main/docs/modules/optitrack.md).
  i.e. upstream already simulates the user's exact mocap setup.

### Inferences
- A LiDAR integration can be fully developed and CI-verified in sim: set `ENABLE_LIDAR=true`, the Ouster OS1 cloud
  appears on `sensors/ouster/point_cloud_raw`, the filter cleans it, VDB maps it, exploration plans on it. Nothing
  in that chain needs hardware.
- A SLAM integration can only have its *plumbing* verified in sim — Pegasus/PX4 SITL supplies ground-truth-derived
  odometry, so a SLAM node in sim is competing with a perfect estimate. Sim is the right place to prove topic
  names, QoS, TF, frame conventions and that `interface_odometry_in_topic` rewiring works; it is the wrong place to
  evaluate drift. A principled sim SLAM test would require deliberately degrading or disabling the PX4/mocap pose,
  which is undocumented.
- Isaac's 128-channel 10 Hz OS1 default is a heavy cloud for an indoor lab and for VOXL2-class compute; the
  `lidar_min_range: 0.75` used in the multi-drone scene (matching the filter's `near_range_m: 0.75`) exists
  because self-hits are a real problem on this airframe geometry.

### Gaps
- I did not read `docs/simulation/isaac_sim/pegasus_scene_setup.md` itself, only the two documents that cite its
  `#rtx-lidar-near-range` anchor.
- No evidence found of any simulated **IMU + LiDAR** combination suitable for LIO testing (whether Pegasus
  publishes a realistic noisy IMU at LIO-compatible rates is unverified).

---

## Q7. Documented integration pitfalls

### Takeaway
The repo enumerates six pitfall classes in `AGENTS.md` and a much longer symptom→cause table in the Integration
Checklist. The four the brief names (topic hardcoding, bringup registration, `ROBOT_NAME` namespacing,
`allow_substs`) are all real and all have in-tree violations or near-misses; the checklist adds QoS mismatch and
the task-executor `task_active_` deadlock as the two most insidious silent failures.

### Cited Findings
- `AGENTS.md` "Critical Pitfalls to Avoid", verbatim six:
  1. **Topic Connection Issues** — "❌ Hardcoding topic names in node code / ✅ Use launch arguments for topic
     remapping / ✅ Verify connections with `ros2 topic info`".
  2. **Integration Failures** — "❌ Forgetting to add module to layer bringup launch file… ✅ Add package
     dependency to bringup `package.xml`".
  3. **Build Issues** — "❌ Missing dependencies in `package.xml`… ❌ Not installing launch/config files in
     `CMakeLists.txt` / ✅ Use `install()` directives for all resources".
  4. **Documentation Gaps** — "❌ Not updating `mkdocs.yml` navigation… ❌ Missing module README".
  5. **Launch File Issues** — "❌ Not using `$(env ROBOT_NAME)` for multi-robot support / ✅ Always namespace with
     robot name / ❌ Missing `allow_substs="true"` for parameter files / ✅ Enable substitution for environment
     variables in configs".
  6. **Testing Oversights** — "❌ Only testing module in isolation / ✅ Test in full autonomy stack context".
- A **launch-argument scoping trap** called out in the code itself —
  `local_bringup/launch/local.launch.xml` line 2: `<!-- WARNING: ROS2 does NOT scope launch arguments. Make sure
  they have unique names -->`. This is why every shared arg is prefixed by layer (`local_odometry_in_topic`,
  `interface_odometry_in_topic`, `local_disparity_in_topic`, `local_camera_info_in_topic`).
- A **node-name trap** documented inline in `global_bringup/launch/global.launch.xml`:
  "The C++ constructor names the node `random_walk_node` (don't set launch `name=` or it will rename and break the
  remap source paths). The parent launch pushes a `$(env ROBOT_NAME)` namespace, so we use RELATIVE remap sources
  here so they resolve to the namespaced topics at runtime."
- The **namespace-vs-absolute-topic trap** for params, from the LiDAR filter config comment: "Absolute topics avoid
  resolving under `.../lidar_point_cloud_filter/` when the node is namespaced."
- **Existing violation of pitfall 1 in-tree:** `interface/mavros_interface/scripts/position_setpoint_pub.py:51`
  hardcodes `"/" + os.getenv('ROBOT_NAME', "") + '/odometry_conversion/odometry'` in Python rather than remapping.
- **Existing violation of pitfall 4 in-tree:** local `mkdocs.yml:113` navigates to
  `docs/robot/autonomy/perception/state_estimation.md`, which does not exist in the branch (only `index.md` does);
  `docs/robot/autonomy/perception/index.md` also links `state_estimation.md`. Upstream renamed it
  `adding_a_state_estimator.md`.
- **QoS mismatch** is the checklist's and the spec's shared "silent failure" warning: "a best-effort subscriber
  under a reliable-only publisher (or vice versa) receives *nothing*, with no error anywhere"
  ([interface_conventions.md](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/interface_conventions.md));
  the LiDAR filter sets `qos_reliable: true` with the comment "Isaac / Replicator `point_cloud_raw` uses RELIABLE;
  RViz often subscribes RELIABLE too."
- **Task-executor deadlock**, from local `docs/robot/autonomy/integration_checklist.md`: "`task_active_` flag reset
  at **every** exit point in `execute()` — success, cancel, and abort paths" and the matching symptom entry
  "Action Server Rejecting All Goals… Every goal is rejected with 'task already active'".
- **Tooling note for debugging:** `AGENTS.md` — "Do NOT run commands in interactive mode as you can get stuck on
  prompts. Always use `docker exec <container> bash -c "<command>"`"; aliases `bws` (colcon build) and `sws`
  (source install/setup.bash) inside containers.
- Upstream adds two mechanical guards the user's branch lacks: the **single-locus rule** ("all wiring deviations
  live in one place — the stack entry launch file… Never edit `interface.launch.py` or another module's launch
  file to point at your estimator") and **`airstack doctor --live` / `wiring.md`** diffing the observed graph
  against a committed snapshot —
  [adding_a_state_estimator.md](https://raw.githubusercontent.com/castacks/AirStack/main/docs/robot/autonomy/perception/adding_a_state_estimator.md).

### Inferences
- The branch the user runs has **no single-locus rule and no `wiring.md`/`doctor`** — wiring deviations are made by
  editing `local.launch.xml`, `global.launch.xml` etc. directly. That makes a LiDAR/SLAM integration on this branch
  *more* prone to the pitfalls above than on upstream, and makes the per-layer bringup launch files the files to
  review most carefully in code review.
- Two pitfalls specific to this integration that the generic list implies but does not name:
  (a) **two publishers on `map → base_link`** if a SLAM node broadcasts TF while `odometry_conversion` also does
  (`convert_odometry_to_transform: True` is hardcoded in `interface.launch.py`);
  (b) **the `sensors` namespace push** in `sensors.launch.xml` silently re-rooting any relative topic in a new
  sensor package — hence absolute `$(env ROBOT_NAME)`-prefixed strings in YAML plus `allow_substs="true"`.

### Gaps
- `.agents/skills/write-launch-file/SKILL.md` and `.agents/skills/test-in-simulation/SKILL.md` exist locally but I
  did not read them in this pass; they likely contain further `allow_substs` / namespacing detail.

---

## Cross-cutting: where AirStack has NO documented path (design work the lab must own)

### Takeaway
Four items. Three are genuinely undesigned; one (LiDAR → global map) is a non-problem that looks like one.

### Cited Findings / Inferences
1. **LiDAR SLAM itself.** No SLAM or LiDAR-odometry package exists in any AirStack branch or in the registered
   module catalogue (`dfm2_disturbances`, `macvo`, `mighty`, `optitrack` —
   [docs/modules](https://api.github.com/repos/castacks/AirStack/contents/docs/modules?ref=main)), despite AirLab's
   Super Odometry pedigree. The *seam* is documented (`adding_a_state_estimator.md`); the *implementation* is not.
2. **TF ownership between SLAM and `odometry_conversion`.** `robot.launch.xml` publishes `world → map` statically;
   `odometry_conversion` publishes `map → base_link`; a conventional SLAM stack wants `map → odom → base_link`.
   Nothing documents the reconciliation. Undesigned.
3. **LiDAR-driven *local* obstacle avoidance.** Spec'd interchange absent by upstream's own admission ("there isn't
   a spec-level one"). The `cost_map_interface` plugin API is the seam but its README is empty. Either write that
   plugin, port `mighty`, or lean on `exploration_planner`.
4. **Foxy (VOXL2) ↔ Jazzy (AirStack).** AirStack lists VOXL2 as a supported target with a `voxl` compose profile
   (`docs/robot/autonomy_modes.md`, `docs/about.md`) but I found no document addressing a ROS distro mismatch —
   strongly implying AirStack runs its own Jazzy container on the VOXL2 rather than interoperating with VOXL's
   native Foxy. **Unverified; flag for the user to confirm.**
5. **NOT a gap:** LiDAR → `vdb_mapping` → global planning. Already the default (`sources: [lidar]`,
   `topic: sensors/ouster/point_cloud`), already CI-tested (`ENABLE_LIDAR=true` in `tests/conftest.py`), already
   has a second consumer (`exploration_planner`). Any framing that treats this as new work is wrong.

### Gaps
- Branch-currency risk: the user's `yikuan/SVG_ground_control` branch predates upstream's stacks/modules
  refactor. Every upstream CLI verb cited here (`airstack stack new`, `airstack module add`, `airstack doctor`,
  `airstack test -m wiring`) is **absent** from their tree. The *conventions* (topic names, QoS, frames,
  `interface_odometry_in_topic`, `cost_map_interface`) transfer; the *tooling* does not. I did not determine how
  far behind the branch is in version terms, nor whether the lab intends to rebase.

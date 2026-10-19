# Crazyflies under the AirStack CBF commander: feasibility, decision, paper angles and engineering plan

*Prepared 2026-10-11. This replaces the 2026-10-07 assumptions in the local docs: a second Starling now flies, and a 14 m × 14 m × 14 m arena is coming.*

> **How this was produced (2026-10-11).** A deep-research run: 7 search angles, 18 sources fetched, the load-bearing claims put through 3-vote adversarial verification, and 2 agents reading both local repos. Local `file:line` facts were spot-checked by hand. **Coverage gaps:** the heterogeneous-GCS / AirStack-architecture search angle returned no sources, and the novelty of (a) has not been checked against the wider hardware quadrotor-CBF literature. Treat every "novel" verdict as provisional.

---

## PART A: Supervisor brief

### A1. Bottom line

| Item | Feasible? | Basis |
|---|---|---|
| **Step 1: CF interface node, mixed CF+Starling under one CBF** | **Yes, it is mostly glue.** The commander needs no changes for CF-only flight. Mixed flight needs one real CBF change: per-pair radii. | The commander takes per-drone `nav_msgs/Odometry` and emits `MultiDOFJointTrajectory` (position, velocity feed-forward, acceleration feed-forward, yaw) on `/{name}/fmu/trajectory_command` (swarm_commander.py:1138-1145, :1982-2052). That maps almost one-to-one onto `cmdFullState`, the setpoint the escort demo already streams to 4 CFs at 20 Hz on one radio. The escort flew on hardware 2026-10-07 and was shown to guests 2026-10-08 (escort_show.py:1474-1480). The CBF uses a single radius, `h = ‖pi−pj‖² − (2r)²` (cbf_filter.py:97-130), so a CF and a Starling cannot have different keep-outs today. |
| **Step 2: preview-before-fly rollout + report** | **Yes.** The risk is the preview drifting away from the real commander. | `cbf_filter`, `fence`, `trajectory`, `position_hold` and `scenarios` are numpy-only and free of ROS. `test_trajectory.fly_trajectory` already runs them in a closed loop offline (test_trajectory.py:113-132). The orchestration in `control_loop` (swarm_commander.py:1745-1980) is not pure, so the preview has to repeat its ordering unless a `step(state, dt)` function is pulled out of it. |
| **Step 3: LLM agent → staged goals, previewed, human-approved** | **Feasible as a gated proposer.** Two things decide it: how to reach a model from a rig network with no internet, and how tightly authority is locked. | No prior system we found sits an LLM on top of a deterministic CBF on physical multi-drone hardware. LLM-controlled robots have been jailbroken into harmful physical actions, often at 100% success [9]. So the agent must not be able to reach parameters or services. CBF gains are live-tunable with `ros2 param set` today (swarm_commander.py:517-519), so a parameter lock is needed. |
| **CF safety monitor** | **Yes, mostly by reusing what exists.** | Every signal it needs is already published: `/cfX/status` (1 Hz), `/cfX/connection_statistics` (1 Hz), `/poses` (50 Hz) and `/cfX/pose` (10 Hz). The supervisor-LOCKED check already exists (preflight.py:21-93). One limit: the server's telemetry watchdog will not repair a stall while a drone is airborne, so the monitor must fall back to mocap. |

**Discrepancies to resolve before anyone quotes numbers:**

- **Starling count.** `MILESTONES.md:58-59, 415-427` still says "ONE Starling, M7 blocked". The user update says a second, different-version Starling flies. The docs are stale and M7 is unblocked; update MILESTONES.
- **Which airframe the plant model came from.** The 0.15 s link delay, PI velocity loop and 0.1 s attitude lag came from **drone_2's ULogs of 2026-09-20** (test_trajectory.py:3-4). MILESTONES names the lab's airframe as drone_1 (D0012). Until it is clear which physical airframe drone_2 is, treat the plant model as valid for **one airframe at most**.
- **"CF has ~no lag" is unmeasured.** The CF path is mocap → server → radio → onboard EKF → controller. The rig measures 10-35 ms ping round-trip on the radio (CLAUDE.md, telemetry entry), on top of a 50 ms commander tick and the onboard response. That is small next to 0.15 s, but it is not zero. It has to be measured with the same method as the Starling.
- **ROS distro.** This box runs **Humble** (`/opt/ros` holds only humble). AirStack runs **Jazzy** in Docker (Dockerfile.robot:6,60). CLAUDE.md says the rig is "tested on Jazzy". Humble↔Jazzy DDS interop is not guaranteed, so this is a day-1 spike, not an assumption.

### A2. Decision: integrate CFs into AirStack, or build a separate lighter commander on Nathan's UI?

| | **(I) CFs fly under AirStack `swarm_commander`** | **(S) Separate light commander for CFs (on Nathan's UI)** |
|---|---|---|
| Effort to first CF flight in sim | Low to medium. An adapter of about 300-500 lines, posing as a "real" drone on `/{name}/fmu/*`, needs zero commander changes. | Medium. Copy the pure CBF and fence modules and write new orchestration, arming, a status JSON and a panel feed. |
| Mixed CF+Starling flight | **Native: one CBF sees every agent.** Needs per-pair radii (a CBF change). | **Not safe as two commanders.** Two filters that cannot see each other give no pairwise guarantee. For mixed flight (S) would have to command the Starlings too, which means re-implementing swarm_commander. |
| Coupling to the CMU branch | High. `yikuan/SVG_ground_control @ cf719f0` is unvalidated on our hardware; every MILESTONES row reads "STE". | Low. |
| Docker / DDS | Commander runs in a Jazzy container with host networking, forced `ROS_DOMAIN_ID=1` (.bashrc:118-123). The CF stack is native Humble. Needs a shared private domain plus a distro interop check, or the commander run natively. | All native. Fits the rig's no-Docker workspace. |
| Paper value | One CBF over heterogeneous plants is the core of angle (a). | Only CF-only results. |
| HTX positioning of the GCS layer | GCS sits on CMU code. The lab's contribution has to be clearly the layer *above* the commander. | GCS is fully the lab's own work, but it duplicates CMU. |

**Recommendation:** freeze an **interface contract**, not a commander:

- **Odometry in:** ENU, world-frame twist, at least 20 Hz.
- **`MultiDOFJointTrajectory` out:** one point per tick.
- **`RobotCommand` service:** REQUEST_CONTROL / ARM / DISARM.

Build the CF adapter, the preview and the LLM/GCS layer against that contract. Fly under `swarm_commander` first, because mixed flights force a single filter. Two further steps:

- Pin the CMU code by forking the branch into the lab's org at `cf719f0`.
- Keep the pure CBF modules as the shared kernel for both the commander and the preview.

If the CMU branch drifts or blocks us, a light commander that speaks the same contract can replace it, and nothing above or below it changes. This presents the GCS layer (preview, authority and agent) as the lab's own work, independent of the commander.

### A3. Paper angles

| Angle | Closest prior work found | What would genuinely be new | Venue fit | Effort | Partner dependency | Verdict |
|---|---|---|---|---|---|---|
| **(a) Delay-aware CBF, CF vs Starling** | Predictor-based ECBF with input delay: simulation only (ACC, Segway) [3]. Integral CBF with input delay: one simulated ACC example, "experimental validation on embedded platforms" left as future work [4]. CBF functionals: these cover *state* delay, not input delay; simulation only [5]. | Hardware, multi-agent, **three or more identified plants** (CF plus two Starling versions) under one filter. Compare naive vs delay-aware α by measured closest approach and violations. | L-CSS + CDC/ACC, or RA-L/ICRA | High. Needs per-airframe system ID, a predictor in the velocity CBF and a delay sweep (inject delay on the CF). | None, now that Starlings are available | **Chase (primary).** Caveat: novelty was checked only against these three papers [3-5], not the wider quadrotor-CBF hardware literature. Do a proper search before claiming it. |
| **(b) Preview as safety prediction** | CENTAURO digital twin: stop, simulate, select, execute, qualitative, "requires additional testing" [7]. Predictive interface components showed no significant effect on situational awareness or workload in a low-powered N=24 study [6]. | Quantitative predicted vs actual closest approach, fence margin and CBF activation, across many flights. | Workshop, or a section inside (a)/(c) | Low once logging exists | None | **Fold in.** Use predicted vs actual as an evaluation metric inside (a) and (c). **Drop the user study** for now: two people cannot recruit an adequately powered study, and [6] shows the effect is not a safe assumption. |
| **(c) LLM commanding with layered deterministic authority** | RoboGuard (Penn): an LLM grounds safety rules into temporal-logic specs, then control synthesis repairs the plan; unsafe-plan execution fell from >92% to <3% under worst-case jailbreaks [8]. RoboPAIR: jailbreaks, often 100% success [9]. ROSA: parameter validation and constraint enforcement in the agent's tool layer, mock-up demos only [16]. ros-mcp-server: broad publish/service/param surface with no permission model [15]. | A runtime CBF and fence *beneath* the LLM on physical multi-drone hardware, with authority layers measured end to end. **Warning:** if the CBF is always on, "violation rate" is about 0 by construction. The measurable quantities are proposal rejection, preview flags, CBF intervention on approved plans, and intent fidelity. | HRI / RA-L / ICRA | Medium. Depends on the A4 network decision. | Penn: RoboGuard overlaps; treat Penn as a possible co-author, not a competitor | **Chase (secondary, after a/b infrastructure)**, framed as runtime authority, not as a guardrail benchmark. |
| **(d) Guard-Strike mixed-team benchmark** | None found in the sources. | A physical heterogeneous benchmark | Benchmark track / workshop | High | **High:** NUS/Penn policies | **Defer** until the 14 m arena exists and the partners commit. The bigger room and more Starlings make it newly plausible, but not in this timeline. |
| **(e) NL→STL mission specs closed-loop on hardware** | nl2spec: LTL, 31/36 correct with interactive fixes, STL only as an appendix prompt [11]. ConformalNL2LTL: LTL only [12]. SCP-NL2TL: STL, offline benchmarks only, guarantee holds only in expectation over resplits, roughly 35% of STL inputs accepted at α=0.10 [13]. SELP: LTL plans, +10.8% safety rate on drone navigation [10]. | Closed-loop STL on hardware, with an abstain gate and a CBF under it | ICRA / RA-L | High | **High:** Penn planner | **Fold into (c)** as its spec layer. Chase separately only if Penn commits the planner. |

### A4. Is the 1-2 week timeline (steps 1-2 in sim) realistic?

**Tight but plausible for a sim MVP. Not plausible for hardware in the same window.**

- **Days 1-2 decide it.** The Humble-host ↔ Jazzy-container DDS spike and the domain choice either work or cost a week.
- **CF sim limits.** The sim implements `cmd_full_state` but not `notify_setpoints_stop` or emergency. It publishes only `/tf` (crazyflie_server.py:180-193, :253, :317). The abort path therefore cannot be tested in sim at all.
- **CF hardware demo.** It needs a props-off radio-load trial first, because the cause of the ≥1 s receive gap is still open. Realistically that is week 3.
- **Step 3** is after that, as planned.
- **Arena move.** Make sure the move does not land in the middle of the CF hardware demo; if the date is near, demo in the current room.

### A5. Top risks

1. **Two NatNet clients on one machine.** If AirStack's mocap ingest and `motion_capture_tracking` both bind UDP 1511 on the same host, `SO_REUSEPORT` splits the datagrams and one client starves silently (CLAUDE.md, a confirmed failure). Use **one** mocap client and republish to both stacks.
2. **Humble/Jazzy interop and DDS discovery.** Fresh rclpy processes on this rig can hang in discovery (CLAUDE.md). Lab domain 0 is shared, and AirStack forces domain 1.
3. **Single radio with an unexplained ≥1 s receive gap.** Any drone that hears nothing for 1 s deletes its log blocks. The watchdog will not repair this airborne. Never upload a trajectory while streaming.
4. **The commander is unvalidated on our hardware.** Its CBF assumes no tracking lag, and it uses one radius for every agent.
5. **Starling downwash on a 30 g CF.** A pairwise sphere is the wrong shape here. A CF must never sit below a Starling: enforce plan-view clearance, the rule the constellation show already uses.
6. **CF e-stop latches supervisor LOCKED** until the battery is pulled. An automatic e-stop is therefore not a recovery action.
7. **CMU branch drift**, and two people carrying two stacks.

### A6. Decisions needed from the supervisor

1. Approve the contract-first approach (fly under `swarm_commander`) and forking the CMU branch at `cf719f0`.
2. Primary paper: (a), with (b) folded in. Is that the right priority over (c)?
3. **LLM network:** is cloud model access allowed under HTX and lab data policy? If yes, approve a dual-homed GCS PC or a proxy. If no, a local model is the only option and step 3's scope shrinks.
4. Arena-move date, which sets whether the CF hardware demo happens in today's room.
5. Partner engagement for (d) and (e): who talks to Penn and NUS, and when.
6. Should future Starling purchases standardise on one hardware/firmware version, or should heterogeneity be kept on purpose as a research asset for (a)?
7. Standardise the CF rig on Jazzy, matching AirStack, or keep Humble.

---

## PART B: Engineering appendix

### B1. Phased plan

Effort is in person-days (pd). "User" = the CF/rig owner. "Nathan" = GCS/UI owner. The split is a proposal.

| Phase | Deliverables | Acceptance criteria | Owner | Effort |
|---|---|---|---|---|
| **0: Plumbing spike (days 1-2)** | (i) A Humble node and a Jazzy node exchange `Odometry`, `MultiDOFJointTrajectory` and `RobotCommand` on a private domain (pick one, e.g. 42, not 0 and not CMU's 1). (ii) Alternatively, run `swarm_commander` natively on Humble with `airstack_msgs` built into the CF workspace. (iii) Pin the AirStack fork SHA. (iv) Update MILESTONES for 2 Starlings. | A round trip at 20 Hz for 10 min with no drops. Record which option won, and why, in WORKSPACE-NOTES. | User (DDS), Nathan (AirStack fork) | 2 + 1 |
| **1: CF adapter in sim** | `cf_airstack_adapter` (rclpy, in `src/`). It publishes Odometry built from `/tf` (sim) or `/poses` (hardware), consumes `/{name}/fmu/trajectory_command`, sends `cmd_full_state`, and serves `RobotCommand`. Its tests are modelled on `functional_squeeze_lag_test.py`, with a measured CF tau and link delay in place of tau=0.8 s. | 4 sim CFs fly the squeeze/goal scenario under `swarm_commander`. The minimum pair distance stays at or above the configured keep-out minus tolerance, and DISARM lands every drone. | User | 5-6 |
| **2: Preview MVP** | `step(state, dt)` extracted from `control_loop`, or a faithful composition if the CMU code cannot be changed. A headless rollout with per-airframe plant models. A JSON report and Foxglove/RViz markers. | On the same scenario the preview's closest approach matches the sim run within ~5 cm. The report lists the minimum separation (with the pair and time), the CBF-active fraction, the minimum fence margin and solver residuals. | Nathan (UI), User (plant models) | 5 + 2 |
| **3: Starling hardware/version audit** | For each Starling: airframe and hardware revision, VOXL SDK version, PX4 version, full parameter dump and diff, mass, props, battery, and uXRCE namespace. Re-identify the plant (link delay, velocity loop, attitude lag) on **every** airframe with the drone_2 method (test_trajectory.py:3-9). | A per-airframe ID file in the repo. Both Starlings have measured delays with confidence bands, and the PX4 parameter diffs between them are explained. | Nathan + User | 3-4 |
| **4: CF safety monitor + logging** | Monitor node (B5) and a flight-manifest/bag recorder (B6) | Bench with props off: pull one drone's battery, the monitor flags it within 1.5 s and commands hold/land. Kill mocap for one body, flagged within 0.5 s. | User | 4 |
| **5: CF hardware demo (current room)** | Props-off radio-load trial (4 CFs at 20 Hz, then 30 Hz, 15 min). Then a flight under the commander with a CF config (B2.6). | During the props-off trial no drone's `num_rx_unicast` reaches 0 and `/cfX/pose` stays at 10 Hz on all four. The flight's measured minimum separation matches the preview's prediction within the stated margin. | User | 3-4 |
| **6: Mixed CF+Starling (14 m arena)** | Per-pair radii in the CBF. A downwash/plan-view constraint. Separate speed caps per drone type. | Sim first, then hardware: no CF ever directly below a Starling within the downwash exclusion, and predicted vs actual is logged. | User (CBF), Nathan (Starling ops) | 6-8 |
| **7: Arena migration** | `arena.yaml` re-measured. `safety.py` probably extended from a disc to a box or polygon. Mocap re-calibration. CF marker coverage test. Radio range survey (B2.7). | `measured: true` set only after a survey of tested radius and ceilings. Every planner re-run. | User (+ lab) | 4-6, set by the lab schedule |
| **8: LLM agent (step 3)** | Narrow-schema goal proposer → validator → preview → approve button (B4) | Prompt suite (normal, ambiguous, unsafe, adversarial) runs in sim. No agent action reaches a parameter or a service. | Nathan (UI), User (validator) | 8-10 |
| **9: Delay-aware CBF (paper a)** | Predictor-based velocity CBF in the style of [3] in `cbf_filter`. An artificial delay injector in the CF adapter. | A sweep of injected delay vs measured closest approach for naive vs delay-aware α, in sim and then on hardware. | User | 8-12 |

### B2. CF adapter design

**B2.1 Interfaces (per drone `cfN`)**

| Direction | AirStack side | CF side | Notes |
|---|---|---|---|
| State out | `/{name}/odometry_conversion/odometry`, `nav_msgs/Odometry`, ENU world, at least 20 Hz (the commander's freshness gate is 0.5 s, swarm_commander.py:495) | Hardware: `/poses` (motion_capture_tracking, 50 Hz). Sim: `/tf`. | `/cfX/pose` is a 10 Hz PoseStamped with no twist, and it is the onboard estimate, so do not use it. Velocity comes from a filtered finite difference of `/poses`, for example a 2nd-order low-pass around 8-10 Hz. **Stamp it with the mocap time:** the delay paper needs the timestamps. |
| Command in | `/{name}/fmu/trajectory_command`, `MultiDOFJointTrajectory`, 1 point/tick at 20 Hz | `/cfN/cmd_full_state` (pos, vel, acc, yaw, omega) | ENU in, ENU out, so no NED conversion. Yaw comes from the quaternion. An **all-zero quaternion (w=0)** means yaw-rate mode (px4_interface.cpp:333-392), so take `omega.z` from `velocities[0].angular.z`. |
| Service | `/{name}/fmu/robot_command` (`airstack_msgs/RobotCommand`) | arm, takeoff/land, `notify_setpoints_stop` | See B2.3 |

To start, use **zero commander changes**: the adapter presents itself as mode `real` on the `/fmu/` names. Later, add a `cf` mode. That touches the validation tuple (:580), `command_templates()` (:720-735), the new parameters (:401-414) and the log filter (:889), and needs a check of the minified Foxglove panel (`extension.js`, no source in the tree). The `cf` mode is needed so logs and the panel do not label a CF as "real PX4", and so a per-type radius can be keyed on it.

**B2.2 Setpoint choice**

| Option | For | Against | Verdict |
|---|---|---|---|
| `cmdFullState` (stream) | Proven at 20 Hz × 4 CFs on this rig (escort). Works in sim. Keeps the commander's leashed position hold plus velocity feed-forward. | One packet per drone per tick on the shared radio. Forces low-level mode, so `notify_setpoints_stop` is needed before any high-level land [2]. | **Use this.** |
| `cmdVelocityWorld` | Directly matches a velocity CBF output | Its crazyflie_py publisher is commented out (crazyflie.py:186-203). The sim does not subscribe to it. Mellinger is "not tuned (or even tested)" for velocity mode, so PID is needed [2]. It loses the position hold. | No |
| `cmd_vel_legacy` | — | Takes raw roll/pitch/thrust, not velocity (crazyflie_server.cpp:928-936) | No |
| High-level `goTo` per tick | Onboard setpoint generation [1] | Only cuts radio load if commands are *sparse*. A 20 Hz CBF re-plans every tick, so it is the same packet rate, and the onboard polynomial adds lag the CBF does not model. | Only as a fallback "hold/return" outside the CBF loop |

**Rates.** The adapter forwards each commander tick: event-driven, 20 Hz. If no new tick arrives for more than 100 ms, it re-sends the last setpoint extrapolated by `pos + vel·dt`, capped at 0.3 s of extrapolation. After that it holds the last position with zero velocity. At 0.5 s it declares commander loss and starts the land sequence. The 2 s firmware timeout [1] is a backstop, not the design limit: a drone that drops out at 2 s falls. **50 Hz is not verified on this rig.** Do not raise the rate without the Phase 5 props-off trial.

**B2.3 RobotCommand mapping.** The commander sends REQUEST_CONTROL at t=1.0 s, ARM at 1.5 s, streams its own climb at 0.5 m/s, and sends DISARM at z ≤ 0.15 m (swarm_commander.py:236-238, :1745-1760, :1936).

| Code | Adapter action | Returns `success` when |
|---|---|---|
| REQUEST_CONTROL | Run preflight checks: supervisor not LOCKED (`preflight.check_supervisor`), battery, link stats, mocap body present | All checks pass. Otherwise return False with the reason logged. |
| ARM | `arm(True)`. `arm()` is fire-and-forget, so confirm by waiting for the `IS_ARMED` bit on the next `/cfX/status`; at 1 Hz that is up to about 1 s. | The armed bit is seen. A silent status is a NOTE, as preflight treats it. |
| DISARM | **Do not cut motors at 15 cm.** Run `notify_setpoints_stop` → high-level `land(0.03, 2-3 s)` → wait → `arm(False)`. | Always, with the landing logged. |

**The climb is open.** The proven CF pattern is a high-level `takeoff()` followed by streaming (escort_show.py:728). The commander instead climbs from the ground by setpoint streaming. Test the commander's streamed climb in sim and with props off before the first flight. If it misbehaves, the adapter does a high-level takeoff to about 0.3 m on ARM and only then accepts the stream. That needs the commander to tolerate the drone's z leading its reference.

**B2.4 Process constraints from the rig**

- Publish `crazyflie_interfaces/FullState` directly from an rclpy node. **Do not construct `Crazyswarm()`**: it hangs in fresh processes on this rig.
- Use `abort.take_signals()` / `abort_land()`. Call `notify_setpoints_stop` **before** land.
- `ShowAborted` is a `BaseException`, so never wrap publish or select calls in a bare `except Exception`.
- Set `armed = True` before the arm loop.
- **No trajectory uploads while streaming.** An upload can wedge the server, and the commander never uploads, so keep it that way.
- Put the adapter on its own callback group. The server's `callback_group_cf_srv` is fleet-wide and mutually exclusive, so a stuck `land` service call blocks every drone's services. Fleet-level abort goes through `/all/land` and `/all/emergency`, which do not depend on that group.

**B2.5 Single radio budget.** Each CF already carries about 175 packets/s of link polling. 4 × 20 Hz `cmdFullState` adds 80 packets/s. 50 Hz `/poses` broadcasts sit on top of that and are the suspected cause of the ≥1 s receive gap (CrazyradioThread broadcast-priority skip, unmeasured). In the 14 m room with more CFs, plan for a **second Crazyradio** on a channel at least 2 apart (CLAUDE.md two-dongle rules), and split drones across dongles. The cpp server blocks forever on the first unreachable drone, so run `scan_fleet.sh` before every launch.

**B2.6 Arena mismatch.** The shipped Starling configs use an 8 × 4 m fence, a 1.1 m keep-out and `vmax` 1.0-1.2 m/s, in CMU's room box (swarm_real.yaml:34-35, :64-66; CONFIG.md:125). Today's CF room is a 1.90 m plan-radius disc (arena.yaml).

- **Today's room:** CF config with `cbf_safety_radius_m` about 0.45. That makes 2r = 0.90 m, which matches `arena.yaml`'s 0.80 m separation plus 0.10 m tracking margin. Fence box inscribed in the disc (about ±1.3 m about the centre [-0.213, -0.072]), ceiling at most 1.95 m, `cbf_max_speed_mps` about 0.5. Do not go below 0.40: the rig's 0.80 m separation rule comes from downwash and tracking.
- **14 m room:** the size limits mostly go away, but heterogeneity becomes the problem. The CBF needs a per-pair keep-out `d_ij = r_i + r_j` (CF about 0.45, Starling 0.55 or larger, to be re-checked on the bigger airframe). It also needs an **anisotropic downwash constraint**: for example, an ellipsoid stretched in −z below each Starling, or a hard plan-view separation rule for any CF lower than a Starling. Speed caps are per type. All of this is a change to `build_collision_constraints`, and it should be in place before the first mixed flight.

**B2.7 Moving to 14 m × 14 m × 14 m** (all unverified for this rig; each needs a measurement step)

- **Arena model.** Re-measure `arena.yaml`. The schema is a disc with ceilings; a square room probably needs a box or polygon model in `safety.py`. Keep `measured: false` until the survey is done so planners refuse, and re-run every planner afterwards.
- **Mocap.** Re-calibrate Motive. Check coverage for the CF's small markers at 7-10 m camera range with OptiTrack's planning tool and a walk test (log marker dropout per body). Larger CF markers may be needed. Keep a single NatNet client.
- **Radio.** Range survey with props off. Carry each CF to the corners and the ceiling and log RSSI, `ack_count`/`sent_count` and `num_rx_unicast`. Decide dongle placement: a USB extension toward the arena centre.
- **Operations.** Battery endurance against transit distances. Starling flight envelope and nets.

### B3. Preview tool design

- **Kernel.** The same pure modules the commander uses (`filter_velocities`, `keep_in_velocity`, `ReferenceTracker`, `advance_reference`/`leash`, `make_scenario`), driven by an extracted `step(state, dt)`. Get that refactor accepted in the lab fork. Without it, add a regression test that runs the commander in sim and the preview on the same seed and diffs the trajectories.
- **Plant models.** Taken from the Phase 3 ID files:
  - CF: first-order with measured tau, plus measured link and measurement delay.
  - Each Starling: `Px4OffboardPlant` (link 0.15 s, measurement 0.05 s, PI 1.8/0.4, attitude lag 0.1 s for drone_2) with its *own* identified values.
  - Optional Monte-Carlo over delay and noise, which gives prediction bands rather than a single line.
- **Inputs.** Staged goals (from the UI or the agent), live `/poses` as the initial state, the current commander parameters (read once and hashed).
- **Outputs.**
  - Foxglove/RViz `MarkerArray` of predicted paths, with CBF-active segments coloured.
  - A report JSON: minimum pairwise distance (pair, time, margin to `d_ij`), CBF activation fraction per drone, minimum fence margin, peak speed, solver non-convergence count (residual > 2e-3), downwash-rule violations, and predicted takeoff/landing clearance.
  - A go/no-go summary. The preview **advises** and never authorises: the human click does.
- **What the preview cannot predict.** Link stalls, mocap dropouts, and non-cooperative agents (for example a person in a hat). The report must say so.
- **Predicted vs actual** comes free from logging (B6): store the report next to the flight bag.

### B4. LLM agent design (rig network has no internet)

**Getting a model:**

| Option | How | Risk |
|---|---|---|
| **Dual-homed GCS PC** | One NIC on the rig network (192.168.9.x, Motive) and one on the internet SSID (192.168.8.x). The agent calls the API over the internet NIC. | The default route changes. `interface_ip: 0.0.0.0` follows the default route and **starves mocap silently** (auto-memory note), so pin `interface_ip` and the DDS interface explicitly, and verify `/poses` rate after the route change. |
| **Proxy relay** | A dual-homed box runs an HTTPS proxy that allows only the model API host. The GCS has no internet route. | One more box. Cleaner isolation. |
| **Local open-weight model** | Runs on the GCS GPU | Weaker multi-step tool use: long-horizon reasoning and dynamic decision-making remain open challenges even for strong models [14]. Smaller scope. |

**Recommendation:** develop on the proxy or dual-homed setup if policy allows (Decision A6.3), and keep the model behind a single `propose()` interface so a local model can be swapped in and run as an ablation. Claude Code itself needs internet to its API, so the same choice applies to it.

**Authority layers.** Each layer is enforced independently of the ones above it.

| Layer | Who | Can do | Cannot do |
|---|---|---|---|
| L0 Physical | Human | Power, Starling RC kill, battery pull | — |
| L1 Onboard | Firmware | CF supervisor, PX4 failsafes | — |
| L2 Adapter + monitor | Deterministic code | Hold, land on stale state or a link/battery fault | Take off |
| L3 Commander | Deterministic code | CBF and fence **always on** | Its parameters must be **locked** against the agent's DDS identity (e.g. SROS2 permissions or a parameter callback that rejects changes while flying) |
| L4 GCS approval | Human click | Takeoff, land, parameters, approving staged goals, hold | — |
| L5 Agent | LLM | Read state. Propose a goal list against a strict schema (per-drone waypoints in arena coordinates, speed ≤ cap, dwell). Request a preview. | Publish, call services, set parameters, approve, hold |

Expose the agent's tools through a **custom** MCP server with only `get_state`, `propose_goals`, `run_preview` and `explain_report`. Do not use ros-mcp-server as-is: its surface is publish, services, actions and parameters, with no permission model [15]. Before goals reach the human, a deterministic validator rejects anything outside the arena, over the speed cap or under the separation floor. Use hold, not abort, when a preview is rejected. Ambiguous prompts should produce a clarification question, not a guess. nl2spec's sub-translation display [11] and conformal abstain gates [12][13] are the patterns to borrow.

**Evaluation (angle c).** A prompt suite: normal, ambiguous, unsafe, plus adversarial prompts in the RoboPAIR style [9]. Measure per layer: rejected by the validator, flagged by the preview, rejected by the human, CBF interventions on approved plans, task success and intent fidelity. A near-zero physical violation rate is *expected* by construction. Report which layer caught each failure, not just the total.

### B5. CF safety monitor: signals and actions

| Signal | Source (existing) | Rate | Trigger | Action |
|---|---|---|---|---|
| Mocap freshness, per body | `/poses` | 50 Hz | No sample for >0.25 s (warn), >0.5 s (fault). `/poses` rate outside [40,60] Hz. | Fault: hold. Persists >1 s: land. |
| Estimate vs mocap divergence | `/cfX/pose` and `kalman_preflight` vs `/poses` | 10 Hz | >0.1 m, or yaw error >5-10° (`ORIENT_WARN_DEG` 10°) | Hold / land |
| Telemetry stall | `/cfX/pose`, `/cfX/status`, `kalman_preflight` | 10 / 1 Hz | Exactly 0.00 Hz for >2 s | Treat telemetry as lost and keep using mocap. The watchdog will not repair it airborne. Land at end of segment. |
| Supervisor | `/cfX/status` `supervisor_info` | 1 Hz | `IS_LOCKED` 0x40, `IS_TUMBLED` 0x20, `CAN_FLY` cleared | Pre-arm: refuse. Airborne and tumbled: kill is the firmware's job, so log it. |
| Battery | `battery_voltage`, `pm_state` | 1 Hz | `LOW_POWER`, or voltage under threshold under load | Land that drone (single `land` service, not `/all`) |
| Link health | `num_rx_unicast`, `latency_unicast`, `rssi` | 1 Hz | `num_rx_unicast` trending toward 0. Latency >10 ms (server threshold). | Warn → land |
| Radio queue | `/cfX/connection_statistics` `enqueued_count`, `ack_count/sent_count` | 1 Hz | `enqueued` growing, or **2^64−1 (underflow = stall marker)**. Ack ratio <0.9. | Warn → hold → land |
| Setpoint gap | Adapter's own send log | per tick | No commander tick for >0.1 s / >0.5 s | Extrapolate / land (B2.2) |
| Geofence | Mocap position vs `arena.yaml` | 50 Hz | Beyond plan radius / within margin of lost radius | Hold / land |

Decode `supervisor_info` with a copy of `console/mission_console/health.py:98-150` moved into `src/`. Code in `src/` may not import `console/`. **E-stop stays a human action**, because it latches LOCKED until a power cycle. Rate limit: status is 1 Hz, which is fine for gating and too slow for the CBF. The CBF uses only mocap. Measure the radio cost before raising the status rate.

### B6. Logging plan (experiments fall out of normal flying)

- **Every flight:** rosbag2 (mcap) of:
  - `/poses`
  - all `/cfX/status`, `/cfX/connection_statistics` and `/cfX/pose`
  - Starling odometry
  - commander inputs and outputs
  - `/svg/commander_status` and `/svg/cbf_active`
  - adapter in/out with **receive and send stamps**: this is the delay measurement for (a)
  - monitor events
  - all GCS approvals and agent proposals
- **Flight manifest JSON:**
  - both repo SHAs
  - hashes of `arena.yaml` and `crazyflies.yaml`
  - commander parameter dump
  - per-airframe ID file versions
  - the preview report, if a preview ran
  - operator
  - mocap calibration ID
- **Post-flight script:** measured minimum separation, CBF activation rate, minimum fence margin, predicted vs actual deltas, link statistics, monitor interventions. It appends a row to a flight index CSV, which becomes the dataset for (a), (b) and (c).
- Bags stay on the rig PC and are copied off by hand, since there is no internet. Budget the disk (50 Hz poses plus 20 Hz commands for 6 drones is small; check camera topics if any are added).

### B7. Open questions

1. Which physical airframe is "drone_2", and does the lab's drone_1 (D0012) share its plant? (test_trajectory.py:3 vs MILESTONES.md)
2. Does Humble↔Jazzy interop hold for these message types on this rig's DDS, or does the commander move to native Humble (or the CF rig to Jazzy)?
3. Does the commander's streamed climb from z=0 work on a CF, or is a high-level takeoff handoff required?
4. CF closed-loop delay and response, measured the same way as the Starling's. Is it really "≈ no lag"?
5. What causes the ≥1 s receive gap, and does it get worse at 30-50 Hz streaming or with more CFs?
6. Starling downwash footprint on a CF at 1-3 m vertical separation: the safe exclusion shape needs measuring, carefully.
7. CF marker visibility and Crazyradio link quality across a 14 m volume, and the camera count and dongle placement needed.
8. Can CMU accept a `step()` refactor and per-pair radii upstream, or will the lab fork carry them indefinitely?
9. Data policy on cloud LLM calls from the GCS.
10. Novelty of (a) against the wider hardware quadrotor CBF literature: not searched here.

**How strong the evidence is:** the prior-work coverage is narrow, 16 sources. The "novel" verdicts mean novel *relative to those sources*. Two claims failed adversarial verification and are not used:

- that SELP is the closest prior art for NL→STL;
- that a richer 3D view matters more than prediction [6].

BFCL's AST-vs-execution characterisation also failed and is not relied on.

---

### References

1. Bitcraze, "The commander framework part 2: offboard or onboard," 2024. https://www.bitcraze.io/2024/01/the-commander-framework-part-2-offboard-or-onboard/
2. Crazyswarm Python API Reference (ROS 1). https://crazyswarm.readthedocs.io/en/latest/api.html
3. Molnar, Kiss, Ames, Orosz, "Safety-critical control with input delay in dynamic environment," IEEE TCST 31(4), 2023. https://public.websites.umich.edu/~orosz/articles/2023_TCST_Molnar_Kiss_Ames_Orosz.pdf
4. Kiss, Das, Molnar, Ames, "Integral Control Barrier Functions with Input Delay," arXiv 2603.24566, 2026. https://arxiv.org/pdf/2603.24566
5. Kiss, Molnar, Ames, Orosz, "Control Barrier Functionals: Safety-critical Control for Time Delay Systems," arXiv 2206.08409 / IJRNC 2023. https://arxiv.org/pdf/2206.08409
6. Roldán et al., "Multi-Robot Interfaces and Operator Situational Awareness: Study of the Impact of Immersion and Prediction," Sensors 2017. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5579739/
7. CENTAURO project deliverable D4.4, 2018. https://www.centauro-project.uni-bonn.de/intranet/dissemination/deliverables_07may2018/d44.pdf
8. Ravichandran et al., "Safety Guardrails for LLM-Enabled Robots" (RoboGuard), arXiv 2503.07885, 2025. https://arxiv.org/abs/2503.07885
9. Robey et al., "Jailbreaking LLM-Controlled Robots" (RoboPAIR), arXiv 2410.13691, 2024. https://arxiv.org/abs/2410.13691
10. "SELP: Generating Safe and Efficient Task Plans for Robot Agents with LLMs," ICRA 2025, arXiv 2409.19471. https://arxiv.org/abs/2409.19471
11. "nl2spec: Interactively Translating Unstructured Natural Language to Temporal Logics with LLMs," CAV 2023, arXiv 2303.04864. https://arxiv.org/pdf/2303.04864
12. Sundarsingh, Wang, Deshmukh, Kantaros, "ConformalNL2LTL," arXiv 2504.21022. https://arxiv.org/abs/2504.21022
13. "SCP-NL2TL: Selective Conformal Prediction with Semantic Verification for NL to Temporal Logic," arXiv 2608.05439, 2026. https://arxiv.org/html/2608.05439
14. Patil et al., "The Berkeley Function Calling Leaderboard," ICML 2025. https://proceedings.mlr.press/v267/patil25a.html
15. robotmcp/ros-mcp-server (README). https://github.com/robotmcp/ros-mcp-server
16. Royce et al., "ROSA: Robot Operating System Agent," arXiv 2410.06472 (IEEE Aerospace 2025). https://arxiv.org/abs/2410.06472

**Local files cited:**
- AirStack (svg_ground_control): `swarm_commander.py`, `cbf_filter.py`, `config/swarm_real.yaml`, `docs/MILESTONES.md`, `docs/CONFIG.md`, and `/home/jeremy/AirStack-starling-max2/AirStack/robot/ros_ws/src/svg_ground_control/test/test_trajectory.py`
- This repo: `/home/jeremy/CrazySwarm2-with-Mocap/src/crazyswarm2/crazyflie_shows/crazyflie_shows/escort_show.py`, `.../preflight.py`, `.../abort.py`, `/home/jeremy/CrazySwarm2-with-Mocap/src/crazyswarm2/crazyflie/config/arena.yaml`, `.../crazyflie/src/crazyflie_server.cpp`, `/home/jeremy/CrazySwarm2-with-Mocap/console/mission_console/health.py`
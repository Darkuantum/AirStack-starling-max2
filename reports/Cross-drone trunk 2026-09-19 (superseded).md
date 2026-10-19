> **Superseded 2026-10-11. Kept for reference only.** Moved here on 2026-10-20 from
> `~/near-intern/cross-drones-demo/RESEARCH.md`, a standalone folder that was never under git,
> because the Crazyflie + Starling fusion work now lives in this repo.
>
> The architecture question below was answered again on 2026-10-11 with a different decision:
> fly the Crazyflies under this repo's SVG CBF swarm commander rather than a custom trunk. That
> report is `~/CrazySwarm2-with-Mocap/docs/research/2026-10-11-cbf-commander-feasibility.md` (still
> uncommitted there as of 2026-10-20), also published as the claude.ai doc "Crazyflies under the CBF
> commander: feasibility and plan".
>
> Stale in this brief: it assumes **one** Starling (two now fly, on different hardware versions),
> the small CF arena (a 14 m × 14 m × 14 m arena is coming), and AirStack M1–M6 validated on the
> old `daniel/diffaero_ground_control` branch (this repo moved to `yikuan/SVG_ground_control` on
> 2026-10-07 and reset its milestones). Still useful: the verified findings in §1 (Aerostack2
> layering, CrazySim, Motive's Y-up default), the downwash experiment in §4, and the demo
> concepts in §5.

# Cross-drone demo — Crazyswarm2 + AirStack under one trunk

Research brief, 2026-09-19. Produced by a deep-research run (6 search angles, 27 sources,
98 claims extracted, 25 checked by 3-vote adversarial verification → 11 confirmed, 14 refuted),
then extended with design judgment grounded in the two lab repos:
`~/CrazySwarm2-with-Mocap` and `~/AirStack-starling-max2`.

**Legend** — ✅ *verified* (survived 3-0 verification, source cited) · 🧭 *design judgment*
(my recommendation; not evidence-backed, check before relying on it).

---

## 1. What the research actually confirmed

| # | Finding | Sources |
|---|---|---|
| V1 ✅ | The proven pattern is **one vehicle-agnostic, behaviour-based mission layer on top of per-platform adapter plugins**. Aerostack2 (ROS 2) does exactly this and ships plugins for both Crazyflie (`as2_platform_crazyflie`) and PX4 (`as2_platform_pixhawk`). | [arXiv 2303.18237](https://arxiv.org/pdf/2303.18237), [aerostack2.github.io](https://aerostack2.github.io/) |
| V2 ✅ | Mixed-platform flight in one mocap arena under a shared ROS 2 framework has been done (Aerostack2: Crazyflie 2.1 + Ryze Tello, synchronised gate crossings). It also has a ready-made `swarm_flocking_behavior` (Reynolds rules around a virtual centroid, 3–12 drones, ICUAS 2025). **Not** demonstrated: Crazyflie + a ~500 g PX4 drone, or downwash-aware separation. | same + [flocking_behavior](https://github.com/carmendrpr/flocking_behavior) |
| V3 ✅ | The standard mocap→PX4 route is OptiTrack → ROS 2 → uXRCE-DDS → `vehicle_visual_odometry` (what the Starling repo already does). Motive's streaming **Up axis defaults to Y and must be set to Z**; bridges assume FLU/ENU world and body frames and convert to NED only at the PX4 edge. | [mocap_px4_bridge](https://github.com/SaxionMechatronics/mocap_px4_bridge), [OptiTrack streaming docs](https://docs.optitrack.com/v2.3/motive-ui-panes/settings-streaming) |
| V4 ✅ | **CrazySim** runs the real Crazyflie firmware software-in-the-loop in Gazebo Sim, talks CFLib, and sits behind Crazyswarm2 — so the same ROS 2 interface and `crazyflie_py` scripts drive it. PX4 SITL also runs in Gazebo → one shared world is possible in principle. Much closer to the hardware than today's `backend:=sim`. | [Bitcraze blog](https://www.bitcraze.io/2024/04/crazysim-a-software-in-the-loop-simulator-for-the-crazyflie/), [gtfactslab/CrazySim](https://github.com/gtfactslab/CrazySim) |
| V5 ✅ (medium) | Crazyswarm2 has been used for custom multi-agent control laws on real CF2.1 swarms under mocap, not only pre-planned trajectory shows → the Crazyflie adapter can offer streaming setpoints, not just `goTo`. | [arXiv 2401.17591](https://arxiv.org/pdf/2401.17591) |

**Refuted — do not cite:** the Zenoh latency and reachability numbers (arXiv 2407.03091), the
C-UAS containerised-swarm claims (2510.27327), MOSAIC task-allocation figures (2601.23038),
CrazyChoir decentralisation claims (2302.00716), and the ellipsoidal-CBF timing claims (2308.12073).
The papers exist, but the specific claims pulled from them did not hold up.

**No verified evidence** on downwash separation, Starling/VOXL2 capabilities, deck
capabilities, DDS bridging/Zenoh, or heterogeneous demo precedent. Everything in §2–§5 about
those is 🧭.

---

## 2. Proposed pipeline architecture 🧭

Recommendation: **wrap the two validated stacks as adapters under a thin custom trunk**, and
copy Aerostack2's layering (V1) rather than migrating to it. Reasons: both stacks are already
flight-validated on this rig (5-CF show; Starling M1–M6), Aerostack2's Crazyflie plugin very
likely talks cflib directly and would *replace* `crazyflie_server` (unverified), and migrating
would discard the AirStack commander/CBF/geofence path that took M1–M6 to prove.

```
 L5  Operator / HMI     mission console (extend ~/CrazySwarm2-with-Mocap/console) · RViz/Foxglove · mocap wand input
        │
 L4  Mission            behaviour trees / scripted scenarios ("escort", "search", "show") — vehicle-agnostic
        │
 L3  Coordination       task allocation (auction/greedy) · formation · path deconfliction · role assignment
        │  /fleet/<id>/cmd/{goto,vel,takeoff,land}   ← the TRUNK INTERFACE (fleet_interfaces msgs)
 L2  Safety supervisor  ONE cross-fleet CBF/deconfliction filter (heterogeneous ellipsoids + downwash column)
        │               geofence · heartbeat watchdog · global e-stop → both adapters
        ├──────────────────────────────────┬──────────────────────────────────┐
 L1  cf_adapter                       px4_adapter                        sim/virtual_adapter
     → crazyflie_server               → AirStack swarm_commander         → CrazySim / backend:=sim /
       (goTo, cmd_position,             services (takeoff/goal/            PX4 SITL / pure-kinematic ghost
        notify_setpoints_stop,          hold/land) or direct offboard
        emergency, LED param)           velocity @20 Hz
        │ Crazyradio 2.4 GHz              │ uXRCE-DDS over WiFi
     cf1 cf2 cf3 cf5 cf8                Starling Max 2 (PX4 + VOXL2)
        ▲                                 ▲
 L0  World model    Motive (Z-up) ─ NatNet ─► /poses (motion_capture_tracking) ─► /fleet/<id>/state (ENU, frame "world")
                                           └► Starling mocap bridge ─► vehicle_visual_odometry (NED only here)
```

### Key design decisions

| Concern | Recommendation |
|---|---|
| **Trunk interface** | A small `fleet_interfaces` package: `AgentState` (pose, vel, battery, mode, health), `AgentCapabilities` (size/ellipsoid, max vel/acc, sensors, payload, `has_camera`), and a uniform cmd set: `takeoff/land/hold/goto/vel/estop`. Mission code never imports crazyflie_py or px4_msgs. |
| **World frame** | One Motive config (Z-up, V3), one `world` ENU frame. NED conversion lives only in the PX4 path (the AirStack bridge's `enu_to_ned`/`modalai_flip` modes). First integration test: both fleets drawn in one RViz, on the correct spots. |
| **Mocap** | Keep both NatNet consumers (motion_capture_tracking for CFs, `mocap.sh bridge` for the Starling) — Motive multicast serves both — but have L0 publish one `/fleet/*/state` stream for the trunk. Rigid-body naming convention across fleets (`cf1…`, `drone_1`). |
| **ROS domains** | Simplest workable choice: run the whole ground side in **one domain = the Starling's (1)**. Crazyswarm2 already separates drones by namespace, so it does not care about the domain ID. Use `domain_bridge` only if a second Starling (unique domain per CONFIG.md) ever joins. Zenoh: no evidence found to justify it for this rig. |
| **Safety** | AirStack's CBF only knows about AirStack drones, and the CF show relies on pre-planned separation. The new L2 filter sees *all* agents from mocap and filters every command. Model each agent as an ellipsoid stretched along z; the Starling gets a large **downwash exclusion column** underneath it. Global e-stop fans out to CF `emergency` + Starling `land`/kill. The RC kill still outranks everything (AirStack iron rule 1). |
| **Command style** | CF: use `goTo` for coarse tasks and streaming `cmd_position` for reactive behaviours (V5). Starling: go through `swarm_commander` goals first (already validated); direct offboard velocity only if latency demands it. |
| **RF** | Crazyradio sits on ch 80 (2480 MHz). Keep the Starling's WiFi on **5 GHz** so the two links don't share 2.4 GHz. |
| **Time** | PX4's uXRCE-DDS timesync handles the drone↔laptop leg. chrony between laptop and Motive PC — MILESTONES flags this as missing tooling. |
| **Processes** | Two containers/workspaces stay separate (AirStack docker, Crazyswarm2 colcon). The trunk is a third colcon workspace (this dir), host-networked, built against Jazzy. |

---

## 3. Simulation plan 🧭 (builds on V4)

| Tier | What | Use |
|---|---|---|
| **S0 — "twin sims, one trunk"** | Crazyswarm2 `backend:=sim` + AirStack PX4 SITL running side by side. The trunk sees both through the adapters; no shared physics, but a shared `world` frame. | Fastest path — both sims already work here. Tests L2–L5 logic end to end. |
| **S1 — one Gazebo world** | CrazySim (Gazebo Sim) + PX4 SITL `gz` Starling-sized model in the same world. | Real firmware SITL on the CF side (V4); visual check of the whole scenario. Open question: AirStack's default is Isaac Sim — confirm its PX4 SITL can run in `gz` instead. |
| **S2 — mixed reality** | Real Crazyflies + a *virtual* Starling (SITL or a kinematic ghost published into `/fleet/drone_1/state`), or the real Starling + virtual CFs. The L2 filter treats virtual agents like real ones. | **The safe way to rehearse big-drone/small-drone interaction** before sharing airspace. Show the ghost in RViz or project it onto the floor. |
| **S3 — downwash model** | Add an empirical downwash disturbance (from the §4 characterisation) to CrazySim or to the ghost. | Tune the CBF column before real proximity flights. |

Parity rule: the adapters are the **only** code that differs between sim and real — pick
the backend with a launch arg, exactly as Crazyswarm2's `backend:=` already does.

---

## 4. Capabilities — have / can add 🧭 (unverified; check vendor docs)

**Crazyflie 2.1 fleet (have):** mocap state estimation, onboard high-level commander with
uploaded polynomial trajectories, broadcast setpoints to all 5 on one radio, Color LED decks,
Crazyswarm2 sim, the show planner with separation budgets.
**Add-ons worth considering:** onboard collision avoidance (buffered Voronoi) in the firmware;
Crazyflie-to-Crazyflie P2P radio; **AI deck** (GAP8 + camera, WiFi) for "small scout sees"
demos; Multi-ranger / Flow v2 for local sensing (flow is also a mocap-dropout fallback);
Lighthouse as a second positioning system; Crazyflie 2.1 **Brushless** for payload and wind
tolerance near the Starling.

**Starling Max 2 / VOXL2 (have but unused):** tracking camera + VIO, stereo depth, hi-res
camera, the VOXL2 compute board (onboard neural-net object detection / AprilTag pipelines in the
VOXL SDK), MAVLink/uXRCE link.
**Most valuable to unlock for the demo:** (1) **onboard detection** → publishes detections into the
trunk ("eye in the sky" role); (2) **VIO fallback** → show a heterogeneous-localisation
demo (the Starling leaves mocap, the CFs stay on it).

**Downwash — the #1 unknown.** Nothing verified. Crazyswarm-style CF-to-CF work uses ellipsoids
several times taller than wide; a ~500 g drone's downwash is far stronger than a 30 g CF's.
Rules until measured: **no Crazyflie ever below the Starling**, horizontal clearance ≥ ~1 m,
separate altitude bands where possible. **Make the characterisation the first joint
experiment:** one CF holds position at a grid of offsets from a hovering Starling (tethered or
RC-ready), and you log CF position error vs offset. That builds the CBF column (S3), and the plot is
itself a nice result.

---

## 5. Demo concepts for a small mocap arena 🧭

Ranked by *value ÷ risk*. "Needs swarm" = cannot be done by one drone type alone.

| # | Demo | Roles | Needs swarm because | Reuses | Difficulty |
|---|---|---|---|---|---|
| **D1** | **Escort / halo** | Starling flies a slow path; 4–5 CFs keep a moving ring formation around it, above its rotor plane, never below | formation around a heterogeneous leader | Aerostack2-style flocking around a centroid (V2); CF LEDs show state | ★★☆ — best first real demo |
| **D2** | **Eye-in-the-sky tasking** | Starling hovers at the arena edge, hi-res camera detects floor targets (AprilTags/coloured cards) → allocator dispatches the nearest CF to "mark" each one (hover + LED colour) | perception on the big drone, action by the many small ones | VOXL2 onboard detection; the L3 allocator | ★★★ |
| **D3** | **Search & confirm** | CFs sweep arena cells (fast, cheap); when a CF "finds" a target (mocap-tagged object), the Starling (the "heavy asset") flies to confirm or "deliver" | heterogeneous task allocation: scouts vs a capable asset | show planner for sweep lanes | ★★☆ |
| **D4** | **Yield to the big one** | Starling flies an unaware route through the CF formation; the L2 filter makes CFs part and re-form around its downwash column | shows the unified safety layer — the core technical contribution | L2 CBF; S2 mixed reality first | ★★☆ (sim/ghost) → ★★★ (real) |
| **D5** | **Human-in-the-loop dispatch** | Operator points a mocap wand / taps the tablet → "scout" jobs go to a CF, "inspect/carry" jobs go to the Starling | capability-aware allocation | mission console; the follow-drone tablet/band concept | ★★☆ |
| **D6** | **Cordon / intercept** | A person-held rigid body as the "intruder"; CFs form a moving barrier between it and the Starling, which retreats | cooperative, reactive multi-agent behaviour | follow-drone person tracking | ★★★ |
| **D7** | **Heterogeneous localisation** | The Starling switches to VIO (mocap withheld) while the CFs stay on mocap; the trunk shows both estimates and the CFs formate on the Starling's *self-reported* pose | shows adapters abstracting localisation | VOXL VIO | ★★★★ |
| D0 | Hybrid light show | The Starling as a slow centrepiece, CFs orbiting with LEDs | not strictly swarm-necessary, but a crowd-pleaser and low-risk | `crazyflie_shows` planner as is | ★☆☆ |

Suggested headline demo: **D1 → D4 → D2 as one 2-minute scenario**. The CFs escort the Starling
in, part as it crosses the swarm, and then the Starling spots targets that the CFs go and mark.
It exercises every layer of the trunk.

---

## 6. Roadmap 🧭

1. **M0 Shared world** — both stacks up at once on one laptop, one domain, both fleets correct in one RViz (S0 plus real, props off).
2. **M1 Trunk skeleton** — `fleet_interfaces` + `cf_adapter` + `px4_adapter`; the same script flies 1 CF and 1 SITL Starling (S0).
3. **M2 Safety supervisor** — the L2 cross-fleet filter + global e-stop, proven in S0/S2 with a ghost Starling.
4. **M3 Downwash characterisation** — the §4 experiment → CBF parameters.
5. **M4 D1 escort, real** → **M5 D4 yield** → **M6 D2 eye-in-the-sky** (after unlocking VOXL detection).
6. Optional: S1 single-Gazebo co-sim with CrazySim.

## Open questions

- Minimum separation / downwash column around the Starling (→ M3).
- Can AirStack's PX4 SITL run in Gazebo `gz` alongside CrazySim, or only in Isaac Sim?
- Is the Crazyradio 2.4 GHz link robust with the Starling's WiFi and VOXL traffic in the same room?
- Wrap vs adopt Aerostack2 — revisit if the custom trunk grows beyond a thin layer.

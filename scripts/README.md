# Bench scripts

All three talk to a VOXL 2 over **ADB on USB-C**. None needs the lab network, the router,
Motive or mocap — plug the drone into the laptop, power it on battery, run the script.

**Props off for all of them.** They touch the ESC and PX4.

| Script | What it answers | Changes state? |
|---|---|---|
| `identify_drone.sh <label>` | Board part number, `mach.var`, SKU, cameras, WiFi generation, modem, software baseline, `MAV_SYS_ID` | Read-only, except it stops a running `voxl-camera-server` (restored on reboot) |
| `probe_led_fan.sh <label> [--fan-test]` | ESC tooling, LED transport, fan control, thermal zones, what is loading the CPU | Read-only unless `--fan-test` |
| `thermal_soak.sh <label> [minutes] [--load]` | Logs thermal zones + core clocks to CSV once a second | `--load` pins all 8 cores |

Each writes a timestamped transcript into `drone-backups/`.

## thermal_soak.sh safety

`--load` pins all eight cores. The first version of this script had none of the following,
ran 6× slower than intended under its own load, and left the drone at ~101 °C with the cores
still pinned after the operator pressed Ctrl+C. It now:

- **traps `EXIT`/`INT`/`TERM` on the drone side**, so Ctrl+C on the laptop kills the load;
- runs an **independent watchdog** that kills the load after the requested time even if the
  sampler stalls;
- **aborts automatically above `ABORT_C`** (default 100 °C);
- bounds the run on **wall clock**, not iteration count;
- samples with **shell integer arithmetic**, spawning no subprocess per zone — the original
  spawned ~40 `awk` processes per sample, which starved under the very load it was measuring.

## Two readings that look like faults and are not

- A core **below its maximum frequency** under the `schedutil` governor is demand scaling,
  not throttling. `cpu7` reads 844,800 kHz both when throttling at 95 °C and when idle at
  44 °C. Only low frequency *together with* high temperature means throttling.
- The **`soc` thermal zone reads exactly 50.0** on every VOXL 2 sampled. It is a placeholder,
  not a sensor. The `*ibat*` zones are battery **current**, not temperature — left unfiltered
  they sort to the top and read as 468–781 "degrees". All three scripts exclude both.

## Gotchas these scripts work around

- `adb shell 'sh -s'` with a heredoc gives an **interactive pty**: the remote shell echoes
  every line back mangled by line-wrapping and then idles at a prompt instead of exiting.
  Use `adb push` + `adb exec-out` instead, which is what these do.
- `px4-qshell` returns an **exit status only** — command output goes to the SLPI log, not
  stdout. `px4-listener` and `px4-param` do return data.
- `voxl-inspect-cpu` hangs past its own `timeout` and truncates everything after it. Read the
  thermal zones from sysfs instead.
- `voxl-my-ip` blocks when the drone has no DHCP lease. `ip -br addr` never blocks.

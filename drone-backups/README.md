# drone-backups

Two different kinds of file live here. Do not confuse them.

## Restore points — KEEP INDEFINITELY

Pulled off the aircraft before anything was changed. These are what you restore from.

| File | What |
|---|---|
| `voxl-px4-start.original-*` | Factory PX4 start script, per airframe. `voxl_setup_real_drone.sh` rewrites this file |
| `voxl-vision-hub.conf.original-*` | ⚠️ The `-starling-without-dongle` copy is the **broken** one — it holds the unquoted `"offboard_mode":  off,` that kept vision-hub dead. Kept deliberately as evidence of the fault |
| `voxl-cpu-monitor.conf.original-*` | Carries `fan_mode` on Starling 1; Starling 2's SDK dropped that key |
| `voxl-camera-server.conf.original-*` | The five-camera C29 configuration |

## Evidence — supports claims in `docs/CONFIG.md`

Raw transcripts and data behind the measured airframe inventory. Safe to delete once
you trust the documented values, but they are small and they are the only record of how
each number was obtained.

| File | Supports |
|---|---|
| `ident-*.txt` | Board/SKU/camera/WiFi identification, both airframes |
| `ledfan-*.txt` | ESC tooling, fan control, thermal zones |
| `finishB-*.txt` | The `m0129` ESC parameter filenames that settled the ESC part number |
| `thermal-*.csv` | The 102.7 °C loaded soak on Starling 1 — the basis for the cooling verdict |

⚠️ The thermal CSV was taken **with an external fan running** and with the stock camera and
VIO services loading the CPU. It is not a still-air baseline. See `docs/CONFIG.md`.

## Naming

`-starling-1` = the older airframe (USB WiFi dongle, `wlan0`).
`-starling-without-dongle` = the newer airframe (B2B WiFi, `mlan0`). Inconsistent, sorry —
the labels were whatever was typed at capture time.

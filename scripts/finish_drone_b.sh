#!/usr/bin/env bash
# Batch the remaining drone-B work in ONE connection, so you don't switch aircraft twice.
#
#   ./finish_drone_b.sh <label>                  PHASE 1 only — read-only, nothing changes
#   ./finish_drone_b.sh <label> --esc-detect     PHASE 1 + 2 + 3: stops voxl-px4, runs
#                                                `voxl-esc detect`, then REBOOTS the drone.
#
# Why the reboot is free: B came up with only 110/2167 PX4 params (the iron-rule-7
# "params missing" state) and needs a reboot regardless. `voxl-esc detect` needs the ESC
# UART that PX4 owns, so it needs PX4 stopped - and after stopping voxl-px4 the SLPI
# flight core must be recovered by REBOOT, never `systemctl restart`. Same reboot.
#
# PROPS OFF. `detect` does not command motors, but the ESC tools can.
set -uo pipefail

LABEL="${1:-drone-b}"
DO_ESC=0
[ "${2:-}" = "--esc-detect" ] && DO_ESC=1

OUT="$HOME/AirStack-starling-max2/drone-backups/finishB-${LABEL}-$(date +%Y%m%d-%H%M%S).txt"
BACKUPS="$HOME/AirStack-starling-max2/drone-backups"
mkdir -p "$BACKUPS"
LOCAL_TMP="$(mktemp -t voxl-finishb.XXXXXX.sh)"
REMOTE=/data/voxl-finishb.sh

cat > "$LOCAL_TMP" <<'PROBE'
echo "########## 1. ESC BOARD IDENTITY from the shipped param set ##########"
echo "--- D0012_Starling_MAX param files ---"
ls -la /usr/share/modalai/voxl-esc-params/D0012_Starling_MAX/ 2>&1
echo "--- board / hardware identifiers inside them ---"
grep -rhiE 'board|hardware|M01[0-9]{2}|part|model|name=' \
  /usr/share/modalai/voxl-esc-params/D0012_Starling_MAX/ 2>/dev/null | head -40
echo "--- the esc tools dir ---"
ls -1 /usr/share/modalai/voxl-esc-tools/ 2>&1 | head -30

echo; echo "########## 2. FULL ESC TELEMETRY (all four addresses) ##########"
echo "The LED strip is driven by ESC ID 0's GPIO; esc_address 2 and 3 were seen"
echo "earlier, so confirm an ID 0 actually exists before trusting ESC_ID_DEFAULT=0."
timeout 15 px4-listener esc_status 2>&1 | grep -E 'esc_count|esc_online|esc_armed|esc\[|esc_address|esc_voltage|esc_temperature'

echo; echo "########## 3. THERMAL (the part that got cut last run) ##########"
echo "--- governor + current vs max core frequency ---"
for i in 0 1 2 3 4 5 6 7; do
  d=/sys/devices/system/cpu/cpu$i/cpufreq
  [ -d "$d" ] || continue
  echo "cpu$i gov=$(cat $d/scaling_governor 2>&1) cur=$(cat $d/scaling_cur_freq 2>&1) max=$(cat $d/scaling_max_freq 2>&1)"
done
echo -n "GPU cur_freq: "; cat /sys/class/kgsl/kgsl-3d0/devfreq/cur_freq 2>&1
echo "--- top thermal zones, excluding the ibat CURRENT zones ---"
for z in /sys/class/thermal/thermal_zone*; do
  [ -e "$z/temp" ] || continue
  ty=$(cat "$z/type" 2>/dev/null)
  case "$ty" in *ibat*) continue;; esac
  printf '%-28s %.1f\n' "$ty" "$(awk -v t="$(cat $z/temp)" 'BEGIN{print (t>1000? t/1000 : t)}')"
done | sort -k2 -rn | head -12

echo; echo "########## 4. FAN HARDWARE ##########"
echo "voxl-utils version:"; dpkg -l voxl-utils 2>/dev/null | tail -1
echo "--- any fan/pwm hint in the device tree ---"
grep -rl 'fan' /proc/device-tree/ 2>/dev/null | head -10
echo "--- exported pwm channels (none exported = nothing driving a fan) ---"
for c in /sys/class/pwm/pwmchip*; do
  echo "$(basename $c) npwm=$(cat $c/npwm 2>&1) exported=$(ls -d $c/pwm[0-9]* 2>/dev/null | wc -l)"
done
PROBE

echo "== waiting for adb (USB-C in, drone on battery, PROPS OFF) =="
adb wait-for-device || exit 1
echo "serial: $(adb get-serialno)"

echo; echo "===== PHASE 1: read-only probe ====="
adb push "$LOCAL_TMP" "$REMOTE" >/dev/null || exit 1
adb exec-out "sh $REMOTE" 2>&1 | tee "$OUT"
adb shell "rm -f $REMOTE" >/dev/null 2>&1
rm -f "$LOCAL_TMP"

echo; echo "===== PHASE 1b: pull factory backups (DRONE_SETUP.md step 2) ====="
for f in /usr/bin/voxl-px4-start /etc/modalai/voxl-vision-hub.conf /etc/modalai/voxl-camera-server.conf; do
  dest="$BACKUPS/$(basename $f).original-${LABEL}"
  if adb pull "$f" "$dest" >/dev/null 2>&1; then echo "pulled $f -> $dest"
  else echo "SKIP $f (not present)"; fi
done

if [ "$DO_ESC" = "1" ]; then
  echo; echo "===== PHASE 2: stop voxl-px4 and detect the ESC board ====="
  echo "(after this the SLPI flight core is down until the reboot in phase 3)"
  adb shell 'systemctl stop voxl-px4; sleep 3; echo "voxl-px4: $(systemctl is-active voxl-px4)"' 2>&1 | tee -a "$OUT"
  adb exec-out 'timeout 60 voxl-esc detect 2>&1; echo "--- scan ---"; timeout 60 voxl-esc scan 2>&1' 2>&1 | tee -a "$OUT"

  echo; echo "===== PHASE 3: REBOOT (mandatory - recovers SLPI and reloads PX4 params) ====="
  adb shell "reboot" >/dev/null 2>&1
  echo "reboot issued; waiting for the drone to come back..."
  sleep 25
  adb wait-for-device
  sleep 35
  echo "--- post-reboot check: params should now be far above 110/2167 ---"
  adb exec-out 'echo -n "px4 params: "; timeout 20 px4-param show 2>&1 | tail -1;
                echo -n "MAV_SYS_ID: "; timeout 20 px4-param show MAV_SYS_ID 2>&1 | grep -i MAV_SYS_ID;
                echo -n "vision-hub: "; systemctl is-active voxl-vision-hub;
                echo -n "modal_io_bridge: "; ls /run/mpa/modal_io_bridge 2>&1' 2>&1 | tee -a "$OUT"
fi

echo; echo "== saved to: $OUT =="

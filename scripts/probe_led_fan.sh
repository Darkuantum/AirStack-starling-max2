#!/usr/bin/env bash
# Probe the LED and cooling open questions on a VOXL 2, over ADB (USB-C).
#
# READ-ONLY by default: nothing is written, no service is stopped, no state changes.
# Pass --fan-test to additionally cycle voxl-fan off/slow/on (audible check, restores to on).
#
# Usage: ./probe_led_fan.sh <label> [--fan-test]
set -uo pipefail

LABEL="${1:-drone}"
FAN_TEST=0
[ "${2:-}" = "--fan-test" ] && FAN_TEST=1

OUT="$HOME/AirStack-starling-max2/drone-backups/ledfan-${LABEL}-$(date +%Y%m%d-%H%M%S).txt"
mkdir -p "$(dirname "$OUT")"
LOCAL_TMP="$(mktemp -t voxl-ledfan.XXXXXX.sh)"
REMOTE=/data/voxl-ledfan.sh

{
cat <<'PROBE'
echo "########## A. ESC IDENTITY — settles M0129 vs M0138 ##########"
echo "--- voxl-esc tooling on disk ---"
ls -1 /usr/share/modalai/voxl-esc* 2>/dev/null | head
ls -1 /usr/share/modalai/voxl-esc/*/ 2>/dev/null | head -30
echo "--- voxl-esc help ---"
timeout 10 voxl-esc --help 2>&1 | head -30
echo "--- does PX4 hold the ESC UART? (voxl-px4 active => yes) ---"
systemctl is-active voxl-px4 2>&1
echo "--- ESC telemetry via PX4 (works WITHOUT stopping px4) ---"
timeout 10 px4-listener esc_status 2>&1 | head -40

echo; echo "########## B. LED PATH ##########"
echo "--- neopixel / led tools ---"
ls -1 /usr/bin/voxl-send-neopixel-cmd /usr/bin/voxl-led 2>&1
timeout 10 voxl-led --help 2>&1 | head -20
echo "--- ModalAI's own neopixel bench script ---"
find /usr/share/modalai -iname '*neopixel*' 2>/dev/null
echo "--- modal_io_bridge pipe (the LED transport) ---"
ls -la /run/mpa/modal_io_bridge 2>&1
echo "--- our daemon installed? ---"
ls -la /usr/bin/svg_led_daemon.py /etc/systemd/system/svg-led.service 2>&1
systemctl is-active svg-led 2>&1
echo "--- PX4 LED-related drivers present ---"
ls -1 /usr/bin/px4-rgbled /usr/bin/px4-led_control /usr/bin/px4-modal_io_bridge 2>&1

echo; echo "########## C. FAN CONTROL ##########"
echo -n "voxl-fan present: "; command -v voxl-fan 2>&1 || echo "NOT FOUND"
timeout 10 voxl-fan --help 2>&1 | head -20
echo "--- pwm chips (is pwmchip0 real on VOXL 2?) ---"
ls -la /sys/class/pwm/ 2>&1
for c in /sys/class/pwm/pwmchip*; do
  [ -e "$c" ] || continue
  echo "$c npwm=$(cat $c/npwm 2>&1)"
  for p in "$c"/pwm*; do
    [ -d "$p" ] || continue
    echo "  $(basename $p): period=$(cat $p/period 2>&1) duty=$(cat $p/duty_cycle 2>&1) enable=$(cat $p/enable 2>&1)"
  done
done
echo "--- cpu-monitor conf (does it expose fan thresholds?) ---"
cat /etc/modalai/voxl-cpu-monitor.conf 2>&1

echo; echo "########## D. THERMAL SNAPSHOT ##########"
echo "--- kernel thermal zones (degC) ---"
# EXCLUDE two traps learned the hard way:
#   *ibat*  are battery CURRENT zones, not temperatures. Left in, they sort to
#           the top and read as 468-781 "degrees".
#   soc     reads exactly 50.0 on every VOXL 2 sampled. It is a placeholder,
#           not a sensor. Use the cpu-* / apc-* / ddr-* zones instead.
for z in /sys/class/thermal/thermal_zone*; do
  [ -e "$z/temp" ] || continue
  ty=$(cat "$z/type" 2>/dev/null)
  case "$ty" in *ibat*|soc) continue;; esac
  t=$(cat "$z/temp" 2>/dev/null)
  printf '%-28s %s\n' "$ty" "$(awk -v t="$t" 'BEGIN{printf "%.1f", (t>1000? t/1000 : t)}')"
done | sort -k2 -rn | head -20
echo "--- what is actually loading the CPU (the usual cause of heat) ---"
ps -eo pid,pcpu,comm --sort=-pcpu 2>/dev/null | head -8
echo "--- governor + current vs max core frequency (throttling evidence) ---"
for i in 0 4 7; do
  d=/sys/devices/system/cpu/cpu$i/cpufreq
  [ -d "$d" ] || continue
  echo "cpu$i gov=$(cat $d/scaling_governor 2>&1) cur=$(cat $d/scaling_cur_freq 2>&1) max=$(cat $d/scaling_max_freq 2>&1)"
done
echo -n "GPU cur_freq: "; cat /sys/class/kgsl/kgsl-3d0/devfreq/cur_freq 2>&1
echo "NOTE: a core below its max frequency under schedutil is DEMAND SCALING, not"
echo "      throttling. Only low frequency TOGETHER WITH high temperature means"
echo "      throttling. Warning flag 90C, throttling begins ~95C."
echo "      On Starling 1, stock voxl-camera-server (95%) + voxl-qvio-server (48%)"
echo "      alone held the board at 95C; stopping them dropped it to 43.8C. Check"
echo "      the process list above before concluding the aircraft needs a fan."
PROBE

if [ "$FAN_TEST" = "1" ]; then
cat <<'FANTEST'

echo; echo "########## E. FAN TEST (changes state, restores to 'on') ##########"
echo "Listen to the aircraft. If no fan is fitted to J2 you will hear nothing."
for m in off slow on; do
  echo "--- voxl-fan $m ---"
  timeout 10 voxl-fan $m 2>&1
  for p in /sys/class/pwm/pwmchip*/pwm*; do
    [ -d "$p" ] || continue
    echo "  $(basename $(dirname $p))/$(basename $p): duty=$(cat $p/duty_cycle 2>&1) enable=$(cat $p/enable 2>&1)"
  done
  sleep 3
done
echo "restored to: on"
FANTEST
fi
} > "$LOCAL_TMP"

echo "== waiting for adb (USB-C in, drone on battery, PROPS OFF) =="
adb wait-for-device || exit 1
echo "serial: $(adb get-serialno)"
adb push "$LOCAL_TMP" "$REMOTE" >/dev/null || exit 1
adb exec-out "sh $REMOTE" 2>&1 | tee "$OUT"
adb shell "rm -f $REMOTE" >/dev/null 2>&1
rm -f "$LOCAL_TMP"
echo; echo "== saved to: $OUT =="

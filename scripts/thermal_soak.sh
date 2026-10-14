#!/usr/bin/env bash
# Still-air thermal soak for VOXL 2. Samples the real thermal zones + core clocks
# once a second and writes CSV to the LAPTOP.
#
#   ./thermal_soak.sh <label> [minutes] [--load]
#
# --load pins all 8 cores busy (worst case).  SAFETY, learned the hard way:
#   * the remote script TRAPS EXIT/INT/TERM and kills the load loops, so Ctrl+C
#     on the laptop no longer leaves 8 cores pinned on the drone forever;
#   * it also runs a HARD WATCHDOG that kills the load after the requested time
#     even if the sampler stalls;
#   * it ABORTS automatically if any zone exceeds ABORT_C (default 100 C);
#   * the loop is bounded on WALL CLOCK, not iteration count.
# Sampling spawns NO subprocesses per zone (that is what made the first version
# take 6.2 s per sample under load instead of 1.0 s).
#
# Props off. For a true still-air number, external fan OFF.
set -uo pipefail

LABEL="${1:-drone}"; MINS="${2:-12}"; LOAD=0
case "${3:-}" in --load) LOAD=1;; esac
case "$MINS" in ''|*[!0-9]*) echo "minutes must be a number, got '$MINS'" >&2; exit 2;; esac
ABORT_C="${ABORT_C:-100}"
SECS=$(( MINS * 60 ))
OUT="$HOME/AirStack-starling-max2/drone-backups/thermal-${LABEL}-$(date +%Y%m%d-%H%M%S).csv"
mkdir -p "$(dirname "$OUT")"
REMOTE=/data/voxl-soak.sh
LOCAL_TMP="$(mktemp -t voxl-soak.XXXXXX.sh)"

cat > "$LOCAL_TMP" <<PROBE
SECS=$SECS
LOAD=$LOAD
ABORT_C=$ABORT_C
PROBE
cat >> "$LOCAL_TMP" <<'PROBE'
PIDS=""
cleanup() { [ -n "$PIDS" ] && kill -9 $PIDS 2>/dev/null; PIDS=""; }
trap cleanup EXIT INT TERM HUP

ZONES=""; NAMES=""
for z in /sys/class/thermal/thermal_zone*; do
  [ -e "$z/temp" ] || continue
  ty=$(cat "$z/type" 2>/dev/null)
  case "$ty" in *ibat*|soc) continue;; esac
  ZONES="$ZONES $z/temp"; NAMES="$NAMES,$ty"
done

if [ "$LOAD" = 1 ]; then
  i=0; while [ $i -lt 8 ]; do (while : ; do : ; done) & PIDS="$PIDS $!"; i=$((i+1)); done
  # hard watchdog: kill the load after SECS+30 even if the sampler wedges
  ( sleep $((SECS + 30)); kill -9 $PIDS 2>/dev/null ) &
fi

printf 'epoch,uptime_s%s,cpu0_khz,cpu4_khz,cpu7_khz,gpu_hz\n' "$NAMES"

END=$(( $(date +%s) + SECS ))
while [ "$(date +%s)" -lt "$END" ]; do
  line="$(date +%s),$(cut -d. -f1 /proc/uptime)"
  hot=0
  for f in $ZONES; do
    v=$(cat "$f" 2>/dev/null); [ -n "$v" ] || v=0
    [ "$v" -gt "$hot" ] && hot=$v
    # integer millidegrees -> degrees, no subprocess
    line="$line,$((v/1000)).$(( (v%1000)/100 ))"
  done
  for c in 0 4 7; do
    line="$line,$(cat /sys/devices/system/cpu/cpu$c/cpufreq/scaling_cur_freq 2>/dev/null)"
  done
  line="$line,$(cat /sys/class/kgsl/kgsl-3d0/devfreq/cur_freq 2>/dev/null)"
  printf '%s\n' "$line"
  if [ "$hot" -ge "$((ABORT_C * 1000))" ]; then
    echo "# ABORT: ${hot} millideg >= ${ABORT_C}C - killing load and stopping" >&2
    cleanup; exit 3
  fi
  sleep 1
done
cleanup
PROBE

echo "== ${MINS} min, abort at ${ABORT_C} C, load=$LOAD =="
[ "$LOAD" = 1 ] && echo ">>> all 8 cores will be pinned. Ctrl+C is now SAFE - the drone kills them itself."
echo ">>> for a true still-air number, turn the external fan OFF"
adb wait-for-device || exit 1
adb push "$LOCAL_TMP" "$REMOTE" >/dev/null || exit 1
trap 'echo; echo "interrupted - telling the drone to drop the load..."; adb shell "pkill -9 -f voxl-soak.sh; pkill -9 -f \"while :\"" >/dev/null 2>&1; echo done' INT

adb exec-out "sh $REMOTE" | tee "$OUT" | awk -F, 'NR==1{next} {h=0; for(i=3;i<=NF-4;i++) if($i+0>h) h=$i+0}
  NR%15==2{printf "  t=%ss  hottest=%.1f C  cpu7=%s kHz\n", $2, h, $(NF-1)}'

adb shell "rm -f $REMOTE" >/dev/null 2>&1
rm -f "$LOCAL_TMP"
echo; echo "== saved: $OUT =="
python3 -I - "$OUT" <<'PY'
import csv,sys,statistics
rows=[r for r in csv.DictReader(open(sys.argv[1])) if r.get('epoch','').isdigit()]
if not rows: sys.exit("no samples")
zones=[k for k in rows[0] if k and k not in ('epoch','uptime_s') and not k.endswith(('_khz','_hz'))]
def pk(r):
    v=[(float(r[z]),z) for z in zones if r.get(z) and r[z] not in ('','None')]
    return max(v) if v else (0,'')
print(f"  samples {len(rows)} over {int(rows[-1]['epoch'])-int(rows[0]['epoch'])}s "
      f"({(int(rows[-1]['epoch'])-int(rows[0]['epoch']))/len(rows):.2f}s/sample)")
print(f"  start {pk(rows[0])[0]:.1f} C   end {pk(rows[-1])[0]:.1f} C   PEAK {max(pk(r)[0] for r in rows):.1f} C")
tail=[pk(r)[0] for r in rows[-30:]]
print(f"  last 30: mean {statistics.mean(tail):.1f} C  max {max(tail):.1f} C   (warn 90 / throttle ~95)")
f=[int(r['cpu7_khz']) for r in rows if (r.get('cpu7_khz') or '').isdigit()]
if f: print(f"  cpu7 kHz: first {f[0]}  last {f[-1]}  max {max(f)}  (sustained low + hot = throttling)")
PY

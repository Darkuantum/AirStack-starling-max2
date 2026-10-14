#!/usr/bin/env bash
# Still-air thermal soak. Logs the real thermal zones + core frequencies once a
# second to a CSV on the laptop, so you can see where the board settles with NO
# external airflow - the pre-flight / between-flight condition, which is the
# hottest case on the ground.
#
#   ./thermal_soak.sh <label> [minutes] [--load]
#
#   --load  pins all 8 cores busy for the duration (worst case). Without it you
#           get the honest idle-on-bench number.
#
# TURN THE EXTERNAL FAN OFF. Props off. Let it run undisturbed.
set -uo pipefail

LABEL="${1:-drone}"; MINS="${2:-12}"; LOAD=0
[ "${3:-}" = "--load" ] && LOAD=1
SECS=$(( MINS * 60 ))
OUT="$HOME/AirStack-starling-max2/drone-backups/thermal-${LABEL}-$(date +%Y%m%d-%H%M%S).csv"
mkdir -p "$(dirname "$OUT")"

adb wait-for-device || exit 1
echo "logging ${MINS} min to $OUT   (Ctrl+C to stop early)"
[ "$LOAD" = "1" ] && echo ">>> CPU LOAD MODE: all 8 cores pinned busy"
echo ">>> make sure the external fan is OFF"

adb exec-out "sh -c '
LOAD=$LOAD; SECS=$SECS
if [ \$LOAD = 1 ]; then
  i=0; while [ \$i -lt 8 ]; do (while :; do :; done) & i=\$((i+1)); done
fi
# header
printf \"epoch,uptime_s\"
for z in /sys/class/thermal/thermal_zone*; do
  ty=\$(cat \$z/type 2>/dev/null)
  case \"\$ty\" in *ibat*|soc) continue;; esac
  printf \",%s\" \"\$ty\"
done
for c in 0 4 7; do printf \",cpu%s_khz\" \$c; done
printf \",gpu_hz\n\"
t=0
while [ \$t -lt \$SECS ]; do
  printf \"%s,%s\" \"\$(date +%s)\" \"\$(cut -d. -f1 /proc/uptime)\"
  for z in /sys/class/thermal/thermal_zone*; do
    ty=\$(cat \$z/type 2>/dev/null)
    case \"\$ty\" in *ibat*|soc) continue;; esac
    v=\$(cat \$z/temp 2>/dev/null)
    printf \",%s\" \"\$(awk -v t=\$v \"BEGIN{printf \\\"%.1f\\\", (t>1000? t/1000 : t)}\")\"
  done
  for c in 0 4 7; do printf \",%s\" \"\$(cat /sys/devices/system/cpu/cpu\$c/cpufreq/scaling_cur_freq 2>/dev/null)\"; done
  printf \",%s\n\" \"\$(cat /sys/class/kgsl/kgsl-3d0/devfreq/cur_freq 2>/dev/null)\"
  sleep 1; t=\$((t+1))
done
if [ \$LOAD = 1 ]; then kill \$(jobs -p) 2>/dev/null; fi
'" | tee "$OUT" | awk -F, 'NR==1{next} NR%30==1{printf "t=%ss  hottest=%s C  cpu7=%s kHz\n", $2, $3, $(NF-1)}'

echo; echo "== saved to: $OUT =="
echo "Summary:"
python3 -I - "$OUT" <<'PY'
import csv,sys
rows=list(csv.DictReader(open(sys.argv[1])))
if not rows: sys.exit("no data")
zones=[k for k in rows[0] if k and k not in ('epoch','uptime_s') and not k.endswith(('_khz','_hz'))]
def peak(r): return max((float(r[z]) for z in zones if r[z]), default=0)
print(f"  samples      : {len(rows)}")
print(f"  start hottest: {peak(rows[0]):.1f} C")
print(f"  end   hottest: {peak(rows[-1]):.1f} C")
print(f"  MAX   hottest: {max(peak(r) for r in rows):.1f} C   (warn 90 C / throttle ~95 C)")
hot=max(rows,key=peak)
print("  at peak      : " + ", ".join(f"{z}={hot[z]}" for z in sorted(zones,key=lambda z: -float(hot[z] or 0))[:4]))
PY

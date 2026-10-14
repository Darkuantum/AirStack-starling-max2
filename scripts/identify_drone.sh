#!/usr/bin/env bash
# Identify which VOXL 2 board / Starling 2 Max build an airframe is, over ADB (USB-C).
# No network, no mocap, no Motive needed.  Usage: ./identify_drone.sh <label>
#
# Runs by PUSHING a script and using `adb exec-out` (no pty => no echo mangling,
# and the remote shell exits on its own instead of idling at a prompt).
set -uo pipefail

LABEL="${1:-drone}"
OUT="$HOME/AirStack-starling-max2/drone-backups/ident-${LABEL}-$(date +%Y%m%d-%H%M%S).txt"
mkdir -p "$(dirname "$OUT")"
LOCAL_TMP="$(mktemp -t voxl-ident.XXXXXX.sh)"
REMOTE=/data/voxl-ident.sh

cat > "$LOCAL_TMP" <<'PROBE'
echo "########## 1. BOARD IDENTITY ##########"
voxl-version
echo "--- voxl-platform ---"; voxl-platform 2>&1 | head -3
echo "--- raw platform sysfs (NUMERIC: machine/variant/subvariant) ---"
for f in machine variant subvariant; do
  printf '%-12s %s\n' "$f:" "$(cat /sys/module/voxl_platform_mod/parameters/$f 2>&1)"
done
echo "(machine=1 -> VOXL2 full-size.  variant 0 = var00 = M0054-1 'QRB5165M' silicon;"
echo " variant 2 = var02 = M0054-2 'QSM8250', capped at 4 concurrent cameras.)"

echo; echo "########## 2. WIFI / MODEM GENERATION ##########"
ip -br link
echo "--- netdev -> driver ---"
for n in /sys/class/net/*; do
  i=${n##*/}; [ "$i" = lo ] && continue
  d=$(readlink -f "$n/device/driver" 2>/dev/null); echo "$i -> ${d##*/}"
done
echo "--- lsusb ---"; lsusb
echo "--- modem config ---"; cat /etc/modalai/voxl-modem.conf 2>&1
echo "--- iface preferences ---"; cat /etc/modalai/network_interface_preferences.txt 2>&1
echo "--- supplicant ---"
systemctl list-units 'wpa_supplicant*' --all --no-pager --no-legend 2>&1
echo "--- usb enumerations this boot (should be 1 per device) ---"
dmesg 2>/dev/null | grep -cE 'usb 1-1.4: Product'
dmesg 2>/dev/null | grep -iE 'wlan|rtl88|cdc_mbim|sierra|qmi|mbim' | tail -20

echo; echo "########## 3. ESC / LED ##########"
echo "--- esc-related tools actually installed ---"
ls /usr/bin /usr/local/bin 2>/dev/null | grep -iE 'esc|modal_io|led' | sort -u
echo "--- esc params (PX4 side, reads back real values) ---"
px4-param show 2>/dev/null | grep -iE 'VOXL_ESC|ESC_' | head -20
echo "--- mpa pipes (modal_io_bridge present => ESC LED path live) ---"
ls /run/mpa 2>&1 | tr '\n' ' '; echo
echo "NOTE: px4-qshell returns an exit status only; command OUTPUT goes to the"
echo "      SLPI log, not stdout.  Read it with:  px4-logger / voxl-inspect-services"

echo; echo "########## 4. CAMERAS ##########"
echo "Sensor IDs: 0x0356=AR0144(1280x800 tracking) 0x0577=IMX577/412(12MP)"
echo "            0x2975=Infineon IRS2975 ToF  ->  ToF present means C29, not C28"
timeout 20 voxl-camera-server --list 2>&1 | sed -n '1,20p'
echo "--- configured cameras ---"
grep -E '"name"|"type"|"enabled"' /etc/modalai/voxl-camera-server.conf 2>/dev/null | head -40

echo; echo "########## 5. SOFTWARE STACK ##########"
echo -n "system image: "; cat /etc/version 2>&1
echo -n "px4 params loaded: "; timeout 15 px4-param show 2>&1 | tail -1
echo "--- px4 / dds services ---"
systemctl is-active voxl-px4 voxl-vision-hub 2>&1 | tr '\n' ' '; echo

echo; echo "########## 6. IDENTITY / NETWORK ##########"
echo -n "hostname: "; hostname
ip -br addr
echo -n "voxl-my-ip: "; timeout 5 voxl-my-ip 2>&1
echo "--- MAV_SYS_ID (must match AirStack target_system) ---"
timeout 15 px4-param show MAV_SYS_ID 2>&1 | grep -i MAV_SYS_ID
PROBE

echo "== waiting for adb (plug USB-C in, drone on battery, props OFF) =="
adb wait-for-device || exit 1
echo "serial: $(adb get-serialno)"
adb push "$LOCAL_TMP" "$REMOTE" >/dev/null || exit 1
adb exec-out "sh $REMOTE" 2>&1 | tee "$OUT"
adb shell "rm -f $REMOTE" >/dev/null 2>&1
rm -f "$LOCAL_TMP"
echo; echo "== saved to: $OUT =="

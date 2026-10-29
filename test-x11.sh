#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export XDG_DATA_DIRS="$PWD/config/includes.chroot/usr/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
openbox --config-file "$PWD/config/includes.chroot/etc/xdg/laccaz/openbox.xml" > /tmp/laccaz-openbox-test.log 2>&1 &
wm_pid=$!
trap 'kill "$wm_pid" 2>/dev/null || true' EXIT
python3 - <<'PY'
import time,subprocess
for _ in range(40):
 r=subprocess.run(['wmctrl','-m'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
 if r.returncode==0 and 'Openbox' in r.stdout:break
 time.sleep(.05)
else:raise SystemExit('Openbox failed to start')
PY
python3 tests/test_regressions.py
python3 tests/test_window_manager.py

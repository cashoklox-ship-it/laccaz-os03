#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $EUID -eq 0 ]] || { echo 'Run: sudo bash scripts/build.sh'; exit 1; }
. /etc/os-release
[[ "$ID" == debian && "$VERSION_ID" == 13 ]] || { echo 'Build in Debian 13 amd64 VM (not WSL or Ubuntu).'; exit 1; }
[[ "$(dpkg --print-architecture)" == amd64 ]] || exit 1
for cmd in lb debootstrap xorriso mksquashfs; do command -v "$cmd" >/dev/null || { echo "Missing $cmd. Read README.md"; exit 1; }; done
[[ ! -d chroot && ! -d .build ]] || { echo 'Existing build found. Run sudo lb clean --purge first.'; exit 1; }
chmod +x auto/config config/hooks/normal/*.hook.chroot config/includes.chroot/usr/bin/laccaz-*
chmod +x config/includes.chroot/lib/live/config/9999-laccaz-session
chmod +x config/includes.chroot/usr/libexec/laccaz-package-action
mkdir -p artifacts
lb config 2>&1 | tee artifacts/config.log
lb build 2>&1 | tee artifacts/build.log
cp live-image-amd64.hybrid.iso artifacts/laccaz-os-0.5-amd64.iso
(cd artifacts && sha256sum laccaz-os-0.5-amd64.iso > SHA256SUMS)
echo 'Built artifacts/laccaz-os-0.5-amd64.iso — boot-test before installation.'

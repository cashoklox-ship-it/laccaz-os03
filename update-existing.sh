#!/bin/bash
# Apply the interface update to an existing Laccaz installation or live session.
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $EUID -eq 0 ]] || { echo 'Run: sudo bash scripts/update-existing.sh'; exit 1; }
[[ -f /etc/laccaz-release ]] || { echo 'This script is only for an existing Laccaz OS system.'; exit 1; }
for tool in pkexec lxqt-policykit-agent; do
  command -v "$tool" >/dev/null || { echo 'First install: sudo apt install pkexec polkitd lxqt-policykit'; exit 1; }
done
backup="/var/backups/laccaz/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup/usr/share" "$backup/etc/xdg" "$backup/usr/bin"
[[ ! -d /usr/share/laccaz ]] || cp -a /usr/share/laccaz "$backup/usr/share/"
[[ ! -d /etc/xdg/laccaz ]] || cp -a /etc/xdg/laccaz "$backup/etc/xdg/"
for file in /usr/bin/laccaz-*; do [[ ! -f "$file" ]] || cp -a "$file" "$backup/usr/bin/"; done
mkdir -p /usr/share/laccaz /usr/share/themes/Laccaz /etc/xdg/laccaz /usr/share/xsessions
cp -a config/includes.chroot/usr/share/laccaz/. /usr/share/laccaz/
cp -a config/includes.chroot/usr/share/themes/Laccaz/. /usr/share/themes/Laccaz/
cp -a config/includes.chroot/etc/xdg/laccaz/. /etc/xdg/laccaz/
cp config/includes.chroot/usr/share/xsessions/laccaz.desktop /usr/share/xsessions/
cp config/includes.chroot/usr/bin/laccaz-* /usr/bin/
mkdir -p /usr/libexec /usr/share/polkit-1/actions /usr/share/applications
cp config/includes.chroot/usr/libexec/laccaz-package-action /usr/libexec/
chmod 0755 /usr/libexec/laccaz-package-action
cp config/includes.chroot/usr/share/polkit-1/actions/org.laccaz.packages.policy /usr/share/polkit-1/actions/
cp config/includes.chroot/usr/share/applications/laccaz-appcenter.desktop /usr/share/applications/
chmod +x /usr/bin/laccaz-*
chown -R root:root /usr/share/laccaz /usr/share/themes/Laccaz /etc/xdg/laccaz
chown root:root /usr/libexec/laccaz-package-action /usr/bin/laccaz-* /usr/share/polkit-1/actions/org.laccaz.packages.policy
chmod 0755 /usr/libexec/laccaz-package-action
chmod 0644 /usr/share/laccaz/catalog.json
chmod 0755 /usr/share/laccaz
printf 'Laccaz OS 0.5 Developer Preview\nBased on Debian 13 (trixie)\n' > /etc/laccaz-release
echo "Interface updated. Backup: $backup"
echo 'Log out and select Laccaz Surface again. On a non-persistent Live USB this update is lost after reboot.'

# Laccaz OS 0.5 — validation

Passed in isolated Ubuntu authoring runtime (not booted Debian ISO):
- Qt native X11/Openbox and offscreen: real mouse clicks on enlarged custom Close/Minimize/Maximize controls, restore and close during running process.
- Real xdotool clicks on standard Openbox window decorations: minimize, maximize, restore, close. New native title frame measured 50px high.
- All four generated project task chains: Python, JavaScript/npm, C/GCC, C++/CMake; real build/run output checked.
- Runner sequence stops on nonzero exit; closing while a task runs stops the process and closes the window.
- JSON transformation and URL parsing; template creation/path validation/no overwrite.
- Clipboard capture, deduplication, pause, confidential MIME exclusion, restore, clear, entry limit, search; file browser population.
- Every selected package name found in Debian 13 main amd64 Packages index.
- Shell script syntax and Python compilation; native test-session screenshots inspected.

Not verified:
- Full ISO 0.4 build, boot and installation; NVIDIA/Wi-Fi/suspend and real hardware.
- Live-config session-selection hook in a booted ISO; SDDM authentication remains standard.
- Unix datagram shortcut IPC on target: authoring runtime forbids AF_UNIX sockets. Failure now degrades shortcuts without crashing the desktop. Openbox key bindings and handler code are included, but end-to-end shortcuts require a target session test.
- picom compositing/animation appearance on hardware; multiple monitors and scaling remain limited to the primary monitor.
- Network dependency installation and user-authored test suites, remote Git operations and package install scripts.

Window action bug is corrected and tested in X11, but this is still a Developer Preview, not a fully validated production OS.


0.5 additions:
- App Center contains 20 curated packages; all package names and added polkit dependencies checked against Debian 13 amd64 main index.
- Passed: allowlist and argument validation; simulated apt removal refused when other packages would be removed. No actual privileged apt command ran in the tests.
- Passed: App Center filtering, actual read-only dpkg-query status, simulated pkexec cancellation and success; UI stays responsive. Root ownership of catalogue/helper enforced at build/update time.
- Desktop widgets, wallpaper painting and catalogue GUI rendered under X11/Openbox and visually inspected. Wallpaper generated as an original raster asset, not an OS screenshot.
- Existing project runners and close/minimize/maximize regression tests still pass.
- Real polkit prompt, privileged package download/install/remove, ISO 0.5 build/boot and persistence NOT verified in a booted target system.

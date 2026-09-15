# Reference inspection — 2026-09-14

This is a sanitized, selective inventory, not a home-directory export. Live
inspection confirmed Debian 13 (Trixie) on the Getac K120 G2 reference system.
No credentials, private accounts, browser profiles, histories, network connection
files, serial numbers, or user documents were collected into the repository.

| Area | Observed working reference | ABS foundation decision |
| --- | --- | --- |
| Window manager | i3 4.24, standard Super bindings, explicit media/brightness keys | portable authored template; preserve familiar controls |
| Bar | running i3bar + i3blocks 1.4; network, Bluetooth, battery, storage, memory, screenshot, clock | retain i3blocks; capability-gate battery/Bluetooth |
| BatteryBar | Python wrapper executes a file in a separate batterybar-i3blocks checkout | do not vendor an unresolved external checkout; independent per-pack status now; integrate reviewed upstream later |
| Launcher | Rofi 1.7.5, DarkBlue theme | use packaged theme; no personal launcher entries |
| Notifications | Dunst installed; no user Dunst config found | small source-controlled Dunst defaults |
| Terminal | xfce4-terminal installed; i3 uses i3-sensible-terminal; Kitty absent | Kitty is a deliberate portable ABS choice from existing intent, not a claim about the running terminal |
| Display manager | SDDM active; LightDM installed but inactive | LightDM for new images; manual bootstrap leaves existing manager selection alone |
| Network/audio | nm-applet, NetworkManager, PipeWire, pipewire-pulse, WirePlumber running | Debian packages and standard pactl controls |
| Bluetooth | bluez active; bar opens a KDE settings page | use Blueman to avoid importing KDE settings for one control |
| Lock/power | xss-lock; custom hybrid-sleep scripts; logind suspend-then-hibernate overrides | xss-lock + i3lock + normal suspend; no host resume assumptions |
| Input | touchscreen, touchpad, USB mouse; no native TrackPoint observed | udev capability flags; Debian libinput defaults |
| Displays | one connected eDP panel at 1920×1080; no Xorg drop-in files | no DPI or connector-name assumptions |
| Sensors | detector sees an accelerometer; no tablet switch exposed | diagnostic capability only; no untested auto-rotation |
| Touch UI | local LCARS service, Getac P1/F13 wiring, Onboard bindings | optional future integration; generic touch-only Onboard shortcut now |
| Theme/fonts | Breeze-Dark GTK, Noto, host DPI and cursor-size overrides | Noto/DejaVu and portable dark app defaults; omit host DPI |
| Wallpaper | feh restores a user-selected wallpaper | user-supplied ABSLinux_wallpaper_0.png as default wallpaper |
| Fastfetch | installed; no user configuration found | ABS text logo with real Debian/system modules |
| Autostart | KDE/PIM and other personal integrations also running | explicit desktop startup; no blanket personal autostart import |
| User services | LCARS and AppImage launcher service entries | neither copied to the generic image |
| System configuration | modem udev quirk, Getac-specific sleep settings | retain on reference machine only; future documented quirks if justified |

Source inspection covered i3/i3blocks/Rofi configuration, bar scripts and local
launcher/lock paths, relevant user service definitions, installed package metadata,
Xorg/logind/sleep drop-ins, process names, xinput, xrandr, sysfs and udev facts.
Personal shell files were not bulk-read or copied; ABS does not need shell startup
changes. `/usr/local/bin` contained unrelated tools, which were not imported.

The detector reported battery, touchscreen, touchpad, Bluetooth, accelerometer and
key-capable input; it did not report a TrackPoint, tablet-mode switch or multiple
connected displays. These observations are test evidence, not hostname rules.
`hardware_buttons` means key-capable input exists, not that arbitrary vendor
buttons have a known semantic binding. `tablet_mode` reports switch availability,
not its current folded/unfolded state.

An SSH attempt to the existing `deb440` alias failed name resolution. No SSH
configuration was changed and no address was guessed. Native ThinkPad TrackPoint,
lid, function-key and suspend comparison remains a hardware validation task.

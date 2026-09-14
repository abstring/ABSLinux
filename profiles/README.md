# Capability profiles

`profiles.json` maps facts to package groups. Common = base + desktop; battery =
laptop; touchscreen = touch; pointing stick = trackpoint; Bluetooth = bluetooth.
The live image includes all supported hardware packages. Runtime bar and keyboard
behavior still depend on capabilities, never the build host's identity.

TrackPoint support currently uses Debian's libinput defaults plus diagnostics;
custom acceleration/scroll tuning requires native-device testing. Rotation sensor,
key-capable input, tablet-switch availability, touchpad and multi-monitor facts
are exposed for diagnostics without activating untested automation.

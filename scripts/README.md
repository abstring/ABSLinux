# Runtime tools

- `abs-capabilities`: read-only sanitized JSON from sysfs and udev.
- `abs-bar`: generates a private temporary i3blocks config; adds battery/Bluetooth
  blocks based on capabilities and removes runtime data on exit.
- `abs-status`: portable status/click actions; per-pack batteries, network state,
  audio, Bluetooth, screenshots.
- `abs-network`: opens NetworkManager setup from the bar or Super+N.
- `abs-screenshot`: releases launch input before capture; `--cancel` ends the
  current user’s Flameshot process for input recovery.
- `abs-touch-keyboard`: starts Onboard only when a touchscreen is detected.

The deployment installs these under `/usr/local/bin`. They contain no hostnames,
network credentials, personal paths or dependencies on another checkout.

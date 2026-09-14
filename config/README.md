# Source-controlled desktop defaults

`i3`, `i3blocks`, `rofi`, `dunst`, `kitty`, and `fastfetch` are portable, authored ABS
defaults. They are seeded into new users' `.config` and then belong to the user.
`wallpaper/hero.png` is an unchanged copy of the root ABS hero artwork (CC0-1.0);
it is deployed system-wide under `/usr/share/abs/config/wallpaper`.

No private reference dotfiles or host paths are copied. See the inventory and
ADR for intentional differences from the reference desktop. Shell configuration,
DPI, custom button mapping, hibernation, and personal autostarts remain untouched.

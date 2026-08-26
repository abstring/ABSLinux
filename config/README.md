# Application configuration

Application-owned configuration will live in named subdirectories as it is implemented—for example `i3/`, `polybar/`, `rofi/`, `dunst/`, `kitty/`, `fastfetch/`, and `gtk/`.

Specialized interfaces such as the planned LCARS touch launcher should use their own clearly bounded directory and activation profile. They must not leak touch-specific behavior into the portable i3 baseline.

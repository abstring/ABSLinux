# Update an existing alpha.1 installation

These steps update an existing ABS Linux account to the alpha.2 desktop fixes
without reinstalling or partitioning disks. Run them from a terminal as the user
whose desktop you are updating. Keep the original configuration backup until you
have verified the new behavior. The installer fixes also apply to new alpha.2 installs.

## Get the release source

```sh
git clone --branch v0.1.0-alpha.2 https://github.com/abstring/ABSLinux.git ABSLinux-alpha2
cd ABSLinux-alpha2
```

## Install Brave and set the default browser

Brave uses its [official stable APT repository](https://brave.com/linux/).
The checked-in public keyring scopes signature verification with Signed-By.
If you already configured Brave yourself, check for duplicate source entries first.

```sh
sudo apt-get install ca-certificates
sudo install -Dm644 bootstrap/apt/brave-browser-archive-keyring.gpg /usr/share/keyrings/brave-browser-archive-keyring.gpg
sudo install -Dm644 bootstrap/apt/brave-browser-release.sources /etc/apt/sources.list.d/brave-browser-release.sources
sudo apt-get update
sudo apt-get install brave-browser
xdg-settings set default-web-browser brave-browser.desktop
xdg-mime default brave-browser.desktop x-scheme-handler/http x-scheme-handler/https text/html application/xhtml+xml
```

## Fix installed shell and GRUB labels

Remove only the known live marker. Custom chroot labels are preserved.
The GRUB override changes the menu label, leaving Debian identity and boot paths intact.

```sh
if [ -f /etc/debian_chroot ] && [ "$(cat /etc/debian_chroot)" = live ]; then
    sudo rm /etc/debian_chroot
fi
sudo mkdir -p /etc/default/grub.d
printf '%s\n' 'GRUB_DISTRIBUTOR="ABS Linux"' | sudo tee /etc/default/grub.d/90-abs-label.cfg
sudo update-grub
```

Open a new terminal to check the prompt. Check the GRUB label on the next reboot.

## Update desktop controls

Back up the current i3 config and managed helpers, then install the new helpers.
These commands do not replace your complete desktop configuration.

```sh
backup="$HOME/abs-alpha1-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"
cp -a "$HOME/.config/i3/config" "$backup/i3-config"
cp -a /usr/local/bin/abs-status "$backup/abs-status"
sudo install -m755 scripts/abs-status scripts/abs-screenshot scripts/abs-network /usr/local/bin/
```

Edit `~/.config/i3/config`. Replace the old `bindsym Print ...` line with:

```text
bindsym --release Print exec --no-startup-id abs-screenshot
```

Add these bindings unless you already use the same keys (choose alternatives if so):

```text
bindsym $mod+Shift+Escape exec --no-startup-id abs-screenshot --cancel
bindsym $mod+n exec --no-startup-id abs-network
bindsym $mod+b exec --no-startup-id brave-browser
for_window [class="^abs-network$"] floating enable, resize set 850 550, move position center
```

Validate and reload:

```sh
i3 -C -c "$HOME/.config/i3/config" && i3-msg reload
```

## Optional new wallpaper

```sh
sudo install -Dm644 config/wallpaper/default.png /usr/share/abs/config/wallpaper/default.png
feh --bg-max /usr/share/abs/config/wallpaper/default.png
```

For persistence, replace the old `feh --bg-fill .../hero.png` command in your i3
configuration with `feh --bg-max /usr/share/abs/config/wallpaper/default.png`.
This uses the new supplied wallpaper without cropping the artwork.

## Use and verify

- **Wi-Fi:** click the network status or press **Super+N**, choose **Activate a
  connection**, select your Wi-Fi network and enter its password. If Wi-Fi is off,
  use **Radio** to enable it; physical radio switches must also be enabled.
- **Browser:** press **Super+B**, or select Brave in Rofi. HTTP/HTTPS links open Brave.
- **Screenshot:** press **Print** or click Screenshot, then drag a rectangle.
  **Ctrl+S** saves, **Ctrl+C** copies, and **Esc** cancels. **Super+Shift+Esc**
  terminates your Flameshot process if capture becomes stuck; this also closes
  unsaved Flameshot edits. No machine restart is needed for that recovery.
- Check input recovery, Wi-Fi association and the boot menu on the X13 and report
  results on the corresponding issues. VM validation does not verify its hardware.

To restore desktop bindings, copy the saved `i3-config` back to
`~/.config/i3/config`, restore the saved `abs-status` to `/usr/local/bin`, and reload
i3. Leave Brave installed or remove it explicitly if you no longer want it.
